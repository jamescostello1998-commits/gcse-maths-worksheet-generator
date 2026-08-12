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
    # For topics where every question repeats the same instruction (e.g. "Is
    # the following an expression, equation, formula, or identity?"), a
    # generator sets `shared_instruction` (the common stem) and `item_text`
    # (just this question's bare item). `prompt` stays the full self-contained
    # form for contexts that never hoist (Practice Tests' mixed papers, the
    # modelled-example page). A single-topic worksheet then shows the
    # instruction once at the top and just `item_text` per question - see
    # app/worksheet/builder.py and app/pdf/renderer.py.
    shared_instruction: Optional[str] = None
    item_text: Optional[str] = None


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
    preamble_lines: tuple[str, ...] = ()
    # Set by the builder when every question shares the same non-empty
    # `shared_instruction` (and carries an `item_text`): the renderers then
    # show this once at the top of the page and render just each question's
    # bare `item_text`, instead of repeating the instruction on every line.
    shared_instruction: Optional[str] = None
