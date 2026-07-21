"""Venn-diagram topics: shading a named region, reading probabilities off one,
formal set notation over one, and algebraic region counts that solve for x.

These are the diagram-bearing siblings of `data_handling.py`'s `set_notation`/
`set_notation_foundation` topics (which do the same union/intersection/
complement work on explicit number-list sets, but without any diagram).

Every generator constructs a `DiagramSpec(kind="venn_diagram", params={...})`
consumed by the already-built, already-tested `draw_venn_diagram` renderer in
`app/pdf/diagrams.py` - see that function's docstring for the exact params
contract (this file never touches diagrams.py itself). Region keys used
throughout: "a_only", "b_only", "both", "neither".
"""

import random
from fractions import Fraction

import sympy as sp

from app.core.models import DiagramSpec, ModelledExample, Question, Tier
from app.topics.base import TopicDefinition

SECTION = "probability"
GROUP = "Venn Diagrams"

_ALL_REGIONS = ("a_only", "b_only", "both", "neither")


# ---------------------------------------------------------------------------
# venn_diagram_shading (Foundation)
# ---------------------------------------------------------------------------

_LABEL_PAIRS = [("A", "B"), ("M", "N"), ("P", "Q"), ("X", "Y"), ("R", "T")]


def _pick_labels(rng: random.Random) -> tuple[str, str]:
    # Plain "A"/"B" is the common case (matches the plain-English phrasing
    # convention used elsewhere), but vary it sometimes for dedup-key variety
    # and so the topic isn't visually identical on every question.
    if rng.random() < 0.5:
        return "A", "B"
    return rng.choice(_LABEL_PAIRS[1:])

# Each entry: (key, phrase_template, answer_template, shade_list, predicate)
# `predicate(in_a, in_b) -> bool` independently defines which of the four
# atomic regions belong to this named region - used as a genuinely different
# derivation to cross-check the hardcoded `shade_list`, not a second copy of
# the same literal.
_REGION_DEFS = [
    (
        "A",
        "Shade the region that represents the elements in {a}.",
        "The region inside {a} (including where it overlaps {b}).",
        ["a_only", "both"],
        lambda a, b: a,
    ),
    (
        "B",
        "Shade the region that represents the elements in {b}.",
        "The region inside {b} (including where it overlaps {a}).",
        ["b_only", "both"],
        lambda a, b: b,
    ),
    (
        "intersection",
        "Shade the region that represents the elements in both {a} and {b}.",
        "The overlapping region of {a} and {b}.",
        ["both"],
        lambda a, b: a and b,
    ),
    (
        "union",
        "Shade the region that represents the elements in {a}, in {b}, or in both.",
        "The whole region covered by {a} and/or {b}.",
        ["a_only", "b_only", "both"],
        lambda a, b: a or b,
    ),
    (
        "A_only",
        "Shade the region that represents the elements in {a} but not in {b}.",
        "The region inside {a} only (not in {b}).",
        ["a_only"],
        lambda a, b: a and not b,
    ),
    (
        "B_only",
        "Shade the region that represents the elements in {b} but not in {a}.",
        "The region inside {b} only (not in {a}).",
        ["b_only"],
        lambda a, b: b and not a,
    ),
    (
        "not_A",
        "Shade the region that represents the elements not in {a}.",
        "The region outside {a} (everything that is not in {a}).",
        ["b_only", "neither"],
        lambda a, b: not a,
    ),
    (
        "not_B",
        "Shade the region that represents the elements not in {b}.",
        "The region outside {b} (everything that is not in {b}).",
        ["a_only", "neither"],
        lambda a, b: not b,
    ),
    (
        "neither",
        "Shade the region that represents the elements in neither {a} nor {b}.",
        "The region outside both {a} and {b}.",
        ["neither"],
        lambda a, b: (not a) and (not b),
    ),
    (
        "not_both",
        "Shade the region that represents the elements that are not in both {a} and {b} at the same time.",
        "Everywhere except the overlap of {a} and {b}.",
        ["a_only", "b_only", "neither"],
        lambda a, b: not (a and b),
    ),
]

