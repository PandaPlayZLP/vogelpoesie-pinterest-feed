#!/usr/bin/env python3
"""Build feed.tsv (Pinterest catalog feed) from the live Etsy shop listings."""

import csv
import os
import re
import sys

import requests

ETSY_API_BASE = "https://openapi.etsy.com/v3/application"

# Default shop id inferred from the Etsy CDN image paths baked into the
# 2026-04-28 artifact (every i.etsystatic.com image URL starts with this id).
# Override with ETSY_SHOP_ID if that inference is ever wrong.
DEFAULT_SHOP_ID = "64554473"

BRAND = "Vogelpoesie"

# (title keyword, product_type, google_product_category, item_group suffix)
PRODUCT_RULES = [
    ("Tasse", "Heimische Vögel > Tassen", "674", "tasse"),
    ("Poster", "Heimische Vögel > Poster A2", "503793", "poster"),
    ("Jutebeutel", "Heimische Vögel > Jutebeutel", "176", "tote"),
    ("Hoodie", "Heimische Vögel > Hoodies Bio-Baumwolle", "5322", "hoodie"),
    ("T-Shirt", "Heimische Vögel > T-Shirts Bio-Baumwolle", "5322", "tshirt"),
]

FIELDNAMES = [
    "id",
    "title",
    "description",
    "link",
    "image_link",
    "additional_image_link",
    "price",
    "availability",
    "condition",
    "brand",
    "product_type",
    "google_product_category",
    "item_group_id",
]


def clean_text(value):
    """Collapse a listing's free text into a single TSV-safe line."""
    return re.sub(r"\s+", " ", value or "").strip()


def slugify(value):
    return re.sub(r"[^\w-]", "", value.lower().replace(" ", "-"))


def classify(title):
    for keyword, product_type, gpc, suffix in PRODUCT_RULES:
        if keyword.lower() in title.lower():
            return product_type, gpc, suffix
    raise ValueError(f"no product rule matches listing title: {title!r}")


def fetch_active_listings(shop_id, api_key):
    """Yield every active listing for the shop, with images included."""
    session = requests.Session()
    session.headers["x-api-key"] = api_key

    offset = 0
    limit = 100
    while True:
        response = session.get(
            f"{ETSY_API_BASE}/shops/{shop_id}/listings/active",
            params={"limit": limit, "offset": offset, "includes": "Images"},
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
        results = payload.get("results", [])
        yield from results

        offset += len(results)
        if not results or offset >= payload.get("count", 0):
            break


def listing_to_row(listing):
    title = clean_text(listing["title"])
    bird = slugify(title.split(" ")[0])
    product_type, gpc, suffix = classify(title)

    images = sorted(listing.get("images", []), key=lambda img: img.get("rank", 0))
    image_urls = [img["url_fullxfull"] for img in images]

    price = listing["price"]
    amount = price["amount"] / price["divisor"]

    return {
        "id": listing["listing_id"],
        "title": title,
        "description": clean_text(listing["description"]),
        "link": (
            f"{listing['url']}?utm_source=pinterest&utm_medium=catalog"
            f"&utm_campaign={bird}-{suffix}"
        ),
        "image_link": image_urls[0] if image_urls else "",
        "additional_image_link": ",".join(image_urls[1:]),
        "price": f"{amount:.2f} {price['currency_code']}",
        "availability": "in stock" if listing["quantity"] > 0 else "out of stock",
        "condition": "new",
        "brand": BRAND,
        "product_type": product_type,
        "google_product_category": gpc,
        "item_group_id": f"{bird}-{suffix}",
    }


def build_rows(listings):
    return [listing_to_row(listing) for listing in listings]


def write_tsv(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=FIELDNAMES, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def resolve_shop_id(environ):
    """ETSY_SHOP_ID, or the default when it is unset or empty.

    GitHub Actions passes an unset repo variable through as "", so an empty
    value must fall back too, not only a missing one.
    """
    return environ.get("ETSY_SHOP_ID", "").strip() or DEFAULT_SHOP_ID


def main():
    api_key = os.environ.get("ETSY_API_KEY")
    if not api_key:
        sys.exit(
            "ETSY_API_KEY is not set. This script needs an Etsy API keystring "
            "with shop read access — see the PR description for the exact "
            "steps to create one and add it as a repo secret."
        )
    shop_id = resolve_shop_id(os.environ)

    listings = fetch_active_listings(shop_id, api_key)
    rows = build_rows(listings)
    if not rows:
        sys.exit("Etsy returned zero active listings — refusing to write an empty feed.")

    write_tsv(rows, "feed.tsv")
    print(f"wrote feed.tsv with {len(rows)} rows")


if __name__ == "__main__":
    main()
