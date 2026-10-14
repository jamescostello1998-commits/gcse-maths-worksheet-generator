"""Quadratic sequences pack: every quadratic-sequence question from the 33 OCR J560 Higher
papers (including ones that never say "quadratic"), cropped as vector content from the
user's own PDFs, plus an appendix of every other sequence question, with independently
verified worked answers."""
import io, sys, re, math
from fractions import Fraction as Fr
import fitz

sys.path.insert(0, r"C:\Users\James\OneDrive\Documents\Worksheet Generator\gcse-worksheet-generator\backend")
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, KeepTogether
from app.pdf.mathtext import to_markup

from quad_items import ITEMS, D, FILES

OUT = r"C:\Users\James\Downloads\OCR_Higher_Quadratic_Sequences.pdf"
SIT = {"2017J": "June 2017", "2018J": "June 2018", "2018N": "November 2018", "2019J": "June 2019",
       "2020N": "November 2020", "2021N": "November 2021", "2022J": "June 2022", "2022N": "November 2022",
       "2023J": "June 2023", "2024J": "June 2024", "2025J": "June 2025"}
PAPER = {"P4": "Paper 4 (calculator)", "P5": "Paper 5 (non-calculator)", "P6": "Paper 6 (calculator)"}


# ---------- independent checks ----------
def solve3(rows):
    """Gaussian elimination over Fractions (a different route from the difference method)."""
    m = [[Fr(v) for v in r] for r in rows]
    n = len(m)
    for c in range(n):
        piv = next(r for r in range(c, n) if m[r][c] != 0)
        m[c], m[piv] = m[piv], m[c]
        for r in range(n):
            if r != c and m[r][c] != 0:
                f = m[r][c] / m[c][c]
                m[r] = [x - f * y for x, y in zip(m[r], m[c])]
    return [m[r][-1] / m[r][r] for r in range(n)]


def abc(terms):
    a, b, c = solve3([[n * n, n, 1, terms[n - 1]] for n in (1, 2, 3)])
    assert all(a * n * n + b * n + c == t for n, t in enumerate(terms, 1)), terms   # 4th term must fit too
    return a, b, c


assert abc([0, 9, 22, 39]) == (2, 3, -5)
assert abc([2, 15, 34, 59]) == (3, 4, -5)
assert abc([-1, 3, 13, 29]) == (3, -5, 1)
assert abc([-1, 5, 13, 23]) == (1, 3, -5)
assert abc([2, 12, 28, 50]) == (3, 1, -2)
assert abc([5, 10, 17, 26]) == (1, 2, 2)
assert solve3([[9, 3, 9], [36, 6, 126]]) == [6, -15]
# Fibonacci x, y, ...: 4th = x + 2y, 7th = 5x + 8y
s = [3, 2]
while len(s) < 7:
    s.append(s[-1] + s[-2])
assert s[3] == 7 and s[6] == 31
assert [5 * n - 6 for n in range(1, 5)] == [-1, 4, 9, 14]
assert [Fr(n * n, n + 1) for n in range(1, 5)] == [Fr(1, 2), Fr(4, 3), Fr(9, 4), Fr(16, 5)]
assert [Fr(3 * n - 1, n * n + 2 * n + 2) for n in range(1, 6)] == [Fr(2, 5), Fr(5, 10), Fr(8, 17), Fr(11, 26), Fr(14, 37)]
r3, r5 = math.sqrt(3), math.sqrt(5)
assert all(math.isclose(5 * r3 ** (n - 1), v) for n, v in zip(range(1, 6), [5, 5 * r3, 15, 15 * r3, 45]))
assert all(math.isclose(3 * r5 ** (n - 1), v) for n, v in zip(range(1, 6), [3, 3 * r5, 15, 15 * r5, 75]))
assert all(math.isclose(r3 ** (n - 1), v) for n, v in zip(range(1, 5), [1, r3, 3, 3 * r3]))
r = 3 ** 0.25
assert math.isclose(r ** 6, 3 * r ** 2) and round(r, 3) == 1.316
assert [Fr(2 * n, 4 * n + 1) for n in range(1, 5)] == [Fr(2, 5), Fr(4, 9), Fr(6, 13), Fr(8, 17)]
sara = set(range(10, 501, 14)); tom = set(range(10, 501, 35))
assert max(sara) == 500 and max(tom) == 500 and len(sara & tom) == 8
assert [14 * n - 4 for n in range(1, 4)] == [10, 24, 38]
assert Fr("4.5") * 7 - 2 == Fr("29.5")
assert 6 * Fr(7, 4) - 7 == 2 * Fr(7, 4)
assert 6 * Fr("1.4") - 7 == Fr("1.4")

