#!/usr/bin/env python3
"""Flag watched Etsy listings whose stock is below a threshold.

Read-only: one GET per listing id from config/stock_watch.json. Writes a
markdown issue body to low-stock.md when anything is flagged.
"""

import json
import os
import sys

import requests

from etsy_auth import api_key_header, check_response

ETSY_API_BASE = "https://openapi.etsy.com/v3/application"
CONFIG_PATH = "config/stock_watch.json"
REPORT_PATH = "low-stock.md"
DEFAULT_THRESHOLD = 5


def load_config(path):
    with open(path, encoding="utf-8") as handle:
        config = json.load(handle)
    return config.get("threshold", DEFAULT_THRESHOLD), config["listings"]


def fetch_listing(session, listing_id):
    """The listing, or None when Etsy no longer has it (deleted or replaced).

    A shop retires listings regularly, and one dead id must not turn the whole
    daily watch red: that hides the real low-stock signal behind a 404.
    """
    response = session.get(f"{ETSY_API_BASE}/listings/{listing_id}", timeout=30)
    if response.status_code == 404:
        return None
    check_response(response)
    return response.json()


def effective_quantity(listing):
    """A listing that is not active sells nothing, whatever its quantity says."""
    if listing.get("state", "active") != "active":
        return 0
    return listing["quantity"]


def find_low(quantities, threshold):
    """quantities: list of (id, label, quantity). Returns those below threshold."""
    return [item for item in quantities if item[2] < threshold]


def render_report(low, threshold):
    lines = [f"Listings below {threshold} in stock:", ""]
    for listing_id, label, quantity in low:
        lines.append(
            f"- [{label}](https://www.etsy.com/listing/{listing_id}): {quantity}"
        )
    return "\n".join(lines) + "\n"


def main():
    api_key_value = api_key_header(os.environ)

    threshold, listings = load_config(CONFIG_PATH)
    session = requests.Session()
    session.headers["x-api-key"] = api_key_value

    quantities = []
    errors = []
    gone = []
    for entry in listings:
        listing_id = entry["id"]
        label = entry.get("label", str(listing_id))
        try:
            listing = fetch_listing(session, listing_id)
        except requests.RequestException as exc:
            errors.append(f"listing {listing_id}: {exc}")
            continue
        if listing is None:
            gone.append(f"{listing_id} ({label})")
            print(f"{listing_id}\tGONE\t{label}", file=sys.stderr)
            continue
        quantities.append((listing_id, label, effective_quantity(listing)))
        print(f"{listing_id}\t{quantities[-1][2]}\t{label}")

    low = find_low(quantities, threshold)
    if low:
        with open(REPORT_PATH, "w", encoding="utf-8") as handle:
            handle.write(render_report(low, threshold))
        print(f"{len(low)} listing(s) below {threshold}; wrote {REPORT_PATH}")

    if gone:
        print(
            "no longer on Etsy, prune config/stock_watch.json: " + "; ".join(gone),
            file=sys.stderr,
        )
    if errors:
        sys.exit("could not read: " + "; ".join(errors))


if __name__ == "__main__":
    main()
