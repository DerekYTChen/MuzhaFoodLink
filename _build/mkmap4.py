import json, math, heapq

roads=json.load(open("roads2.json"))["elements"]
extra=json.load(open("extra2.json"))["elements"]
aerial=json.load(open("aerial.json"))["elements"]

MINLAT,MAXLAT=24.9655,25.0020
MINLON,MAXLON=121.5640,121.5950
KX=math.cos(math.radians(24.985)); W=1200.0
H=round(W*((MAXLAT-MINLAT)/((MAXLON-MINLON)*KX)))
def prj(lat,lon): return ((lon-MINLON)/(MAXLON-MINLON)*W,(MAXLAT-lat)/(MAXLAT-MINLAT)*H)

# n, zh name, cluster, lat, lon
STOPS=[
 (1,"大貓熊咖啡輕食館","zoo",24.99807,121.58114),
 (2,"魚樂𩵚魠魚羹","strip",24.98821,121.57640),
 (3,"舒曼六號餐館","strip",24.98781,121.57594),
 (4,"政大烤場","strip",24.98749,121.57696),
 (5,"滇味廚房","strip",24.98735,121.57761),
 (6,"金鮨日式料理","strip",24.98703,121.57854),
 (7,"政大關東煮・秀食屋","strip",24.98684,121.57861),
 (8,"魯味齋","strip",24.98682,121.57879),
 (9,"政政小廚","strip",24.98762,121.57537),
 (10,"阿里郎韓國小吃","strip",24.98809,121.57386),
 (11,"麵匡匡拉麵食堂","muzha",24.9869994,121.5685427),
 (12,"木柵水煎包","muzha",24.98768,121.56930),
 (13,"京橋日本料理","muzha",24.98875,121.56809),
 (14,"菜根香素食","muzha",24.98818,121.56806),
 (15,"保儀涼麵","muzha",24.98661,121.56827),
 (16,"安九食堂","campus",24.97961,121.57135),
 (17,"貓空龍門客棧","maokong",24.967211,121.586874),
 (18,"大茶壺茶餐廳","maokong",24.968627,121.591778),
 (19,"光羽塩 Lytea","maokong",24.968782,121.585718),
 (20,"四哥的店","maokong",24.967097,121.590759),
]
GATE=(24.98722,121.57705); ZOO_IN=(24.99843,121.58060); MRT=(24.99833,121.57945)


def rdp(P,eps):
    if len(P)<3: return P
    def d(p,a,b):
        (x,y),(x1,y1),(x2,y2)=p,a,b; dx,dy=x2-x1,y2-y1; L=dx*dx+dy*dy
        if L==0: return math.hypot(x-x1,y-y1)
        t=max(0,min(1,((x-x1)*dx+(y-y1)*dy)/L)); return math.hypot(x-(x1+t*dx),y-(y1+t*dy))
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

# ---------- walking route (Dijkstra on the real road graph) ----------
def mdist(a,b): return math.hypot((a[0]-b[0])*110574,(a[1]-b[1])*100900)
G={}
def key(p): return (round(p[0],7),round(p[1],7))
for e in roads:
    if e["type"]!="way": continue
    t=e.get("tags",{}); nm=t.get("name","")
    if t.get("highway")=="motorway" or "高速公路" in nm or "快速道路" in nm: continue
    g=[(n["lat"],n["lon"]) for n in (e.get("geometry") or [])]
    for a,b in zip(g,g[1:]):
        ka,kb=key(a),key(b); w=mdist(a,b)
        G.setdefault(ka,{})[kb]=min(G.setdefault(ka,{}).get(kb,9e9),w)
        G.setdefault(kb,{})[ka]=min(G.setdefault(kb,{}).get(ka,9e9),w)
