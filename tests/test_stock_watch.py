import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import stock_watch


class StockWatchTest(unittest.TestCase):
    def test_find_low_is_strictly_below_threshold(self):
        items = [(1, "a", 4), (2, "b", 5), (3, "c", 0)]
        self.assertEqual(stock_watch.find_low(items, 5), [(1, "a", 4), (3, "c", 0)])

    def test_inactive_listing_counts_as_zero(self):
        self.assertEqual(
            stock_watch.effective_quantity({"state": "sold_out", "quantity": 9}), 0
        )
        self.assertEqual(
            stock_watch.effective_quantity({"state": "active", "quantity": 9}), 9
        )

    def test_report_lists_each_listing_with_quantity(self):
        report = stock_watch.render_report([(7, "Mug", 2)], 5)
        self.assertIn("etsy.com/listing/7", report)
        self.assertIn(": 2", report)


if __name__ == "__main__":
    unittest.main()
