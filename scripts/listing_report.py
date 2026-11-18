#!/usr/bin/env python3
"""Rank the listings that gained the most views over the last 7 days.

Reads data/listing_stats.csv (written daily by listing_stats.py) and writes
reports/most-viewed-unsold.md once 7 consecutive dates exist. With --sales
PATH, an Etsy Order Items CSV export, listings that sold in the 60 days
before the report date are left out.

Only the `Listing ID` and `Sale Date` columns of the export are read. The
rest holds buyer names and addresses and is never kept or printed.
"""

import argparse
import csv
import datetime
import os
import sys

WINDOW_DAYS = 7
SALES_DAYS = 60
TOP_N = 10
STATS_PATH = "data/listing_stats.csv"
REPORT_PATH = "reports/most-viewed-unsold.md"

# Etsy exports US-style dates (MM/DD/YY); ISO is accepted too.
SALE_DATE_FORMATS = ("%m/%d/%y", "%m/%d/%Y", "%Y-%m-%d")


def read_stats(path):
    """{date: {listing_id: row}} with date as datetime.date and views/favorites as int."""
    by_date = {}
    with open(path, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            date = datetime.date.fromisoformat(row["date"])
            by_date.setdefault(date, {})[row["listing_id"]] = {
                "title": row["title"],
                "views": int(row["views"]),
                "num_favorers": int(row["num_favorers"]),
            }
    return by_date


def consecutive_window(dates, length=WINDOW_DAYS):
    """(window, run): the last `length` days ending at the newest date when all
    exist, else None; `run` is how many consecutive dates end at the newest."""
    newest = max(dates)
    run = 0
    while newest - datetime.timedelta(days=run) in dates:
        run += 1
    if run < length:
        return None, run
    return [newest - datetime.timedelta(days=offset) for offset in range(length - 1, -1, -1)], run


def parse_sale_date(value, line):
    for fmt in SALE_DATE_FORMATS:
        try:
            return datetime.datetime.strptime(value.strip(), fmt).date()
        except ValueError:
            pass
    # Only the date field is echoed, never the row: it sits beside buyer data.
    sys.exit(
        f"sales export line {line}: cannot read Sale Date {value[:20]!r}; "
        f"expected one of {', '.join(SALE_DATE_FORMATS)}"
    )


def load_last_sales(path, report_date):
    """{listing_id: newest sale date on or before report_date}, from the two
    needed columns only. A later sale (export newer than the stats) must not
    hide an earlier one that is inside the 60 days."""
    last_sale = {}
    skipped = 0
    with open(path, newline="", encoding="utf-8-sig") as handle:
        reader = csv.reader(handle)
        header = next(reader, [])
        columns = {name.strip().lower(): index for index, name in enumerate(header)}
        missing = [name for name in ("Sale Date", "Listing ID") if name.lower() not in columns]
        if missing:
            sys.exit(
                f"sales export {path} has no {' or '.join(repr(m) for m in missing)} column "
                f"(found {len(header)} columns); export Etsy's Order Items CSV"
            )
        date_col, id_col = columns["sale date"], columns["listing id"]
        for row in reader:
            line = reader.line_num
            if len(row) <= max(date_col, id_col) or not row[id_col].strip():
                skipped += 1
                continue
            listing_id = row[id_col].strip()
            sale_date = parse_sale_date(row[date_col], line)
            if sale_date > report_date:
                continue
            if listing_id not in last_sale or sale_date > last_sale[listing_id]:
                last_sale[listing_id] = sale_date
    if skipped:
        print(
            f"warning: skipped {skipped} sales export row(s) with no Listing ID "
            f"or too few columns",
            file=sys.stderr,
        )
    return last_sale


def rank_listings(by_date, window, last_sales=None):
    """(ranked rows, listings missing a day). Active = present on the newest day.

    Gain is newest minus the listing's earliest snapshot in the window, which is
    the window start unless the listing is missing that day. With last_sales,
    listings with a sale on or after report date - 60 days are dropped.
    """
    report_date = window[-1]
    cutoff = report_date - datetime.timedelta(days=SALES_DAYS)
    ranked = []
    gaps = []
    for listing_id, latest in by_date[report_date].items():
        snapshots = [(d, by_date[d][listing_id]) for d in window if listing_id in by_date[d]]
        absent = [d for d in window if listing_id not in by_date[d]]
        if absent:
            gaps.append((listing_id, latest["title"], absent))

        last_sale = None
        if last_sales is not None:
            last_sale = last_sales.get(listing_id)
            if last_sale is not None and last_sale >= cutoff:
                continue

        first = snapshots[0][1]
        ranked.append(
            {
                "listing_id": listing_id,
                "title": latest["title"],
                "views_gained": latest["views"] - first["views"],
                "favorites_gained": latest["num_favorers"] - first["num_favorers"],
                "last_sale": last_sale,
            }
        )
    ranked.sort(key=lambda r: (-r["views_gained"], -r["favorites_gained"], r["listing_id"]))
    return ranked[:TOP_N], gaps


def cell(text):
    """Title text safe inside a markdown table cell and link label."""
    for char in ("\\", "|", "[", "]"):
        text = text.replace(char, "\\" + char)
    return " ".join(text.split())


def render_report(window, ranked, gaps, sales_checked):
    start, end = window[0], window[-1]
    cutoff = end - datetime.timedelta(days=SALES_DAYS)
    lines = [
        f"# Most-viewed listings with no recent sale ({end.isoformat()})",
        "",
    ]
    if sales_checked:
        lines += [
            f"Listings with a sale from {cutoff.isoformat()} to {end.isoformat()} "
            f"({SALES_DAYS} days before the report date, inclusive) are left out.",
            "",
        ]
    else:
        lines += [
            "**Sales were not checked.** No `--sales` export was given, so this ranks "
            "views alone and may include listings that sold recently.",
            "",
        ]
    lines += [
        f"Views and favorites gained are the change from {start.isoformat()} to "
        f"{end.isoformat()}, the {WINDOW_DAYS} daily snapshots in a row "
        f"({WINDOW_DAYS - 1} days of change). Top {TOP_N}.",
        "",
        "| # | Listing | Views gained | Favorites gained | Last sale |",
        "|---|---|---|---|---|",
    ]
    for rank, row in enumerate(ranked, start=1):
        if not sales_checked:
            last_sale = "not checked"
        else:
            last_sale = row["last_sale"].isoformat() if row["last_sale"] else "none in export"
        lines.append(
            f"| {rank} | [{cell(row['title'])}](https://www.etsy.com/listing/{row['listing_id']}) "
            f"| {row['views_gained']} | {row['favorites_gained']} | {last_sale} |"
        )
    lines.append("")

    lines += ["## Active listings missing from a day in the window", ""]
    if gaps:
        lines.append(
            "Their gains run from the earliest day they have; the ranking above may "
            "understate them."
        )
        lines.append("")
        for listing_id, title, absent in gaps:
            days = ", ".join(d.isoformat() for d in absent)
            lines.append(f"- [{cell(title)}](https://www.etsy.com/listing/{listing_id}): missing {days}")
    else:
        lines.append("None.")
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--sales", metavar="PATH", help="Etsy Order Items CSV export")
    parser.add_argument("--stats", default=STATS_PATH, help=argparse.SUPPRESS)
    parser.add_argument(
        "--out",
        default=REPORT_PATH,
        help=f"report path (default {REPORT_PATH}, which the daily workflow overwrites)",
    )
    args = parser.parse_args(argv)

    by_date = read_stats(args.stats) if os.path.exists(args.stats) else {}
    if not by_date:
        print(f"0 dates in {args.stats}; need {WINDOW_DAYS} consecutive")
        return 0
    window, run = consecutive_window(by_date)
    if window is None:
        print(
            f"{len(by_date)} date(s) in {args.stats}, {run} consecutive up to "
            f"{max(by_date).isoformat()}; need {WINDOW_DAYS} consecutive"
        )
        return 0

    last_sales = load_last_sales(args.sales, window[-1]) if args.sales else None
    ranked, gaps = rank_listings(by_date, window, last_sales)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as handle:
        handle.write(render_report(window, ranked, gaps, last_sales is not None))
    print(f"wrote {args.out}: {len(ranked)} listings, {len(gaps)} with missing days")
    return 0


if __name__ == "__main__":
    sys.exit(main())
