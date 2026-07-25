"""Data model for the fixed/static Practice Tests feature - deliberately
separate from app/core/models.py's Question/TopicDefinition (which back the
232 procedurally-generated topics) since a PracticeQuestion is a frozen
snapshot plus an OCR-style mark breakdown that no ordinary Question carries.
"""

from dataclasses import dataclass
from typing import Optional

from app.core.models import DiagramSpec, Tier


@dataclass(frozen=True)
class MarkPoint:
    """One OCR-style marking point, e.g. ("M1", "10 × 0.2 = 2", 1)."""

    code: str
    description: str
    marks: int


@dataclass(frozen=True)
class PracticeQuestion:
    topic_id: str
    prompt: str
    solution_steps: tuple[str, ...]
    final_answer: str
    marks: int
    mark_scheme: tuple[MarkPoint, ...]
    diagram: Optional[DiagramSpec] = None
    solution_diagram: Optional[DiagramSpec] = None


@dataclass(frozen=True)
class PracticeTestPaper:
    id: str
    name: str
    tier: Tier
    questions: tuple[PracticeQuestion, ...]

    @property
    def total_marks(self) -> int:
        return sum(q.marks for q in self.questions)


def _diagram_to_dict(spec: Optional[DiagramSpec]) -> Optional[dict]:
    return None if spec is None else {"kind": spec.kind, "params": spec.params}


def _diagram_from_dict(data: Optional[dict]) -> Optional[DiagramSpec]:
    return None if data is None else DiagramSpec(kind=data["kind"], params=data["params"])


def paper_to_dict(paper: PracticeTestPaper) -> dict:
    """JSON-safe serialization, used by build.py when writing frozen papers
    and mirrored by paper_from_dict for loader.py to read them back."""
    return {
        "id": paper.id,
        "name": paper.name,
        "tier": paper.tier.value,
        "questions": [
            {
                "topic_id": q.topic_id,
                "prompt": q.prompt,
                "solution_steps": list(q.solution_steps),
                "final_answer": q.final_answer,
                "marks": q.marks,
                "mark_scheme": [
                    {"code": p.code, "description": p.description, "marks": p.marks} for p in q.mark_scheme
                ],
                "diagram": _diagram_to_dict(q.diagram),
                "solution_diagram": _diagram_to_dict(q.solution_diagram),
            }
            for q in paper.questions
        ],
    }


def paper_from_dict(data: dict) -> PracticeTestPaper:
    questions = tuple(
        PracticeQuestion(
            topic_id=q["topic_id"],
            prompt=q["prompt"],
            solution_steps=tuple(q["solution_steps"]),
            final_answer=q["final_answer"],
            marks=q["marks"],
            mark_scheme=tuple(MarkPoint(code=p["code"], description=p["description"], marks=p["marks"]) for p in q["mark_scheme"]),
            diagram=_diagram_from_dict(q["diagram"]),
            solution_diagram=_diagram_from_dict(q["solution_diagram"]),
        )
        for q in data["questions"]
    )
    return PracticeTestPaper(id=data["id"], name=data["name"], tier=Tier(data["tier"]), questions=questions)
