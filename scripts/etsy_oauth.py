"""Etsy OAuth 2.0 tokens for the shop-owner calls (orders), kept outside the repo.

Public catalogue reads only need the x-api-key header (see etsy_auth.py).
Receipts and transactions also need a Bearer token for scope transactions_r,
which Tino grants once through etsy_oauth_login.py. Etsy access tokens live
1 hour; refresh tokens live 90 days and every refresh returns a new one, so
the stored file is rewritten after each refresh.
"""

import json
import os
import sys
import tempfile

# The documented token host. The OAS lists openapi.etsy.com for the same path.
TOKEN_URL = "https://api.etsy.com/v3/public/oauth/token"
AUTHORIZE_URL = "https://www.etsy.com/oauth/connect"
SCOPE = "transactions_r"
DEFAULT_TOKENS_PATH = "~/.config/vogelpoesie/etsy_tokens.json"
LOGIN_SCRIPT = "scripts/etsy_oauth_login.py"


def client_id(environ):
    """The app keystring, which Etsy's OAuth calls take as client_id.

    Accepts ETSY_API_KEY as the keystring alone or as `keystring:shared_secret`.
    """
    keystring = environ.get("ETSY_API_KEY", "").strip().split(":", 1)[0]
    if not keystring:
        sys.exit(
            "ETSY_API_KEY not set: export the app keystring from "
            "https://www.etsy.com/developers/your-apps."
        )
    return keystring


def token_record(payload, now, previous_refresh_token=None):
    """What gets stored from a token response: never the app secret."""
    refresh_token = payload.get("refresh_token") or previous_refresh_token
    if not payload.get("access_token") or not refresh_token:
        sys.exit("Etsy token response had no access_token or refresh_token.")
    return {
        "access_token": payload["access_token"],
        "refresh_token": refresh_token,
        "expires_at": int(now) + int(payload.get("expires_in", 3600)),
        "scope": payload.get("scope", ""),
    }


def write_private(path, text):
    """Atomically replace `path` with `text`, readable by the owner only.

    mkstemp creates the file 0600 before any byte is written, so there is no
    window where the content is world-readable; os.replace swaps it in whole,
    so a crash never leaves a half-written token file.
    """
    path = os.path.expanduser(path)
    directory = os.path.dirname(path) or "."
    os.makedirs(directory, mode=0o700, exist_ok=True)
    fd, temp_path = tempfile.mkstemp(dir=directory, prefix=".tmp-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
        os.replace(temp_path, path)
    except BaseException:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise
    return path


def save_tokens(path, tokens):
    return write_private(path, json.dumps(tokens, indent=2) + "\n")


def load_tokens(path):
    path = os.path.expanduser(path)
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        sys.exit(
            f"No Etsy tokens at {path}: run `python3 {LOGIN_SCRIPT}` once and "
            f"approve access in the browser (README, 'Order access')."
        )