_ATOM_MEMBERSHIP = {
    "a_only": (True, False),
    "b_only": (False, True),
    "both": (True, True),
    "neither": (False, False),
}


def _verify_shade_list(key: str, shade_list: list[str], predicate) -> None:
    # Independent check: rebuild the region set by evaluating the boolean
    # predicate over the four atomic (in_a, in_b) combinations - a different
    # method than trusting the hardcoded `shade_list` literal directly.
    derived = {atom for atom, (in_a, in_b) in _ATOM_MEMBERSHIP.items() if predicate(in_a, in_b)}
    if derived != set(shade_list):
        raise ValueError(f"venn_diagram_shading verification failed for region '{key}'")


def generate_venn_diagram_shading(tier: Tier, rng: random.Random) -> Question:
    a_label, b_label = _pick_labels(rng)
    key, phrase_template, answer_template, shade_list, predicate = rng.choice(_REGION_DEFS)
    _verify_shade_list(key, shade_list, predicate)

    prompt = phrase_template.format(a=a_label, b=b_label)
    final_answer = answer_template.format(a=a_label, b=b_label)

    steps = [
        f"The Venn diagram has two circles, {a_label} and {b_label}, inside a rectangle representing "
        "everything being considered.",
        f"'{prompt}' tells you which of the four regions (in {a_label} only, in {b_label} only, in "
        "both, or in neither) needs shading.",
        f"{final_answer}",
    ]
    return Question(
        topic_id="venn_diagram_shading",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=final_answer,
        dedup_key=f"venn_shade:{key}:{a_label}:{b_label}",
        diagram=DiagramSpec(kind="venn_diagram", params={"labels": [a_label, b_label]}),
        solution_diagram=DiagramSpec(
            kind="venn_diagram",
            params={"labels": [a_label, b_label], "shade": list(shade_list)},
        ),
    )


def generate_modelled_example_venn_diagram_shading(tier: Tier, rng: random.Random) -> ModelledExample:
    a_label, b_label = _pick_labels(rng)
    key, phrase_template, answer_template, shade_list, predicate = rng.choice(_REGION_DEFS)
    _verify_shade_list(key, shade_list, predicate)

    prompt = phrase_template.format(a=a_label, b=b_label)
    final_answer = answer_template.format(a=a_label, b=b_label)

    teaching_steps = [
        "A Venn diagram splits everything into four separate regions: inside the first circle only, "
        "inside the second circle only, inside both circles at once (the overlap), and inside neither "
        "(outside both circles but still inside the rectangle).",
        f"Read the instruction carefully - '{prompt}' - and work out which of those four regions it "
        "describes before shading anything.",
        f"Here, that means: {final_answer}",
        "Shade exactly that region and leave every other region blank - shading too much or too little "
        "is the most common mistake with these questions.",
    ]
    worked_calculation = [
        f"Instruction: {prompt}",
        f"Region to shade: {final_answer}",
    ]
    return ModelledExample(
        topic_id="venn_diagram_shading",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=final_answer,
        diagram=DiagramSpec(
            kind="venn_diagram",
            params={"labels": [a_label, b_label], "shade": list(shade_list)},
        ),
    )


# ---------------------------------------------------------------------------
# venn_diagram_probability (Foundation)
# ---------------------------------------------------------------------------

# Each entry: (key, regions, notation, complement_regions). `complement_regions`
# is written independently (not derived at runtime from `regions`) so it gives
# a genuinely separate cross-check of the numerator.
_PROB_EVENTS = [
    ("A", ["a_only", "both"], "A", ["b_only", "neither"]),
    ("B", ["b_only", "both"], "B", ["a_only", "neither"]),
    ("intersection", ["both"], "A ∩ B", ["a_only", "b_only", "neither"]),
    ("union", ["a_only", "b_only", "both"], "A ∪ B", ["neither"]),
    ("A_only", ["a_only"], "A only", ["b_only", "both", "neither"]),
    ("B_only", ["b_only"], "B only", ["a_only", "both", "neither"]),
    ("not_A", ["b_only", "neither"], "A'", ["a_only", "both"]),
    ("not_B", ["a_only", "neither"], "B'", ["b_only", "both"]),
    ("neither", ["neither"], "neither A nor B", ["a_only", "b_only", "both"]),
]


