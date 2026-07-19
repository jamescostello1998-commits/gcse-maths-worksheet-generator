from fastapi import APIRouter, Response

from app.api.schemas import (
    GenerateWorksheetRequest,
    GroupSchema,
    SectionSchema,
    TopicSummary,
)
from app.core.models import Tier
from app.core.registry import list_topics, sections_tree
from app.pdf.renderer import render_worksheet
from app.topics.base import TopicDefinition
from app.worksheet.builder import build_worksheet

router = APIRouter()


def _to_topic_summary(t: TopicDefinition) -> TopicSummary:
    return TopicSummary(
        id=t.id,
        name=t.display_name,
        description=t.description,
        fixed_tier=t.fixed_tier,
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
    worksheet = build_worksheet(payload.topic_id, tier)
    pdf_bytes = render_worksheet(worksheet)
    filename = f"{payload.topic_id}-{tier.value}-worksheet.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
