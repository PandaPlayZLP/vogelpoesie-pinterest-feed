import contextlib
import datetime
import io
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import listing_report
import listing_stats


def listing(listing_id, views=10, favorers=2, title=None, **extra):
    return {
        "listing_id": listing_id,
        "title": title or f"Bird {listing_id} Poster",
        "views": views,
        "num_favorers": favorers,
        "state": "active",
        **extra,
    }


class TempDirTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = tmp.name

    def path(self, *parts):
        return os.path.join(self.dir, *parts)


class ListingStatsTest(TempDirTest):
    def read(self, path):
        with open(path, encoding="utf-8") as handle:
            return handle.read()

    def test_appends_a_row_per_listing_and_creates_the_directory(self):
        path = self.path("data", "listing_stats.csv")
        rows = listing_stats.build_rows([listing(1, 5, 1), listing(2, 7, 3)], "2026-11-14")
        listing_stats.write_stats(rows, "2026-11-14", path)
        rows = listing_stats.build_rows([listing(1, 6, 1), listing(2, 9, 3)], "2026-11-15")
        listing_stats.write_stats(rows, "2026-11-15", path)

        stored = listing_stats.read_stats(path)
        self.assertEqual(
            [(r["date"], r["listing_id"], r["views"]) for r in stored],
            [
                ("2026-11-14", "1", "5"),
                ("2026-11-14", "2", "7"),
                ("2026-11-15", "1", "6"),
                ("2026-11-15", "2", "9"),
            ],
        )
        self.assertEqual(
            self.read(path).splitlines()[0], "date,listing_id,title,views,num_favorers,state"
        )

    def test_same_day_rerun_replaces_that_dates_rows(self):
        path = self.path("listing_stats.csv")
        listing_stats.write_stats(
            listing_stats.build_rows([listing(1, 5), listing(2, 7)], "2026-11-14"),
            "2026-11-14",
            path,
        )
        for views in (20, 30):
            listing_stats.write_stats(
                listing_stats.build_rows([listing(1, views)], "2026-11-15"), "2026-11-15", path
            )
        listing_stats.write_stats(
            listing_stats.build_rows([listing(1, 6), listing(2, 8)], "2026-11-14"),
            "2026-11-14",
            path,
        )

        stored = [(r["date"], r["listing_id"], r["views"]) for r in listing_stats.read_stats(path)]
        self.assertEqual(
            stored,
            [("2026-11-14", "1", "6"), ("2026-11-14", "2", "8"), ("2026-11-15", "1", "30")],
        )

    def test_missing_field_exits_naming_field_and_listing_and_leaves_file_untouched(self):
        path = self.path("listing_stats.csv")
        listing_stats.write_stats(
            listing_stats.build_rows([listing(1)], "2026-11-14"), "2026-11-14", path
        )
        before = self.read(path)

        for field in ("views", "num_favorers"):
            broken = listing(4242)
            del broken[field]
            with mock.patch.dict(
                os.environ, {"ETSY_API_KEY": "key", "ETSY_SHARED_SECRET": "secret"}
            ), mock.patch.object(
                listing_stats, "fetch_active_listings", return_value=[listing(1), broken]
            ):
                with self.assertRaises(SystemExit) as caught:
                    listing_stats.main(path)
            message = str(caught.exception)
            self.assertIn(field, message)
            self.assertIn("4242", message)
            self.assertEqual(self.read(path), before)

    def test_null_field_counts_as_missing(self):
        with self.assertRaises(SystemExit) as caught:
            listing_stats.build_rows([listing(77, views=None)], "2026-11-14")
        self.assertIn("views", str(caught.exception))
        self.assertIn("77", str(caught.exception))

    def test_zero_views_is_recorded_not_rejected(self):
        rows = listing_stats.build_rows([listing(1, views=0, favorers=0)], "2026-11-14")
        self.assertEqual((rows[0]["views"], rows[0]["num_favorers"]), (0, 0))

    def test_zero_listings_exits_without_writing(self):
        path = self.path("listing_stats.csv")
        with mock.patch.dict(
            os.environ, {"ETSY_API_KEY": "key", "ETSY_SHARED_SECRET": "secret"}
        ), mock.patch.object(listing_stats, "fetch_active_listings", return_value=[]):
            with self.assertRaises(SystemExit):
                listing_stats.main(path)
        self.assertFalse(os.path.exists(path))

    def test_fetch_pages_until_count_reached(self):
        pages = [
            {"count": 3, "results": [listing(1), listing(2)]},
            {"count": 3, "results": [listing(3)]},
        ]
        responses = []
        for payload in pages:
            response = mock.Mock(ok=True)
            response.json.return_value = payload
            responses.append(response)
        session = mock.Mock()
        session.headers = {}
        session.get.side_effect = responses
        with mock.patch.object(listing_stats.requests, "Session", return_value=session):
            result = listing_stats.fetch_active_listings("123", "k:s")

        self.assertEqual([l["listing_id"] for l in result], [1, 2, 3])
        self.assertEqual(session.headers["x-api-key"], "k:s")
        offsets = [call.kwargs["params"]["offset"] for call in session.get.call_args_list]
        self.assertEqual(offsets, [0, 2])
        for call in session.get.call_args_list:
            self.assertTrue(call.args[0].endswith("/shops/123/listings/active"))


