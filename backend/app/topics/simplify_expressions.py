"""Simplify an algebraic expression by collecting like terms.

A core Foundation skill (e.g. 5x + 3x - 2x -> 6x, or 3a + 2b + 5a - b ->
8a + b). The answer is built by summing the coefficients of each like term
directly, then independently verified with sympy (expand the original minus
the answer and confirm it is identically zero) - a genuinely different code
path than the coefficient bookkeeping that builds the displayed answer.
"""

import random

import sympy as sp

from app.core.models import ModelledExample, Question, Tier
from app.topics.base import TopicDefinition
from app.topics.phrasing import simplify_verb

SECTION = "algebra"
GROUP = "Expressions, Formulae, Equations & Identities"

# Sympy symbols for the independent verification path only (never for building
# the displayed strings). "a"/"b" are drawn upright by mathtext.py (only x/n
# are italicised), so a two-variable question stays visually consistent using
# a and b, while single-variable questions use x.
_X, _A, _B = sp.symbols("x a b")

# Canonical display order for the collected answer.
_TERM_ORDER = ["x^2", "x", "a", "b", ""]

_SYM_EXPR = {"x^2": _X**2, "x": _X, "a": _A, "b": _B, "": sp.Integer(1)}


def _fmt_terms(terms: list[tuple[int, str]]) -> str:
    """Render an ordered list of (coefficient, symbol) terms as a string,
    e.g. [(3,'x^2'),(-2,'x'),(5,'')] -> '3x^2 - 2x + 5'. Skips zero terms,
    omits a coefficient of 1/-1 on a lettered term."""
    parts: list[str] = []
    for coeff, sym in terms:
        if coeff == 0:
            continue
        if not parts:
            if sym == "":
                parts.append(str(coeff))
            elif coeff == 1:
                parts.append(sym)
            elif coeff == -1:
                parts.append(f"-{sym}")
            else:
                parts.append(f"{coeff}{sym}")
        else:
            sign = "+" if coeff > 0 else "-"
            mag = abs(coeff)
            if sym == "":
                parts.append(f"{sign} {mag}")
            elif mag == 1:
                parts.append(f"{sign} {sym}")
            else:
                parts.append(f"{sign} {mag}{sym}")
    return " ".join(parts) if parts else "0"


def _expr_of(terms: list[tuple[int, str]]):
    total = sp.Integer(0)
    for coeff, sym in terms:
        total += coeff * _SYM_EXPR[sym]
    return total


def _nonzero(rng: random.Random, lo: int, hi: int) -> int:
    while True:
        v = rng.randint(lo, hi)
        if v != 0:
            return v


def _build(rng: random.Random) -> tuple[str, str, str, str]:
    """Return (prompt_expr, answer, shape, dedup_extra)."""
    shape = rng.choice(["single_var", "single_var_const", "two_var", "with_square"])

    # raw_terms: the shuffled terms as they appear in the question.
    if shape == "single_var":
        raw = [(_nonzero(rng, -9, 9), "x") for _ in range(rng.randint(3, 4))]
    elif shape == "single_var_const":
        raw = [(_nonzero(rng, -8, 8), "x") for _ in range(rng.randint(2, 3))]
        raw += [(_nonzero(rng, -9, 9), "") for _ in range(rng.randint(2, 3))]
    elif shape == "two_var":
        raw = [(_nonzero(rng, -8, 8), "a") for _ in range(2)]
        raw += [(_nonzero(rng, -8, 8), "b") for _ in range(2)]
        if rng.random() < 0.4:
            raw.append((_nonzero(rng, -6, 6), "a"))
    else:  # with_square
        raw = [(_nonzero(rng, -6, 6), "x^2") for _ in range(2)]
        raw += [(_nonzero(rng, -8, 8), "x") for _ in range(2)]
        if rng.random() < 0.5:
            raw.append((_nonzero(rng, -9, 9), ""))

    rng.shuffle(raw)

    # Collected answer: sum coefficients per symbol (the primary computation).
    combined: dict[str, int] = {}
    for coeff, sym in raw:
        combined[sym] = combined.get(sym, 0) + coeff
    answer_terms = [(combined.get(sym, 0), sym) for sym in _TERM_ORDER]

    prompt_expr = _fmt_terms(raw)
    answer = _fmt_terms(answer_terms)

    # Reject a degenerate everything-cancels answer, and a prompt that has no
    # like terms to collect at all (would already be simplified).
    if answer == "0":
        raise ValueError("collect_like_terms: answer collapsed to 0")
    syms_present = [s for _, s in raw]
    if all(syms_present.count(s) <= 1 for s in set(syms_present)):
        raise ValueError("collect_like_terms: nothing to collect")

    # Independent verification: expand (original - answer) via sympy and
    # confirm it is identically zero for all variables.
    residual = sp.expand(_expr_of(raw) - _expr_of(answer_terms))
    if residual != 0:
        raise ValueError("collect_like_terms verification failed")

    extra = "|".join(f"{c}{s}" for c, s in raw)
    return prompt_expr, answer, shape, extra


