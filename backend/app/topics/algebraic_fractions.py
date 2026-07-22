import random

import sympy as sp

from app.core.models import ModelledExample, Question, Tier
from app.topics.algebra_utils import X, fmt_linear
from app.topics.base import TopicDefinition

SECTION = "algebra"
GROUP = "Algebraic Fractions"


def _rand_nonzero(rng: random.Random, lo: int, hi: int) -> int:
    while True:
        v = rng.randint(lo, hi)
        if v != 0:
            return v


def _fmt_binom(a: int) -> str:
    """Render (x + a) or (x - a), for the linear factor x + a."""
    if a > 0:
        return f"(x + {a})"
    if a < 0:
        return f"(x - {-a})"
    return "x"


def generate_algebraic_fractions_add_subtract(tier: Tier, rng: random.Random) -> Question:
    p = rng.randint(1, 9)
    q = rng.randint(1, 9)
    a = _rand_nonzero(rng, -8, 8)
    b = _rand_nonzero(rng, -8, 8)
    while b == a:
        b = _rand_nonzero(rng, -8, 8)
    op = rng.choice(["+", "-"])
    sign = 1 if op == "+" else -1

    # Combine over the common denominator (x+a)(x+b): the numerator is
    # p(x+b) +/- q(x+a).
    new_coeff = p + sign * q
    new_const = p * b + sign * q * a

    # Independent verification: build both sides as sympy expressions over
    # the symbol X and confirm their difference simplifies to 0 - a
    # genuinely different computation path than the manual combine above.
    lhs = sp.Rational(p, 1) / (X + a) + sign * sp.Rational(q, 1) / (X + b)
    rhs = (new_coeff * X + new_const) / ((X + a) * (X + b))
    if sp.simplify(lhs - rhs) != 0:
        raise ValueError("algebraic_fractions_add_subtract verification failed")

    numerator_str = fmt_linear(new_coeff, new_const)
    denom_str = f"{_fmt_binom(a)}{_fmt_binom(b)}"
    answer = f"({numerator_str})/{denom_str}"

    prompt = f"Simplify {p}/{_fmt_binom(a)} {op} {q}/{_fmt_binom(b)}, giving your answer as a single fraction."
    steps = [
        f"Write both fractions over the common denominator {denom_str}:",
        f"{p}/{_fmt_binom(a)} {op} {q}/{_fmt_binom(b)} = ({p}{_fmt_binom(b)} {op} {q}{_fmt_binom(a)})/{denom_str}",
        f"Expand the numerator: {p}{_fmt_binom(b)} {op} {q}{_fmt_binom(a)} = {numerator_str}",
        f"= {answer}",
    ]
    return Question(
        topic_id="algebraic_fractions_add_subtract",
        tier=Tier.HIGHER,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"algfrac_addsub:{p}:{q}:{a}:{b}:{op}",
    )


