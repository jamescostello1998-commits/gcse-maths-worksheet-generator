import fitz
from prox_locate import D, FILES as _F

FILES = dict(_F)
FILES.update({"2018N-P5": "563121-question-paper-paper-5.pdf", "2021N-P4": "667698-question-paper-paper-4.pdf",
              "2023J-P6": "OM311705055-question-paper-paper-6.pdf"})


def foot(k, pg):
    p = fitz.open(D + FILES[k])[pg]
    ys = [w[1] for w in p.get_text("words") if w[4].startswith("©") or w[4] == "Turn"]
    return (min(ys) - 6) if ys else p.rect.height - 50


# key, label, section, marks, note, [(page, y_start, y_end|None)]
# A = says "quadratic"; B = quadratic but not labelled; O = other sequences (appendix)
RAW = [
    ("2018J-P4", "19", "A", 4, "", [(18, 62, None)]),
    ("2018N-P4", "17", "A", 4, "", [(14, 361, None)]),
    ("2021N-P4", "15", "A", 4, "", [(12, 340, None)]),
    ("2022N-P4", "18", "A", 13, "Quadratic part: (c). Parts (a) Fibonacci and (b) geometric are shown for context.",
     [(15, 62, None), (16, 62, None)]),
    ("2019J-P4", "12", "B", 7, "Quadratic part: (b), the nth term an² + bn with two terms given. Part (a) is linear.",
     [(8, 62, None)]),
    ("2017J-P4", "19", "B", 6, "(a) has square-number numerators, n²; (b) says quadratic.", [(17, 62, None)]),
    ("2023J-P5", "12", "B", 4, "The denominators 5, 10, 17, 26 form a quadratic sequence.", [(10, 335, None)]),
    ("2018N-P5", "16", "O", 4, "Geometric (surds)", [(13, 62, 458)]),
    ("2020N-P6", "17", "O", 4, "Geometric (surds)", [(18, 62, 400)]),
    ("2023J-P6", "17", "O", 4, "Geometric, kth term r^k", [(18, 426, None)]),
    ("2024J-P5", "14", "O", 3, "Fraction sequence with linear numerator and denominator", [(10, 413, None)]),
    ("2025J-P5", "6", "O", 6, "Linear sequences and common terms", [(4, 62, None)]),
    ("2025J-P4", "18", "O", 6, "Recurrence relations", [(15, 62, None)]),
]
ITEMS = []
for k, lab, sec, mk, note, regs in RAW:
    rr = [(pg, y0 - 4, (y1 - 6) if y1 else foot(k, pg)) for pg, y0, y1 in regs]
    ITEMS.append(dict(k=k, lab=lab, sec=sec, mk=mk, note=note, regs=rr))
