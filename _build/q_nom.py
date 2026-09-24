import json,urllib.request,urllib.parse,time
names="十五分 十一命 頂店 渡船巷 渡船頭 打鐵寮 外埔 炮子林 番仔公館 灰窯坑 軍功坑 抱子腳 貓空 木柵".split()
VB="121.5450,25.0150,121.6150,24.9550"
out={}
for nm in names:
    q=urllib.parse.urlencode({"q":nm,"format":"json","limit":5,"viewbox":VB,"bounded":1})
    r=urllib.request.Request("https://nominatim.openstreetmap.org/search?"+q,
        headers={"User-Agent":"muzha-food-link/1.0 (derekyt.chen@gmail.com)"})
    try:
        d=json.load(urllib.request.urlopen(r,timeout=25))
    except Exception as e:
        print(nm,"ERR",e); time.sleep(1.2); continue
    if not d: print(f"{nm:6s} none"); time.sleep(1.2); continue
    b=d[0]
    out[nm]=(float(b["lat"]),float(b["lon"]))
    print(f'{nm:6s} {b["lat"]:>11s} {b["lon"]:>12s}  {b.get("type","")}/{b.get("class","")}  {b["display_name"][:46]}')
    time.sleep(1.2)
json.dump(out,open("anchors.json","w"),ensure_ascii=False,indent=1)
print("saved",len(out))
