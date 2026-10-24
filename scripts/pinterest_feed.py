#!/usr/bin/env python3
"""Build feed.tsv (Pinterest catalog feed) from the live Etsy shop listings."""

import csv
import os
import re
import sys

import requests

from etsy_auth import api_key_header

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
    """(product_type, gpc, suffix) for the first matching rule, else None."""
    for keyword, product_type, gpc, suffix in PRODUCT_RULES:
        if keyword.lower() in title.lower():
            return product_type, gpc, suffix
    return None


# Etsy caps both the active-listings page size and the batch lookup at 100.
PAGE_SIZE = 100


def fetch_active_listings(shop_id, api_key_value):
    """Return every active listing for the shop, with images included.

    findAllActiveListingsByShop does not accept `includes`, so images come
    from a second, batched getListingsByListingIds call.
    """
    session = requests.Session()
    session.headers["x-api-key"] = api_key_value

    listing_ids = []
    offset = 0
    while True:
        response = session.get(
            f"{ETSY_API_BASE}/shops/{shop_id}/listings/active",
            params={"limit": PAGE_SIZE, "offset": offset},
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
        results = payload.get("results", [])
        listing_ids.extend(listing["listing_id"] for listing in results)

        offset += len(results)
        if not results or offset >= payload.get("count", 0):
            break

    listings = []
    for start in range(0, len(listing_ids), PAGE_SIZE):
        chunk = listing_ids[start : start + PAGE_SIZE]
        response = session.get(
            f"{ETSY_API_BASE}/listings/batch",
            params={
                "listing_ids": ",".join(str(listing_id) for listing_id in chunk),
                "includes": "Images",
            },
            timeout=30,
        )
        response.raise_for_status()
        listings.extend(
            listing
            for listing in response.json().get("results", [])
            # A listing can go inactive between the two calls.
            if listing.get("state", "active") == "active"
        )
    # Keep the active-listings order so feed.tsv does not churn between runs.
    position = {listing_id: index for index, listing_id in enumerate(listing_ids)}
    listings.sort(key=lambda listing: position.get(listing["listing_id"], len(position)))
    return listings


def listing_to_row(listing):
    """One feed row, or None when no product rule matches the title."""
    title = clean_text(listing["title"])
    bird = slugify(title.split(" ")[0])
    match = classify(title)
    if match is None:
        return None
    product_type, gpc, suffix = match

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
    """Feed rows for every classifiable listing; unmatched titles are logged
    to stderr and skipped so one new product type cannot kill the feed."""
    rows = []
    for listing in listings:
        row = listing_to_row(listing)
        if row is None:
            # ::warning:: surfaces the skip as an annotation on the Actions run.
            print(
                f"::warning::skipped listing {listing['listing_id']}: no product rule "
                f"matches title {clean_text(listing['title'])!r}",
                file=sys.stderr,
            )
            continue
        rows.append(row)
    return rows


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
    api_key_value = api_key_header(os.environ)
    shop_id = resolve_shop_id(os.environ)

    listings = fetch_active_listings(shop_id, api_key_value)
    if not listings:
        sys.exit("Etsy returned zero active listings — refusing to write an empty feed.")
    rows = build_rows(listings)
    if not rows:
        sys.exit(
            f"none of {len(listings)} active listings matches a product rule — "
            "refusing to write an empty feed."
        )

    write_tsv(rows, "feed.tsv")
    print(f"wrote feed.tsv with {len(rows)} rows")


if __name__ == "__main__":
    main()
