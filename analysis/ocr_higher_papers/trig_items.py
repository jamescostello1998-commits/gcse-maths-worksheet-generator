import fitz

D = "C:/Users/James/Downloads/"
FILES = {"2017J-P4": "470238-j560-03-paper-4-higher-tier.pdf", "2017J-P5": "470239-j560-05-paper-5-higher-tier.pdf",
         "2017J-P6": "470240-j560-06-paper-6-higher-tier.pdf",
         "2023J-P4": "OM37705053-question-paper-paper-4.pdf", "2023J-P5": "OM39705054-question-paper-paper-5.pdf",
         "2023J-P6": "OM311705055-question-paper-paper-6.pdf",
         "2025J-P4": "OMA257.pdf", "2025J-P5": "OMA259.pdf", "2025J-P6": "OMA2511.pdf"}
for s, b in {"2018J": 528854, "2018N": 563120, "2019J": 620507, "2020N": 643916, "2021N": 667698,
             "2022J": 678152, "2022N": 691747, "2024J": 727820}.items():
    for j, p in enumerate(("P4", "P5", "P6")):
        FILES[f"{s}-{p}"] = f"{b + j}-question-paper-paper-{4 + j}.pdf"


def foot(k, pg):
    p = fitz.open(D + FILES[k])[pg]
    ys = [w[1] for w in p.get_text("words") if w[4].startswith("©") or w[4] == "Turn"]
    return (min(ys) - 6) if ys else p.rect.height - 50


# key, label, section, marks, note, [(page, y_start, y_end|None)]
# A = one triangle; B = two triangles / multi-step; C = non-calculator exact values; D = rule is one possible method
RAW = [
    ("2025J-P4", "20", "A", 3, "", [(16, 374, 779)]),
    ("2020N-P4", "14", "A", 6, "", [(12, 62, None)]),
    ("2021N-P4", "17", "A", 6, "", [(14, 62, None)]),
    ("2018J-P4", "18", "A", 6, "", [(17, 62, None)]),
    ("2023J-P4", "20", "A", 5, "", [(19, 62, 620)]),
    ("2018N-P6", "19", "A", 6, "", [(18, 62, None)]),
    ("2019J-P6", "17", "A", 8, "Bearings: part (b) uses the cosine rule. Part (a) is speed, distance and time.",
     [(17, 62, None), (18, 62, None)]),
    ("2017J-P4", "14", "B", 6, "", [(12, 62, None)]),
    ("2022J-P6", "21", "B", 6, "", [(18, 62, None)]),
    ("2022N-P6", "19", "B", 6, "", [(18, 62, None)]),
    ("2024J-P6", "18", "B", 6, "", [(17, 62, None)]),
    ("2022N-P5", "17", "C", 3, "", [(17, 62, 600)]),
    ("2020N-P5", "18", "C", 5, "", [(16, 62, None)]),
    ("2017J-P5", "20", "C", 7, "", [(14, 62, None)]),
    ("2025J-P5", "22", "C", 6, "", [(18, 62, None)]),
    ("2021N-P4", "19", "D", 9, "Part (a) is right-angled trigonometry; in (b) the area can be found with ½ab sin C.",
     [(17, 62, None), (18, 62, None)]),
    ("2024J-P5", "20", "D", 7, "The chord AB can be found with the cosine rule (or right-angled trigonometry).",
     [(15, 62, None)]),
]
ITEMS = []
for k, lab, sec, mk, note, regs in RAW:
    rr = [(pg, y0 - 4, (y1 - 6) if y1 else foot(k, pg)) for pg, y0, y1 in regs]
    ITEMS.append(dict(k=k, lab=lab, sec=sec, mk=mk, note=note, regs=rr))
