import random

from fastapi import APIRouter, HTTPException, Response

from app.api.schemas import (
    GenerateWorksheetRequest,
    GroupSchema,
    SectionSchema,
    TopicSummary,
)
from app.core.models import Tier
from app.core.registry import get_topic, list_topics, sections_tree
from app.pdf.modelled_example_renderer import render_modelled_example
from app.pdf.renderer import render_worksheet
from app.topics.base import TopicDefinition
from app.worksheet.builder import DEFAULT_COUNT, build_worksheet

PRACTICE_QUESTION_COUNT = 5

router = APIRouter()


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
    pdf_bytes = render_worksheet(worksheet, answers_only=payload.answers_only)
    suffix = "-answers-only" if payload.answers_only else ""
    filename = f"{payload.topic_id}-{tier.value}-worksheet{suffix}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/modelled-examples")
def create_modelled_example(payload: GenerateWorksheetRequest) -> Response:
    tier = Tier(payload.tier.value)
    topic = get_topic(payload.topic_id)
    if topic.generate_modelled_example is None:
        raise HTTPException(status_code=404, detail=f"No modelled example available for '{payload.topic_id}'")

    rng = random.Random()
    example = topic.generate_modelled_example(tier, rng)
    practice_worksheet = build_worksheet(payload.topic_id, tier, count=PRACTICE_QUESTION_COUNT, rng=rng)
    pdf_bytes = render_modelled_example(topic.display_name, tier, example, practice_worksheet.questions)
    filename = f"{payload.topic_id}-{tier.value}-modelled-example.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
