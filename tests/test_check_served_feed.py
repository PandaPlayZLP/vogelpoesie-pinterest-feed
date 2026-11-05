import contextlib
import io
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import check_served_feed

HEADER = "id\ttitle\tdescription\tlink\timage_link\tprice"
GOOD_ROW = '1\tOne\t"Long, free text\nwith a newline and a ""quote"""\thttps://x/1\thttps://img/1.jpg\t9 EUR'
OTHER_GOOD_ROW = "2\tTwo\tplain\thttps://x/2\thttps://img/2.jpg\t9 EUR"
NO_IMAGE_ROW = "3\tThree\tplain\thttps://x/3\t\t9 EUR"


def run_check(text):
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "served.tsv")
        with open(path, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = check_served_feed.main(["check_served_feed.py", path])
        return code, out.getvalue()


class CheckServedFeedTest(unittest.TestCase):
    def test_good_feed_passes_and_prints_row_count(self):
        code, out = run_check("\n".join([HEADER, GOOD_ROW, OTHER_GOOD_ROW]) + "\n")
        self.assertEqual(code, 0)
        self.assertIn("serves 2 rows", out)

    def test_single_empty_image_link_fails_naming_the_id(self):
        code, out = run_check(
            "\n".join([HEADER, GOOD_ROW, NO_IMAGE_ROW, OTHER_GOOD_ROW]) + "\n"
        )
        self.assertEqual(code, 1)
        self.assertTrue(out.startswith("::error::"))
        self.assertIn("3", out.split(": ", 1)[1])
        self.assertNotIn("1, 2", out)

    def test_whitespace_only_image_link_fails(self):
        code, _ = run_check(
            "\n".join([HEADER, "4\tFour\td\thttps://x/4\t  \t9 EUR"]) + "\n"
        )
        self.assertEqual(code, 1)

    def test_header_only_fails(self):
        code, out = run_check(HEADER + "\n")
        self.assertEqual(code, 1)
        self.assertIn("::error::", out)
        self.assertIn("no data rows", out)

    def test_missing_required_column_fails(self):
        code, out = run_check("id\ttitle\tdescription\n1\tOne\td\n")
        self.assertEqual(code, 1)
        self.assertIn("image_link", out)

    def test_empty_file_fails(self):
        code, out = run_check("")
        self.assertEqual(code, 1)
        self.assertIn("::error::", out)

    def test_committed_feed_passes(self):
        feed = os.path.join(os.path.dirname(__file__), "..", "feed.tsv")
        count, error = check_served_feed.check_feed(feed)
        self.assertIsNone(error)
        self.assertGreater(count, 0)


if __name__ == "__main__":
    unittest.main()
