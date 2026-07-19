import io

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

from app.core.errors import PdfRenderError
from app.core.models import Question, Worksheet
from app.pdf.diagrams import render_diagram
from app.pdf.styles import MARGIN, RULE, build_styles


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _question_block(number: int, question: Question, styles: dict) -> KeepTogether:
    elements = [Paragraph(f"<b>Q{number}.</b> {_escape(question.prompt)}", styles["QuestionText"])]
    if question.diagram is not None:
        elements.append(Spacer(1, 4))
        elements.append(render_diagram(question.diagram))
        elements.append(Spacer(1, 6))
    return KeepTogether(elements)


def _solution_block(number: int, question: Question, styles: dict) -> KeepTogether:
    elements = [Paragraph(f"Q{number}", styles["SolutionHeading"])]
    for step in question.solution_steps:
        elements.append(Paragraph(_escape(step), styles["SolutionStep"]))
    elements.append(Paragraph(f"Answer: {_escape(question.final_answer)}", styles["FinalAnswer"]))
    return KeepTogether(elements)


def render_worksheet(worksheet: Worksheet) -> bytes:
    try:
        return _render(worksheet)
    except Exception as exc:
        raise PdfRenderError(exc) from exc


def _render(worksheet: Worksheet) -> bytes:
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

    for i, question in enumerate(worksheet.questions, start=1):
        story.append(_question_block(i, question, styles))

    story.append(PageBreak())
    story.append(Paragraph("Worked Solutions", styles["SectionHeading"]))
    story.append(HRFlowable(width="100%", thickness=0.75, color=RULE, spaceAfter=16))

    for i, question in enumerate(worksheet.questions, start=1):
        story.append(_solution_block(i, question, styles))

    doc.build(story)
    return buffer.getvalue()
