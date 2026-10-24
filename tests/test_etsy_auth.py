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


if __name__ == "__main__":
    unittest.main()
