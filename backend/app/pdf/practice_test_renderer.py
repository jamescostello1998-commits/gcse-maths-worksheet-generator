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
    lines = [
        "Answer all questions.",
        "Write your answers clearly in the space provided.",
        "You may use a calculator.",
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
    return [
        Paragraph("GCSE Mathematics", styles["Meta"]),
        Paragraph(_escape(paper.name), styles["Title"]),
        Paragraph(
            f"{tier_label} Tier &nbsp;&#8226;&nbsp; Time allowed: 1 hour 30 minutes "
            f"&nbsp;&#8226;&nbsp; Total marks: {paper.total_marks}",
            styles["Meta"],
        ),
        HRFlowable(width="100%", thickness=0.75, color=RULE, spaceAfter=16),
        _candidate_info_table(styles),
        Spacer(1, 16),
        Paragraph("Instructions", styles["SectionHeading"]),
        _instructions_box(paper, styles),
    ]


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
    elements.append(Spacer(1, 14))
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
        _mark_scheme_table(paper, styles),
    ]

    doc.build(story)
    return buffer.getvalue()
