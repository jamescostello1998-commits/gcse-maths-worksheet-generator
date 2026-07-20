import math
import random
from fractions import Fraction

from app.core.models import ModelledExample, Question, Tier
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


def generate_fraction_of_amount(tier: Tier, rng: random.Random) -> Question:
    b = rng.randint(2, 10)
    a = rng.randint(1, b - 1)
    amount = b * rng.randint(2, 40)
    unit = amount // b
    result = unit * a

    # Independent check via exact Fraction arithmetic (a different path than the
    # integer divide-then-multiply used to build the steps above).
    check = Fraction(a, b) * amount
    if check != result:
        raise ValueError("fraction_of_amount verification failed")

    steps = [
        f"Divide by the denominator: {amount} ÷ {b} = {unit}",
        f"Multiply by the numerator: {unit} × {a} = {result}",
    ]
    return Question(
        topic_id="fractions_of_amount",
        tier=Tier.FOUNDATION,
        prompt=f"Find {a}/{b} of {amount}.",
        solution_steps=tuple(steps),
        final_answer=str(result),
        dedup_key=f"frac_of_amount:{a}:{b}:{amount}",
    )


def generate_modelled_example_add_subtract(tier: Tier, rng: random.Random) -> ModelledExample:
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
    independent = (a / b) + (c / d) if op == "+" else (a / b) - (c / d)
    if abs(independent - float(result)) > 1e-9:
        raise ValueError("modelled example add_subtract_fractions verification failed")

    lcm_val = b * d // math.gcd(b, d)
    scale1, scale2 = lcm_val // b, lcm_val // d
    num1_scaled, num2_scaled = a * scale1, c * scale2
    combined_num = num1_scaled + num2_scaled if op == "+" else num1_scaled - num2_scaled
    common_gcd = math.gcd(abs(combined_num), lcm_val)

    verb = "add" if op == "+" else "subtract"
    teaching_steps = [
        f"We want to {verb} {a}/{b} {op} {c}/{d}. Fractions can only be added or subtracted once "
        "they share the same denominator, so the first job is always to find a common one.",
        f"The lowest common denominator of {b} and {d} is their LCM: {lcm_val}.",
        f"Convert each fraction to an equivalent fraction with denominator {lcm_val}: multiply "
        f"{a}/{b} by {scale1}/{scale1} to get {num1_scaled}/{lcm_val}, and multiply {c}/{d} by "
        f"{scale2}/{scale2} to get {num2_scaled}/{lcm_val}.",
        f"Now that the denominators match, {verb} the numerators and keep the denominator the same: "
        f"{num1_scaled}/{lcm_val} {op} {num2_scaled}/{lcm_val} = {combined_num}/{lcm_val}.",
        "Finally, check whether the fraction can be simplified: "
        + (
            f"dividing both {combined_num} and {lcm_val} by their highest common factor, "
            f"{common_gcd}, gives {_fmt_fraction(result)}."
            if common_gcd > 1
            else f"{combined_num} and {lcm_val} share no common factor, so {_fmt_fraction(result)} "
            "is already in its simplest form."
        ),
    ]
    worked_calculation = [
        f"{a}/{b} {op} {c}/{d}",
        f"= {num1_scaled}/{lcm_val} {op} {num2_scaled}/{lcm_val}",
        f"= {combined_num}/{lcm_val}",
    ]
    if common_gcd > 1:
        worked_calculation.append(f"= {_fmt_fraction(result)}")

    return ModelledExample(
        topic_id="fractions_add_subtract",
        tier=Tier.FOUNDATION,
        prompt=f"Work out {a}/{b} {op} {c}/{d}. Give your answer as a fraction in its simplest form.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=_fmt_fraction(result),
    )


