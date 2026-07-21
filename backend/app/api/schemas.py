from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from app.worksheet.builder import MAX_COUNT, MIN_COUNT


class TierEnum(str, Enum):
    foundation = "foundation"
    higher = "higher"


class TopicSummary(BaseModel):
    id: str
    name: str
    description: str
    fixed_tier: Optional[TierEnum] = None
    has_modelled_example: bool = False
    default_question_count: int


class GroupSchema(BaseModel):
    name: str
    topics: list[TopicSummary]


class SectionSchema(BaseModel):
    id: str
    name: str
    groups: list[GroupSchema]


class GenerateWorksheetRequest(BaseModel):
    topic_id: str
    tier: TierEnum
    count: Optional[int] = Field(default=None, ge=MIN_COUNT, le=MAX_COUNT)
    answers_only: bool = False
