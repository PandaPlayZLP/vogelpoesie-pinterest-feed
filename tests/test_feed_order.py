import contextlib
import csv
import datetime
import io
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import listing_report
import pinterest_feed

TODAY = datetime.date(2026, 11, 18)
SALES_HEADER = "Sale Date,Listing ID,Buyer\n"


def stats(days, views_by_id, newest=TODAY):
    """{date: {listing_id (str): row}} for `days` consecutive days ending at
    `newest`. views_by_id maps id -> (views on the first day, gain per day)."""
    by_date = {}
    for offset in range(days):
        date = newest - datetime.timedelta(days=days - 1 - offset)
        by_date[date] = {
            str(listing_id): {
                "title": f"Bird {listing_id} Poster",
                "views": start + offset * step,
                "num_favorers": 0,
            }
            for listing_id, (start, step) in views_by_id.items()
        }
    return by_date


def feed_row(listing_id):
    return {"id": listing_id, "title": f"Bird {listing_id} Poster"}


def ids(rows):
    return [row["id"] for row in rows]


# 1 gains 1/day, 2 gains 9/day, 3 gains 5/day, 4 gains 7/day.
VIEWS = {1: (100, 1), 2: (100, 9), 3: (100, 5), 4: (100, 7)}


class OrderListingsTest(unittest.TestCase):
    def test_unsold_listings_follow_7_day_view_gain(self):
        rows = [feed_row(i) for i in (1, 2, 3, 4)]
        ordered, info = pinterest_feed.order_listings(rows, stats(7, VIEWS), TODAY)
        self.assertEqual(ids(ordered), [2, 4, 3, 1])
        self.assertEqual(info["mode"], pinterest_feed.MODE_VIEWS)
        self.assertEqual(info["days"], 7)
        self.assertEqual(info["snapshot_date"], "2026-11-18")

    def test_int_feed_ids_match_string_stats_ids(self):
        # The stats CSV yields string ids, the Etsy feed rows ints.
        by_date = stats(7, {2: (0, 9), 1: (0, 1)})
        self.assertTrue(all(isinstance(key, str) for key in by_date[TODAY]))
        ordered, _ = pinterest_feed.order_listings([feed_row(1), feed_row(2)], by_date, TODAY)
        self.assertEqual(ids(ordered), [2, 1])

    def test_sold_and_missing_listings_follow_in_current_order(self):
        # 9 is in the feed but not in the stats; 2 sold on 2026-11-01.
        rows = [feed_row(i) for i in (9, 1, 2, 3, 4)]
        with tempfile.TemporaryDirectory() as tmp:
            sales = os.path.join(tmp, "sales.csv")
            with open(sales, "w") as handle:
                handle.write(SALES_HEADER + "11/01/26,2,x\n" + "08/01/26,4,x\n")
            ordered, info = pinterest_feed.order_listings(rows, stats(7, VIEWS), TODAY, sales)
        # 4 sold too long ago to count; 9 and 2 keep their relative order.
        self.assertEqual(ids(ordered), [4, 3, 1, 9, 2])
        self.assertIn("sales checked", info["notes"])
        self.assertNotIn("sales not checked", info["notes"])

    def test_no_row_is_dropped_or_duplicated(self):
        rows = [feed_row(i) for i in (7, 1, 8, 2, 3, 4)]
        ordered, _ = pinterest_feed.order_listings(rows, stats(7, VIEWS), TODAY)
        self.assertEqual(sorted(ids(ordered)), sorted(ids(rows)))
        self.assertEqual(ids(ordered)[-2:], [7, 8])

    def test_under_7_days_keeps_current_order_and_says_how_many(self):
        rows = [feed_row(i) for i in (1, 2, 3, 4)]
        ordered, info = pinterest_feed.order_listings(rows, stats(5, VIEWS), TODAY)
        self.assertEqual(ordered, rows)
        self.assertEqual(info["mode"], pinterest_feed.MODE_CURRENT)
        self.assertEqual(info["days"], 5)
        self.assertIn("5 of 7 days", info["notes"])

    def test_gap_in_the_dates_counts_only_the_run_ending_at_the_newest(self):
        by_date = stats(8, VIEWS)
        del by_date[TODAY - datetime.timedelta(days=3)]
        rows = [feed_row(i) for i in (1, 2)]
        ordered, info = pinterest_feed.order_listings(rows, by_date, TODAY)
        self.assertEqual(ordered, rows)
        self.assertIn("3 of 7 days", info["notes"])

    def test_no_stats_at_all(self):
        rows = [feed_row(1), feed_row(2)]
        ordered, info = pinterest_feed.order_listings(rows, {}, TODAY)
        self.assertEqual(ordered, rows)
        self.assertEqual(info["snapshot_date"], "")
        self.assertIn("0 of 7 days", info["notes"])
        self.assertNotIn("stale snapshot", info["notes"])

    def test_stale_snapshot_is_noted_and_still_used(self):
        newest = TODAY - datetime.timedelta(days=1)
        rows = [feed_row(i) for i in (1, 2)]
        ordered, info = pinterest_feed.order_listings(rows, stats(7, VIEWS, newest), TODAY)
        self.assertEqual(ids(ordered), [2, 1])
        self.assertIn("stale snapshot", info["notes"])
        self.assertEqual(info["snapshot_date"], "2026-11-17")

    def test_current_snapshot_is_not_stale(self):
        _, info = pinterest_feed.order_listings([feed_row(1)], stats(7, VIEWS), TODAY)
        self.assertNotIn("stale snapshot", info["notes"])

    def test_without_sales_the_log_says_so(self):
        _, info = pinterest_feed.order_listings([feed_row(1)], stats(7, VIEWS), TODAY)
        self.assertIn("sales not checked", info["notes"])
        _, info = pinterest_feed.order_listings([feed_row(1)], stats(3, VIEWS), TODAY)
        self.assertIn("sales not checked", info["notes"])

    def test_bad_sales_file_fails_instead_of_ordering_without_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            sales = os.path.join(tmp, "sales.csv")
            with open(sales, "w") as handle:
                handle.write("Foo,Bar\n1,2\n")
            with self.assertRaises(SystemExit):
                pinterest_feed.order_listings([feed_row(1)], stats(7, VIEWS), TODAY, sales)


