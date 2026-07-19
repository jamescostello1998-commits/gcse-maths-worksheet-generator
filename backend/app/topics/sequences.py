import random

import sympy as sp

from app.core.models import Question, Tier
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


TOPIC_NEXT_TERM = TopicDefinition(
    id="sequences_next_term",
    display_name="Next Term",
    description="Find the next term in an arithmetic sequence.",
    generate=generate_next_term,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
)

TOPIC_TERM_TO_TERM_RULE = TopicDefinition(
    id="sequences_term_to_term_rule",
    display_name="Term-to-Term Rule",
    description="Describe the term-to-term rule of a sequence and find the next term.",
    generate=generate_term_to_term_rule,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
)

TOPIC_NTH_TERM = TopicDefinition(
    id="sequences_nth_term",
    display_name="nth Term of a Linear Sequence",
    description="Find an expression for the nth term of an arithmetic sequence.",
    generate=generate_nth_term,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
)

TOPIC_QUADRATIC_NTH_TERM = TopicDefinition(
    id="sequences_quadratic_nth_term",
    display_name="nth Term of a Quadratic Sequence",
    description="Find an expression for the nth term of a quadratic sequence.",
    generate=generate_quadratic_nth_term,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
)
