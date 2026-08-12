"""Renders the worksheet and modelled-example as real Word (.docx) documents -
the Word-format sibling of app/pdf/renderer.py and
app/pdf/modelled_example_renderer.py, produced when the user picks "Word"
instead of "PDF" on the home-page format toggle.

Full layout parity with the PDF (same title/meta/rule, numbered questions,
diagrams, Worked Solutions / answers-only, and the modelled-example worked
example + backward-fading practice page), rendered with the Bell Tasks
typography scheme: prose in Calibri, maths in Cambria Math, and fractions /
powers as REAL native Word equations (see app/docx/docx_omml.py). Sizes and
colours mirror the PDF's own hierarchy from app/pdf/styles.py (not Bell Tasks'
uniform 18pt purple).

Maths handling largely matches Bell Tasks (the user's choice): fractions
("num/den" and the "\\frac{}{}" marker), powers ("x^2", "^(1/2)", and even
bracketed/unattached ones like "(25x^4)^(1/2)") and column vectors
("\\colvec{}{}") become real native equations; vector letters ("\\vec{a}"/
"\\vec{b}") render as bold Cambria Math (matching the PDF's own <b> treatment);
the remaining rarer constructs the tokenizer/omml don't cover (surds "√n",
recurring-decimal dots "\\recur{}{}", "x_n" subscripts, "\\plain{}") render as
plain Cambria Math / Calibri text. The "\\frac{}{}" and "\\colvec{}{}" markers (heavily used in
solution steps/answers) can't be seen by the tokenizer, so they're handled
here before tokenizing since their content can be algebraic.
"""

import io
import re

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Mm, Pt, RGBColor

from app.bell_tasks.diagram_raster import rasterize_drawing
from app.bell_tasks.math_tokenizer import (
    ExponentSpan,
    FractionalExponentSpan,
    FractionSpan,
    TextSpan,
    tokenize,
)
from app.core.errors import PdfRenderError
from app.core.models import ModelledExample, Question, Tier, Worksheet
from app.docx import docx_omml
from app.pdf.diagrams import render_diagram
from app.pdf.modelled_example_renderer import _steps_shown_count

# Colours mirror app/pdf/styles.py.
INK = RGBColor(0x1A, 0x1A, 0x1A)
MUTED = RGBColor(0x6B, 0x6B, 0x6B)
ACCENT = RGBColor(0x2F, 0x6F, 0x4F)
ACCENT_HEX = "2F6F4F"
HIGHLIGHT_FILL = "FDF0D5"
RULE_HEX = "DDDDDD"

FONT_WORDS = "Calibri"
FONT_MATH = "Cambria Math"

MARGIN_MM = 22

_FADE_BLANK = "_" * 46
_ANSWER_BLANK = "_" * 22

# A base for an exponent is a bare digit run or a single letter not itself
# preceded by another letter (so "cos^-1" doesn't grab the "s") - same rule as
# app/bell_tasks/math_tokenizer._BASE.
_BASE = r"(?:(?<![A-Za-z])[A-Za-z]|\d+)"

# One combined pre-tokenize scan handling (in priority order) the explicit
# sentinel markers AND every exponent form, before the ordinary text between
# them is handed to the Bell Tasks tokenizer:
#   - "\\frac{}{}" -> a native baseline fraction, "\\colvec{}{}" -> a native
#     stacked column vector; "\\recur"/"\\plain" -> plain text.
#   - an exponent (attached to a bare base, OR unattached after a ")" / compound
#     expression) -> a native superscript equation, using an EMPTY base for the
#     unattached case (confirmed to render cleanly in Word). This is what stops a
#     bracketed power like "(25x^4)^(1/2)" or "(x^-2)^4" printing a literal "^"
#     caret - it raises just like the PDF does, matching the "powers rendered as
#     powers" intent, while attached simple powers stay native as Bell Tasks
#     renders them. A genuinely compound exponent with nested parens
#     (e.g. "x^(6-(-4))" in some index-law steps) matches none of these and, as
#     in the PDF itself, stays literal - accepted per the Bell-Tasks-exact scope.
_SEG_RE = re.compile(
    r"\\frac\{(?P<mnum>[^{}]*)\}\{(?P<mden>[^{}]*)\}"
    r"|\\recur\{(?P<mprefix>[^{}]*)\}\{(?P<mblock>[^{}]*)\}"
    r"|\\plain\{(?P<mplain>[^{}]*)\}"
    r"|\\colvec\{(?P<mvectop>[^{}]*)\}\{(?P<mvecbot>[^{}]*)\}"
    r"|\\vec\{(?P<vec>[ab])\}"
    r"|(?P<feb>" + _BASE + r")\^\((?P<fen>-?\d+)/(?P<fed>-?\d+)\)"
    r"|\^\((?P<ufn>-?\d+)/(?P<ufd>-?\d+)\)"
    r"|(?P<eb>" + _BASE + r")\^(?P<eexp>-?\d+)"
    r"|\^(?P<uexp>-?\d+)"
)