def sp(src,tgt):
    s=min(G,key=lambda k:mdist(k,src))
    dist={s:0};prev={};pq=[(0,s)];seen=set()
    while pq:
        d,u=heapq.heappop(pq)
        if u in seen: continue
        seen.add(u)
        for v,w in G[u].items():
            nd=d+w
            if nd<dist.get(v,9e9): dist[v]=nd;prev[v]=u;heapq.heappush(pq,(nd,v))
    t=min(seen,key=lambda k:mdist(k,tgt))
    snap=mdist(t,tgt)
    p=[t]
    while p[-1]!=s: p.append(prev[p[-1]])
    print("  reachable nodes %d, target snap %.0f m"%(len(seen),snap))
    return p[::-1],dist[t]
rp,rlen=sp(GATE,ZOO_IN)
print("walk route %.0f m (%d nodes)"%(rlen,len(rp)))
route=dstr([prj(a,b) for a,b in rp],eps=1.4)

# ---------- layers ----------
zoo=[e for e in extra if e.get("tags",{}).get("tourism")=="zoo" and e["type"]=="way"][0]
unirel=[e for e in extra if e["type"]=="relation" and e.get("tags",{}).get("name")=="國立政治大學"][0]
def stitch(segs):
    out=[];pool=[s[:] for s in segs]
    while pool:
        cur=pool.pop(0); ch=True
        while ch:
            ch=False
            for i,s in enumerate(pool):
                if cur[-1]==s[0]: cur=cur+s[1:]
                elif cur[-1]==s[-1]: cur=cur+s[::-1][1:]
                elif cur[0]==s[-1]: cur=s+cur[1:]
                elif cur[0]==s[0]: cur=s[::-1]+cur[1:]
                else: continue
                pool.pop(i); ch=True; break
        out.append(cur)
    return out
campus=[dstr([prj(a,b) for a,b in r],r[0]==r[-1],eps=1.4)
        for r in stitch([[(n["lat"],n["lon"]) for n in m["geometry"]] for m in unirel["members"] if m.get("geometry")])
        if len(r)>=4]

MAJOR={"新光路二段","萬壽路","指南路二段","指南路一段","指南路三段","木柵路三段","木柵路四段",
"木柵路五段","新光路一段","秀明路一段","政大一街","政大二街","政大三街","保儀路","萬安街",
"忠順街二段","木新路二段","老泉街","萬壽橋"}
minor=[];major=[]
for e in roads:
    if e["type"]!="way": continue
    g=e.get("geometry") or []
    if len(g)<2: continue
    P=toP(g)
    if not inbox(P): continue
    t=e.get("tags",{}); nm=t.get("name","")
    if t.get("highway")=="motorway" or "高速公路" in nm or "快速道路" in nm or "隧道" in nm: continue
    (major if nm in MAJOR else minor).append(dstr(P,eps=2.2))

riv=[dstr(toP(e["geometry"]),eps=2.5) for e in extra
     if e.get("tags",{}).get("waterway")=="river" and len(e.get("geometry") or [])>=2 and inbox(toP(e["geometry"]))]
lakes=[dstr(toP(e["geometry"]),True,eps=1.2) for e in extra
       if e.get("tags",{}).get("natural")=="water" and len(e.get("geometry") or [])>=4 and inbox(toP(e["geometry"]),0)]

# ---------- decorative flora (Pikmin-style ornament, NOT data) ----------
# Positions are procedural and deterministic (seed 7). They do not represent
# anything observed on the ground. Purely to warm up the empty green space.
import random as _r
_r.seed(7)
_pin=[prj(la,lo) for n,zh,cl,la,lo in STOPS]
_rt=[prj(a,b) for a,b in rp]
_wt=[]
for _e in extra:
    _t=_e.get("tags",{})
    if _t.get("waterway")=="river" or _t.get("natural")=="water":
        for _n in (_e.get("geometry") or []): _wt.append(prj(_n["lat"],_n["lon"]))
def _far(p,pts,r):
    r2=r*r
    return all((p[0]-q[0])**2+(p[1]-q[1])**2>r2 for q in pts)