class RankListingsLimitTest(unittest.TestCase):
    def test_default_stays_top_10_and_none_keeps_all(self):
        views = {i: (0, i) for i in range(1, 16)}
        by_date = stats(7, views)
        window = sorted(by_date)
        ranked, _ = listing_report.rank_listings(by_date, window)
        self.assertEqual(len(ranked), listing_report.TOP_N)
        everything, _ = listing_report.rank_listings(by_date, window, limit=None)
        self.assertEqual(len(everything), 15)
        self.assertEqual(everything[: listing_report.TOP_N], ranked)


class RunLogTest(unittest.TestCase):
    def test_header_once_and_one_row_per_run(self):
        info = {"snapshot_date": "2026-11-18", "days": 7, "mode": "views-7day",
                "notes": ["stale snapshot", "sales not checked"]}
        rows = [feed_row(i) for i in range(1, 8)]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "data", "feed_runs.csv")
            pinterest_feed.append_run_log(path, TODAY, info, rows)
            pinterest_feed.append_run_log(path, TODAY, info, rows)
            with open(path, newline="") as handle:
                logged = list(csv.DictReader(handle))
        self.assertEqual(len(logged), 2)
        self.assertEqual(list(logged[0]), pinterest_feed.RUN_LOG_FIELDS)
        self.assertEqual(logged[0]["run_date"], "2026-11-18")
        self.assertEqual(logged[0]["days_of_data"], "7")
        self.assertEqual(logged[0]["notes"], "stale snapshot; sales not checked")
        self.assertEqual(logged[0]["top5_ids"], "1;2;3;4;5")


