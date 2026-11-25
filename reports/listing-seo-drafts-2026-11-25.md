# Vogelpoesie listing SEO drafts, 2026-11-25

**DRAFT. Nothing in this file has been applied.** No Etsy edits, no pins, no spend. Every title, tag set and description opening below is a proposal for the shop owner to review and paste by hand.

## Sources and what is missing

- **Stats:** `data/listing_stats.csv` on `origin/main`, seven daily snapshots 2026-11-19 to 2026-11-25, 37 active listings. Lifetime views and favorites below are the 11-25 snapshot. The brief quoted the 11-22 snapshot (mug 262 / 14, T-shirt 316 / 20); the mug has since moved to 277 / 17.
- **Prices and description facts:** `feed.tsv` on `origin/main` (Etsy API output). Every product fact in the description lines comes from there; nothing was invented.
- **No keyword data.** No DataForSEO or EverBee export exists in the repo or anywhere on this machine. Gmail could not be searched (the mail connector was denied permission in this session), so an export sent by mail was not checked. The titles and tags are therefore **reasoned from the current titles, the descriptions and common German Etsy search wording, not from search volumes.** Treat them as hypotheses and compare views per listing in the daily snapshots after publishing.
- **No sales data.** There is no Etsy Order Items export in the repo (`reports/most-viewed-unsold.md` itself says sales were not checked). The brief says 2 to 3 sales in three weeks, all at 21.90 EUR, which is the mug price, so the sales were almost certainly mugs. Which mugs is unknown.
- **Current tags are unknown.** The feed does not carry tags and live Etsy pages were not read, so these tag sets are not diffed against what is live.

## How the 15 listings were chosen

1. **Top ten by lifetime views** (11-25 snapshot). Places 9 and 10 tie at 60 views (Zaunkönig poster 4456775240, Stieglitz bag 4456775774); both are kept, and the Eisvogel poster at 57 is the first one left out.
2. **Five more by favorites, outside the top ten.** "Few sales" cannot be checked without a sales export, so the rule is: most favorites among the remaining 27 listings, ties broken by favorites per view. Three listings have 4 favorites (Stieglitz T-shirt, Eisvogel poster, Amsel mug). Five listings have 3 favorites; the two with the highest favorite rate (Zaunkönig mug mit Spruch 3 of 24, Zaunkönig T-shirt 3 of 34) take places 4 and 5. Left out at 3 favorites: Eichelhäher mug (3 of 55), Eisvogel T-shirt (3 of 54), Zaunkönig mug (3 of 53).
3. If the real sales list shows that one of these 15 is a recent seller, drop it from the rollout; the drafts do not depend on each other.

