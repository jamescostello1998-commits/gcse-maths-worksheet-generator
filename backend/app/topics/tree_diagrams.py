import dataclasses
import itertools
import random
from decimal import Decimal
from fractions import Fraction

import sympy as sp

from app.core.models import DiagramSpec, ModelledExample, Question, Tier
from app.topics.base import TopicDefinition

SECTION = "probability"
GROUP = "Tree Diagrams"

COLOURS = ["red", "blue", "green", "yellow"]
TREE_DRAWING_QUESTION_COUNT = 5

ALGEBRAIC_TARGETS = ["both_first", "both_second", "first_then_second", "second_then_first", "at_least_one_first"]
_X_SYM = sp.symbols("x")

# (subject, cat1_a_clause, cat1_b_clause, cat1_a_short, cat1_b_short,
#  cat2_a_clause, cat2_b_clause, cat2_a_short, cat2_b_short) - every clause
# is a plural predicate that reads naturally after "who" (e.g. "students
# who play a sport"), and the short forms are the branch captions used on
# the frequency tree diagram itself.
_FREQUENCY_TREE_CONTEXTS = [
    ("students", "play a sport", "do not play a sport", "Sport", "No sport",
     "are male", "are female", "Male", "Female"),
    ("customers", "used a discount code", "did not use a discount code", "Discount", "No discount",
     "paid by card", "paid by cash", "Card", "Cash"),
    ("workers", "travel to work by bus", "do not travel to work by bus", "Bus", "No bus",
     "work the morning shift", "work the evening shift", "Morning", "Evening"),
    ("people", "own a pet", "do not own a pet", "Pet", "No pet",
     "are under 18", "are 18 or over", "Under 18", "18 or over"),
]

_FREQUENCY_TREE_FRACTIONS = [
    Fraction(1, 4), Fraction(3, 4), Fraction(1, 5), Fraction(2, 5), Fraction(3, 5), Fraction(4, 5),
    Fraction(1, 8), Fraction(3, 8), Fraction(5, 8), Fraction(7, 8), Fraction(1, 10), Fraction(3, 10),
    Fraction(7, 10), Fraction(9, 10), Fraction(1, 3), Fraction(2, 3),
]

_FREQUENCY_TREE_TOTALS = [40, 60, 80, 100, 120, 150, 160, 200, 240, 250, 300, 360, 400]


def _resolve_split(rng: random.Random, parent_total: int, mode: str) -> tuple:
    """Split parent_total into two child counts one of two ways: mode
    'given' states one child's count directly (a plain number - the
    student finds the other child by subtraction alone, no calculation
    needed) or mode 'fraction' states one child as a fraction/percentage of
    parent_total (the one genuine calculation this generator ever asks
    for - the other child is still found by subtraction). Returns
    (count_a, count_b, stated_is_a, stated_value_str, is_fraction)."""
    stated_is_a = rng.random() < 0.5
    if mode == "fraction":
        for _ in range(100):
            frac = rng.choice(_FREQUENCY_TREE_FRACTIONS)
            stated_frac = parent_total * frac
            if stated_frac.denominator != 1:
                continue
            stated = int(stated_frac)
            other = parent_total - stated
            if stated < 1 or other < 1:
                continue
            # Independent cross-check via Decimal - a different numeric
            # representation from the Fraction arithmetic above.
            d_stated = Decimal(parent_total) * Decimal(frac.numerator) / Decimal(frac.denominator)
            if int(d_stated) != stated:
                raise ValueError("frequency_tree: Fraction/Decimal cross-check mismatch")
            count_a, count_b = (stated, other) if stated_is_a else (other, stated)
            return count_a, count_b, stated_is_a, _frac_str(frac), True
        raise ValueError("frequency_tree: failed to find a clean fraction split")

    lo = max(1, round(parent_total * 0.15))
    hi = min(parent_total - 1, round(parent_total * 0.85))
    if lo > hi:
        lo, hi = 1, parent_total - 1
    stated = rng.randint(lo, hi)
    other = parent_total - stated
    count_a, count_b = (stated, other) if stated_is_a else (other, stated)
    return count_a, count_b, stated_is_a, str(stated), False


def _build_frequency_tree(rng: random.Random) -> dict:
    """Pick a total, then resolve the tree's three splits (root, then one
    further split within each top-level branch) via _resolve_split. Exactly
    one split (chosen at random) uses a fraction/percentage calculation
    half the time; the other half, every split states a count directly, so
    the whole tree is completed by subtraction alone - per the user's
    explicit request that most (and half of all) questions shouldn't need
    more than one fraction/percentage-of-amount calculation. Rerolls until
    every one of the six resulting frequencies is a clean positive integer
    with no branch degenerately small. The fraction-vs-given coin flip is
    made ONCE, before any retrying - not re-flipped on every rejected
    attempt - so the intended ~50/50 split holds even though a fraction
    split occasionally needs a few retries to land on clean integers (a
    'given' split almost never does), which would otherwise bias the mix
    toward zero-fraction questions."""
    use_fraction = rng.random() < 0.5
    for _ in range(500):
        ctx = rng.choice(_FREQUENCY_TREE_CONTEXTS)
        total = rng.choice(_FREQUENCY_TREE_TOTALS)

        fraction_split = rng.randrange(3) if use_fraction else -1
        modes = ["fraction" if i == fraction_split else "given" for i in range(3)]

        try:
            n_a, n_b, root_is_a, root_str, root_frac = _resolve_split(rng, total, modes[0])
            if n_a < 2 or n_b < 2:
                continue
            n_aa, n_ab, a_is_a, a_str, a_frac = _resolve_split(rng, n_a, modes[1])
            n_ba, n_bb, b_is_a, b_str, b_frac = _resolve_split(rng, n_b, modes[2])
        except ValueError:
            continue
        if min(n_aa, n_ab, n_ba, n_bb) < 1:
            continue
        if n_aa + n_ab + n_ba + n_bb != total:
            raise ValueError("frequency_tree: leaf counts do not sum to the total")

        return {
            "ctx": ctx, "total": total,
            "n_a": n_a, "n_b": n_b, "n_aa": n_aa, "n_ab": n_ab, "n_ba": n_ba, "n_bb": n_bb,
            "root": (root_is_a, root_str, root_frac),
            "a": (a_is_a, a_str, a_frac),
            "b": (b_is_a, b_str, b_frac),
        }
    raise ValueError("frequency_tree: failed to find a valid combination")


