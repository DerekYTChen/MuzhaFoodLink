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
cd _build && uv run python mkmap4.py && cd ..
python3 -c "s=open('index.template.html',encoding='utf-8').read();\
s=s.replace('<!--MAPFRAG-->',open('_build/map_frag.svg',encoding='utf-8').read());\
s=s.replace('<!--PINFRAG-->',open('_build/pins_frag.svg',encoding='utf-8').read());\
s=s.replace('<!--STOPSFRAG-->',open('_build/stops_frag.html',encoding='utf-8').read());\
open('index.html','w',encoding='utf-8').write(s)"
```
Then re-check: every `data-i18n` key exists in both `en` and `zh`, no unused keys,
20 `<li data-stop>` matching 20 `.m-pin`, and no label or pin collisions in either language.

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
