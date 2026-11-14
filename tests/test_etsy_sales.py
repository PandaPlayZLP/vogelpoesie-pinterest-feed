import csv
import json
import os
import pathlib
import stat
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))

import etsy_oauth  # noqa: E402
import etsy_oauth_login  # noqa: E402
import etsy_sales  # noqa: E402

NOW = 1_800_000_000
DAY = 86400
ENV = {"ETSY_API_KEY": "keystring1", "ETSY_SHARED_SECRET": "secret1", "ETSY_SHOP_ID": ""}


class _Response:
    def __init__(self, status_code, payload=None, text=None, url=""):
        self.status_code = status_code
        self.ok = 200 <= status_code < 400
        self._payload = payload
        self.text = text if text is not None else json.dumps(payload)
        self.url = url

    def json(self):
        return self._payload


class _Session:
    """Replays canned responses and records every call, like requests.Session."""

    def __init__(self, *responses):
        self.headers = {}
        self.responses = list(responses)
        self.calls = []

    def _next(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs, dict(self.headers)))
        response = self.responses.pop(0)
        response.url = response.url or url
        return response

    def get(self, url, **kwargs):
        return self._next("GET", url, **kwargs)

    def post(self, url, **kwargs):
        return self._next("POST", url, **kwargs)


def _tokens(expires_at, refresh="99.refresh-old", access="99.access-old"):
    return {"access_token": access, "refresh_token": refresh, "expires_at": expires_at, "scope": "transactions_r"}


def _page(count, *transactions):
    return _Response(200, {"count": count, "results": list(transactions)})


_next_transaction_id = iter(range(1, 10**6))


def _sale(listing_id, created, transaction_id=None):
    # Real transactions carry more (title, buyer_user_id, variations); none of it may leak.
    return {
        "transaction_id": transaction_id or next(_next_transaction_id),
        "listing_id": listing_id,
        "created_timestamp": created,
        "buyer_user_id": 555,
        "title": "x",
    }