def generate_modelled_example_simplify_fraction(tier: Tier, rng: random.Random) -> ModelledExample:
    while True:
        p = rng.randint(1, 11)
        q = rng.randint(2, 12)
        if p < q and math.gcd(p, q) == 1:
            break
    k = rng.randint(2, 8)
    num, den = p * k, q * k

    hcf = math.gcd(num, den)
    if num // hcf != p or den // hcf != q:
        raise ValueError("modelled example simplify_fraction verification failed")

    teaching_steps = [
        f"A fraction is in its simplest form when there's no whole number bigger than 1 that divides "
        f"exactly into both the numerator and the denominator. To simplify {num}/{den}, we need to find "
        "the highest common factor (HCF) of the two numbers.",
        f"The highest common factor of {num} and {den} is {hcf} — the largest number that divides "
        f"exactly into both of them.",
        "Dividing the numerator and denominator by the SAME number keeps the fraction's value exactly "
        f"the same (it's the same as multiplying by {hcf}/{hcf}, which equals 1), so we divide both "
        f"{num} and {den} by {hcf}.",
        f"{num} ÷ {hcf} = {p} and {den} ÷ {hcf} = {q}, and since {p} and {q} share no common factor "
        f"other than 1, {p}/{q} is fully simplified.",
    ]
    worked_calculation = [
        f"{num}/{den}",
        f"HCF({num}, {den}) = {hcf}",
        f"= ({num}÷{hcf})/({den}÷{hcf})",
        f"= {p}/{q}",
    ]
    return ModelledExample(
        topic_id="fractions_simplify",
        tier=Tier.FOUNDATION,
        prompt=f"Simplify the fraction {num}/{den} fully.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{p}/{q}",
    )


def generate_modelled_example_multiply_fractions(tier: Tier, rng: random.Random) -> ModelledExample:
    a, b = rng.randint(1, 9), rng.randint(2, 12)
    c, d = rng.randint(1, 9), rng.randint(2, 12)
    result = Fraction(a, b) * Fraction(c, d)

    if abs((a / b) * (c / d) - float(result)) > 1e-9:
        raise ValueError("modelled example multiply_fractions verification failed")

    product_num, product_den = a * c, b * d
    common = math.gcd(product_num, product_den)

    teaching_steps = [
        "Multiplying fractions is more direct than adding them — there's no need for a common "
        f"denominator. To work out {a}/{b} × {c}/{d}, multiply the two numerators together and the "
        "two denominators together separately.",
        f"Numerators: {a} × {c} = {product_num}. Denominators: {b} × {d} = {product_den}. This gives "
        f"{product_num}/{product_den}.",
        "Finally, check whether the fraction can be simplified: "
        + (
            f"dividing both {product_num} and {product_den} by their highest common factor, {common}, "
            f"gives {_fmt_fraction(result)}."
            if common > 1
            else f"{product_num} and {product_den} share no common factor, so {_fmt_fraction(result)} "
            "is already in its simplest form."
        ),
        f"So {a}/{b} × {c}/{d} = {_fmt_fraction(result)}.",
    ]
    worked_calculation = [
        f"{a}/{b} × {c}/{d}",
        f"= ({a}×{c})/({b}×{d})",
        f"= {product_num}/{product_den}",
    ]
    if common > 1:
        worked_calculation.append(f"= {_fmt_fraction(result)}")

    return ModelledExample(
        topic_id="fractions_multiply",
        tier=Tier.FOUNDATION,
        prompt=f"Work out {a}/{b} × {c}/{d}. Give your answer as a fraction in its simplest form.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=_fmt_fraction(result),
    )


