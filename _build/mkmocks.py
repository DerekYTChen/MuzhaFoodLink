"""Generate photo-backed proposal illustrations for the wayfinding section.
Photos are embedded as data URIs because external SVG image references do not
render when an SVG is loaded using <img>. Edit this generator, then run it.
"""
import base64
from pathlib import Path

A = Path(__file__).resolve().parent.parent / "assets"
CJK = "'PingFang TC','Noto Sans CJK TC','Hiragino Sans GB','Microsoft JhengHei',sans-serif"
SANS = "'Helvetica Neue',Arial,sans-serif"
PAPER, INK, SOFT, MOSS, CORAL = "#f4ead1", "#231f1c", "#5a534b", "#2c5540", "#dd5546"

def uri(name):
    return "data:image/jpeg;base64," + base64.b64encode((A / name).read_bytes()).decode()

def sign():
    # Board sits at x438 on the same depth band as the two existing temporary
    # notice boards. It is only slightly larger, not a foreground billboard.
    p = []
    p.append('<g transform="translate(438 554) skewY(5)">')
    p.append(f'<rect width="164" height="230" rx="4" fill="{MOSS}" stroke="#242321" stroke-width="3"/>')
    p.append(f'<rect x="7" y="7" width="150" height="216" fill="{PAPER}"/>')
    p.append(f'<rect x="7" y="7" width="150" height="35" fill="{CORAL}"/>')
    p.append(f'<text x="82" y="23" text-anchor="middle" fill="#fbf6e8" font-family="{SANS}" font-size="9.5" font-weight="700" letter-spacing="1.3">CONCEPT ONLY</text>')
    p.append(f'<text x="82" y="36" text-anchor="middle" fill="#fbf6e8" font-family="{CJK}" font-size="12" font-weight="700">提案示意</text>')
    p.append(f'<text x="82" y="68" text-anchor="middle" fill="{MOSS}" font-family="{CJK}" font-size="22" font-weight="700">木柵食旅連線</text>')
    p.append(f'<text x="82" y="84" text-anchor="middle" fill="{SOFT}" font-family="{SANS}" font-size="10.5" font-weight="600" letter-spacing=".7">MUZHA FOOD LINK</text>')
    p.append(f'<path d="M82 96 L106 126 H94 V154 H70 V126 H58 Z" fill="{CORAL}"/>')
    p.append(f'<text x="82" y="178" text-anchor="middle" fill="{INK}" font-family="{CJK}" font-size="17" font-weight="700">直走 1.9 公里</text>')
    p.append(f'<text x="82" y="191" text-anchor="middle" fill="{SOFT}" font-family="{SANS}" font-size="9.2" letter-spacing=".35">STRAIGHT AHEAD · 1.9 KM</text>')
    p.append(f'<path d="M24 198 H140" stroke="{INK}" stroke-width="1" opacity=".25"/>')
    p.append(f'<text x="82" y="212" text-anchor="middle" fill="{MOSS}" font-family="{CJK}" font-size="10">憑當日門票，招待小菜</text>')
    p.append(f'<text x="82" y="221" text-anchor="middle" fill="{SOFT}" font-family="{SANS}" font-size="7.5">same-day ticket treat</text>')
    p.append('<rect x="7" y="7" width="150" height="216" fill="url(#overcast)" opacity=".30"/>')
    p.append('<rect x="7" y="7" width="150" height="216" fill="url(#grain)" opacity=".13"/>')
    p.append('</g>')
    panel = '\n    '.join(p)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 1466 882" role="img">
 <defs>
  <linearGradient id="overcast" x1="0" y1="0" x2=".7" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".55"/><stop offset="1" stop-color="#4c5450" stop-opacity=".85"/></linearGradient>
  <filter id="soft" x="-40%" y="-60%" width="180%" height="240%"><feGaussianBlur stdDeviation="6"/></filter>
  <filter id="grain"><feTurbulence type="fractalNoise" baseFrequency=".7" numOctaves="2" seed="3"/></filter>
 </defs>
 <image xlink:href="{uri('gondola-station.jpg')}" width="1466" height="882" preserveAspectRatio="xMidYMid slice"/>
 <g>
  <ellipse cx="520" cy="798" rx="83" ry="10" fill="#1a1a18" opacity=".25" filter="url(#soft)"/>
  <path d="M457 769 L451 798 M584 783 L591 802" stroke="#494a48" stroke-width="5" stroke-linecap="round"/>
  {panel}
  <rect x="436" y="793" width="29" height="11" rx="4" fill="#bebdb7" opacity=".85"/>
  <rect x="578" y="797" width="29" height="11" rx="4" fill="#bebdb7" opacity=".85"/>
 </g>
</svg>'''

def decal():
    # Small, semi-transparent rectangle on the right door glass, not an opaque
    # second signboard. Its y band remains visible through the site's crop.
    d = []
    d.append('<g transform="translate(562 548) skewY(1.2)">')
    d.append(f'<rect width="202" height="176" rx="11" fill="{PAPER}" fill-opacity=".87" stroke="{MOSS}" stroke-width="5"/>')
    d.append(f'<text x="101" y="23" text-anchor="middle" fill="{CORAL}" font-family="{CJK}" font-size="12" font-weight="700">提案示意</text>')
    d.append(f'<text x="101" y="35" text-anchor="middle" fill="{CORAL}" font-family="{SANS}" font-size="8" font-weight="700" letter-spacing="1">PROPOSAL SAMPLE</text>')
    d.append(f'<text x="101" y="59" text-anchor="middle" fill="{INK}" font-family="{CJK}" font-size="15">我們是</text>')
    d.append(f'<text x="101" y="84" text-anchor="middle" fill="{MOSS}" font-family="{CJK}" font-size="13.5" font-weight="700">「木柵食旅連線」店家</text>')
    d.append(f'<text x="101" y="103" text-anchor="middle" fill="{SOFT}" font-family="{SANS}" font-size="9" font-weight="600" letter-spacing=".45">WE ARE A MUZHA FOOD LINK SHOP</text>')
    d.append(f'<path d="M22 115 H180" stroke="{INK}" stroke-width="1" opacity=".25"/>')
    d.append(f'<text x="101" y="137" text-anchor="middle" fill="{MOSS}" font-family="{CJK}" font-size="12" font-weight="700">憑當日動物園門票，招待小菜</text>')
    d.append(f'<text x="101" y="153" text-anchor="middle" fill="{SOFT}" font-family="{SANS}" font-size="9">Show your same-day zoo ticket</text>')
    d.append(f'<text x="101" y="169" text-anchor="middle" fill="{SOFT}" font-family="{SANS}" font-size="8" opacity=".85">for a small treat from us</text>')
    d.append('<path d="M0 176 L88 0 H132 L44 176 Z" fill="#fff" opacity=".12"/>')
    d.append('</g>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 1200 1200" role="img">
 <image xlink:href="{uri('dianwei.jpg')}" width="1200" height="1200"/>
 {''.join(d)}
</svg>'''

for name, art in [('wayfinding-sign-mockup.svg', sign()), ('dianwei-window-decal-mockup.svg', decal())]:
    (A / name).write_text(art, encoding='utf8')
    print(name, len(art) // 1024, 'KB')
