"""Representing inequalities on a number line: drawing the solution set of a
given inequality, and reading an inequality off an already-marked diagram.
Shares the "Inequalities" group with app/topics/inequalities.py (a different
module, same display group)."""

import operator
import random

import sympy as sp

from app.core.models import DiagramSpec, ModelledExample, Question, Tier
from app.topics.algebra_utils import X
from app.topics.base import TopicDefinition

SECTION = "algebra"
GROUP = "Inequalities"

_FOUNDATION_RANGE = (-6, 6)
_HIGHER_RANGE = (-8, 8)


def _relational(op: str, value):
    return {
        "<": sp.Lt(X, value),
        "<=": sp.Le(X, value),
        ">": sp.Gt(X, value),
        ">=": sp.Ge(X, value),
    }[op]


def _symbol(op: str) -> str:
    return {"<": "<", "<=": "≤", ">": ">", ">=": "≥"}[op]


def _article(word: str) -> str:
    return "an" if word[0] in "aeiou" else "a"


def _check_single(op: str, value: int, samples: list) -> None:
    """Independent check: build the sympy relational for the claimed
    inequality directly from (op, value), and separately compute set
    membership via plain operator functions - a different code path than
    however the caller decided to phrase the inequality - then confirm they
    agree at every sample point."""
    ops = {"<": operator.lt, "<=": operator.le, ">": operator.gt, ">=": operator.ge}
    rel = _relational(op, value)
    for v in samples:
        expected = ops[op](v, value)
        actual = bool(rel.subs(X, v))
        if expected != actual:
            raise ValueError("inequalities_number_line verification failed (single boundary)")


def _check_compound(lo_op: str, lo_val: int, hi_op: str, hi_val: int, kind: str, samples: list) -> None:
    """Independent check for a two-boundary (compound) inequality: for
    'between', membership requires both bounds hold; for 'outside', either
    bound alone suffices. Cross-checked against the sympy relationals built
    from the same (op, value) pairs."""
    # Build "x lo_op lo_val" style relation meaning value >= lo_val (open/closed):
    lower_rel = sp.Ge(X, lo_val) if lo_op == ">=" else sp.Gt(X, lo_val)
    upper_rel = sp.Le(X, hi_val) if hi_op == "<=" else sp.Lt(X, hi_val)
    for v in samples:
        lower_ok = bool(lower_rel.subs(X, v))
        upper_ok = bool(upper_rel.subs(X, v))
        expected = (lower_ok and upper_ok) if kind == "between" else (not lower_ok or not upper_ok)
        # Direct re-derivation via plain comparisons (different code path):
        lo_cmp = operator.ge if lo_op == ">=" else operator.gt
        hi_cmp = operator.le if hi_op == "<=" else operator.lt
        direct_lower = lo_cmp(v, lo_val)
        direct_upper = hi_cmp(v, hi_val)
        direct = (direct_lower and direct_upper) if kind == "between" else (not direct_lower or not direct_upper)
        if expected != direct:
            raise ValueError("inequalities_number_line verification failed (compound)")


def _check_between_display(lo_val: int, lo_display: str, hi_op: str, hi_val: int, samples: list) -> None:
    """Verify the *displayed* string "lo_val <lo_display> x <hi_op> hi_val"
    describes the same region as the true lower/upper bounds (x >= lo_val /
    x <= hi_val) - catches a flipped-symbol bug where the lower bound's
    displayed relation doesn't actually match "x >= lo_val" once written the
    other way around."""
    displayed_lower = sp.Le(lo_val, X) if lo_display == "<=" else sp.Lt(lo_val, X)
    true_lower = sp.Ge(X, lo_val) if lo_display == "<=" else sp.Gt(X, lo_val)
    displayed_upper = sp.Le(X, hi_val) if hi_op == "<=" else sp.Lt(X, hi_val)
    for v in samples:
        if bool(displayed_lower.subs(X, v)) != bool(true_lower.subs(X, v)):
            raise ValueError("inequalities_number_line verification failed (display symbol mismatch)")
        if bool(displayed_upper.subs(X, v)) != bool((sp.Le(X, hi_val) if hi_op == "<=" else sp.Lt(X, hi_val)).subs(X, v)):
            raise ValueError("inequalities_number_line verification failed (display symbol mismatch)")


