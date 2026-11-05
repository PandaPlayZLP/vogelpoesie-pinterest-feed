#!/usr/bin/env python3
"""Check a feed.tsv fetched from the public URL: header, rows, images.

Usage: check_served_feed.py PATH

Exits 1 with an `::error::` line (GitHub Actions annotation) when the header
lacks id/title/image_link, there are no data rows, or any row has an empty
image_link. Per-row only: it never compares against the committed feed.tsv,
because the CDN purge is asynchronous and a slightly stale copy is fine.
"""

import csv
import sys

REQUIRED_COLUMNS = ("id", "title", "image_link")


def check_feed(path):
    """Return (row_count, error); error is None when the feed is fine."""
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle, delimiter="\t")
        header = next(reader, None)
        if header is None:
            return 0, "served feed is empty"
        missing = [name for name in REQUIRED_COLUMNS if name not in header]
        if missing:
            return 0, f"served feed header lacks column(s): {', '.join(missing)}"
        id_index = header.index("id")
        image_index = header.index("image_link")

        count = 0
        without_image = []
        for line_no, row in enumerate(reader, start=2):
            if not row:
                continue
            count += 1
            image = row[image_index] if image_index < len(row) else ""
            if not image.strip():
                row_id = row[id_index].strip() if id_index < len(row) else ""
                without_image.append(row_id or f"(row {line_no}, no id)")

    if count == 0:
        return 0, "served feed has a header but no data rows"
    if without_image:
        return count, (
            f"{len(without_image)} of {count} rows have an empty image_link: "
            + ", ".join(without_image)
        )
    return count, None


def main(argv):
    if len(argv) != 2:
        print("usage: check_served_feed.py PATH", file=sys.stderr)
        return 2
    count, error = check_feed(argv[1])
    if error:
        print(f"::error::{error}")
        return 1
    print(f"public feed serves {count} rows, all with an image_link")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
