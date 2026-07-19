from enum import Enum

from pydantic import BaseModel


class TierEnum(str, Enum):
    foundation = "foundation"
    higher = "higher"


class TopicSummary(BaseModel):
    id: str
    name: str
    description: str


class GenerateWorksheetRequest(BaseModel):
    topic_id: str
    tier: TierEnum