def etsy_listing(listing_id):
    return {
        "listing_id": listing_id,
        "title": f"Bird {listing_id} Poster",
        "description": "d",
        "url": f"https://www.etsy.com/listing/{listing_id}/x",
        "quantity": 1,
        "price": {"amount": 1000, "divisor": 100, "currency_code": "EUR"},
        "images": [{"rank": 1, "url_fullxfull": "https://example.invalid/i.jpg"}],
    }


class MainTest(unittest.TestCase):
    def run_main(self, tmp, listings, by_date=None, extra=()):
        stats_path = os.path.join(tmp, "listing_stats.csv")
        if by_date:
            with open(stats_path, "w", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(["date", "listing_id", "title", "views", "num_favorers", "state"])
                for date, listings_on_date in sorted(by_date.items()):
                    for listing_id, row in listings_on_date.items():
                        writer.writerow(
                            [date.isoformat(), listing_id, row["title"], row["views"],
                             row["num_favorers"], "active"]
                        )
        argv = [
            "--stats", stats_path,
            "--runs-log", os.path.join(tmp, "data", "feed_runs.csv"),
            "--out", os.path.join(tmp, "feed.tsv"),
            *extra,
        ]
        with mock.patch.object(pinterest_feed, "fetch_active_listings", return_value=listings), \
             mock.patch.dict(os.environ, {"ETSY_API_KEY": "k", "ETSY_SHARED_SECRET": "s"}), \
             mock.patch.object(pinterest_feed, "utc_today", return_value=TODAY), \
             contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            pinterest_feed.main(argv)

    def read_csv(self, path, delimiter=","):
        with open(path, newline="") as handle:
            return list(csv.DictReader(handle, delimiter=delimiter))

    def test_feed_is_ordered_and_run_is_logged(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.run_main(tmp, [etsy_listing(i) for i in (1, 2, 3, 4)], stats(7, VIEWS))
            feed = self.read_csv(os.path.join(tmp, "feed.tsv"), "\t")
            log = self.read_csv(os.path.join(tmp, "data", "feed_runs.csv"))
        self.assertEqual([row["id"] for row in feed], ["2", "4", "3", "1"])
        self.assertEqual(len(log), 1)
        self.assertEqual(log[0]["ordering_mode"], "views-7day")
        self.assertEqual(log[0]["top5_ids"], "2;4;3;1")
        self.assertEqual(log[0]["notes"], "sales not checked")

    def test_unreadable_stats_keep_the_current_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "listing_stats.csv"), "w") as handle:
                handle.write("not,the,right,header\n1,2,3,4\n")
            self.run_main(tmp, [etsy_listing(i) for i in (1, 2)])
            feed = self.read_csv(os.path.join(tmp, "feed.tsv"), "\t")
            log = self.read_csv(os.path.join(tmp, "data", "feed_runs.csv"))
        self.assertEqual([row["id"] for row in feed], ["1", "2"])
        self.assertIn("stats unreadable", log[0]["notes"])

    def test_failed_build_logs_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(SystemExit):
                self.run_main(tmp, [])
            with self.assertRaises(SystemExit):
                bad = dict(etsy_listing(1), title="Unmatched Thing")
                self.run_main(tmp, [bad])
            with open(os.path.join(tmp, "sales.csv"), "w") as handle:
                handle.write("Foo,Bar\n")
            with self.assertRaises(SystemExit):
                self.run_main(
                    tmp, [etsy_listing(1)], stats(7, VIEWS),
                    ["--sales", os.path.join(tmp, "sales.csv")],
                )
            self.assertFalse(os.path.exists(os.path.join(tmp, "data", "feed_runs.csv")))
            self.assertFalse(os.path.exists(os.path.join(tmp, "feed.tsv")))


if __name__ == "__main__":
    unittest.main()