# ---------------------------------------------------------------------------
# Low-level run / text helpers
# ---------------------------------------------------------------------------


def _add_text_run(paragraph, text: str, font_name: str, size_pt: float, color: RGBColor, bold: bool):
    run = paragraph.add_run(text)
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.font.color.rgb = color
    run.font.bold = bold
    return run


def _emit_tokens(paragraph, text: str, size_pt: float, color: RGBColor, color_hex: str, bold: bool) -> None:
    for token in tokenize(text):
        if isinstance(token, TextSpan):
            _add_text_run(paragraph, token.text, token.font, size_pt, color, bold)
        elif isinstance(token, FractionSpan):
            docx_omml.add_fraction(paragraph, token.sign, token.numerator, token.denominator, size_pt, color_hex)
        elif isinstance(token, ExponentSpan):
            docx_omml.add_exponent(paragraph, token.base, token.exponent, size_pt, color_hex)
        elif isinstance(token, FractionalExponentSpan):
            docx_omml.add_fractional_exponent(
                paragraph, token.base, token.numerator, token.denominator, size_pt, color_hex
            )


def _emit_segment(paragraph, seg: str, size_pt: float, color: RGBColor, color_hex: str, bold: bool) -> None:
    """Handle the explicit markers and every exponent form (which the tokenizer
    can't fully cover) first, tokenizing the ordinary text between them."""
    pos = 0
    for m in _SEG_RE.finditer(seg):
        if m.start() > pos:
            _emit_tokens(paragraph, seg[pos : m.start()], size_pt, color, color_hex, bold)
        if m.group("mnum") is not None:
            docx_omml.add_fraction(paragraph, "", m.group("mnum"), m.group("mden"), size_pt, color_hex)
        elif m.group("mplain") is not None:
            # Opt-out-of-styling marker (e.g. ratio "1:n"): a plain upright run.
            _add_text_run(paragraph, m.group("mplain"), FONT_WORDS, size_pt, color, bold)
        elif m.group("mprefix") is not None:
            # Recurring decimal - plain-text parenthesis convention (the app's
            # own pre-dot-image notation), prefix already includes "0.".
            _add_text_run(paragraph, f"{m.group('mprefix')}({m.group('mblock')})", FONT_MATH, size_pt, color, bold)
        elif m.group("mvectop") is not None:
            # Column vector - a real native stacked "(top / bottom)" equation.
            docx_omml.add_column_vector(paragraph, m.group("mvectop"), m.group("mvecbot"), size_pt, color_hex)
        elif m.group("vec") is not None:
            # Vector letter (\vec{a}/\vec{b}) - always bold, matching real exam
            # convention and the PDF's own <b> treatment (handled here, not left
            # to the tokenizer, which would flatten it to plain Cambria Math).
            _add_text_run(paragraph, m.group("vec"), FONT_MATH, size_pt, color, bold=True)
        elif m.group("feb") is not None:
            docx_omml.add_fractional_exponent(paragraph, m.group("feb"), m.group("fen"), m.group("fed"), size_pt, color_hex)
        elif m.group("ufn") is not None:
            docx_omml.add_fractional_exponent(paragraph, "", m.group("ufn"), m.group("ufd"), size_pt, color_hex)
        elif m.group("eb") is not None:
            docx_omml.add_exponent(paragraph, m.group("eb"), m.group("eexp"), size_pt, color_hex)
        else:  # unattached integer exponent (e.g. after a ")")
            docx_omml.add_exponent(paragraph, "", m.group("uexp"), size_pt, color_hex)
        pos = m.end()
    if pos < len(seg):
        _emit_tokens(paragraph, seg[pos:], size_pt, color, color_hex, bold)


