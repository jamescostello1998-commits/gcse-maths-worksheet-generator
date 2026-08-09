import random
from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, Response

from app.api.schemas import (
    FormatEnum,
    GenerateBellTasksRequest,
    GenerateWorksheetRequest,
    GroupSchema,
    PracticeTestSummary,
    SectionSchema,
    TopicSummary,
)
from app.bell_tasks.generator import generate_bell_tasks_pptx
from app.core.models import Tier
from app.core.registry import get_topic, list_topics, sections_tree
from app.docx.render import render_modelled_example_docx, render_worksheet_docx
from app.pdf.modelled_example_renderer import render_modelled_example
from app.pdf.practice_test_renderer import render_mark_scheme, render_practice_test_paper
from app.pdf.renderer import render_worksheet
from app.practice_tests.loader import get_practice_test, list_practice_tests
from app.practice_tests.models import PracticeTestPaper
from app.topics.base import TopicDefinition
from app.worksheet.builder import DEFAULT_COUNT, build_worksheet

PRACTICE_QUESTION_COUNT = 5

_DOCX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

router = APIRouter()


def _download_response(content: bytes, fmt: FormatEnum, filename_stem: str) -> Response:
    """One Response for either format - the only per-format differences are the
    media type and the file extension."""
    if fmt == FormatEnum.docx:
        media_type, ext = _DOCX_MEDIA_TYPE, "docx"
    else:
        media_type, ext = "application/pdf", "pdf"
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename_stem}.{ext}"'},
    )


def _to_topic_summary(t: TopicDefinition) -> TopicSummary:
    return TopicSummary(
        id=t.id,
        name=t.display_name,
        description=t.description,
        fixed_tier=t.fixed_tier,
        has_modelled_example=t.generate_modelled_example is not None,
        default_question_count=t.question_count or DEFAULT_COUNT,
    )


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/topics", response_model=list[TopicSummary])
def get_topics() -> list[TopicSummary]:
    return [_to_topic_summary(t) for t in list_topics()]


@router.get("/sections", response_model=list[SectionSchema])
def get_sections() -> list[SectionSchema]:
    return [
        SectionSchema(
            id=section.id,
            name=section.name,
            groups=[
                GroupSchema(
                    name=group.name,
                    topics=[_to_topic_summary(t) for t in group.topics],
                )
                for group in section.groups
            ],
        )
        for section in sections_tree()
    ]


@router.post("/worksheets")
def create_worksheet(payload: GenerateWorksheetRequest) -> Response:
    tier = Tier(payload.tier.value)
    topic = get_topic(payload.topic_id)
    count = payload.count or topic.question_count or DEFAULT_COUNT
    worksheet = build_worksheet(payload.topic_id, tier, count=count)
    if payload.format == FormatEnum.docx:
        content = render_worksheet_docx(worksheet, answers_only=payload.answers_only)
    else:
        content = render_worksheet(worksheet, answers_only=payload.answers_only)
    suffix = "-answers-only" if payload.answers_only else ""
    filename_stem = f"{payload.topic_id}-{tier.value}-worksheet{suffix}"
    return _download_response(content, payload.format, filename_stem)


@router.post("/modelled-examples")
def create_modelled_example(payload: GenerateWorksheetRequest) -> Response:
    tier = Tier(payload.tier.value)
    topic = get_topic(payload.topic_id)
    if topic.generate_modelled_example is None:
        raise HTTPException(status_code=404, detail=f"No modelled example available for '{payload.topic_id}'")

    rng = random.Random()
    example = topic.generate_modelled_example(tier, rng)
    practice_worksheet = build_worksheet(payload.topic_id, tier, count=PRACTICE_QUESTION_COUNT, rng=rng)
    if payload.format == FormatEnum.docx:
        content = render_modelled_example_docx(
            topic.display_name, tier, example, practice_worksheet.questions, topic.preamble_lines or ()
        )
    else:
        content = render_modelled_example(
            topic.display_name, tier, example, practice_worksheet.questions, topic.preamble_lines or ()
        )
    filename_stem = f"{payload.topic_id}-{tier.value}-modelled-example"
    return _download_response(content, payload.format, filename_stem)


@router.post("/bell-tasks")
def create_bell_tasks(payload: GenerateBellTasksRequest) -> Response:
    pptx_bytes = generate_bell_tasks_pptx(payload.topic_ids)
    filename = f"bell-tasks-{date.today().isoformat()}.pptx"
    return Response(
        content=pptx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _to_practice_test_summary(paper: PracticeTestPaper) -> PracticeTestSummary:
    return PracticeTestSummary(
        id=paper.id,
        name=paper.name,
        tier=paper.tier,
        sitting_id=paper.sitting_id,
        paper_number=paper.paper_number,
        calculator_allowed=paper.calculator_allowed,
        total_marks=paper.total_marks,
        question_count=len(paper.questions),
    )


@router.get("/practice-tests", response_model=list[PracticeTestSummary])
def get_practice_tests(tier: Optional[Tier] = None) -> list[PracticeTestSummary]:
    papers = list_practice_tests()
    if tier is not None:
        papers = [p for p in papers if p.tier == tier]
    return [_to_practice_test_summary(p) for p in papers]


@router.get("/practice-tests/{paper_id}/paper")
def download_practice_test_paper(paper_id: str) -> Response:
    paper = get_practice_test(paper_id)
    pdf_bytes = render_practice_test_paper(paper)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{paper_id}-test-paper.pdf"'},
    )


@router.get("/practice-tests/{paper_id}/mark-scheme")
def download_practice_test_mark_scheme(paper_id: str) -> Response:
    paper = get_practice_test(paper_id)
    pdf_bytes = render_mark_scheme(paper)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{paper_id}-mark-scheme.pdf"'},
    )
