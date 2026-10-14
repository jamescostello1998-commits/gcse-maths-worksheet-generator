import fitz, json
D="C:/Users/James/Downloads/"
FILES={"2017J-P5":"470239-j560-05-paper-5-higher-tier.pdf","2018J-P5":"528855-question-paper-paper-5.pdf","2018N-P6":"563122-question-paper-paper-6.pdf",
"2019J-P5":"620508-question-paper-paper-5.pdf","2020N-P6":"643918-question-paper-paper-6.pdf","2021N-P5":"667699-question-paper-paper-5.pdf",
"2022J-P5":"678153-question-paper-paper-5.pdf","2022N-P5":"691748-question-paper-paper-5.pdf","2023J-P5":"OM39705054-question-paper-paper-5.pdf",
"2024J-P5":"727821-question-paper-paper-5.pdf","2024J-P6":"727822-question-paper-paper-6.pdf","2025J-P5":"OMA259.pdf"}
Q={"2017J-P5":13,"2018J-P5":13,"2018N-P6":14,"2019J-P5":10,"2020N-P6":18,"2021N-P5":13,"2022J-P5":16,"2022N-P5":11,"2023J-P5":16,"2024J-P5":17,"2024J-P6":17,"2025J-P5":18}
out={}
for k,f in FILES.items():
    d=fitz.open(D+f); qn=str(Q[k]); nxt=str(Q[k]+1)
    for i,p in enumerate(d):
        ws=p.get_text("words")
        starts=[w for w in ws if w[4]==qn and w[0]<60]
        if starts:
            y0=starts[0][1]
            nx=[w[1] for w in ws if w[4]==nxt and w[0]<60 and w[1]>y0]
            parts=[(w[4],round(w[1])) for w in ws if w[4] in("(a)","(b)","(c)") and w[0]<90 and w[1]>=y0-2]
            out[k]={"page":i,"y0":round(y0),"y1":round(nx[0]) if nx else None,"h":round(p.rect.height),"parts":parts}
            print(k,out[k]); break
    else: print(k,"NOT FOUND")
json.dump(out,open('loc.json','w'))