class SalesTestCase(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.tokens_path = os.path.join(self.dir.name, "cfg", "etsy_tokens.json")
        self.out_path = os.path.join(self.dir.name, "out", "etsy-sold-order-items.csv")
        patcher = mock.patch.dict(os.environ, ENV, clear=False)
        patcher.start()
        self.addCleanup(patcher.stop)

    def run_main(self, session):
        etsy_sales.main(
            ["--tokens", self.tokens_path, "--out", self.out_path], session=session, now=lambda: NOW
        )

    def read_rows(self):
        with open(self.out_path, newline="", encoding="utf-8") as handle:
            return list(csv.reader(handle))


class TokenRefreshTests(SalesTestCase):
    def test_expired_token_is_refreshed_and_rotated_pair_saved_0600(self):
        etsy_oauth.save_tokens(self.tokens_path, _tokens(NOW - 10))
        refresh = _Response(
            200,
            {"access_token": "99.access-new", "refresh_token": "99.refresh-new", "expires_in": 3600, "scope": "transactions_r"},
        )
        session = _Session(refresh, _page(0))
        self.run_main(session)

        method, url, kwargs, _ = session.calls[0]
        self.assertEqual((method, url), ("POST", etsy_oauth.TOKEN_URL))
        self.assertEqual(kwargs["data"]["grant_type"], "refresh_token")
        self.assertEqual(kwargs["data"]["refresh_token"], "99.refresh-old")
        self.assertEqual(kwargs["data"]["client_id"], "keystring1")
        self.assertNotIn("refresh-old", url)  # never in a URL check_response may print

        stored = etsy_oauth.load_tokens(self.tokens_path)
        self.assertEqual(stored["refresh_token"], "99.refresh-new")
        self.assertEqual(stored["access_token"], "99.access-new")
        self.assertEqual(stored["expires_at"], NOW + 3600)
        self.assertEqual(stat.S_IMODE(os.stat(self.tokens_path).st_mode), 0o600)

        _, _, _, headers = session.calls[1]
        self.assertEqual(headers["Authorization"], "Bearer 99.access-new")
        self.assertEqual(headers["x-api-key"], "keystring1:secret1")

    def test_rotated_token_survives_a_failing_order_call(self):
        etsy_oauth.save_tokens(self.tokens_path, _tokens(NOW - 10))
        refresh = _Response(200, {"access_token": "99.a2", "refresh_token": "99.r2", "expires_in": 3600})
        session = _Session(refresh, _Response(500, text="oops"))
        with self.assertRaises(SystemExit):
            self.run_main(session)
        self.assertEqual(etsy_oauth.load_tokens(self.tokens_path)["refresh_token"], "99.r2")

    def test_valid_token_is_not_refreshed(self):
        etsy_oauth.save_tokens(self.tokens_path, _tokens(NOW + 3000))
        session = _Session(_page(0))
        self.run_main(session)
        self.assertEqual([call[0] for call in session.calls], ["GET"])
        self.assertEqual(session.calls[0][3]["Authorization"], "Bearer 99.access-old")

    def test_rejected_refresh_exits_with_etsys_body_and_keeps_old_file(self):
        etsy_oauth.save_tokens(self.tokens_path, _tokens(NOW - 10))
        body = '{"error":"invalid_grant","error_description":"refresh token expired"}'
        session = _Session(_Response(400, text=body))
        with self.assertRaises(SystemExit) as caught:
            self.run_main(session)
        message = str(caught.exception.code)
        self.assertIn("400", message)
        self.assertIn("refresh token expired", message)
        self.assertNotIn("refresh-old", message)
        self.assertEqual(etsy_oauth.load_tokens(self.tokens_path)["refresh_token"], "99.refresh-old")
        self.assertFalse(os.path.exists(self.out_path))

    def test_missing_token_file_names_the_login_script(self):
        with self.assertRaises(SystemExit) as caught:
            self.run_main(_Session())
        self.assertIn("etsy_oauth_login.py", str(caught.exception.code))


class FetchSalesTests(SalesTestCase):
    def test_pages_through_every_transaction_and_keeps_last_60_days(self):
        etsy_oauth.save_tokens(self.tokens_path, _tokens(NOW + 3000))
        first = [_sale(1000 + i, NOW - i * 3600) for i in range(100)]
        second = [_sale(2001, NOW - 59 * DAY), _sale(2002, NOW - 61 * DAY), _sale(2003, NOW - 400 * DAY)]
        session = _Session(_page(103, *first), _page(103, *second))
        self.run_main(session)

        offsets = [call[2]["params"]["offset"] for call in session.calls]
        self.assertEqual(offsets, [0, 100])
        self.assertTrue(all(call[2]["params"]["limit"] == 100 for call in session.calls))
        self.assertTrue(session.calls[0][1].endswith("/v3/application/shops/64554473/transactions"))

        rows = self.read_rows()
        self.assertEqual(rows[0], ["Sale Date", "Listing ID"])
        listing_ids = {row[1] for row in rows[1:]}
        self.assertEqual(len(rows) - 1, 101)
        self.assertIn("2001", listing_ids)
        self.assertNotIn("2002", listing_ids)
        self.assertNotIn("2003", listing_ids)

    def test_csv_holds_only_sale_date_and_listing_id(self):
        etsy_oauth.save_tokens(self.tokens_path, _tokens(NOW + 3000))
        # 1_800_000_000 is 2027-01-15 08:00 UTC.
        session = _Session(_page(1, _sale(4321, NOW)))
        self.run_main(session)
        self.assertEqual(self.read_rows(), [["Sale Date", "Listing ID"], ["01/15/27", "4321"]])
        with open(self.out_path, encoding="utf-8") as handle:
            self.assertNotIn("555", handle.read())
        self.assertEqual(stat.S_IMODE(os.stat(self.out_path).st_mode), 0o600)

    def test_empty_page_stops_even_if_count_is_larger(self):
        session = _Session(_page(500, _sale(1, NOW)), _page(500))
        self.assertEqual(etsy_sales.fetch_sales(session, "1", NOW - DAY), [(1, NOW)])
        self.assertEqual(len(session.calls), 2)

    def test_transaction_repeated_across_pages_counts_once(self):
        # A new sale between the two calls pushes the last row of page 1 onto page 2.
        first = [_sale(10 + i, NOW - i, transaction_id=100 + i) for i in range(100)]
        second = [_sale(109, NOW - 99, transaction_id=199), _sale(7, NOW - 200, transaction_id=300)]
        session = _Session(_page(102, *first), _page(102, *second))
        sales = etsy_sales.fetch_sales(session, "1", NOW - DAY)
        self.assertEqual(len(sales), 101)
        self.assertIn((7, NOW - 200), sales)

    def test_rows_without_listing_or_timestamp_are_skipped_and_create_timestamp_used(self):
        session = _Session(
            _page(
                3,
                {"transaction_id": 1, "listing_id": None, "created_timestamp": NOW},
                {"transaction_id": 2, "listing_id": 5},
                {"transaction_id": 3, "listing_id": 6, "create_timestamp": NOW - 5},
            )
        )
        self.assertEqual(etsy_sales.fetch_sales(session, "1", NOW - DAY), [(6, NOW - 5)])

    def test_order_call_error_exits_with_etsys_body(self):
        etsy_oauth.save_tokens(self.tokens_path, _tokens(NOW + 3000))
        body = '{"error":"insufficient_scope: transactions_r"}'
        session = _Session(_Response(403, text=body))
        with self.assertRaises(SystemExit) as caught:
            self.run_main(session)
        message = str(caught.exception.code)
        self.assertIn("403", message)
        self.assertIn("insufficient_scope", message)
        self.assertIn("/shops/64554473/transactions", message)
        self.assertNotIn("access-old", message)
        self.assertFalse(os.path.exists(self.out_path))


class LoginTests(SalesTestCase):
    def test_pkce_challenge_matches_rfc7636_appendix_b(self):
        verifier = "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
        self.assertEqual(
            etsy_oauth_login.challenge_for(verifier), "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM"
        )
        made_verifier, made_challenge = etsy_oauth_login.make_pkce()
        self.assertTrue(43 <= len(made_verifier) <= 128)
        self.assertEqual(made_challenge, etsy_oauth_login.challenge_for(made_verifier))

    def test_state_mismatch_and_etsy_error_exit(self):
        with self.assertRaises(SystemExit):
            etsy_oauth_login.parse_redirect("https://localhost/etsy-callback?code=abc&state=other", "mine")
        with self.assertRaises(SystemExit) as caught:
            etsy_oauth_login.parse_redirect(
                "https://localhost/etsy-callback?error=access_denied&error_description=User+declined&state=mine",
                "mine",
            )
        self.assertIn("User declined", str(caught.exception.code))

    def test_bare_code_is_accepted_and_text_without_code_is_not(self):
        self.assertEqual(etsy_oauth_login.parse_redirect("  abc-DEF_123  ", "mine"), "abc-DEF_123")
        with self.assertRaises(SystemExit):
            etsy_oauth_login.parse_redirect("https://localhost/etsy-callback", "mine")

    def test_login_exchanges_code_with_verifier_and_saves_tokens(self):
        printed = []
        session = _Session(
            _Response(200, {"access_token": "99.a", "refresh_token": "99.r", "expires_in": 3600, "scope": "transactions_r"})
        )

        def paste(_prompt):
            url = printed[1]
            query = dict(part.split("=", 1) for part in url.split("?", 1)[1].split("&"))
            self.assertEqual(query["scope"], "transactions_r")
            self.assertEqual(query["code_challenge_method"], "S256")
            self.assertEqual(query["client_id"], "keystring1")
            paste.challenge = query["code_challenge"]
            return f"https://localhost/etsy-callback?code=the-code&state={query['state']}"

        with mock.patch("builtins.print", side_effect=lambda *a, **k: printed.append(" ".join(map(str, a)))):
            etsy_oauth_login.main(["--tokens", self.tokens_path], read_line=paste, session=session, now=lambda: NOW)

        _, url, kwargs, _ = session.calls[0]
        self.assertEqual(url, etsy_oauth.TOKEN_URL)
        data = kwargs["data"]
        self.assertEqual(data["grant_type"], "authorization_code")
        self.assertEqual(data["code"], "the-code")
        self.assertEqual(data["redirect_uri"], "https://localhost/etsy-callback")
        self.assertEqual(etsy_oauth_login.challenge_for(data["code_verifier"]), paste.challenge)
        self.assertEqual(etsy_oauth.load_tokens(self.tokens_path)["refresh_token"], "99.r")
        self.assertEqual(stat.S_IMODE(os.stat(self.tokens_path).st_mode), 0o600)
        self.assertFalse(any("99.a" in line or "99.r" in line for line in printed))

    def test_login_without_transactions_scope_saves_nothing(self):
        session = _Session(_Response(200, {"access_token": "99.a", "refresh_token": "99.r", "scope": "shops_r"}))
        with mock.patch("builtins.print"), self.assertRaises(SystemExit):
            etsy_oauth_login.main(
                ["--tokens", self.tokens_path], read_line=lambda _p: "bare-code", session=session, now=lambda: NOW
            )
        self.assertFalse(os.path.exists(self.tokens_path))


if __name__ == "__main__":
    unittest.main()
