#!/usr/bin/env python3
"""Record every active listing's lifetime views and favorites for today.

Appends one row per listing to data/listing_stats.csv, replacing any rows
already stored for the same UTC date. Etsy's `views` are lifetime totals, so
the day-by-day history this builds is what lets listing_report.py compute
views gained.
"""

import csv
import datetime
import os
import sys
import tempfile

import requests

from etsy_auth import api_key_header, check_response
from pinterest_feed import ETSY_API_BASE, PAGE_SIZE, resolve_shop_id

STATS_PATH = "data/listing_stats.csv"
FIELDNAMES = ["date", "listing_id", "title", "views", "num_favorers", "state"]
REQUIRED_FIELDS = ("views", "num_favorers")


def fetch_active_listings(shop_id, api_key_value):
    """Every active listing for the shop, straight from the listings page(s).

    No images call: views and num_favorers are on ShopListing itself.
    """
    session = requests.Session()
    session.headers["x-api-key"] = api_key_value

    listings = []
    offset = 0
    while True:
        response = session.get(
            f"{ETSY_API_BASE}/shops/{shop_id}/listings/active",
            params={"limit": PAGE_SIZE, "offset": offset},
            timeout=30,
        )
        check_response(response)
        payload = response.json()
        results = payload.get("results", [])
        listings.extend(results)

        offset += len(results)
        if not results or offset >= payload.get("count", 0):
            break
    return listings


def build_rows(listings, date):
    """One stats row per listing, or exit naming the first missing field.

    Etsy documents `views` and `num_favorers` on ShopListing, but that was
    never checked against the live API. A missing field must fail the run
    rather than be recorded as zero, which would look like a real dead day.
    """
    rows = []
    for listing in listings:
        listing_id = listing.get("listing_id")
        for field in REQUIRED_FIELDS:
            if listing.get(field) is None:
                sys.exit(
                    f"Etsy listing {listing_id} has no '{field}' field in the "
                    f"active-listings response: the assumption that ShopListing "
                    f"carries views and num_favorers is wrong. Nothing recorded."
                )
        rows.append(
            {
                "date": date,
                "listing_id": listing_id,
                "title": " ".join((listing.get("title") or "").split()),
                "views": listing["views"],
                "num_favorers": listing["num_favorers"],
                "state": listing.get("state", "active"),
            }
        )
    return rows


def read_stats(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_stats(rows, date, path):
    """Store `rows` as the only rows for `date`; other dates are kept as is.

    Written to a temp file and renamed, so a crash cannot leave a truncated
    history behind.
    """
    kept = [row for row in read_stats(path) if row["date"] != date]
    merged = sorted(kept + rows, key=lambda row: row["date"])

    directory = os.path.dirname(path) or "."
    os.makedirs(directory, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=directory, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, lineterminator="\n")
            writer.writeheader()
            writer.writerows(merged)
        os.replace(tmp_path, path)
    except BaseException:
        os.unlink(tmp_path)
        raise


def main(path=STATS_PATH):
    api_key_value = api_key_header(os.environ)
    shop_id = resolve_shop_id(os.environ)
    date = datetime.datetime.now(datetime.timezone.utc).date().isoformat()

    listings = fetch_active_listings(shop_id, api_key_value)
    if not listings:
        sys.exit("Etsy returned zero active listings — refusing to record an empty day.")
    rows = build_rows(listings, date)

    write_stats(rows, date, path)
    print(f"recorded {len(rows)} listings for {date} in {path}")


if __name__ == "__main__":
    main()
