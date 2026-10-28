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
