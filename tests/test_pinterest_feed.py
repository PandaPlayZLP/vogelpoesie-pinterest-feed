import contextlib
import csv
import io
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))

import pinterest_feed  # noqa: E402

# Shaped like the Etsy v3 "listings/batch?includes=Images" response, with
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


class UnmatchedTitleTests(unittest.TestCase):
    UNMATCHED = {
        **FIXTURE_LISTINGS[0],
        "listing_id": 3333333333,
        "title": "Testvogel Kissen Aquarell",
    }

    def test_unmatched_title_is_skipped_and_logged(self):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            rows = pinterest_feed.build_rows(
                [FIXTURE_LISTINGS[0], self.UNMATCHED, FIXTURE_LISTINGS[1]]
            )
        self.assertEqual(
            [row["id"] for row in rows], [1111111111, 2222222222]
        )
        self.assertIn("3333333333", stderr.getvalue())
        self.assertIn("Testvogel Kissen Aquarell", stderr.getvalue())


def _response(payload):
    response = mock.Mock()
    response.json.return_value = payload
    return response


class FetchActiveListingsTests(unittest.TestCase):
    def test_ids_from_active_then_images_from_batch(self):
        session = mock.Mock()
        session.headers = {}
        active_page = {
            "count": 2,
            "results": [{"listing_id": 1111111111}, {"listing_id": 2222222222}],
        }
        session.get.side_effect = [
            _response(active_page),
            _response({"count": 2, "results": FIXTURE_LISTINGS}),
        ]
        with mock.patch.object(pinterest_feed.requests, "Session", return_value=session):
            listings = pinterest_feed.fetch_active_listings("64554473", "key:secret")

        self.assertEqual(listings, FIXTURE_LISTINGS)
        self.assertEqual(session.headers["x-api-key"], "key:secret")
        active_call, batch_call = session.get.call_args_list
        self.assertTrue(active_call.args[0].endswith("/shops/64554473/listings/active"))
        # findAllActiveListingsByShop has no `includes` parameter.
        self.assertNotIn("includes", active_call.kwargs["params"])
        self.assertTrue(batch_call.args[0].endswith("/listings/batch"))
        self.assertEqual(
            batch_call.kwargs["params"],
            {"listing_ids": "1111111111,2222222222", "includes": "Images"},
        )


    def test_paginates_active_and_chunks_batch_by_100(self):
        session = mock.Mock()
        session.headers = {}
        ids = list(range(1, 151))
        active_pages = [
            {"count": 150, "results": [{"listing_id": i} for i in ids[:100]]},
            {"count": 150, "results": [{"listing_id": i} for i in ids[100:]]},
        ]
        # Batch answers out of order and includes one listing gone inactive.
        batch_pages = [
            {"results": [{"listing_id": i, "state": "active"} for i in reversed(ids[:100])]},
            {
                "results": [{"listing_id": i, "state": "active"} for i in ids[100:149]]
                + [{"listing_id": 150, "state": "inactive"}]
            },
        ]
        session.get.side_effect = [_response(p) for p in active_pages + batch_pages]
        with mock.patch.object(pinterest_feed.requests, "Session", return_value=session):
            listings = pinterest_feed.fetch_active_listings("64554473", "key:secret")

        calls = session.get.call_args_list
        self.assertEqual([c.kwargs["params"].get("offset") for c in calls[:2]], [0, 100])
        self.assertEqual(
            [len(c.kwargs["params"]["listing_ids"].split(",")) for c in calls[2:]],
            [100, 50],
        )
        self.assertEqual([l["listing_id"] for l in listings], ids[:149])


class ResolveShopIdTests(unittest.TestCase):
    def test_unset_falls_back_to_default(self):
        self.assertEqual(
            pinterest_feed.resolve_shop_id({}), pinterest_feed.DEFAULT_SHOP_ID
        )

    def test_empty_falls_back_to_default(self):
        # What GitHub Actions passes for `${{ vars.ETSY_SHOP_ID }}` when the
        # repo variable does not exist.
        self.assertEqual(
            pinterest_feed.resolve_shop_id({"ETSY_SHOP_ID": ""}),
            pinterest_feed.DEFAULT_SHOP_ID,
        )

    def test_set_value_wins(self):
        self.assertEqual(
            pinterest_feed.resolve_shop_id({"ETSY_SHOP_ID": "12345"}), "12345"
        )


if __name__ == "__main__":
    unittest.main()
