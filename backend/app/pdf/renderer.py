import io

from reportlab.lib.pagesizes import A4
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

from reportlab.lib.styles import ParagraphStyle

from app.core.errors import PdfRenderError
from app.core.models import Question, Worksheet
from app.pdf.diagrams import render_diagram
from app.pdf.mathtext import to_markup
from app.pdf.styles import ACCENT, FONT_BOLD, HIGHLIGHT, MARGIN, RULE, build_styles

_PAGE_WIDTH = A4[0] - 2 * MARGIN


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _fmt(text: str, style: ParagraphStyle) -> str:
    return to_markup(_escape(text), font_size=style.fontSize, color=style.textColor, bold=style.fontName == FONT_BOLD)


def _preamble_box(lines: tuple[str, ...], styles: dict) -> Table:
    """A boxed panel of fixed reference lines (e.g. formulae) shown once at
    the top of a worksheet, before Q1 - reuses the same boxed styling as
    the modelled-example page's worked-calculation box for a consistent
    house style."""
    cell = [Paragraph("Formulae", styles["TeachingHeading"])]
    cell += [Paragraph(_fmt(line, styles["WorkedCalcLine"]), styles["WorkedCalcLine"]) for line in lines]
    box = Table([[cell]], colWidths=[_PAGE_WIDTH])
    box.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), HIGHLIGHT),
                ("BOX", (0, 0), (-1, -1), 0.75, ACCENT),
                ("TOPPADDING", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                ("LEFTPADDING", (0, 0), (-1, -1), 16),
                ("RIGHTPADDING", (0, 0), (-1, -1), 16),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    return box


def _question_block(number: int, question: Question, styles: dict) -> KeepTogether:
    elements = [Paragraph(f"<b>Q{number}.</b> {_fmt(question.prompt, styles['QuestionText'])}", styles["QuestionText"])]
    if question.diagram is not None:
        elements.append(Spacer(1, 4))
        elements.append(render_diagram(question.diagram))
        elements.append(Spacer(1, 6))
    return KeepTogether(elements)


def _solution_block(number: int, question: Question, styles: dict) -> KeepTogether:
    elements = [Paragraph(f"Q{number}", styles["SolutionHeading"])]
    for step in question.solution_steps:
        elements.append(Paragraph(_fmt(step, styles["SolutionStep"]), styles["SolutionStep"]))
    if question.solution_diagram is not None:
        elements.append(Spacer(1, 4))
        elements.append(render_diagram(question.solution_diagram))
        elements.append(Spacer(1, 4))
    elements.append(Paragraph(f"Answer: {_fmt(question.final_answer, styles['FinalAnswer'])}", styles["FinalAnswer"]))
    return KeepTogether(elements)


def _answer_row(number: int, question: Question, styles: dict) -> Paragraph:
    return Paragraph(f"<b>Q{number}.</b> {_fmt(question.final_answer, styles['AnswerRow'])}", styles["AnswerRow"])


def render_worksheet(worksheet: Worksheet, answers_only: bool = False) -> bytes:
    try:
        return _render(worksheet, answers_only=answers_only)
    except Exception as exc:
        raise PdfRenderError(exc) from exc


def _render(worksheet: Worksheet, answers_only: bool = False) -> bytes:
    styles = build_styles()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN,
        title=f"{worksheet.topic_name} ({worksheet.tier.value.title()})",
    )

    tier_label = worksheet.tier.value.title()
    story = [
        Paragraph(_escape(worksheet.topic_name), styles["Title"]),
        Paragraph(
            f"{tier_label} Tier &nbsp;&#8226;&nbsp; {len(worksheet.questions)} Questions "
            f"&nbsp;&#8226;&nbsp; Generated {worksheet.generated_at:%d %b %Y}",
            styles["Meta"],
        ),
        HRFlowable(width="100%", thickness=0.75, color=RULE, spaceAfter=16),
    ]
    if worksheet.preamble_lines:
        story.append(_preamble_box(worksheet.preamble_lines, styles))
        story.append(Spacer(1, 12))

    for i, question in enumerate(worksheet.questions, start=1):
        story.append(_question_block(i, question, styles))

    story.append(PageBreak())
    if answers_only:
        story.append(Paragraph("Answers", styles["SectionHeading"]))
        story.append(HRFlowable(width="100%", thickness=0.75, color=RULE, spaceAfter=16))
        for i, question in enumerate(worksheet.questions, start=1):
            story.append(_answer_row(i, question, styles))
    else:
        story.append(Paragraph("Worked Solutions", styles["SectionHeading"]))
        story.append(HRFlowable(width="100%", thickness=0.75, color=RULE, spaceAfter=16))
        for i, question in enumerate(worksheet.questions, start=1):
            story.append(_solution_block(i, question, styles))

    doc.build(story)
    return buffer.getvalue()