def _steps(prompt_expr: str, answer: str, shape: str) -> list[str]:
    what = {
        "single_var": "the x terms",
        "single_var_const": "the x terms, and separately the number terms",
        "two_var": "the a terms, and separately the b terms",
        "with_square": "the x^2 terms, the x terms, and any number terms",
    }[shape]
    return [
        f"Start with the expression: {prompt_expr}.",
        f"Like terms have exactly the same letter part, so group {what} together, "
        "keeping the + or - sign in front of each term.",
        "Add the coefficients within each group (a term with no number in front counts as 1).",
        f"This simplifies to {answer}.",
    ]


def generate_collect_like_terms(tier: Tier, rng: random.Random) -> Question:
    for _ in range(60):
        try:
            prompt_expr, answer, shape, extra = _build(rng)
            break
        except ValueError:
            continue
    else:
        raise ValueError("collect_like_terms could not build a valid question")

    return Question(
        topic_id="collect_like_terms_F",
        tier=Tier.FOUNDATION,
        prompt=f"{simplify_verb(rng)} {prompt_expr}",
        solution_steps=tuple(_steps(prompt_expr, answer, shape)),
        final_answer=answer,
        dedup_key=f"collect:{shape}:{extra}",
    )


def generate_modelled_example_collect_like_terms(tier: Tier, rng: random.Random) -> ModelledExample:
    for _ in range(60):
        try:
            prompt_expr, answer, shape, _ = _build(rng)
            break
        except ValueError:
            continue
    else:
        raise ValueError("collect_like_terms modelled example could not build a valid question")

    teaching_steps = [
        f"The expression is {prompt_expr}. \"Simplifying by collecting like terms\" means grouping "
        "together the terms that share exactly the same letter part, then combining each group into "
        "a single term - it does not change the value of the expression, just tidies it up.",
        "First, decide which terms are 'like'. Terms are like each other only if their letter part "
        "matches exactly: x and x are like, x^2 and x are NOT like, and plain numbers are like each "
        "other. A useful trick is to keep the + or - sign attached to the term it sits in front of.",
        "Now add the coefficients within each group. Remember a lone letter such as x really means "
        "1x, and -x means -1x, so those count as +1 and -1 when you total a group up.",
        f"Writing each combined group back out gives the fully simplified expression: {answer}.",
    ]
    worked_calculation = [prompt_expr, "Group and add like terms", f"= {answer}"]
    return ModelledExample(
        topic_id="collect_like_terms_F",
        tier=Tier.FOUNDATION,
        prompt=f"Simplify {prompt_expr} by collecting like terms.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
    )


TOPIC_COLLECT_LIKE_TERMS = TopicDefinition(
    id="collect_like_terms_F",
    display_name="Collecting Like Terms",
    description="Simplify an algebraic expression by collecting like terms.",
    generate=generate_collect_like_terms,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_collect_like_terms,
)
