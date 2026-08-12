import random
from dataclasses import replace
from datetime import datetime, timezone

from app.core.errors import WorksheetGenerationError
from app.core.models import Question, Tier, Worksheet
from app.core.registry import get_topic

DEFAULT_COUNT = 20
DEFAULT_MAX_ATTEMPTS = 400
MIN_COUNT = 5
MAX_COUNT = 40

# Topics where every question repeats the SAME leading instruction, mapped to
# that exact instruction string. On a single-topic worksheet the builder hoists
# it to one page-level header and shows each question's bare remainder
# (item_text) instead of repeating it - see app/pdf/renderer.py and
# app/docx/render.py. Fail-safe: a topic is only hoisted if EVERY question's
# prompt genuinely begins with this string and leaves a non-empty remainder
# (see _apply_shared_instruction); if a generator's wording ever drifts, the
# match fails and the full prompt is shown as before. Practice Tests (frozen,
# mixed papers) and modelled examples never pass through here, so they always
# keep the full self-contained prompt.
HOISTED_INSTRUCTIONS: dict[str, str] = {
    "classify_expressions_F": "Is the following an expression, equation, formula, or identity?",
    "prime_numbers_F": "From this list, write down all the prime numbers:",
    "lcm_by_listing_F": "Find the lowest common multiple (LCM) of",
    "hcf_by_listing_F": "Find the highest common factor (HCF) of",
    "hcf_lcm_by_prime_factors_H": "Using prime factorisation, find the",
    "expand_double_brackets_F": "Expand and simplify:",
    "expand_double_brackets_no_coefficient_F": "Expand and simplify:",
    "expand_double_brackets_H": "Expand and simplify:",
    "expand_triple_brackets_H": "Expand and simplify:",
    "expand_triple_brackets_no_coefficient_H": "Expand and simplify:",
    "change_subject_factorise_H": "Make x the subject of the formula",
    "simultaneous_common_coefficient_F": "Solve the simultaneous equations:",
    "simultaneous_different_coefficient_H": "Solve the simultaneous equations:",
    "simultaneous_quadratic_H": "Solve the simultaneous equations:",
    "solving_inequalities_F": "Solve the inequality:",
    "solving_inequalities_H": "Solve the inequality:",
    "quadratic_inequalities_H": "Solve the inequality:",
    "sequences_next_term_F": "Find the next term in the sequence:",
    "exact_trig_values_H": "Write down the exact value of",
    "stats_mean_F": "Find the mean of this data set:",
    "stats_mode_F": "Find the mode of this data set:",
    "stats_median_F": "Find the median of this data set:",
    "stats_range_F": "Find the range of this data set:",
    "fractional_equations_F": "Solve the following equation.",
    "fractional_equations_H": "Solve the following equation.",
    "cross_multiplication_F": "Solve the following equation.",
    "cross_multiplication_H": "Solve the following equation.",
    "fractional_equations_advanced_H": "Solve the following equation, giving your answers to 2 decimal places where necessary.",
}


def _apply_shared_instruction(topic_id: str, questions: list[Question]) -> tuple[list[Question], str | None]:
    """If this topic is in HOISTED_INSTRUCTIONS and every question's prompt
    starts with that instruction (leaving a non-empty remainder), return the
    questions rewritten with shared_instruction/item_text set, plus the shared
    instruction. Otherwise return them unchanged with None."""
    instr = HOISTED_INSTRUCTIONS.get(topic_id)
    if not instr:
        return questions, None
    items = [q.prompt[len(instr):].strip() if q.prompt.startswith(instr) else None for q in questions]
    if not all(items):
        return questions, None  # wording drifted - fall back to full prompts
    rewritten = [replace(q, shared_instruction=instr, item_text=item) for q, item in zip(questions, items)]
    return rewritten, instr


def build_worksheet(
    topic_id: str,
    tier: Tier,
    count: int = DEFAULT_COUNT,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    rng: random.Random | None = None,
) -> Worksheet:
    topic = get_topic(topic_id)
    rng = rng or random.Random()

    seen_keys: set[str] = set()
    questions: list[Question] = []
    attempts = 0

    while len(questions) < count and attempts < max_attempts:
        attempts += 1
        question = topic.generate(tier, rng)
        if question.dedup_key in seen_keys:
            continue
        seen_keys.add(question.dedup_key)
        questions.append(question)

    if len(questions) < count:
        raise WorksheetGenerationError(
            topic_id=topic_id,
            tier=tier.value,
            attempts=attempts,
            produced=len(questions),
        )

    questions, shared_instruction = _apply_shared_instruction(topic.id, questions)

    return Worksheet(
        topic_id=topic.id,
        topic_name=topic.display_name,
        tier=tier,
        questions=tuple(questions),
        generated_at=datetime.now(timezone.utc),
        preamble_lines=topic.preamble_lines or (),
        shared_instruction=shared_instruction,
    )
