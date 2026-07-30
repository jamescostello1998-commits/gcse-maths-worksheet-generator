from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.bell_tasks.generator import NUM_BOXES
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


class GenerateBellTasksRequest(BaseModel):
    topic_ids: list[str]

    @field_validator("topic_ids")
    @classmethod
    def _exactly_six_distinct_topics(cls, value: list[str]) -> list[str]:
        if len(value) != NUM_BOXES:
            raise ValueError(f"Bell Tasks needs exactly {NUM_BOXES} topic ids, got {len(value)}")
        if len(set(value)) != NUM_BOXES:
            raise ValueError("Bell Tasks topic ids must all be distinct")
        return value


class PracticeTestSummary(BaseModel):
    id: str
    name: str
    tier: TierEnum
    sitting_id: str
    paper_number: int
    calculator_allowed: bool
    total_marks: int
    question_count: int
