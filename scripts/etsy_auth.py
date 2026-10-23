"""Etsy Open API v3 credentials, shared by every script that calls Etsy."""

import sys

YOUR_APPS_URL = "https://www.etsy.com/developers/your-apps"


def api_key_header(environ):
    """The x-api-key header value Etsy v3 requires: `keystring:shared_secret`.

    Reads ETSY_API_KEY (keystring) and ETSY_SHARED_SECRET. An ETSY_API_KEY
    that already holds `keystring:shared_secret` is used as is. Exits naming
    whichever secret is missing, since every Etsy call would 403 without it.
    """
    keystring = environ.get("ETSY_API_KEY", "").strip()
    shared_secret = environ.get("ETSY_SHARED_SECRET", "").strip()
    if ":" in keystring:
        return keystring

    missing = [
        name
        for name, value in (
            ("ETSY_API_KEY", keystring),
            ("ETSY_SHARED_SECRET", shared_secret),
        )
        if not value
    ]
    if missing:
        sys.exit(
            f"{' and '.join(missing)} not set: add as GitHub repo secret(s). "
            f"Etsy v3 needs both the keystring and the shared secret, found "
            f"on {YOUR_APPS_URL}."
        )
    return f"{keystring}:{shared_secret}"
