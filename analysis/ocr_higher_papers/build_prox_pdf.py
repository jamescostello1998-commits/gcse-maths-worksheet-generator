"""Algebraic direct & inverse proportion pack: every such question part from the 33
OCR J560 Higher papers, cropped as vector content from the user's own PDFs, grouped
direct / inverse / harder, with independently verified worked answers."""
import io, sys, math
from fractions import Fraction as Fr
import fitz

sys.path.insert(0, r"C:\Users\James\OneDrive\Documents\Worksheet Generator\gcse-worksheet-generator\backend")
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, KeepTogether
from app.pdf.mathtext import to_markup

from prox_items import ITEMS, D, FILES

OUT = r"C:\Users\James\Downloads\OCR_Higher_Algebraic_Proportion.pdf"
SIT = {"2017J": "June 2017", "2018J": "June 2018", "2018N": "November 2018", "2019J": "June 2019",
       "2020N": "November 2020", "2021N": "November 2021", "2022J": "June 2022", "2022N": "November 2022",
       "2023J": "June 2023", "2024J": "June 2024", "2025J": "June 2025"}
PAPER = {"P4": "Paper 4 (calculator)", "P5": "Paper 5 (non-calculator)", "P6": "Paper 6 (calculator)"}

# ---------- independent checks: recompute k from the given pair, then the asked value ----------
sq = lambda n: math.isqrt(n) if math.isqrt(n) ** 2 == n else None
assert Fr(30, 10 ** 2) == Fr(3, 10)                       # v = 0.3t^2 (graph reads v = 30 at t = 10)
assert Fr(1, sq(16)) == Fr(1, 4)                           # y = (1/4)sqrt(x)
assert 15 // sq(25) * sq(81) == 27                         # p = 3 sqrt(m) -> 27
k = 9 * 10 ** 2; assert k == 900 and Fr(k, 36) == 25 and sq(k // 4) == 15      # table: 25 and 15
assert Fr("0.04") * 80 == Fr("3.2") and Fr("3.2") / 32 == Fr("0.1")
assert 40 * sq(9) == 120
assert {6 * sq(4), 3 * sq(16), 2 * sq(36)} == {12}          # y sqrt(x) constant
assert Fr("3.75") * 16 == 60
assert 2 * 25 == 50
assert 5 * sq(36) == 30 and Fr(30, 20) ** 2 == Fr(9, 4)     # x = 2.25
assert Fr(9 * 4, 100) == Fr("0.36")
assert Fr(16 * 8, 8 ** 3) == Fr(1, 4)
assert 7 * sq(144) == 84 and Fr(84, sq(16)) == 21
assert 4 * 12 ** 3 == 6912
assert 5 * 36 == 180
assert Fr("1.15") ** 2 == Fr("1.3225")                      # +32.25%
assert Fr("0.7") ** 2 == Fr("0.49")                         # -51%
assert Fr(10, 60) * 6 == 1 and Fr(8, Fr("1.6")) == 5 and Fr(6, 5) == Fr("1.2")   # z = 1.2x
assert Fr(9, 2) == Fr("4.5")

F = lambda n, d: f"\\frac{{{n}}}{{{d}}}"
ANS = [
    ("v = 0.3t²", ["From the graph, v = 30 when t = 10.", "v = kt²  so  30 = k × 10²  so  k = 0.3",
                   "(Any accurate reading from the curve gives the same k, e.g. v ≈ 7.5 when t = 5.)"]),
    (f"y = {F(1, 4)}√x", ["y = k√x", "1 = k × √16 = 4k", f"k = {F(1, 4)}"]),
    ("p = 27", ["p = k√m", "15 = k × √25 = 5k, so k = 3", "p = 3√81 = 3 × 9 = 27"]),
    ("Table: x = 10, 6, 15 and y = 9, 25, 4", [f"y = {F('k', 'x²')}", "9 = k ÷ 10², so k = 900",
                                               f"x = 6:  y = {F(900, 36)} = 25",
                                               "y = 4:  x² = 900 ÷ 4 = 225, so x = 15"]),
    ("y = 0.1", [f"y = {F('k', 'x')}", "k = 0.04 × 80 = 3.2", f"y = {F('3.2', 32)} = 0.1"]),
    (f"y = {F(120, '√x')}", [f"y = {F('k', '√x')}", "40 = k ÷ √9 = k ÷ 3, so k = 120"]),
    (f"(a) shown   (b) a = {F(60, 'b²')}",
     ["(a) If y = k ÷ √x then y × √x is constant:", "6 × √4 = 12,  3 × √16 = 12,  2 × √36 = 12, all equal, so y ∝ 1/√x",
      f"(b) a = {F('k', 'b²')}:  3.75 = k ÷ 16, so k = 60"]),
    (f"y = {F(50, 'x²')}", [f"y = {F('k', 'x²')}", "2 = k ÷ 25, so k = 50"]),
    (f"(a) y = {F(30, '√x')}   (b) x = 2.25", [f"(a) y = {F('k', '√x')}:  5 = k ÷ √36 = k ÷ 6, so k = 30",
                                                f"(b) 20 = {F(30, '√x')}, so √x = 1.5", "x = 1.5² = 2.25"]),
    ("y = 0.36", [f"y = {F('k', 'x²')}", "9 = k ÷ 4, so k = 36", f"y = {F(36, 100)} = 0.36"]),
    (f"y = 0.25  (= {F(1, 4)})", [f"y = {F('k', 'x³')}", "16 = k ÷ 8, so k = 128", f"y = {F(128, 512)} = {F(1, 4)}"]),
    ("y = 21", [f"y = {F('k', '√x')}", "7 = k ÷ √144 = k ÷ 12, so k = 84", f"y = {F(84, '√16')} = {F(84, 4)} = 21"]),
    (f"y = {F(6912, 'x³')}", [f"y = {F('k', 'x³')}", "4 = k ÷ 12³ = k ÷ 1728, so k = 6912"]),
    (f"y = {F(180, 'x²')}", [f"y = {F('k', 'x²')}", "5 = k ÷ 36, so k = 180"]),
    ("32.25% increase", ["y = kx²", "x increases by 15%, so x becomes 1.15x", "y becomes k(1.15x)² = 1.3225kx²",
                         "Multiplier 1.3225, so y increases by 32.25%"]),
    ("51% decrease", ["y = kx²", "x decreases by 30%, so x becomes 0.7x", "y becomes k(0.7x)² = 0.49kx²",
                      "Multiplier 0.49, so y decreases by 51%"]),
    ("(a) 100%   (b) 50%", ["(a) y = kx: doubling x doubles y, so y increases by 100%",
                            f"(b) z = {F('k', 'x')}: doubling x halves z, so z decreases by 50%"]),
    ("z = 1.2x", ["x = ay:  10 = 60a, so a = 1/6, giving y = 6x", "y = bz:  8 = 1.6b, so b = 5, giving z = y ÷ 5",
                  "z = 6x ÷ 5 = 1.2x"]),
    ("y = 4.5x", ["Error: y ∝ x means y = kx (y is x multiplied by a constant), not y = x + c.",
                  "Correct: y = kx, so 9 = 2k, k = 4.5", "y = 4.5x"]),
]
assert len(ANS) == len(ITEMS) == 19

SECTIONS = {"D": "Direct proportion", "I": "Inverse proportion", "H": "Percentage change, chained proportion and error-spotting"}
order = [i for s in "DIH" for i, it in enumerate(ITEMS) if it["sec"] == s]

doc = fitz.open()
W, H = 595, 842
ML, MR, MT, MB = 40, 40, 44, 46
INK, ACC, MUT = (0.09, 0.13, 0.17), (0.12, 0.30, 0.55), (0.40, 0.44, 0.50)
srcs = {}
src = lambda k: srcs.setdefault(k, fitz.open(D + FILES[k]))

page = doc.new_page(width=W, height=H)
y = MT
page.insert_text((ML, y + 18), "Algebraic direct and inverse proportion", fontname="hebo", fontsize=21, color=INK)
page.insert_text((ML, y + 38), "Every question of this type from OCR GCSE Maths Higher, June 2017 - June 2025",
                 fontname="helv", fontsize=11, color=MUT)
nparts = sum(it["lab"].count("(") or 1 for it in ITEMS)
intro = [f"{nparts} question parts from 11 sittings (shown as {len(ITEMS)} questions), in three sections:",
         "A  Direct proportion (3)   B  Inverse proportion (13)",
         "C  Percentage change, chained proportion and error-spotting (6)",
         "Questions are shown exactly as printed, with the original question numbers and working space.",
         "Answers with working are at the back."]
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
    hs = [(r[2] - r[1]) * scale for r in it["regs"]]
    head = it["sec"] != current
    need = (30 if head else 0) + 22 + sum(hs) + 6 * (len(hs) - 1) + 14
    if y + need > H - MB:
        page = doc.new_page(width=W, height=H)
        y = MT
    if head:
        letter = "ABC"["DIH".index(it["sec"])]
        page.insert_text((ML, y + 16), f"Section {letter}  -  {SECTIONS[it['sec']]}", fontname="hebo", fontsize=14, color=ACC)
        toc.append((f"Section {letter} - {SECTIONS[it['sec']]}", doc.page_count))
        y += 30
        current = it["sec"]
    sit, pp = it["k"][:5], it["k"][6:]
    page.insert_text((ML, y + 12), f"Question {n}", fontname="hebo", fontsize=11, color=INK)
    page.insert_text((ML + 78, y + 12), f"OCR {SIT[sit]}  -  {PAPER[pp]}  -  Q{it['lab']}  -  {it['mk']} marks",
                     fontname="helv", fontsize=9, color=MUT)
    y += 18
    page.draw_line((ML, y), (W - MR, y), color=(0.86, 0.88, 0.91), width=0.6)
    y += 4
    for (pg, y0, y1), h in zip(it["regs"], hs):
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
import re
BS = chr(92)
_FR = re.compile("(" + BS + BS + "frac" + r"\{[^{}]*\}\{[^{}]*\})")
def upright(t):
    # keep every variable upright (like y and k) - only bare x/n would otherwise be italicised
    out = []
    for seg in _FR.split(t):
        if seg.startswith(BS + "frac"):
            out.append(seg)
        else:
            out.append(re.sub(r"(?<![A-Za-z])([xn])(?![A-Za-z])", lambda m: BS + "plain{" + m.group(1) + "}", seg))
    return "".join(out)
md = lambda t, st: Paragraph(to_markup(esc(upright(t)), font_size=st.fontSize, color=st.textColor, bold=st.fontName.endswith("Bold")), st)

story = [Paragraph("Answers", sH),
         Paragraph("Worked solutions written for this pack, not OCR's mark schemes. Each one was checked by "
                   "recomputing the constant of proportionality with exact arithmetic.", sSub)]
current = None
for i in order:
    it = ITEMS[i]
    if it["sec"] != current:
        letter = "ABC"["DIH".index(it["sec"])]
        story.append(Paragraph(f"Section {letter} - {SECTIONS[it['sec']]}", sSec))
        current = it["sec"]
    ans, steps = ANS[i]
    sit, pp = it["k"][:5], it["k"][6:]
    blk = [Paragraph(f"Question {it['qno']} <font color='#5B6776' name='Helvetica' size='9'>&nbsp;&nbsp;OCR {SIT[sit]} {PAPER[pp]} Q{it['lab']} [{it['mk']}]</font>", sQ)]
    blk += [md(s, sStep) for s in steps] + [md("Answer: " + ans, sAns)]
    story.append(KeepTogether(blk))
buf = io.BytesIO()
SimpleDocTemplate(buf, pagesize=A4, leftMargin=ML, rightMargin=MR, topMargin=MT, bottomMargin=MB).build(story)
ans_start = doc.page_count + 1
doc.insert_pdf(fitz.open(stream=buf.getvalue(), filetype="pdf"))
total = doc.page_count
for n, pg in enumerate(doc, 1):
    pg.insert_text((ML, H - 22), "Algebraic proportion - OCR GCSE Maths Higher (J560) - questions (c) OCR",
                   fontname="helv", fontsize=8, color=MUT)
    pg.insert_text((W - MR - 40, H - 22), f"Page {n} of {total}", fontname="helv", fontsize=8, color=MUT)
doc.set_toc([[1, t, p] for t, p in toc] + [[1, "Answers", ans_start]])
doc.set_metadata({"title": "Algebraic direct and inverse proportion - OCR GCSE Maths Higher 2017-2025"})
doc.save(OUT, garbage=3, deflate=True)
print("saved", total, "pages; answers from", ans_start, "; parts", nparts)