def _prob_counts(rng: random.Random) -> dict[str, int]:
    return {
        "a_only": rng.randint(2, 15),
        "b_only": rng.randint(2, 15),
        "both": rng.randint(2, 15),
        "neither": rng.randint(2, 15),
    }


def _verify_prob(counts: dict[str, int], total: int, regions: list[str], complement_regions: list[str]) -> Fraction:
    numerator = sum(counts[r] for r in regions)
    # Independent check: recompute the same numerator by subtracting the
    # complementary regions' total from the grand total - a different
    # arithmetic order/grouping than directly summing the target regions.
    numerator_check = total - sum(counts[r] for r in complement_regions)
    if numerator_check != numerator:
        raise ValueError("venn_diagram_probability verification failed")
    prob = Fraction(numerator, total)
    if Fraction(numerator_check, total) != prob:
        raise ValueError("venn_diagram_probability verification failed (fraction mismatch)")
    return prob


def generate_venn_diagram_probability(tier: Tier, rng: random.Random) -> Question:
    counts = _prob_counts(rng)
    total = sum(counts.values())
    event_key, regions, notation, complement_regions = rng.choice(_PROB_EVENTS)
    prob = _verify_prob(counts, total, regions, complement_regions)

    region_text = {k: str(v) for k, v in counts.items()}
    steps = [
        f"Total number of elements = {counts['a_only']} + {counts['b_only']} + {counts['both']} + "
        f"{counts['neither']} = {total}",
        f"Number of outcomes in {notation} = " + " + ".join(str(counts[r]) for r in regions)
        + f" = {sum(counts[r] for r in regions)}",
        f"P({notation}) = {sum(counts[r] for r in regions)}/{total} = {prob.numerator}/{prob.denominator}",
    ]
    prompt = (
        "The Venn diagram shows the number of students in each region for sets A and B. "
        f"Find P({notation})."
    )
    return Question(
        topic_id="venn_diagram_probability",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=f"{prob.numerator}/{prob.denominator}",
        dedup_key=f"venn_prob:{event_key}:{counts['a_only']}:{counts['b_only']}:{counts['both']}:{counts['neither']}",
        diagram=DiagramSpec(
            kind="venn_diagram", params={"labels": ["A", "B"], "region_text": region_text}
        ),
    )


def generate_modelled_example_venn_diagram_probability(tier: Tier, rng: random.Random) -> ModelledExample:
    counts = _prob_counts(rng)
    total = sum(counts.values())
    event_key, regions, notation, complement_regions = rng.choice(_PROB_EVENTS)
    prob = _verify_prob(counts, total, regions, complement_regions)
    numerator = sum(counts[r] for r in regions)

    region_text = {k: str(v) for k, v in counts.items()}
    teaching_steps = [
        "The four regions of a two-set Venn diagram give the number of outcomes in each part of the "
        "sample space - add every region together to get the total number of equally likely outcomes.",
        f"Here the total is {counts['a_only']} + {counts['b_only']} + {counts['both']} + "
        f"{counts['neither']} = {total}.",
        f"'{notation}' picks out one or more of those regions - work out which ones apply, then add "
        f"up just those counts: {numerator}.",
        f"Probability is always favourable outcomes over total outcomes, so P({notation}) = "
        f"{numerator}/{total}, which simplifies to {prob.numerator}/{prob.denominator}.",
    ]
    worked_calculation = [
        f"Total = {total}",
        f"Favourable ({notation}) = {numerator}",
        f"P({notation}) = {numerator}/{total} = {prob.numerator}/{prob.denominator}",
    ]
    prompt = (
        "The Venn diagram shows the number of students in each region for sets A and B. "
        f"Find P({notation})."
    )
    return ModelledExample(
        topic_id="venn_diagram_probability",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{prob.numerator}/{prob.denominator}",
        diagram=DiagramSpec(
            kind="venn_diagram", params={"labels": ["A", "B"], "region_text": region_text}
        ),
    )


