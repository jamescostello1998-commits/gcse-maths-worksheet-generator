from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


class Tier(str, Enum):
    FOUNDATION = "foundation"
    HIGHER = "higher"


@dataclass(frozen=True)
class DiagramSpec:
    """A ReportLab-agnostic description of a figure to draw alongside a
    question. `params` holds plain JSON-ish values (numbers, strings, lists)
    consumed by the matching renderer in app/pdf/diagrams.py."""

    kind: str
    params: dict[str, Any]


@dataclass(frozen=True)
class Question:
    topic_id: str
    tier: Tier
    prompt: str
    solution_steps: tuple[str, ...]
    final_answer: str
    dedup_key: str
    diagram: Optional[DiagramSpec] = None
    solution_diagram: Optional[DiagramSpec] = None


@dataclass(frozen=True)
class ModelledExample:
    """A single, richly-narrated worked example for the 'modelled example'
    teaching page. `worked_calculation` is the terse line-by-line numeric
    working - shown boxed at the top of the page, right under the prompt, so
    the student can see the calculation in full before reading about it.
    `teaching_steps` are the prose explanation that follows underneath: read
    like a teacher talking through the reasoning, one idea per line, rather
    than just restating the numbers."""

    topic_id: str
    tier: Tier
    prompt: str
    worked_calculation: tuple[str, ...]
    teaching_steps: tuple[str, ...]
    final_answer: str
    diagram: Optional[DiagramSpec] = None


@dataclass(frozen=True)
class Worksheet:
    topic_id: str
    topic_name: str
    tier: Tier
    questions: tuple[Question, ...]
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