def generate_modelled_example_divide_fractions(tier: Tier, rng: random.Random) -> ModelledExample:
    a, b = rng.randint(1, 9), rng.randint(2, 12)
    c, d = rng.randint(1, 9), rng.randint(2, 12)
    result = Fraction(a, b) / Fraction(c, d)

    if result * Fraction(c, d) != Fraction(a, b):
        raise ValueError("modelled example divide_fractions verification failed")

    product_num, product_den = a * d, b * c
    common = math.gcd(product_num, product_den)

    teaching_steps = [
        "Dividing by a fraction is the same as multiplying by its reciprocal (the fraction flipped "
        f"upside down). This is often remembered as 'keep, change, flip': keep {a}/{b} as it is, "
        f"change ÷ to ×, and flip {c}/{d} to become {d}/{c}.",
        f"So {a}/{b} ÷ {c}/{d} becomes the multiplication {a}/{b} × {d}/{c}.",
        f"Now multiply straight across: numerators {a} × {d} = {product_num}, denominators "
        f"{b} × {c} = {product_den}, giving {product_num}/{product_den}.",
        "Finally, simplify: "
        + (
            f"dividing both {product_num} and {product_den} by their highest common factor, {common}, "
            f"gives {_fmt_fraction(result)}."
            if common > 1
            else f"{product_num} and {product_den} share no common factor, so {_fmt_fraction(result)} "
            "is already in its simplest form."
        ),
    ]
    worked_calculation = [
        f"{a}/{b} ÷ {c}/{d}",
        f"= {a}/{b} × {d}/{c}",
        f"= ({a}×{d})/({b}×{c})",
        f"= {product_num}/{product_den}",
    ]
    if common > 1:
        worked_calculation.append(f"= {_fmt_fraction(result)}")

    return ModelledExample(
        topic_id="fractions_divide",
        tier=Tier.HIGHER,
        prompt=f"Work out {a}/{b} ÷ {c}/{d}. Give your answer as a fraction in its simplest form.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=_fmt_fraction(result),
    )


