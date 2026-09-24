import json,urllib.request,urllib.parse,time
Q='[out:json][timeout:90];node["place"](24.9550,121.5450,25.0150,121.6150);out tags;'
hosts=["https://overpass.kumi.systems/api/interpreter",
       "https://overpass-api.de/api/interpreter",
       "https://overpass.osm.jp/api/interpreter"]
for att in range(2):
  for host in hosts:
    try:
        r=urllib.request.Request(host,data=urllib.parse.urlencode({"data":Q}).encode(),
            headers={"User-Agent":"muzha-food-link/1.0 (derekyt.chen@gmail.com)"})
        d=json.load(urllib.request.urlopen(r,timeout=120))
        json.dump(d,open("places.json","w"),ensure_ascii=False)
        print(host,"OK",len(d["elements"]))
        raise SystemExit
    except SystemExit: raise
    except Exception as ex: print(host,"fail",type(ex).__name__,ex); time.sleep(2)
print("ALL FAILED")
