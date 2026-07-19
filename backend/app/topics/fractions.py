import math
import random
from fractions import Fraction

from app.core.models import Question, Tier
from app.topics.base import TopicDefinition

SECTION = "number"
GROUP = "Fractions"


def _fmt_fraction(f: Fraction) -> str:
    if f.denominator == 1:
        return str(f.numerator)
    return f"{f.numerator}/{f.denominator}"


def generate_simplify_fraction(tier: Tier, rng: random.Random) -> Question:
    while True:
        p = rng.randint(1, 11)
        q = rng.randint(2, 12)
        if p < q and math.gcd(p, q) == 1:
            break
    k = rng.randint(2, 8)
    num, den = p * k, q * k

    hcf = math.gcd(num, den)
    if num // hcf != p or den // hcf != q:
        raise ValueError("simplify_fraction verification failed")

    steps = [
        f"Find the highest common factor of {num} and {den}: {hcf}",
        f"Divide numerator and denominator by {hcf}: {num}÷{hcf} / {den}÷{hcf} = {p}/{q}",
    ]
    return Question(
        topic_id="fractions_simplify",
        tier=Tier.FOUNDATION,
        prompt=f"Simplify the fraction {num}/{den} fully.",
        solution_steps=tuple(steps),
        final_answer=f"{p}/{q}",
        dedup_key=f"simplify:{num}:{den}",
    )


def generate_add_subtract_fractions(tier: Tier, rng: random.Random) -> Question:
    b = rng.randint(2, 12)
    a = rng.randint(1, b - 1)
    d = rng.randint(2, 12)
    c = rng.randint(1, d - 1)
    op = rng.choice(["+", "-"])

    frac1, frac2 = Fraction(a, b), Fraction(c, d)
    if op == "-" and frac1 < frac2:
        a, b, c, d = c, d, a, b
        frac1, frac2 = Fraction(a, b), Fraction(c, d)

    result = frac1 + frac2 if op == "+" else frac1 - frac2

    # Independent verification via plain float arithmetic (separate path from Fraction/LCM logic).
    independent = (a / b) + (c / d) if op == "+" else (a / b) - (c / d)
    if abs(independent - float(result)) > 1e-9:
        raise ValueError("add_subtract_fractions verification failed")

    lcm_val = b * d // math.gcd(b, d)
    scale1, scale2 = lcm_val // b, lcm_val // d
    num1_scaled, num2_scaled = a * scale1, c * scale2
    combined_num = num1_scaled + num2_scaled if op == "+" else num1_scaled - num2_scaled

    steps = [
        f"Find a common denominator: LCM({b}, {d}) = {lcm_val}",
        f"Convert: {a}/{b} = {num1_scaled}/{lcm_val}, {c}/{d} = {num2_scaled}/{lcm_val}",
        f"{'Add' if op == '+' else 'Subtract'}: {num1_scaled}/{lcm_val} {op} {num2_scaled}/{lcm_val} = {combined_num}/{lcm_val}",
        f"Simplify: {_fmt_fraction(result)}",
    ]
    return Question(
        topic_id="fractions_add_subtract",
        tier=Tier.FOUNDATION,
        prompt=f"Work out {a}/{b} {op} {c}/{d}. Give your answer as a fraction in its simplest form.",
        solution_steps=tuple(steps),
        final_answer=_fmt_fraction(result),
        dedup_key=f"add_sub:{a}:{b}:{c}:{d}:{op}",
    )


def generate_multiply_fractions(tier: Tier, rng: random.Random) -> Question:
    a, b = rng.randint(1, 9), rng.randint(2, 12)
    c, d = rng.randint(1, 9), rng.randint(2, 12)
    result = Fraction(a, b) * Fraction(c, d)

    # Independent verification via plain float arithmetic.
    if abs((a / b) * (c / d) - float(result)) > 1e-9:
        raise ValueError("multiply_fractions verification failed")

    steps = [
        f"Multiply numerators: {a} × {c} = {a * c}",
        f"Multiply denominators: {b} × {d} = {b * d}",
        f"Simplify {a * c}/{b * d} = {_fmt_fraction(result)}",
    ]
    return Question(
        topic_id="fractions_multiply",
        tier=Tier.FOUNDATION,
        prompt=f"Work out {a}/{b} × {c}/{d}. Give your answer as a fraction in its simplest form.",
        solution_steps=tuple(steps),
        final_answer=_fmt_fraction(result),
        dedup_key=f"multiply:{a}:{b}:{c}:{d}",
    )


