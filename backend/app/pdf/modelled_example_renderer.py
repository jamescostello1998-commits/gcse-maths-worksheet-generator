"""Renders the two-page 'modelled example' PDF: a single, richly-narrated
worked example on page 1, followed by 5 practice questions on page 2 that
use backward fading (each shows progressively less of the worked solution,
so question 1 is heavily scaffolded and question 5 is fully independent).

Distinct from app/pdf/renderer.py's render_worksheet, which renders the
standard 20-question worksheet + terse worked solutions.
"""

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

from app.core.errors import PdfRenderError
from app.core.models import ModelledExample, Question, Tier
from app.pdf.diagrams import render_diagram
from app.pdf.mathtext import to_markup
from app.pdf.styles import ACCENT, HIGHLIGHT, MARGIN, RULE, build_styles

_PAGE_WIDTH = A4[0] - 2 * MARGIN

_FADE_BLANK = "_" * 46
_ANSWER_BLANK = "_" * 22


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _fmt(text: str) -> str:
    return to_markup(_escape(text))


def _steps_shown_count(index: int, n_steps: int) -> int:
    """Backward-fading schedule across 5 practice questions: question 1
    shows almost the full worked solution (only the final answer is left
    blank), and each later question shows progressively less, until
    question 5 (index 4) is a fully independent problem with no working
    shown at all."""
    if index == 0:
        return n_steps
    if index == 1:
        return max(0, n_steps - 1)
    if index == 2:
        return n_steps // 2
    if index == 3:
        return min(1, n_steps)
    return 0


def _worked_calculation_box(lines: tuple[str, ...], styles: dict) -> Table:
    cell = [Paragraph(_fmt(line), styles["WorkedCalcLine"]) for line in lines]
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


def _worked_example_elements(topic_name: str, tier: Tier, example: ModelledExample, styles: dict) -> list:
    tier_label = tier.value.title()
    elements = [
        Paragraph(_escape(topic_name), styles["Title"]),
        Paragraph(f"{tier_label} Tier &nbsp;&#8226;&nbsp; Worked Example", styles["Meta"]),
        HRFlowable(width="100%", thickness=0.75, color=RULE, spaceAfter=16),
        Paragraph(_fmt(example.prompt), styles["WorkedPrompt"]),
    ]
    if example.diagram is not None:
        elements.append(Spacer(1, 4))
        elements.append(render_diagram(example.diagram))
        elements.append(Spacer(1, 10))
    elements.append(_worked_calculation_box(example.worked_calculation, styles))
    elements.append(Paragraph("How it works", styles["TeachingHeading"]))
    for i, step in enumerate(example.teaching_steps, start=1):
        elements.append(Paragraph(f"<b>{i}.</b> {_fmt(step)}", styles["TeachingStep"]))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(f"Answer: {_fmt(example.final_answer)}", styles["TeachingAnswer"]))
    return elements


def _practice_block(number: int, question: Question, index: int, styles: dict) -> KeepTogether:
    elements = [Paragraph(f"<b>Q{number}.</b> {_fmt(question.prompt)}", styles["PracticeQuestion"])]
    if question.diagram is not None:
        elements.append(Spacer(1, 4))
        elements.append(render_diagram(question.diagram))
        elements.append(Spacer(1, 6))

    n_steps = len(question.solution_steps)
    shown = _steps_shown_count(index, n_steps)
    if shown == 0:
        # Fully independent: don't reveal the step count via a matching number
        # of blank lines - just give a plain working area.
        elements.append(Paragraph("Show your full working below.", styles["ScaffoldBlank"]))
        for _ in range(3):
            elements.append(Paragraph(_FADE_BLANK, styles["ScaffoldBlank"]))
    else:
        for i, step in enumerate(question.solution_steps):
            if i < shown:
                elements.append(Paragraph(_fmt(step), styles["ScaffoldGiven"]))
            else:
                elements.append(Paragraph(_FADE_BLANK, styles["ScaffoldBlank"]))
    elements.append(Paragraph(f"Answer: {_ANSWER_BLANK}", styles["ScaffoldBlank"]))
    elements.append(Spacer(1, 10))
    return KeepTogether(elements)


def render_modelled_example(
    topic_name: str, tier: Tier, example: ModelledExample, practice_questions: tuple[Question, ...],
) -> bytes:
    try:
        return _render(topic_name, tier, example, practice_questions)
    except Exception as exc:
        raise PdfRenderError(exc) from exc


def _render(
    topic_name: str, tier: Tier, example: ModelledExample, practice_questions: tuple[Question, ...],
) -> bytes:
    styles = build_styles()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN,
        title=f"{topic_name} ({tier.value.title()}) - Modelled Example",
    )

    story = _worked_example_elements(topic_name, tier, example, styles)
    story.append(PageBreak())
    story.append(Paragraph("Now You Try", styles["SectionHeading"]))
    story.append(
        Paragraph(
            "Each question gives you a little less working than the one before - by Q5 you're on your own.",
            styles["PracticeIntro"],
        )
    )
    story.append(HRFlowable(width="100%", thickness=0.75, color=RULE, spaceAfter=12))

    for i, question in enumerate(practice_questions):
        story.append(_practice_block(i + 1, question, i, styles))

    doc.build(story)
    return buffer.getvalue()