FLC=["#dd5546","#e3a22c","#fbf6e8","#cf8fb4","#9dc4d8","#e8cf5a"]
def _flower(x,y,c,sc):
    pet="".join('<circle cx="%.2f" cy="%.2f" r="3.0"/>'%(math.cos(math.radians(-90+k*72))*3.5,
        -12.5+math.sin(math.radians(-90+k*72))*3.5) for k in range(5))
    return ('<g transform="translate(%.0f,%.0f) scale(%.2f)">'
            '<path class="m-stem" d="M0 0 0 -11"/><g fill="%s">%s</g>'
            '<circle cx="0" cy="-12.5" r="1.5" fill="#f6e4a6"/></g>')%(x,y,sc,c,pet)
def _shroom(x,y,sc):
    dots="".join('<circle cx="%.1f" cy="%.1f" r="%.1f"/>'%d for d in
                 ((-4.2,-9.4,1.5),(0.6,-11.2,1.8),(4.6,-9.0,1.3)))
    return ('<g transform="translate(%.0f,%.0f) scale(%.2f)">'
            '<path class="m-cap" d="M-3.2 0 q-0.4 -6.4 3.2 -6.4 q3.6 0 3.2 6.4 z" fill="#fbf6e8"/>'
            '<path class="m-cap" d="M-9.4 -6.2 q0 -7.6 9.4 -7.6 q9.4 0 9.4 7.6 z" fill="#dd5546"/>'
            '<g fill="#fbf6e8" opacity=".92">%s</g></g>')%(x,y,sc,dots)
_cand=[]
GS=98
gy=56
while gy<H-40:
    gx=44
    while gx<W-40:
        p=(gx+_r.uniform(-30,30),gy+_r.uniform(-26,26))
        if _far(p,_pin,52) and _far(p,_rt,15) and _far(p,_wt,13): _cand.append(p)
        gx+=GS
    gy+=GS
_r.shuffle(_cand)
_fs=_cand
flora=[_flower(x,y,_r.choice(FLC),_r.uniform(.62,1.0)) for x,y in _fs]

cable=[dstr(toP(e["geometry"]),eps=1.2) for e in aerial
       if e["type"]=="way" and e.get("tags",{}).get("aerialway")=="gondola"]
STN=[(e["tags"]["name"],e["tags"].get("name:en",""),e["lat"],e["lon"]) for e in aerial
     if e["type"]=="node" and e.get("tags",{}).get("aerialway")=="station"]