def generate_divide_fractions(tier: Tier, rng: random.Random) -> Question:
    a, b = rng.randint(1, 9), rng.randint(2, 12)
    c, d = rng.randint(1, 9), rng.randint(2, 12)
    result = Fraction(a, b) / Fraction(c, d)

    # Independent verification: re-multiplying by the divisor must reconstruct the dividend exactly.
    if result * Fraction(c, d) != Fraction(a, b):
        raise ValueError("divide_fractions verification failed")

    steps = [
        f"Keep-change-flip: {a}/{b} ÷ {c}/{d} = {a}/{b} × {d}/{c}",
        f"Multiply: ({a}×{d})/({b}×{c}) = {a * d}/{b * c}",
        f"Simplify: {_fmt_fraction(result)}",
    ]
    return Question(
        topic_id="fractions_divide",
        tier=Tier.HIGHER,
        prompt=f"Work out {a}/{b} ÷ {c}/{d}. Give your answer as a fraction in its simplest form.",
        solution_steps=tuple(steps),
        final_answer=_fmt_fraction(result),
        dedup_key=f"divide:{a}:{b}:{c}:{d}",
    )


def generate_mixed_number_arithmetic(tier: Tier, rng: random.Random) -> Question:
    den1 = rng.randint(2, 8)
    num1 = rng.randint(1, den1 - 1)
    whole1 = rng.randint(1, 5)
    den2 = rng.randint(2, 8)
    num2 = rng.randint(1, den2 - 1)
    whole2 = rng.randint(1, 5)
    op = rng.choice(["+", "-"])

    frac1 = Fraction(whole1 * den1 + num1, den1)
    frac2 = Fraction(whole2 * den2 + num2, den2)
    if op == "-" and frac1 < frac2:
        whole1, num1, den1, whole2, num2, den2 = whole2, num2, den2, whole1, num1, den1
        frac1 = Fraction(whole1 * den1 + num1, den1)
        frac2 = Fraction(whole2 * den2 + num2, den2)

    result = frac1 + frac2 if op == "+" else frac1 - frac2

    # Independent verification via plain float arithmetic on the original mixed numbers.
    v1 = whole1 + num1 / den1
    v2 = whole2 + num2 / den2
    independent = v1 + v2 if op == "+" else v1 - v2
    if abs(independent - float(result)) > 1e-9:
        raise ValueError("mixed_number_arithmetic verification failed")

    result_whole = result.numerator // result.denominator
    result_num = result.numerator % result.denominator
    mixed_str = str(result_whole) if result_num == 0 else f"{result_whole} {result_num}/{result.denominator}"

    steps = [
        f"Convert to improper fractions: {whole1} {num1}/{den1} = {frac1.numerator}/{frac1.denominator}, "
        f"{whole2} {num2}/{den2} = {frac2.numerator}/{frac2.denominator}",
        f"{'Add' if op == '+' else 'Subtract'} the improper fractions: "
        f"{frac1.numerator}/{frac1.denominator} {op} {frac2.numerator}/{frac2.denominator} = "
        f"{result.numerator}/{result.denominator}",
        f"Convert back to a mixed number: {mixed_str}",
    ]
    return Question(
        topic_id="fractions_mixed_number_arithmetic",
        tier=Tier.HIGHER,
        prompt=(
            f"Work out {whole1} {num1}/{den1} {op} {whole2} {num2}/{den2}. "
            "Give your answer as a mixed number."
        ),
        solution_steps=tuple(steps),
        final_answer=mixed_str,
        dedup_key=f"mixed:{whole1}:{num1}:{den1}:{whole2}:{num2}:{den2}:{op}",
    )


TOPIC_SIMPLIFY = TopicDefinition(
    id="fractions_simplify",
    display_name="Simplifying Fractions",
    description="Reduce a fraction to its simplest form.",
    generate=generate_simplify_fraction,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
)

TOPIC_ADD_SUBTRACT = TopicDefinition(
    id="fractions_add_subtract",
    display_name="Adding & Subtracting Fractions",
    description="Add or subtract fractions with different denominators.",
    generate=generate_add_subtract_fractions,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
)

TOPIC_MULTIPLY = TopicDefinition(
    id="fractions_multiply",
    display_name="Multiplying Fractions",
    description="Multiply two fractions and simplify the result.",
    generate=generate_multiply_fractions,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
)

TOPIC_DIVIDE = TopicDefinition(
    id="fractions_divide",
    display_name="Dividing Fractions",
    description="Divide two fractions using keep-change-flip.",
    generate=generate_divide_fractions,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
)

TOPIC_MIXED_NUMBER_ARITHMETIC = TopicDefinition(
    id="fractions_mixed_number_arithmetic",
    display_name="Mixed Number Arithmetic",
    description="Add or subtract mixed numbers with different denominators.",
    generate=generate_mixed_number_arithmetic,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
)
