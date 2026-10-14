"""Sine rule, cosine rule and area of a triangle (½ab sin C) pack: every such question from the
33 OCR J560 Higher papers, cropped as vector content from the user's own PDFs, grouped by what
is needed, with worked answers checked by an independent coordinate-geometry route."""
import io, sys, re
from math import sin, cos, tan, asin, acos, radians as r, degrees as dg, sqrt, hypot, isclose
from fractions import Fraction as Fr
import fitz

sys.path.insert(0, r"C:\Users\James\OneDrive\Documents\Worksheet Generator\gcse-worksheet-generator\backend")
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, KeepTogether
from app.pdf.mathtext import to_markup

from trig_items import ITEMS, D, FILES

OUT = r"C:\Users\James\Downloads\OCR_Higher_Sine_Cosine_Rules.pdf"
SIT = {"2017J": "June 2017", "2018J": "June 2018", "2018N": "November 2018", "2019J": "June 2019",
       "2020N": "November 2020", "2021N": "November 2021", "2022J": "June 2022", "2022N": "November 2022",
       "2023J": "June 2023", "2024J": "June 2024", "2025J": "June 2025"}
PAPER = {"P4": "Paper 4 (calculator)", "P5": "Paper 5 (non-calculator)", "P6": "Paper 6 (calculator)"}


# ---------- independent checks: rebuild each figure from coordinates and re-measure ----------
def dist(P, Q):
    return hypot(P[0] - Q[0], P[1] - Q[1])


def ang(P, Q, R):  # angle at Q in degrees, via the dot product
    u, v = (P[0] - Q[0], P[1] - Q[1]), (R[0] - Q[0], R[1] - Q[1])
    return dg(acos((u[0] * v[0] + u[1] * v[1]) / (hypot(*u) * hypot(*v))))


def polar(L, a, O=(0, 0)):
    return (O[0] + L * cos(r(a)), O[1] + L * sin(r(a)))


def area(*P):  # shoelace
    return abs(sum(P[i][0] * P[i - 1][1] - P[i - 1][0] * P[i][1] for i in range(len(P)))) / 2


close = lambda a, b, t=1e-6: isclose(a, b, rel_tol=t, abs_tol=t)
rd = lambda x, n: float(f"{x:.{n}f}")
sf3 = lambda x: float(f"{x:.3g}")