F = lambda n, d: f"\\frac{{{n}}}{{{d}}}"


def diff_steps(terms, a, b, c):
    d1 = [y - x for x, y in zip(terms, terms[1:])]
    d2 = d1[1] - d1[0]
    sq = [a * n * n for n in range(1, 5)]
    rem = [t - s for t, s in zip(terms, sq)]
    lin = f"{b}n {'+' if c >= 0 else '-'} {abs(c)}" if b != 1 else f"n {'+' if c >= 0 else '-'} {abs(c)}"
    if b == -5:
        lin = "-5n + 1"
    return [f"First differences: {', '.join(map(str, d1))}",
            f"Second difference: {d2}, so a = {d2} ÷ 2 = {a}",
            f"Subtract {a if a != 1 else ''}n² ({', '.join(map(str, sq))}) from the terms: {', '.join(map(str, rem))}",
            f"That linear sequence is {lin}, so b = {b} and c = {c}",
            f"Check n = 1: {a} + {b} + {c} = {terms[0]}".replace("+ -", "- ")]


ANS = [
    ("a = 2,  b = 3,  c = -5", diff_steps([0, 9, 22, 39], 2, 3, -5)),
    ("a = 3,  b = 4,  c = -5", diff_steps([2, 15, 34, 59], 3, 4, -5)),
    ("a = 3,  b = -5,  c = 1", diff_steps([-1, 3, 13, 29], 3, -5, 1)),
    ("(a)(ii) x = 3, y = 2   (b) (√3)^(n - 1)   (c) b = 3, c = -5",
     ["(a)(i) Terms: x,  y,  x + y,  y + (x + y) = x + 2y",
      "(a)(ii) Keep going: 5th = 2x + 3y,  6th = 3x + 5y,  7th = 5x + 8y",
      "x + 2y = 7  and  5x + 8y = 31",
      "Multiply the first by 4: 4x + 8y = 28. Subtract: x = 3, then 3 + 2y = 7 so y = 2",
      "(b) Each term is the one before × √3, starting at 1, so the nth term is (√3)^(n - 1)",
      "(c) First differences 6, 8, 10; second difference 2, so the n² coefficient is 1 (as given)",
      "Subtract n² (1, 4, 9, 16): -2, 1, 4, 7, which is 3n - 5, so b = 3 and c = -5"]),
    ("(a) 5n - 6   (b) a = 6,  b = -15",
     ["(a) The terms go up by 5, and the term before the first is -1 - 5 = -6, so 5n - 6",
      "(b) n = 3:  9a + 3b = 9, so 3a + b = 3",
      "n = 6:  36a + 6b = 126, so 6a + b = 21",
      "Subtract: 3a = 18, so a = 6, and b = 3 - 18 = -15",
      "Check: 6 × 36 - 15 × 6 = 216 - 90 = 126"]),
    (f"(a) {F('n²', 'n + 1')}   (b) a = 3,  b = 1,  c = -2",
     ["(a) Numerators 1, 4, 9, 16 are the square numbers: n²",
      f"Denominators 2, 3, 4, 5 are n + 1, so the nth term is {F('n²', 'n + 1')}",
      "(b) " + diff_steps([2, 12, 28, 50], 3, 1, -2)[0]] + diff_steps([2, 12, 28, 50], 3, 1, -2)[1:]),
    (f"(a) {F(14, 37)}   (b) {F('3n - 1', 'n² + 2n + 2')}",
     ["Numerators 2, 5, 8, 11 go up by 3: 3n - 1",
      "Denominators 5, 10, 17, 26: first differences 5, 7, 9, second difference 2, so n² + ...",
      "Subtract n² (1, 4, 9, 16): 4, 6, 8, 10, which is 2n + 2, so the denominator is n² + 2n + 2",
      f"(a) n = 5: numerator 14, denominator 25 + 10 + 2 = 37, giving {F(14, 37)}"]),
    ("(a) 45   (b) 5(√3)^(n - 1)",
     ["Each term is the one before × √3", "(a) 15√3 × √3 = 15 × 3 = 45",
      "(b) First term 5, multiplied by √3 a total of (n - 1) times"]),
    ("(a) 75   (b) 3(√5)^(n - 1)",
     ["Each term is the one before × √5", "(a) 15√5 × √5 = 15 × 5 = 75",
      "(b) First term 3, multiplied by √5 a total of (n - 1) times"]),
    ("r = 1.316 or r = -1.316",
     ["Sixth term = 3 × second term:  r⁶ = 3r²".replace("⁶", "^6"),
      "r ≠ 0, so divide by r²:  r^4 = 3",
      "r = ±3^(1/4) = ±1.31607..."]),
    (f"{F('2n', '4n + 1')}",
     ["Numerators 2, 4, 6, 8: 2n", "Denominators 5, 9, 13, 17 go up by 4: 4n + 1"]),
    ("(a) 8   (b) 14n - 4",
     ["(a) Sara: 10, 24, 38, ..., 500 (10 + 14 × 35 = 500, so 500 is her last term)",
      "Tom: 10, 45, 80, ..., 500 (10 + 35 × 14 = 500)",
      "A common term is 10 more than a multiple of both 14 and 35, i.e. of LCM(14, 35) = 70",
      "10, 80, 150, 220, 290, 360, 430, 500: 8 terms",
      "(b) Goes up by 14, term before the first is 10 - 14 = -4: 14n - 4"]),
    ("(a) k = 4.5   (b)(i) u1 = 1.75   (ii) every term is 1.4",
     ["(a) u3 = k × u2 - 2:  29.5 = 7k - 2, so 7k = 31.5 and k = 4.5",
      "(b)(i) u2 = 6u1 - 7 and u2 = 2u1, so 6u1 - 7 = 2u1, 4u1 = 7, u1 = 1.75",
      "(ii) u2 = 6 × 1.4 - 7 = 1.4, so every term is 1.4: the sequence stays constant"]),
]
assert len(ANS) == len(ITEMS) == 13