def _add_runs(paragraph, text: str, *, size_pt: float, color: RGBColor, bold: bool = False) -> None:
    """Renders `text` (the same plain-ASCII maths convention app/pdf/mathtext.py
    parses) into the paragraph as a mix of styled text runs and native
    equations. A literal "\\n" becomes a real in-paragraph line break (matching
    the PDF's <br/> handling)."""
    color_hex = str(color)
    for i, line in enumerate(text.split("\n")):
        if i > 0:
            paragraph.add_run().add_break(WD_BREAK.LINE)
        _emit_segment(paragraph, line, size_pt, color, color_hex, bold)


# ---------------------------------------------------------------------------
# Structural helpers (rule, box, diagram, headings)
# ---------------------------------------------------------------------------


def _add_hrule(doc, space_after_pt: float = 8) -> None:
    p = doc.add_paragraph()
    p_pr = p._p.get_or_add_pPr()
    pbdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "6")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), RULE_HEX)
    pbdr.append(bottom)
    p_pr.append(pbdr)
    p.paragraph_format.space_after = Pt(space_after_pt)


def _set_cell_shading(cell, fill_hex: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill_hex)
    tc_pr.append(shd)


def _set_table_borders(table, color_hex: str) -> None:
    tbl_pr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "8")
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), color_hex)
        borders.append(el)
    tbl_pr.append(borders)


def _usable_width_emu(doc) -> int:
    s = doc.sections[0]
    return s.page_width - s.left_margin - s.right_margin


def _boxed_box(doc, heading: str | None, lines: tuple[str, ...], line_size_pt: float) -> None:
    """A shaded, accent-bordered single-cell box reproducing the PDF's
    formulae / worked-calculation panels."""
    table = doc.add_table(rows=1, cols=1)
    table.autofit = False
    width = _usable_width_emu(doc)
    table.columns[0].width = width
    _set_table_borders(table, ACCENT_HEX)
    cell = table.cell(0, 0)
    cell.width = width
    _set_cell_shading(cell, HIGHLIGHT_FILL)

    para0 = cell.paragraphs[0]
    remaining = list(lines)
    if heading:
        _add_text_run(para0, heading, FONT_WORDS, 11.5, MUTED, True)
    else:
        _add_runs(para0, remaining.pop(0), size_pt=line_size_pt, color=INK, bold=True)
    for line in remaining:
        p = cell.add_paragraph()
        _add_runs(p, line, size_pt=line_size_pt, color=INK, bold=True)


def _add_diagram(doc, spec) -> None:
    drawing = render_diagram(spec)
    png = rasterize_drawing(drawing)
    usable_in = _usable_width_emu(doc) / 914400
    width_in = min(drawing.width / 72.0, usable_in)
    doc.add_picture(io.BytesIO(png), width=Inches(width_in))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER


def _title_block(doc, topic_name: str, meta_text: str) -> None:
    t = doc.add_paragraph()
    _add_text_run(t, topic_name, FONT_WORDS, 20, INK, True)
    t.paragraph_format.space_after = Pt(4)
    m = doc.add_paragraph()
    _add_text_run(m, meta_text, FONT_WORDS, 10.5, MUTED, False)
    m.paragraph_format.space_after = Pt(4)
    _add_hrule(doc, space_after_pt=12)


def _section_heading(doc, text: str) -> None:
    h = doc.add_paragraph()
    _add_text_run(h, text, FONT_WORDS, 17, INK, True)
    h.paragraph_format.space_after = Pt(8)
    _add_hrule(doc, space_after_pt=12)


def _new_document() -> Document:
    doc = Document()
    for section in doc.sections:
        section.left_margin = Mm(MARGIN_MM)
        section.right_margin = Mm(MARGIN_MM)
        section.top_margin = Mm(MARGIN_MM)
        section.bottom_margin = Mm(MARGIN_MM)
    normal = doc.styles["Normal"]
    normal.font.name = FONT_WORDS
    normal.font.size = Pt(11)
    return doc


# ---------------------------------------------------------------------------
# Worksheet blocks
# ---------------------------------------------------------------------------


