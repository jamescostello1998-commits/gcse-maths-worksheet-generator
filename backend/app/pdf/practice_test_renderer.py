"""Renders the two PDFs for a fixed practice-test paper (app/practice_tests):
the test paper itself (OCR-style cover page + numbered questions with marks
shown in brackets, e.g. "[3]") and a separate mark scheme (OCR-style
Question/Answer/Marks/Guidance table with M1/A1/B1-coded marking points).

Same SimpleDocTemplate + flowable-list idiom as renderer.py and
modelled_example_renderer.py. The cover-page/instructions wording is
original text written in the generic UK exam-paper genre (candidate boxes,
"answer all questions", marks-in-margin) - not copied from any real OCR
paper, which would be their copyrighted wording.
"""

import io

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.core.errors import PdfRenderError
from app.core.models import DiagramSpec, Tier
from app.pdf.diagrams import render_diagram
from app.pdf.mathtext import to_markup
from app.pdf.styles import ACCENT, FONT, FONT_BOLD, GRID, HIGHLIGHT, INK, MARGIN, MUTED, RULE, build_styles
from app.practice_tests.models import PracticeQuestion, PracticeTestPaper

_PAGE_WIDTH = A4[0] - 2 * MARGIN
_MARKS_COL_WIDTH = 40
_QUESTION_COL_WIDTH = _PAGE_WIDTH - _MARKS_COL_WIDTH


def _extra_styles() -> dict[str, ParagraphStyle]:
    return {
        "CoverLabel": ParagraphStyle(
            "CoverLabel", fontName=FONT, fontSize=9.5, textColor=MUTED, leading=12,
        ),
        "InstructionItem": ParagraphStyle(
            "InstructionItem", fontName=FONT, fontSize=10.5, textColor=INK, leading=16,
        ),
        "MarksLabel": ParagraphStyle(
            "MarksLabel", fontName=FONT_BOLD, fontSize=11, textColor=INK, alignment=2,  # TA_RIGHT
        ),
        "MarkSchemeHeader": ParagraphStyle(
            "MarkSchemeHeader", fontName=FONT_BOLD, fontSize=9.5, textColor=INK, leading=12,
        ),
        "MarkSchemeCell": ParagraphStyle(
            "MarkSchemeCell", fontName=FONT, fontSize=9, textColor=INK, leading=13,
        ),
        "MarkingGuidance": ParagraphStyle(
            "MarkingGuidance", fontName=FONT, fontSize=9.5, textColor=MUTED, leading=14,
        ),
        "FormulaGroupHeading": ParagraphStyle(
            "FormulaGroupHeading", fontName=FONT_BOLD, fontSize=11.5, textColor=ACCENT,
            spaceBefore=12, spaceAfter=6,
        ),
        "FormulaLine": ParagraphStyle(
            "FormulaLine", fontName=FONT, fontSize=11, textColor=INK, leftIndent=6, leading=16, spaceAfter=4,
        ),
        "AnswerLabel": ParagraphStyle(
            "AnswerLabel", fontName=FONT_BOLD, fontSize=10.5, textColor=INK,
        ),
    }


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _fmt(text: str, style: ParagraphStyle) -> str:
    return to_markup(_escape(text), font_size=style.fontSize, color=style.textColor, bold=style.fontName == FONT_BOLD)


def _candidate_info_table(styles: dict) -> Table:
    col_width = _PAGE_WIDTH / 3
    table = Table(
        [
            [
                Paragraph("Candidate Name", styles["CoverLabel"]),
                Paragraph("Centre Number", styles["CoverLabel"]),
                Paragraph("Candidate Number", styles["CoverLabel"]),
            ],
            [Paragraph("&nbsp;", styles["CoverLabel"])] * 3,
        ],
        colWidths=[col_width] * 3,
    )
    table.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.75, GRID),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, GRID),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 1), (-1, 1), 26),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return table