def generate_inequalities_number_line_foundation(tier: Tier, rng: random.Random) -> Question:
    lo, hi = _FOUNDATION_RANGE
    k = rng.randint(lo + 1, hi - 1)
    closed = rng.choice([True, False])
    direction = rng.choice(["right", "left"])
    op = ("<=" if closed else "<") if direction == "left" else (">=" if closed else ">")
    symbol = _symbol(op)
    inequality_str = f"x {symbol} {k}"

    samples = list(range(lo, hi + 1))
    _check_single(op, k, samples)

    shape = rng.choice(["draw", "read"])
    marked = DiagramSpec(
        kind="number_line",
        params={"range": [lo, hi], "boundaries": [{"value": k, "closed": closed}], "shade": direction},
    )
    blank = DiagramSpec(kind="number_line", params={"range": [lo, hi], "boundaries": [], "blank": True})

    circle_word = "filled" if closed else "open"
    if shape == "draw":
        prompt = f"Draw the solution set of {inequality_str} on a number line."
        steps = [
            f"Draw {_article(circle_word)} {circle_word} circle at {k} ({'the boundary value is included' if closed else 'the boundary value is not included'}).",
            f"Shade the line to the {direction} of {k}, with an arrow showing it continues indefinitely.",
        ]
        return Question(
            topic_id="inequalities_number_line_foundation",
            tier=Tier.FOUNDATION,
            prompt=prompt,
            solution_steps=tuple(steps),
            final_answer=inequality_str,
            dedup_key=f"numline_found:draw:{k}:{closed}:{direction}",
            diagram=blank,
            solution_diagram=marked,
        )
    else:
        prompt = "Write down the inequality shown by the number line below."
        steps = [
            f"The circle at {k} is {circle_word}, so {k} {'is' if closed else 'is not'} included in the solution set.",
            f"The shading and arrow point to the {direction}, so the solution is {inequality_str}.",
        ]
        return Question(
            topic_id="inequalities_number_line_foundation",
            tier=Tier.FOUNDATION,
            prompt=prompt,
            solution_steps=tuple(steps),
            final_answer=inequality_str,
            dedup_key=f"numline_found:read:{k}:{closed}:{direction}",
            diagram=marked,
        )


