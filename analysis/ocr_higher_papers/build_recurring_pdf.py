"""Recurring-decimal question pack: every recurring decimal question part from the
33 OCR J560 Higher papers, cropped (as vector content) from the user's own PDFs,
grouped by type, with independently-verified worked answers at the back."""
import io, sys
from fractions import Fraction as Fr
import fitz

sys.path.insert(0, r"C:\Users\James\OneDrive\Documents\Worksheet Generator\gcse-worksheet-generator\backend")
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether
from app.pdf.mathtext import to_markup

from crops import ITEMS, FILES, D

OUT = r"C:\Users\James\Downloads\OCR_Higher_Recurring_Decimals.pdf"
SIT = {"2017J": "June 2017", "2018J": "June 2018", "2018N": "November 2018", "2019J": "June 2019",
       "2020N": "November 2020", "2021N": "November 2021", "2022J": "June 2022", "2022N": "November 2022",
       "2023J": "June 2023", "2024J": "June 2024", "2025J": "June 2025"}
PAPER = {"P4": "Paper 4 (calculator)", "P5": "Paper 5 (non-calculator)", "P6": "Paper 6 (calculator)"}

# ---------- independent verification of every answer (exact arithmetic) ----------
def rec(intpart, prefix, block):
    """Value of intpart.prefix(block)(block)... as an exact Fraction."""
    p = Fr(int(prefix), 10 ** len(prefix)) if prefix else Fr(0)
    b = Fr(int(block), (10 ** len(block) - 1) * 10 ** len(prefix))
    return intpart + p + b

assert Fr(7, 9) == rec(0, "", "7")
assert Fr(5, 12) == rec(0, "41", "6")
assert Fr(1, 6) == rec(0, "1", "6")
assert Fr(3, 11) == rec(0, "", "27")
assert rec(3, "", "18") == Fr(35, 11) and Fr(70, 22) == Fr(35, 11)
assert [k for k in range(1, 20) if 10 <= 35 * k <= 99 and 10 <= 11 * k <= 99] == [1, 2]
assert rec(0, "", "76") == Fr(76, 99)
assert rec(0, "", "19") == Fr(19, 99)
assert rec(0, "1", "5") == Fr(7, 45)
assert [k for k in range(1, 30) if 10 <= 7 * k <= 99 and 10 <= 45 * k <= 99] == [2]   # only 14/90
assert rec(0, "4", "16") == Fr(206, 495)
assert rec(0, "4", "8") == Fr(22, 45)
assert rec(0, "", "27") == Fr(3, 11)
assert rec(0, "", "18") == Fr(2, 11)
assert Fr(19, 990) == rec(0, "0", "19")
assert Fr(10, 11) == rec(0, "", "90")
assert rec(0, "", "6") * rec(0, "", "54") == Fr(4, 11)
assert Fr(5, 9) - rec(0, "1", "3") == Fr(19, 45)
P, Q = rec(1, "", "2"), Fr(5, 3)
assert 2 * Q - P == Fr(19, 9) == 2 + Fr(1, 9)
assert rec(1, "4", "2") / rec(0, "", "2") == Fr(32, 5) == 6 + Fr(2, 5)

