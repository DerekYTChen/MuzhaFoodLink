import json, math
roads=json.load(open("roads.json"))["elements"]
extra=json.load(open("extra.json"))["elements"]

POIS=[("zoo",24.9953546,121.5861491),("uni",24.9872,121.5766),("mrt",24.99833,121.57945)]
REST=[("panda",24.99807,121.58114),("shuman",24.98781,121.57594),("yule",24.98821,121.57640),
("dianwei",24.98735,121.57761),("jinsushi",24.98703,121.57854),("oden",24.98684,121.57861),
("luwei",24.98682,121.57879),("bbq",24.98749,121.57696),("hotpot",24.98736,121.57757),
("arirang",24.98809,121.57386),("zheng",24.98762,121.57537),("anjiu",24.97961,121.57135),
("shuijian",24.98768,121.56930),("kyobashi",24.98875,121.56809),("veg",24.98818,121.56806),
("liangmian",24.98661,121.56827)]

zoo=[e for e in extra if e.get("tags",{}).get("tourism")=="zoo" and e["type"]=="way"][0]
unirel=[e for e in extra if e["type"]=="relation" and e.get("tags",{}).get("name")=="國立政治大學"][0]
uni_ways=[m["geometry"] for m in unirel["members"] if m.get("geometry")]

minlat,maxlat=24.9775,25.0016
minlon,maxlon=121.5648,121.5940
k=math.cos(math.radians(24.99))
W=1200.0
H=W*((maxlat-minlat)/((maxlon-minlon)*k))
def prj(lat,lon):
    return ((lon-minlon)/(maxlon-minlon)*W, (maxlat-lat)/(maxlat-minlat)*H)

def rdp(P,eps):
    if len(P)<3: return P
    def d(p,a,b):
        (x,y),(x1,y1),(x2,y2)=p,a,b
        dx,dy=x2-x1,y2-y1
        L=dx*dx+dy*dy
        if L==0: return math.hypot(x-x1,y-y1)
        t=max(0,min(1,((x-x1)*dx+(y-y1)*dy)/L))
        return math.hypot(x-(x1+t*dx),y-(y1+t*dy))
    dm,idx=0,0
    for i in range(1,len(P)-1):
        dd=d(P[i],P[0],P[-1])
        if dd>dm: dm,idx=dd,i
    if dm>eps:
        return rdp(P[:idx+1],eps)[:-1]+rdp(P[idx:],eps)
    return [P[0],P[-1]]

def toP(geom): return [prj(g["lat"],g["lon"]) for g in geom]
def dstr(P,close=False,eps=1.6):
    P=rdp(P,eps)
    s="".join(("M" if i==0 else "L")+f"{x:.0f} {y:.0f}" for i,(x,y) in enumerate(P))
    return s+("Z" if close else "")
def inbox(P,m=40):
    return any(-m<=x<=W+m and -m<=y<=H+m for x,y in P)

MAJOR={"新光路二段","萬壽路","指南路二段","指南路一段","木柵路三段","木柵路四段","新光路一段","秀明路一段","指南路三段","政大一街","政大二街","政大三街","保儀路","萬安街","忠順街二段"}
minor=[];major=[];route={}
for e in roads:
    if e["type"]!="way": continue
    g=e.get("geometry") or []
    if len(g)<2: continue
    P=toP(g)
    if not inbox(P): continue
    t=e.get("tags",{}); nm=t.get("name",""); hw=t.get("highway","")
    if hw=="motorway" or "高速公路" in nm or "快速道路" in nm or "隧道" in nm: continue
    if nm in ("萬壽路","新光路二段"): route.setdefault(nm,[]).append(P)
    (major if nm in MAJOR else minor).append(dstr(P,eps=2.2))

riv=[dstr(toP(e["geometry"]),eps=2.5) for e in extra if e.get("tags",{}).get("waterway")=="river" and len(e.get("geometry") or [])>=2 and inbox(toP(e["geometry"]))]
lakes=[dstr(toP(e["geometry"]),True,eps=1.2) for e in extra if e.get("tags",{}).get("natural")=="water" and len(e.get("geometry") or [])>=4 and inbox(toP(e["geometry"]),0)]

frag=[]
frag.append('<g class="m-water">'+"".join(f'<path class="m-lake" d="{d}"/>' for d in lakes)+"".join(f'<path d="{d}"/>' for d in riv)+'</g>')
frag.append('<g class="m-campus">'+"".join(f'<path d="{dstr(toP(g),eps=1.5)}"/>' for g in uni_ways if len(g)>=2)+'</g>')
frag.append(f'<path class="m-zoo" d="{dstr(toP(zoo["geometry"]),True,eps=1.2)}"/>')
frag.append('<g class="m-road-minor">'+"".join(f'<path d="{d}"/>' for d in minor)+'</g>')
frag.append('<g class="m-road-major">'+"".join(f'<path d="{d}"/>' for d in major)+'</g>')
rt=[]
for nm in ("萬壽路","新光路二段"):
    for P in route.get(nm,[]): rt.append(dstr(P,eps=2.0))
frag.append('<g class="m-route">'+"".join(f'<path d="{d}"/>' for d in rt)+'</g>')
open("map_frag.svg","w").write("\n".join(frag))
pins={k:(round(prj(a,b)[0]),round(prj(a,b)[1])) for k,a,b in POIS+REST}
json.dump(pins,open("pins.json","w"))
print("viewBox 0 0 1200 %.0f"%H,"bytes",len("\n".join(frag)))
print(json.dumps(pins))