def _instructions_box(paper: PracticeTestPaper, styles: dict) -> Table:
    calculator_line = (
        "You may use a calculator, geometrical instruments, and tracing paper."
        if paper.calculator_allowed
        else "You must NOT use a calculator for this paper - geometrical instruments and tracing paper may still be used."
    )
    lines = [
        "Answer all questions.",
        "Write your answers clearly in the space provided.",
        calculator_line,
        "A Formulae Sheet for this tier is included in this document.",
        "Show your working - marks may be awarded for a correct method even if your final answer is incorrect.",
        "The number of marks for each question is shown in brackets, e.g. [3].",
        f"The total number of marks for this paper is {paper.total_marks}.",
    ]
    body = "<br/>".join(f"&#8226; {_escape(line)}" for line in lines)
    para = Paragraph(body, styles["InstructionItem"])
    box = Table([[para]], colWidths=[_PAGE_WIDTH])
    box.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.75, ACCENT),
                ("BACKGROUND", (0, 0), (-1, -1), HIGHLIGHT),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ("LEFTPADDING", (0, 0), (-1, -1), 14),
                ("RIGHTPADDING", (0, 0), (-1, -1), 14),
            ]
        )
    )
    return box


def _cover_page_elements(paper: PracticeTestPaper, styles: dict) -> list:
    tier_label = paper.tier.value.title()
    calculator_note = "" if paper.calculator_allowed else " &nbsp;&#8226;&nbsp; Non-calculator"
    return [
        Paragraph("GCSE Mathematics", styles["Meta"]),
        Paragraph(_escape(paper.name), styles["Title"]),
        Paragraph(
            f"{tier_label} Tier &nbsp;&#8226;&nbsp; Time allowed: 1 hour 30 minutes "
            f"&nbsp;&#8226;&nbsp; Total marks: {paper.total_marks}{calculator_note}",
            styles["Meta"],
        ),
        HRFlowable(width="100%", thickness=0.75, color=RULE, spaceAfter=16),
        _candidate_info_table(styles),
        Spacer(1, 16),
        Paragraph("Instructions", styles["SectionHeading"]),
        _instructions_box(paper, styles),
    ]


def _formula_line(text: str, styles: dict) -> Paragraph:
    style = styles["FormulaLine"]
    return Paragraph(_fmt(text, style), style)


def _formulae_sheet_elements(tier: Tier, styles: dict) -> list:
    """A reference Formulae Sheet, bound into the paper right after the cover
    page - matching where a real OCR paper carries its own tier-specific
    sheet. Content is the same set of generic mathematical facts every real
    OCR Formulae Sheet gives (confirmed by reading both tiers' actual 2024
    sheets) - not copied wording, since these are plain facts, not creative
    expression."""
    elements: list = [
        Paragraph("Formulae Sheet", styles["SectionHeading"]),
        Paragraph(
            "These formulae are provided for reference - you do not need to memorise them.",
            styles["Meta"],
        ),
        Paragraph("Perimeter, Area and Volume", styles["FormulaGroupHeading"]),
        _formula_line("Area of a trapezium = (1/2) × (a + b) × h", styles),
        _formula_line("Volume of a prism = area of cross-section × length", styles),
        _formula_line("Circumference of a circle = 2 × π × r = π × d", styles),
        _formula_line("Area of a circle = π × r^2", styles),
        Paragraph("Pythagoras' Theorem and Trigonometry", styles["FormulaGroupHeading"]),
        render_diagram(
            DiagramSpec(kind="right_triangle", params={"leg1_label": "b", "leg2_label": "a", "hyp_label": "c"})
        ),
        Spacer(1, 4),
        _formula_line("In any right-angled triangle with hypotenuse c: a^2 + b^2 = c^2", styles),
        _formula_line("sin(A) = a/c", styles),
        _formula_line("cos(A) = b/c", styles),
        _formula_line("tan(A) = a/b", styles),
    ]
    if tier == Tier.HIGHER:
        elements += [
            Paragraph("The Quadratic Formula", styles["FormulaGroupHeading"]),
            _formula_line("The solutions of ax^2 + bx + c = 0 are:", styles),
            _formula_line("x = (-b ± √(b^2 - 4ac)) / 2a", styles),
            Paragraph("Sine Rule, Cosine Rule and Area of a Triangle", styles["FormulaGroupHeading"]),
            render_diagram(
                DiagramSpec(
                    kind="general_triangle",
                    params={
                        "side_a_label": "a", "side_b_label": "b", "side_c_label": "c",
                        "angle_A_label": "A", "angle_B_label": "B", "angle_C_label": "C",
                    },
                )
            ),
            Spacer(1, 4),
            _formula_line("Sine rule: a / sin(A) = b / sin(B) = c / sin(C)", styles),
            _formula_line("Cosine rule: a^2 = b^2 + c^2 - 2bc × cos(A)", styles),
            _formula_line("Area of triangle = (1/2) × a × b × sin(C)", styles),
        ]
    elements += [
        Paragraph("Compound Interest", styles["FormulaGroupHeading"]),
        _formula_line("Total accrued = P × (1 + r/100)^n", styles),
        Paragraph("Probability", styles["FormulaGroupHeading"]),
        _formula_line("P(A or B) = P(A) + P(B) - P(A and B)", styles),
    ]
    if tier == Tier.HIGHER:
        elements.append(_formula_line("P(A and B) = P(A) × P(B | A)", styles))
    return elements


