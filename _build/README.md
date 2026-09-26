# Build assets for the Muzha Food Link page

Everything on the page is generated from verified data. Nothing here is decorative guesswork.

## Data sources (all OpenStreetMap via Overpass, cross-checked with Nominatim)
- `roads2.json` — all non-motorway highways in bbox 24.9650,121.5590,25.0025,121.6005
- `extra2.json` — rivers, lakes, the Taipei Zoo polygon, the NCCU campus relation
- `aerial.json` — the 貓空纜車 (Maokong Gondola) `aerialway` ways plus its six stations
- `maokong.json` — named food and tea POIs on the Maokong ridge
- NCCU and Taipei Zoo are both in 萬興里, Wenshan District (confirmed via Nominatim)
- 麵匡匡拉麵食堂 resolved to 24.9869994, 121.5685427 (保儀路 73 號)

## Scripts
- `route.py`   — builds a walking graph from every road node and runs Dijkstra from the
                 NCCU main gate (24.98722, 121.57705) to the zoo entrance (24.99843, 121.58060).
                 Result: **1,867 m** → the page says 1.9 km. Writes `route_path.json`.
- `mkmap4.py`  — current generator. Projects roads, the Jingmei River, lakes, the zoo,
                 the campus, the walking route, the gondola cable and its stations, plus
                 20 stop pins into the **1200 x 1559** SVG viewBox (equirectangular,
                 cos(24.985°) x-scale, bounds lat 24.9655–25.0020, lon 121.5640–121.5950).
                 Ramer-Douglas-Peucker simplification keeps the markup near 25 KB.
                 Pin bubbles are spread by a repulsion solver (R=16, max leader 44 px);
                 a leader line still points at the true coordinate.
                 Dijkstra falls back to the nearest *reachable* node if the snapped target
                 is on a disconnected component.
                 Writes `map_frag.svg`, `pins_frag.svg` and `stops_frag.html`
                 (the stop list is generated so the numbering can never drift from the pins).
- `g2.py`      — generates the eight YouTube QR codes (ERROR_CORRECT_M) into `../qr/*.svg`.
                 All eight were decoded back with OpenCV to confirm they resolve to the
                 correct `https://youtu.be/<id>`.
- Obsolete: `mkmap3.py`, `mkmap2.py`, `pins.py`, `roads.json`, `extra.json`.

## The 20 stops, in five clusters
1. zoo gate (1), 2. Zhinan/Wanshou student strip (2-10), 3. older Muzha blocks incl.
麵匡匡 and 保儀路 (11-15), 4. inside the NCCU campus (16), 5. Maokong tea houses at the
top of the gondola (17-20).

## Rebuilding index.html

```
cd _build
uv run python mkmap4.py     # map_frag.svg, pins_frag.svg, stops_frag.html
uv run python mkchart.py    # chart_frag.svg
uv run python build.py      # index.html
```

`build.py` refuses to write the file if any `<!--...FRAG-->` placeholder is
missing from the template or left unreplaced, and prints the element counts
so a silently empty fragment is visible. Do not hand-type the replacement
command: there are four fragments now and forgetting one produces a page
that looks fine until the missing section is scrolled to.

Bump the `?v=` query on `styles.css`, `i18n.js`, `ambient.js` and
`script.js` in the template whenever you touch them. Browser caching in this
project has served stale JS repeatedly.

## Deliberate omissions and honesty rules
- Google Maps star ratings are **not** shown. They cannot be retrieved programmatically
  without the paid Places API, and inventing them would be dishonest. The copy says
  ratings will be confirmed in person before publication.
- There is **no supporter counter**. Nobody has been contacted yet, so the page states
  plainly that this is a proposal, not a set of commitments.
- The form has **no backend**. Submitting builds a `mailto:derekyt.chen@gmail.com` draft
  in the visitor's own mail app; nothing is stored anywhere.

## Pikmin Bloom activity layer (added 2026-09-24)

An optional map layer, **off by default**, behind the "Show Pikmin Bloom activity"
toggle under the map. Toggle state persists in `localStorage` key `mfl-pikmin`.

### What it is
Pikmin Bloom seeds mushrooms from where people actually walk, so the pattern is a
rough proxy for pedestrian activity. This is the only reason the layer is worth
having: it speaks to the essay's foot-traffic argument.

### Source
9 Pikmin Bloom screenshots taken by one player between **23:07 and 23:35 on
2026-09-24**, stored in `pikmin/`:
- `orig1..4.jpeg` - first batch (zoo, Maokong, 木柵, 十五份 area)
- `pair1..5_b.jpeg` - Pikmin frames; `pair1..5_a.jpeg` - matching Google Maps frames

