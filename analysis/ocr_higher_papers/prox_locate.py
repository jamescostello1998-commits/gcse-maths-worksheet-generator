import fitz
D="C:/Users/James/Downloads/"
FILES={"2017J-P4":"470238-j560-03-paper-4-higher-tier.pdf","2017J-P6":"470240-j560-06-paper-6-higher-tier.pdf",
"2018J-P4":"528854-question-paper-paper-4.pdf","2018J-P6":"528856-question-paper-paper-6.pdf","2018N-P4":"563120-question-paper-paper-4.pdf",
"2019J-P4":"620507-question-paper-paper-4.pdf","2020N-P4":"643916-question-paper-paper-4.pdf","2020N-P6":"643918-question-paper-paper-6.pdf",
"2021N-P6":"667700-question-paper-paper-6.pdf","2022J-P5":"678153-question-paper-paper-5.pdf","2022N-P4":"691747-question-paper-paper-4.pdf",
"2022N-P6":"691749-question-paper-paper-6.pdf","2023J-P4":"OM37705053-question-paper-paper-4.pdf","2023J-P5":"OM39705054-question-paper-paper-5.pdf",
"2024J-P4":"727820-question-paper-paper-4.pdf","2024J-P5":"727821-question-paper-paper-5.pdf","2024J-P6":"727822-question-paper-paper-6.pdf",
"2025J-P4":"OMA257.pdf","2025J-P5":"OMA259.pdf"}
NEED={"2017J-P4":15,"2017J-P6":12,"2018J-P4":11,"2018J-P6":6,"2018N-P4":14,"2019J-P4":16,"2020N-P4":16,"2020N-P6":9,"2021N-P6":14,
"2022J-P5":11,"2022N-P4":13,"2022N-P6":14,"2023J-P4":15,"2023J-P5":11,"2024J-P4":10,"2024J-P5":8,"2024J-P6":15,"2025J-P4":15,"2025J-P5":13}
def qmarks(p):
    out=[]
    for w in p.get_text("words"):
        if w[0]<60 and w[4].isdigit() and 1<=int(w[4])<=30: out.append((int(w[4]),round(w[1])))
        if w[0]<90 and w[4] in ("(a)","(b)","(c)","(d)","(e)"): out.append((w[4],round(w[1])))
    return out
if __name__=="__main__":
    for k,q in NEED.items():
        d=fitz.open(D+FILES[k])
        for i,p in enumerate(d):
            m=qmarks(p)
            if (q,) and any(x[0]==q for x in m):
                print(k,"Q",q,"page",i,m); 
                print("   next page",i+1,qmarks(d[i+1]) if i+1<d.page_count else None); break