# ---------------------------------------------------------------------------
# venn_diagram_notation (Higher)
# ---------------------------------------------------------------------------

# Each entry: (key, notation, description, predicate(in_a, in_b) -> bool)
_NOTATION_OPS = [
    ("set_a", "A", "the elements in A", lambda a, b: a),
    ("set_b", "B", "the elements in B", lambda a, b: b),
    ("union", "A ∪ B", "the elements in A, in B, or in both", lambda a, b: a or b),
    ("intersection", "A ∩ B", "the elements in both A and B", lambda a, b: a and b),
    ("complement_a", "A'", "the elements not in A", lambda a, b: not a),
    ("complement_b", "B'", "the elements not in B", lambda a, b: not b),
    ("complement_union", "(A ∪ B)'", "the elements in neither A nor B", lambda a, b: not (a or b)),
    (
        "complement_intersection",
        "(A ∩ B)'",
        "the elements that are not in both A and B at once",
        lambda a, b: not (a and b),
    ),
    ("a_and_not_b", "A ∩ B'", "the elements in A but not in B", lambda a, b: a and not b),
    ("b_and_not_a", "B ∩ A'", "the elements in B but not in A", lambda a, b: b and not a),
]


def _build_notation_sets(rng: random.Random) -> tuple[list[int], dict[str, list[int]], set[int], set[int]]:
    sizes = {r: rng.randint(1, 3) for r in _ALL_REGIONS}
    total_universal = sum(sizes.values())
    pool = list(range(1, total_universal + 1))
    rng.shuffle(pool)

    idx = 0
    region_elems: dict[str, list[int]] = {}
    for r in _ALL_REGIONS:
        n = sizes[r]
        region_elems[r] = sorted(pool[idx : idx + n])
        idx += n

    universal_sorted = sorted(pool)
    a_set = set(region_elems["a_only"]) | set(region_elems["both"])
    b_set = set(region_elems["b_only"]) | set(region_elems["both"])
    return universal_sorted, region_elems, a_set, b_set


def _resolve_notation_result(op_key: str, universal_sorted: list[int], a_set: set[int], b_set: set[int]) -> set[int]:
    if op_key == "set_a":
        return set(a_set)
    if op_key == "set_b":
        return set(b_set)
    if op_key == "union":
        return a_set | b_set
    if op_key == "intersection":
        return a_set & b_set
    if op_key == "complement_a":
        return set(universal_sorted) - a_set
    if op_key == "complement_b":
        return set(universal_sorted) - b_set
    if op_key == "complement_union":
        return set(universal_sorted) - (a_set | b_set)
    if op_key == "complement_intersection":
        return set(universal_sorted) - (a_set & b_set)
    if op_key == "a_and_not_b":
        return a_set - b_set
    return b_set - a_set


def _format_set(values: set[int]) -> str:
    ordered = sorted(values)
    if not ordered:
        return "{ } (the empty set)"
    return "{" + ", ".join(str(x) for x in ordered) + "}"


