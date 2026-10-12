import csv
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))

import pinterest_feed  # noqa: E402

# Shaped like the Etsy v3 "listings/active?includes=Images" response, with
# invented ids/text standing in for a real shop's data purely to exercise
# the TSV transform locally (no live Etsy call, no production feed.tsv).
FIXTURE_LISTINGS = [
    {
        "listing_id": 1111111111,
        "title": "Testvogel Tasse Aquarell mit Gedicht",
        "description": "Zeile eins.\nZeile zwei.\tmit Tab.",
        "url": "https://www.etsy.com/listing/1111111111/testvogel-tasse",
        "quantity": 5,
        "price": {"amount": 2190, "divisor": 100, "currency_code": "EUR"},
        "images": [
            {"rank": 1, "url_fullxfull": "https://example.invalid/a1.jpg"},
            {"rank": 2, "url_fullxfull": "https://example.invalid/a2.jpg"},
        ],
    },
    {
        "listing_id": 2222222222,
        "title": "Testvogel Poster A2 Botanische Illustration",
        "description": "Ein Poster.",
        "url": "https://www.etsy.com/listing/2222222222/testvogel-poster",
        "quantity": 0,
        "price": {"amount": 3490, "divisor": 100, "currency_code": "EUR"},
        "images": [{"rank": 1, "url_fullxfull": "https://example.invalid/b1.jpg"}],
    },
]


class ListingToRowTests(unittest.TestCase):
    def test_matches_original_column_shape(self):
        rows = pinterest_feed.build_rows(FIXTURE_LISTINGS)
        self.assertEqual(len(rows), len(FIXTURE_LISTINGS))
        for row in rows:
            self.assertEqual(set(row.keys()), set(pinterest_feed.FIELDNAMES))

    def test_text_fields_are_flattened_to_one_line(self):
        row = pinterest_feed.build_rows(FIXTURE_LISTINGS)[0]
        self.assertNotIn("\n", row["description"])
        self.assertNotIn("\t", row["description"])

    def test_price_and_availability(self):
        in_stock, out_of_stock = pinterest_feed.build_rows(FIXTURE_LISTINGS)
        self.assertEqual(in_stock["price"], "21.90 EUR")
        self.assertEqual(in_stock["availability"], "in stock")
        self.assertEqual(out_of_stock["availability"], "out of stock")

    def test_product_type_classification(self):
        mug, poster = pinterest_feed.build_rows(FIXTURE_LISTINGS)
        self.assertEqual(mug["product_type"], "Heimische Vögel > Tassen")
        self.assertEqual(mug["google_product_category"], "674")
        self.assertEqual(mug["item_group_id"], "testvogel-tasse")
        self.assertEqual(poster["product_type"], "Heimische Vögel > Poster A2")
        self.assertEqual(poster["google_product_category"], "503793")

    def test_write_tsv_round_trip_header(self):
        rows = pinterest_feed.build_rows(FIXTURE_LISTINGS)
        with tempfile.TemporaryDirectory() as tmp:
            out_path = pathlib.Path(tmp) / "feed.tsv"
            pinterest_feed.write_tsv(rows, out_path)

            with open(out_path, newline="", encoding="utf-8") as handle:
                reader = csv.reader(handle, delimiter="\t")
                header = next(reader)
                data_rows = list(reader)

        self.assertEqual(header, pinterest_feed.FIELDNAMES)
        self.assertEqual(len(data_rows), len(rows))


if __name__ == "__main__":
    unittest.main()