def generate_modelled_example_mixed_number_arithmetic(tier: Tier, rng: random.Random) -> ModelledExample:
    den1 = rng.randint(2, 8)
    num1 = rng.randint(1, den1 - 1)
    whole1 = rng.randint(1, 5)
    den2 = rng.randint(2, 8)
    num2 = rng.randint(1, den2 - 1)
    whole2 = rng.randint(1, 5)
    op = rng.choice(["+", "-"])

    v1 = whole1 + num1 / den1
    v2 = whole2 + num2 / den2
    if op == "-" and v1 < v2:
        whole1, num1, den1, whole2, num2, den2 = whole2, num2, den2, whole1, num1, den1
        v1 = whole1 + num1 / den1
        v2 = whole2 + num2 / den2

    raw_num1 = whole1 * den1 + num1
    raw_num2 = whole2 * den2 + num2
    lcm_val = den1 * den2 // math.gcd(den1, den2)
    scale1, scale2 = lcm_val // den1, lcm_val // den2
    scaled_num1, scaled_num2 = raw_num1 * scale1, raw_num2 * scale2
    combined_num = scaled_num1 + scaled_num2 if op == "+" else scaled_num1 - scaled_num2
    result = Fraction(combined_num, lcm_val)

    # Independent verification via plain float arithmetic on the original mixed numbers.
    independent = v1 + v2 if op == "+" else v1 - v2
    if abs(independent - float(result)) > 1e-9:
        raise ValueError("modelled example mixed_number_arithmetic verification failed")

    result_whole = result.numerator // result.denominator
    result_num = result.numerator % result.denominator
    mixed_str = str(result_whole) if result_num == 0 else f"{result_whole} {result_num}/{result.denominator}"

    verb = "add" if op == "+" else "subtract"
    teaching_steps = [
        "Mixed numbers combine a whole number with a fraction, which makes them awkward to add or "
        "subtract directly, so the standard method is to first convert both into improper (top-heavy) "
        "fractions: multiply the whole number by the denominator, then add the numerator, all over the "
        "same denominator.",
        f"{whole1} {num1}/{den1} = ({whole1}×{den1}+{num1})/{den1} = {raw_num1}/{den1}, and "
        f"{whole2} {num2}/{den2} = ({whole2}×{den2}+{num2})/{den2} = {raw_num2}/{den2}.",
        f"Now it's a normal fraction {verb}, so we need a common denominator: the LCM of {den1} and "
        f"{den2} is {lcm_val}. Converting: {raw_num1}/{den1} = {scaled_num1}/{lcm_val} and "
        f"{raw_num2}/{den2} = {scaled_num2}/{lcm_val}.",
        f"{'Add' if op == '+' else 'Subtract'} the numerators over the common denominator: "
        f"{scaled_num1}/{lcm_val} {op} {scaled_num2}/{lcm_val} = {combined_num}/{lcm_val}.",
        f"Finally, convert the improper fraction back to a mixed number by dividing {combined_num} by "
        f"{lcm_val}: this gives {mixed_str}.",
    ]
    worked_calculation = [
        f"{whole1} {num1}/{den1} {op} {whole2} {num2}/{den2}",
        f"= {raw_num1}/{den1} {op} {raw_num2}/{den2}",
        f"= {scaled_num1}/{lcm_val} {op} {scaled_num2}/{lcm_val}",
        f"= {combined_num}/{lcm_val}",
        f"= {mixed_str}",
    ]
    return ModelledExample(
        topic_id="fractions_mixed_number_arithmetic",
        tier=Tier.HIGHER,
        prompt=(
            f"Work out {whole1} {num1}/{den1} {op} {whole2} {num2}/{den2}. "
            "Give your answer as a mixed number."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=mixed_str,
    )


def generate_modelled_example_fraction_of_amount(tier: Tier, rng: random.Random) -> ModelledExample:
    b = rng.randint(2, 10)
    a = rng.randint(1, b - 1)
    amount = b * rng.randint(2, 40)
    unit = amount // b
    result = unit * a

    # Independent check via exact Fraction arithmetic (a different path than the
    # integer divide-then-multiply used to build the steps above).
    check = Fraction(a, b) * amount
    if check != result:
        raise ValueError("modelled example fraction_of_amount verification failed")

    teaching_steps = [
        f"Finding {a}/{b} of {amount} means splitting {amount} into {b} equal parts (the denominator "
        f"tells us how many parts to split into), then taking {a} of those parts (the numerator tells "
        "us how many to take).",
        f"Divide the amount by the denominator to find the value of one single part: "
        f"{amount} ÷ {b} = {unit}.",
        f"Multiply that single part by the numerator to find {a} parts: {unit} × {a} = {result}.",
        f"So {a}/{b} of {amount} is {result}.",
    ]
    worked_calculation = [
        f"{a}/{b} of {amount}",
        f"= {amount} ÷ {b} × {a}",
        f"= {unit} × {a}",
        f"= {result}",
    ]
    return ModelledExample(
        topic_id="fractions_of_amount",
        tier=Tier.FOUNDATION,
        prompt=f"Find {a}/{b} of {amount}.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=str(result),
    )


TOPIC_SIMPLIFY = TopicDefinition(
    id="fractions_simplify",
    display_name="Simplifying Fractions",
    description="Reduce a fraction to its simplest form.",
    generate=generate_simplify_fraction,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_simplify_fraction,
)

TOPIC_ADD_SUBTRACT = TopicDefinition(
    id="fractions_add_subtract",
    display_name="Adding & Subtracting Fractions",
    description="Add or subtract fractions with different denominators.",
    generate=generate_add_subtract_fractions,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_add_subtract,
)

TOPIC_MULTIPLY = TopicDefinition(
    id="fractions_multiply",
    display_name="Multiplying Fractions",
    description="Multiply two fractions and simplify the result.",
    generate=generate_multiply_fractions,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_multiply_fractions,
)

TOPIC_DIVIDE = TopicDefinition(
    id="fractions_divide",
    display_name="Dividing Fractions",
    description="Divide two fractions using keep-change-flip.",
    generate=generate_divide_fractions,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_divide_fractions,
)

TOPIC_MIXED_NUMBER_ARITHMETIC = TopicDefinition(
    id="fractions_mixed_number_arithmetic",
    display_name="Mixed Number Arithmetic",
    description="Add or subtract mixed numbers with different denominators.",
    generate=generate_mixed_number_arithmetic,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_mixed_number_arithmetic,
)

TOPIC_OF_AMOUNT = TopicDefinition(
    id="fractions_of_amount",
    display_name="Fractions of an Amount",
    description="Find a fraction of a given amount.",
    generate=generate_fraction_of_amount,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_fraction_of_amount,
)
