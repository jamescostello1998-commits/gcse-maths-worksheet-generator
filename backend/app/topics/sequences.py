import random
from fractions import Fraction

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
        topic_id="sequences_next_term_F",
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
        topic_id="sequences_term_to_term_rule_F",
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
        topic_id="sequences_nth_term_F",
        tier=Tier.FOUNDATION,
        prompt=(
            f"Here are the first four terms of a sequence: {', '.join(map(str, terms))}.\n"
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
        topic_id="sequences_quadratic_nth_term_H",
        tier=Tier.HIGHER,
        prompt=(
            f"Here are the first four terms of a quadratic sequence: {', '.join(map(str, terms))}.\n"
            "Find an expression for the nth term."
        ),
        solution_steps=tuple(steps),
        final_answer=formula,
        dedup_key=f"seq_quad_nth:{a}:{b}:{c}",
    )


_SPECIAL_KINDS = ("triangular", "square", "cube", "arithmetic")

_SPECIAL_NAMES = {
    "triangular": "triangular numbers",
    "square": "square numbers",
    "cube": "cube numbers",
}

_SPECIAL_FORMULA = {
    "triangular": "\\frac{n(n + 1)}{2}",
    "square": "n^2",
    "cube": "n^3",
}

_GEOMETRIC_RATIOS = (
    Fraction(1, 2),
    Fraction(2, 1),
    Fraction(3, 2),
    Fraction(2, 3),
    Fraction(3, 1),
)


def _ordinal(n: int) -> str:
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def _special_term(kind: str, n: int) -> int:
    if kind == "triangular":
        return n * (n + 1) // 2
    if kind == "square":
        return n * n
    if kind == "cube":
        return n**3
    raise AssertionError(kind)


def _special_term_iterative(kind: str, n: int) -> int:
    """Independently recompute the nth special number via a genuinely
    different accumulation method than the closed-form formula in
    _special_term - a real second check, not a restatement of the same
    formula."""
    if kind == "triangular":
        total = 0
        for k in range(1, n + 1):
            total += k
        return total
    if kind == "square":
        total = 0  # the sum of the first n odd numbers equals n^2
        for k in range(n):
            total += 2 * k + 1
        return total
    if kind == "cube":
        total = 0  # n added to itself n*n times equals n^3
        for _ in range(n * n):
            total += n
        return total
    raise AssertionError(kind)


def _special_step_text(kind: str, n: int, value: int) -> str:
    if kind == "triangular":
        return f"Term {n} = \\frac{{{n}({n} + 1)}}{{2}} = {n * (n + 1)}/2 = {value}"
    if kind == "square":
        return f"Term {n} = {n}^2 = {value}"
    return f"Term {n} = {n}^3 = {value}"


