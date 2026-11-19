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

The [`build-feed` workflow](.github/workflows/build-feed.yml) runs daily at 08:00 UTC, regenerates `feed.tsv` from the shop's active Etsy listings, and commits it if it changed. It and the [`stock-watch` workflow](.github/workflows/stock-watch.yml) need two repo secrets, `ETSY_API_KEY` (the app keystring) and `ETSY_SHARED_SECRET`: Etsy Open API v3 rejects any request whose `x-api-key` header is not `keystring:shared_secret`. Both values are on https://www.etsy.com/developers/your-apps.

The [`listing-stats` workflow](.github/workflows/listing-stats.yml) runs daily at 07:00 UTC and records every active listing's lifetime views and favorites in `data/listing_stats.csv`; once 7 consecutive days exist it also writes `reports/most-viewed-unsold.md` (top 10 by views gained; run `scripts/listing_report.py --sales <Etsy Order Items CSV> --out <other path>` locally (the workflow overwrites the default path) to drop listings that sold in the last 60 days, and never commit that export).

## Feed order

`feed.tsv` lists the listings most worth pinning first. [`pinterest_feed.py`](scripts/pinterest_feed.py) (`order_listings`) reuses `listing_report.rank_listings`, so the feed and the most-viewed report share one ranking:

- Listings that did not sell in the last 60 days come first, by views gained over the last 7 days of `data/listing_stats.csv`.
- Everything else follows in the order the Etsy API returned it: listings that sold in the last 60 days, and listings missing from the newest snapshot. No row is dropped; which listings the feed contains does not change.
- With fewer than 7 consecutive days of stats the order is unchanged, and the run log says `N of 7 days`.
- `--sales PATH` takes an Etsy Order Items CSV in the `listing_report.py` format. The workflow does not pass it, because the export holds buyer data and never goes in the repo, so the daily ordering is views only and the run log says `sales not checked`. Run `python scripts/pinterest_feed.py --sales PATH` locally to apply the 60-day filter (it needs the Etsy secrets in the environment and rewrites `feed.tsv`; do not commit that file from a run with a different order than the workflow produces).

The workflow runs an hour after the 07:00 stats run and waits up to 15 minutes for today's rows in `data/listing_stats.csv`. If they never arrive it warns and builds from the earlier snapshot. It uses its own concurrency group (`build-feed`), not the stats group.

Every successful run appends one row to `data/feed_runs.csv`, committed daily even when `feed.tsv` is unchanged (a failed build logs nothing):

| column | meaning |
|---|---|
| `run_date` | UTC date of the run |
| `snapshot_date` | newest snapshot in the stats file, blank if there is none |
| `days_of_data` | consecutive days of stats ending at that snapshot |
| `ordering_mode` | `views-7day`, or `current` when the API order was kept |
| `notes` | `;`-separated: `stale snapshot` (newest snapshot is not today's), `N of 7 days`, `sales checked` / `sales not checked`, `stats unreadable (...)` |
| `top5_ids` | first five listing ids of the feed, `;`-separated |

Two runs on the same day append two rows; count distinct `run_date` values to count days.