# ---------- Pikmin Bloom activity layer ----------
# Observed 2026-09-24, 23:07-23:35, from 9 Pikmin Bloom screenshots (see pikmin/).
# Anchor lat/lon are the real OSM nodes whose names Pikmin renders as labels
# (hamlet nodes via Nominatim; 動物園 / 轉角一 are the gondola station nodes).
# LEVEL is a bucket, not a count: 3 = many clusters, 2 = several, 1 = one or two,
# 0 = none seen. Buckets because sprite counting off a JPEG is +/-2.
PIKMIN=[
 ("動物園","Taipei Zoo",24.9959573,121.5762884,3),
 ("外埔","Waipu / NCCU",24.9850537,121.5788420,3),
 ("頂店","Dingdian",24.9890160,121.5697772,2),
 ("十一命","Shiyiming",24.9927887,121.5742714,2),
 ("渡船巷","Duchuanxiang",24.9874390,121.5714840,2),
 ("貓纜轉角一","Gondola Corner 1",24.9919382,121.5829967,2),
 ("抱子腳","Baozijiao",24.9968119,121.5712556,1),
 ("打鐵寮","Datieliao",24.9847910,121.5710941,1),
 ("渡船頭","Duchuantou",24.9830704,121.5721469,1),
 ("番仔公館","Fanzaigongguan",24.9831876,121.5800011,1),
 ("炮子林","Paozilin",24.9800509,121.5794300,0),
]
RAD={3:46,2:32,1:21,0:13}
pk=[];pkout=[]
for nm,en,la,lo,lv in PIKMIN:
    if not (MINLAT<=la<=MAXLAT and MINLON<=lo<=MAXLON):
        pkout.append(nm); continue
    x,y=prj(la,lo); r=RAD[lv]
    g=[f'<title>{nm} / {en}</title>']
    if lv==0:
        g.append(f'<circle class="m-pk-none" cx="{x:.0f}" cy="{y:.0f}" r="{r}"/>')
    else:
        g.append(f'<circle class="m-pk-halo" cx="{x:.0f}" cy="{y:.0f}" r="{r}"/>')
        g.append(f'<circle class="m-pk-ring" cx="{x:.0f}" cy="{y:.0f}" r="{r}"/>')
        g.append(('<g transform="translate(%.0f,%.0f) scale(%.2f)">'
          '<path class="m-pk-stem" d="M-3.2 0 q-0.4 -6.4 3.2 -6.4 q3.6 0 3.2 6.4 z"/>'
          '<path class="m-pk-cap" d="M-9.4 -6.2 q0 -7.6 9.4 -7.6 q9.4 0 9.4 7.6 z"/>'
          '<g class="m-pk-dot"><circle cx="-4.2" cy="-9.4" r="1.5"/>'
          '<circle cx="0.6" cy="-11.2" r="1.8"/><circle cx="4.6" cy="-9" r="1.3"/></g></g>')
          %(x,y+7,0.9+0.28*lv))
    pk.append(f'<g class="m-pk m-pk-l{lv}">'+"".join(g)+'</g>')
print("pikmin points",len(pk),"| outside map bounds:",",".join(pkout) or "none")

frag=[]
frag.append('<g class="m-campus">'+"".join(f'<path d="{d}"/>' for d in campus)+'</g>')
frag.append(f'<path class="m-zoo" d="{dstr(toP(zoo["geometry"]),True,eps=1.2)}"/>')
frag.append('<g class="m-water">'+"".join(f'<path class="m-lake" d="{d}"/>' for d in lakes)+"".join(f'<path d="{d}"/>' for d in riv)+'</g>')
frag.append('<g class="m-flora">'+"".join(flora)+'</g>')
frag.append('<g class="m-road-minor">'+"".join(f'<path d="{d}"/>' for d in minor)+'</g>')
frag.append('<g class="m-road-major">'+"".join(f'<path d="{d}"/>' for d in major)+'</g>')
frag.append('<g class="m-cable">'+"".join(f'<path d="{d}"/>' for d in cable)+'</g>')
frag.append(f'<g class="m-route"><path d="{route}"/></g>')
sd=[]
for nm,en,la,lo in STN:
    x,y=prj(la,lo); sd.append(f'<circle class="m-stn" cx="{x:.0f}" cy="{y:.0f}" r="9"/>')
frag.append('<g class="m-pikmin">'+"".join(pk)+'</g>')
frag.append('<g class="m-stations">'+"".join(sd)+'</g>')
open("map_frag.svg","w").write("\n".join(frag))

# ---------- pins ----------
R=16.0
pts=[(n,)+prj(la,lo) for n,zh,cl,la,lo in STOPS]
bub={n:[x,y-25] for n,x,y in pts}; anchor={n:(x,y) for n,x,y in pts}
for _ in range(1200):
    moved=False; ks=list(bub)
    for i in range(len(ks)):
        for j in range(i+1,len(ks)):
            A,B=bub[ks[i]],bub[ks[j]]
            dx,dy=B[0]-A[0],B[1]-A[1]; d=math.hypot(dx,dy) or .01
            if d<R*2+4:
                p=(R*2+4-d)/2; ux,uy=dx/d,dy/d
                A[0]-=ux*p;A[1]-=uy*p;B[0]+=ux*p;B[1]+=uy*p;moved=True
    for k in ks:
        ax,ay=anchor[k];B=bub[k]
        dx,dy=B[0]-ax,B[1]-ay; d=math.hypot(dx,dy) or .01
        if d>44: B[0]=ax+dx/d*44;B[1]=ay+dy/d*44
        B[0]=max(R+4,min(W-R-4,B[0])); B[1]=max(R+4,min(H-R-4,B[1]))
    if not moved: break