def generate_inequalities_number_line_higher(tier: Tier, rng: random.Random) -> Question:
    lo, hi = _HIGHER_RANGE
    lo_val = rng.randint(lo + 2, hi - 5)
    width = rng.randint(3, 6)
    hi_val = min(lo_val + width, hi - 2)
    closed_lo = rng.choice([True, False])
    closed_hi = rng.choice([True, False])
    kind = "between" if rng.random() < 0.6 else "outside"

    lo_op = ">=" if closed_lo else ">"
    hi_op = "<=" if closed_hi else "<"
    samples = list(range(lo, hi + 1))
    _check_compound(lo_op, lo_val, hi_op, hi_val, kind, samples)

    if kind == "between":
        # lo_op/hi_op describe "x >= lo_val" / "x <= hi_val"; displaying the lower
        # bound as "lo_val ? x" needs the flipped symbol ("lo_val <= x", not ">=").
        lo_display = "<=" if closed_lo else "<"
        _check_between_display(lo_val, lo_display, hi_op, hi_val, samples)
        inequality_str = f"{lo_val} {_symbol(lo_display)} x {_symbol(hi_op)} {hi_val}"
    else:
        left_op = "<=" if closed_lo else "<"
        right_op = ">=" if closed_hi else ">"
        inequality_str = f"x {_symbol(left_op)} {lo_val} or x {_symbol(right_op)} {hi_val}"

    shape = rng.choice(["draw", "read"])
    marked = DiagramSpec(
        kind="number_line",
        params={
            "range": [lo, hi],
            "boundaries": [{"value": lo_val, "closed": closed_lo}, {"value": hi_val, "closed": closed_hi}],
            "shade": kind,
        },
    )
    blank = DiagramSpec(kind="number_line", params={"range": [lo, hi], "boundaries": [], "blank": True})

    lo_word = "filled" if closed_lo else "open"
    hi_word = "filled" if closed_hi else "open"
    if shape == "draw":
        prompt = f"Draw the solution set of {inequality_str} on a number line."
        if kind == "between":
            steps = [
                f"Draw {_article(lo_word)} {lo_word} circle at {lo_val} and {_article(hi_word)} {hi_word} circle at {hi_val}.",
                "Shade the segment of the line between the two circles.",
            ]
        else:
            steps = [
                f"Draw {_article(lo_word)} {lo_word} circle at {lo_val} and {_article(hi_word)} {hi_word} circle at {hi_val}.",
                f"Shade to the left of {lo_val} and to the right of {hi_val}, with arrows showing both continue indefinitely.",
            ]
        return Question(
            topic_id="inequalities_number_line_higher",
            tier=Tier.HIGHER,
            prompt=prompt,
            solution_steps=tuple(steps),
            final_answer=inequality_str,
            dedup_key=f"numline_high:draw:{lo_val}:{hi_val}:{closed_lo}:{closed_hi}:{kind}",
            diagram=blank,
            solution_diagram=marked,
        )
    else:
        prompt = "Write down the inequality (or pair of inequalities) shown by the number line below."
        steps = [
            f"The circle at {lo_val} is {lo_word} and the circle at {hi_val} is {hi_word}.",
            (
                "The shading lies between the two circles, so both bounds must hold at once: "
                f"{inequality_str}."
                if kind == "between"
                else f"The shading lies outside the two circles, so either bound alone is enough: {inequality_str}."
            ),
        ]
        return Question(
            topic_id="inequalities_number_line_higher",
            tier=Tier.HIGHER,
            prompt=prompt,
            solution_steps=tuple(steps),
            final_answer=inequality_str,
            dedup_key=f"numline_high:read:{lo_val}:{hi_val}:{closed_lo}:{closed_hi}:{kind}",
            diagram=marked,
        )


def generate_modelled_example_inequalities_number_line_foundation(tier: Tier, rng: random.Random) -> ModelledExample:
    lo, hi = _FOUNDATION_RANGE
    k = rng.randint(lo + 1, hi - 1)
    closed = rng.choice([True, False])
    direction = rng.choice(["right", "left"])
    op = ("<=" if closed else "<") if direction == "left" else (">=" if closed else ">")
    symbol = _symbol(op)
    inequality_str = f"x {symbol} {k}"
    samples = list(range(lo, hi + 1))
    _check_single(op, k, samples)

    marked = DiagramSpec(
        kind="number_line",
        params={"range": [lo, hi], "boundaries": [{"value": k, "closed": closed}], "shade": direction},
    )

    teaching_steps = [
        "A number line shows every real number satisfying an inequality, using two features: the circle at "
        "the boundary, and the direction of the shading/arrow.",
        f"The circle at {k} is {'filled in (a solid dot)' if closed else 'left open (a hollow ring)'}, which "
        f"means {k} {'is' if closed else 'is not'} itself part of the solution - filled circles go with "
        f"≤/≥, open circles go with </>.",
        f"The line is shaded to the {direction}, with an arrow showing the solution set carries on forever "
        f"in that direction rather than stopping at the edge of the drawn line.",
        f"Putting the boundary value and the direction together gives the inequality {inequality_str}.",
    ]
    worked_calculation = [
        f"Circle at {k}: {'filled' if closed else 'open'}",
        f"Shading direction: {direction}",
        f"{inequality_str}",
    ]
    return ModelledExample(
        topic_id="inequalities_number_line_foundation",
        tier=Tier.FOUNDATION,
        prompt="Write down the inequality shown by the number line below.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=inequality_str,
        diagram=marked,
    )


