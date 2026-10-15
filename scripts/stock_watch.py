#!/usr/bin/env python3
"""Flag watched Etsy listings whose stock is below a threshold.

Read-only: one GET per listing id from config/stock_watch.json. Writes a
markdown issue body to low-stock.md when anything is flagged.
"""

import json
import os
import sys

import requests

ETSY_API_BASE = "https://openapi.etsy.com/v3/application"
CONFIG_PATH = "config/stock_watch.json"
REPORT_PATH = "low-stock.md"
DEFAULT_THRESHOLD = 5


def load_config(path):
    with open(path, encoding="utf-8") as handle:
        config = json.load(handle)
    return config.get("threshold", DEFAULT_THRESHOLD), config["listings"]


def fetch_listing(session, listing_id):
    response = session.get(f"{ETSY_API_BASE}/listings/{listing_id}", timeout=30)
    response.raise_for_status()
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
    api_key = os.environ.get("ETSY_API_KEY")
    if not api_key:
        sys.exit("ETSY_API_KEY is not set: add it as a GitHub repo secret.")

    threshold, listings = load_config(CONFIG_PATH)
    session = requests.Session()
    session.headers["x-api-key"] = api_key

    quantities = []
    errors = []
    for entry in listings:
        listing_id = entry["id"]
        label = entry.get("label", str(listing_id))
        try:
            quantity = effective_quantity(fetch_listing(session, listing_id))
        except requests.RequestException as exc:
            errors.append(f"listing {listing_id}: {exc}")
            continue
        quantities.append((listing_id, label, quantity))
        print(f"{listing_id}\t{quantity}\t{label}")

    low = find_low(quantities, threshold)
    if low:
        with open(REPORT_PATH, "w", encoding="utf-8") as handle:
            handle.write(render_report(low, threshold))
        print(f"{len(low)} listing(s) below {threshold}; wrote {REPORT_PATH}")

    if errors:
        sys.exit("could not read: " + "; ".join(errors))


if __name__ == "__main__":
    main()