def generate_venn_diagram_notation(tier: Tier, rng: random.Random) -> Question:
    universal_sorted, region_elems, a_set, b_set = _build_notation_sets(rng)
    op_key, notation, description, predicate = rng.choice(_NOTATION_OPS)

    result = _resolve_notation_result(op_key, universal_sorted, a_set, b_set)

    # Independent check: rebuild the result by scanning every element of the
    # flattened universal-set list and testing membership via the boolean
    # predicate - a different traversal than the set-operator expressions
    # used in `_resolve_notation_result` above.
    manual_result = {x for x in universal_sorted if predicate(x in a_set, x in b_set)}
    if manual_result != result:
        raise ValueError("venn_diagram_notation verification failed")

    final_answer = _format_set(result)
    region_text = {r: ", ".join(str(x) for x in region_elems[r]) for r in _ALL_REGIONS}

    steps = [
        f"ξ = {{{', '.join(str(x) for x in universal_sorted)}}}",
        f"A = {_format_set(a_set)}, B = {_format_set(b_set)}",
        f"{notation} means {description}.",
        f"{notation} = {final_answer}",
    ]
    prompt = (
        f"ξ = {{{', '.join(str(x) for x in universal_sorted)}}}. The Venn diagram shows sets A and B. "
        f"List the elements of {notation}."
    )
    return Question(
        topic_id="venn_diagram_notation",
        tier=Tier.HIGHER,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=final_answer,
        dedup_key=(
            f"venn_notation:{op_key}:{region_elems['a_only']}:{region_elems['b_only']}:"
            f"{region_elems['both']}:{region_elems['neither']}"
        ),
        diagram=DiagramSpec(
            kind="venn_diagram",
            params={"labels": ["A", "B"], "universal_label": "S", "region_text": region_text},
        ),
    )


def generate_modelled_example_venn_diagram_notation(tier: Tier, rng: random.Random) -> ModelledExample:
    universal_sorted, region_elems, a_set, b_set = _build_notation_sets(rng)
    op_key, notation, description, predicate = rng.choice(_NOTATION_OPS)

    result = _resolve_notation_result(op_key, universal_sorted, a_set, b_set)

    manual_result = {x for x in universal_sorted if predicate(x in a_set, x in b_set)}
    if manual_result != result:
        raise ValueError("modelled example venn_diagram_notation verification failed")

    final_answer = _format_set(result)
    region_text = {r: ", ".join(str(x) for x in region_elems[r]) for r in _ALL_REGIONS}

    teaching_steps = [
        "The Venn diagram already sorts every element of the universal set ξ into one of four regions, "
        "so set notation is really just a shorthand for picking out a combination of those regions.",
        f"Here, {notation} means {description}.",
        f"Go through ξ = {{{', '.join(str(x) for x in universal_sorted)}}} one element at a time and "
        "check whether each one belongs to A, to B, both, or neither, then apply the rule for "
        f"{notation}.",
        f"Collecting every element that passes the test gives {notation} = {final_answer}.",
    ]
    worked_calculation = [
        f"A = {_format_set(a_set)}, B = {_format_set(b_set)}",
        f"{notation} = {final_answer}",
    ]
    prompt = (
        f"ξ = {{{', '.join(str(x) for x in universal_sorted)}}}. The Venn diagram shows sets A and B. "
        f"List the elements of {notation}."
    )
    return ModelledExample(
        topic_id="venn_diagram_notation",
        tier=Tier.HIGHER,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=final_answer,
        diagram=DiagramSpec(
            kind="venn_diagram",
            params={"labels": ["A", "B"], "universal_label": "S", "region_text": region_text},
        ),
    )


# ---------------------------------------------------------------------------
# venn_diagram_algebra (Higher)
# ---------------------------------------------------------------------------

# Each entry: (key, kind, region_keys, description). `kind` is "count" or
# "probability".
_ALGEBRA_TARGETS = [
    ("a_only", "count", ["a_only"], "the number of elements in A only"),
    ("b_only", "count", ["b_only"], "the number of elements in B only"),
    ("both", "count", ["both"], "the number of elements in both A and B"),
    ("neither", "count", ["neither"], "the number of elements in neither A nor B"),
    ("A", "count", ["a_only", "both"], "the number of elements in A"),
    ("B", "count", ["b_only", "both"], "the number of elements in B"),
    ("prob_A", "probability", ["a_only", "both"], "the probability that a randomly chosen element is in A"),
    (
        "prob_intersection",
        "probability",
        ["both"],
        "the probability that a randomly chosen element is in both A and B",
    ),
    (
        "prob_union",
        "probability",
        ["a_only", "b_only", "both"],
        "the probability that a randomly chosen element is in A or B (or both)",
    ),
]

