from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class Tier(str, Enum):
    FOUNDATION = "foundation"
    HIGHER = "higher"


@dataclass(frozen=True)
class Question:
    topic_id: str
    tier: Tier
    prompt: str
    solution_steps: tuple[str, ...]
    final_answer: str
    dedup_key: str


@dataclass(frozen=True)
class Worksheet:
    topic_id: str
    topic_name: str
    tier: Tier
    questions: tuple[Question, ...]
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