# ---------- answers: (item index, answer text, [working lines]) ----------
F = lambda n, d: f"\\frac{{{n}}}{{{d}}}"
R_ = lambda pre, blk: f"\\recur{{{pre}}}{{{blk}}}"
ANS = {
    0: (R_("0.", "7"), ["7 ÷ 9 = 0.7777…, so the 7 recurs."]),
    2: (R_("0.41", "6"), ["5 ÷ 12 = 0.41666…, so only the 6 recurs."]),
    6: (R_("0.1", "6"), ["1 ÷ 6 = 0.1666…, so only the 6 recurs."]),
    9: (R_("0.", "27"), ["3 ÷ 11 = 0.272727…, so the block 27 recurs."]),
    1: ("For example 35 and 11 (or 70 and 22)",
        ["Let x = 3.181818…", "100x = 318.181818…", "100x − x: 99x = 315",
         f"x = {F(315, 99)} = {F(35, 11)}",
         "35 ÷ 11 = 3.1818… (equivalent pair with two-digit numbers: 70 ÷ 22)"]),
    3: (F(76, 99), ["Let x = 0.7676…", "100x = 76.7676…", "99x = 76", f"x = {F(76, 99)}"]),
    4: (f"Shown: {F(19, 99)}", ["Let x = 0.1919…", "100x = 19.1919…", "100x − x: 99x = 19",
                               f"x = {F(19, 99)}"]),
    7: ("Yes, she is correct (14 ÷ 90)",
        ["Let x = 0.1555…", "100x = 15.555…   and   10x = 1.555…", "90x = 14",
         f"x = {F(14, 90)} = {F(7, 45)}",
         f"Equivalent fractions: {F(7, 45)}, {F(14, 90)}, {F(21, 135)}, … Only {F(14, 90)} uses two two-digit numbers."]),
    8: (F(206, 495), ["Let x = 0.41616…", "1000x = 416.1616…   and   10x = 4.1616…", "990x = 412",
                      f"x = {F(412, 990)} = {F(206, 495)}"]),
    10: (F(22, 45), ["Let x = 0.4888…", "100x = 48.888…   and   10x = 4.888…", "90x = 44",
                     f"x = {F(44, 90)} = {F(22, 45)}"]),
    12: (F(3, 11), ["Let x = 0.2727…", "100x = 27.2727…", "99x = 27", f"x = {F(27, 99)} = {F(3, 11)}"]),
    15: (f"Shown: {F(2, 11)}", ["Let x = 0.1818…", "100x = 18.1818…", "99x = 18",
                               f"x = {F(18, 99)} = {F(2, 11)}"]),
    5: (R_("0.0", "19"), [f"{F(19, 990)} = {F(19, 99)} ÷ 10", "= 0.191919… ÷ 10 = 0.0191919…",
                          "Dividing by 10 moves every digit one place right."]),
    16: (R_("0.", "90"), [f"{F(10, 11)} = 5 × {F(2, 11)}", "= 5 × 0.181818…", "= 0.909090…"]),
    11: (F(4, 11), [f"{R_('0.', '6')} = {F(6, 9)} = {F(2, 3)}", f"{R_('0.', '54')} = {F(54, 99)} = {F(6, 11)}",
                    f"{F(2, 3)} × {F(6, 11)} = {F(12, 33)} = {F(4, 11)}"]),
    13: ("p = 19, q = 45", [f"Let x = 0.1333…:  100x = 13.333…, 10x = 1.333…, 90x = 12, x = {F(12, 90)} = {F(2, 15)}",
                            f"{F('p', 'q')} = {F(5, 9)} − {F(2, 15)} = {F(25, 45)} − {F(6, 45)} = {F(19, 45)}",
                            "19 and 45 share no common factor, so this is in lowest terms."]),
    14: (f"R = 2 {F(1, 9)}", [f"P = {R_('1.', '2')} = 1 + {F(2, 9)} = {F(11, 9)}",
                              f"Q = 1{F(2, 3)} = {F(5, 3)} = {F(15, 9)}",
                              "Q is the midpoint, so R = 2Q − P",
                              f"R = {F(30, 9)} − {F(11, 9)} = {F(19, 9)} = 2 {F(1, 9)}"]),
    17: (f"6 {F(2, 5)}", [f"Let x = 1.4222…:  100x = 142.22…, 10x = 14.22…, 90x = 128, x = {F(128, 90)} = {F(64, 45)}",
                          f"{R_('0.', '2')} = {F(2, 9)}",
                          f"{F(64, 45)} ÷ {F(2, 9)} = {F(64, 45)} × {F(9, 2)} = {F(576, 90)} = {F(32, 5)} = 6 {F(2, 5)}"]),
}

SECTIONS = [
    ("A", "Fraction to recurring decimal", "F2R"),
    ("B", "Recurring decimal to fraction", "R2F"),
    ("C", "Using a known recurring result", "KNOWN"),
    ("D", "Calculating with recurring decimals", "ARITH"),
]
order = []
for code, title, typ in SECTIONS:
    for i, it in enumerate(ITEMS):
        if it["typ"] == typ:
            order.append((code, title, i))
assert len(order) == 18 and set(ANS) == set(range(18))

# ---------- question pages (vector crops) ----------
ACCENT = (0.12, 0.30, 0.55)
MUTED = (0.40, 0.44, 0.50)
doc = fitz.open()
W, H = 595, 842
ML, MR, MT, MB = 40, 40, 44, 46
srcs = {}


def src(k):
    if k not in srcs:
        srcs[k] = fitz.open(D + FILES[k])
    return srcs[k]


def new_page():
    return doc.new_page(width=W, height=H)


page = new_page()
y = MT
page.insert_text((ML, y + 18), "Recurring decimals", fontname="hebo", fontsize=22, color=(0.09, 0.13, 0.17))
page.insert_text((ML, y + 38), "Every recurring decimal question from OCR GCSE Maths Higher, June 2017 – June 2025",
                 fontname="helv", fontsize=11, color=MUTED)
lines = ["18 question parts from 11 sittings, in four sections:",
         "A  Fraction to recurring decimal (4)     B  Recurring decimal to fraction (8)",
         "C  Using a known recurring result (2)   D  Calculating with recurring decimals (4)",
         "Questions are shown exactly as printed, with the original question numbers and working space.",
         "Most are from Paper 5, the non-calculator paper. Answers with working are at the back."]
for j, t in enumerate(lines):
    page.insert_text((ML, y + 64 + j * 15), t, fontname="helv", fontsize=9.5, color=(0.2, 0.24, 0.3))