### How it is georeferenced (exactly, not by eye)
Pikmin renders OSM `place=hamlet` nodes as its place labels. Every label in the
screenshots (十五分, 十一命, 頂店, 渡船巷, 渡船頭, 打鐵寮, 外埔, 炮子林,
番仔公館, 灰窯坑, 軍功坑, 抱子腳) is a real OSM node. Coordinates were fetched
from Nominatim by `q_nom.py` -> `anchors.json`, cross-checked against the
Overpass place dump in `places.json` (119 nodes). 動物園 and 貓纜轉角一 use the
gondola station nodes already in `aerial.json`.

So **positions are exact**. No pixel-to-lat/lon fitting was needed, and the
Google Maps screenshots ended up serving only as a sanity check on which
junction was which.

### Why levels and not counts
Counting is the weak link, not positioning. Automated sprite detection
(`detect.py`, colour-matching the dark green count badges, output in
`badges.json`) found only 4-9 badges per frame where 8-14 are visible, because
badges overlap each other and JPEG compression smears the edges. Counts were
therefore made by eye and are +/-2, so they are published as buckets:

    3 = many clusters   2 = several   1 = one or two   0 = none seen

`RAD` in `mkmap4.py` maps level to circle radius (46/32/21/13 px).

### The 11 points shown
    動物園 3, 外埔 (NCCU) 3, 頂店 2, 十一命 2, 渡船巷 2, 貓纜轉角一 2,
    抱子腳 1, 打鐵寮 1, 渡船頭 1, 番仔公館 1, 炮子林 0

Not shown: 十五分, 軍功坑, 灰窯坑 fall outside the map bounds
(lat 24.9655-25.0020, lon 121.5640-121.5950).

### The observation it supports
The cluster band follows the NCCU corridor and the Muzha street grid and thins
out toward the hills. That gradient is robust to the +/-2 counting error; the
individual numbers are not.

### Honesty rules for this layer
- One snapshot by one player on one night. Never call it a survey or a count.
- The caveat text (`map.pk.caveat`, both languages) must stay visible whenever
  the layer is on; `script.js` `pikmin()` ties them together.
- Do not add per-mushroom pins. That would imply a precision the source
  screenshots cannot support.

## Decorative flora
`mkmap4.py` also scatters ~158 small flowers across empty green space
(deterministic, seed 7), rejected within 52 px of a pin, 15 px of the route and
13 px of water. Pure ornament, carries no data, and has no legend entry. The
decorative mushrooms that were in the first version were **removed** so nothing
competes visually with the activity glyphs.

---

## Seasonality chart (section 02, "Why the winter break")

Added so the site evidences the essay's central claim instead of asserting it.

**Source.** `zoo_monthly.pdf` in this folder, downloaded from the Taipei City
Government file server and linked on the page to the zoo's own annual-report
index. It is 臺北市立動物園107年至115入園人數統計表: monthly admissions for ROC
years 107 to 115, i.e. 2018 to 2026. The numbers transcribed into
`zoo_data.py` are 2024 and 2025 only.

**Why those two years.** 2020 to 2022 are COVID-distorted in every month
(March 2020 falls to 129,839 against a normal ~280,000), so including them
would flatten the seasonal signal the chart exists to show. 2026 is
incomplete. 2018 and 2019 are usable but older; two recent full years is
enough to show a pattern without implying more precision than there is.

**The finding.** January and February are the zoo's two strongest months at
about +25% against its own 12-month mean of 212,537. Those are exactly the
weeks NCCU's winter break empties the campus. June and September, when
students are on campus, are the two weakest at about -42%. The two
seasonalities are genuinely anti-correlated, and the summer break is *not*
symmetric, which is the real reason the pilot targets winter. That
asymmetry is a finding, not a convenience: it would have been easier to
claim both breaks work.

**The chart is language-neutral on purpose.** `mkchart.py` emits only
numerals inside the SVG (month numbers 1-12, values in thousands), so one
fragment serves both languages. Every word around it is an i18n key. Month
names or a "average" label inside the SVG would have forced two fragments.

Regenerate with `uv run python mkchart.py` -> `chart_frag.svg`.

**Narrow screens.** Twelve bars with numeric labels are illegible below about
620px, and scaling the SVG down scales its text down with it. The chart is
therefore given `min-width:620px` inside `.chart-scroll{overflow-x:auto}`
rather than allowed to shrink.

## Section 04, "How I mapped this"

The method and its limits, promoted out of a tooltip and onto the page: the
route computed on OSM geometry (1,867 m), the 20 stops at true coordinates
with ratings deliberately omitted as unverified, and the Pikmin Bloom survey
with its one-player/one-night/±2 limits stated in the body text. This
section exists because the map's credibility comes from how it was made, and
none of that was visible to a reader.

## Section 06 addition, the pilot spec