SECTIONS = {"A": "Quadratic sequences: the question says 'quadratic'",
            "B": "Quadratic sequences the question doesn't name",
            "O": "Other sequence questions (not quadratic)"}
LET = {"A": "Section A", "B": "Section B", "O": "Appendix"}
order = [i for s in "ABO" for i, it in enumerate(ITEMS) if it["sec"] == s]

doc = fitz.open()
W, H = 595, 842
ML, MR, MT, MB = 40, 40, 44, 46
INK, ACC, MUT = (0.09, 0.13, 0.17), (0.12, 0.30, 0.55), (0.40, 0.44, 0.50)
srcs = {}
src = lambda k: srcs.setdefault(k, fitz.open(D + FILES[k]))
cnt = {s: sum(1 for it in ITEMS if it["sec"] == s) for s in "ABO"}

page = doc.new_page(width=W, height=H)
y = MT
page.insert_text((ML, y + 18), "Quadratic sequences", fontname="hebo", fontsize=21, color=INK)
page.insert_text((ML, y + 38), "Every quadratic sequence question from OCR GCSE Maths Higher, June 2017 - June 2025",
                 fontname="helv", fontsize=11, color=MUT)
intro = [f"{cnt['A'] + cnt['B']} questions from 7 papers, plus every other sequence question in an appendix:",
         f"A  The question says 'quadratic' ({cnt['A']})    B  Quadratic, but the question doesn't say so ({cnt['B']})",
         f"Appendix  Other sequence questions: geometric, linear, recurrence ({cnt['O']})",
         "Questions are shown whole, exactly as printed, with the original question numbers and working space.",
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
    head = it["sec"] != current
    noteh = 14 if it["note"] else 0
    first_h = (it["regs"][0][2] - it["regs"][0][1]) * scale
    if (head and current is not None and it["sec"] == "O") or y + (30 if head else 0) + 22 + noteh + first_h + 14 > H - MB:
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
         Paragraph("Worked solutions written for this pack, not OCR's mark schemes. Every answer was checked with "
                   "exact arithmetic, solving for a, b and c by a second method and testing all four given terms.", sSub)]
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
    pg.insert_text((ML, H - 22), "Quadratic sequences - OCR GCSE Maths Higher (J560) - questions (c) OCR",
                   fontname="helv", fontsize=8, color=MUT)
    pg.insert_text((W - MR - 40, H - 22), f"Page {n} of {total}", fontname="helv", fontsize=8, color=MUT)
doc.set_toc([[1, t, p] for t, p in toc] + [[1, "Answers", ans_start]])
doc.set_metadata({"title": "Quadratic sequences - OCR GCSE Maths Higher 2017-2025"})
doc.save(OUT, garbage=3, deflate=True)
print("saved", total, "pages; answers from", ans_start)
