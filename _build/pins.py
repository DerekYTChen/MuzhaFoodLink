import json,math
exec(open("mkmap2.py").read().split("frag=[]")[0])
STOPS=[
 (1,24.99807,121.58114),(2,24.98821,121.57640),(3,24.98781,121.57594),(4,24.98749,121.57696),
 (5,24.98735,121.57761),(6,24.98703,121.57854),(7,24.98684,121.57861),(8,24.98682,121.57879),
 (9,24.98762,121.57537),(10,24.98809,121.57386),(11,24.98768,121.56930),(12,24.98875,121.56809),
 (13,24.98818,121.56806),(14,24.98661,121.56827),(15,24.97961,121.57135),
]
o=[]
o.append('<g class="m-pins">')
for n,la,lo in STOPS:
    x,y=prj(la,lo)
    o.append(f'<g class="m-pin" data-stop="{n}" tabindex="0"><circle class="m-pin-hit" cx="{x:.0f}" cy="{y:.0f}" r="22"/><circle class="m-pin-dot" cx="{x:.0f}" cy="{y:.0f}" r="13"/><text x="{x:.0f}" y="{y+4.5:.0f}">{n}</text></g>')
o.append('</g>')
anchors=[("zoo",24.9953546,121.5861491),("mrt",24.99833,121.57945),("gate",24.9872,121.5766)]
o.append('<g class="m-anchors">')
for k,la,lo in anchors:
    x,y=prj(la,lo)
    o.append(f'<g class="m-anchor m-{k}"><circle cx="{x:.0f}" cy="{y:.0f}" r="10"/></g>')
o.append('</g>')
for k,la,lo,dx,dy,a in [("zoo",24.9953546,121.5861491,18,-14,"start"),("mrt",24.99833,121.57945,-16,-16,"end"),("gate",24.9872,121.5766,16,-18,"start")]:
    x,y=prj(la,lo)
    o.append(f'<text class="m-lbl m-lbl-{k}" x="{x+dx:.0f}" y="{y+dy:.0f}" text-anchor="{a}" data-i18n="map.lbl.{k}"></text>')
# campus + maokong direction label
x,y=prj(24.9830,121.5810); o.append(f'<text class="m-lbl m-lbl-campus" x="{x:.0f}" y="{y:.0f}" data-i18n="map.lbl.campus"></text>')
x,y=prj(24.9792,121.5900); o.append(f'<text class="m-lbl m-lbl-hint" x="{x:.0f}" y="{y:.0f}" text-anchor="end" data-i18n="map.lbl.maokong"></text>')
open("pins_frag.svg","w").write("\n".join(o))
print(len("\n".join(o)))
