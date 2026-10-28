import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))

import etsy_auth  # noqa: E402


class ApiKeyHeaderTests(unittest.TestCase):
    def test_joins_keystring_and_shared_secret(self):
        env = {"ETSY_API_KEY": "keystring1", "ETSY_SHARED_SECRET": "secret1"}
        self.assertEqual(etsy_auth.api_key_header(env), "keystring1:secret1")

    def test_combined_value_in_api_key_is_used_as_is(self):
        env = {"ETSY_API_KEY": "keystring1:secret1", "ETSY_SHARED_SECRET": ""}
        self.assertEqual(etsy_auth.api_key_header(env), "keystring1:secret1")

    def test_missing_shared_secret_exits_naming_it(self):
        # What GitHub Actions passes when the ETSY_SHARED_SECRET secret is unset.
        env = {"ETSY_API_KEY": "keystring1", "ETSY_SHARED_SECRET": ""}
        with self.assertRaises(SystemExit) as caught:
            etsy_auth.api_key_header(env)
        self.assertIn("ETSY_SHARED_SECRET", str(caught.exception.code))
        self.assertNotIn("ETSY_API_KEY", str(caught.exception.code))

    def test_missing_both_exits_naming_both(self):
        with self.assertRaises(SystemExit) as caught:
            etsy_auth.api_key_header({"ETSY_API_KEY": "", "ETSY_SHARED_SECRET": ""})
        self.assertIn("ETSY_API_KEY and ETSY_SHARED_SECRET", str(caught.exception.code))


class _Response:
    def __init__(self, status_code, text):
        self.status_code = status_code
        self.ok = 200 <= status_code < 400
        self.text = text
        self.url = "https://openapi.etsy.com/v3/application/shops/1/listings/active"


class CheckResponseTests(unittest.TestCase):
    def test_ok_response_passes_through(self):
        response = _Response(200, '{"count": 0}')
        self.assertIs(etsy_auth.check_response(response), response)

    def test_403_exits_with_etsys_own_reason(self):
        response = _Response(
            403, '{"error":"API key not found or not active, or incorrect shared secret for API key."}'
        )
        with self.assertRaises(SystemExit) as caught:
            etsy_auth.check_response(response)
        message = str(caught.exception.code)
        self.assertIn("403", message)
        self.assertIn("not active", message)
        self.assertIn("/shops/1/listings/active", message)

    def test_empty_body_still_names_the_status(self):
        with self.assertRaises(SystemExit) as caught:
            etsy_auth.check_response(_Response(500, "   "))
        self.assertIn("500", str(caught.exception.code))
        self.assertIn("<empty body>", str(caught.exception.code))


if __name__ == "__main__":
    unittest.main()
