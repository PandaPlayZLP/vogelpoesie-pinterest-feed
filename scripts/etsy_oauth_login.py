#!/usr/bin/env python3
"""One-time Etsy login granting order read access (scope transactions_r).

Prints the authorize URL, waits for the URL the browser lands on after Tino
approves, exchanges its code (authorization code + PKCE) and stores the access
and refresh tokens outside the repo with mode 600. Run by hand, never in CI.

The redirect URI must be registered byte-for-byte on the Etsy app. Nothing has
to answer at it: the browser shows an error page, and its address bar still
holds the code to paste here.
"""

import argparse
import base64
import hashlib
import os
import secrets
import sys
import time
from urllib.parse import parse_qs, urlencode, urlsplit

import requests

from etsy_auth import check_response
from etsy_oauth import (
    AUTHORIZE_URL,
    DEFAULT_TOKENS_PATH,
    SCOPE,
    TOKEN_URL,
    client_id,
    save_tokens,
    token_record,
)

DEFAULT_REDIRECT_URI = "https://localhost/etsy-callback"


def make_pkce():
    """(code_verifier, code_challenge) per RFC 7636, S256."""
    verifier = secrets.token_urlsafe(32)  # 43 chars from [A-Za-z0-9_-]
    return verifier, challenge_for(verifier)


def challenge_for(verifier):
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


def authorize_url(keystring, redirect_uri, state, challenge):
    query = urlencode(
        {
            "response_type": "code",
            "client_id": keystring,
            "redirect_uri": redirect_uri,
            "scope": SCOPE,
            "state": state,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        }
    )
    return f"{AUTHORIZE_URL}?{query}"


def parse_redirect(pasted, expected_state):
    """The authorization code from the pasted redirect URL (or a bare code).

    Exits on Etsy's own error (e.g. access_denied) and on a state mismatch,
    which means the URL does not belong to this login attempt.
    """
    pasted = pasted.strip()
    if "code=" not in pasted and "error=" not in pasted:
        if not pasted or "?" in pasted or "/" in pasted:
            sys.exit("Pasted text holds no `code=`: copy the whole address bar URL.")
        return pasted  # bare code: PKCE still binds it to this login

    params = parse_qs(urlsplit(pasted).query or pasted.split("?", 1)[-1])
    if "error" in params:
        description = params.get("error_description", [""])[0]
        sys.exit(f"Etsy refused the login: {params['error'][0]} {description}".strip())
    if params.get("state", [None])[0] != expected_state:
        sys.exit("State in the pasted URL does not match this login; start over.")
    code = params.get("code", [""])[0]
    if not code:
        sys.exit("Pasted URL has an empty `code=`: copy the whole address bar URL.")
    return code


def exchange_code(session, keystring, redirect_uri, code, verifier):
    # Form body, never the query string: check_response prints the URL.
    response = session.post(
        TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "client_id": keystring,
            "redirect_uri": redirect_uri,
            "code": code,
            "code_verifier": verifier,
        },
        timeout=30,
    )
    check_response(response)
    return response.json()


def main(argv=None, read_line=input, session=None, now=time.time):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--redirect-uri",
        default=os.environ.get("ETSY_REDIRECT_URI", "").strip() or DEFAULT_REDIRECT_URI,
        help="callback URL registered on the Etsy app (default: %(default)s)",
    )
    parser.add_argument("--tokens", default=DEFAULT_TOKENS_PATH, help="token file")
    args = parser.parse_args(argv)

    keystring = client_id(os.environ)
    verifier, challenge = make_pkce()
    state = secrets.token_urlsafe(16)

    print("1. Open this URL, sign in as the Vogelpoesie owner and click 'Allow access':\n")
    print(authorize_url(keystring, args.redirect_uri, state, challenge))
    print(f"\n2. The browser then lands on {args.redirect_uri}?code=... (an error page is fine).")
    code = parse_redirect(read_line("   Paste that whole address bar URL here: "), state)

    session = session or requests.Session()
    payload = exchange_code(session, keystring, args.redirect_uri, code, verifier)
    granted = payload.get("scope", "").split()
    if SCOPE not in granted:
        sys.exit(f"Etsy granted scope {granted or '<none>'}, not {SCOPE}; run again.")

    path = save_tokens(args.tokens, token_record(payload, now()))
    print(f"\nSaved Etsy tokens to {path} (mode 600). scripts/etsy_sales.py can run now.")


if __name__ == "__main__":
    main()