# 2025 P4 Q20: BC = 12 sin40 / sin58
bc = 12 * sin(r(40)) / sin(r(58))
A, C = (0, 0), polar(12, 0)
B = polar(12 * sin(r(82)) / sin(r(58)), 40)
assert close(dist(B, C), bc) and close(ang(A, B, C), 58) and rd(bc, 2) == 9.10
# 2020N P4 Q14: angle A = 72, AC = 15, BC = 18
B_ = dg(asin(15 * sin(r(72)) / 18)); C_ = 180 - 72 - B_; ab = 18 * sin(r(C_)) / sin(r(72))
A, B, C = (0, 0), (ab, 0), polar(15, 72)
assert close(dist(B, C), 18) and sf3(ab) == 15.6
# 2021N P4 Q17: angle A = 53, AC = 48, BC = 85
B_ = dg(asin(48 * sin(r(53)) / 85)); C_ = 180 - 53 - B_; ab = 85 * sin(r(C_)) / sin(r(53))
A, B, C = (0, 0), (ab, 0), polar(48, 53)
assert close(dist(B, C), 85) and sf3(ab) == 105
# 2018J P4 Q18: sides 5.8, 6.4, 3.9 -> area by cosine rule + 1/2ab sinC, checked by Heron
cosA = (5.8 ** 2 + 6.4 ** 2 - 3.9 ** 2) / (2 * 5.8 * 6.4); a18 = 0.5 * 5.8 * 6.4 * sin(acos(cosA))
s = (5.8 + 6.4 + 3.9) / 2
assert close(a18, sqrt(s * (s - 5.8) * (s - 6.4) * (s - 3.9))) and sf3(a18) == 11.1
# 2023 P4 Q20: angle BAC and area
cosA = (10.6 ** 2 + 12.5 ** 2 - 8.2 ** 2) / (2 * 10.6 * 12.5); A_ = dg(acos(cosA))
A, C = (0, 0), (12.5, 0); B = polar(10.6, A_)
assert close(dist(B, C), 8.2) and rd(A_, 1) == 40.5
assert sf3(area(A, B, C)) == 43.1 and sf3(0.5 * 10.6 * 12.5 * sin(r(40.5))) == 43.0
# 2018N P6 Q19: AB = 9, AC = 10, C = 60, B acute
B_ = dg(asin(10 * sin(r(60)) / 9)); A_ = 180 - 60 - B_; BCl = 9 * sin(r(A_)) / sin(r(60))
C, A = (0, 0), (10, 0); B = polar(BCl, 60)
assert close(dist(A, B), 9) and ang(A, B, C) < 90 and BCl > 5
assert 9 * sin(r(180 - 60 - (180 - B_))) / sin(r(60)) < 5          # obtuse case gives BC < 5, so rejected
a19 = area(A, B, C); assert close(a19, 0.5 * 9 * 10 * sin(r(A_))) and sf3(a19) == 32.3
# 2019 P6 Q17: (a) time, (b) distance AB with bearings 015 and 057
t = 3250 / 890; assert 15 + int(t) == 18 and round((t - 3) * 60) == 39
Ab, Bb = polar(3250, 90 - 15), polar(4960, 90 - 57)
abd = sqrt(3250 ** 2 + 4960 ** 2 - 2 * 3250 * 4960 * cos(r(42)))
assert close(dist(Ab, Bb), abd) and round(abd) == 3347
# 2017 P4 Q14: angle A from triangle ADE, then AC by the sine rule
A_ = dg(acos((28 ** 2 + 41 ** 2 - 22 ** 2) / (2 * 28 * 41)))
assert close(dist((28, 0), polar(41, A_)), 22)
ac = 64 * sin(r(72)) / sin(r(A_)); ab = 64 * sin(r(180 - 72 - A_)) / sin(r(A_))
A, C, B = (0, 0), (ac, 0), polar(ab, A_)
assert close(dist(B, C), 64) and close(ang(A, B, C), 72) and sf3(ac - 28) == 92.4
# 2022J P6 Q21: AC by sine rule, AX = AC sin43; check AX/tan32 + AX/tan43 = 7.5
ac = 7.5 * sin(r(32)) / sin(r(105)); ax = ac * sin(r(43))
assert close(ax / tan(r(32)) + ax / tan(r(43)), 7.5) and sf3(ax) == 2.81
# 2022N P6 Q19: QS by sine rule in PQS, then angle QSR by cosine rule in QRS
qs = 9 * sin(r(30)) / sin(r(15)); P, Q = (0, 0), polar(9, 30)
S = (9 * sin(r(135)) / sin(r(15)), 0)
assert close(dist(Q, S), qs) and close(ang(P, S, Q), 15)
qsr = dg(acos((qs ** 2 + 13 ** 2 - 8 ** 2) / (2 * qs * 13)))
dirSQ = dg(acos((Q[0] - S[0]) / qs)); R = polar(13, dirSQ - qsr, S)               # turn from SQ away from SP
assert close(dist(Q, R), 8) and rd(qsr, 1) == 25.7
# 2024 P6 Q18: AC by sine rule in ABC, AD by cosine rule in ACD
B = (0, 0); A = polar(8, 60); C = (A[0] + A[1] / tan(r(20)), 0)
ac = 8 * sin(r(60)) / sin(r(20)); assert close(dist(A, C), ac) and close(ang(B, A, C), 100)
dirCA = dg(acos((A[0] - C[0]) / ac)); Dp = polar(6, dirCA - 55, C)
ad = sqrt(ac ** 2 + 36 - 2 * ac * 6 * cos(r(55)))
assert close(ang(A, C, Dp), 55) and close(dist(A, Dp), ad) and sf3(ad) == 17.5
# non-calculator: exact values
assert Fr(1, 2) * 3 * 13 * Fr(1, 2) + Fr(1, 2) * 5 * 12 == Fr(159, 4) and Fr(159, 4) * 10 == Fr(795, 2)
assert 5 ** 2 + 12 ** 2 == 13 ** 2
assert close(area((0, 0), (3 * cos(r(30)), 3 * sin(r(30))), (13, 0)), 9.75)
assert Fr(1, 2) * 100 * 80 * Fr(1, 2) * Fr(5, 2) == 5000
assert close(area((0, 0), (100, 0), polar(80, 30)), 2000)
assert close(0.5 * 7 * 8 * sin(r(45)), 14 * sqrt(2))
bd2 = 5 ** 2 + 7 ** 2 - 2 * 5 * 7 * Fr(4, 5); assert bd2 == 18
assert close(dist((7, 0), (4, 3)) ** 2, 18) and close(0.5 * sqrt(18) * 14 * sin(r(45)), 21)
# 2021N P4 Q19: BO = 6/sin20, area = 1/2 AB^2 sin40, checked as 1/2 x base x height
bo = 6 / sin(r(20)); assert rd(bo, 2) == 17.54
tA, tB = 6 / tan(r(35)), 6 / tan(r(20)); AB = tA + tB
a21 = 0.5 * AB * AB * sin(r(40)); assert close(a21, 0.5 * (2 * tA) * (AB * sin(r(70)))) and round(a21) == 202
# 2024 P5 Q20: AB = 12 root 3, major arc 16 pi
O, Aa = (0, 0), (0, -12); Bb = polar(12, -90 + 120)
assert close(dist(Aa, Bb), 12 * sqrt(3)) and close(ang(O, Aa, Bb), 30) and Fr(240, 360) * 24 == 16