| # | Listing | Price | Views | Favs | Fav rate | Views gained 11-19 to 11-25 | Role |
|---|---|---|---|---|---|---|---|
| 1 | [Rotkehlchen T-Shirt Aquarell Bio-Baumwolle, Voge…](https://www.etsy.com/listing/4456765393) `4456765393` | 39.90 EUR | 316 | 20 | 6.3% | 1 | Top 10 (#1 by views) |
| 2 | [Rotkehlchen Tasse Aquarell, Vogel Kaffeetasse 33…](https://www.etsy.com/listing/4456775972) `4456775972` | 21.90 EUR | 277 | 17 | 6.1% | 26 | Top 10 (#2 by views) |
| 3 | [Eisvogel Hoodie Linolschnitt Bio-Baumwolle, Voge…](https://www.etsy.com/listing/4456776688) `4456776688` | 64.90 EUR | 158 | 8 | 5.1% | 7 | Top 10 (#3 by views) |
| 4 | [Stieglitz Poster A2 Botanische Illustration, Dis…](https://www.etsy.com/listing/4456775898) `4456775898` | 44.90 EUR | 144 | 11 | 7.6% | 2 | Top 10 (#4 by views) |
| 5 | [Rotkehlchen Poster A2 Linolschnitt, Vogel Wandde…](https://www.etsy.com/listing/4456776284) `4456776284` | 44.90 EUR | 138 | 10 | 7.2% | 4 | Top 10 (#5 by views) |
| 6 | [Blaumeise T-Shirt Aquarell Bio-Baumwolle, Garten…](https://www.etsy.com/listing/4456764353) `4456764353` | 39.90 EUR | 75 | 2 | 2.7% | 0 | Top 10 (#6 by views) |
| 7 | [Eisvogel Tasse mit Spruch Aquarell, Vogel Kaffee…](https://www.etsy.com/listing/4494001018) `4494001018` | 21.90 EUR | 71 | 6 | 8.5% | 0 | Top 10 (#7 by views) |
| 8 | [Rotkehlchen Poster A2 Botanische Illustration, V…](https://www.etsy.com/listing/4456775420) `4456775420` | 44.90 EUR | 61 | 3 | 4.9% | 0 | Top 10 (#8 by views) |
| 9 | [Zaunkönig Poster A2 Botanische Illustration, Vog…](https://www.etsy.com/listing/4456775240) `4456775240` | 44.90 EUR | 60 | 9 | 15.0% | 0 | Top 10 (#9 by views, tied at 60) |
| 10 | [Stieglitz Jutebeutel Aquarell Bio-Baumwolle, Vog…](https://www.etsy.com/listing/4456775774) `4456775774` | 34.90 EUR | 60 | 2 | 3.3% | 3 | Top 10 (#10 by views, tied at 60) |
| 11 | [Stieglitz T-Shirt Distelfink Aquarell Bio-Baumwo…](https://www.etsy.com/listing/4456775670) `4456775670` | 39.90 EUR | 15 | 4 | 26.7% | 0 | Favorites pick (4 favorites on 15 views) |
| 12 | [Amsel Tasse mit Spruch Aquarell, Vogel Kaffeetas…](https://www.etsy.com/listing/4493994193) `4493994193` | 21.90 EUR | 41 | 4 | 9.8% | 3 | Favorites pick (4 favorites on 41 views) |
| 13 | [Eisvogel Poster A2 Botanische Illustration, Voge…](https://www.etsy.com/listing/4456776576) `4456776576` | 44.90 EUR | 57 | 4 | 7.0% | 3 | Favorites pick (4 favorites on 57 views) |
| 14 | [Zaunkönig Tasse mit Spruch, Spruchtasse Aquarell…](https://www.etsy.com/listing/4493994437) `4493994437` | 21.90 EUR | 24 | 3 | 12.5% | 0 | Favorites pick (3 favorites on 24 views, ratio 12.5%) |
| 15 | [Zaunkönig T-Shirt Aquarell Bio-Baumwolle, Kleins…](https://www.etsy.com/listing/4456775286) `4456775286` | 39.90 EUR | 34 | 3 | 8.8% | 0 | Favorites pick (3 favorites on 34 views, ratio 8.8%) |

Shop-wide: 68 new views in the six days between the first and last snapshot (about 11 per day, down from about 14 in the first window the brief quotes). The Robin mug alone is 26 of them.

## Which listings the Pinterest feed should lead with

1. **Rotkehlchen Tasse, 4456775972.** The only listing with real current momentum (+26 views in six days, 38% of all new shop views), 17 favorites, and 21.90 EUR is the price the shop actually sells at. The Robin is also the winter bird in the listing's own verse ("Im Frost singt es noch"), which suits a December pin. Strongest case; also the feed's current number one.
2. **Rotkehlchen T-Shirt, 4456765393.** Most lifetime views (316) and most favorites (20) in the shop, but only +1 view in six days: its earlier traffic has dried up (cause unknown), and no sale at its 39.90 EUR price is known (the only prices mentioned for sales are 21.90 EUR). A pin gives it a new source of traffic and tests whether the interest turns into orders. Open risk: it may be a price question rather than a traffic one.
3. **Stieglitz Poster A2 Botanische Illustration, 4456775898.** Best favorite rate of any listing with over 100 views (11 of 144, 7.6%). Posters are vertical art images, which fits how Pinterest users save decor and gift ideas, and it is one of three species (Rotkehlchen, Stieglitz, Eisvogel) that already pull views.

**How this differs from the feed.** `scripts/pinterest_feed.py` orders by 7-day view gain (`MODE_VIEWS = "views-7day"`), with no sales export. That agrees on the mug at place 1. After that it is ranking differences of 1 to 7 views over six days (hoodie +7, Eichelhäher mug +6, Robin linocut poster +4), which is noise at about 11 views per day. Favorites are a steadier signal. This file deliberately does not recommend changing the feed code; it only suggests which listings to give the best pin images and boards first. One test worth a pin if a fourth slot is free: the Stieglitz T-shirt (4456775670), 4 favorites on 15 views.

## Problems found in the live listings (fix regardless of SEO)

- **All four hoodies with a description in the feed (Eisvogel Linolschnitt 4456776688, Eisvogel Aquarell 4456765739, Rotkehlchen 4456776174, Kranich 4456775454):** the description opens with `100% Bio-Baumwolle`, the spec list says 85% Bio-Baumwolle / 15% recyceltes Polyester. Found by searching all of `feed.tsv`; the two newer hoodies (Stieglitz 4566856835, Blaumeise 4566831572) do not use that opening.
- **Stieglitz bag 4456775774:** sold as `Jutebeutel` but described as 100% Bio-Baumwolle. Pick one material word.
- **Zaunkönig T-Shirt 4456775286:** title claims `Kleinster Vogel Europas`; the Sommer- und Wintergoldhähnchen are smaller. The descriptions say `einer der kleinsten heimischen Vögel`, which is correct.
- **`mit Spruch Aquarell` mugs:** nine of the twelve `mit Spruch` mugs (Eichelhäher 4493994473, Kranich 4493994277, Eisvogel 4494001018, Stieglitz 4493994155, Amsel 4493994193, Nachtigall 4493994241, Dompfaff 4493994321, Waldkauz 4494001374, Schwalbe 4493994357) say nothing about a verse in the opening of the description. Only the Zaunkönig, Blaumeise and Rotkehlchen `Spruch` mugs do. Confirm from the listing photos that the verse is printed, then say so in the first line (or drop `mit Spruch` from the title).

## Rules the drafts follow

- **Search phrase first.** Each title opens with `<Vogel> <Produkt>` (`Rotkehlchen Tasse`, `Eisvogel Hoodie`), which is what a buyer types and what shows in the first 40 characters on mobile. This deliberately differs from the 2026-10-13 notes in the Obsidian vault, which led with `Geschenk für Vogelliebhaber:`. The gift phrase comes second.
- **Style words separate the Robin listings.** Six Robin listings exist (T-shirt, hoodie, Aquarell mug, mug mit Gedicht, linocut poster, botanical poster). Aquarell, Linolschnitt, Botanische Illustration and Spruch decide which listing a query should land on.
- **English keyword kept** at the end of every title.
- **Limits:** every title is at most 140 characters, every tag set has exactly 13 tags of at most 20 characters, no repeats within a set, and no `:`, `%` or `&` in titles (Etsy restricts those characters in titles, from memory; commas only are used, so the restriction cannot apply). Checked by script, not by eye.
- **Seasonal tags.** `Weihnachtsgeschenk`, `Wichtelgeschenk`, `Nikolausgeschenk` are on purpose for the next three weeks. Swap them in January for `Geburtstagsgeschenk` and `Muttertagsgeschenk`. `Weihnachtsgeschenk` is also in the **titles** of nine drafts (Robin T-shirt, Robin mug, Robin linocut poster, Blaumeise T-shirt, Eisvogel mug, Stieglitz T-shirt, Amsel mug, Zaunkönig T-shirt, Zaunkönig mug), and the Robin T-shirt's second description line opens "Ein Weihnachtsgeschenk". Take it out of those titles and that line in January too. Before publishing, confirm the order cut-off for Christmas delivery: the listings say 1 to 5 working days processing plus 2 to 4 days shipping within Germany, made on demand.
- **Tail-only edits on the two proven listings.** For the Robin mug and Robin T-shirt the first words are unchanged, so any change in views is attributable to the tail and tags.
- **Description lines** are two sentences each, the first with the product, motif, material and size, the second with who it is for and the verse that already opens the live text. Free shipping is mentioned only for the mug, because only the mug description says it.

## Suggested rollout

1. Publish the 13 non-proven listings first (everything except the Robin mug and Robin T-shirt), and note the date.
2. Wait a week and compare views per listing in `data/listing_stats.csv` against the 11-19 to 11-25 gains above.
3. Then apply the two tail-only edits to the Robin mug and T-shirt.

---

## Drafts

### 1. Rotkehlchen T-Shirt Aquarell Bio-Baumwolle · [4456765393](https://www.etsy.com/listing/4456765393)

Top 10 (#1 by views) · 316 views, 20 favorites, +1 views in six days · 39.90 EUR

**Current title** (125 chars): `Rotkehlchen T-Shirt Aquarell Bio-Baumwolle, Vogel Shirt Geschenk Naturliebhaber, Weihnachtsgeschenk, Vogel Liebhaber Geschenk`

**New title** (129 chars): `Rotkehlchen T-Shirt Aquarell, Bio-Baumwolle Unisex Shirt, Vogel Geschenk für Naturliebhaber, Weihnachtsgeschenk, Robin Bird Shirt`

**Why:** The front (`Rotkehlchen T-Shirt Aquarell`) already matches the search phrase, so it stays. Changes: adds `Unisex`, replaces the duplicated gift phrases with one `Vogel Geschenk für Naturliebhaber`, and adds an English keyword (the current title has none). Tail-only edit because this listing has the most lifetime views.

**13 tags:** `Rotkehlchen Shirt` (17), `Vogel T-Shirt` (13), `Bio Baumwolle Shirt` (19), `Geschenk Vogelfreund` (20), `Weihnachtsgeschenk` (18), `Wichtelgeschenk` (15), `Nikolausgeschenk` (16), `Gartenvogel Shirt` (17), `Heimische Vögel` (15), `Naturliebhaber Shirt` (20), `Robin T-Shirt` (13), `Bird Lover Gift` (15), `Aquarell Vogel Shirt` (20)

Paste: Rotkehlchen Shirt, Vogel T-Shirt, Bio Baumwolle Shirt, Geschenk Vogelfreund, Weihnachtsgeschenk, Wichtelgeschenk, Nikolausgeschenk, Gartenvogel Shirt, Heimische Vögel, Naturliebhaber Shirt, Robin T-Shirt, Bird Lover Gift, Aquarell Vogel Shirt

**Description, first two lines:**

> Rotkehlchen T-Shirt aus 100% Bio-Baumwolle (GOTS-zertifiziert) mit Aquarell-Illustration des heimischen Singvogels, bedruckt in Deutschland. Unisex Regular Fit, XS bis 5XL.
>
> Ein Weihnachtsgeschenk für Vogelfreund:innen und Naturliebhaber:innen, das Naturliebe trägt. „Im Frost singt es noch, ein kleines Feuer im Wintergarten.“

### 2. Rotkehlchen Tasse Aquarell · [4456775972](https://www.etsy.com/listing/4456775972)

Top 10 (#2 by views) · 277 views, 17 favorites, +26 views in six days · 21.90 EUR

**Current title** (117 chars): `Rotkehlchen Tasse Aquarell, Vogel Kaffeetasse 330ml Keramik, Geschenk Vogelliebhaber Naturkunde, Robin Watercolor Mug`

**New title** (127 chars): `Rotkehlchen Tasse Aquarell, Vogel Kaffeetasse 330 ml Keramik, Geschenk Vogelliebhaber, Weihnachtsgeschenk, Robin Watercolor Mug`

**Why:** This mug took 26 of the shop's 68 new views in the last six days, and 21.90 EUR is the price of every sale mentioned. Smallest possible edit: only `Naturkunde` (a weak search word) is swapped for `Weihnachtsgeschenk`; the first 60 characters do not change. The last description sentence cross-links the `mit Spruch` mug (4493994115, 38 views), which gets almost no traffic of its own.

**13 tags:** `Rotkehlchen Tasse` (17), `Vogel Tasse` (11), `Kaffeetasse Vogel` (17), `Teetasse Rotkehlchen` (20), `Vogelliebhaber Tasse` (20), `Weihnachtsgeschenk` (18), `Wichtelgeschenk` (15), `Nikolausgeschenk` (16), `Gartenvogel Tasse` (17), `Keramiktasse 330ml` (18), `Robin Mug` (9), `Bird Lover Gift` (15), `Heimische Vögel` (15)

Paste: Rotkehlchen Tasse, Vogel Tasse, Kaffeetasse Vogel, Teetasse Rotkehlchen, Vogelliebhaber Tasse, Weihnachtsgeschenk, Wichtelgeschenk, Nikolausgeschenk, Gartenvogel Tasse, Keramiktasse 330ml, Robin Mug, Bird Lover Gift, Heimische Vögel

**Description, first two lines:**

> Rotkehlchen Tasse im Aquarell-Stil: rostrote Brust, freundlicher Blick, beidseitig bedruckt auf hochweißer Keramik, 330 ml, spülmaschinen- und mikrowellengeeignet.
>
> Ein Geschenk für Vogelliebhaber:innen, bedruckt in Deutschland, kostenloser Versand innerhalb Deutschlands. Das Motiv gibt es auch mit Gedicht: Rotkehlchen Tasse mit Spruch.

### 3. Eisvogel Hoodie Linolschnitt Bio-Baumwolle · [4456776688](https://www.etsy.com/listing/4456776688)

Top 10 (#3 by views) · 158 views, 8 favorites, +7 views in six days · 64.90 EUR

**Current title** (90 chars): `Eisvogel Hoodie Linolschnitt Bio-Baumwolle, Vogel Sweater Geschenk, Kingfisher Bird Hoodie`

**New title** (125 chars): `Eisvogel Hoodie Linolschnitt, Vogel Kapuzenpullover mit Bio-Baumwolle, Sweater Geschenk für Naturliebhaber, Kingfisher Hoodie`

**Why:** Current title says `Bio-Baumwolle` as if the whole garment were; the specs say 85% organic cotton / 15% recycled polyester, so the draft says `mit Bio-Baumwolle`. Adds the German word buyers use for the product, `Kapuzenpullover`.

**13 tags:** `Eisvogel Hoodie` (15), `Vogel Hoodie` (12), `Vogel Kapuzenpulli` (18), `Eisvogel Pullover` (17), `Linolschnitt Hoodie` (19), `Natur Hoodie` (12), `Nachhaltiger Hoodie` (19), `Weihnachtsgeschenk` (18), `Wichtelgeschenk` (15), `Geschenk Vogelfreund` (20), `Kingfisher Hoodie` (17), `Heimische Vögel` (15), `Eisvogel Geschenk` (17)

Paste: Eisvogel Hoodie, Vogel Hoodie, Vogel Kapuzenpulli, Eisvogel Pullover, Linolschnitt Hoodie, Natur Hoodie, Nachhaltiger Hoodie, Weihnachtsgeschenk, Wichtelgeschenk, Geschenk Vogelfreund, Kingfisher Hoodie, Heimische Vögel, Eisvogel Geschenk

**Description, first two lines:**

> Eisvogel Hoodie mit kraftvollem Linolschnitt-Motiv: 85% Bio-Baumwolle, 15% recyceltes Polyester, 320 g/m² mit weichem Innenfleece, Kapuze und Kängurutasche.
>
> Unisex Regular Fit, XS bis 5XL, bedruckt in Deutschland, ein warmer Begleiter für Naturliebhaber:innen. „Ein Blitz aus Kobalt, dann Stille, der Fluss hält den Atem an.“

**Check before publishing:** The live description's first sentence says `100% Bio-Baumwolle`, but its own spec list says 85% / 15%. Fix the live text; the draft above uses the spec-list figures.

### 4. Stieglitz Poster A2 Botanische Illustration · [4456775898](https://www.etsy.com/listing/4456775898)

Top 10 (#4 by views) · 144 views, 11 favorites, +2 views in six days · 44.90 EUR

**Current title** (117 chars): `Stieglitz Poster A2 Botanische Illustration, Distelfink Wanddeko, Geschenk Vogelliebhaber, Goldfinch Naturkunde Print`

**New title** (127 chars): `Stieglitz Poster A2 Botanische Illustration, Distelfink Kunstdruck Wanddeko, Geschenk Vogelliebhaber, Goldfinch Botanical Print`

**Why:** Adds `Kunstdruck` (the word for a poster as wall art) and the synonym `Distelfink` stays next to it. `Naturkunde` dropped, `Botanical` made explicit in the English tail so it separates from the Robin linocut poster.

**13 tags:** `Stieglitz Poster` (16), `Distelfink Poster` (17), `Vogel Poster A2` (15), `Botanischer Druck` (17), `Vogelkunde Poster` (17), `Kunstdruck A2` (13), `Wanddeko Wohnzimmer` (19), `Weihnachtsgeschenk` (18), `Wichtelgeschenk` (15), `Einzugsgeschenk` (15), `Ornithologie Poster` (19), `Goldfinch Print` (15), `Heimische Vögel` (15)

Paste: Stieglitz Poster, Distelfink Poster, Vogel Poster A2, Botanischer Druck, Vogelkunde Poster, Kunstdruck A2, Wanddeko Wohnzimmer, Weihnachtsgeschenk, Wichtelgeschenk, Einzugsgeschenk, Ornithologie Poster, Goldfinch Print, Heimische Vögel

**Description, first two lines:**

> Stieglitz Poster A2 im Stil klassischer botanischer Illustration, fein gezeichnet und beschriftet: DIN A2 (42 x 59,4 cm), Giclée-Qualität auf mattem 200 g/m² Premium-Fotopapier, bedruckt in Deutschland.
>
> Wanddeko für Naturliebhaber:innen, gerollt in stabiler Versandröhre, Rahmen nicht enthalten (passend zu Standardrahmen A2). „Wo die Distel blüht, singt die Welt in Farbe.“

### 5. Rotkehlchen Poster A2 Linolschnitt · [4456776284](https://www.etsy.com/listing/4456776284)

Top 10 (#5 by views) · 138 views, 10 favorites, +4 views in six days · 44.90 EUR

**Current title** (107 chars): `Rotkehlchen Poster A2 Linolschnitt, Vogel Wanddeko Naturkunde, Geschenk Vogelliebhaber, Robin Linocut Print`

**New title** (127 chars): `Rotkehlchen Poster A2 Linolschnitt, Vogel Kunstdruck Wanddeko, Geschenk Vogelliebhaber, Weihnachtsgeschenk, Robin Linocut Print`

**Why:** Linolschnitt is the differentiator against the botanical Robin poster (4456775420), so style words (`Linolschnitt`, `Linoldruck`, `Linocut`) carry the tags and the botanical words stay off this listing.

**13 tags:** `Rotkehlchen Poster` (18), `Linolschnitt Poster` (19), `Linoldruck Vogel` (16), `Vogel Poster A2` (15), `Kunstdruck A2` (13), `Wanddeko Wohnzimmer` (19), `Wanddeko Küche` (14), `Weihnachtsgeschenk` (18), `Wichtelgeschenk` (15), `Einzugsgeschenk` (15), `Robin Linocut Print` (19), `Wintervogel Bild` (16), `Heimische Vögel` (15)

Paste: Rotkehlchen Poster, Linolschnitt Poster, Linoldruck Vogel, Vogel Poster A2, Kunstdruck A2, Wanddeko Wohnzimmer, Wanddeko Küche, Weihnachtsgeschenk, Wichtelgeschenk, Einzugsgeschenk, Robin Linocut Print, Wintervogel Bild, Heimische Vögel

**Description, first two lines:**

> Rotkehlchen Poster A2 im Linolschnitt-Stil, grafisch und kontrastreich: DIN A2 (42 x 59,4 cm) auf mattem 200 g/m² Premium-Fotopapier, bedruckt in Deutschland.
>
> Wanddeko für Naturliebhaber:innen und Singvogel-Freund:innen, gerollt in stabiler Versandröhre, Rahmen nicht enthalten. „Im Frost singt es noch, ein kleines Feuer im Wintergarten.“

### 6. Blaumeise T-Shirt Aquarell Bio-Baumwolle · [4456764353](https://www.etsy.com/listing/4456764353)

Top 10 (#6 by views) · 75 views, 2 favorites, +0 views in six days · 39.90 EUR

**Current title** (91 chars): `Blaumeise T-Shirt Aquarell Bio-Baumwolle, Gartenvogel Shirt Futterspende Geschenk, Blue Tit`

**New title** (129 chars): `Blaumeise T-Shirt Aquarell, Bio-Baumwolle Unisex Shirt, Gartenvogel Geschenk für Vogelfreunde, Weihnachtsgeschenk, Blue Tit Shirt`

**Why:** 75 views, 2 favorites. `Futterspende` is dropped (no evidence anyone searches it), `Blue Tit Shirt` made searchable as a phrase. Same structure as the Robin T-shirt so the shop reads consistently.

**13 tags:** `Blaumeise Shirt` (15), `Vogel T-Shirt` (13), `Gartenvogel Shirt` (17), `Bio Baumwolle Shirt` (19), `Singvogel Shirt` (15), `Aquarell Vogel Shirt` (20), `Vogelfreund Shirt` (17), `Weihnachtsgeschenk` (18), `Wichtelgeschenk` (15), `Geschenk Vogelfreund` (20), `Blue Tit Shirt` (14), `Bird Lover Gift` (15), `Heimische Vögel` (15)

Paste: Blaumeise Shirt, Vogel T-Shirt, Gartenvogel Shirt, Bio Baumwolle Shirt, Singvogel Shirt, Aquarell Vogel Shirt, Vogelfreund Shirt, Weihnachtsgeschenk, Wichtelgeschenk, Geschenk Vogelfreund, Blue Tit Shirt, Bird Lover Gift, Heimische Vögel

**Description, first two lines:**

> Blaumeise T-Shirt aus 100% Bio-Baumwolle (GOTS-zertifiziert) mit Aquarell-Illustration der lebhaften Gartenbesucherin, bedruckt in Deutschland. Unisex Regular Fit, XS bis 5XL.
>
> Ein Geschenk für alle, die heimische Singvögel lieben. „Auch im Frost bleibt sie blau, ein kleiner Himmel am Ast.“

### 7. Eisvogel Tasse mit Spruch Aquarell · [4494001018](https://www.etsy.com/listing/4494001018)

Top 10 (#7 by views) · 71 views, 6 favorites, +0 views in six days · 21.90 EUR

**Current title** (119 chars): `Eisvogel Tasse mit Spruch Aquarell, Vogel Kaffeetasse 330ml Keramik, Geschenk Vogelliebhaber, Kingfisher Watercolor Mug`

**New title** (129 chars): `Eisvogel Tasse mit Spruch Aquarell, Vogel Kaffeetasse 330 ml Keramik, Geschenk Vogelliebhaber, Weihnachtsgeschenk, Kingfisher Mug`

**Why:** Keeps `mit Spruch` because the title promises a verse. There is a second Eisvogel mug (4567201669, 9 views) with a different motif; this listing keeps `Spruch`, the other should lean on `Weide am Fluss`.

**13 tags:** `Eisvogel Tasse` (14), `Vogel Tasse` (11), `Kaffeetasse Vogel` (17), `Spruchtasse Vogel` (17), `Tasse mit Spruch` (16), `Vogelliebhaber Tasse` (20), `Weihnachtsgeschenk` (18), `Wichtelgeschenk` (15), `Nikolausgeschenk` (16), `Keramiktasse 330ml` (18), `Kingfisher Mug` (14), `Bird Lover Gift` (15), `Naturfreund Geschenk` (20)

Paste: Eisvogel Tasse, Vogel Tasse, Kaffeetasse Vogel, Spruchtasse Vogel, Tasse mit Spruch, Vogelliebhaber Tasse, Weihnachtsgeschenk, Wichtelgeschenk, Nikolausgeschenk, Keramiktasse 330ml, Kingfisher Mug, Bird Lover Gift, Naturfreund Geschenk

**Description, first two lines:**

> Eisvogel Tasse im Aquarell-Stil: Sturzflug aus dem Geäst über klarem Wasser, kobaltblauer Rücken, orangerote Brust, beidseitig bedruckt auf hochweißer Keramik (330 ml).
>
> Spülmaschinen- und mikrowellengeeignet, bedruckt in Deutschland, eine Geschenkidee für Vogel- und Naturliebhaber:innen. „Ein Blitz aus Kobalt, dann Stille, der Fluss hält den Atem an.“

**Check before publishing:** Title says `mit Spruch`, but the feed description's first sentence does not say the verse is printed on the mug (the Zaunkönig `mit Spruch` mug says so explicitly). Check the listing photos before publishing the description lines above (the same gap affects eight more `mit Spruch Aquarell` mugs, see the problems section).

### 8. Rotkehlchen Poster A2 Botanische Illustration · [4456775420](https://www.etsy.com/listing/4456775420)

Top 10 (#8 by views) · 61 views, 3 favorites, +0 views in six days · 44.90 EUR

**Current title** (120 chars): `Rotkehlchen Poster A2 Botanische Illustration, Vogel Wanddeko Naturkunde, Geschenk Vogelliebhaber, Robin Botanical Print`

**New title** (137 chars): `Rotkehlchen Poster A2 Botanische Illustration, Vogelkunde Kunstdruck beschriftet, Wanddeko Geschenk Vogelliebhaber, Robin Botanical Print`

**Why:** Pair of the linocut poster above; kept apart on purpose (botanical / Vogelkunde / Ornithologie words here, Linolschnitt words there) so the two Robin posters do not fight for the same query.

**13 tags:** `Rotkehlchen Bild` (16), `Botanischer Druck` (17), `Vogelkunde Poster` (17), `Naturkunde Poster` (17), `Ornithologie Poster` (19), `Kunstdruck A2` (13), `Vogel Bild A2` (13), `Weihnachtsgeschenk` (18), `Wichtelgeschenk` (15), `Einzugsgeschenk` (15), `Geschenk Ornithologe` (20), `Robin Botanical Art` (19), `Heimische Vögel` (15)

Paste: Rotkehlchen Bild, Botanischer Druck, Vogelkunde Poster, Naturkunde Poster, Ornithologie Poster, Kunstdruck A2, Vogel Bild A2, Weihnachtsgeschenk, Wichtelgeschenk, Einzugsgeschenk, Geschenk Ornithologe, Robin Botanical Art, Heimische Vögel

**Description, first two lines:**

> Rotkehlchen Poster A2 im Stil klassischer botanischer Illustration, fein gezeichnet und beschriftet: DIN A2 (42 x 59,4 cm), Giclée-Qualität auf mattem 200 g/m² Premium-Fotopapier, bedruckt in Deutschland.
>
> Wanddeko für Naturliebhaber:innen und Singvogel-Freund:innen, gerollt in stabiler Versandröhre, Rahmen nicht enthalten. „Im Frost singt es noch, ein kleines Feuer im Wintergarten.“

### 9. Zaunkönig Poster A2 Botanische Illustration · [4456775240](https://www.etsy.com/listing/4456775240)

Top 10 (#9 by views, tied at 60) · 60 views, 9 favorites, +0 views in six days · 44.90 EUR

**Current title** (80 chars): `Zaunkönig Poster A2 Botanische Illustration, Vogel Wanddeko, Wren Bird Art Print`

**New title** (116 chars): `Zaunkönig Poster A2 Botanische Illustration, Vogel Kunstdruck Wanddeko, Geschenk Vogelliebhaber, Wren Bird Art Print`

**Why:** Highest favorite rate in the top ten (9 of 60 views, 15%) with no `Geschenk` phrase in the current title, so the gift words are the main addition.

**13 tags:** `Zaunkönig Poster` (16), `Zaunkönig Bild` (14), `Botanischer Druck` (17), `Vogelkunde Poster` (17), `Ornithologie Poster` (19), `Kunstdruck A2` (13), `Wanddeko Wohnzimmer` (19), `Weihnachtsgeschenk` (18), `Wichtelgeschenk` (15), `Einzugsgeschenk` (15), `Wren Poster` (11), `Vogel Poster A2` (15), `Heimische Vögel` (15)

Paste: Zaunkönig Poster, Zaunkönig Bild, Botanischer Druck, Vogelkunde Poster, Ornithologie Poster, Kunstdruck A2, Wanddeko Wohnzimmer, Weihnachtsgeschenk, Wichtelgeschenk, Einzugsgeschenk, Wren Poster, Vogel Poster A2, Heimische Vögel

**Description, first two lines:**

> Zaunkönig Poster A2 im Stil klassischer botanischer Illustration, fein gezeichnet und beschriftet: DIN A2 (42 x 59,4 cm), mattes 200 g/m² Premium-Fotopapier, bedruckt in Deutschland.
>
> Wanddeko für Naturliebhaber:innen und Singvogel-Freund:innen, gerollt in stabiler Versandröhre, Rahmen nicht enthalten. „Klein, doch sein Lied bricht durch den Morgen.“

### 10. Stieglitz Jutebeutel Aquarell Bio-Baumwolle · [4456775774](https://www.etsy.com/listing/4456775774)

Top 10 (#10 by views, tied at 60) · 60 views, 2 favorites, +3 views in six days · 34.90 EUR

**Current title** (83 chars): `Stieglitz Jutebeutel Aquarell Bio-Baumwolle, Vogel Stoffbeutel, Goldfinch Bird Tote`

**New title** (122 chars): `Stieglitz Stoffbeutel Aquarell, Bio-Baumwolle Tasche mit langen Henkeln, Vogel Einkaufsbeutel Geschenk, Goldfinch Tote Bag`

**Why:** The listing is a cotton bag, so the title says `Stoffbeutel` and `Bio-Baumwolle`. `Jutebeutel` stays only as a tag, because German buyers use it as the generic word for a cloth bag. Decision for the shop owner: drop that tag if you do not want the word at all.

**13 tags:** `Stoffbeutel Vogel` (17), `Baumwollbeutel` (14), `Jutebeutel` (10), `Einkaufsbeutel` (14), `Stieglitz Beutel` (16), `Distelfink Tasche` (17), `Bio Baumwolltasche` (18), `Nachhaltige Tasche` (18), `Weihnachtsgeschenk` (18), `Wichtelgeschenk` (15), `Geschenk Vogelfreund` (20), `Tote Bag Vogel` (14), `Goldfinch Tote Bag` (18)

Paste: Stoffbeutel Vogel, Baumwollbeutel, Jutebeutel, Einkaufsbeutel, Stieglitz Beutel, Distelfink Tasche, Bio Baumwolltasche, Nachhaltige Tasche, Weihnachtsgeschenk, Wichtelgeschenk, Geschenk Vogelfreund, Tote Bag Vogel, Goldfinch Tote Bag

**Description, first two lines:**

> Stieglitz Stoffbeutel aus 100% Bio-Baumwolle (GOTS-zertifiziert) im Aquarell-Stil, ca. 38 x 42 cm mit langen Henkeln für die Schulter, bedruckt in Deutschland.
>
> Nachhaltige Einkaufstasche mit Charakter für Naturliebhaber:innen, waschbar bei 30°C. „Wo die Distel blüht, singt die Welt in Farbe.“

**Check before publishing:** Current title and feed category say `Jutebeutel`, the description says `Jutebeutel aus Bio-Baumwolle` and `100% Bio-Baumwolle`. Jute and cotton are different materials; the same contradiction was noted in the 2026-10-13 notes. Confirm the material and make title and description agree.

### 11. Stieglitz T-Shirt Distelfink Aquarell Bio-Baumwolle · [4456775670](https://www.etsy.com/listing/4456775670)

Favorites pick (4 favorites on 15 views) · 15 views, 4 favorites, +0 views in six days · 39.90 EUR

**Current title** (96 chars): `Stieglitz T-Shirt Distelfink Aquarell Bio-Baumwolle, Vogel Shirt Geschenk Naturfreund, Goldfinch`

**New title** (135 chars): `Stieglitz T-Shirt Aquarell, Distelfink Bio-Baumwolle Unisex Shirt, Vogel Geschenk für Naturfreunde, Weihnachtsgeschenk, Goldfinch Shirt`

**Why:** 4 favorites on 15 views is 27%, the best ratio in the shop, but the sample is tiny. This is a traffic problem, not a listing problem: a title change will not fix 15 views, which is why it is a candidate for a test pin.

**13 tags:** `Stieglitz Shirt` (15), `Distelfink Shirt` (16), `Vogel T-Shirt` (13), `Bio Baumwolle Shirt` (19), `Aquarell Vogel Shirt` (20), `Singvogel Shirt` (15), `Vogelfreund Shirt` (17), `Weihnachtsgeschenk` (18), `Wichtelgeschenk` (15), `Geschenk Vogelfreund` (20), `Goldfinch Shirt` (15), `Bird Lover Gift` (15), `Heimische Vögel` (15)

Paste: Stieglitz Shirt, Distelfink Shirt, Vogel T-Shirt, Bio Baumwolle Shirt, Aquarell Vogel Shirt, Singvogel Shirt, Vogelfreund Shirt, Weihnachtsgeschenk, Wichtelgeschenk, Geschenk Vogelfreund, Goldfinch Shirt, Bird Lover Gift, Heimische Vögel

**Description, first two lines:**

> Stieglitz T-Shirt aus 100% Bio-Baumwolle (GOTS-zertifiziert) mit detaillierter Aquarell-Illustration des Distelfinks, bedruckt in Deutschland. Unisex Regular Fit, XS bis 5XL.
>
> Ein Geschenk, das Naturliebe trägt. „Wo die Distel blüht, singt die Welt in Farbe.“

### 12. Amsel Tasse mit Spruch Aquarell · [4493994193](https://www.etsy.com/listing/4493994193)

Favorites pick (4 favorites on 41 views) · 41 views, 4 favorites, +3 views in six days · 21.90 EUR

**Current title** (115 chars): `Amsel Tasse mit Spruch Aquarell, Vogel Kaffeetasse 330ml Keramik, Geschenk Vogelliebhaber, Blackbird Watercolor Mug`

**New title** (125 chars): `Amsel Tasse mit Spruch Aquarell, Vogel Kaffeetasse 330 ml Keramik, Geschenk Vogelliebhaber, Weihnachtsgeschenk, Blackbird Mug`

**Why:** Blackbird is a common garden-bird search word in German (`Amsel`). Gift and season words added; structure matches the Robin mug.

**13 tags:** `Amsel Tasse` (11), `Vogel Tasse` (11), `Kaffeetasse Vogel` (17), `Spruchtasse Vogel` (17), `Tasse mit Spruch` (16), `Vogelliebhaber Tasse` (20), `Weihnachtsgeschenk` (18), `Wichtelgeschenk` (15), `Nikolausgeschenk` (16), `Keramiktasse 330ml` (18), `Blackbird Mug` (13), `Bird Lover Gift` (15), `Gartenvogel Tasse` (17)

Paste: Amsel Tasse, Vogel Tasse, Kaffeetasse Vogel, Spruchtasse Vogel, Tasse mit Spruch, Vogelliebhaber Tasse, Weihnachtsgeschenk, Wichtelgeschenk, Nikolausgeschenk, Keramiktasse 330ml, Blackbird Mug, Bird Lover Gift, Gartenvogel Tasse

**Description, first two lines:**

> Amsel Tasse im Aquarell-Stil: tiefschwarzes Männchen mit goldgelbem Augenring, der erste Sänger im Frühlingsgarten, beidseitig bedruckt auf hochweißer Keramik (330 ml).
>
> Spülmaschinen- und mikrowellengeeignet, bedruckt in Deutschland, eine Geschenkidee für Vogelliebhaber:innen. „Sie singt dem Morgen, bevor das Licht die Welt berührt.“

**Check before publishing:** Same open question as the Eisvogel mug: confirm the verse is actually printed on this `mit Spruch` mug before the description says so.

### 13. Eisvogel Poster A2 Botanische Illustration · [4456776576](https://www.etsy.com/listing/4456776576)

Favorites pick (4 favorites on 57 views) · 57 views, 4 favorites, +3 views in six days · 44.90 EUR

**Current title** (122 chars): `Eisvogel Poster A2 Botanische Illustration, Vogel Wanddeko Naturkunde, Geschenk Vogelliebhaber, Kingfisher Botanical Print`

**New title** (133 chars): `Eisvogel Poster A2 Botanische Illustration, Vogel Kunstdruck Wanddeko Naturkunde, Geschenk Vogelliebhaber, Kingfisher Botanical Print`

**Why:** Same poster template as the other botanical posters, with `Kunstdruck` added and the Eisvogel (the shop's second strongest species by views) in the first two words.

**13 tags:** `Eisvogel Poster` (15), `Eisvogel Bild` (13), `Botanischer Druck` (17), `Vogelkunde Poster` (17), `Ornithologie Poster` (19), `Kunstdruck A2` (13), `Wanddeko Wohnzimmer` (19), `Weihnachtsgeschenk` (18), `Wichtelgeschenk` (15), `Einzugsgeschenk` (15), `Kingfisher Poster` (17), `Vogel Poster A2` (15), `Heimische Vögel` (15)

Paste: Eisvogel Poster, Eisvogel Bild, Botanischer Druck, Vogelkunde Poster, Ornithologie Poster, Kunstdruck A2, Wanddeko Wohnzimmer, Weihnachtsgeschenk, Wichtelgeschenk, Einzugsgeschenk, Kingfisher Poster, Vogel Poster A2, Heimische Vögel

**Description, first two lines:**

> Eisvogel Poster A2 im Stil klassischer botanischer Illustration, fein gezeichnet und beschriftet: DIN A2 (42 x 59,4 cm), Giclée-Qualität auf mattem 200 g/m² Premium-Fotopapier, bedruckt in Deutschland.
>
> Wanddeko für Naturliebhaber:innen und Singvogel-Freund:innen, gerollt in stabiler Versandröhre, Rahmen nicht enthalten. „Ein Blitz aus Kobalt, dann Stille, der Fluss hält den Atem an.“

### 14. Zaunkönig Tasse mit Spruch · [4493994437](https://www.etsy.com/listing/4493994437)

Favorites pick (3 favorites on 24 views, ratio 12.5%) · 24 views, 3 favorites, +0 views in six days · 21.90 EUR

**Current title** (139 chars): `Zaunkönig Tasse mit Spruch, Spruchtasse Aquarell, Vogel Kaffeetasse 330ml Keramik, Geschenk Vogelliebhaber Naturfreund, Wren Quote Mug Gift`

**New title** (130 chars): `Zaunkönig Tasse mit Spruch Aquarell, Vogel Kaffeetasse 330 ml Keramik, Geschenk Vogelliebhaber, Weihnachtsgeschenk, Wren Quote Mug`

**Why:** Already well built; the draft adds `Weihnachtsgeschenk`, drops the repeated `Spruchtasse` and `Naturfreund` from the title to stay under 140 characters, and moves `Spruchtasse Vogel` into the tags. The tag set adds `Tasse Gedicht Vogel` for buyers who search for poems rather than `Spruch`.

**13 tags:** `Zaunkönig Tasse` (15), `Spruchtasse Vogel` (17), `Tasse mit Spruch` (16), `Vogel Tasse` (11), `Kaffeetasse Vogel` (17), `Tasse Gedicht Vogel` (19), `Weihnachtsgeschenk` (18), `Wichtelgeschenk` (15), `Nikolausgeschenk` (16), `Keramiktasse 330ml` (18), `Wren Mug` (8), `Bird Lover Gift` (15), `Heimische Vögel` (15)

Paste: Zaunkönig Tasse, Spruchtasse Vogel, Tasse mit Spruch, Vogel Tasse, Kaffeetasse Vogel, Tasse Gedicht Vogel, Weihnachtsgeschenk, Wichtelgeschenk, Nikolausgeschenk, Keramiktasse 330ml, Wren Mug, Bird Lover Gift, Heimische Vögel

**Description, first two lines:**

> Zaunkönig Tasse mit Spruch: Aquarell-Illustration plus deutscher Vers, direkt auf hochweiße Premium-Keramik gedruckt, 330 ml, spülmaschinen- und mikrowellengeeignet.
>
> Ein Geschenk für Vogel- und Wortliebhaber:innen, bedruckt in Deutschland. „Klein, doch sein Lied bricht durch den Morgen.“

### 15. Zaunkönig T-Shirt Aquarell Bio-Baumwolle · [4456775286](https://www.etsy.com/listing/4456775286)

Favorites pick (3 favorites on 34 views, ratio 8.8%) · 34 views, 3 favorites, +0 views in six days · 39.90 EUR

**Current title** (99 chars): `Zaunkönig T-Shirt Aquarell Bio-Baumwolle, Kleinster Vogel Europas, Vogel Shirt Gartenvogel Geschenk`

**New title** (130 chars): `Zaunkönig T-Shirt Aquarell, Bio-Baumwolle Unisex Shirt, Gartenvogel Geschenk für Vogelfreunde, Weihnachtsgeschenk, Wren Bird Shirt`

**Why:** Drops `Kleinster Vogel Europas` (see flag) and puts the search phrase `Zaunkönig T-Shirt` plus a gift phrase in the front half.

**13 tags:** `Zaunkönig Shirt` (15), `Vogel T-Shirt` (13), `Gartenvogel Shirt` (17), `Bio Baumwolle Shirt` (19), `Singvogel Shirt` (15), `Aquarell Vogel Shirt` (20), `Vogelfreund Shirt` (17), `Weihnachtsgeschenk` (18), `Wichtelgeschenk` (15), `Geschenk Vogelfreund` (20), `Wren Shirt` (10), `Bird Lover Gift` (15), `Heimische Vögel` (15)

Paste: Zaunkönig Shirt, Vogel T-Shirt, Gartenvogel Shirt, Bio Baumwolle Shirt, Singvogel Shirt, Aquarell Vogel Shirt, Vogelfreund Shirt, Weihnachtsgeschenk, Wichtelgeschenk, Geschenk Vogelfreund, Wren Shirt, Bird Lover Gift, Heimische Vögel

**Description, first two lines:**

> Zaunkönig T-Shirt aus 100% Bio-Baumwolle (GOTS-zertifiziert) mit detaillierter Aquarell-Illustration, bedruckt in Deutschland. Unisex Regular Fit, XS bis 5XL.
>
> Ein Geschenk, das Naturliebe trägt. „Klein, doch sein Lied bricht durch den Morgen.“

**Check before publishing:** Current title claims `Kleinster Vogel Europas`. That is not true: Sommer- und Wintergoldhähnchen are smaller than the Zaunkönig. Removed in the draft; the Zaunkönig poster and mug titles do not make the claim.

