"""One-off dev script (not part of the app itself): renders two PDFs for a
full-topic aesthetic review - one question from every one of the app's 296
topics, each topic on its own page, ordered by Section > Group exactly as
the app's own homepage shows them. `all_topics_review_questions.pdf` shows
just the question (matching what a student sees); `all_topics_review_answers.pdf`
additionally shows the full worked solution for that same question (matching
the app's own "Worked Solutions" page), so both can be reviewed in separate
passes.

Reuses the real renderer's own block-building helpers (`_question_block`,
`_solution_block`) and styles (`build_styles`) directly, so this is a true
preview of the app's actual current styling, not a reimplementation of it.

Run manually from `backend/`:
    .venv\\Scripts\\python.exe -m scripts.generate_review_pdfs
"""

import io
import random

from reportlab.lib.pagesizes import A4
from reportlab.platypus import HRFlowable, PageBreak, Paragraph, SimpleDocTemplate, Spacer

from app.core.registry import sections_tree
from app.core.models import Tier
from app.pdf.renderer import _question_block, _solution_block
from app.pdf.styles import MARGIN, RULE, build_styles
from app.worksheet.builder import build_worksheet

TIER_LABELS = {Tier.FOUNDATION: "Foundation", Tier.HIGHER: "Higher"}

# Fixed seed so re-running this script produces the same questions across a
# staged review (question wording won't shift between "look at questions.pdf"
# and "look at answers.pdf" sessions, or if it's regenerated after a fix).
SEED = 42


def _topic_count() -> int:
    return sum(len(group.topics) for section in sections_tree() for group in section.groups)


def _build_doc(*, include_solutions: bool) -> bytes:
    styles = build_styles()
    total = _topic_count()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN,
        title=f"All Topics Review - {'Answers' if include_solutions else 'Questions'}",
    )

    story = []
    rng = random.Random(SEED)
    index = 0
    for section in sections_tree():
        for group in section.groups:
            for topic in group.topics:
                index += 1
                if index > 1:
                    story.append(PageBreak())

                breadcrumb = (
                    f"{section.name} › {group.name} › {topic.display_name} "
                    f"({TIER_LABELS[topic.fixed_tier]})"
                )
                story.append(Paragraph(breadcrumb, styles["SectionHeading"]))
                story.append(Paragraph(f"Topic {index} of {total} &nbsp;•&nbsp; id: {topic.id}", styles["Meta"]))
                story.append(HRFlowable(width="100%", thickness=0.75, color=RULE, spaceAfter=14))

                worksheet = build_worksheet(topic.id, topic.fixed_tier, count=1, rng=rng)
                question = worksheet.questions[0]
                story.append(_question_block(1, question, styles))
                if include_solutions:
                    story.append(Spacer(1, 12))
                    story.append(_solution_block(1, question, styles))

    doc.build(story)
    return buffer.getvalue()


def main() -> None:
    print("Generating questions PDF...")
    questions_pdf = _build_doc(include_solutions=False)
    with open("all_topics_review_questions.pdf", "wb") as f:
        f.write(questions_pdf)

    print("Generating answers PDF...")
    answers_pdf = _build_doc(include_solutions=True)
    with open("all_topics_review_answers.pdf", "wb") as f:
        f.write(answers_pdf)

    print("Done: all_topics_review_questions.pdf, all_topics_review_answers.pdf")


if __name__ == "__main__":
    main()