def generate_algebraic_fractions_multiply_divide(tier: Tier, rng: random.Random) -> Question:
    d = _rand_nonzero(rng, 2, 9)
    s = _rand_nonzero(rng, -8, 8)
    while s == d or s == -d:
        s = _rand_nonzero(rng, -8, 8)
    op = rng.choice(["×", "÷"])

    d2 = d * d
    frac1_num = f"(x^2 - {d2})"
    frac1_den = _fmt_binom(s)

    if op == "×":
        frac2_num = _fmt_binom(s)
        frac2_den = _fmt_binom(-d)
        combined = (X**2 - d2) / (X + s) * (X + s) / (X - d)
    else:
        frac2_num = _fmt_binom(-d)
        frac2_den = _fmt_binom(s)
        combined = ((X**2 - d2) / (X + s)) / ((X - d) / (X + s))

    # Independent verification: build the original combined expression and
    # the claimed simplified result as sympy expressions over X and confirm
    # their difference simplifies to 0.
    answer_expr = X + d
    if sp.simplify(combined - answer_expr) != 0:
        raise ValueError("algebraic_fractions_multiply_divide verification failed")

    answer = fmt_linear(1, d)
    prompt = f"Simplify {frac1_num}/{frac1_den} {op} {frac2_num}/{frac2_den}, giving your answer in its simplest form."

    steps = [f"Factorise the difference of two squares: {frac1_num} = {_fmt_binom(-d)}{_fmt_binom(d)}"]
    if op == "÷":
        steps.append(
            f"Dividing by a fraction means multiplying by its reciprocal: "
            f"÷ {frac2_num}/{frac2_den} becomes × {frac2_den}/{frac2_num}"
        )
        steps.append(f"{_fmt_binom(-d)}{_fmt_binom(d)}/{frac1_den} × {frac2_den}/{frac2_num}")
    else:
        steps.append(f"{_fmt_binom(-d)}{_fmt_binom(d)}/{frac1_den} × {frac2_num}/{frac2_den}")
    steps.append(f"Cancel the common factors {frac1_den} and {_fmt_binom(-d)}:")
    steps.append(f"= {answer}")

    return Question(
        topic_id="algebraic_fractions_multiply_divide",
        tier=Tier.HIGHER,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"algfrac_muldiv:{d}:{s}:{op}",
    )


def generate_modelled_example_algebraic_fractions_add_subtract(tier: Tier, rng: random.Random) -> ModelledExample:
    p = rng.randint(1, 9)
    q = rng.randint(1, 9)
    a = _rand_nonzero(rng, -8, 8)
    b = _rand_nonzero(rng, -8, 8)
    while b == a:
        b = _rand_nonzero(rng, -8, 8)
    op = rng.choice(["+", "-"])
    sign = 1 if op == "+" else -1

    new_coeff = p + sign * q
    new_const = p * b + sign * q * a

    lhs = sp.Rational(p, 1) / (X + a) + sign * sp.Rational(q, 1) / (X + b)
    rhs = (new_coeff * X + new_const) / ((X + a) * (X + b))
    if sp.simplify(lhs - rhs) != 0:
        raise ValueError("modelled example algebraic_fractions_add_subtract verification failed")

    numerator_str = fmt_linear(new_coeff, new_const)
    denom_str = f"{_fmt_binom(a)}{_fmt_binom(b)}"
    answer = f"({numerator_str})/{denom_str}"

    prompt = f"Simplify {p}/{_fmt_binom(a)} {op} {q}/{_fmt_binom(b)}, giving your answer as a single fraction."

    teaching_steps = [
        "Fractions can only be added or subtracted once they share a common denominator - and for two "
        f"algebraic fractions with different linear denominators like {_fmt_binom(a)} and {_fmt_binom(b)}, "
        f"the common denominator is simply their product, {denom_str}.",
        f"Multiply each fraction so it has that common denominator: {p}/{_fmt_binom(a)} becomes "
        f"{p}{_fmt_binom(b)}/{denom_str} (multiplying top and bottom by {_fmt_binom(b)}), and "
        f"{q}/{_fmt_binom(b)} becomes {q}{_fmt_binom(a)}/{denom_str} (multiplying top and bottom by "
        f"{_fmt_binom(a)}).",
        f"With a shared denominator, the fractions can now be combined into one: "
        f"({p}{_fmt_binom(b)} {op} {q}{_fmt_binom(a)})/{denom_str}.",
        f"Expand and collect like terms in the numerator: {p}{_fmt_binom(b)} {op} {q}{_fmt_binom(a)} "
        f"simplifies to {numerator_str}.",
        f"The denominator is left factorised rather than expanded out, since that's the standard way to "
        f"present an algebraic fraction answer: {answer}.",
    ]
    worked_calculation = [
        f"{p}/{_fmt_binom(a)} {op} {q}/{_fmt_binom(b)}",
        f"= ({p}{_fmt_binom(b)} {op} {q}{_fmt_binom(a)})/{denom_str}",
        f"= {answer}",
    ]
    return ModelledExample(
        topic_id="algebraic_fractions_add_subtract",
        tier=Tier.HIGHER,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
    )


