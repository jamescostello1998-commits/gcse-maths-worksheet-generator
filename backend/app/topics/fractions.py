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


def generate_divide_fractions_foundation(tier: Tier, rng: random.Random) -> Question:
    a, b = rng.randint(1, 6), rng.randint(2, 8)
    c, d = rng.randint(1, 6), rng.randint(2, 8)
    result = Fraction(a, b) / Fraction(c, d)

    # Independent verification: re-multiplying by the divisor must reconstruct the dividend exactly.
    if result * Fraction(c, d) != Fraction(a, b):
        raise ValueError("divide_fractions_foundation verification failed")

    steps = [
        f"Keep-change-flip: {a}/{b} ÷ {c}/{d} = {a}/{b} × {d}/{c}",
        f"Multiply: ({a}×{d})/({b}×{c}) = {a * d}/{b * c}",
        f"Simplify: {_fmt_fraction(result)}",
    ]
    return Question(
        topic_id="fractions_divide_foundation",
        tier=Tier.FOUNDATION,
        prompt=f"Work out {a}/{b} ÷ {c}/{d}. Give your answer as a fraction in its simplest form.",
        solution_steps=tuple(steps),
        final_answer=_fmt_fraction(result),
        dedup_key=f"divide_f:{a}:{b}:{c}:{d}",
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


def generate_fractions_equivalent(tier: Tier, rng: random.Random) -> Question:
    shape = rng.choice(["missing_numerator", "identify_equivalent"])

    if shape == "missing_numerator":
        b = rng.randint(2, 10)
        a = rng.randint(1, b - 1)
        while math.gcd(a, b) != 1:
            a = rng.randint(1, b - 1)
        k = rng.randint(2, 9)
        d = b * k
        missing_num = a * k

        # Independent verification via cross-multiplication - a different check than the
        # scale-factor multiplication used to build the answer.
        if a * d != missing_num * b:
            raise ValueError("fractions_equivalent (missing_numerator) verification failed")

        steps = [
            f"Find the scale factor between the denominators: {d} ÷ {b} = {k}",
            f"Multiply the numerator by the same scale factor: {a} × {k} = {missing_num}",
        ]
        return Question(
            topic_id="fractions_equivalent",
            tier=Tier.FOUNDATION,
            prompt=f"{a}/{b} = ?/{d}. Find the missing numerator.",
            solution_steps=tuple(steps),
            final_answer=str(missing_num),
            dedup_key=f"equiv_num:{a}:{b}:{d}",
        )

    # identify_equivalent: build 3 non-equivalent distractors alongside the genuine
    # equivalent fraction, verifying via cross-multiplication that exactly one candidate
    # is a true equivalent.
    b = rng.randint(2, 10)
    a = rng.randint(1, b - 1)
    while math.gcd(a, b) != 1:
        a = rng.randint(1, b - 1)
    k = rng.randint(2, 6)
    correct = (a * k, b * k)

    distractors: set[tuple[int, int]] = set()
    attempts = 0
    while len(distractors) < 3 and attempts < 200:
        attempts += 1
        kind = rng.choice(["off_num", "off_den", "mismatched_scale"])
        if kind == "off_num":
            cand = (correct[0] + rng.choice([-1, 1]), correct[1])
        elif kind == "off_den":
            delta = rng.choice([-1, 1])
            new_den = correct[1] + delta
            if new_den <= 1:
                continue
            cand = (correct[0], new_den)
        else:
            k2 = rng.randint(2, 9)
            k3 = k2 + rng.choice([-1, 1])
            if k3 < 1:
                continue
            cand = (a * k2, b * k3)
        num, den = cand
        if num <= 0 or den <= 1 or cand == correct or cand in distractors:
            continue
        if a * den == num * b:
            continue  # accidentally equivalent - reject and try again
        distractors.add(cand)

    if len(distractors) < 3:
        raise ValueError("fractions_equivalent could not build distinct distractors")

    candidates = [correct] + list(distractors)[:3]
    rng.shuffle(candidates)

    # Independent verification: exactly one candidate must satisfy the cross-multiplication test.
    equivalent_flags = [a * den == num * b for num, den in candidates]
    if sum(equivalent_flags) != 1:
        raise ValueError("fractions_equivalent (identify_equivalent) verification failed")
    correct_index = equivalent_flags.index(True)

    letters = ["A", "B", "C", "D"]
    options_str = ", ".join(f"{letters[i]}) {n}/{d}" for i, (n, d) in enumerate(candidates))
    correct_letter = letters[correct_index]
    correct_num, correct_den = candidates[correct_index]

    steps = [
        f"Cross-multiply {a}/{b} against each option: a candidate p/q is equivalent only if {a} × q = p × {b}.",
        f"Only option {correct_letter}) {correct_num}/{correct_den} works: "
        f"{a} × {correct_den} = {correct_num} × {b} = {a * correct_den}.",
    ]
    return Question(
        topic_id="fractions_equivalent",
        tier=Tier.FOUNDATION,
        prompt=f"Which of the following fractions is equivalent to {a}/{b}? {options_str}",
        solution_steps=tuple(steps),
        final_answer=f"{correct_letter}) {correct_num}/{correct_den}",
        dedup_key=f"equiv_id:{a}:{b}:{sorted(candidates)}",
    )


def generate_fractions_ordering(tier: Tier, rng: random.Random) -> Question:
    n = rng.choice([4, 5])
    fracs: list[Fraction] = []
    used_dens: set[int] = set()
    attempts = 0
    while len(fracs) < n and attempts < 300:
        attempts += 1
        den = rng.randint(2, 12)
        if den in used_dens:
            continue
        num = rng.randint(1, den - 1)
        val = Fraction(num, den)
        if val in fracs:
            continue
        used_dens.add(den)
        fracs.append(val)
    if len(fracs) < n:
        raise ValueError("fractions_ordering could not generate enough distinct fractions")

    direction = rng.choice(["ascending", "descending"])
    order = sorted(fracs, reverse=(direction == "descending"))

    # Independent verification: convert every fraction to a common denominator (the LCM of
    # all denominators) and order by the resulting numerators - a different method than
    # directly comparing Fraction objects.
    lcm_val = 1
    for f in fracs:
        lcm_val = lcm_val * f.denominator // math.gcd(lcm_val, f.denominator)
    scaled = [(f.numerator * (lcm_val // f.denominator), f) for f in fracs]
    scaled_sorted = sorted(scaled, key=lambda pair: pair[0], reverse=(direction == "descending"))
    order_via_lcm = [f for _, f in scaled_sorted]
    if order_via_lcm != order:
        raise ValueError("fractions_ordering verification failed")

    display_strs = [_fmt_fraction(f) for f in fracs]
    ordered_strs = [_fmt_fraction(f) for f in order]
    common_form = ", ".join(
        f"{_fmt_fraction(f)} = {f.numerator * (lcm_val // f.denominator)}/{lcm_val}" for f in fracs
    )
    direction_words = "smallest to largest" if direction == "ascending" else "largest to smallest"

    steps = [
        f"Convert every fraction to the same denominator, the LCM of "
        f"{', '.join(str(f.denominator) for f in fracs)}: {lcm_val}",
        f"Rewrite each fraction over {lcm_val}: {common_form}",
        f"Order the numerators {direction_words.replace('smallest to largest', 'from smallest to largest').replace('largest to smallest', 'from largest to smallest')} "
        f"and convert back: {', '.join(ordered_strs)}",
    ]
    return Question(
        topic_id="fractions_ordering",
        tier=Tier.FOUNDATION,
        prompt=f"Write these fractions in order, {direction_words}: {', '.join(display_strs)}",
        solution_steps=tuple(steps),
        final_answer=", ".join(ordered_strs),
        dedup_key=f"order:{[(f.numerator, f.denominator) for f in fracs]}:{direction}",
    )


def generate_fractions_improper_mixed(tier: Tier, rng: random.Random) -> Question:
    shape = rng.choice(["to_mixed", "to_improper"])
    den = rng.randint(2, 10)
    whole = rng.randint(1, 6)
    num = rng.randint(1, den - 1)
    while math.gcd(num, den) != 1:
        num = rng.randint(1, den - 1)

    improper_num = whole * den + num

    # Independent verification: convert forward then back and confirm the round trip
    # reproduces the original whole number and remainder numerator exactly.
    check_whole, check_num = divmod(improper_num, den)
    if check_whole != whole or check_num != num:
        raise ValueError("fractions_improper_mixed verification failed")

    if shape == "to_mixed":
        steps = [
            f"Divide the numerator by the denominator: {improper_num} ÷ {den} = {whole} remainder {num}",
            f"Write as a mixed number: {whole} {num}/{den}",
        ]
        return Question(
            topic_id="fractions_improper_mixed",
            tier=Tier.FOUNDATION,
            prompt=f"Write {improper_num}/{den} as a mixed number.",
            solution_steps=tuple(steps),
            final_answer=f"{whole} {num}/{den}",
            dedup_key=f"imp_to_mixed:{improper_num}:{den}",
        )
    else:
        steps = [
            f"Multiply the whole number by the denominator: {whole} × {den} = {whole * den}",
            f"Add the numerator: {whole * den} + {num} = {improper_num}",
            f"Write over the same denominator: {improper_num}/{den}",
        ]
        return Question(
            topic_id="fractions_improper_mixed",
            tier=Tier.FOUNDATION,
            prompt=f"Write {whole} {num}/{den} as an improper fraction.",
            solution_steps=tuple(steps),
            final_answer=f"{improper_num}/{den}",
            dedup_key=f"mixed_to_imp:{whole}:{num}:{den}",
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


def generate_modelled_example_divide_fractions_foundation(tier: Tier, rng: random.Random) -> ModelledExample:
    a, b = rng.randint(1, 6), rng.randint(2, 8)
    c, d = rng.randint(1, 6), rng.randint(2, 8)
    result = Fraction(a, b) / Fraction(c, d)

    if result * Fraction(c, d) != Fraction(a, b):
        raise ValueError("modelled example divide_fractions_foundation verification failed")

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
        topic_id="fractions_divide_foundation",
        tier=Tier.FOUNDATION,
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


def generate_modelled_example_fractions_equivalent(tier: Tier, rng: random.Random) -> ModelledExample:
    shape = rng.choice(["missing_numerator", "identify_equivalent"])

    if shape == "missing_numerator":
        b = rng.randint(2, 10)
        a = rng.randint(1, b - 1)
        while math.gcd(a, b) != 1:
            a = rng.randint(1, b - 1)
        k = rng.randint(2, 9)
        d = b * k
        missing_num = a * k

        if a * d != missing_num * b:
            raise ValueError("modelled example fractions_equivalent (missing_numerator) verification failed")

        teaching_steps = [
            f"Equivalent fractions represent the same value even though their numerators and "
            f"denominators are different - you get from one to the other by multiplying (or dividing) "
            f"both the top and bottom by the SAME number.",
            f"Here we know the new denominator is {d}, so first work out what {b} was multiplied by to "
            f"become {d}: {d} ÷ {b} = {k}. This {k} is the scale factor.",
            f"Whatever we do to the denominator, we must do to the numerator too, to keep the fraction's "
            f"value unchanged. So multiply the numerator by the same scale factor: {a} × {k} = {missing_num}.",
            f"So {a}/{b} = {missing_num}/{d}.",
        ]
        worked_calculation = [
            f"{a}/{b} = ?/{d}",
            f"{d} ÷ {b} = {k}",
            f"{a} × {k} = {missing_num}",
        ]
        return ModelledExample(
            topic_id="fractions_equivalent",
            tier=Tier.FOUNDATION,
            prompt=f"{a}/{b} = ?/{d}. Find the missing numerator.",
            worked_calculation=tuple(worked_calculation),
            teaching_steps=tuple(teaching_steps),
            final_answer=str(missing_num),
        )

    b = rng.randint(2, 10)
    a = rng.randint(1, b - 1)
    while math.gcd(a, b) != 1:
        a = rng.randint(1, b - 1)
    k = rng.randint(2, 6)
    correct = (a * k, b * k)

    distractors: set[tuple[int, int]] = set()
    attempts = 0
    while len(distractors) < 3 and attempts < 200:
        attempts += 1
        kind = rng.choice(["off_num", "off_den", "mismatched_scale"])
        if kind == "off_num":
            cand = (correct[0] + rng.choice([-1, 1]), correct[1])
        elif kind == "off_den":
            delta = rng.choice([-1, 1])
            new_den = correct[1] + delta
            if new_den <= 1:
                continue
            cand = (correct[0], new_den)
        else:
            k2 = rng.randint(2, 9)
            k3 = k2 + rng.choice([-1, 1])
            if k3 < 1:
                continue
            cand = (a * k2, b * k3)
        num, den = cand
        if num <= 0 or den <= 1 or cand == correct or cand in distractors:
            continue
        if a * den == num * b:
            continue
        distractors.add(cand)

    if len(distractors) < 3:
        raise ValueError("modelled example fractions_equivalent could not build distinct distractors")

    candidates = [correct] + list(distractors)[:3]
    rng.shuffle(candidates)

    equivalent_flags = [a * den == num * b for num, den in candidates]
    if sum(equivalent_flags) != 1:
        raise ValueError("modelled example fractions_equivalent (identify_equivalent) verification failed")
    correct_index = equivalent_flags.index(True)

    letters = ["A", "B", "C", "D"]
    options_str = ", ".join(f"{letters[i]}) {n}/{d}" for i, (n, d) in enumerate(candidates))
    correct_letter = letters[correct_index]
    correct_num, correct_den = candidates[correct_index]

    teaching_steps = [
        f"To check whether a fraction p/q is equivalent to {a}/{b}, use cross-multiplication: they are "
        f"equivalent only if {a} × q equals p × {b}. This works because both sides are just two "
        "different ways of writing 'the same value scaled up to a common denominator'.",
        f"Test each option this way. Most options will fail because they've been changed by only one "
        "of numerator/denominator, or scaled by mismatched amounts, which breaks the equal-value "
        "relationship.",
        f"Only option {correct_letter}) {correct_num}/{correct_den} passes the test: "
        f"{a} × {correct_den} = {a * correct_den}, and {correct_num} × {b} = {correct_num * b}, which match.",
    ]
    worked_calculation = [
        f"{a}/{b} vs {options_str}",
        f"{a} × {correct_den} = {a * correct_den}",
        f"{correct_num} × {b} = {correct_num * b}  (match)",
    ]
    return ModelledExample(
        topic_id="fractions_equivalent",
        tier=Tier.FOUNDATION,
        prompt=f"Which of the following fractions is equivalent to {a}/{b}? {options_str}",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{correct_letter}) {correct_num}/{correct_den}",
    )


def generate_modelled_example_fractions_ordering(tier: Tier, rng: random.Random) -> ModelledExample:
    n = rng.choice([4, 5])
    fracs: list[Fraction] = []
    used_dens: set[int] = set()
    attempts = 0
    while len(fracs) < n and attempts < 300:
        attempts += 1
        den = rng.randint(2, 12)
        if den in used_dens:
            continue
        num = rng.randint(1, den - 1)
        val = Fraction(num, den)
        if val in fracs:
            continue
        used_dens.add(den)
        fracs.append(val)
    if len(fracs) < n:
        raise ValueError("modelled example fractions_ordering could not generate enough distinct fractions")

    direction = rng.choice(["ascending", "descending"])
    order = sorted(fracs, reverse=(direction == "descending"))

    lcm_val = 1
    for f in fracs:
        lcm_val = lcm_val * f.denominator // math.gcd(lcm_val, f.denominator)
    scaled = [(f.numerator * (lcm_val // f.denominator), f) for f in fracs]
    scaled_sorted = sorted(scaled, key=lambda pair: pair[0], reverse=(direction == "descending"))
    order_via_lcm = [f for _, f in scaled_sorted]
    if order_via_lcm != order:
        raise ValueError("modelled example fractions_ordering verification failed")

    display_strs = [_fmt_fraction(f) for f in fracs]
    ordered_strs = [_fmt_fraction(f) for f in order]
    common_form = ", ".join(
        f"{_fmt_fraction(f)} = {f.numerator * (lcm_val // f.denominator)}/{lcm_val}" for f in fracs
    )
    direction_words = "smallest to largest" if direction == "ascending" else "largest to smallest"

    teaching_steps = [
        "Fractions with different denominators can't be compared just by looking at their numerators - "
        "they need to be rewritten over the SAME denominator first, so each 'slice' represents the same "
        "size.",
        f"The denominators here are {', '.join(str(f.denominator) for f in fracs)}, so find their LCM "
        f"(lowest common multiple): {lcm_val}.",
        f"Convert every fraction to have denominator {lcm_val}: {common_form}.",
        f"Now that all the denominators match, the fraction with the biggest numerator is the biggest "
        f"value, and the fraction with the smallest numerator is the smallest value - so just order the "
        f"numerators {direction_words}.",
        f"Finally, write the answer using the ORIGINAL fractions (not the common-denominator versions), "
        f"in that same order: {', '.join(ordered_strs)}.",
    ]
    worked_calculation = [
        f"{', '.join(display_strs)}",
        f"= {common_form}",
        f"order ({direction_words}): {', '.join(ordered_strs)}",
    ]
    return ModelledExample(
        topic_id="fractions_ordering",
        tier=Tier.FOUNDATION,
        prompt=f"Write these fractions in order, {direction_words}: {', '.join(display_strs)}",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=", ".join(ordered_strs),
    )


def generate_modelled_example_fractions_improper_mixed(tier: Tier, rng: random.Random) -> ModelledExample:
    shape = rng.choice(["to_mixed", "to_improper"])
    den = rng.randint(2, 10)
    whole = rng.randint(1, 6)
    num = rng.randint(1, den - 1)
    while math.gcd(num, den) != 1:
        num = rng.randint(1, den - 1)

    improper_num = whole * den + num

    check_whole, check_num = divmod(improper_num, den)
    if check_whole != whole or check_num != num:
        raise ValueError("modelled example fractions_improper_mixed verification failed")

    if shape == "to_mixed":
        teaching_steps = [
            f"An improper fraction has a numerator bigger than its denominator, which means its value "
            f"is more than 1 whole - {improper_num}/{den} is really some whole number of "
            f"{den}ths plus a bit left over.",
            f"To find how many whole {den}ths fit inside, divide the numerator by the denominator: "
            f"{improper_num} ÷ {den} = {whole} remainder {num}. The whole-number part of that division "
            "is the whole number in our mixed number.",
            f"Whatever is left over (the remainder) becomes the new numerator, sitting over the same "
            f"original denominator: remainder {num} over {den}.",
            f"Putting it together gives the mixed number {whole} {num}/{den}.",
        ]
        worked_calculation = [
            f"{improper_num}/{den}",
            f"{improper_num} ÷ {den} = {whole} remainder {num}",
            f"= {whole} {num}/{den}",
        ]
        return ModelledExample(
            topic_id="fractions_improper_mixed",
            tier=Tier.FOUNDATION,
            prompt=f"Write {improper_num}/{den} as a mixed number.",
            worked_calculation=tuple(worked_calculation),
            teaching_steps=tuple(teaching_steps),
            final_answer=f"{whole} {num}/{den}",
        )
    else:
        teaching_steps = [
            f"A mixed number like {whole} {num}/{den} combines a whole number with a fraction - to "
            "convert it into a single (improper) fraction, we need to express the whole number part in "
            f"{den}ths too, so everything is over the same denominator.",
            f"Multiply the whole number by the denominator to find how many {den}ths are in the whole "
            f"number part: {whole} × {den} = {whole * den}.",
            f"Add on the fractional part's numerator, since that's the extra {den}ths on top: "
            f"{whole * den} + {num} = {improper_num}.",
            f"Write this total over the original denominator: {improper_num}/{den}.",
        ]
        worked_calculation = [
            f"{whole} {num}/{den}",
            f"{whole} × {den} + {num} = {improper_num}",
            f"= {improper_num}/{den}",
        ]
        return ModelledExample(
            topic_id="fractions_improper_mixed",
            tier=Tier.FOUNDATION,
            prompt=f"Write {whole} {num}/{den} as an improper fraction.",
            worked_calculation=tuple(worked_calculation),
            teaching_steps=tuple(teaching_steps),
            final_answer=f"{improper_num}/{den}",
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

TOPIC_DIVIDE_FOUNDATION = TopicDefinition(
    id="fractions_divide_foundation",
    display_name="Dividing Fractions (Foundation)",
    description="Divide two fractions using keep-change-flip.",
    generate=generate_divide_fractions_foundation,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_divide_fractions_foundation,
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

TOPIC_EQUIVALENT = TopicDefinition(
    id="fractions_equivalent",
    display_name="Equivalent Fractions",
    description="Find a missing numerator, or identify which fraction is equivalent to a given one.",
    generate=generate_fractions_equivalent,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_fractions_equivalent,
)

TOPIC_ORDERING = TopicDefinition(
    id="fractions_ordering",
    display_name="Ordering Fractions",
    description="Order a list of fractions with different denominators.",
    generate=generate_fractions_ordering,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_fractions_ordering,
)

TOPIC_IMPROPER_MIXED = TopicDefinition(
    id="fractions_improper_mixed",
    display_name="Improper Fractions and Mixed Numbers",
    description="Convert between improper fractions and mixed numbers.",
    generate=generate_fractions_improper_mixed,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_fractions_improper_mixed,
)
