from PIL import Image
import numpy as np, glob, json
from scipy import ndimage
BG=np.array([62,136,111])
out={}
for f in sorted(glob.glob('*_b.jpeg')):
    a=np.asarray(Image.open(f).convert('RGB')).astype(int)
    m=np.abs(a-BG).max(axis=2)<40
    m=ndimage.binary_closing(m,np.ones((3,3)))
    lab,n=ndimage.label(m)
    res=[]
    for i,sl in enumerate(ndimage.find_objects(lab),1):
        h=sl[0].stop-sl[0].start; w=sl[1].stop-sl[1].start
        ar=(lab[sl]==i).sum()
        if not(24<=h<=64 and 38<=w<=260): continue
        if ar<0.42*h*w: continue
        cy=(sl[0].start+sl[0].stop)/2
        if cy<118 or cy>1462: continue
        # split merged badges: each badge ~54px wide
        k=max(1,round(w/56))
        for j in range(k):
            cx=sl[1].start+w*(j+0.5)/k
            res.append([round(cx,1),round(cy,1),round(w/k),h,k])
    res.sort(key=lambda r:(r[1],r[0]))
    out[f]=res
    print(f,'badges',len(res))
    for r in res: print('   ',r)
json.dump(out,open('../badges.json','w'),indent=1)