F = lambda n, d: f"\\frac{{{n}}}{{{d}}}"
ANS = [
    ("BC = 9.10 cm (3 s.f.)",
     ["Two angles and a side, so use the sine rule. BC is opposite A, AC is opposite B:",
      f"{F('BC', 'sin 40°')} = {F(12, 'sin 58°')}",
      "BC = 12 × sin 40° ÷ sin 58° = 9.0955..."]),
    ("AB = 15.6 cm",
     ["BC (18 cm) is opposite the given angle A, so find angle B with the sine rule first:",
      f"{F('sin B', 15)} = {F('sin 72°', 18)},  so sin B = 0.79255..., B = 52.42°",
      "C = 180° - 72° - 52.42° = 55.58°",
      f"{F('AB', 'sin C')} = {F(18, 'sin 72°')},  so AB = 18 × sin 55.58° ÷ sin 72° = 15.61..."]),
    ("AB = 105 mm (3 s.f.)",
     ["BC (85 mm) is opposite the given angle A, so find angle B first:",
      f"{F('sin B', 48)} = {F('sin 53°', 85)},  so sin B = 0.45099..., B = 26.81°",
      "C = 180° - 53° - 26.81° = 100.19°",
      "AB = 85 × sin 100.19° ÷ sin 53° = 104.75..."]),
    ("11.1 cm²",
     ["Three sides, no angles: find an angle with the cosine rule (here the angle between 5.8 and 6.4):",
      f"cos θ = {F('5.8² + 6.4² - 3.9²', '2 × 5.8 × 6.4')} = 0.79997...,  θ = 36.87°",
      "Area = ½ × 5.8 × 6.4 × sin 36.87° = 11.136..."]),
    ("(a) 40.5° shown   (b) 43.0 cm² (43.1 cm² using the unrounded angle)",
     [f"(a) cos BAC = {F('10.6² + 12.5² - 8.2²', '2 × 10.6 × 12.5')} = {F('201.37', 265)} = 0.75989...",
      "BAC = cos^-1(0.75989...) = 40.546... = 40.5° (1 d.p.)",
      "(b) Area = ½ × 10.6 × 12.5 × sin 40.5° = 43.0 cm²"]),
    ("32.3 cm²",
     ["AB = 9 is opposite C = 60°, and AC = 10 is opposite B:",
      f"{F('sin B', 10)} = {F('sin 60°', 9)},  so sin B = 0.96225..., B = 74.21°",
      "(The other solution, B = 105.79°, gives BC = 2.55 cm, ruled out by BC > 5 and angle ABC < 90°.)",
      "A = 180° - 60° - 74.21° = 45.79°",
      "Area = ½ × AB × AC × sin A = ½ × 9 × 10 × sin 45.79° = 32.257..."]),
    ("(a) 6.39 pm (18:39)   (b) 3350 km (3 s.f.)",
     ["(a) Time = 3250 ÷ 890 = 3.6517 hours = 3 hours 39 minutes, so 3pm + 3 h 39 min = 6.39 pm",
      "(b) Angle ATB = 57° - 15° = 42°",
      "AB² = 3250² + 4960² - 2 × 3250 × 4960 × cos 42° = 11 205 111",
      "AB = 3347.4... km"]),
    ("CD = 92.4 m",
     [f"Triangle ADE, cosine rule:  cos A = {F('28² + 41² - 22²', '2 × 28 × 41')} = 0.86280...,  A = 30.37°",
      f"Triangle ABC, sine rule:  {F('AC', 'sin 72°')} = {F(64, 'sin 30.37°')},  so AC = 120.40 m",
      "CD = AC - AD = 120.40 - 28 = 92.40..."]),
    ("AX = 2.81 cm",
     ["Angle BAC = 180° - 32° - 43° = 105°",
      f"Sine rule:  {F('AC', 'sin 32°')} = {F('7.5', 'sin 105°')},  so AC = 4.1146 cm",
      "Triangle AXC is right-angled:  AX = AC × sin 43° = 2.806..."]),
    ("Angle QSR = 25.7°",
     ["Triangle PQS: angle PQS = 180° - 30° - 15° = 135°",
      f"Sine rule:  {F('QS', 'sin 30°')} = {F(9, 'sin 15°')},  so QS = 17.387 cm",
      f"Triangle QRS, cosine rule (QR = 8 is opposite angle QSR):  cos QSR = {F('17.387² + 13² - 8²', '2 × 17.387 × 13')} = 0.90099...",
      "QSR = 25.71..."]),
    ("AD = 17.5 cm",
     ["Triangle ABC: angle BAC = 180° - 60° - 20° = 100°",
      f"Sine rule:  {F('AC', 'sin 60°')} = {F(8, 'sin 20°')},  so AC = 20.257 cm",
      "Triangle ACD, cosine rule:  AD² = 20.257² + 6² - 2 × 20.257 × 6 × cos 55° = 306.91",
      "AD = 17.518..."]),
    ("14√2 m²",
     ["Area = ½ab sin C = ½ × 7 × 8 × sin 45°",
      f"sin 45° = {F('√2', 2)},  so area = 28 × {F('√2', 2)} = 14√2"]),
    ("(a) 5000 kg   (b) e.g. the yield per square metre varies from year to year",
     ["(a) Area = ½ × 100 × 80 × sin 30° = 4000 × ½ = 2000 m²",
      "Mass = 2000 × 2.5 = 5000 kg",
      "(b) 2.5 kg/m² is only an average: weather, pests or crop rotation could change the harvest in 2019"]),
    ("£397.5 million",
     ["Triangle ACD is right-angled at D:  AC² = 5² + 12² = 169, so AC = 13 km",
      "Area ACD = ½ × 5 × 12 = 30 km²",
      "Area ABC = ½ × 3 × 13 × sin 30° = ½ × 3 × 13 × ½ = 9.75 km²",
      "Total area = 39.75 km², cost = 39.75 × £10 million = £397.5 million"]),
    ("21 cm²",
     ["Triangle ABD, cosine rule:  BD² = 5² + 7² - 2 × 5 × 7 × cos x° = 74 - 70 × 0.8 = 18",
      "BD = √18 = 3√2 cm",
      f"Area BDC = ½ × BD × BC × sin 45° = ½ × 3√2 × 14 × {F('√2', 2)} = {F('42 × 2', 4)} = 21"]),
    ("(a) shown   (b) 202 cm² (3 s.f.)",
     ["(a) O is equidistant from all three sides, so BO bisects angle B",
      "Angle ABC = 180° - 70° - 70° = 40°, so the angle between BO and BA is 20°",
      "The radius meets BA at right angles:  sin 20° = 6 ÷ BO,  so BO = 6 ÷ sin 20° = 17.543 = 17.54 cm",
      "(b) Tangent lengths:  from B, 6 ÷ tan 20° = 16.485;  from A (AO bisects 70°), 6 ÷ tan 35° = 8.569",
      "BA = BC = 16.485 + 8.569 = 25.054 cm",
      "Area = ½ × BA × BC × sin 40° = ½ × 25.054² × sin 40° = 201.7..."]),
    ("12√3 + 16π cm",
     ["OA = OB = 12, so triangle OAB is isosceles: angle OBA = 30°, angle AOB = 120°",
      "Cosine rule:  AB² = 12² + 12² - 2 × 12 × 12 × cos 120° = 288 + 144 = 432",
      "(cos 120° = -½.)  AB = √432 = 12√3",
      f"Major arc: {F(240, 360)} × 2π × 12 = 16π",
      "Perimeter = 12√3 + 16π"]),
]
assert len(ANS) == len(ITEMS) == 17

