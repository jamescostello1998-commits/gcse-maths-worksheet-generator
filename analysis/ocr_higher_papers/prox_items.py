import fitz
from prox_locate import D, FILES
def foot(k,pg):
    p=fitz.open(D+FILES[k])[pg]
    ys=[w[1] for w in p.get_text("words") if w[4].startswith("©") or w[4]=="Turn"]
    return (min(ys)-6) if ys else p.rect.height-50
# key, label, section, marks, [(page, y_start, y_end|None)]
RAW=[
("2017J-P4","15(d)","D",3,[(13,62,329),(14,206,440)]),
("2022N-P4","13","D",3,[(12,66,404)]),
("2025J-P5","13","D",3,[(11,62,369)]),
("2017J-P6","12","I",4,[(13,426,None)]),
("2018J-P6","6","I",3,[(4,465,None)]),
("2018N-P4","14","I",3,[(12,357,None)]),
("2019J-P4","16(a)(b)","I",5,[(13,62,None)]),
("2020N-P4","16","I",3,[(15,62,436)]),
("2021N-P6","14(a)(b)","I",6,[(13,62,None)]),
("2022J-P5","11","I",3,[(13,62,None)]),
("2022N-P6","14(b)","I",3,[(12,452,None)]),
("2023J-P4","15","I",3,[(13,530,None)]),
("2024J-P6","15","I",3,[(15,68,445)]),
("2025J-P4","15","I",3,[(12,270,None)]),
("2018J-P4","11","H",4,[(11,62,322)]),
("2023J-P5","11","H",4,[(10,62,335)]),
("2024J-P5","8(a)(b)","H",2,[(6,62,283)]),
("2020N-P6","9","H",4,[(9,62,None)]),
("2024J-P4","10","H",3,[(9,62,None)]),
]
ITEMS=[]
for k,lab,sec,mk,regs in RAW:
    rr=[(pg,y0-4,(y1-6) if y1 else foot(k,pg)) for pg,y0,y1 in regs]
    ITEMS.append(dict(k=k,lab=lab,sec=sec,mk=mk,regs=rr))
