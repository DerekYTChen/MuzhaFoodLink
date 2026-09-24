import json,math
roads=json.load(open("roads.json"))["elements"]
KX=math.cos(math.radians(24.99))
def dist(a,b): return math.hypot((a[0]-b[0])*110574,(a[1]-b[1])*100900)
ch={}
for e in roads:
    if e["type"]!="way": continue
    nm=e.get("tags",{}).get("name","")
    if nm in ("萬壽路","新光路二段","指南路二段"):
        g=e.get("geometry") or []
        ch.setdefault(nm,[]).append([(n["lat"],n["lon"]) for n in g])
for k,v in ch.items():
    print(k,len(v),[ (len(s),round(dist(s[0],s[-1]))) for s in v])
def stitch(segs):
    out=[];pool=segs[:]
    while pool:
        cur=pool.pop(0); c=True
        while c:
            c=False
            for i,s in enumerate(pool):
                if cur[-1]==s[0]: cur=cur+s[1:]
                elif cur[-1]==s[-1]: cur=cur+s[::-1][1:]
                elif cur[0]==s[-1]: cur=s+cur[1:]
                elif cur[0]==s[0]: cur=s[::-1]+cur[1:]
                else: continue
                pool.pop(i); c=True; break
        out.append(cur)
    return out
L=stitch(ch.get("指南路二段",[])+ch.get("萬壽路",[])+ch.get("新光路二段",[]))
GATE=(24.98722,121.57705); ZOO=(24.99843,121.58060)
for l in L:
    dg=min(dist(p,GATE) for p in l); dz=min(dist(p,ZOO) for p in l)
    print(len(l),"gate %.0f zoo %.0f"%(dg,dz), l[0], l[-1])