SECTIONS = {"A": "One triangle", "B": "Two triangles: find a shared length first",
            "C": "Non-calculator: exact values", "D": "Questions where a rule is one possible method"}
LET = {"A": "Section A", "B": "Section B", "C": "Section C", "D": "Section D"}
SECS = "ABCD"
order = [i for s in SECS for i, it in enumerate(ITEMS) if it["sec"] == s]
cnt = {s: sum(1 for it in ITEMS if it["sec"] == s) for s in SECS}
TITLE = "Sine rule, cosine rule and area of a triangle"
SUB = "Every non-right-angled trigonometry question from OCR GCSE Maths Higher, June 2017 - June 2025"
INTRO = [f"{len(ITEMS)} questions from {len({it['k'] for it in ITEMS})} papers, in four sections:",
         f"A  One triangle ({cnt['A']})    B  Two triangles: find a shared length first ({cnt['B']})",
         f"C  Non-calculator: exact values ({cnt['C']})    D  A rule is one possible method ({cnt['D']})",
         "Questions are shown whole, exactly as printed, with the original question numbers and working space.",
         "Answers with working are at the back."]
ANS_NOTE = ("Worked solutions written for this pack, not OCR's mark schemes. Every answer was checked by "
            "rebuilding the figure from coordinates and re-measuring it (or with exact arithmetic for the "
            "non-calculator questions). Intermediate values are kept unrounded in the calculator.")
