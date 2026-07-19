from enum import Enum
from typing import Optional

from pydantic import BaseModel


class TierEnum(str, Enum):
    foundation = "foundation"
    higher = "higher"


class TopicSummary(BaseModel):
    id: str
    name: str
    description: str
    fixed_tier: Optional[TierEnum] = None


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
