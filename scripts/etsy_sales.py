#!/usr/bin/env python3
"""Write which listings sold in the last 60 days, from Etsy order data.

Reads getShopReceiptTransactionsByShop (scope transactions_r) with the token
from etsy_oauth_login.py, refreshing it first when it is near expiry, and
writes one row per sold item: `Sale Date`, `Listing ID`. Those are the two
columns the listing ranking reads from an Etsy Order Items export via
--sales; nothing else from the order leaves memory.

Transactions, not receipts: a receipt carries the buyer's name, email and
address, a transaction does not. The transactions endpoint has no date filter
and no documented sort order, so every page is read and filtered here.
"""

import argparse
import csv
import io
import os
import sys
import time
from datetime import datetime, timezone

import requests

from etsy_auth import api_key_header, check_response
from etsy_oauth import (
    DEFAULT_TOKENS_PATH,
    TOKEN_URL,
    client_id,
    load_tokens,
    save_tokens,
    token_record,
    write_private,
)

ETSY_API_BASE = "https://openapi.etsy.com/v3/application"
DEFAULT_SHOP_ID = "64554473"
DEFAULT_OUT = "~/Obsidian/projects/vogelpoesie/etsy-sold-order-items.csv"
DEFAULT_DAYS = 60
PAGE_SIZE = 100
# Refresh a token this close to expiry rather than have it lapse mid-paging.
REFRESH_MARGIN = 300
FIELDNAMES = ["Sale Date", "Listing ID"]
# The Etsy Order Items export writes Sale Date as MM/DD/YY; match it so the
# ranking reads this file and a manual export the same way.
SALE_DATE_FORMAT = "%m/%d/%y"


def access_token(session, keystring, tokens_path, now):
    """A usable access token, refreshing (and storing the rotated pair) if due."""
    tokens = load_tokens(tokens_path)
    if tokens.get("expires_at", 0) - REFRESH_MARGIN > now:
        return tokens["access_token"]

    # Form body, never the query string: check_response prints the URL.
    response = session.post(
        TOKEN_URL,
        data={
            "grant_type": "refresh_token",
            "client_id": keystring,
            "refresh_token": tokens["refresh_token"],
        },
        timeout=30,
    )
    check_response(response)
    fresh = token_record(response.json(), now, tokens["refresh_token"])
    # Saved before any order call: the old refresh token may already be dead,
    # so losing the new one to a later failure would force a fresh login.
    save_tokens(tokens_path, fresh)
    return fresh["access_token"]


def fetch_sales(session, shop_id, since):
    """[(listing_id, created_timestamp)] for transactions created at or after `since`."""
    sales = []
    offset = 0
    while True:
        response = session.get(
            f"{ETSY_API_BASE}/shops/{shop_id}/transactions",
            params={"limit": PAGE_SIZE, "offset": offset},
            timeout=30,
        )
        check_response(response)
        payload = response.json()
        results = payload.get("results", [])
        for transaction in results:
            created = transaction.get("created_timestamp") or transaction.get(
                "create_timestamp"
            )
            listing_id = transaction.get("listing_id")
            if listing_id and created and created >= since:
                sales.append((listing_id, created))

        offset += len(results)
        if not results or offset >= payload.get("count", 0):
            break
    return sales


def render_csv(sales):
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(FIELDNAMES)
    for listing_id, created in sorted(sales, key=lambda sale: (-sale[1], sale[0])):
        sale_date = datetime.fromtimestamp(created, timezone.utc).strftime(SALE_DATE_FORMAT)
        writer.writerow([sale_date, listing_id])
    return out.getvalue()


def main(argv=None, session=None, now=time.time):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", default=DEFAULT_OUT, help="CSV path (default: %(default)s)")
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS)
    parser.add_argument("--tokens", default=DEFAULT_TOKENS_PATH, help="token file")
    args = parser.parse_args(argv)

    api_key_value = api_key_header(os.environ)
    keystring = client_id(os.environ)
    shop_id = os.environ.get("ETSY_SHOP_ID", "").strip() or DEFAULT_SHOP_ID
    current = now()

    session = session or requests.Session()
    session.headers["x-api-key"] = api_key_value
    token = access_token(session, keystring, args.tokens, current)
    session.headers["Authorization"] = f"Bearer {token}"

    sales = fetch_sales(session, shop_id, current - args.days * 86400)
    path = write_private(args.out, render_csv(sales))
    print(f"Wrote {len(sales)} sold items from the last {args.days} days to {path}")


if __name__ == "__main__":
    main()
