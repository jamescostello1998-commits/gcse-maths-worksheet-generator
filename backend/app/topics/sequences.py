import random

import sympy as sp

from app.core.models import ModelledExample, Question, Tier
from app.topics.base import TopicDefinition

SECTION = "algebra"
GROUP = "Sequences"


def _rand_nonzero(rng: random.Random, lo: int, hi: int) -> int:
    while True:
        v = rng.randint(lo, hi)
        if v != 0:
            return v


def _fmt_linear_n(coeff: int, const: int) -> str:
    parts: list[str] = []
    if coeff == 1:
        parts.append("n")
    elif coeff == -1:
        parts.append("-n")
    elif coeff != 0:
        parts.append(f"{coeff}n")
    if const != 0:
        sign = "+" if const > 0 else "-"
        if parts:
            parts.append(f"{sign} {abs(const)}")
        else:
            parts.append(str(const))
    if not parts:
        return "0"
    return " ".join(parts)


def _fmt_quadratic_n(a: int, b: int, c: int) -> str:
    parts = ["n^2" if a == 1 else ("-n^2" if a == -1 else f"{a}n^2")]
    if b != 0:
        term = "n" if abs(b) == 1 else f"{abs(b)}n"
        parts.append(f"{'+' if b > 0 else '-'} {term}")
    if c != 0:
        parts.append(f"{'+' if c > 0 else '-'} {abs(c)}")
    return " ".join(parts)


def generate_next_term(tier: Tier, rng: random.Random) -> Question:
    a1 = rng.randint(-10, 20)
    d = _rand_nonzero(rng, -6, 6)
    n_given = rng.choice([4, 5])
    terms = [a1 + i * d for i in range(n_given)]
    next_term = a1 + n_given * d

    diffs = {terms[i + 1] - terms[i] for i in range(len(terms) - 1)}
    if diffs != {d} or next_term - terms[-1] != d:
        raise ValueError("sequences_next_term verification failed")

    direction = "Add" if d > 0 else "Subtract"
    steps = [
        f"{direction} {abs(d)} each time.",
        f"Next term = {terms[-1]} {'+' if d > 0 else '-'} {abs(d)} = {next_term}",
    ]
    return Question(
        topic_id="sequences_next_term",
        tier=Tier.FOUNDATION,
        prompt=f"Find the next term in the sequence: {', '.join(map(str, terms))}, ...",
        solution_steps=tuple(steps),
        final_answer=str(next_term),
        dedup_key=f"seq_next:{a1}:{d}:{n_given}",
    )


def generate_term_to_term_rule(tier: Tier, rng: random.Random) -> Question:
    kind = rng.choice(["arithmetic", "geometric"])

    if kind == "arithmetic":
        a1 = rng.randint(-10, 15)
        d = _rand_nonzero(rng, -6, 6)
        terms = [a1 + i * d for i in range(4)]
        if {terms[i + 1] - terms[i] for i in range(3)} != {d}:
            raise ValueError("sequences_term_to_term_rule verification failed: arithmetic")
        rule = f"add {d}" if d > 0 else f"subtract {-d}"
        next_term = terms[-1] + d
    else:
        a1 = rng.choice([1, 2, 3, -1, -2, -3])
        ratio = rng.choice([2, 3, -2])
        terms = [a1 * (ratio**i) for i in range(4)]
        for i in range(3):
            if terms[i] * ratio != terms[i + 1]:
                raise ValueError("sequences_term_to_term_rule verification failed: geometric")
        rule = f"multiply by {ratio}"
        next_term = terms[-1] * ratio

    steps = [f"Term-to-term rule: {rule}", f"Next term = {next_term}"]
    return Question(
        topic_id="sequences_term_to_term_rule",
        tier=Tier.FOUNDATION,
        prompt=(
            f"Here are the first four terms of a sequence: {', '.join(map(str, terms))}. "
            "Describe the term-to-term rule, and find the next term."
        ),
        solution_steps=tuple(steps),
        final_answer=f"Rule: {rule}. Next term = {next_term}",
        dedup_key=f"seq_rule:{kind}:{a1}:{terms[1] - terms[0] if kind == 'arithmetic' else ratio}",
    )


