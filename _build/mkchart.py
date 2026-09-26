# -*- coding: utf-8 -*-
"""Seasonality chart: Taipei Zoo monthly admissions, 2024-2025 mean.
Language-neutral by design: only numerals appear inside the SVG, so the
same fragment serves both the English and Chinese page. All prose labels
live in the HTML around it, keyed through i18n.
"""
from zoo_data import MEAN, AVG

W, H = 1000, 340
L, R, T, B = 46, 18, 34, 46          # plot padding
PW, PH = W - L - R, H - T - B
MAXV = 300000.0                       # fixed ceiling, round number above the peak
BREAK = {1, 2}                        # NCCU winter break months (campus closed)

def y(v): return T + PH - (v / MAXV) * PH

out = []
a = out.append
a('<svg class="season-chart" viewBox="0 0 %d %d" role="img" '
  'aria-labelledby="sc-title sc-desc">' % (W, H))
a('  <title id="sc-title" data-i18n="season.svgTitle"></title>')
a('  <desc id="sc-desc" data-i18n="season.svgDesc"></desc>')

# horizontal guides at 100k / 200k / 300k
a('  <g class="sc-grid">')
for v in (100000, 200000, 300000):
    a('    <line x1="%d" y1="%.1f" x2="%d" y2="%.1f"/>' % (L, y(v), W - R, y(v)))
    a('    <text class="sc-ax" x="%d" y="%.1f">%d</text>' % (L - 8, y(v) + 4, v // 1000))
a('  </g>')

# bars
slot = PW / 12.0
bw = slot * 0.58
a('  <g class="sc-bars">')
for i, v in enumerate(MEAN, 1):
    bx = L + slot * (i - 0.5) - bw / 2
    cls = "sc-bar sc-hi" if i in BREAK else "sc-bar"
    a('    <rect class="%s" x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3"/>'
      % (cls, bx, y(v), bw, T + PH - y(v)))
    a('    <text class="sc-val%s" x="%.1f" y="%.1f">%d</text>'
      % (" sc-valhi" if i in BREAK else "", bx + bw / 2, y(v) - 9, round(v / 1000)))
    a('    <text class="sc-mon%s" x="%.1f" y="%.1f">%d</text>'
      % (" sc-monhi" if i in BREAK else "", bx + bw / 2, T + PH + 22, i))
a('  </g>')

# 12-month average line
a('  <g class="sc-avg">')
a('    <line x1="%d" y1="%.1f" x2="%d" y2="%.1f"/>' % (L, y(AVG), W - R, y(AVG)))
a('    <text class="sc-avgv" x="%d" y="%.1f">%d</text>' % (W - R, y(AVG) - 8, round(AVG / 1000)))
a('  </g>')

# baseline
a('  <line class="sc-base" x1="%d" y1="%.1f" x2="%d" y2="%.1f"/>'
  % (L, T + PH, W - R, T + PH))
a('</svg>')

svg = "\n".join(out) + "\n"
open("chart_frag.svg", "w", encoding="utf-8").write(svg)
print("chart_frag.svg  bars=%d  peak=%d  avg=%d" % (len(MEAN), round(max(MEAN)), round(AVG)))
