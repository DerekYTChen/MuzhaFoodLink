import json, math
roads=json.load(open("roads.json"))["elements"]
extra=json.load(open("extra.json"))["elements"]

MINLAT,MAXLAT=24.9838,25.0016
MINLON,MAXLON=121.5648,121.5940
KX=math.cos(math.radians(24.99))
W=1200.0
H=round(W*((MAXLAT-MINLAT)/((MAXLON-MINLON)*KX)))
def prj(lat,lon):
    return ((lon-MINLON)/(MAXLON-MINLON)*W,(MAXLAT-lat)/(MAXLAT-MINLAT)*H)

STOPS=[(1,24.99807,121.58114),(2,24.98821,121.57640),(3,24.98781,121.57594),(4,24.98749,121.57696),
(5,24.98735,121.57761),(6,24.98703,121.57854),(7,24.98684,121.57861),(8,24.98682,121.57879),
(9,24.98762,121.57537),(10,24.98809,121.57386),(11,24.98768,121.56930),(12,24.98875,121.56809),
(13,24.98818,121.56806),(14,24.98661,121.56827)]
GATE=(24.98722,121.57705); ZOO_IN=(24.99843,121.58060); MRT=(24.99833,121.57945)

def rdp(P,eps):
    if len(P)<3: return P
    def d(p,a,b):
        (x,y),(x1,y1),(x2,y2)=p,a,b; dx,dy=x2-x1,y2-y1; L=dx*dx+dy*dy
        if L==0: return math.hypot(x-x1,y-y1)
        t=max(0,min(1,((x-x1)*dx+(y-y1)*dy)/L))
        return math.hypot(x-(x1+t*dx),y-(y1+t*dy))
    dm,idx=0,0
    for i in range(1,len(P)-1):
        dd=d(P[i],P[0],P[-1])
        if dd>dm: dm,idx=dd,i
    return rdp(P[:idx+1],eps)[:-1]+rdp(P[idx:],eps) if dm>eps else [P[0],P[-1]]
def toP(g): return [prj(n["lat"],n["lon"]) for n in g]
def dstr(P,close=False,eps=1.8):
    P=rdp(P,eps)
    return "".join(("M" if i==0 else "L")+f"{x:.0f} {y:.0f}" for i,(x,y) in enumerate(P))+("Z" if close else "")
def inbox(P,m=50): return any(-m<=x<=W+m and -m<=y<=H+m for x,y in P)

# ---- campus: stitch relation member ways into closed rings ----
unirel=[e for e in extra if e["type"]=="relation" and e.get("tags",{}).get("name")=="國立政治大學"][0]
segs=[[(n["lat"],n["lon"]) for n in m["geometry"]] for m in unirel["members"] if m.get("geometry")]
rings=[];pool=segs[:]
while pool:
    cur=pool.pop(0)
    changed=True
    while changed:
        changed=False
        for i,s in enumerate(pool):
            for a,b in ((cur[-1],s[0]),(cur[-1],s[-1]),(cur[0],s[0]),(cur[0],s[-1])):
                pass
            if cur[-1]==s[0]: cur=cur+s[1:]
            elif cur[-1]==s[-1]: cur=cur+s[::-1][1:]
            elif cur[0]==s[-1]: cur=s+cur[1:]
            elif cur[0]==s[0]: cur=s[::-1]+cur[1:]
            else: continue
            pool.pop(i); changed=True; break
    rings.append(cur)
campus=[dstr([prj(a,b) for a,b in r],r[0]==r[-1],eps=1.4) for r in rings if len(r)>=4]

zoo=[e for e in extra if e.get("tags",{}).get("tourism")=="zoo" and e["type"]=="way"][0]

# ---- roads ----
MAJOR={"新光路二段","萬壽路","指南路二段","指南路一段","木柵路三段","木柵路四段","新光路一段",
"秀明路一段","指南路三段","政大一街","政大二街","政大三街","保儀路","萬安街","忠順街二段","木新路二段"}
minor=[];major=[];chain={}
for e in roads:
    if e["type"]!="way": continue
    g=e.get("geometry") or []
    if len(g)<2: continue
    P=toP(g)
    if not inbox(P): continue
    t=e.get("tags",{}); nm=t.get("name",""); hw=t.get("highway","")
    if hw=="motorway" or "高速公路" in nm or "快速道路" in nm or "隧道" in nm: continue
    (major if nm in MAJOR else minor).append(dstr(P,eps=2.2))

route_pts=[tuple(x) for x in json.load(open("route_path.json"))]
route=[dstr([prj(a,b) for a,b in route_pts],eps=1.4)]
print("route pts",len(route_pts))

