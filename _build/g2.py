import qrcode, json
ids = ["o-2Ih1w_RCM","-9OHJkzVGkE","1DNJ2SSmtuc","hgGGnv0VNl8","rud9SDJnPXw","Qwmw0jWqtA0","j7A88Eca3iE","QckhfASPPhA"]
out={}
for i in ids:
    q=qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,border=2)
    q.add_data("https://youtu.be/"+i); q.make(fit=True)
    m=q.get_matrix(); n=len(m)
    d=[]
    for y,row in enumerate(m):
        x=0
        while x<n:
            if row[x]:
                s=x
                while x<n and row[x]: x+=1
                d.append(f"M{s} {y}h{x-s}v1h-{x-s}z")
            else: x+=1
    out[i]={"n":n,"d":"".join(d)}
json.dump(out,open("qr.json","w"))
print({k:(v["n"],len(v["d"])) for k,v in out.items()})