def _fmt_fraction(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _fib_like_list(a1: int, a2: int, total_terms: int) -> list[int]:
    terms = [a1, a2]
    while len(terms) < total_terms:
        terms.append(terms[-1] + terms[-2])
    return terms


def _fib_like_nth(a1: int, a2: int, n: int) -> int:
    """Independently recompute the nth term (1-indexed) via a rolling
    pair-update loop rather than building/indexing the list _fib_like_list
    constructs - a genuinely different code path to the same value."""
    if n == 1:
        return a1
    if n == 2:
        return a2
    x, y = a1, a2
    for _ in range(n - 2):
        x, y = y, x + y
    return y


def _geometric_term_direct(a: int, r: Fraction, n: int) -> Fraction:
    return Fraction(a) * (r ** (n - 1))


def _geometric_term_repeated(a: int, r: Fraction, n: int) -> Fraction:
    """Independently recompute the nth geometric term via repeated
    multiplication in a loop, rather than the ** power operator used by
    _geometric_term_direct - a genuinely different code route to the same
    Fraction value."""
    term = Fraction(a)
    for _ in range(n - 1):
        term *= r
    return term


def generate_special_sequences_foundation(tier: Tier, rng: random.Random) -> Question:
    kind = rng.choice(_SPECIAL_KINDS)

    if kind == "arithmetic":
        a1 = rng.randint(-10, 20)
        d = _rand_nonzero(rng, -6, 6)
        n_given = rng.choice([4, 5])
        terms = [a1 + i * d for i in range(n_given)]
        next_term = a1 + n_given * d

        diffs = {terms[i + 1] - terms[i] for i in range(len(terms) - 1)}
        if diffs != {d} or next_term - terms[-1] != d:
            raise ValueError("special_sequences_foundation verification failed: arithmetic")

        steps = [
            f"This is an arithmetic sequence: it goes up (or down) by the same amount, {d}, each time.",
            f"Next term = {terms[-1]} {'+' if d > 0 else '-'} {abs(d)} = {next_term}",
        ]
        prompt = (
            f"Here are the first {n_given} terms of a sequence: {', '.join(map(str, terms))}. "
            "Find the next term."
        )
        answer = str(next_term)
        dedup_key = f"seq_special_found:arithmetic:{a1}:{d}:{n_given}"
    else:
        num_shown = rng.choice([3, 4, 5])
        offset = rng.choice([1, 2, 3])
        shown_ns = list(range(1, num_shown + 1))
        terms = [_special_term(kind, n) for n in shown_ns]
        target_n = num_shown + offset

        # Independent verification: recompute every shown term AND the target
        # term via a genuinely different accumulation method
        # (_special_term_iterative), not just the same closed-form formula
        # restated.
        for n, t in zip(shown_ns, terms):
            if _special_term_iterative(kind, n) != t:
                raise ValueError(f"special_sequences_foundation verification failed: {kind} shown term")
        target_term = _special_term(kind, target_n)
        if _special_term_iterative(kind, target_n) != target_term:
            raise ValueError(f"special_sequences_foundation verification failed: {kind} target term")

        name = _SPECIAL_NAMES[kind]
        formula = _SPECIAL_FORMULA[kind]
        if offset == 1:
            ask = "Find the next term in the sequence."
        else:
            ask = f"Find the {_ordinal(target_n)} term of the sequence."

        steps = [
            f"These are the {name}: the nth term is given by {formula}.",
            _special_step_text(kind, target_n, target_term),
        ]
        prompt = f"The first {num_shown} {name} are: {', '.join(map(str, terms))}. " + ask
        answer = str(target_term)
        dedup_key = f"seq_special_found:{kind}:{num_shown}:{offset}"

    return Question(
        topic_id="special_sequences_F",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=dedup_key,
    )


def generate_special_sequences_higher(tier: Tier, rng: random.Random) -> Question:
    kind = rng.choice(["fibonacci", "geometric"])

    if kind == "fibonacci":
        a1 = rng.randint(1, 12)
        a2 = rng.randint(1, 12)
        num_shown = rng.choice([4, 5])
        ask_count = rng.choice([1, 2])
        total_terms = num_shown + ask_count

        terms_full = _fib_like_list(a1, a2, total_terms)
        shown = terms_full[:num_shown]
        targets = terms_full[num_shown:]

        for n in range(num_shown + 1, total_terms + 1):
            if _fib_like_nth(a1, a2, n) != terms_full[n - 1]:
                raise ValueError("special_sequences_higher verification failed: fibonacci")

        rule = "each term (from the 3rd onwards) is found by adding the two terms before it"
        if ask_count == 1:
            ask = "Find the next term of the sequence."
            answer = str(targets[0])
        else:
            ask = "Find the next two terms of the sequence."
            answer = f"{targets[0]}, {targets[1]}"

        steps = [
            f"Rule: {rule}.",
            f"{shown[-2]} + {shown[-1]} = {targets[0]}",
        ]
        if ask_count == 2:
            steps.append(f"{shown[-1]} + {targets[0]} = {targets[1]}")

        prompt = (
            f"The first {num_shown} terms of a Fibonacci-type sequence are: {', '.join(map(str, shown))}. "
            f"{rule[0].upper()}{rule[1:]}. " + ask
        )
        dedup_key = f"seq_special_high:fibonacci:{a1}:{a2}:{num_shown}:{ask_count}"
    else:
        a = rng.randint(1, 6)
        r = rng.choice(_GEOMETRIC_RATIOS)
        num_shown = rng.choice([3, 4])
        offset = rng.choice([1, 2])
        target_n = num_shown + offset

        shown_terms = [_geometric_term_direct(a, r, n) for n in range(1, num_shown + 1)]
        target_direct = _geometric_term_direct(a, r, target_n)
        target_repeated = _geometric_term_repeated(a, r, target_n)
        if target_direct != target_repeated:
            raise ValueError("special_sequences_higher verification failed: geometric cross-check")
        for n, t in zip(range(1, num_shown + 1), shown_terms):
            if _geometric_term_repeated(a, r, n) != t:
                raise ValueError("special_sequences_higher verification failed: geometric shown term")

        r_str = _fmt_fraction(r)
        shown_str = ", ".join(_fmt_fraction(t) for t in shown_terms)
        steps = [
            f"Common ratio r = {r_str} (divide any term by the term before it).",
            f"nth term = a × r^(n - 1) = {a} × ({r_str})^{target_n - 1}",
            f"Term {target_n} = {_fmt_fraction(target_direct)}",
        ]
        prompt = (
            f"The first {num_shown} terms of a geometric sequence are: {shown_str}. "
            f"Find the {_ordinal(target_n)} term of the sequence."
        )
        answer = _fmt_fraction(target_direct)
        dedup_key = f"seq_special_high:geometric:{a}:{r.numerator}:{r.denominator}:{num_shown}:{offset}"

    return Question(
        topic_id="special_sequences_H",
        tier=Tier.HIGHER,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=dedup_key,
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
        topic_id="sequences_next_term_F",
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
        topic_id="sequences_term_to_term_rule_F",
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
        topic_id="sequences_nth_term_F",
        tier=Tier.FOUNDATION,
        prompt=(
            f"Here are the first four terms of a sequence: {', '.join(map(str, terms))}.\n"
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
        topic_id="sequences_quadratic_nth_term_H",
        tier=Tier.HIGHER,
        prompt=(
            f"Here are the first four terms of a quadratic sequence: {', '.join(map(str, terms))}.\n"
            "Find an expression for the nth term."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=formula,
    )


def generate_modelled_example_special_sequences_foundation(tier: Tier, rng: random.Random) -> ModelledExample:
    kind = rng.choice(_SPECIAL_KINDS)

    if kind == "arithmetic":
        a1 = rng.randint(-10, 20)
        d = _rand_nonzero(rng, -6, 6)
        n_given = rng.choice([4, 5])
        terms = [a1 + i * d for i in range(n_given)]
        next_term = a1 + n_given * d

        diffs = {terms[i + 1] - terms[i] for i in range(len(terms) - 1)}
        if diffs != {d} or next_term - terms[-1] != d:
            raise ValueError("modelled example special_sequences_foundation verification failed: arithmetic")

        teaching_steps = [
            "Special sequences come in a few recognisable families - arithmetic (add/subtract the same "
            "amount each time), triangular, square, and cube numbers. The first job is always to spot "
            "which family a given list of terms belongs to.",
            f"Comparing consecutive terms here: "
            + ", ".join(f"{terms[i + 1]} - {terms[i]} = {d}" for i in range(len(terms) - 1))
            + f". The difference is constant at {d}, so this is an arithmetic sequence.",
            f"Continue the same pattern from the last given term: {terms[-1]} "
            f"{'+' if d > 0 else '-'} {abs(d)} = {next_term}.",
        ]
        worked_calculation = [
            f"{', '.join(map(str, terms))}, ...",
            f"Common difference = {d}",
            f"Next term = {terms[-1]} {'+' if d > 0 else '-'} {abs(d)} = {next_term}",
        ]
        prompt = (
            f"Here are the first {n_given} terms of a sequence: {', '.join(map(str, terms))}. "
            "Find the next term."
        )
        answer = str(next_term)
    else:
        num_shown = rng.choice([3, 4, 5])
        offset = rng.choice([1, 2, 3])
        shown_ns = list(range(1, num_shown + 1))
        terms = [_special_term(kind, n) for n in shown_ns]
        target_n = num_shown + offset

        for n, t in zip(shown_ns, terms):
            if _special_term_iterative(kind, n) != t:
                raise ValueError(f"modelled example special_sequences_foundation verification failed: {kind} shown")
        target_term = _special_term(kind, target_n)
        if _special_term_iterative(kind, target_n) != target_term:
            raise ValueError(f"modelled example special_sequences_foundation verification failed: {kind} target")

        name = _SPECIAL_NAMES[kind]
        formula = _SPECIAL_FORMULA[kind]
        ask = (
            "Find the next term in the sequence."
            if offset == 1
            else f"Find the {_ordinal(target_n)} term of the sequence."
        )
        teaching_steps = [
            f"The {name} are a special sequence with a known formula for the nth term: {formula}. "
            "Recognising the pattern in the given terms (rather than working out a common difference) "
            "is the key skill being tested here.",
            "Checking the given terms against the formula confirms the pattern: "
            + ", ".join(_special_step_text(kind, n, t) for n, t in zip(shown_ns, terms))
            + ".",
            f"Applying the same formula to term number {target_n} gives the answer: "
            f"{_special_step_text(kind, target_n, target_term)}.",
        ]
        worked_calculation = [
            f"{', '.join(map(str, terms))}",
            f"nth term = {formula}",
            _special_step_text(kind, target_n, target_term),
        ]
        prompt = f"The first {num_shown} {name} are: {', '.join(map(str, terms))}. " + ask
        answer = str(target_term)

    return ModelledExample(
        topic_id="special_sequences_F",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
    )


def generate_modelled_example_special_sequences_higher(tier: Tier, rng: random.Random) -> ModelledExample:
    kind = rng.choice(["fibonacci", "geometric"])

    if kind == "fibonacci":
        a1 = rng.randint(1, 12)
        a2 = rng.randint(1, 12)
        num_shown = rng.choice([4, 5])
        ask_count = rng.choice([1, 2])
        total_terms = num_shown + ask_count

        terms_full = _fib_like_list(a1, a2, total_terms)
        shown = terms_full[:num_shown]
        targets = terms_full[num_shown:]

        for n in range(num_shown + 1, total_terms + 1):
            if _fib_like_nth(a1, a2, n) != terms_full[n - 1]:
                raise ValueError("modelled example special_sequences_higher verification failed: fibonacci")

        rule = "each term (from the 3rd onwards) is found by adding the two terms before it"
        if ask_count == 1:
            ask = "Find the next term of the sequence."
            answer = str(targets[0])
        else:
            ask = "Find the next two terms of the sequence."
            answer = f"{targets[0]}, {targets[1]}"

        prompt = (
            f"The first {num_shown} terms of a Fibonacci-type sequence are: {', '.join(map(str, shown))}. "
            f"{rule[0].upper()}{rule[1:]}. " + ask
        )
        teaching_steps = [
            "A Fibonacci-type sequence doesn't have a constant difference or a constant ratio between "
            "terms - instead, each new term is built directly from the two terms immediately before it, "
            "so the rule to spot is 'add the previous two terms together'.",
            "Check the rule holds for the terms already given: "
            + ", ".join(f"{shown[i]} + {shown[i + 1]} = {shown[i + 2]}" for i in range(len(shown) - 2))
            + ".",
            f"Apply the same rule to extend the sequence: {shown[-2]} + {shown[-1]} = {targets[0]}"
            + (f", then {shown[-1]} + {targets[0]} = {targets[1]}." if ask_count == 2 else "."),
        ]
        worked_calculation = [
            f"{', '.join(map(str, shown))}, ...",
            f"{shown[-2]} + {shown[-1]} = {targets[0]}",
        ]
        if ask_count == 2:
            worked_calculation.append(f"{shown[-1]} + {targets[0]} = {targets[1]}")
    else:
        a = rng.randint(1, 6)
        r = rng.choice(_GEOMETRIC_RATIOS)
        num_shown = rng.choice([3, 4])
        offset = rng.choice([1, 2])
        target_n = num_shown + offset

        shown_terms = [_geometric_term_direct(a, r, n) for n in range(1, num_shown + 1)]
        target_direct = _geometric_term_direct(a, r, target_n)
        target_repeated = _geometric_term_repeated(a, r, target_n)
        if target_direct != target_repeated:
            raise ValueError(
                "modelled example special_sequences_higher verification failed: geometric cross-check"
            )

        r_str = _fmt_fraction(r)
        shown_str = ", ".join(_fmt_fraction(t) for t in shown_terms)
        prompt = (
            f"The first {num_shown} terms of a geometric sequence are: {shown_str}. "
            f"Find the {_ordinal(target_n)} term of the sequence."
        )
        teaching_steps = [
            "A geometric sequence has a constant common ratio between consecutive terms, rather than a "
            "constant difference - so the first step is always to divide a term by the one before it to "
            "find that ratio.",
            f"Dividing consecutive terms here gives a common ratio of r = {r_str} every time.",
            f"The nth term of a geometric sequence is a × r^(n - 1), where a is the first term. "
            f"Substituting n = {target_n}: {a} × ({r_str})^{target_n - 1} = {_fmt_fraction(target_direct)}.",
        ]
        worked_calculation = [
            f"{shown_str}, ...",
            f"r = {r_str}",
            f"Term {target_n} = {a} × ({r_str})^{target_n - 1} = {_fmt_fraction(target_direct)}",
        ]
        answer = _fmt_fraction(target_direct)

    return ModelledExample(
        topic_id="special_sequences_H",
        tier=Tier.HIGHER,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
    )


TOPIC_NEXT_TERM = TopicDefinition(
    id="sequences_next_term_F",
    display_name="Next Term",
    description="Find the next term in an arithmetic sequence.",
    generate=generate_next_term,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_next_term,
)

TOPIC_TERM_TO_TERM_RULE = TopicDefinition(
    id="sequences_term_to_term_rule_F",
    display_name="Term-to-Term Rule",
    description="Describe the term-to-term rule of a sequence and find the next term.",
    generate=generate_term_to_term_rule,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_term_to_term_rule,
)

TOPIC_NTH_TERM = TopicDefinition(
    id="sequences_nth_term_F",
    display_name="nth Term of a Linear Sequence",
    description="Find an expression for the nth term of an arithmetic sequence.",
    generate=generate_nth_term,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_nth_term,
)

TOPIC_QUADRATIC_NTH_TERM = TopicDefinition(
    id="sequences_quadratic_nth_term_H",
    display_name="nth Term of a Quadratic Sequence",
    description="Find an expression for the nth term of a quadratic sequence.",
    generate=generate_quadratic_nth_term,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_quadratic_nth_term,
)

TOPIC_SPECIAL_SEQUENCES_FOUNDATION = TopicDefinition(
    id="special_sequences_F",
    display_name="Special Sequences",
    description="Recognise triangular, square, cube and arithmetic sequences and find further terms.",
    generate=generate_special_sequences_foundation,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_special_sequences_foundation,
)

TOPIC_SPECIAL_SEQUENCES_HIGHER = TopicDefinition(
    id="special_sequences_H",
    display_name="Fibonacci-Type and Geometric Sequences",
    description=(
        "Find terms of a Fibonacci-type sequence, or of a geometric sequence with a rational common ratio."
    ),
    generate=generate_special_sequences_higher,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_special_sequences_higher,
)
