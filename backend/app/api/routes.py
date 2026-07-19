from fastapi import APIRouter, Response

from app.api.schemas import GenerateWorksheetRequest, TopicSummary
from app.core.models import Tier
from app.core.registry import list_topics
from app.pdf.renderer import render_worksheet
from app.worksheet.builder import build_worksheet

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/topics", response_model=list[TopicSummary])
def get_topics() -> list[TopicSummary]:
    return [
        TopicSummary(id=t.id, name=t.display_name, description=t.description)
        for t in list_topics()
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
