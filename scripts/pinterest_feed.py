#!/usr/bin/env python3
"""Build feed.tsv (Pinterest catalog feed) from the live Etsy shop listings."""

import argparse
import csv
import datetime
import os
import re
import sys

import requests

import listing_report
from etsy_auth import api_key_header, check_response

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


RUN_LOG_PATH = "data/feed_runs.csv"
RUN_LOG_FIELDS = [
    "run_date",
    "snapshot_date",
    "days_of_data",
    "ordering_mode",
    "notes",
    "top5_ids",
]
MODE_VIEWS = "views-7day"
MODE_CURRENT = "current"

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
        check_response(response)
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
    """One feed row, or None when the title matches no rule or has no image."""
    title = clean_text(listing["title"])
    bird = slugify(title.split(" ")[0])
    match = classify(title)
    if match is None:
        return None
    product_type, gpc, suffix = match

    images = sorted(listing.get("images", []), key=lambda img: img.get("rank", 0))
    image_urls = [img["url_fullxfull"] for img in images if img.get("url_fullxfull")]
    if not image_urls:
        return None

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
        "image_link": image_urls[0],
        "additional_image_link": ",".join(image_urls[1:]),
        "price": f"{amount:.2f} {price['currency_code']}",
        "availability": "in stock" if listing["quantity"] > 0 else "out of stock",
        "condition": "new",
        "brand": BRAND,
        "product_type": product_type,
        "google_product_category": gpc,
        "item_group_id": f"{bird}-{suffix}",
    }


def build_rows(listings, skipped=None):
    """Feed rows for every usable listing. Listings with an unmatched title or
    no image are logged to stderr and skipped, so one new product type or a
    photo still uploading cannot kill the feed (Pinterest rejects rows without
    image_link). `skipped`, if given, is a dict that gets "no rule" and
    "no image" counts."""
    skipped = skipped if skipped is not None else {}
    skipped.update({"no rule": 0, "no image": 0})
    rows = []
    for listing in listings:
        row = listing_to_row(listing)
        if row is not None:
            rows.append(row)
            continue
        # ::warning:: surfaces the skip as an annotation on the Actions run.
        title = clean_text(listing["title"])
        if classify(title) is None:
            skipped["no rule"] += 1
            reason = f"no product rule matches title {title!r}"
        else:
            skipped["no image"] += 1
            reason = "no image"
        print(f"::warning::skipped listing {listing['listing_id']}: {reason}", file=sys.stderr)
    return rows


def write_tsv(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=FIELDNAMES, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def utc_today():
    return datetime.datetime.now(datetime.timezone.utc).date()


def load_stats(path):
    """({date: {listing_id: row}}, problem). An unreadable history must not
    take the feed down: the feed keeps its current order and the problem goes
    to the run log."""
    if not os.path.exists(path):
        return {}, None
    try:
        return listing_report.read_stats(path), None
    except (OSError, ValueError, KeyError) as error:
        return {}, f"stats unreadable ({type(error).__name__}: {error})"


def order_listings(rows, by_date, today, sales_path=None):
    """(ordered rows, info) for the feed's `rows`.

    With 7 consecutive days of stats, listings that did not sell in the last
    60 days come first, ranked by listing_report.rank_listings (7-day view
    gain). Every other row (sold, or missing from the newest snapshot)
    follows in its current order. Rows are only moved, never dropped. Under 7
    consecutive days the current order is kept.

    `info` has snapshot_date (newest snapshot, "" if none), days (consecutive
    days ending at it), mode and notes.
    """
    notes = []
    window, days, snapshot = None, 0, None
    if by_date:
        snapshot = max(by_date)
        window, days = listing_report.consecutive_window(by_date)
        if snapshot != today:
            notes.append("stale snapshot")
    if window is None:
        notes.append(f"{days} of {listing_report.WINDOW_DAYS} days")
        ordered, mode = list(rows), MODE_CURRENT
    else:
        last_sales = None
        if sales_path:
            last_sales = listing_report.load_last_sales(sales_path, window[-1])
            notes.append("sales checked")
        # Stats keys are strings, feed ids are ints.
        ranked, _gaps = listing_report.rank_listings(by_date, window, last_sales, limit=None)
        position = {row["listing_id"]: index for index, row in enumerate(ranked)}
        unsold = [row for row in rows if str(row["id"]) in position]
        unsold.sort(key=lambda row: position[str(row["id"])])
        rest = [row for row in rows if str(row["id"]) not in position]
        ordered, mode = unsold + rest, MODE_VIEWS
    if not sales_path:
        notes.append("sales not checked")
    info = {
        "snapshot_date": snapshot.isoformat() if snapshot else "",
        "days": days,
        "mode": mode,
        "notes": notes,
    }
    return ordered, info


def append_run_log(path, run_date, info, rows):
    """Append one row for this run; the header is written with the first one."""
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    is_new = not os.path.exists(path) or os.path.getsize(path) == 0
    with open(path, "a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=RUN_LOG_FIELDS, lineterminator="\n")
        if is_new:
            writer.writeheader()
        writer.writerow(
            {
                "run_date": run_date.isoformat(),
                "snapshot_date": info["snapshot_date"],
                "days_of_data": info["days"],
                "ordering_mode": info["mode"],
                "notes": "; ".join(info["notes"]),
                "top5_ids": ";".join(str(row["id"]) for row in rows[:5]),
            }
        )


def resolve_shop_id(environ):
    """ETSY_SHOP_ID, or the default when it is unset or empty.

    GitHub Actions passes an unset repo variable through as "", so an empty
    value must fall back too, not only a missing one.
    """
    return environ.get("ETSY_SHOP_ID", "").strip() or DEFAULT_SHOP_ID


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sales",
        metavar="PATH",
        help="Etsy Order Items CSV export (listing_report format); listings "
        "sold in the last 60 days go after the unsold ones",
    )
    parser.add_argument("--stats", default=listing_report.STATS_PATH, help=argparse.SUPPRESS)
    parser.add_argument("--runs-log", default=RUN_LOG_PATH, help=argparse.SUPPRESS)
    parser.add_argument("--out", default="feed.tsv", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    api_key_value = api_key_header(os.environ)
    shop_id = resolve_shop_id(os.environ)
    today = utc_today()

    listings = fetch_active_listings(shop_id, api_key_value)
    if not listings:
        sys.exit("Etsy returned zero active listings — refusing to write an empty feed.")
    skipped = {}
    rows = build_rows(listings, skipped)
    if not rows:
        sys.exit(
            f"none of {len(listings)} active listings is feedable "
            f"(skipped: {skipped['no rule']} no rule, {skipped['no image']} no image) — "
            "refusing to write an empty feed."
        )

    by_date, stats_problem = load_stats(args.stats)
    rows, info = order_listings(rows, by_date, today, args.sales)
    if stats_problem:
        info["notes"].insert(0, stats_problem)
        print(f"::warning::{stats_problem}", file=sys.stderr)

    write_tsv(rows, args.out)
    # Only a finished build is logged.
    append_run_log(args.runs_log, today, info, rows)
    print(
        f"wrote {args.out} with {len(rows)} rows "
        f"(skipped: {skipped['no rule']} no rule, {skipped['no image']} no image)"
    )
    print(f"ordering: {info['mode']}; {'; '.join(info['notes'])}")


if __name__ == "__main__":
    main()