def _frequency_tree_prompt(data: dict, target_cat1: str, target_cat2: str) -> str:
    subject, cat1_a, cat1_b, *_rest = data["ctx"]
    cat2_a, cat2_b = data["ctx"][5], data["ctx"][6]
    total = data["total"]
    root_is_a, root_str, _ = data["root"]
    a_is_a, a_str, _ = data["a"]
    b_is_a, b_str, _ = data["b"]

    root_clause = cat1_a if root_is_a else cat1_b
    root_other = cat1_b if root_is_a else cat1_a
    a_clause = cat2_a if a_is_a else cat2_b
    b_clause = cat2_a if b_is_a else cat2_b

    return (
        f"{total} {subject} were surveyed. {root_str} of the {total} {subject} {root_clause}; the rest "
        f"{root_other}. Of the {data['n_a']} who {cat1_a}, {a_str} {a_clause}. Of the {data['n_b']} who "
        f"{cat1_b}, {b_str} {b_clause}. Complete the frequency tree, then work out the number of the "
        f"{total} {subject} who {target_cat1} and {target_cat2}."
    )


def _split_calc(parent_total: int, split: tuple, clause_a: str, clause_b: str, count_a: int, count_b: int) -> str:
    """A single-line 'how you find both children' description - a
    calculation line if this split used a fraction, otherwise a plain
    statement that one side is given, in both cases finishing with the
    subtraction that finds the other side."""
    stated_is_a, stated_str, is_frac = split
    stated_clause = clause_a if stated_is_a else clause_b
    other_clause = clause_b if stated_is_a else clause_a
    stated_count = count_a if stated_is_a else count_b
    other_count = count_b if stated_is_a else count_a
    if is_frac:
        head = f"number who {stated_clause} = {stated_str} × {parent_total} = {stated_count}"
    else:
        head = f"{stated_count} who {stated_clause} is given directly"
    return f"{head}, so number who {other_clause} = {parent_total} - {stated_count} = {other_count}"


def generate_frequency_tree(tier: Tier, rng: random.Random) -> Question:
    data = _build_frequency_tree(rng)
    subject, cat1_a, cat1_b, cat1_a_short, cat1_b_short, cat2_a, cat2_b, cat2_a_short, cat2_b_short = data["ctx"]
    total = data["total"]
    n_a, n_b = data["n_a"], data["n_b"]
    n_aa, n_ab, n_ba, n_bb = data["n_aa"], data["n_ab"], data["n_ba"], data["n_bb"]

    targets = [
        (cat1_a, cat2_a, n_aa), (cat1_a, cat2_b, n_ab),
        (cat1_b, cat2_a, n_ba), (cat1_b, cat2_b, n_bb),
    ]
    target_cat1, target_cat2, answer = rng.choice(targets)

    stage1 = [(cat1_a_short, ""), (cat1_b_short, "")]
    stage2 = [[(cat2_a_short, ""), (cat2_b_short, "")], [(cat2_a_short, ""), (cat2_b_short, "")]]

    steps = [
        f"Of the {total} {subject}: {_split_calc(total, data['root'], cat1_a, cat1_b, n_a, n_b)}",
        f"Of the {n_a} who {cat1_a}: {_split_calc(n_a, data['a'], cat2_a, cat2_b, n_aa, n_ab)}",
        f"Of the {n_b} who {cat1_b}: {_split_calc(n_b, data['b'], cat2_a, cat2_b, n_ba, n_bb)}",
    ]

    return Question(
        topic_id="frequency_tree_F",
        tier=Tier.FOUNDATION,
        prompt=_frequency_tree_prompt(data, target_cat1, target_cat2),
        solution_steps=tuple(steps),
        final_answer=str(answer),
        dedup_key=f"freq_tree:{subject}:{total}:{data['root']}:{data['a']}:{data['b']}:{target_cat1}:{target_cat2}",
        diagram=DiagramSpec(kind="frequency_tree", params={"root": str(total), "stage1": stage1, "stage2": stage2}),
        solution_diagram=DiagramSpec(
            kind="frequency_tree",
            params={
                "root": str(total),
                "stage1": [(cat1_a_short, str(n_a)), (cat1_b_short, str(n_b))],
                "stage2": [
                    [(cat2_a_short, str(n_aa)), (cat2_b_short, str(n_ab))],
                    [(cat2_a_short, str(n_ba)), (cat2_b_short, str(n_bb))],
                ],
            },
        ),
    )