def generate_nth_term(tier: Tier, rng: random.Random) -> Question:
    d = _rand_nonzero(rng, -6, 6)
    a1 = rng.randint(-10, 20)
    intercept = a1 - d
    terms = [a1 + i * d for i in range(4)]

    for i in range(4):
        if d * (i + 1) + intercept != terms[i]:
            raise ValueError("sequences_nth_term verification failed")

    formula = _fmt_linear_n(d, intercept)
    steps = [
        f"Common difference = {d}",
        f"nth term = {d}n {'+' if intercept >= 0 else '-'} {abs(intercept)}" if intercept != 0 else f"nth term = {d}n",
        f"nth term = {formula}",
    ]
    return Question(
        topic_id="sequences_nth_term",
        tier=Tier.FOUNDATION,
        prompt=(
            f"Here are the first four terms of a sequence: {', '.join(map(str, terms))}. "
            "Find an expression for the nth term."
        ),
        solution_steps=tuple(steps),
        final_answer=formula,
        dedup_key=f"seq_nth:{d}:{intercept}",
    )


def generate_quadratic_nth_term(tier: Tier, rng: random.Random) -> Question:
    a = _rand_nonzero(rng, -3, 3)
    b = rng.randint(-6, 6)
    c = rng.randint(-10, 10)
    terms = [a * i * i + b * i + c for i in range(1, 5)]

    first_diffs = [terms[i + 1] - terms[i] for i in range(3)]
    second_diffs = {first_diffs[i + 1] - first_diffs[i] for i in range(2)}
    if second_diffs != {2 * a}:
        raise ValueError("sequences_quadratic_nth_term verification failed: second differences")

    # Independent verification: solve for A, B, C from the first three terms as a 3x3
    # linear system (a different method than direct formula evaluation), and confirm
    # it both reproduces a, b, c and correctly predicts the held-out 4th term.
    A, B, C = sp.symbols("A B C")
    eqs = [
        sp.Eq(A * 1 + B * 1 + C, terms[0]),
        sp.Eq(A * 4 + B * 2 + C, terms[1]),
        sp.Eq(A * 9 + B * 3 + C, terms[2]),
    ]
    sol = sp.solve(eqs, [A, B, C])
    if sol[A] != a or sol[B] != b or sol[C] != c:
        raise ValueError("sequences_quadratic_nth_term verification failed: coefficient cross-check")
    if int(sol[A] * 16 + sol[B] * 4 + sol[C]) != terms[3]:
        raise ValueError("sequences_quadratic_nth_term verification failed: held-out term mismatch")

    formula = _fmt_quadratic_n(a, b, c)
    steps = [
        f"First differences: {', '.join(str(v) for v in first_diffs)}",
        f"Second difference is constant: {2 * a}, so the coefficient of n^2 is {2 * a} ÷ 2 = {a}",
        f"nth term = {formula}",
    ]
    return Question(
        topic_id="sequences_quadratic_nth_term",
        tier=Tier.HIGHER,
        prompt=(
            f"Here are the first four terms of a quadratic sequence: {', '.join(map(str, terms))}. "
            "Find an expression for the nth term."
        ),
        solution_steps=tuple(steps),
        final_answer=formula,
        dedup_key=f"seq_quad_nth:{a}:{b}:{c}",
    )


def generate_modelled_example_next_term(tier: Tier, rng: random.Random) -> ModelledExample:
    a1 = rng.randint(-10, 20)
    d = _rand_nonzero(rng, -6, 6)
    n_given = rng.choice([4, 5])
    terms = [a1 + i * d for i in range(n_given)]
    next_term = a1 + n_given * d

    diffs = {terms[i + 1] - terms[i] for i in range(len(terms) - 1)}
    if diffs != {d} or next_term - terms[-1] != d:
        raise ValueError("modelled example sequences_next_term verification failed")

    direction = "adding" if d > 0 else "subtracting"
    teaching_steps = [
        "The first thing to look for in any sequence is the pattern between consecutive terms - here, "
        "that means checking the difference between each term and the one before it.",
        f"Working through the list: "
        + ", ".join(f"{terms[i + 1]} - {terms[i]} = {d}" for i in range(len(terms) - 1))
        + f". The difference is always {d}, so this is an arithmetic sequence formed by {direction} "
        f"{abs(d)} each time.",
        f"To continue the pattern, apply the same rule to the last given term: "
        f"{terms[-1]} {'+' if d > 0 else '-'} {abs(d)} = {next_term}.",
    ]
    worked_calculation = [
        f"{', '.join(map(str, terms))}, ...",
        f"Difference = {d}",
        f"Next term = {terms[-1]} {'+' if d > 0 else '-'} {abs(d)} = {next_term}",
    ]
    return ModelledExample(
        topic_id="sequences_next_term",
        tier=Tier.FOUNDATION,
        prompt=f"Find the next term in the sequence: {', '.join(map(str, terms))}, ...",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=str(next_term),
    )


