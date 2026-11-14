# Vogelpoesie Pinterest Catalog Feed

Auto-generated TSV product feed for Pinterest's data source ingestion. Regenerated daily from the live Etsy API. Pinterest fetches `feed.tsv` and creates Product Pins for all listings automatically.

**Feed URL:** `https://cdn.jsdelivr.net/gh/PandaPlayZLP/vogelpoesie-pinterest-feed@main/feed.tsv`

Not the `github.io` URL: the apex `tinod.me` redirects every path to the portfolio site, and a
GitHub Pages project URL inherits that redirect from the user site's custom domain, so
`pandaplayzlp.github.io/vogelpoesie-pinterest-feed/feed.tsv` answers 404. The CDN path serves
the committed file with `text/tab-separated-values`, and the build purges its cache after each
commit and then fetches the public URL to prove it works.

Submit this URL to Pinterest Business → Catalogs → Data Sources (TSV format, daily refresh).

Pipeline: Etsy API → [`scripts/pinterest_feed.py`](scripts/pinterest_feed.py) → this repo → GitHub Pages → Pinterest.

The [`build-feed` workflow](.github/workflows/build-feed.yml) runs daily, regenerates `feed.tsv` from the shop's active Etsy listings, and commits it if it changed. It and the [`stock-watch` workflow](.github/workflows/stock-watch.yml) need two repo secrets, `ETSY_API_KEY` (the app keystring) and `ETSY_SHARED_SECRET`: Etsy Open API v3 rejects any request whose `x-api-key` header is not `keystring:shared_secret`. Both values are on https://www.etsy.com/developers/your-apps.

## Order access

[`scripts/etsy_sales.py`](scripts/etsy_sales.py) writes which listings sold in the last 60 days
(`Sale Date`, `Listing ID` only, one row per sold item) to
`~/Obsidian/projects/vogelpoesie/etsy-sold-order-items.csv`, the file the listing ranking reads
with `--sales`. Order data needs an Etsy OAuth token (scope `transactions_r`) on top of the API
key. The token lives in `~/.config/vogelpoesie/etsy_tokens.json` (mode 600), never in this repo,
and the job runs on Tino's machine: every refresh returns a new refresh token that has to be
saved, which a GitHub Actions secret cannot do.

One-time setup:

1. On https://www.etsy.com/developers/your-apps, open the Vogelpoesie app, edit it and add this
   callback URL exactly (https, no trailing slash): `https://localhost/etsy-callback`. Save.
   If Etsy refuses it, register any https URL you control and pass it to the login script as
   `--redirect-uri <that URL>` (or set `ETSY_REDIRECT_URI`); it must match character for character.
2. Create a credentials file only you can read, then open it in an editor (so the secret never
   lands in shell history):

   ```bash
   install -d -m 700 ~/.config/vogelpoesie
   install -m 600 /dev/null ~/.config/vogelpoesie/etsy.env
   nano ~/.config/vogelpoesie/etsy.env
   ```

   and enter two lines, keystring first, then the shared secret, both from the app page:

   ```text
   ETSY_API_KEY=<keystring>
   ETSY_SHARED_SECRET=<shared secret>
   ```

3. From this repo, run the login:

   ```bash
   python3 -m pip install --user -r scripts/requirements.txt  # once, if requests is missing
   set -a; . ~/.config/vogelpoesie/etsy.env; set +a
   python3 scripts/etsy_oauth_login.py
   ```

4. Open the printed `https://www.etsy.com/oauth/connect?...` URL, sign in as the shop owner and
   click **Allow access**. The browser then shows a "can't connect" page at
   `https://localhost/etsy-callback?code=...`. That is expected: copy the whole address bar URL
   and paste it into the waiting script. It saves the tokens and prints where.
5. Check it works: `python3 scripts/etsy_sales.py` prints how many sold items it wrote and where.
6. Run it daily, e.g. `crontab -e`:

   ```cron
   15 6 * * * cd ~/code/vogelpoesie-pinterest-feed && set -a && . ~/.config/vogelpoesie/etsy.env && set +a && python3 scripts/etsy_sales.py >> ~/.config/vogelpoesie/etsy_sales.log 2>&1
   ```

`Sale Date` is written as `MM/DD/YY` (the Etsy Order Items export format) in UTC.

Log in again (steps 3–4) only if the job stops with Etsy's `invalid_grant` error. That happens when
it has not run for 90 days, so the refresh token expired, or when access was revoked on Etsy.