# Independently-written complement of each target's region_keys (against
# _ALL_REGIONS) - used as a separate cross-check, not derived at runtime from
# the region_keys above.
_ALGEBRA_TARGET_COMPLEMENTS = {
    "a_only": ["b_only", "both", "neither"],
    "b_only": ["a_only", "both", "neither"],
    "both": ["a_only", "b_only", "neither"],
    "neither": ["a_only", "b_only", "both"],
    "A": ["b_only", "neither"],
    "B": ["a_only", "neither"],
    "prob_A": ["b_only", "neither"],
    "prob_intersection": ["a_only", "b_only", "neither"],
    "prob_union": ["neither"],
}


def _format_expr(coef: int, const: int) -> str:
    if coef == 0:
        return str(const)
    term = "x" if coef == 1 else f"{coef}x"
    if const == 0:
        return term
    return f"{term} + {const}"


def _build_algebra_scenario(rng: random.Random):
    x_true = rng.randint(2, 9)
    ca = rng.choice([1, 2, 3])
    cb = rng.choice([1, 2, 3])
    cboth = rng.choice([1, 2])
    const_both = rng.choice([0, 2, 3, 5])
    neither_val = rng.randint(5, 20)

    counts = {
        "a_only": ca * x_true,
        "b_only": cb * x_true,
        "both": cboth * x_true + const_both,
        "neither": neither_val,
    }
    total = sum(counts.values())

    x = sp.symbols("x")
    total_coeff = ca + cb + cboth
    total_const = const_both + neither_val
    solutions = sp.solve(sp.Eq(total_coeff * x + total_const, total), x)
    if len(solutions) != 1:
        raise ValueError("venn_diagram_algebra: sympy did not return a unique solution for x")
    x_solved = solutions[0]

    # Independent check: substitute the solved x back into the original sum
    # expression - rather than trusting sympy's solve output directly - and
    # confirm it reconstructs the given total exactly.
    if total_coeff * x_solved + total_const != total:
        raise ValueError("venn_diagram_algebra verification failed: substitution does not match total")
    if int(x_solved) != x_true:
        raise ValueError("venn_diagram_algebra verification failed: solved x does not match construction")

    region_text = {
        "a_only": _format_expr(ca, 0),
        "b_only": _format_expr(cb, 0),
        "both": _format_expr(cboth, const_both),
        "neither": str(neither_val),
    }
    return x_solved, total_coeff, total_const, total, counts, region_text


def _resolve_algebra_target(rng: random.Random, counts: dict, total: int):
    target_key, target_kind, region_keys, description = rng.choice(_ALGEBRA_TARGETS)
    raw_value = sum(counts[r] for r in region_keys)

    # Independent cross-check: recompute the same target value via total
    # minus the complementary regions, using a separately-written complement
    # lookup (not the runtime set-difference of `region_keys`).
    complement_keys = _ALGEBRA_TARGET_COMPLEMENTS[target_key]
    check_value = total - sum(counts[r] for r in complement_keys)
    if check_value != raw_value:
        raise ValueError("venn_diagram_algebra verification failed: target value mismatch")

    if target_kind == "count":
        final_answer = str(raw_value)
    else:
        frac = Fraction(raw_value, total)
        final_answer = f"{frac.numerator}/{frac.denominator}"
    return target_key, target_kind, description, raw_value, final_answer


