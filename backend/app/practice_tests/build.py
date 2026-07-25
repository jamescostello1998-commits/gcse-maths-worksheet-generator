"""One-time assembly script for the 20 fixed practice papers. Not run at
request time - run manually (`python -m app.practice_tests.build`), the
output JSON files are committed to the repo as static content. Re-running
this script reproduces byte-identical output, since every seed is derived
deterministically from (paper_id, topic_id) via SHA-256 (never Python's
built-in `hash()`, which is randomised per-process for strings).
"""

import hashlib
import json
import random
from pathlib import Path

from app.core.models import Tier
from app.practice_tests.mark_scheme import build_mark_scheme
from app.practice_tests.models import PracticeQuestion, PracticeTestPaper, paper_to_dict
from app.practice_tests.topic_selection import eligible_topics_by_section, select_paper_topics, typical_marks_for
from app.topics.base import TopicDefinition

DATA_DIR = Path(__file__).parent / "data"
PAPERS_PER_TIER = 10
TARGET_MARKS = 100
MAX_REPAIR_ATTEMPTS = 300


def _seed(*parts: str) -> int:
    digest = hashlib.sha256("|".join(parts).encode()).digest()
    return int.from_bytes(digest[:8], "big")


def _paper_id(tier: Tier, index: int) -> str:
    return f"{tier.value}-{index:02d}"


def _paper_name(tier: Tier, index: int) -> str:
    return f"{tier.value.title()} Practice Test {index}"


def _build_practice_question(topic: TopicDefinition, seed: int) -> PracticeQuestion:
    question = topic.generate(topic.fixed_tier, random.Random(seed))
    marks, mark_scheme = build_mark_scheme(question.solution_steps, question.final_answer)
    return PracticeQuestion(
        topic_id=topic.id,
        prompt=question.prompt,
        solution_steps=question.solution_steps,
        final_answer=question.final_answer,
        marks=marks,
        mark_scheme=mark_scheme,
        diagram=question.diagram,
        solution_diagram=question.solution_diagram,
    )


def _repair_to_target(
    paper_id: str,
    questions: list[PracticeQuestion],
    chosen_topics: list[TopicDefinition],
    by_section: dict[str, list[TopicDefinition]],
    typical_marks: dict[str, int],
) -> list[PracticeQuestion]:
    """A handful of topics have branch-dependent solution_steps length (see
    CLAUDE.md), so the REAL marks total occasionally drifts by 1-2 from the
    "typical" total topic_selection planned against. Swap one slot at a time
    for an alternate, not-yet-used topic whose typical marks would close the
    gap exactly, until the real total lands on TARGET_MARKS."""
    used_ids = {t.id for t in chosen_topics}
    rng = random.Random(_seed("repair", paper_id))
    attempt = 0
    while sum(q.marks for q in questions) != TARGET_MARKS and attempt < MAX_REPAIR_ATTEMPTS:
        attempt += 1
        gap = TARGET_MARKS - sum(q.marks for q in questions)
        idx = rng.randrange(len(questions))
        needed = questions[idx].marks + gap
        if needed < 1:
            continue
        candidates = [
            t
            for topics in by_section.values()
            for t in topics
            if t.id not in used_ids and typical_marks[t.id] == needed
        ]
        if candidates:
            replacement = rng.choice(candidates)
            used_ids.discard(chosen_topics[idx].id)
            used_ids.add(replacement.id)
            questions[idx] = _build_practice_question(replacement, _seed("question", paper_id, replacement.id))
            chosen_topics[idx] = replacement
    return questions


MAX_PAPER_RETRIES = 20


def _assemble_paper(
    tier: Tier,
    index: int,
    by_section: dict[str, list[TopicDefinition]],
    typical_marks: dict[str, int],
) -> PracticeTestPaper:
    base_paper_id = _paper_id(tier, index)
    last_error: Exception | None = None
    for retry in range(MAX_PAPER_RETRIES):
        seed_key = base_paper_id if retry == 0 else f"{base_paper_id}#retry{retry}"
        try:
            return _try_assemble_paper(tier, index, base_paper_id, seed_key, by_section, typical_marks)
        except ValueError as exc:
            last_error = exc
            continue
    raise ValueError(f"Could not assemble {base_paper_id} after {MAX_PAPER_RETRIES} retries: {last_error}")


def _try_assemble_paper(
    tier: Tier,
    index: int,
    paper_id: str,
    seed_key: str,
    by_section: dict[str, list[TopicDefinition]],
    typical_marks: dict[str, int],
) -> PracticeTestPaper:
    selection_rng = random.Random(_seed("select", seed_key))
    chosen_topics = list(select_paper_topics(tier, selection_rng, typical_marks, by_section))

    questions = [
        _build_practice_question(topic, _seed("question", seed_key, topic.id)) for topic in chosen_topics
    ]
    questions = _repair_to_target(seed_key, questions, chosen_topics, by_section, typical_marks)

    total = sum(q.marks for q in questions)
    if total != TARGET_MARKS:
        raise ValueError(f"Paper {paper_id} settled at {total} marks, not {TARGET_MARKS}")

    return PracticeTestPaper(id=paper_id, name=_paper_name(tier, index), tier=tier, questions=tuple(questions))


def _typical_marks_for_tier(tier: Tier, by_section: dict[str, list[TopicDefinition]]) -> dict[str, int]:
    typical_marks: dict[str, int] = {}
    for topics in by_section.values():
        for topic in topics:
            sample_rng = random.Random(_seed("typical", topic.id))
            typical_marks[topic.id] = typical_marks_for(topic, sample_rng)
    return typical_marks


def build_papers(paper_ids: list[str] | None = None) -> list[PracticeTestPaper]:
    """Build the given paper ids (e.g. ["foundation-01", "higher-01"]), or
    all 20 if omitted. Does not write to disk - see main()/write_papers()."""
    papers: list[PracticeTestPaper] = []
    for tier in (Tier.FOUNDATION, Tier.HIGHER):
        by_section = eligible_topics_by_section(tier)
        typical_marks = _typical_marks_for_tier(tier, by_section)
        for index in range(1, PAPERS_PER_TIER + 1):
            pid = _paper_id(tier, index)
            if paper_ids is not None and pid not in paper_ids:
                continue
            papers.append(_assemble_paper(tier, index, by_section, typical_marks))
    return papers


def write_papers(papers: list[PracticeTestPaper]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for paper in papers:
        path = DATA_DIR / f"{paper.id}.json"
        path.write_text(json.dumps(paper_to_dict(paper), indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    papers = build_papers()
    write_papers(papers)
    for paper in papers:
        print(f"{paper.id}: {len(paper.questions)} questions, {paper.total_marks} marks")


if __name__ == "__main__":
    main()
