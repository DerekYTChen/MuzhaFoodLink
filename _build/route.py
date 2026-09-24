import json,math,heapq
roads=json.load(open("roads.json"))["elements"]
def m(a,b): return math.hypot((a[0]-b[0])*110574,(a[1]-b[1])*100900)
G={}
def key(p): return (round(p[0],7),round(p[1],7))
for e in roads:
    if e["type"]!="way": continue
    t=e.get("tags",{}); nm=t.get("name","")
    if t.get("highway")=="motorway" or "高速公路" in nm or "快速道路" in nm: continue
    g=[(n["lat"],n["lon"]) for n in (e.get("geometry") or [])]
    for a,b in zip(g,g[1:]):
        ka,kb=key(a),key(b); w=m(a,b)
        G.setdefault(ka,{})[kb]=min(G.setdefault(ka,{}).get(kb,9e9),w)
        G.setdefault(kb,{})[ka]=min(G.setdefault(kb,{}).get(ka,9e9),w)
print("nodes",len(G))
def nearest(p): return min(G,key=lambda k:m(k,p))
def sp(s,t):
    s,t=nearest(s),nearest(t)
    dist={s:0};prev={};pq=[(0,s)];seen=set()
    while pq:
        d,u=heapq.heappop(pq)
        if u in seen: continue
        seen.add(u)
        if u==t: break
        for v,w in G[u].items():
            nd=d+w
            if nd<dist.get(v,9e9): dist[v]=nd;prev[v]=u;heapq.heappush(pq,(nd,v))
    if t not in dist: return None,None
    path=[t]
    while path[-1]!=s: path.append(prev[path[-1]])
    return path[::-1],dist[t]
GATE=(24.98722,121.57705); ZOO=(24.99843,121.58060)
p,d=sp(GATE,ZOO)
print("route nodes",len(p),"length %.0f m"%d)
json.dump(p,open("route_path.json","w"))