def generate_venn_diagram_algebra(tier: Tier, rng: random.Random) -> Question:
    x_solved, total_coeff, total_const, total, counts, region_text = _build_algebra_scenario(rng)
    target_key, target_kind, description, raw_value, final_answer = _resolve_algebra_target(rng, counts, total)
    description_line = description[0].upper() + description[1:]

    steps = [
        f"a_only + b_only + both + neither = total: ({region_text['a_only']}) + ({region_text['b_only']}) "
        f"+ ({region_text['both']}) + {region_text['neither']} = {total}",
        f"Collecting like terms: {total_coeff}x + {total_const} = {total}",
        f"x = {x_solved}",
        f"Substituting x = {x_solved}: A only = {counts['a_only']}, B only = {counts['b_only']}, "
        f"both = {counts['both']}, neither = {counts['neither']}",
        f"{description_line} = {final_answer}",
    ]
    prompt = (
        "The Venn diagram shows the number of elements in each region of sets A and B, given in terms "
        f"of x. There are {total} elements in total. Find the value of x, and hence find {description}."
    )
    return Question(
        topic_id="venn_diagram_algebra",
        tier=Tier.HIGHER,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=final_answer,
        dedup_key=f"venn_algebra:{region_text}:{total}:{target_key}",
        diagram=DiagramSpec(
            kind="venn_diagram", params={"labels": ["A", "B"], "region_text": region_text}
        ),
    )


def generate_modelled_example_venn_diagram_algebra(tier: Tier, rng: random.Random) -> ModelledExample:
    x_solved, total_coeff, total_const, total, counts, region_text = _build_algebra_scenario(rng)
    target_key, target_kind, description, raw_value, final_answer = _resolve_algebra_target(rng, counts, total)

    teaching_steps = [
        "Each region of the Venn diagram is given as an algebraic expression in x rather than a plain "
        "number - adding all four regions together must equal the stated total, which gives you an "
        "equation you can solve for x.",
        f"Adding the four regions: ({region_text['a_only']}) + ({region_text['b_only']}) + "
        f"({region_text['both']}) + {region_text['neither']} = {total}, which collects to "
        f"{total_coeff}x + {total_const} = {total}.",
        f"Solving that linear equation gives x = {x_solved} - always check by substituting back in: "
        f"{total_coeff} × {x_solved} + {total_const} does equal {total}.",
        f"Once x is known, substitute it into each region to get real numbers ({counts['a_only']}, "
        f"{counts['b_only']}, {counts['both']}, {counts['neither']}), then use those to find "
        f"{description}: {final_answer}.",
    ]
    worked_calculation = [
        f"{total_coeff}x + {total_const} = {total}",
        f"x = {x_solved}",
        f"{description[0].upper() + description[1:]} = {final_answer}",
    ]
    prompt = (
        "The Venn diagram shows the number of elements in each region of sets A and B, given in terms "
        f"of x. There are {total} elements in total. Find the value of x, and hence find {description}."
    )
    return ModelledExample(
        topic_id="venn_diagram_algebra",
        tier=Tier.HIGHER,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=final_answer,
        diagram=DiagramSpec(
            kind="venn_diagram", params={"labels": ["A", "B"], "region_text": region_text}
        ),
    )


# ---------------------------------------------------------------------------
# Topic definitions
# ---------------------------------------------------------------------------

TOPIC_VENN_SHADING = TopicDefinition(
    id="venn_diagram_shading",
    display_name="Venn Diagram Shading",
    description="Shade the correct region of a two-set Venn diagram described in plain English.",
    generate=generate_venn_diagram_shading,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_venn_diagram_shading,
)

TOPIC_VENN_PROBABILITY = TopicDefinition(
    id="venn_diagram_probability",
    display_name="Probability from a Venn Diagram",
    description="Use the counts shown in a two-set Venn diagram to find a probability.",
    generate=generate_venn_diagram_probability,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_venn_diagram_probability,
)

TOPIC_VENN_NOTATION = TopicDefinition(
    id="venn_diagram_notation",
    display_name="Venn Diagram Set Notation",
    description="Use formal set notation to find the elements of a set shown in a Venn diagram.",
    generate=generate_venn_diagram_notation,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_venn_diagram_notation,
)

TOPIC_VENN_ALGEBRA = TopicDefinition(
    id="venn_diagram_algebra",
    display_name="Algebraic Venn Diagrams",
    description=(
        "Form and solve an equation from algebraic region counts in a Venn diagram, then find a count "
        "or probability."
    ),
    generate=generate_venn_diagram_algebra,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_venn_diagram_algebra,
)