def generate_modelled_example_term_to_term_rule(tier: Tier, rng: random.Random) -> ModelledExample:
    kind = rng.choice(["arithmetic", "geometric"])

    if kind == "arithmetic":
        a1 = rng.randint(-10, 15)
        d = _rand_nonzero(rng, -6, 6)
        terms = [a1 + i * d for i in range(4)]
        if {terms[i + 1] - terms[i] for i in range(3)} != {d}:
            raise ValueError("modelled example sequences_term_to_term_rule verification failed: arithmetic")
        rule = f"add {d}" if d > 0 else f"subtract {-d}"
        next_term = terms[-1] + d
        teaching_steps = [
            "A term-to-term rule describes how to get from one term to the next, rather than how to "
            "work out any term directly - so the job is to spot what single operation turns each term "
            "into the next one.",
            f"Compare consecutive terms: "
            + ", ".join(f"{terms[i + 1]} - {terms[i]} = {d}" for i in range(3))
            + f". The difference is constant at {d}, so the rule is '{rule}'.",
            f"Apply the rule once more to the last term to find the next one: "
            f"{terms[-1]} {'+' if d > 0 else '-'} {abs(d)} = {next_term}.",
        ]
    else:
        a1 = rng.choice([1, 2, 3, -1, -2, -3])
        ratio = rng.choice([2, 3, -2])
        terms = [a1 * (ratio**i) for i in range(4)]
        for i in range(3):
            if terms[i] * ratio != terms[i + 1]:
                raise ValueError("modelled example sequences_term_to_term_rule verification failed: geometric")
        rule = f"multiply by {ratio}"
        next_term = terms[-1] * ratio
        teaching_steps = [
            "A term-to-term rule describes how to get from one term to the next. Here, the terms don't "
            "share a constant difference, so check instead whether each term is a constant multiple of "
            "the one before it.",
            f"Divide each term by the one before it: "
            + ", ".join(f"{terms[i + 1]} ÷ {terms[i]} = {ratio}" for i in range(3))
            + f". The ratio is constant at {ratio}, so the rule is '{rule}'.",
            f"Apply the rule once more to the last term to find the next one: {terms[-1]} × {ratio} = {next_term}.",
        ]

    worked_calculation = [
        f"{', '.join(map(str, terms))}",
        f"Rule: {rule}",
        f"Next term = {next_term}",
    ]
    return ModelledExample(
        topic_id="sequences_term_to_term_rule",
        tier=Tier.FOUNDATION,
        prompt=(
            f"Here are the first four terms of a sequence: {', '.join(map(str, terms))}. "
            "Describe the term-to-term rule, and find the next term."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"Rule: {rule}. Next term = {next_term}",
    )


def generate_modelled_example_nth_term(tier: Tier, rng: random.Random) -> ModelledExample:
    d = _rand_nonzero(rng, -6, 6)
    a1 = rng.randint(-10, 20)
    intercept = a1 - d
    terms = [a1 + i * d for i in range(4)]

    for i in range(4):
        if d * (i + 1) + intercept != terms[i]:
            raise ValueError("modelled example sequences_nth_term verification failed")

    formula = _fmt_linear_n(d, intercept)
    teaching_steps = [
        f"The nth term of a linear (arithmetic) sequence always has the form dn + c, where d is the "
        "common difference between consecutive terms and c is a constant that shifts the whole sequence.",
        f"Find the common difference by comparing consecutive terms: it's {d} each time, so the "
        f"formula starts as {d}n.",
        f"To find c, check what {d}n gives when n = 1: {d}×1 = {d}. The actual first term is {a1}, so "
        f"c must make up the difference: c = {a1} - {d} = {intercept}.",
        f"Putting it together: nth term = {formula}. Check against n = 2: "
        f"{d}×2 {'+' if intercept >= 0 else '-'} {abs(intercept)} = {terms[1]}, which matches the "
        "second term given.",
    ]
    worked_calculation = [
        f"{', '.join(map(str, terms))}",
        f"Common difference = {d}",
        f"c = {a1} - {d} = {intercept}",
        f"nth term = {formula}",
    ]
    return ModelledExample(
        topic_id="sequences_nth_term",
        tier=Tier.FOUNDATION,
        prompt=(
            f"Here are the first four terms of a sequence: {', '.join(map(str, terms))}. "
            "Find an expression for the nth term."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=formula,
    )


def generate_modelled_example_quadratic_nth_term(tier: Tier, rng: random.Random) -> ModelledExample:
    a = _rand_nonzero(rng, -3, 3)
    b = rng.randint(-6, 6)
    c = rng.randint(-10, 10)
    terms = [a * i * i + b * i + c for i in range(1, 5)]

    first_diffs = [terms[i + 1] - terms[i] for i in range(3)]
    second_diffs = {first_diffs[i + 1] - first_diffs[i] for i in range(2)}
    if second_diffs != {2 * a}:
        raise ValueError("modelled example sequences_quadratic_nth_term verification failed")

    A, B, C = sp.symbols("A B C")
    eqs = [
        sp.Eq(A * 1 + B * 1 + C, terms[0]),
        sp.Eq(A * 4 + B * 2 + C, terms[1]),
        sp.Eq(A * 9 + B * 3 + C, terms[2]),
    ]
    sol = sp.solve(eqs, [A, B, C])
    if sol[A] != a or sol[B] != b or sol[C] != c:
        raise ValueError("modelled example sequences_quadratic_nth_term verification failed: coefficients")
    if int(sol[A] * 16 + sol[B] * 4 + sol[C]) != terms[3]:
        raise ValueError("modelled example sequences_quadratic_nth_term verification failed: held-out term")

    formula = _fmt_quadratic_n(a, b, c)
    teaching_steps = [
        "When a sequence's term-to-term differences aren't constant, it isn't linear - but if the "
        "differences BETWEEN those differences (the second differences) are constant, the sequence is "
        "quadratic, with an nth term of the form An^2 + Bn + C.",
        f"First differences: {', '.join(str(v) for v in first_diffs)}. These aren't constant, so try "
        f"the differences of THOSE differences: {first_diffs[1] - first_diffs[0]}, "
        f"{first_diffs[2] - first_diffs[1]} - constant at {2 * a}.",
        f"The second difference is always 2A, so A = {2 * a} ÷ 2 = {a}.",
        f"Once A is known, comparing A×n^2 to the actual terms reveals the remaining linear part: "
        f"nth term = {formula}. Check against the 4th term: substituting n = 4 gives {terms[3]}, which matches.",
    ]
    worked_calculation = [
        f"{', '.join(map(str, terms))}",
        f"1st differences: {', '.join(str(v) for v in first_diffs)}",
        f"2nd difference = {2 * a}, so A = {a}",
        f"nth term = {formula}",
    ]
    return ModelledExample(
        topic_id="sequences_quadratic_nth_term",
        tier=Tier.HIGHER,
        prompt=(
            f"Here are the first four terms of a quadratic sequence: {', '.join(map(str, terms))}. "
            "Find an expression for the nth term."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=formula,
    )


TOPIC_NEXT_TERM = TopicDefinition(
    id="sequences_next_term",
    display_name="Next Term",
    description="Find the next term in an arithmetic sequence.",
    generate=generate_next_term,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_next_term,
)

TOPIC_TERM_TO_TERM_RULE = TopicDefinition(
    id="sequences_term_to_term_rule",
    display_name="Term-to-Term Rule",
    description="Describe the term-to-term rule of a sequence and find the next term.",
    generate=generate_term_to_term_rule,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_term_to_term_rule,
)

TOPIC_NTH_TERM = TopicDefinition(
    id="sequences_nth_term",
    display_name="nth Term of a Linear Sequence",
    description="Find an expression for the nth term of an arithmetic sequence.",
    generate=generate_nth_term,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_nth_term,
)

TOPIC_QUADRATIC_NTH_TERM = TopicDefinition(
    id="sequences_quadratic_nth_term",
    display_name="nth Term of a Quadratic Sequence",
    description="Find an expression for the nth term of a quadratic sequence.",
    generate=generate_quadratic_nth_term,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_quadratic_nth_term,
)
