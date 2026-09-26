#!/usr/bin/env python3
"""Assemble index.html from index.template.html plus the generated fragments.

Run from the _build directory:  uv run python build.py
Regenerate the fragments first if the map or chart data changed:
    uv run python mkmap4.py     -> map_frag.svg, pins_frag.svg, stops_frag.html
    uv run python mkchart.py    -> chart_frag.svg
"""
import pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
SITE = HERE.parent

FRAGMENTS = {
    "MAPFRAG":   "map_frag.svg",
    "PINFRAG":   "pins_frag.svg",
    "STOPSFRAG": "stops_frag.html",
    "CHARTFRAG": "chart_frag.svg",
    "SIZEFRAG":  "sizing_frag.html",
}

def main() -> int:
    tpl = (SITE / "index.template.html").read_text(encoding="utf-8")
    out = tpl
    for name, fn in FRAGMENTS.items():
        token = "<!--%s-->" % name
        if token not in out:
            print("error: %s missing from the template" % token); return 1
        out = out.replace(token, (HERE / fn).read_text(encoding="utf-8"))

    left = re.findall(r"<!--([A-Z]+FRAG)-->", out)
    if left:
        print("error: unreplaced placeholders %s" % left); return 1

    (SITE / "index.html").write_text(out, encoding="utf-8")
    print("index.html  %d bytes  fragments=%d" % (len(out), len(FRAGMENTS)))
    for label, pat in (("stops", r"<li data-stop"), ("pins", r'class="m-pin"'),
                       ("pikmin", r'class="m-pk '), ("chart bars", r'class="sc-bar[ "]')):
        print("  %-11s %d" % (label, len(re.findall(pat, out))))
    return 0

if __name__ == "__main__":
    sys.exit(main())