riv=[dstr(toP(e["geometry"]),eps=2.5) for e in extra if e.get("tags",{}).get("waterway")=="river" and len(e.get("geometry") or [])>=2 and inbox(toP(e["geometry"]))]
lakes=[dstr(toP(e["geometry"]),True,eps=1.2) for e in extra if e.get("tags",{}).get("natural")=="water" and len(e.get("geometry") or [])>=4 and inbox(toP(e["geometry"]),0)]

frag=[]
frag.append('<g class="m-campus">'+"".join(f'<path d="{d}"/>' for d in campus)+'</g>')
frag.append(f'<path class="m-zoo" d="{dstr(toP(zoo["geometry"]),True,eps=1.2)}"/>')
frag.append('<g class="m-water">'+"".join(f'<path class="m-lake" d="{d}"/>' for d in lakes)+"".join(f'<path d="{d}"/>' for d in riv)+'</g>')
frag.append('<g class="m-road-minor">'+"".join(f'<path d="{d}"/>' for d in minor)+'</g>')
frag.append('<g class="m-road-major">'+"".join(f'<path d="{d}"/>' for d in major)+'</g>')
frag.append('<g class="m-route">'+"".join(f'<path d="{d}"/>' for d in route)+'</g>')
open("map_frag.svg","w").write("\n".join(frag))

# ---- pins with collision-avoiding bubbles + leader lines ----
R=17.0
pts=[(n,)+prj(la,lo) for n,la,lo in STOPS]
bub={n:[x,y-26] for n,x,y in pts}
anchor={n:(x,y) for n,x,y in pts}
for _ in range(900):
    moved=False
    ks=list(bub)
    for ii in range(len(ks)):
        for jj in range(ii+1,len(ks)):
            A,B=bub[ks[ii]],bub[ks[jj]]
            dx,dy=B[0]-A[0],B[1]-A[1]; d=math.hypot(dx,dy) or .01
            if d<R*2+4:
                push=(R*2+4-d)/2
                ux,uy=dx/d,dy/d
                A[0]-=ux*push;A[1]-=uy*push;B[0]+=ux*push;B[1]+=uy*push;moved=True
    for k in ks:
        ax,ay=anchor[k];B=bub[k]
        dx,dy=B[0]-ax,B[1]-ay; d=math.hypot(dx,dy) or .01
        if d>46:
            B[0]=ax+dx/d*46;B[1]=ay+dy/d*46
        B[0]=max(R+4,min(W-R-4,B[0]));B[1]=max(R+4,min(H-R-4,B[1]))
    if not moved: break
o=['<g class="m-pins">']
for n,x,y in pts:
    bx,by=bub[n]
    o.append(f'<g class="m-pin" data-stop="{n}" tabindex="0">'
             f'<circle class="m-pin-hit" cx="{bx:.0f}" cy="{by:.0f}" r="24"/>'
             f'<line class="m-pin-leader" x1="{x:.0f}" y1="{y:.0f}" x2="{bx:.0f}" y2="{by:.0f}"/>'
             f'<circle class="m-pin-here" cx="{x:.0f}" cy="{y:.0f}" r="4"/>'
             f'<circle class="m-pin-dot" cx="{bx:.0f}" cy="{by:.0f}" r="{R:.0f}"/>'
             f'<text x="{bx:.0f}" y="{by+5.5:.0f}">{n}</text></g>')
o.append('</g>')
ANCH=[("zoo",ZOO_IN,14,38,"start"),("mrt",MRT,-34,4,"end"),("gate",GATE,-6,46,"middle")]
o.append('<g class="m-anchors">')
for k,(la,lo),dx,dy,al in ANCH:
    x,y=prj(la,lo)
    o.append(f'<circle class="m-anchor-dot m-{k}" cx="{x:.0f}" cy="{y:.0f}" r="11"/>')
o.append('</g>')
for k,(la,lo),dx,dy,al in ANCH:
    x,y=prj(la,lo)
    o.append(f'<text class="m-lbl" x="{x+dx:.0f}" y="{y+dy:.0f}" text-anchor="{al}" data-i18n="map.lbl.{k}"></text>')
x,y=prj(24.98470,121.57850); o.append(f'<text class="m-lbl m-lbl-soft" x="{x:.0f}" y="{y:.0f}" text-anchor="middle" data-i18n="map.lbl.campus"></text>')
x,y=prj(24.98520,121.59250); o.append(f'<text class="m-lbl m-lbl-soft" x="{x:.0f}" y="{y:.0f}" text-anchor="end" data-i18n="map.lbl.maokong"></text>')
x,y=prj(24.99180,121.57720); o.append(f'<text class="m-lbl m-lbl-route" x="{x:.0f}" y="{y:.0f}" data-i18n="map.lbl.route" text-anchor="end"></text>')
open("pins_frag.svg","w").write("\n".join(o))
print("viewBox 0 0 1200",H,"map bytes",len("\n".join(frag)),"pin bytes",len("\n".join(o)))
