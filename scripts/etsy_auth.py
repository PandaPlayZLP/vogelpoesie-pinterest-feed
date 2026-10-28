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


def check_response(response):
    """Return the response, or exit with Etsy's own explanation of a failure.

    `raise_for_status` throws away the body, and Etsy puts the actual cause
    there (e.g. 403 "API key not found or not active, or incorrect shared
    secret for API key."), so a bare status code leaves nobody able to tell a
    pending app approval from a mistyped secret.
    """
    if response.ok:
        return response
    body = " ".join(response.text.split())[:400] or "<empty body>"
    sys.exit(f"Etsy {response.status_code} on {response.url}: {body}")
