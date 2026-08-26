from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from app.bell_tasks.generator import BOX_COUNTS, YEAR_10
from app.worksheet.builder import MAX_COUNT, MIN_COUNT


class TierEnum(str, Enum):
    foundation = "foundation"
    higher = "higher"


class FormatEnum(str, Enum):
    pdf = "pdf"
    docx = "docx"


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
    # Default "pdf" so existing request bodies (which omit it) are unchanged.
    format: FormatEnum = FormatEnum.pdf


class BellTasksYearEnum(str, Enum):
    year_10 = "year_10"
    year_11 = "year_11"


class GenerateBellTasksRequest(BaseModel):
    topic_ids: list[str]
    # Default "year_10" so an existing request body (which omits it) keeps
    # meaning the original 6-box template.
    year: BellTasksYearEnum = BellTasksYearEnum(YEAR_10)

    @model_validator(mode="after")
    def _exactly_n_distinct_topics(self) -> "GenerateBellTasksRequest":
        expected = BOX_COUNTS[self.year.value]
        if len(self.topic_ids) != expected:
            raise ValueError(f"Bell Tasks for {self.year.value} needs exactly {expected} topic ids, got {len(self.topic_ids)}")
        if len(set(self.topic_ids)) != expected:
            raise ValueError("Bell Tasks topic ids must all be distinct")
        return self


class PracticeTestSummary(BaseModel):
    id: str
    name: str
    tier: TierEnum
    sitting_id: str
    paper_number: int
    calculator_allowed: bool
    total_marks: int
    question_count: int
