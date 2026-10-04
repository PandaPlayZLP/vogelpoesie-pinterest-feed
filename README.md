# Vogelpoesie Pinterest Catalog Feed

Auto-generated TSV product feed for Pinterest's data source ingestion. Regenerated daily from the live Etsy API. Pinterest fetches `feed.tsv` and creates Product Pins for all listings automatically.

**Feed URL:** `https://pandaplayzlp.github.io/vogelpoesie-pinterest-feed/feed.tsv`

Submit this URL to Pinterest Business → Catalogs → Data Sources (TSV format, daily refresh).

Pipeline: Etsy API → [`scripts/pinterest_feed.py`](scripts/pinterest_feed.py) → this repo → GitHub Pages → Pinterest.

The [`build-feed` workflow](.github/workflows/build-feed.yml) runs daily, regenerates `feed.tsv` from the shop's active Etsy listings, and commits it if it changed. It needs an `ETSY_API_KEY` repo secret — see the setup note in the PR that added this workflow if that secret isn't configured yet.
