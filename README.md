# Vogelpoesie Pinterest Catalog Feed

Auto-generated TSV product feed for Pinterest's data source ingestion. Regenerated daily from the live Etsy API. Pinterest fetches `feed.tsv` and creates Product Pins for all listings automatically.

**Feed URL:** `https://pandaplayzlp.github.io/vogelpoesie-pinterest-feed/feed.tsv`

Submit this URL to Pinterest Business → Catalogs → Data Sources (TSV format, daily refresh).

Pipeline: Etsy API → `pinterest-feed.py` → this repo → GitHub Pages → Pinterest.