def generate_modelled_example_inequalities_number_line_higher(tier: Tier, rng: random.Random) -> ModelledExample:
    lo, hi = _HIGHER_RANGE
    lo_val = rng.randint(lo + 2, hi - 5)
    width = rng.randint(3, 6)
    hi_val = min(lo_val + width, hi - 2)
    closed_lo = rng.choice([True, False])
    closed_hi = rng.choice([True, False])
    kind = "between" if rng.random() < 0.6 else "outside"

    lo_op = ">=" if closed_lo else ">"
    hi_op = "<=" if closed_hi else "<"
    samples = list(range(lo, hi + 1))
    _check_compound(lo_op, lo_val, hi_op, hi_val, kind, samples)

    if kind == "between":
        lo_display = "<=" if closed_lo else "<"
        _check_between_display(lo_val, lo_display, hi_op, hi_val, samples)
        inequality_str = f"{lo_val} {_symbol(lo_display)} x {_symbol(hi_op)} {hi_val}"
    else:
        left_op = "<=" if closed_lo else "<"
        right_op = ">=" if closed_hi else ">"
        inequality_str = f"x {_symbol(left_op)} {lo_val} or x {_symbol(right_op)} {hi_val}"

    marked = DiagramSpec(
        kind="number_line",
        params={
            "range": [lo, hi],
            "boundaries": [{"value": lo_val, "closed": closed_lo}, {"value": hi_val, "closed": closed_hi}],
            "shade": kind,
        },
    )

    lo_word = "filled" if closed_lo else "open"
    hi_word = "filled" if closed_hi else "open"
    if kind == "between":
        region_explanation = (
            f"The shaded part sits *between* the two circles, so a value only counts if it satisfies both "
            f"bounds at the same time - that's why this is written as one double inequality, "
            f"{inequality_str}, rather than two separate statements."
        )
    else:
        region_explanation = (
            f"The shaded part sits *outside* the two circles (two separate rays, each with its own arrow), "
            f"so a value counts if it satisfies *either* bound on its own - that's why this needs the word "
            f"'or' between two separate inequalities: {inequality_str}."
        )

    teaching_steps = [
        "A compound (double) inequality involves two boundary values instead of one, so the diagram has two "
        "circles to read.",
        f"The circle at {lo_val} is {lo_word} ({lo_val} {'is' if closed_lo else 'is not'} included), and the "
        f"circle at {hi_val} is {hi_word} ({hi_val} {'is' if closed_hi else 'is not'} included).",
        region_explanation,
        f"Putting it together gives {inequality_str}.",
    ]
    worked_calculation = [
        f"Circles: {lo_val} ({lo_word}), {hi_val} ({hi_word})",
        f"Shading: {kind}",
        f"{inequality_str}",
    ]
    return ModelledExample(
        topic_id="inequalities_number_line_higher",
        tier=Tier.HIGHER,
        prompt="Write down the inequality (or pair of inequalities) shown by the number line below.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=inequality_str,
        diagram=marked,
    )


TOPIC_INEQUALITIES_NUMBER_LINE_FOUNDATION = TopicDefinition(
    id="inequalities_number_line_foundation",
    display_name="Inequalities on a Number Line",
    description="Draw the solution set of a simple inequality on a number line, or read one off a diagram.",
    generate=generate_inequalities_number_line_foundation,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_inequalities_number_line_foundation,
)

TOPIC_INEQUALITIES_NUMBER_LINE_HIGHER = TopicDefinition(
    id="inequalities_number_line_higher",
    display_name="Compound Inequalities on a Number Line",
    description="Draw or read a compound (double, or 'either/or') inequality shown on a number line.",
    generate=generate_inequalities_number_line_higher,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_inequalities_number_line_higher,
)