def _instruction_paragraph(doc, text: str) -> None:
    """The hoisted shared instruction, shown once at the top of a page."""
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(10)
    _add_runs(p, text, size_pt=11.5, color=INK, bold=True)


def _question_block(doc, number: int, question: Question, *, hoist: bool = False) -> None:
    body = question.item_text if (hoist and question.item_text) else question.prompt
    p = doc.add_paragraph()
    _add_text_run(p, f"Q{number}. ", FONT_WORDS, 11.5, INK, True)
    _add_runs(p, body, size_pt=11.5, color=INK, bold=False)
    p.paragraph_format.space_after = Pt(10)
    if question.diagram is not None:
        _add_diagram(doc, question.diagram)


def _solution_block(doc, number: int, question: Question, *, hoist: bool = False) -> None:
    h = doc.add_paragraph()
    _add_text_run(h, f"Q{number}", FONT_WORDS, 11.5, ACCENT, True)
    if hoist and question.item_text:
        _add_text_run(h, ". ", FONT_WORDS, 11.5, ACCENT, True)
        _add_runs(h, question.item_text, size_pt=11.5, color=ACCENT, bold=True)
    h.paragraph_format.space_before = Pt(8)
    h.paragraph_format.space_after = Pt(4)
    for step in question.solution_steps:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        _add_runs(p, step, size_pt=10.5, color=INK, bold=False)
    if question.solution_diagram is not None:
        _add_diagram(doc, question.solution_diagram)
    a = doc.add_paragraph()
    a.paragraph_format.left_indent = Pt(14)
    a.paragraph_format.space_after = Pt(10)
    _add_text_run(a, "Answer: ", FONT_WORDS, 10.5, INK, True)
    _add_runs(a, question.final_answer, size_pt=10.5, color=INK, bold=True)


def _answer_row(doc, number: int, question: Question, *, hoist: bool = False) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    _add_text_run(p, f"Q{number}. ", FONT_WORDS, 10.5, INK, True)
    if hoist and question.item_text:
        _add_runs(p, question.item_text, size_pt=10.5, color=INK, bold=False)
        _add_text_run(p, " — ", FONT_WORDS, 10.5, INK, False)
    _add_runs(p, question.final_answer, size_pt=10.5, color=INK, bold=False)


def render_worksheet_docx(worksheet: Worksheet, answers_only: bool = False) -> bytes:
    try:
        return _render_worksheet(worksheet, answers_only)
    except Exception as exc:  # noqa: BLE001 - mirror render_worksheet's error wrapping
        raise PdfRenderError(exc) from exc


def _render_worksheet(worksheet: Worksheet, answers_only: bool) -> bytes:
    doc = _new_document()
    tier_label = worksheet.tier.value.title()
    meta = (
        f"{tier_label} Tier  \u2022  {len(worksheet.questions)} Questions  \u2022  "
        f"Generated {worksheet.generated_at:%d %b %Y}"
    )
    _title_block(doc, worksheet.topic_name, meta)

    if worksheet.preamble_lines:
        _boxed_box(doc, "Formulae", worksheet.preamble_lines, 12.5)
        doc.add_paragraph()

    hoist = worksheet.shared_instruction is not None
    if hoist:
        _instruction_paragraph(doc, worksheet.shared_instruction)

    for i, question in enumerate(worksheet.questions, start=1):
        _question_block(doc, i, question, hoist=hoist)

    doc.add_page_break()
    if answers_only:
        _section_heading(doc, "Answers")
        if hoist:
            _instruction_paragraph(doc, worksheet.shared_instruction)
        for i, question in enumerate(worksheet.questions, start=1):
            _answer_row(doc, i, question, hoist=hoist)
    else:
        _section_heading(doc, "Worked Solutions")
        if hoist:
            _instruction_paragraph(doc, worksheet.shared_instruction)
        for i, question in enumerate(worksheet.questions, start=1):
            _solution_block(doc, i, question, hoist=hoist)

    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


# ---------------------------------------------------------------------------
# Modelled example
# ---------------------------------------------------------------------------