FOOT = "Sine and cosine rules - OCR GCSE Maths Higher (J560) - questions (c) OCR"
META = "Sine rule, cosine rule and area of a triangle - OCR GCSE Maths Higher 2017-2025"

doc = fitz.open()
W, H = 595, 842
ML, MR, MT, MB = 40, 40, 44, 46
INK, ACC, MUT = (0.09, 0.13, 0.17), (0.12, 0.30, 0.55), (0.40, 0.44, 0.50)
srcs = {}
src = lambda k: srcs.setdefault(k, fitz.open(D + FILES[k]))

page = doc.new_page(width=W, height=H)
y = MT
page.insert_text((ML, y + 18), TITLE, fontname="hebo", fontsize=21, color=INK)
page.insert_text((ML, y + 38), SUB,
                 fontname="helv", fontsize=11, color=MUT)
intro = INTRO
for j, t in enumerate(intro):
    page.insert_text((ML, y + 64 + j * 15), t, fontname="helv", fontsize=9.5, color=(0.2, 0.24, 0.3))
y += 64 + len(intro) * 15 + 8
page.draw_line((ML, y), (W - MR, y), color=(0.8, 0.83, 0.87), width=0.8)
y += 14

scale = (W - ML - MR) / 555.0
toc, current = [], None
for n, i in enumerate(order, 1):
    it = ITEMS[i]
    it["qno"] = n
    head = it["sec"] != current
    noteh = 14 if it["note"] else 0
    first_h = (it["regs"][0][2] - it["regs"][0][1]) * scale
    if y + (30 if head else 0) + 22 + noteh + first_h + 14 > H - MB:
        page = doc.new_page(width=W, height=H)
        y = MT
    if head:
        page.insert_text((ML, y + 16), f"{LET[it['sec']]}  -  {SECTIONS[it['sec']]}",
                         fontname="hebo", fontsize=14, color=ACC)
        toc.append((f"{LET[it['sec']]} - {SECTIONS[it['sec']]}", doc.page_count))
        y += 30
        current = it["sec"]
    sit, pp = it["k"][:5], it["k"][6:]
    page.insert_text((ML, y + 12), f"Question {n}", fontname="hebo", fontsize=11, color=INK)
    page.insert_text((ML + 78, y + 12), f"OCR {SIT[sit]}  -  {PAPER[pp]}  -  Q{it['lab']}  -  {it['mk']} marks",
                     fontname="helv", fontsize=9, color=MUT)
    y += 18
    if it["note"]:
        page.insert_text((ML, y + 10), it["note"], fontname="heit", fontsize=9, color=ACC)
        y += noteh
    page.draw_line((ML, y), (W - MR, y), color=(0.86, 0.88, 0.91), width=0.6)
    y += 4
    for j, (pg, y0, y1) in enumerate(it["regs"]):
        h = (y1 - y0) * scale
        if j and y + h > H - MB:          # a later region of a multi-page question goes on a fresh page
            page = doc.new_page(width=W, height=H)
            y = MT
            page.insert_text((ML, y + 12), f"Question {n} (continued)", fontname="hebo", fontsize=11, color=INK)
            y += 22
        page.show_pdf_page(fitz.Rect(ML, y, W - MR, y + h), src(it["k"]), pg, clip=fitz.Rect(20, y0, 575, y1))
        y += h + 6
    y += 8