Six rows: the offer (a same-day extra, not a discount, because margins are
thin), what it costs a shop (nothing but the extra), what a shop gets,
size and length, what gets measured, and an explicit stop rule (fewer than
five redemptions a week per shop by week four ends it). The stop rule is
labelled as a self-set threshold, not a validated benchmark.

## Video wall trimmed 8 -> 3

Eight third-party YouTube links read as a link farm and none of them are
Derek's work. Three are kept, chosen because each shows the actual corridor.
The five unused `qr/*.svg` files are left in place but no longer referenced.

## Grid overflow fix

`repeat(auto-fit,minmax(300px,1fr))` forces a track wider than a 308px
viewport, so five grids overflowed horizontally on small phones
(`.method-grid`, `.method-notes`, `.spec-list`, and the pre-existing
`.timeline` and `.metrics>div`). All now use
`minmax(min(300px,100%),1fr)`, which is identical at wide widths.

## The background score (`../ambient.js`)

Replaced 2026-09-26. It used to be a 132 BPM carnival march, which suited a
consumer campaign page but not a proposal about three shops closing. The score
is now a slow warm room: 72 BPM, 4/4, a four-bar loop of Am9 - Fmaj7 - C - G,
played by a felt piano, a breathing saw pad, upright-bass plucks, a brushed
shaker kept almost under the floor, and an occasional vibraphone bell. Reverb
is much wetter (`wet` 0.13 -> 0.30, IR 1.0s -> 2.8s).

Nothing above `CFG` changed: `mtof`, `impulse`, `noiseBuffer`, `chain`, the
live player, the visibility ducking and `render()` are untouched, and the
public API is still `{start, stop, toggle, isPlaying, render}`.

Measured with a throwaway `_measure.html` that renders 24 s through
`OfflineAudioContext` and prints the numbers into a `<pre>`; the file is
deleted after each pass so it never ships.

| | carnival (old) | room (new) |
|---|---|---|
| peak | -9.3 dBFS | -10.6 dBFS |
| RMS | -26.3 dBFS | -27.9 dBFS |
| clipped samples | 0 | 0 |
| onsets / sec | 10.96 | 1.08 |
| stereo width | not measured | 0.285 |

The tenfold drop in onsets is the point, not a regression: do not "fix" it.

## The wayfinding illustrations (`../assets/`)

Added 2026-09-26, in section 06 next to the pilot spec, as `.wayfinding`.
Two concept mock-ups answering the one question the map cannot: how a zoo
family notices this route at the moment they decide where to go next.

- `wayfinding-sign-mockup.svg` - a weighted A-frame board on the gondola-station
  forecourt. Base is Derek's own 2026 photograph of the actual exit, supplied
  after the first mock-up. It replaced the Street View base entirely; there is
  no Google imagery or attribution in this artefact.
- `dianwei-window-decal-mockup.svg` - a removable decal on the glass at
  滇味廚房. Base is Derek's own September 2026 photograph.

Both are generated by `mkmocks.py`, which carries the scene measurements in its
docstring: where the two real notice boards stand, the pavement plane the board
is skewed onto, and the crop band the CSS actually shows. Edit the generator,
never the SVG, then re-run `uv run python mkmocks.py`.

Two content rules set by the user on 2026-09-26: the board's arrow points
**straight up**, because from the gondola-station forecourt the food strip is
1.9 km straight ahead and not a turn; and the decal reads as a participation
badge (`我們是「木柵食旅連線」店家`), not a generic advert. Every line on both
artefacts is Chinese **and** English, because the zoo draws international
families in the same holiday weeks the pilot targets.

Both SVGs carry the photo as a **base64 data URI**, not an external `href`.
That is required: an SVG loaded through `<img src>` runs in secure static mode
and browsers block every external resource it asks for, so a linked photo
renders as a blank plate. `gondola-station.jpg` and `dianwei.jpg` are the
downscaled sources kept for regeneration (`sips -Z 1100 -s format jpeg`); they
are not served.

Framing rules these files must keep:
- The signs self-label `CONCEPT ONLY / 提案示意` and `PROPOSAL SAMPLE / 提案示意`
  inside the artwork, so a screenshot cannot be mistaken for an installation.
- The copy separates convening from permitting: the Village Chief can bring
  people to the table, but the site owner or the zoo approves placement. A 里長
  cannot authorise street furniture, and the page must never imply otherwise.
- 滇味廚房 has not agreed to anything. Say so wherever the image appears.

Alt text comes from `way.sign.alt` / `way.decal.alt` through a new
`data-i18n-alt` applier in `script.js`. Do not use `alt=""` plus
`aria-describedby` here: the empty alt drops the image from the accessibility
tree and the caption is then never announced.

`.wayfinding-grid` uses `repeat(auto-fit,...)`, not `repeat(2,...)`. A fixed
two-column track overflows a phone even with the `min()` guard.