def _practice_block(doc, number: int, question: Question, index: int) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(8)
    _add_text_run(p, f"Q{number}. ", FONT_WORDS, 11.5, INK, True)
    _add_runs(p, question.prompt, size_pt=11.5, color=INK, bold=True)
    if question.diagram is not None:
        _add_diagram(doc, question.diagram)

    n_steps = len(question.solution_steps)
    shown = _steps_shown_count(index, n_steps)
    if shown == 0:
        intro = doc.add_paragraph()
        intro.paragraph_format.left_indent = Pt(14)
        _add_text_run(intro, "Show your full working below.", FONT_WORDS, 10.5, MUTED, False)
        for _ in range(3):
            b = doc.add_paragraph()
            b.paragraph_format.left_indent = Pt(14)
            _add_text_run(b, _FADE_BLANK, FONT_WORDS, 10.5, MUTED, False)
    else:
        for i, step in enumerate(question.solution_steps):
            line = doc.add_paragraph()
            line.paragraph_format.left_indent = Pt(14)
            line.paragraph_format.space_after = Pt(6)
            if i < shown:
                _add_runs(line, step, size_pt=10.5, color=INK, bold=False)
            else:
                _add_text_run(line, _FADE_BLANK, FONT_WORDS, 10.5, MUTED, False)
    ans = doc.add_paragraph()
    ans.paragraph_format.left_indent = Pt(14)
    _add_text_run(ans, f"Answer: {_ANSWER_BLANK}", FONT_WORDS, 10.5, MUTED, False)


def render_modelled_example_docx(
    topic_name: str,
    tier: Tier,
    example: ModelledExample,
    practice_questions: tuple[Question, ...],
    preamble_lines: tuple[str, ...] = (),
) -> bytes:
    try:
        return _render_modelled_example(topic_name, tier, example, practice_questions, preamble_lines)
    except Exception as exc:  # noqa: BLE001
        raise PdfRenderError(exc) from exc


def _render_modelled_example(
    topic_name: str,
    tier: Tier,
    example: ModelledExample,
    practice_questions: tuple[Question, ...],
    preamble_lines: tuple[str, ...],
) -> bytes:
    doc = _new_document()
    tier_label = tier.value.title()

    t = doc.add_paragraph()
    _add_text_run(t, topic_name, FONT_WORDS, 20, INK, True)
    t.paragraph_format.space_after = Pt(4)
    m = doc.add_paragraph()
    _add_text_run(m, f"{tier_label} Tier  \u2022  Worked Example", FONT_WORDS, 10.5, MUTED, False)
    m.paragraph_format.space_after = Pt(4)
    _add_hrule(doc, space_after_pt=12)

    if preamble_lines:
        _boxed_box(doc, "Formulae", preamble_lines, 12.5)
        doc.add_paragraph()

    wp = doc.add_paragraph()
    _add_runs(wp, example.prompt, size_pt=13.5, color=INK, bold=True)
    wp.paragraph_format.space_after = Pt(12)
    if example.diagram is not None:
        _add_diagram(doc, example.diagram)

    _boxed_box(doc, None, example.worked_calculation, 12.5)

    th = doc.add_paragraph()
    _add_text_run(th, "How it works", FONT_WORDS, 11.5, MUTED, True)
    th.paragraph_format.space_before = Pt(16)
    th.paragraph_format.space_after = Pt(10)
    for i, step in enumerate(example.teaching_steps, start=1):
        sp = doc.add_paragraph()
        sp.paragraph_format.left_indent = Pt(16)
        sp.paragraph_format.space_after = Pt(14)
        _add_text_run(sp, f"{i}. ", FONT_WORDS, 11.5, INK, True)
        _add_runs(sp, step, size_pt=11.5, color=INK, bold=False)

    ans = doc.add_paragraph()
    ans.paragraph_format.space_before = Pt(6)
    _add_text_run(ans, "Answer: ", FONT_WORDS, 13, ACCENT, True)
    _add_runs(ans, example.final_answer, size_pt=13, color=ACCENT, bold=True)

    doc.add_page_break()
    h = doc.add_paragraph()
    _add_text_run(h, "Now You Try", FONT_WORDS, 17, INK, True)
    h.paragraph_format.space_after = Pt(6)
    intro = doc.add_paragraph()
    _add_text_run(
        intro,
        "Each question gives you a little less working than the one before - by Q5 you're on your own.",
        FONT_WORDS,
        10.5,
        MUTED,
        False,
    )
    _add_hrule(doc, space_after_pt=12)

    for i, question in enumerate(practice_questions):
        _practice_block(doc, i + 1, question, i)

    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()