def generate_modelled_example_frequency_tree(tier: Tier, rng: random.Random) -> ModelledExample:
    data = _build_frequency_tree(rng)
    subject, cat1_a, cat1_b, cat1_a_short, cat1_b_short, cat2_a, cat2_b, cat2_a_short, cat2_b_short = data["ctx"]
    total = data["total"]
    n_a, n_b = data["n_a"], data["n_b"]
    n_aa, n_ab, n_ba, n_bb = data["n_aa"], data["n_ab"], data["n_ba"], data["n_bb"]

    targets = [
        (cat1_a, cat2_a, n_aa), (cat1_a, cat2_b, n_ab),
        (cat1_b, cat2_a, n_ba), (cat1_b, cat2_b, n_bb),
    ]
    target_cat1, target_cat2, answer = rng.choice(targets)

    worked_calculation = [
        _split_calc(total, data["root"], cat1_a, cat1_b, n_a, n_b),
        _split_calc(n_a, data["a"], cat2_a, cat2_b, n_aa, n_ab),
        _split_calc(n_b, data["b"], cat2_a, cat2_b, n_ba, n_bb),
        f"Answer: {answer}",
    ]
    any_fraction = data["root"][2] or data["a"][2] or data["b"][2]
    teaching_steps = [
        "A frequency tree splits a total into branches using RAW COUNTS at each oval, not probabilities - "
        "work outward from the given total, resolving one split at a time. Most of what you need is given "
        "to you directly as a plain number - the only time you actually have to calculate anything is when "
        "a split is described as a FRACTION or PERCENTAGE of a group; every other value comes from simple "
        "subtraction once you know its branch's own total."
        if any_fraction
        else "A frequency tree splits a total into branches using RAW COUNTS at each oval, not probabilities - "
        "every split here states one branch's count directly, so the whole tree is just subtraction: "
        "each pair of branches must add back up to the count they split from.",
        f"First split, out of all {total} {subject}: {_split_calc(total, data['root'], cat1_a, cat1_b, n_a, n_b)}.",
        f"Second split, within the {n_a} who {cat1_a}: {_split_calc(n_a, data['a'], cat2_a, cat2_b, n_aa, n_ab)}.",
        f"Third split, within the {n_b} who {cat1_b}: {_split_calc(n_b, data['b'], cat2_a, cat2_b, n_ba, n_bb)}.",
        f"Every path through the tree ends at one of the four right-hand ovals - read off the oval for "
        f"{subject} who {target_cat1} and {target_cat2}: {answer}.",
    ]

    return ModelledExample(
        topic_id="frequency_tree_F",
        tier=Tier.FOUNDATION,
        prompt=_frequency_tree_prompt(data, target_cat1, target_cat2),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=str(answer),
        diagram=DiagramSpec(
            kind="frequency_tree",
            params={
                "root": str(total),
                "stage1": [(cat1_a_short, str(n_a)), (cat1_b_short, str(n_b))],
                "stage2": [
                    [(cat2_a_short, str(n_aa)), (cat2_b_short, str(n_ab))],
                    [(cat2_a_short, str(n_ba)), (cat2_b_short, str(n_bb))],
                ],
            },
        ),
    )


def _frac_str(f: Fraction) -> str:
    return f"{f.numerator}/{f.denominator}"


def _solve_algebraic_weights(w1: int, w2: int) -> Fraction:
    """Solve w1*x + w2*x = 1 for x using sympy (primary method - mirrors the
    genuine equation formed from 'the two branch probabilities sum to 1'),
    then independently re-verify the result using plain Fraction arithmetic
    with no sympy involved at all - a completely separate code path from
    sympy's own solver."""
    solutions = sp.solve(sp.Eq(w1 * _X_SYM + w2 * _X_SYM, 1), _X_SYM)
    if len(solutions) != 1:
        raise ValueError("tree_diagram_algebraic: unexpected sympy solve result")
    x_sympy = sp.nsimplify(solutions[0])
    num, den = sp.fraction(x_sympy)
    x_from_sympy = Fraction(int(num), int(den))

    # Independent check: closed-form x = 1/(w1+w2) via plain Fraction
    # arithmetic, then substitute back into the original equation and
    # confirm it equals 1 - never trusting sympy's solve output blindly.
    x_closed_form = Fraction(1, w1 + w2)
    if w1 * x_closed_form + w2 * x_closed_form != 1:
        raise ValueError("tree_diagram_algebraic: closed-form x fails to satisfy the equation")
    if x_from_sympy != x_closed_form:
        raise ValueError("tree_diagram_algebraic: sympy solution disagrees with the closed-form check")
    return x_closed_form


def _algebraic_setup(rng: random.Random) -> tuple:
    """Pick a scenario, style, and coefficients for an algebraic two-outcome
    tree question. Returns (n1, n2, style, w1, w2, expr1, expr2, equation_desc,
    setup_text) - the algebraic label strings (expr1/expr2) are what should
    reach the diagram, never the solved numeric probabilities."""
    n1, n2 = rng.sample(COLOURS, 2)
    style = rng.choice(["coeff", "one_minus"])

    if style == "coeff":
        w1, w2 = rng.sample(range(1, 6), 2)
        expr1 = "x" if w1 == 1 else f"{w1}x"
        expr2 = "x" if w2 == 1 else f"{w2}x"
        equation_desc = f"{expr1} + {expr2} = 1"
        setup_text = (
            f"A biased spinner can only land on {n1} or {n2}. The probability that it lands on {n1} is "
            f"{expr1}, and the probability that it lands on {n2} is {expr2}."
        )
    else:
        w1 = 1
        w2 = rng.randint(2, 6)
        expr1 = "x"
        expr2 = "1-x"
        equation_desc = f"x + {w2}x = 1"
        setup_text = (
            f"A biased spinner can only land on {n1} or {n2}. The probability that it lands on {n1} is x, "
            f"and the probability that it lands on {n2} is 1 - x. Landing on {n2} is {w2} times as likely "
            f"as landing on {n1}."
        )

    return n1, n2, style, w1, w2, expr1, expr2, equation_desc, setup_text


def _algebraic_target(rng: random.Random, n1: str, n2: str, p1: Fraction, p2: Fraction) -> tuple:
    """Pick one combined-outcome target for two spins of the spinner. Returns
    (target, prompt_event, formula_prob, calc_line)."""
    target = rng.choice(ALGEBRAIC_TARGETS)
    if target == "both_first":
        prompt_event = f"both spins land on {n1}"
        formula_prob = p1 * p1
        calc_line = f"P({prompt_event}) = {_frac_str(p1)} × {_frac_str(p1)} = {_frac_str(formula_prob)}"
    elif target == "both_second":
        prompt_event = f"both spins land on {n2}"
        formula_prob = p2 * p2
        calc_line = f"P({prompt_event}) = {_frac_str(p2)} × {_frac_str(p2)} = {_frac_str(formula_prob)}"
    elif target == "first_then_second":
        prompt_event = f"the first spin lands on {n1} and the second lands on {n2}"
        formula_prob = p1 * p2
        calc_line = f"P({prompt_event}) = {_frac_str(p1)} × {_frac_str(p2)} = {_frac_str(formula_prob)}"
    elif target == "second_then_first":
        prompt_event = f"the first spin lands on {n2} and the second lands on {n1}"
        formula_prob = p2 * p1
        calc_line = f"P({prompt_event}) = {_frac_str(p2)} × {_frac_str(p1)} = {_frac_str(formula_prob)}"
    else:  # at_least_one_first
        prompt_event = f"at least one of the two spins lands on {n1}"
        both_second = p2 * p2
        formula_prob = 1 - both_second
        calc_line = (
            f"P({prompt_event}) = 1 - P(both {n2}) = 1 - {_frac_str(both_second)} = {_frac_str(formula_prob)}"
        )
    return target, prompt_event, formula_prob, calc_line