y += 64 + len(lines) * 15 + 8
page.draw_line((ML, y), (W - MR, y), color=(0.8, 0.83, 0.87), width=0.8)
y += 14

scale = (W - ML - MR) / 555.0
qno = 0
current = None
toc = []
for code, title, i in order:
    it = ITEMS[i]
    qno += 1
    it["qno"] = qno
    crop = fitz.Rect(20, it["y0"], 575, it["y1"])
    h = crop.height * scale
    need_heading = code != current
    block = (30 if need_heading else 0) + 22 + h + 14
    if y + block > H - MB:
        page = new_page()
        y = MT
    if need_heading:
        page.insert_text((ML, y + 16), f"Section {code}  ·  {title}", fontname="hebo", fontsize=14, color=ACCENT)
        toc.append((f"Section {code}  ·  {title}", doc.page_count))
        y += 30
        current = code
    sit, pp = it["k"][:5], it["k"][6:]
    page.insert_text((ML, y + 12), f"Question {qno}", fontname="hebo", fontsize=11, color=(0.09, 0.13, 0.17))
    page.insert_text((ML + 78, y + 12), f"OCR {SIT[sit]}  ·  {PAPER[pp]}  ·  Q{it['lab']}  ·  {it['mk']} mark{'s' if it['mk'] > 1 else ''}",
                     fontname="helv", fontsize=9, color=MUTED)
    y += 18
    page.draw_line((ML, y), (W - MR, y), color=(0.86, 0.88, 0.91), width=0.6)
    y += 4
    page.show_pdf_page(fitz.Rect(ML, y, W - MR, y + h), src(it["k"]), it["page"], clip=crop)
    y += h + 14

# ---------- answers (ReportLab, app math typesetting) ----------
ink = HexColor("#16202C")
acc = HexColor("#1F4D8C")
muted = HexColor("#5B6776")
sH = ParagraphStyle("h", fontName="Helvetica-Bold", fontSize=20, leading=26, textColor=ink, spaceAfter=4)
sSub = ParagraphStyle("s", fontName="Helvetica", fontSize=10, leading=14, textColor=muted, spaceAfter=10)
sSec = ParagraphStyle("sec", fontName="Helvetica-Bold", fontSize=13, leading=18, textColor=acc, spaceBefore=10, spaceAfter=4)
sQ = ParagraphStyle("q", fontName="Helvetica-Bold", fontSize=10.5, leading=15, textColor=ink, spaceBefore=8, spaceAfter=4)
sStep = ParagraphStyle("st", fontName="Helvetica", fontSize=10.5, leading=21, textColor=ink, leftIndent=14)
sAns = ParagraphStyle("a", fontName="Helvetica-Bold", fontSize=10.5, leading=20, textColor=acc, leftIndent=14, spaceAfter=4)


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def md(t, style):
    return Paragraph(to_markup(esc(t), font_size=style.fontSize, color=style.textColor, bold=style.fontName.endswith("Bold")), style)


story = [Paragraph("Answers", sH),
         Paragraph("Worked solutions written for this pack, not OCR's mark schemes. "
                   "Every answer has been checked with exact fraction arithmetic.", sSub)]
current = None
for code, title, i in order:
    it = ITEMS[i]
    if code != current:
        story.append(Paragraph(f"Section {code} · {title}", sSec))
        current = code
    ans, steps = ANS[i]
    sit, pp = it["k"][:5], it["k"][6:]
    block = [Paragraph(f"Question {it['qno']} <font color='#5B6776' name='Helvetica' size='9'>&nbsp;&nbsp;OCR {SIT[sit]} {PAPER[pp]} Q{it['lab']} [{it['mk']}]</font>", sQ)]
    block += [md(s, sStep) for s in steps]
    block.append(md("Answer: " + ans, sAns))
    story.append(KeepTogether(block))
buf = io.BytesIO()
SimpleDocTemplate(buf, pagesize=A4, leftMargin=ML, rightMargin=MR, topMargin=MT, bottomMargin=MB,
                  title="Recurring decimals - answers").build(story)
ans_doc = fitz.open(stream=buf.getvalue(), filetype="pdf")
ans_start = doc.page_count + 1
doc.insert_pdf(ans_doc)

# footers
total = doc.page_count
for n, pg in enumerate(doc, 1):
    pg.insert_text((ML, H - 22), "Recurring decimals · OCR GCSE Maths Higher (J560) · questions © OCR",
                   fontname="helv", fontsize=8, color=MUTED)
    pg.insert_text((W - MR - 40, H - 22), f"Page {n} of {total}", fontname="helv", fontsize=8, color=MUTED)
doc.set_toc([[1, t, p] for t, p in toc] + [[1, "Answers", ans_start]])
doc.set_metadata({"title": "Recurring decimals - OCR GCSE Maths Higher questions 2017-2025"})
doc.save(OUT, garbage=3, deflate=True)
print("saved", OUT, total, "pages; answers start p", ans_start)