def _lines_for_marks(marks: int) -> int:
    """Working-space line count, scaled to the question's mark value - a
    real OCR paper gives roughly proportionally more ruled space for a
    higher-mark question, matching how much working it actually expects."""
    return max(2, marks * 2)


def _working_lines(count: int) -> Table:
    """`count` blank ruled lines spanning the question column, for the
    student's working - each row is an empty cell with a bottom border only,
    matching a real exam paper's ruled writing space."""
    data = [[""] for _ in range(count)]
    table = Table(data, colWidths=[_PAGE_WIDTH])
    table.setStyle(
        TableStyle(
            [
                ("LINEBELOW", (0, 0), (-1, -1), 0.5, MUTED),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 15),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    return table


def _answer_line(styles: dict) -> Table:
    """A distinct boxed final-answer line, separate from the working space
    above it - matches real OCR papers, which always give a dedicated ruled
    line for the final answer rather than leaving it implicit in the
    working."""
    label = Paragraph("Answer", styles["AnswerLabel"])
    table = Table([[label, ""]], colWidths=[55, _PAGE_WIDTH - 55])
    table.setStyle(
        TableStyle(
            [
                ("LINEBELOW", (1, 0), (1, 0), 0.75, INK),
                ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    return table


def _question_block(number: int, question: PracticeQuestion, styles: dict) -> KeepTogether:
    prompt_para = Paragraph(f"<b>{number}.</b> {_fmt(question.prompt, styles['QuestionText'])}", styles["QuestionText"])
    marks_para = Paragraph(f"[{question.marks}]", styles["MarksLabel"])
    row = Table([[prompt_para, marks_para]], colWidths=[_QUESTION_COL_WIDTH, _MARKS_COL_WIDTH])
    row.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    elements: list = [row]
    if question.diagram is not None:
        elements.append(Spacer(1, 4))
        elements.append(render_diagram(question.diagram))
    elements.append(Spacer(1, 10))
    elements.append(_working_lines(_lines_for_marks(question.marks)))
    elements.append(Spacer(1, 4))
    elements.append(_answer_line(styles))
    elements.append(Spacer(1, 18))
    return KeepTogether(elements)


def render_practice_test_paper(paper: PracticeTestPaper) -> bytes:
    try:
        return _render_paper(paper)
    except Exception as exc:
        raise PdfRenderError(exc) from exc


def _render_paper(paper: PracticeTestPaper) -> bytes:
    styles = build_styles()
    styles.update(_extra_styles())
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN,
        title=f"{paper.name} ({paper.tier.value.title()})",
    )

    story = _cover_page_elements(paper, styles)
    story.append(PageBreak())
    story.extend(_formulae_sheet_elements(paper.tier, styles))
    story.append(PageBreak())
    for i, question in enumerate(paper.questions, start=1):
        story.append(_question_block(i, question, styles))

    doc.build(story)
    return buffer.getvalue()


def _mark_scheme_table(paper: PracticeTestPaper, styles: dict) -> Table:
    header = [
        Paragraph("<b>Q</b>", styles["MarkSchemeHeader"]),
        Paragraph("<b>Answer</b>", styles["MarkSchemeHeader"]),
        Paragraph("<b>Marks</b>", styles["MarkSchemeHeader"]),
        Paragraph("<b>Guidance</b>", styles["MarkSchemeHeader"]),
    ]
    rows = [header]
    for i, question in enumerate(paper.questions, start=1):
        guidance = "<br/>".join(
            f"<b>{point.code}</b> {_fmt(point.description, styles['MarkSchemeCell'])}" for point in question.mark_scheme
        )
        rows.append(
            [
                Paragraph(str(i), styles["MarkSchemeCell"]),
                Paragraph(_fmt(question.final_answer, styles["MarkSchemeCell"]), styles["MarkSchemeCell"]),
                Paragraph(str(question.marks), styles["MarkSchemeCell"]),
                Paragraph(guidance, styles["MarkSchemeCell"]),
            ]
        )

    fixed_width = 30 + 90 + 48
    col_widths = [30, 90, 48, _PAGE_WIDTH - fixed_width]
    table = Table(rows, colWidths=col_widths, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, GRID),
                ("BACKGROUND", (0, 0), (-1, 0), HIGHLIGHT),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return table


def _marking_instructions_box(styles: dict) -> Table:
    """A short, own-words summary of real OCR marking convention (M/A/B marks,
    common abbreviations) - checked directly against the "Subject-Specific
    Marking Instructions" pages of actual OCR mark schemes spanning June 2017
    to June 2024, not copied from any of their wording."""
    lines = [
        "M marks are for using a correct method, and are not lost for purely numerical errors.",
        "A marks require the preceding M mark(s) to have been awarded.",
        "B marks are independent of method marks, awarded for a correct final or intermediate answer.",
        "oe = or equivalent &#8226; isw = ignore subsequent working after a correct answer &#8226; "
        "nfww = not from wrong working &#8226; rot = rounded or truncated &#8226; "
        "soi = seen or implied &#8226; dep = dependent on an earlier mark.",
    ]
    body = "<br/>".join(f"&#8226; {line}" for line in lines)
    para = Paragraph(body, styles["MarkingGuidance"])
    box = Table([[para]], colWidths=[_PAGE_WIDTH])
    box.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.75, GRID),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ("LEFTPADDING", (0, 0), (-1, -1), 14),
                ("RIGHTPADDING", (0, 0), (-1, -1), 14),
            ]
        )
    )
    return box


def render_mark_scheme(paper: PracticeTestPaper) -> bytes:
    try:
        return _render_mark_scheme(paper)
    except Exception as exc:
        raise PdfRenderError(exc) from exc


def _render_mark_scheme(paper: PracticeTestPaper) -> bytes:
    styles = build_styles()
    styles.update(_extra_styles())
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN,
        title=f"{paper.name} ({paper.tier.value.title()}) - Mark Scheme",
    )

    tier_label = paper.tier.value.title()
    story = [
        Paragraph(_escape(f"{paper.name} - Mark Scheme"), styles["Title"]),
        Paragraph(
            f"{tier_label} Tier &nbsp;&#8226;&nbsp; Total {paper.total_marks} marks", styles["Meta"]
        ),
        HRFlowable(width="100%", thickness=0.75, color=RULE, spaceAfter=16),
        _marking_instructions_box(styles),
        Spacer(1, 16),
        _mark_scheme_table(paper, styles),
    ]

    doc.build(story)
    return buffer.getvalue()