def _algebraic_brute_force_check(n1: str, n2: str, w1: int, w2: int, target: str, formula_prob: Fraction) -> None:
    """Independent verification of the target probability: treat w1/w2 as
    pseudo-counts of a physical bag (P(n1) = w1/(w1+w2) exactly matches a bag
    with w1 n1-counters and w2 n2-counters out of w1+w2 total) and brute-force
    enumerate every physically-labelled pair of picks with replacement - a
    genuinely different method than the p1/p2 Fraction multiplication used to
    build the solution steps."""
    items = [n1] * w1 + [n2] * w2
    sample = list(itertools.product(items, items))
    if target == "both_first":
        matches = [o for o in sample if o == (n1, n1)]
    elif target == "both_second":
        matches = [o for o in sample if o == (n2, n2)]
    elif target == "first_then_second":
        matches = [o for o in sample if o == (n1, n2)]
    elif target == "second_then_first":
        matches = [o for o in sample if o == (n2, n1)]
    else:  # at_least_one_first
        matches = [o for o in sample if n1 in o]
    brute_prob = Fraction(len(matches), len(sample))
    if brute_prob != formula_prob:
        raise ValueError("tree_diagram_algebraic verification failed")


def generate_tree_diagram_independent(tier: Tier, rng: random.Random) -> Question:
    c1, c2 = rng.sample(COLOURS, 2)
    n1 = rng.randint(2, 8)
    n2 = rng.randint(2, 8)
    total = n1 + n2
    p1, p2 = Fraction(n1, total), Fraction(n2, total)

    event = rng.choice(["same", "sequence"])
    items = [c1] * n1 + [c2] * n2
    sample = list(itertools.product(items, items))

    if event == "same":
        formula_prob = p1 * p1 + p2 * p2
        matches = [o for o in sample if o[0] == o[1]]
        prompt_event = "both counters are the same colour"
        steps_extra = [
            f"P(both {c1}) = {_frac_str(p1)} × {_frac_str(p1)} = {_frac_str(p1 * p1)}",
            f"P(both {c2}) = {_frac_str(p2)} × {_frac_str(p2)} = {_frac_str(p2 * p2)}",
            f"P(same colour) = {_frac_str(p1 * p1)} + {_frac_str(p2 * p2)} = {_frac_str(formula_prob)}",
        ]
    else:
        first, second = rng.choice([(c1, c2), (c2, c1), (c1, c1), (c2, c2)])
        p_first = p1 if first == c1 else p2
        p_second = p1 if second == c1 else p2
        formula_prob = p_first * p_second
        matches = [o for o in sample if o[0] == first and o[1] == second]
        prompt_event = f"the first counter is {first} and the second counter is {second}"
        steps_extra = [
            f"P({first} then {second}) = {_frac_str(p_first)} × {_frac_str(p_second)} = {_frac_str(formula_prob)}",
        ]

    # Independent check: brute-force count over every physically-labelled
    # pair of picks (with replacement) - a different method than the
    # branch-probability multiplication used to build the tree above.
    brute_prob = Fraction(len(matches), len(sample))
    if brute_prob != formula_prob:
        raise ValueError("tree_diagram_independent verification failed")

    stage1 = [(c1.title(), _frac_str(p1)), (c2.title(), _frac_str(p2))]
    stage2 = [
        [(c1.title(), _frac_str(p1)), (c2.title(), _frac_str(p2))],
        [(c1.title(), _frac_str(p1)), (c2.title(), _frac_str(p2))],
    ]

    steps = [
        f"A counter is picked, replaced, then a second counter is picked. The probabilities stay the same "
        f"each time: P({c1}) = {_frac_str(p1)}, P({c2}) = {_frac_str(p2)}.",
        *steps_extra,
    ]
    return Question(
        topic_id="tree_diagram_independent_F",
        tier=Tier.FOUNDATION,
        prompt=(
            f"A bag contains {n1} {c1} and {n2} {c2} counters. A counter is picked at random, replaced, and "
            f"then a second counter is picked at random. The tree diagram shows this information. "
            f"Find the probability that {prompt_event}."
        ),
        solution_steps=tuple(steps),
        final_answer=_frac_str(formula_prob),
        dedup_key=f"tree_indep:{c1}:{c2}:{n1}:{n2}:{event}:{prompt_event}",
        diagram=DiagramSpec(kind="tree_diagram", params={"stage1": stage1, "stage2": stage2}),
    )