def seed_stats(path, days=7, listings=12, start=datetime.date(2026, 11, 10), skip=()):
    """Listing n gains n views and n // 2 favorites a day, from a base of 1000 * n.

    `skip` is a set of (day index, listing id) pairs to leave out.
    """
    for day in range(days):
        date = (start + datetime.timedelta(days=day)).isoformat()
        rows = listing_stats.build_rows(
            [
                listing(n, 1000 * n + n * day, n + (n // 2) * day, title=f"Bird {n}")
                for n in range(1, listings + 1)
                if (day, n) not in skip
            ],
            date,
        )
        listing_stats.write_stats(rows, date, path)


# Invented data. Buyer is here to prove it never reaches the report.
SALES_CSV = """﻿Sale Date,Order ID,Buyer,listing id,Quantity
11/16/26,1,Quentin Fiktiv,12,1
09/17/26,2,Quentin Fiktiv,11,1
09/16/26,3,Quentin Fiktiv,10,1
10/20/26,4,Maxi Muster,9,2
01/05/26,5,Maxi Muster,8,1
09/01/26,5,Maxi Muster,8,1
12/24/26,6,Maxi Muster,7,1
10/01/26,8,Maxi Muster,6,1
12/24/26,9,Maxi Muster,6,1
,7,Maxi Muster,,1
"""


class ListingReportTest(TempDirTest):
    def run_report(self, *extra):
        self.stats = self.path("data", "listing_stats.csv")
        self.out = self.path("reports", "most-viewed-unsold.md")
        argv = ["--stats", self.stats, "--out", self.out, *extra]
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = listing_report.main(argv)
        return code, stdout.getvalue()

    def report(self):
        with open(self.out, encoding="utf-8") as handle:
            return handle.read()

    def seed(self, **kwargs):
        seed_stats(self.path("data", "listing_stats.csv"), **kwargs)

    def sales(self, content=SALES_CSV):
        path = self.path("EtsySoldOrderItems2026-11.csv")
        with open(path, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
        return path

    def test_ranks_ten_of_twelve_by_views_gained_over_the_window(self):
        self.seed()
        code, _ = self.run_report()
        text = self.report()

        self.assertEqual(code, 0)
        rows = [line for line in text.splitlines() if line.startswith("| ") and "etsy.com" in line]
        self.assertEqual(len(rows), 10)
        # Day 0 to day 6 is 6 days of change: listing 12 gains 72 views, 36 favorites.
        self.assertIn("| 1 | [Bird 12](https://www.etsy.com/listing/12) | 72 | 36 |", rows[0])
        self.assertIn("| 10 | [Bird 3](https://www.etsy.com/listing/3) | 18 | 6 |", rows[-1])
        self.assertNotIn("Bird 1](", text)
        self.assertNotIn("Bird 2](", text)
        self.assertIn("2026-11-10 to 2026-11-16", text)

    def test_without_sales_the_report_says_sales_were_not_checked(self):
        self.seed()
        self.run_report()
        text = self.report()
        self.assertIn("Sales were not checked", text)
        self.assertIn("not checked |", text)

    def test_sales_filter_drops_listings_sold_within_60_days(self):
        self.seed()
        self.run_report("--sales", self.sales())
        text = self.report()

        self.assertNotIn("Sales were not checked", text)
        # Report date 2026-11-16, cutoff 2026-09-17 inclusive.
        self.assertNotIn("Bird 12](", text, "sold on the report date")
        self.assertNotIn("Bird 11](", text, "sold exactly 60 days before")
        self.assertNotIn("Bird 9](", text, "sold 27 days before")
        self.assertIn("Bird 10](https://www.etsy.com/listing/10) | 60 | 30 | 2026-09-16 |", text)
        self.assertIn("Bird 8](https://www.etsy.com/listing/8) | 48 | 24 | 2026-09-01 |", text)
        # A sale dated after the report date is not a sale before it.
        self.assertIn("Bird 7](https://www.etsy.com/listing/7) | 42 | 18 | none in export |", text)
        # In-window sale plus a later one: the later one must not hide it.
        self.assertNotIn("Bird 6](", text)
        rows = [line for line in text.splitlines() if line.startswith("| ") and "etsy.com" in line]
        self.assertEqual(len(rows), 8)  # 12 listings minus 4 sold

    def test_buyer_columns_never_reach_the_report(self):
        self.seed()
        self.run_report("--sales", self.sales())
        text = self.report()
        for private in ("Quentin", "Fiktiv", "Maxi", "Muster"):
            self.assertNotIn(private, text)

    def test_sales_export_without_required_header_fails_clearly(self):
        self.seed()
        path = self.sales("Date,Order ID,Listing\n11/16/26,1,12\n")
        with self.assertRaises(SystemExit) as caught:
            self.run_report("--sales", path)
        message = str(caught.exception)
        self.assertIn("Sale Date", message)
        self.assertIn("Listing ID", message)
        self.assertFalse(os.path.exists(self.out))

    def test_unreadable_sale_date_names_line_but_not_buyer(self):
        self.seed()
        path = self.sales("Sale Date,Buyer,Listing ID\nsoon,Quentin Fiktiv,12\n")
        with self.assertRaises(SystemExit) as caught:
            self.run_report("--sales", path)
        self.assertIn("line 2", str(caught.exception))
        self.assertNotIn("Quentin", str(caught.exception))

    def test_listings_missing_a_day_are_listed(self):
        self.seed(skip={(0, 5), (3, 5), (3, 6)})
        self.run_report()
        text = self.report()
        section = text.split("## Active listings missing")[1]
        self.assertIn("Bird 5](https://www.etsy.com/listing/5): missing 2026-11-10, 2026-11-13", section)
        self.assertIn("Bird 6](https://www.etsy.com/listing/6): missing 2026-11-13", section)
        self.assertNotIn("Bird 7", section)

    def test_title_markdown_is_escaped(self):
        path = self.path("data", "listing_stats.csv")
        for day in range(7):
            date = (datetime.date(2026, 11, 10) + datetime.timedelta(days=day)).isoformat()
            listing_stats.write_stats(
                listing_stats.build_rows([listing(1, day, 0, title="A] [b | c")], date), date, path
            )
        self.run_report()
        self.assertIn("[A\\] \\[b \\| c](", self.report())

    def test_no_missing_days_says_none(self):
        self.seed()
        self.run_report()
        self.assertTrue(self.report().rstrip().endswith("None."))

    def test_under_seven_dates_prints_count_and_writes_nothing(self):
        self.seed(days=6)
        code, output = self.run_report()
        self.assertEqual(code, 0)
        self.assertIn("6 date(s)", output)
        self.assertFalse(os.path.exists(self.out))

    def test_missing_stats_file_exits_zero_and_writes_nothing(self):
        code, output = self.run_report()
        self.assertEqual(code, 0)
        self.assertIn("0 dates", output)
        self.assertFalse(os.path.exists(self.out))

    def test_seven_dates_with_a_gap_are_not_consecutive(self):
        self.seed(days=4)
        seed_stats(self.path("data", "listing_stats.csv"), days=3, start=datetime.date(2026, 11, 15))
        code, output = self.run_report()
        self.assertEqual(code, 0)
        self.assertIn("7 date(s)", output)
        self.assertIn("3 consecutive", output)
        self.assertFalse(os.path.exists(self.out))

    def test_window_is_the_newest_seven_days_when_more_exist(self):
        self.seed(days=9)
        self.run_report()
        self.assertIn("2026-11-12 to 2026-11-18", self.report())


if __name__ == "__main__":
    unittest.main()