def generate_modelled_example_algebraic_fractions_multiply_divide(tier: Tier, rng: random.Random) -> ModelledExample:
    d = _rand_nonzero(rng, 2, 9)
    s = _rand_nonzero(rng, -8, 8)
    while s == d or s == -d:
        s = _rand_nonzero(rng, -8, 8)
    op = rng.choice(["×", "÷"])

    d2 = d * d
    frac1_num = f"(x^2 - {d2})"
    frac1_den = _fmt_binom(s)

    if op == "×":
        frac2_num = _fmt_binom(s)
        frac2_den = _fmt_binom(-d)
        combined = (X**2 - d2) / (X + s) * (X + s) / (X - d)
    else:
        frac2_num = _fmt_binom(-d)
        frac2_den = _fmt_binom(s)
        combined = ((X**2 - d2) / (X + s)) / ((X - d) / (X + s))

    answer_expr = X + d
    if sp.simplify(combined - answer_expr) != 0:
        raise ValueError("modelled example algebraic_fractions_multiply_divide verification failed")

    answer = fmt_linear(1, d)
    prompt = f"Simplify {frac1_num}/{frac1_den} {op} {frac2_num}/{frac2_den}, giving your answer in its simplest form."

    op_explainer = (
        f"Dividing by a fraction means multiplying by its reciprocal (flip it upside down), so "
        f"÷ {frac2_num}/{frac2_den} becomes × {frac2_den}/{frac2_num}."
        if op == "÷"
        else "Multiplying two fractions together just means multiplying the numerators together and the "
        "denominators together."
    )
    written_out = (
        f"Writing everything out: {_fmt_binom(-d)}{_fmt_binom(d)}/{frac1_den} × {frac2_den}/{frac2_num}"
        if op == "÷"
        else f"Writing everything out: {_fmt_binom(-d)}{_fmt_binom(d)}/{frac1_den} × {frac2_num}/{frac2_den}"
    )
    teaching_steps = [
        f"Before multiplying anything out, always check whether either numerator or denominator "
        f"factorises - here {frac1_num} is a difference of two squares, since {d2} = {d}^2, so it "
        f"factors as {_fmt_binom(-d)}{_fmt_binom(d)}.",
        op_explainer,
        written_out,
        f"Before multiplying across, look for factors common to a numerator and a denominator that can "
        f"be cancelled first - here {frac1_den} appears in one denominator and one numerator, and "
        f"{_fmt_binom(-d)} appears in one numerator and one denominator, so both cancel completely.",
        f"After cancelling, all that remains is {answer}.",
    ]
    worked_calculation = [
        f"{frac1_num} = {_fmt_binom(-d)}{_fmt_binom(d)}",
        f"{frac1_num}/{frac1_den} {op} {frac2_num}/{frac2_den}",
        f"= {answer}",
    ]
    return ModelledExample(
        topic_id="algebraic_fractions_multiply_divide",
        tier=Tier.HIGHER,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
    )


TOPIC_ALGEBRAIC_FRACTIONS_ADD_SUBTRACT = TopicDefinition(
    id="algebraic_fractions_add_subtract",
    display_name="Adding and Subtracting Algebraic Fractions",
    description="Combine two algebraic fractions with linear denominators into a single simplified fraction.",
    generate=generate_algebraic_fractions_add_subtract,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_algebraic_fractions_add_subtract,
)

TOPIC_ALGEBRAIC_FRACTIONS_MULTIPLY_DIVIDE = TopicDefinition(
    id="algebraic_fractions_multiply_divide",
    display_name="Multiplying and Dividing Algebraic Fractions",
    description="Multiply or divide algebraic fractions, factorising and cancelling common factors.",
    generate=generate_algebraic_fractions_multiply_divide,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_algebraic_fractions_multiply_divide,
)