def generate_modelled_example_tree_diagram_independent(tier: Tier, rng: random.Random) -> ModelledExample:
    c1, c2 = rng.sample(COLOURS, 2)
    n1 = rng.randint(2, 8)
    n2 = rng.randint(2, 8)
    total = n1 + n2
    p1, p2 = Fraction(n1, total), Fraction(n2, total)

    event = rng.choice(["same", "sequence"])
    items = [c1] * n1 + [c2] * n2
    sample = list(itertools.product(items, items))

    if event == "same":
        formula_prob = p1 * p1 + p2 * p2
        matches = [o for o in sample if o[0] == o[1]]
        prompt_event = "both counters are the same colour"
        worked_calculation = [
            f"P(both {c1}) = {_frac_str(p1)} × {_frac_str(p1)} = {_frac_str(p1 * p1)}",
            f"P(both {c2}) = {_frac_str(p2)} × {_frac_str(p2)} = {_frac_str(p2 * p2)}",
            f"P(same) = {_frac_str(p1 * p1)} + {_frac_str(p2 * p2)} = {_frac_str(formula_prob)}",
        ]
        teaching_extra = (
            f"'Same colour' can happen along two branches of the tree - both {c1} or both {c2} - so we "
            "multiply along each of those branches, then add the branch totals together, following each "
            "route through the tree separately."
        )
    else:
        first, second = rng.choice([(c1, c2), (c2, c1), (c1, c1), (c2, c2)])
        p_first = p1 if first == c1 else p2
        p_second = p1 if second == c1 else p2
        formula_prob = p_first * p_second
        matches = [o for o in sample if o[0] == first and o[1] == second]
        prompt_event = f"the first counter is {first} and the second counter is {second}"
        worked_calculation = [
            f"P({first} then {second}) = {_frac_str(p_first)} × {_frac_str(p_second)}",
            f"= {_frac_str(formula_prob)}",
        ]
        teaching_extra = (
            f"This event follows just one route through the tree - {first} on the first branch, then "
            f"{second} on the second - so we multiply along that single path only."
        )

    # Independent check: brute-force count over every physically-labelled
    # pair of picks (with replacement) - a different method than the
    # branch-probability multiplication used to build the tree above.
    brute_prob = Fraction(len(matches), len(sample))
    if brute_prob != formula_prob:
        raise ValueError("modelled example tree_diagram_independent verification failed")

    stage1 = [(c1.title(), _frac_str(p1)), (c2.title(), _frac_str(p2))]
    stage2 = [
        [(c1.title(), _frac_str(p1)), (c2.title(), _frac_str(p2))],
        [(c1.title(), _frac_str(p1)), (c2.title(), _frac_str(p2))],
    ]

    teaching_steps = [
        "Because the counter is replaced after the first pick, the bag is back to exactly how it started - "
        "so the probabilities on the second set of branches are identical to the first. This is what makes "
        "the two picks independent.",
        f"Along the top branch, P({c1}) = {_frac_str(p1)}; along the bottom branch, P({c2}) = {_frac_str(p2)}. "
        "The tree diagram repeats these same two probabilities at the second stage.",
        "To find the probability of following a particular path through the tree, multiply the "
        "probabilities along the branches of that path.",
        teaching_extra,
        f"So P({prompt_event}) = {_frac_str(formula_prob)}.",
    ]

    return ModelledExample(
        topic_id="tree_diagram_independent_F",
        tier=Tier.FOUNDATION,
        prompt=(
            f"A bag contains {n1} {c1} and {n2} {c2} counters. A counter is picked at random, replaced, and "
            f"then a second counter is picked at random. The tree diagram shows this information. "
            f"Find the probability that {prompt_event}."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=_frac_str(formula_prob),
        diagram=DiagramSpec(kind="tree_diagram", params={"stage1": stage1, "stage2": stage2}),
    )


def generate_tree_diagram_dependent(tier: Tier, rng: random.Random) -> Question:
    c1, c2 = rng.sample(COLOURS, 2)
    n1 = rng.randint(3, 8)
    n2 = rng.randint(3, 8)
    total = n1 + n2

    p1, p2 = Fraction(n1, total), Fraction(n2, total)
    p1_given1 = Fraction(n1 - 1, total - 1)
    p2_given1 = Fraction(n2, total - 1)
    p1_given2 = Fraction(n1, total - 1)
    p2_given2 = Fraction(n2 - 1, total - 1)

    event = rng.choice(["same", "different", "sequence"])
    labels = [c1] * n1 + [c2] * n2
    ordered_pairs = list(itertools.permutations(range(total), 2))

    def outcome(i: int, j: int) -> tuple[str, str]:
        return (labels[i], labels[j])

    if event == "same":
        formula_prob = p1 * p1_given1 + p2 * p2_given2
        matches = [1 for i, j in ordered_pairs if outcome(i, j)[0] == outcome(i, j)[1]]
        prompt_event = "both counters are the same colour"
    elif event == "different":
        formula_prob = p1 * p2_given1 + p2 * p1_given2
        matches = [1 for i, j in ordered_pairs if outcome(i, j)[0] != outcome(i, j)[1]]
        prompt_event = "the two counters are different colours"
    else:
        first, second = rng.choice([(c1, c2), (c2, c1), (c1, c1), (c2, c2)])
        if (first, second) == (c1, c2):
            formula_prob = p1 * p2_given1
        elif (first, second) == (c2, c1):
            formula_prob = p2 * p1_given2
        elif (first, second) == (c1, c1):
            formula_prob = p1 * p1_given1
        else:
            formula_prob = p2 * p2_given2
        matches = [1 for i, j in ordered_pairs if outcome(i, j) == (first, second)]
        prompt_event = f"the first counter is {first} and the second counter is {second}"

    # Independent check: brute-force count over every ordered pair of
    # distinct physical counters (without replacement) - a different method
    # than the branch-probability multiplication used to build the tree.
    brute_prob = Fraction(len(matches), len(ordered_pairs))
    if brute_prob != formula_prob:
        raise ValueError("tree_diagram_dependent verification failed")

    stage1 = [(c1.title(), _frac_str(p1)), (c2.title(), _frac_str(p2))]
    stage2 = [
        [(c1.title(), _frac_str(p1_given1)), (c2.title(), _frac_str(p2_given1))],
        [(c1.title(), _frac_str(p1_given2)), (c2.title(), _frac_str(p2_given2))],
    ]

    steps = [
        f"After the first counter is picked (without replacement), there are {total - 1} counters left.",
        f"P({c1} then {c1}) = {_frac_str(p1)} × {_frac_str(p1_given1)} = {_frac_str(p1 * p1_given1)}",
        f"P({c1} then {c2}) = {_frac_str(p1)} × {_frac_str(p2_given1)} = {_frac_str(p1 * p2_given1)}",
        f"P({c2} then {c1}) = {_frac_str(p2)} × {_frac_str(p1_given2)} = {_frac_str(p2 * p1_given2)}",
        f"P({c2} then {c2}) = {_frac_str(p2)} × {_frac_str(p2_given2)} = {_frac_str(p2 * p2_given2)}",
        f"P({prompt_event}) = {_frac_str(formula_prob)}",
    ]
    return Question(
        topic_id="tree_diagram_dependent_H",
        tier=Tier.HIGHER,
        prompt=(
            f"A bag contains {n1} {c1} and {n2} {c2} counters. Two counters are picked at random, one after "
            f"the other, without replacement. The tree diagram shows this information. "
            f"Find the probability that {prompt_event}."
        ),
        solution_steps=tuple(steps),
        final_answer=_frac_str(formula_prob),
        dedup_key=f"tree_dep:{c1}:{c2}:{n1}:{n2}:{event}:{prompt_event}",
        diagram=DiagramSpec(kind="tree_diagram", params={"stage1": stage1, "stage2": stage2}),
    )


def generate_modelled_example_tree_diagram_dependent(tier: Tier, rng: random.Random) -> ModelledExample:
    c1, c2 = rng.sample(COLOURS, 2)
    n1 = rng.randint(3, 8)
    n2 = rng.randint(3, 8)
    total = n1 + n2

    p1, p2 = Fraction(n1, total), Fraction(n2, total)
    p1_given1 = Fraction(n1 - 1, total - 1)
    p2_given1 = Fraction(n2, total - 1)
    p1_given2 = Fraction(n1, total - 1)
    p2_given2 = Fraction(n2 - 1, total - 1)

    event = rng.choice(["same", "different", "sequence"])
    labels = [c1] * n1 + [c2] * n2
    ordered_pairs = list(itertools.permutations(range(total), 2))

    def outcome(i: int, j: int) -> tuple[str, str]:
        return (labels[i], labels[j])

    p_c1c1 = p1 * p1_given1
    p_c1c2 = p1 * p2_given1
    p_c2c1 = p2 * p1_given2
    p_c2c2 = p2 * p2_given2

    if event == "same":
        formula_prob = p_c1c1 + p_c2c2
        matches = [1 for i, j in ordered_pairs if outcome(i, j)[0] == outcome(i, j)[1]]
        prompt_event = "both counters are the same colour"
        worked_calculation = [
            f"P(both {c1}) = {_frac_str(p1)} × {_frac_str(p1_given1)} = {_frac_str(p_c1c1)}",
            f"P(both {c2}) = {_frac_str(p2)} × {_frac_str(p2_given2)} = {_frac_str(p_c2c2)}",
            f"P(same) = {_frac_str(p_c1c1)} + {_frac_str(p_c2c2)} = {_frac_str(formula_prob)}",
        ]
    elif event == "different":
        formula_prob = p_c1c2 + p_c2c1
        matches = [1 for i, j in ordered_pairs if outcome(i, j)[0] != outcome(i, j)[1]]
        prompt_event = "the two counters are different colours"
        worked_calculation = [
            f"P({c1} then {c2}) = {_frac_str(p1)} × {_frac_str(p2_given1)} = {_frac_str(p_c1c2)}",
            f"P({c2} then {c1}) = {_frac_str(p2)} × {_frac_str(p1_given2)} = {_frac_str(p_c2c1)}",
            f"P(different) = {_frac_str(p_c1c2)} + {_frac_str(p_c2c1)} = {_frac_str(formula_prob)}",
        ]
    else:
        first, second = rng.choice([(c1, c2), (c2, c1), (c1, c1), (c2, c2)])
        if (first, second) == (c1, c2):
            formula_prob = p_c1c2
        elif (first, second) == (c2, c1):
            formula_prob = p_c2c1
        elif (first, second) == (c1, c1):
            formula_prob = p_c1c1
        else:
            formula_prob = p_c2c2
        matches = [1 for i, j in ordered_pairs if outcome(i, j) == (first, second)]
        prompt_event = f"the first counter is {first} and the second counter is {second}"
        p_first_branch = p1 if first == c1 else p2
        p_second_branch = {
            (c1, c1): p1_given1, (c1, c2): p2_given1, (c2, c1): p1_given2, (c2, c2): p2_given2,
        }[(first, second)]
        worked_calculation = [
            f"P({first} then {second}) = {_frac_str(p_first_branch)} × {_frac_str(p_second_branch)}",
            f"= {_frac_str(formula_prob)}",
        ]

    # Independent check: brute-force count over every ordered pair of
    # distinct physical counters (without replacement) - a different method
    # than the branch-probability multiplication used to build the tree.
    brute_prob = Fraction(len(matches), len(ordered_pairs))
    if brute_prob != formula_prob:
        raise ValueError("modelled example tree_diagram_dependent verification failed")

    stage1 = [(c1.title(), _frac_str(p1)), (c2.title(), _frac_str(p2))]
    stage2 = [
        [(c1.title(), _frac_str(p1_given1)), (c2.title(), _frac_str(p2_given1))],
        [(c1.title(), _frac_str(p1_given2)), (c2.title(), _frac_str(p2_given2))],
    ]

    teaching_steps = [
        f"Because the first counter is NOT replaced, picking it changes what's left in the bag - there are "
        f"only {total - 1} counters for the second pick, so the second-stage branch probabilities depend on "
        "which colour was picked first. This is what makes the events dependent.",
        f"If the first counter was {c1}, only {n1 - 1} {c1} counters remain out of {total - 1}, so "
        f"P({c1} | first was {c1}) = {_frac_str(p1_given1)}. If the first was {c2} instead, all {n1} {c1} "
        f"counters are still there, so P({c1} | first was {c2}) = {_frac_str(p1_given2)}. The second-stage "
        "branches are different depending on which first branch you followed.",
        "As before, multiply the probabilities along a branch to find the probability of that whole path "
        "through the tree.",
        f"P({prompt_event}) = {_frac_str(formula_prob)}.",
    ]

    return ModelledExample(
        topic_id="tree_diagram_dependent_H",
        tier=Tier.HIGHER,
        prompt=(
            f"A bag contains {n1} {c1} and {n2} {c2} counters. Two counters are picked at random, one after "
            f"the other, without replacement. The tree diagram shows this information. "
            f"Find the probability that {prompt_event}."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=_frac_str(formula_prob),
        diagram=DiagramSpec(kind="tree_diagram", params={"stage1": stage1, "stage2": stage2}),
    )


def generate_tree_diagram_drawing(tier: Tier, rng: random.Random) -> Question:
    c1, c2 = rng.sample(COLOURS, 2)
    n1 = rng.randint(2, 8)
    n2 = rng.randint(2, 8)
    total = n1 + n2
    p1, p2 = Fraction(n1, total), Fraction(n2, total)

    target_first, target_second = rng.choice([(c1, c1), (c1, c2), (c2, c1), (c2, c2)])
    p_first = p1 if target_first == c1 else p2
    p_second = p1 if target_second == c1 else p2
    formula_prob = p_first * p_second

    # Independent check: brute-force count over every physically-labelled
    # pair of picks (with replacement) - a different method than the
    # branch-probability multiplication used above.
    items = [c1] * n1 + [c2] * n2
    sample = list(itertools.product(items, items))
    matches = [o for o in sample if o == (target_first, target_second)]
    brute_prob = Fraction(len(matches), len(sample))
    if brute_prob != formula_prob:
        raise ValueError("tree_diagram_drawing verification failed")

    stage1 = [(c1.title(), _frac_str(p1)), (c2.title(), _frac_str(p2))]
    stage2 = [
        [(c1.title(), _frac_str(p1)), (c2.title(), _frac_str(p2))],
        [(c1.title(), _frac_str(p1)), (c2.title(), _frac_str(p2))],
    ]

    steps = [
        f"Draw two branches from the start: P({c1}) = {_frac_str(p1)}, P({c2}) = {_frac_str(p2)}.",
        "From each of those branches, draw two more with the same probabilities (the counter is replaced).",
        f"P({target_first} then {target_second}) = {_frac_str(p_first)} × {_frac_str(p_second)} = "
        f"{_frac_str(formula_prob)}",
    ]
    return Question(
        topic_id="tree_diagram_drawing_F",
        tier=Tier.FOUNDATION,
        prompt=(
            f"A bag contains {n1} {c1} and {n2} {c2} counters. A counter is picked at random, replaced, and "
            f"then a second counter is picked at random. Draw a fully-labelled tree diagram to show this "
            f"information, and use it to find the probability that the first counter is {target_first} and "
            f"the second counter is {target_second}."
        ),
        solution_steps=tuple(steps),
        final_answer=_frac_str(formula_prob),
        dedup_key=f"tree_draw:{c1}:{c2}:{n1}:{n2}:{target_first}:{target_second}",
        solution_diagram=DiagramSpec(kind="tree_diagram", params={"stage1": stage1, "stage2": stage2}),
    )


def generate_modelled_example_tree_diagram_drawing(tier: Tier, rng: random.Random) -> ModelledExample:
    c1, c2 = rng.sample(COLOURS, 2)
    n1 = rng.randint(2, 8)
    n2 = rng.randint(2, 8)
    total = n1 + n2
    p1, p2 = Fraction(n1, total), Fraction(n2, total)

    target_first, target_second = rng.choice([(c1, c1), (c1, c2), (c2, c1), (c2, c2)])
    p_first = p1 if target_first == c1 else p2
    p_second = p1 if target_second == c1 else p2
    formula_prob = p_first * p_second

    # Independent check: brute-force count over every physically-labelled
    # pair of picks (with replacement) - a different method than the
    # branch-probability multiplication used above.
    items = [c1] * n1 + [c2] * n2
    sample = list(itertools.product(items, items))
    matches = [o for o in sample if o == (target_first, target_second)]
    brute_prob = Fraction(len(matches), len(sample))
    if brute_prob != formula_prob:
        raise ValueError("modelled example tree_diagram_drawing verification failed")

    stage1 = [(c1.title(), _frac_str(p1)), (c2.title(), _frac_str(p2))]
    stage2 = [
        [(c1.title(), _frac_str(p1)), (c2.title(), _frac_str(p2))],
        [(c1.title(), _frac_str(p1)), (c2.title(), _frac_str(p2))],
    ]

    worked_calculation = [
        f"P({target_first}) = {_frac_str(p_first)}, P({target_second}) = {_frac_str(p_second)}",
        f"P({target_first} then {target_second}) = {_frac_str(p_first)} × {_frac_str(p_second)}",
        f"= {_frac_str(formula_prob)}",
    ]
    teaching_steps = [
        "Start by drawing two branches from a single starting point, one for each colour, and label each "
        f"branch with its probability: P({c1}) = {_frac_str(p1)}, P({c2}) = {_frac_str(p2)}.",
        "Because the counter is replaced before the second pick, the bag is exactly as it was at the "
        "start - so from the end of EACH of those first two branches, draw the same two branches again "
        "with the same two probabilities.",
        "Every complete path from the start to the end of the tree represents one possible pair of picks - "
        "there are four such paths in total here.",
        f"To find the probability of a specific path (here, {target_first} then {target_second}), multiply "
        f"the probabilities along that one path: {_frac_str(p_first)} × {_frac_str(p_second)} = "
        f"{_frac_str(formula_prob)}.",
    ]

    return ModelledExample(
        topic_id="tree_diagram_drawing_F",
        tier=Tier.FOUNDATION,
        prompt=(
            f"A bag contains {n1} {c1} and {n2} {c2} counters. A counter is picked at random, replaced, and "
            f"then a second counter is picked at random. Draw a fully-labelled tree diagram to show this "
            f"information, and use it to find the probability that the first counter is {target_first} and "
            f"the second counter is {target_second}."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=_frac_str(formula_prob),
        diagram=DiagramSpec(kind="tree_diagram", params={"stage1": stage1, "stage2": stage2}),
    )


def generate_tree_diagram_algebraic(tier: Tier, rng: random.Random) -> Question:
    n1, n2, style, w1, w2, expr1, expr2, equation_desc, setup_text = _algebraic_setup(rng)
    x_val = _solve_algebraic_weights(w1, w2)
    p1 = w1 * x_val
    p2 = w2 * x_val

    target, prompt_event, formula_prob, calc_line = _algebraic_target(rng, n1, n2, p1, p2)
    _algebraic_brute_force_check(n1, n2, w1, w2, target, formula_prob)

    stage1 = [(n1.title(), expr1), (n2.title(), expr2)]
    stage2 = [
        [(n1.title(), expr1), (n2.title(), expr2)],
        [(n1.title(), expr1), (n2.title(), expr2)],
    ]

    steps = [
        f"{setup_text} Since the spinner can only land on {n1} or {n2}, the two probabilities must sum to "
        f"1: {equation_desc}.",
        f"Solving this equation gives x = {_frac_str(x_val)}.",
        f"Substituting back: P({n1}) = {_frac_str(p1)}, P({n2}) = {_frac_str(p2)}.",
        calc_line,
    ]
    return Question(
        topic_id="tree_diagram_algebraic_H",
        tier=Tier.HIGHER,
        prompt=(
            f"{setup_text} The spinner is spun twice. Find the probability that {prompt_event}."
        ),
        solution_steps=tuple(steps),
        final_answer=_frac_str(formula_prob),
        dedup_key=f"tree_alg:{style}:{n1}:{n2}:{w1}:{w2}:{target}",
        diagram=DiagramSpec(kind="tree_diagram", params={"stage1": stage1, "stage2": stage2}),
    )


def generate_modelled_example_tree_diagram_algebraic(tier: Tier, rng: random.Random) -> ModelledExample:
    n1, n2, style, w1, w2, expr1, expr2, equation_desc, setup_text = _algebraic_setup(rng)
    x_val = _solve_algebraic_weights(w1, w2)
    p1 = w1 * x_val
    p2 = w2 * x_val

    target, prompt_event, formula_prob, calc_line = _algebraic_target(rng, n1, n2, p1, p2)
    _algebraic_brute_force_check(n1, n2, w1, w2, target, formula_prob)

    stage1 = [(n1.title(), expr1), (n2.title(), expr2)]
    stage2 = [
        [(n1.title(), expr1), (n2.title(), expr2)],
        [(n1.title(), expr1), (n2.title(), expr2)],
    ]

    worked_calculation = [
        f"{equation_desc}, so x = {_frac_str(x_val)}",
        f"P({n1}) = {_frac_str(p1)}, P({n2}) = {_frac_str(p2)}",
        calc_line,
    ]
    teaching_steps = [
        f"Because this spinner only has two possible outcomes, {n1} and {n2}, their probabilities must add "
        f"up to exactly 1 - that's what lets us turn the algebraic expressions into a real equation: "
        f"{equation_desc}.",
        f"Solving that equation for x gives x = {_frac_str(x_val)}. Once x is known, substitute it back "
        f"into each expression to get the actual numeric probabilities: P({n1}) = {_frac_str(p1)} and "
        f"P({n2}) = {_frac_str(p2)}.",
        "The tree diagram for spinning twice has the same two branches repeated at the second stage, "
        "since the spinner doesn't change between spins.",
        "To find the probability of a specific outcome (or combination of outcomes), multiply along the "
        "branches of the tree that match it, adding several products together if more than one path "
        "satisfies the event.",
        f"So {calc_line}.",
    ]

    return ModelledExample(
        topic_id="tree_diagram_algebraic_H",
        tier=Tier.HIGHER,
        prompt=(
            f"{setup_text} The spinner is spun twice. Find the probability that {prompt_event}."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=_frac_str(formula_prob),
        diagram=DiagramSpec(kind="tree_diagram", params={"stage1": stage1, "stage2": stage2}),
    )


def generate_tree_diagram_mixed(tier: Tier, rng: random.Random) -> Question:
    if rng.random() < 0.5:
        q = generate_tree_diagram_independent(Tier.FOUNDATION, rng)
    else:
        q = generate_tree_diagram_dependent(Tier.HIGHER, rng)
    return dataclasses.replace(
        q, topic_id="tree_diagram_mixed_H", tier=Tier.HIGHER, dedup_key=f"mixed:{q.dedup_key}"
    )


def generate_modelled_example_tree_diagram_mixed(tier: Tier, rng: random.Random) -> ModelledExample:
    if rng.random() < 0.5:
        example = generate_modelled_example_tree_diagram_independent(Tier.FOUNDATION, rng)
    else:
        example = generate_modelled_example_tree_diagram_dependent(Tier.HIGHER, rng)
    return dataclasses.replace(example, topic_id="tree_diagram_mixed_H", tier=Tier.HIGHER)


TOPIC_TREE_INDEPENDENT = TopicDefinition(
    id="tree_diagram_independent_F",
    display_name="Interpreting Tree Diagrams (Independent Events)",
    description="Use a tree diagram to find probabilities when events are independent (with replacement).",
    generate=generate_tree_diagram_independent,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_tree_diagram_independent,
)

TOPIC_TREE_DEPENDENT = TopicDefinition(
    id="tree_diagram_dependent_H",
    display_name="Interpreting Tree Diagrams (Dependent Events)",
    description="Use a tree diagram to find probabilities when events are dependent (without replacement).",
    generate=generate_tree_diagram_dependent,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_tree_diagram_dependent,
)

TOPIC_TREE_DRAWING = TopicDefinition(
    id="tree_diagram_drawing_F",
    display_name="Drawing Tree Diagrams",
    description="Draw a fully-labelled tree diagram from a description, then use it to find a probability. (5 questions)",
    generate=generate_tree_diagram_drawing,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    question_count=TREE_DRAWING_QUESTION_COUNT,
    generate_modelled_example=generate_modelled_example_tree_diagram_drawing,
)

TOPIC_TREE_ALGEBRAIC = TopicDefinition(
    id="tree_diagram_algebraic_H",
    display_name="Tree Diagrams with Algebraic Probabilities",
    description=(
        "Form and solve an equation for x from two algebraic branch probabilities that sum to 1, then use "
        "a tree diagram to find a combined probability."
    ),
    generate=generate_tree_diagram_algebraic,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_tree_diagram_algebraic,
)

TOPIC_TREE_MIXED = TopicDefinition(
    id="tree_diagram_mixed_H",
    display_name="Mixed Tree Diagrams",
    description="A mix of independent and dependent tree diagram probability questions.",
    generate=generate_tree_diagram_mixed,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_tree_diagram_mixed,
)

TOPIC_FREQUENCY_TREE = TopicDefinition(
    id="frequency_tree_F",
    display_name="Frequency Trees",
    description="Complete a frequency tree from given fractions of a total, then read off a specific frequency.",
    generate=generate_frequency_tree,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_frequency_tree,
)