# ---------- answers ----------
ink, acc, muted = HexColor("#16202C"), HexColor("#1F4D8C"), HexColor("#5B6776")
sH = ParagraphStyle("h", fontName="Helvetica-Bold", fontSize=20, leading=26, textColor=ink, spaceAfter=4)
sSub = ParagraphStyle("s", fontName="Helvetica", fontSize=10, leading=14, textColor=muted, spaceAfter=10)
sSec = ParagraphStyle("sec", fontName="Helvetica-Bold", fontSize=13, leading=18, textColor=acc, spaceBefore=10, spaceAfter=4)
sQ = ParagraphStyle("q", fontName="Helvetica-Bold", fontSize=10.5, leading=15, textColor=ink, spaceBefore=8, spaceAfter=4)
sStep = ParagraphStyle("st", fontName="Helvetica", fontSize=10.5, leading=21, textColor=ink, leftIndent=14)
sAns = ParagraphStyle("a", fontName="Helvetica-Bold", fontSize=10.5, leading=21, textColor=acc, leftIndent=14, spaceAfter=4)
esc = lambda t: t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
BS = chr(92)
_FR = re.compile("(" + BS + BS + "frac" + r"\{[^{}]*\}\{[^{}]*\})")


def upright(t):
    # keep every variable upright (like a, b, c) - only bare x/n would otherwise be italicised
    out = []
    for seg in _FR.split(t):
        if seg.startswith(BS + "frac"):
            out.append(seg)
        else:
            out.append(re.sub(r"(?<![A-Za-z])([xn])(?![A-Za-z])", lambda m: BS + "plain{" + m.group(1) + "}", seg))
    return "".join(out)


md = lambda t, st: Paragraph(to_markup(esc(upright(t)), font_size=st.fontSize, color=st.textColor, bold=st.fontName.endswith("Bold")), st)

story = [Paragraph("Answers", sH),
         Paragraph(ANS_NOTE, sSub)]
current = None
for i in order:
    it = ITEMS[i]
    if it["sec"] != current:
        sec_head = Paragraph(f"{LET[it['sec']]} - {SECTIONS[it['sec']]}", sSec)
        current = it["sec"]
    else:
        sec_head = None
    ans, steps = ANS[i]
    sit, pp = it["k"][:5], it["k"][6:]
    blk = ([sec_head] if sec_head else []) + [Paragraph(f"Question {it['qno']} <font color='#5B6776' name='Helvetica' size='9'>&nbsp;&nbsp;OCR {SIT[sit]} {PAPER[pp]} Q{it['lab']} [{it['mk']}]</font>", sQ)]
    blk += [md(s, sStep) for s in steps] + [md("Answer: " + re.sub(r"\s{3,}", ";  ", ans), sAns)]
    story.append(KeepTogether(blk))
buf = io.BytesIO()
SimpleDocTemplate(buf, pagesize=A4, leftMargin=ML, rightMargin=MR, topMargin=MT, bottomMargin=MB).build(story)
ans_start = doc.page_count + 1
doc.insert_pdf(fitz.open(stream=buf.getvalue(), filetype="pdf"))
total = doc.page_count
for n, pg in enumerate(doc, 1):
    pg.insert_text((ML, H - 22), FOOT,
                   fontname="helv", fontsize=8, color=MUT)
    pg.insert_text((W - MR - 40, H - 22), f"Page {n} of {total}", fontname="helv", fontsize=8, color=MUT)
doc.set_toc([[1, t, p] for t, p in toc] + [[1, "Answers", ans_start]])
doc.set_metadata({"title": META})
doc.save(OUT, garbage=3, deflate=True)
print("saved", total, "pages; answers from", ans_start)
