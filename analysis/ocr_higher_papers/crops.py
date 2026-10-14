import fitz, json
from locate import FILES, D
# (paper, label, type, marks, page, y_start, y_end or None)  y_end None = footer/next question
loc=json.load(open('loc.json'))
def foot(p):
    ys=[w[1] for w in p.get_text("words") if w[4].startswith("©") or w[4]=="Turn"]
    return min(ys)-6 if ys else p.rect.height-50
def nextq(k):
    d=fitz.open(D+FILES[k]); L=loc[k]; p=d[L["page"]]
    return L["y1"]-6 if L["y1"] else foot(p)
ITEMS=[]
def add(k,lab,typ,mk,ys,ye=None):
    L=loc[k]; ITEMS.append(dict(k=k,lab=lab,typ=typ,mk=mk,page=L["page"],y0=ys-4,y1=(ye-6) if ye else nextq(k)))
add("2017J-P5","13(a)","F2R",1,348,465); add("2017J-P5","13(b)","R2F",3,465)
add("2018J-P5","13(a)","F2R",2,239,460); add("2018J-P5","13(b)","R2F",2,460)
add("2018N-P6","14(a)","R2F",3,420,602); add("2018N-P6","14(b)","KNOWN",2,602)
add("2019J-P5","10(a)","F2R",2,69,199); add("2019J-P5","10(b)","R2F",4,199)
add("2020N-P6","18","R2F",3,400)
add("2021N-P5","13(a)","F2R",2,70,421); add("2021N-P5","13(b)","R2F",3,421)
add("2022J-P5","16","ARITH",5,65)
add("2022N-P5","11","R2F",3,65)
add("2023J-P5","16(b)","ARITH",4,257)
add("2024J-P5","17","ARITH",5,62)
add("2024J-P6","17(a)","R2F",3,70,317); add("2024J-P6","17(b)","KNOWN",2,317)
add("2025J-P5","18","ARITH",5,62)
if __name__=="__main__":
    for i,it in enumerate(ITEMS):
        d=fitz.open(D+FILES[it["k"]]); p=d[it["page"]]
        p.get_pixmap(dpi=60,clip=fitz.Rect(20,it["y0"],575,it["y1"])).save(f"crop_{i:02d}.png")
        print(i,it["k"],it["lab"],round(it["y0"]),round(it["y1"]))
