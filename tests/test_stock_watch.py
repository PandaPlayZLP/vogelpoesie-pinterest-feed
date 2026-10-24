import contextlib
import io
import os
import subprocess
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import stock_watch

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "stock_watch.json")


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

    def test_quantity_2_flagged_50_passes(self):
        items = [
            (1, "low", stock_watch.effective_quantity({"state": "active", "quantity": 2})),
            (2, "ok", stock_watch.effective_quantity({"state": "active", "quantity": 50})),
        ]
        self.assertEqual(stock_watch.find_low(items, 5), [(1, "low", 2)])

    def test_missing_api_key_exits_nonzero_naming_secret(self):
        env = {
            k: v
            for k, v in os.environ.items()
            if k not in ("ETSY_API_KEY", "ETSY_SHARED_SECRET")
        }
        script = os.path.join(os.path.dirname(__file__), "..", "scripts", "stock_watch.py")
        result = subprocess.run(
            [sys.executable, script], env=env, capture_output=True, text=True
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ETSY_API_KEY", result.stderr)
        self.assertIn("ETSY_SHARED_SECRET", result.stderr)

    def test_sends_keystring_and_shared_secret_header(self):
        session = mock.Mock()
        session.headers = {}
        response = mock.Mock()
        response.json.return_value = {"state": "active", "quantity": 50}
        session.get.return_value = response
        env = {"ETSY_API_KEY": "keystring1", "ETSY_SHARED_SECRET": "secret1"}
        with mock.patch.dict(os.environ, env), mock.patch.object(
            stock_watch.requests, "Session", return_value=session
        ), mock.patch.object(stock_watch, "CONFIG_PATH", CONFIG_PATH), contextlib.redirect_stdout(
            io.StringIO()
        ):
            stock_watch.main()
        self.assertEqual(session.headers["x-api-key"], "keystring1:secret1")


if __name__ == "__main__":
    unittest.main()
