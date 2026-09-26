# Source: 臺北市立動物園107年至115入園人數統計表 (Taipei Zoo monthly admissions)
# https://www.zoo.gov.taipei/  PDF: www-ws.gov.taipei/001/Upload/432/relfile/18423/9337/
# ROC year 113 = 2024, 114 = 2025. COVID years (2020-2022) excluded as distorted.
Y2024 = [216743,321728,284372,247970,192804,118424,168803,211940,139665,231897,233421,257206]
Y2025 = [304084,217591,224230,239623,206991,98306,186623,220803,134195,160117,256202,227140]
MEAN = [(a+b)/2 for a,b in zip(Y2024,Y2025)]
AVG  = sum(MEAN)/12
if __name__ == "__main__":
    for i,(m,a,b) in enumerate(zip(MEAN,Y2024,Y2025),1):
        print(f"{i:>2}月 2024={a:>7,} 2025={b:>7,} mean={m:>9,.0f} {m/AVG*100-100:+6.1f}%")
    print(f"monthly average {AVG:,.0f}")
    print(f"Jan+Feb mean {(MEAN[0]+MEAN[1])/2:,.0f}  = {((MEAN[0]+MEAN[1])/2)/AVG*100-100:+.1f}%")
    print(f"Jun+Sep mean {(MEAN[5]+MEAN[8])/2:,.0f}  = {((MEAN[5]+MEAN[8])/2)/AVG*100-100:+.1f}%")
    print(f"2024 total {sum(Y2024):,}  2025 total {sum(Y2025):,}")