o=[]
o.append('<g class="m-pins">')
for n,x,y in pts:
    bx,by=bub[n]
    o.append(f'<g class="m-pin" data-stop="{n}">'
      f'<circle class="m-pin-hit" cx="{bx:.0f}" cy="{by:.0f}" r="23"/>'
      f'<line class="m-pin-leader" x1="{x:.0f}" y1="{y:.0f}" x2="{bx:.0f}" y2="{by:.0f}"/>'
      f'<circle class="m-pin-here" cx="{x:.0f}" cy="{y:.0f}" r="4"/>'
      f'<circle class="m-pin-dot" cx="{bx:.0f}" cy="{by:.0f}" r="{R:.0f}"/>'
      f'<text x="{bx:.0f}" y="{by+5:.0f}">{n}</text></g>')
o.append('</g>')
ANCH=[("zoo",ZOO_IN,14,36,"start"),("mrt",MRT,-32,4,"end"),("gate",GATE,-22,58,"end")]
o.append('<g class="m-anchors">'+"".join(
  f'<circle class="m-anchor-dot m-{k}" cx="{prj(*p)[0]:.0f}" cy="{prj(*p)[1]:.0f}" r="11"/>' for k,p,_,_,_ in ANCH)+'</g>')
for k,p,dx,dy,al in ANCH:
    x,y=prj(*p); o.append(f'<text class="m-lbl" x="{x+dx:.0f}" y="{y+dy:.0f}" text-anchor="{al}" data-i18n="map.lbl.{k}"></text>')
SLBL={"貓空":("maokongStn",0,-46,"middle"),"指南宮":("zhinan",-16,6,"end"),
      "動物園南":("zooSouth",16,6,"start"),"動物園":("gondolaZoo",-16,6,"end")}
for nm,en,la,lo in STN:
    if nm in SLBL:
        k,dx,dy,al=SLBL[nm]; x,y=prj(la,lo)
        o.append(f'<text class="m-lbl m-lbl-cable" x="{x+dx:.0f}" y="{y+dy:.0f}" text-anchor="{al}" data-i18n="map.lbl.{k}"></text>')
x,y=prj(24.98300,121.57950); o.append(f'<text class="m-lbl m-lbl-soft" x="{x:.0f}" y="{y:.0f}" text-anchor="middle" data-i18n="map.lbl.campus"></text>')
x,y=prj(24.99180,121.57720); o.append(f'<text class="m-lbl m-lbl-route" x="{x:.0f}" y="{y:.0f}" text-anchor="end" data-i18n="map.lbl.route"></text>')
open("pins_frag.svg","w").write("\n".join(o))

# ---------- stop list HTML ----------
CL=[("zoo","map.cl.zoo"),("strip","map.cl.strip"),("muzha","map.cl.muzha"),
    ("campus","map.cl.campus"),("maokong","map.cl.maokong")]
h=[]
for cl,ck in CL:
    rows=[s for s in STOPS if s[2]==cl]
    h.append(f'          <p class="map-cluster" data-i18n="{ck}"></p>')
    h.append(f'          <ol class="stop-list" start="{rows[0][0]}">')
    for n,zh,_,_,_ in rows:
        h.append(f'            <li data-stop="{n}"><b>{zh}</b><span data-i18n="st.{n}"></span></li>')
    h.append('          </ol>')
open("stops_frag.html","w").write("\n".join(h))
print("viewBox 0 0 1200",H,"| map",len("\n".join(frag)),"pins",len("\n".join(o)),"stops",len(STOPS))
