import random
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction

from app.core.models import ModelledExample, Question, Tier
from app.topics.base import TopicDefinition

SECTION = "number"
GROUP = "Standard Form"


def _fmt_decimal_fixed(d: Decimal) -> str:
    s = format(d, "f")
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s


def _fraction_to_decimal(f: Fraction) -> Decimal:
    return Decimal(f.numerator) / Decimal(f.denominator)


def _random_mantissa(rng: random.Random) -> Decimal:
    whole = rng.randint(1, 9)
    extra_digits = rng.choice(["", str(rng.randint(1, 9)), f"{rng.randint(0, 9)}{rng.randint(1, 9)}"])
    return Decimal(f"{whole}.{extra_digits}" if extra_digits else str(whole))


def _random_calc_mantissa(rng: random.Random) -> Decimal:
    """A one-decimal-place mantissa (never a whole number) for the calculator topic,
    so multiply/divide combinations reliably need a calculator and 3sf rounding."""
    whole = rng.randint(1, 9)
    tenths = rng.randint(1, 9)
    return Decimal(f"{whole}.{tenths}")


def generate_to_standard_form(tier: Tier, rng: random.Random) -> Question:
    a = _random_mantissa(rng)
    n = rng.randint(2, 8)
    ordinary = a * Decimal(10) ** n

    if not (Decimal(1) <= a < Decimal(10)) or a * Decimal(10) ** n != ordinary:
        raise ValueError("to_standard_form verification failed")

    steps = [
        f"Move the decimal point until there is one non-zero digit before it: {_fmt_decimal_fixed(a)}",
        f"Count how many places the decimal point moved: {n}",
        f"{_fmt_decimal_fixed(ordinary)} = {_fmt_decimal_fixed(a)} × 10^{n}",
    ]
    return Question(
        topic_id="standard_form_to",
        tier=Tier.FOUNDATION,
        prompt=f"Write {_fmt_decimal_fixed(ordinary)} in standard form.",
        solution_steps=tuple(steps),
        final_answer=f"{_fmt_decimal_fixed(a)} × 10^{n}",
        dedup_key=f"to_standard:{a}:{n}",
    )


def generate_to_standard_form_small(tier: Tier, rng: random.Random) -> Question:
    a = _random_mantissa(rng)
    n = rng.randint(2, 8)
    exponent = -n
    ordinary = a * Decimal(10) ** exponent

    if not (Decimal(1) <= a < Decimal(10)) or a * Decimal(10) ** exponent != ordinary:
        raise ValueError("to_standard_form_small verification failed")

    steps = [
        f"Move the decimal point until there is one non-zero digit before it: {_fmt_decimal_fixed(a)}",
        f"Count how many places the decimal point moved: {n} (the number is less than 1, so the power is negative)",
        f"{_fmt_decimal_fixed(ordinary)} = {_fmt_decimal_fixed(a)} × 10^{exponent}",
    ]
    return Question(
        topic_id="standard_form_to_small",
        tier=Tier.FOUNDATION,
        prompt=f"Write {_fmt_decimal_fixed(ordinary)} in standard form.",
        solution_steps=tuple(steps),
        final_answer=f"{_fmt_decimal_fixed(a)} × 10^{exponent}",
        dedup_key=f"to_standard_small:{a}:{exponent}",
    )


def generate_from_standard_form_large(tier: Tier, rng: random.Random) -> Question:
    a = _random_mantissa(rng)
    n = rng.randint(2, 6)
    ordinary = a * Decimal(10) ** n

    if not (Decimal(1) <= a < Decimal(10)) or a * Decimal(10) ** n != ordinary:
        raise ValueError("from_standard_form_large verification failed")

    steps = [
        f"Multiply {_fmt_decimal_fixed(a)} by 10^{n}, which means moving the decimal point {n} place(s) right.",
        f"{_fmt_decimal_fixed(a)} × 10^{n} = {_fmt_decimal_fixed(ordinary)}",
    ]
    return Question(
        topic_id="standard_form_from_large",
        tier=Tier.FOUNDATION,
        prompt=f"Write {_fmt_decimal_fixed(a)} × 10^{n} as an ordinary number.",
        solution_steps=tuple(steps),
        final_answer=_fmt_decimal_fixed(ordinary),
        dedup_key=f"from_standard_large:{a}:{n}",
    )


def generate_from_standard_form_small(tier: Tier, rng: random.Random) -> Question:
    a = _random_mantissa(rng)
    n = rng.randint(-5, -2)
    ordinary = a * Decimal(10) ** n

    if not (Decimal(1) <= a < Decimal(10)) or a * Decimal(10) ** n != ordinary:
        raise ValueError("from_standard_form_small verification failed")

    steps = [
        f"Multiply {_fmt_decimal_fixed(a)} by 10^{n}, which means moving the decimal point {abs(n)} place(s) left.",
        f"{_fmt_decimal_fixed(a)} × 10^{n} = {_fmt_decimal_fixed(ordinary)}",
    ]
    return Question(
        topic_id="standard_form_from_small",
        tier=Tier.FOUNDATION,
        prompt=f"Write {_fmt_decimal_fixed(a)} × 10^{n} as an ordinary number.",
        solution_steps=tuple(steps),
        final_answer=_fmt_decimal_fixed(ordinary),
        dedup_key=f"from_standard_small:{a}:{n}",
    )


def generate_multiply_divide_standard_form(tier: Tier, rng: random.Random) -> Question:
    op = rng.choice(["multiply", "divide"])
    n1 = rng.randint(-4, 6)
    n2 = rng.randint(-4, 6)

    if op == "multiply":
        a1, a2 = rng.randint(1, 9), rng.randint(1, 9)
        raw_mantissa = Fraction(a1 * a2)
        raw_exp = n1 + n2
    else:
        a2 = rng.choice([1, 2, 4, 5, 8])
        a1 = rng.randint(1, 9)
        raw_mantissa = Fraction(a1, a2)
        raw_exp = n1 - n2

    norm_mantissa, norm_exp = raw_mantissa, raw_exp
    while norm_mantissa >= 10:
        norm_mantissa /= 10
        norm_exp += 1
    while norm_mantissa < 1:
        norm_mantissa *= 10
        norm_exp -= 1

    # Independent verification via exact Fraction arithmetic on the ordinary-number equivalents.
    val1 = Fraction(a1) * Fraction(10) ** n1
    val2 = Fraction(a2) * Fraction(10) ** n2
    combined = val1 * val2 if op == "multiply" else val1 / val2
    check_val = norm_mantissa * Fraction(10) ** norm_exp
    if combined != check_val:
        raise ValueError("multiply_divide_standard_form verification failed")

    symbol = "×" if op == "multiply" else "÷"
    raw_mantissa_str = str(int(raw_mantissa)) if raw_mantissa.denominator == 1 else _fmt_decimal_fixed(_fraction_to_decimal(raw_mantissa))
    steps = [
        f"{'Multiply' if op == 'multiply' else 'Divide'} the mantissas: {a1} {symbol} {a2} = {raw_mantissa_str}",
        f"{'Add' if op == 'multiply' else 'Subtract'} the powers of 10: {n1} {'+' if op == 'multiply' else '-'} {n2} = {raw_exp}",
    ]
    if (norm_mantissa, norm_exp) != (raw_mantissa, raw_exp):
        steps.append(
            f"Renormalize so the mantissa is between 1 and 10: "
            f"{_fmt_decimal_fixed(_fraction_to_decimal(norm_mantissa))} × 10^{norm_exp}"
        )
    final_answer = f"{_fmt_decimal_fixed(_fraction_to_decimal(norm_mantissa))} × 10^{norm_exp}"
    return Question(
        topic_id="standard_form_multiply_divide",
        tier=Tier.HIGHER,
        prompt=f"Work out ({a1} × 10^{n1}) {symbol} ({a2} × 10^{n2}). Give your answer in standard form.",
        solution_steps=tuple(steps),
        final_answer=final_answer,
        dedup_key=f"muldiv:{op}:{a1}:{n1}:{a2}:{n2}",
    )


def generate_multiply_divide_standard_form_foundation(tier: Tier, rng: random.Random) -> Question:
    op = rng.choice(["multiply", "divide"])
    n1 = rng.randint(1, 5)
    n2 = rng.randint(1, 5)

    if op == "multiply":
        a1, a2 = rng.randint(1, 9), rng.randint(1, 9)
        raw_mantissa = Fraction(a1 * a2)
        raw_exp = n1 + n2
    else:
        a2 = rng.choice([1, 2, 4, 5, 8])
        a1 = rng.randint(1, 9)
        raw_mantissa = Fraction(a1, a2)
        raw_exp = n1 - n2

    norm_mantissa, norm_exp = raw_mantissa, raw_exp
    while norm_mantissa >= 10:
        norm_mantissa /= 10
        norm_exp += 1
    while norm_mantissa < 1:
        norm_mantissa *= 10
        norm_exp -= 1

    # Independent verification via exact Fraction arithmetic on the ordinary-number equivalents.
    val1 = Fraction(a1) * Fraction(10) ** n1
    val2 = Fraction(a2) * Fraction(10) ** n2
    combined = val1 * val2 if op == "multiply" else val1 / val2
    check_val = norm_mantissa * Fraction(10) ** norm_exp
    if combined != check_val:
        raise ValueError("multiply_divide_standard_form_foundation verification failed")

    symbol = "×" if op == "multiply" else "÷"
    raw_mantissa_str = str(int(raw_mantissa)) if raw_mantissa.denominator == 1 else _fmt_decimal_fixed(_fraction_to_decimal(raw_mantissa))
    steps = [
        f"{'Multiply' if op == 'multiply' else 'Divide'} the mantissas: {a1} {symbol} {a2} = {raw_mantissa_str}",
        f"{'Add' if op == 'multiply' else 'Subtract'} the powers of 10: {n1} {'+' if op == 'multiply' else '-'} {n2} = {raw_exp}",
    ]
    if (norm_mantissa, norm_exp) != (raw_mantissa, raw_exp):
        steps.append(
            f"Renormalize so the mantissa is between 1 and 10: "
            f"{_fmt_decimal_fixed(_fraction_to_decimal(norm_mantissa))} × 10^{norm_exp}"
        )
    final_answer = f"{_fmt_decimal_fixed(_fraction_to_decimal(norm_mantissa))} × 10^{norm_exp}"
    return Question(
        topic_id="standard_form_multiply_divide_foundation",
        tier=Tier.FOUNDATION,
        prompt=f"Work out ({a1} × 10^{n1}) {symbol} ({a2} × 10^{n2}). Give your answer in standard form.",
        solution_steps=tuple(steps),
        final_answer=final_answer,
        dedup_key=f"muldiv_f:{op}:{a1}:{n1}:{a2}:{n2}",
    )


def generate_add_subtract_standard_form(tier: Tier, rng: random.Random) -> Question:
    n1 = rng.randint(3, 7)
    n2 = n1 - rng.randint(1, 2)
    a1 = rng.randint(1, 9)
    a2 = rng.randint(1, 9)
    op = rng.choice(["+", "-"])

    shift = n1 - n2
    shifted_a1 = a1 * 10**shift
    combined_coeff = shifted_a1 + a2 if op == "+" else shifted_a1 - a2
    if combined_coeff <= 0:
        raise ValueError("add_subtract_standard_form produced a non-positive coefficient")

    digits = len(str(combined_coeff))
    exp = n2 + digits - 1
    mantissa = Fraction(combined_coeff, 10 ** (digits - 1))

    # Independent verification via exact Fraction arithmetic straight from the original inputs.
    val1 = Fraction(a1) * Fraction(10) ** n1
    val2 = Fraction(a2) * Fraction(10) ** n2
    combined_direct = val1 + val2 if op == "+" else val1 - val2
    check_val = mantissa * Fraction(10) ** exp
    if combined_direct != check_val:
        raise ValueError("add_subtract_standard_form verification failed")

    mantissa_str = _fmt_decimal_fixed(_fraction_to_decimal(mantissa))
    steps = [
        f"Write both numbers with the same power of 10: {a1}×10^{n1} = {shifted_a1}×10^{n2}, {a2}×10^{n2} = {a2}×10^{n2}",
        f"{'Add' if op == '+' else 'Subtract'} the coefficients: {shifted_a1} {op} {a2} = {combined_coeff}",
        f"Write in standard form: {combined_coeff} × 10^{n2} = {mantissa_str} × 10^{exp}",
    ]
    return Question(
        topic_id="standard_form_add_subtract",
        tier=Tier.HIGHER,
        prompt=f"Work out ({a1} × 10^{n1}) {op} ({a2} × 10^{n2}). Give your answer in standard form.",
        solution_steps=tuple(steps),
        final_answer=f"{mantissa_str} × 10^{exp}",
        dedup_key=f"addsub:{op}:{a1}:{n1}:{a2}:{n2}",
    )


def generate_standard_form_calculator(tier: Tier, rng: random.Random) -> Question:
    for _ in range(50):
        op = rng.choice(["multiply", "divide"])
        a1 = _random_calc_mantissa(rng)
        a2 = _random_calc_mantissa(rng)
        n1 = rng.randint(-6, 8)
        n2 = rng.randint(-6, 8)

        raw_mantissa = a1 * a2 if op == "multiply" else a1 / a2
        raw_exp = n1 + n2 if op == "multiply" else n1 - n2

        norm_mantissa, norm_exp = raw_mantissa, raw_exp
        while norm_mantissa >= 10:
            norm_mantissa /= 10
            norm_exp += 1
        while norm_mantissa < 1:
            norm_mantissa *= 10
            norm_exp -= 1

        rounded_mantissa = norm_mantissa.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if rounded_mantissa >= 10:
            rounded_mantissa = Decimal("1.00")
            norm_exp += 1

        if rounded_mantissa == rounded_mantissa.to_integral_value():
            continue  # a "clean" single-digit mantissa isn't what this calculator topic tests - retry
        break
    else:
        raise ValueError("standard_form_calculator could not find a suitably messy combination")

    # Independent verification: recompute the true mantissa via exact Fraction arithmetic
    # (a genuinely different, exact-rational path from the Decimal arithmetic above, with
    # no rounding at all), renormalise it separately, and re-round it with a second,
    # independently-invoked Decimal.quantize call - then compare against the claimed answer.
    check_fraction = Fraction(a1) * Fraction(a2) if op == "multiply" else Fraction(a1) / Fraction(a2)
    check_exp = raw_exp
    while check_fraction >= 10:
        check_fraction /= 10
        check_exp += 1
    while check_fraction < 1:
        check_fraction *= 10
        check_exp -= 1
    check_decimal = Decimal(check_fraction.numerator) / Decimal(check_fraction.denominator)
    check_rounded = check_decimal.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if check_rounded >= 10:
        check_rounded = Decimal("1.00")
        check_exp += 1
    if check_rounded != rounded_mantissa or check_exp != norm_exp:
        raise ValueError("standard_form_calculator verification failed")

    symbol = "×" if op == "multiply" else "÷"
    is_exact = rounded_mantissa == norm_mantissa
    raw_display = _fmt_decimal_fixed(raw_mantissa.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP))

    steps = [
        f"{'Multiply' if op == 'multiply' else 'Divide'} the mantissas on your calculator: "
        f"{_fmt_decimal_fixed(a1)} {symbol} {_fmt_decimal_fixed(a2)} = {raw_display}",
        f"{'Add' if op == 'multiply' else 'Subtract'} the powers of 10: "
        f"{n1} {'+' if op == 'multiply' else '-'} {n2} = {raw_exp}",
    ]
    if norm_exp != raw_exp:
        norm_display = _fmt_decimal_fixed(norm_mantissa.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP))
        steps.append(f"Renormalise so the mantissa is between 1 and 10: {norm_display} × 10^{norm_exp}")
    if is_exact:
        steps.append(f"The mantissa is already exact to 3 significant figures: {rounded_mantissa} × 10^{norm_exp}")
    else:
        steps.append(f"Round the mantissa to 3 significant figures: {rounded_mantissa} × 10^{norm_exp}")

    final_answer = f"{rounded_mantissa} × 10^{norm_exp}"
    return Question(
        topic_id="standard_form_calculator",
        tier=Tier.FOUNDATION,
        prompt=(
            f"Use a calculator to work out ({_fmt_decimal_fixed(a1)} × 10^{n1}) {symbol} "
            f"({_fmt_decimal_fixed(a2)} × 10^{n2}). Give your answer in standard form, rounded to "
            "3 significant figures if necessary."
        ),
        solution_steps=tuple(steps),
        final_answer=final_answer,
        dedup_key=f"calc:{op}:{a1}:{n1}:{a2}:{n2}",
    )


def generate_modelled_example_to_standard_form(tier: Tier, rng: random.Random) -> ModelledExample:
    a = _random_mantissa(rng)
    n = rng.randint(2, 8)
    ordinary = a * Decimal(10) ** n

    if not (Decimal(1) <= a < Decimal(10)) or a * Decimal(10) ** n != ordinary:
        raise ValueError("modelled example to_standard_form verification failed")

    teaching_steps = [
        f"Standard form writes a number as a value between 1 and 10, multiplied by a power of 10. "
        f"To convert {_fmt_decimal_fixed(ordinary)}, first find the digit that should sit before the "
        "decimal point: that's always the first non-zero digit of the number.",
        f"Move the decimal point so it sits right after that digit, giving {_fmt_decimal_fixed(a)}. "
        "This is called the mantissa, and it must always be between 1 and 10.",
        f"Count exactly how many places the decimal point moved to get from {_fmt_decimal_fixed(ordinary)} "
        f"to {_fmt_decimal_fixed(a)}: it moved {n} place(s) to the left, so the power of 10 is {n} "
        "(moving the point left means the original number was bigger than the mantissa, so the power is positive).",
        f"Putting it together: {_fmt_decimal_fixed(ordinary)} = {_fmt_decimal_fixed(a)} × 10^{n}.",
    ]
    worked_calculation = [
        _fmt_decimal_fixed(ordinary),
        f"= {_fmt_decimal_fixed(a)} × 10^{n}",
    ]
    return ModelledExample(
        topic_id="standard_form_to",
        tier=Tier.FOUNDATION,
        prompt=f"Write {_fmt_decimal_fixed(ordinary)} in standard form.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{_fmt_decimal_fixed(a)} × 10^{n}",
    )


def generate_modelled_example_to_standard_form_small(tier: Tier, rng: random.Random) -> ModelledExample:
    a = _random_mantissa(rng)
    n = rng.randint(2, 8)
    exponent = -n
    ordinary = a * Decimal(10) ** exponent

    if not (Decimal(1) <= a < Decimal(10)) or a * Decimal(10) ** exponent != ordinary:
        raise ValueError("modelled example to_standard_form_small verification failed")

    teaching_steps = [
        f"Standard form writes a number as a value between 1 and 10, multiplied by a power of 10 - "
        f"and this works for small numbers (less than 1) too. To convert {_fmt_decimal_fixed(ordinary)}, "
        "first find the first non-zero digit: that's the digit that should sit before the decimal point.",
        f"Move the decimal point so it sits right after that digit, giving {_fmt_decimal_fixed(a)}. "
        "This is the mantissa, and it must always be between 1 and 10 - even for a small number.",
        f"Count exactly how many places the decimal point moved to get from {_fmt_decimal_fixed(ordinary)} "
        f"to {_fmt_decimal_fixed(a)}: it moved {n} place(s) to the right this time, so the power of 10 "
        f"is -{n} (moving the point right means the original number was smaller than the mantissa, so "
        "the power is negative).",
        f"Putting it together: {_fmt_decimal_fixed(ordinary)} = {_fmt_decimal_fixed(a)} × 10^{exponent}.",
    ]
    worked_calculation = [
        _fmt_decimal_fixed(ordinary),
        f"= {_fmt_decimal_fixed(a)} × 10^{exponent}",
    ]
    return ModelledExample(
        topic_id="standard_form_to_small",
        tier=Tier.FOUNDATION,
        prompt=f"Write {_fmt_decimal_fixed(ordinary)} in standard form.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{_fmt_decimal_fixed(a)} × 10^{exponent}",
    )


def generate_modelled_example_from_standard_form_large(tier: Tier, rng: random.Random) -> ModelledExample:
    a = _random_mantissa(rng)
    n = rng.randint(2, 6)
    ordinary = a * Decimal(10) ** n

    if not (Decimal(1) <= a < Decimal(10)) or a * Decimal(10) ** n != ordinary:
        raise ValueError("modelled example from_standard_form_large verification failed")

    teaching_steps = [
        f"{_fmt_decimal_fixed(a)} × 10^{n} means multiplying {_fmt_decimal_fixed(a)} by 10, {n} times "
        "over. Multiplying by 10 moves the decimal point one place to the right each time.",
        f"Since the power here is {n}, the decimal point moves {n} place(s) to the right.",
        f"Count out {n} places from where the decimal point currently sits in {_fmt_decimal_fixed(a)}, "
        "filling in zeros as placeholders wherever there are no digits left to move past.",
        f"This gives {_fmt_decimal_fixed(a)} × 10^{n} = {_fmt_decimal_fixed(ordinary)}.",
    ]
    worked_calculation = [
        f"{_fmt_decimal_fixed(a)} × 10^{n}",
        f"= {_fmt_decimal_fixed(ordinary)}",
    ]
    return ModelledExample(
        topic_id="standard_form_from_large",
        tier=Tier.FOUNDATION,
        prompt=f"Write {_fmt_decimal_fixed(a)} × 10^{n} as an ordinary number.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=_fmt_decimal_fixed(ordinary),
    )


def generate_modelled_example_from_standard_form_small(tier: Tier, rng: random.Random) -> ModelledExample:
    a = _random_mantissa(rng)
    n = rng.randint(-5, -2)
    ordinary = a * Decimal(10) ** n

    if not (Decimal(1) <= a < Decimal(10)) or a * Decimal(10) ** n != ordinary:
        raise ValueError("modelled example from_standard_form_small verification failed")

    teaching_steps = [
        f"{_fmt_decimal_fixed(a)} × 10^{n} means dividing {_fmt_decimal_fixed(a)} by 10, {abs(n)} times "
        "over, since the power is negative. Dividing by 10 moves the decimal point one place to the "
        "left each time.",
        f"Since the power here is {n}, the decimal point moves {abs(n)} place(s) to the left.",
        f"Count out {abs(n)} places from where the decimal point currently sits in {_fmt_decimal_fixed(a)}, "
        "filling in zeros as placeholders wherever there are no digits left to move past.",
        f"This gives {_fmt_decimal_fixed(a)} × 10^{n} = {_fmt_decimal_fixed(ordinary)}.",
    ]
    worked_calculation = [
        f"{_fmt_decimal_fixed(a)} × 10^{n}",
        f"= {_fmt_decimal_fixed(ordinary)}",
    ]
    return ModelledExample(
        topic_id="standard_form_from_small",
        tier=Tier.FOUNDATION,
        prompt=f"Write {_fmt_decimal_fixed(a)} × 10^{n} as an ordinary number.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=_fmt_decimal_fixed(ordinary),
    )


def generate_modelled_example_multiply_divide_standard_form(tier: Tier, rng: random.Random) -> ModelledExample:
    op = rng.choice(["multiply", "divide"])
    n1 = rng.randint(-4, 6)
    n2 = rng.randint(-4, 6)

    if op == "multiply":
        a1, a2 = rng.randint(1, 9), rng.randint(1, 9)
        raw_mantissa = Fraction(a1 * a2)
        raw_exp = n1 + n2
    else:
        a2 = rng.choice([1, 2, 4, 5, 8])
        a1 = rng.randint(1, 9)
        raw_mantissa = Fraction(a1, a2)
        raw_exp = n1 - n2

    norm_mantissa, norm_exp = raw_mantissa, raw_exp
    while norm_mantissa >= 10:
        norm_mantissa /= 10
        norm_exp += 1
    while norm_mantissa < 1:
        norm_mantissa *= 10
        norm_exp -= 1

    # Independent verification via exact Fraction arithmetic on the ordinary-number equivalents.
    val1 = Fraction(a1) * Fraction(10) ** n1
    val2 = Fraction(a2) * Fraction(10) ** n2
    combined = val1 * val2 if op == "multiply" else val1 / val2
    check_val = norm_mantissa * Fraction(10) ** norm_exp
    if combined != check_val:
        raise ValueError("modelled example multiply_divide_standard_form verification failed")

    symbol = "×" if op == "multiply" else "÷"
    raw_mantissa_str = str(int(raw_mantissa)) if raw_mantissa.denominator == 1 else _fmt_decimal_fixed(_fraction_to_decimal(raw_mantissa))
    norm_mantissa_str = _fmt_decimal_fixed(_fraction_to_decimal(norm_mantissa))
    needs_renormalise = (norm_mantissa, norm_exp) != (raw_mantissa, raw_exp)

    teaching_steps = [
        "Standard form numbers are built from two separate parts - a mantissa and a power of 10 - and "
        f"multiplying or dividing lets you deal with each part on its own. To {op} "
        f"({a1} × 10^{n1}) {symbol} ({a2} × 10^{n2}), handle the mantissas ({a1} and {a2}) and the "
        f"powers of 10 ({n1} and {n2}) separately.",
        f"{'Multiply' if op == 'multiply' else 'Divide'} the two mantissas together: "
        f"{a1} {symbol} {a2} = {raw_mantissa_str}.",
        f"{'Add' if op == 'multiply' else 'Subtract'} the powers of 10, since "
        + ("multiplying powers of 10 means adding their indices" if op == "multiply" else "dividing powers of 10 means subtracting their indices")
        + f": {n1} {'+' if op == 'multiply' else '-'} {n2} = {raw_exp}. This gives {raw_mantissa_str} × 10^{raw_exp}.",
    ]
    if needs_renormalise:
        teaching_steps.append(
            f"This isn't yet in standard form, because the mantissa {raw_mantissa_str} isn't between 1 "
            f"and 10. Move the decimal point until it is, adjusting the power of 10 to compensate: "
            f"{norm_mantissa_str} × 10^{norm_exp}."
        )
    else:
        teaching_steps.append(
            f"The mantissa {raw_mantissa_str} is already between 1 and 10, so this is already in "
            "standard form - no further adjustment is needed."
        )

    worked_calculation = [
        f"({a1} × 10^{n1}) {symbol} ({a2} × 10^{n2})",
        f"= {raw_mantissa_str} × 10^{raw_exp}",
    ]
    if needs_renormalise:
        worked_calculation.append(f"= {norm_mantissa_str} × 10^{norm_exp}")

    return ModelledExample(
        topic_id="standard_form_multiply_divide",
        tier=Tier.HIGHER,
        prompt=f"Work out ({a1} × 10^{n1}) {symbol} ({a2} × 10^{n2}). Give your answer in standard form.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{norm_mantissa_str} × 10^{norm_exp}",
    )


def generate_modelled_example_multiply_divide_standard_form_foundation(
    tier: Tier, rng: random.Random
) -> ModelledExample:
    op = rng.choice(["multiply", "divide"])
    n1 = rng.randint(1, 5)
    n2 = rng.randint(1, 5)

    if op == "multiply":
        a1, a2 = rng.randint(1, 9), rng.randint(1, 9)
        raw_mantissa = Fraction(a1 * a2)
        raw_exp = n1 + n2
    else:
        a2 = rng.choice([1, 2, 4, 5, 8])
        a1 = rng.randint(1, 9)
        raw_mantissa = Fraction(a1, a2)
        raw_exp = n1 - n2

    norm_mantissa, norm_exp = raw_mantissa, raw_exp
    while norm_mantissa >= 10:
        norm_mantissa /= 10
        norm_exp += 1
    while norm_mantissa < 1:
        norm_mantissa *= 10
        norm_exp -= 1

    # Independent verification via exact Fraction arithmetic on the ordinary-number equivalents.
    val1 = Fraction(a1) * Fraction(10) ** n1
    val2 = Fraction(a2) * Fraction(10) ** n2
    combined = val1 * val2 if op == "multiply" else val1 / val2
    check_val = norm_mantissa * Fraction(10) ** norm_exp
    if combined != check_val:
        raise ValueError("modelled example multiply_divide_standard_form_foundation verification failed")

    symbol = "×" if op == "multiply" else "÷"
    raw_mantissa_str = str(int(raw_mantissa)) if raw_mantissa.denominator == 1 else _fmt_decimal_fixed(_fraction_to_decimal(raw_mantissa))
    norm_mantissa_str = _fmt_decimal_fixed(_fraction_to_decimal(norm_mantissa))
    needs_renormalise = (norm_mantissa, norm_exp) != (raw_mantissa, raw_exp)

    teaching_steps = [
        "Standard form numbers are built from two separate parts - a mantissa and a power of 10 - and "
        f"multiplying or dividing lets you deal with each part on its own. To {op} "
        f"({a1} × 10^{n1}) {symbol} ({a2} × 10^{n2}), handle the mantissas ({a1} and {a2}) and the "
        f"powers of 10 ({n1} and {n2}) separately.",
        f"{'Multiply' if op == 'multiply' else 'Divide'} the two mantissas together: "
        f"{a1} {symbol} {a2} = {raw_mantissa_str}.",
        f"{'Add' if op == 'multiply' else 'Subtract'} the powers of 10, since "
        + ("multiplying powers of 10 means adding their indices" if op == "multiply" else "dividing powers of 10 means subtracting their indices")
        + f": {n1} {'+' if op == 'multiply' else '-'} {n2} = {raw_exp}. This gives {raw_mantissa_str} × 10^{raw_exp}.",
    ]
    if needs_renormalise:
        teaching_steps.append(
            f"This isn't yet in standard form, because the mantissa {raw_mantissa_str} isn't between 1 "
            f"and 10. Move the decimal point until it is, adjusting the power of 10 to compensate: "
            f"{norm_mantissa_str} × 10^{norm_exp}."
        )
    else:
        teaching_steps.append(
            f"The mantissa {raw_mantissa_str} is already between 1 and 10, so this is already in "
            "standard form - no further adjustment is needed."
        )

    worked_calculation = [
        f"({a1} × 10^{n1}) {symbol} ({a2} × 10^{n2})",
        f"= {raw_mantissa_str} × 10^{raw_exp}",
    ]
    if needs_renormalise:
        worked_calculation.append(f"= {norm_mantissa_str} × 10^{norm_exp}")

    return ModelledExample(
        topic_id="standard_form_multiply_divide_foundation",
        tier=Tier.FOUNDATION,
        prompt=f"Work out ({a1} × 10^{n1}) {symbol} ({a2} × 10^{n2}). Give your answer in standard form.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{norm_mantissa_str} × 10^{norm_exp}",
    )


def generate_modelled_example_add_subtract_standard_form(tier: Tier, rng: random.Random) -> ModelledExample:
    n1 = rng.randint(3, 7)
    n2 = n1 - rng.randint(1, 2)
    a1 = rng.randint(1, 9)
    a2 = rng.randint(1, 9)
    op = rng.choice(["+", "-"])

    shift = n1 - n2
    shifted_a1 = a1 * 10**shift
    combined_coeff = shifted_a1 + a2 if op == "+" else shifted_a1 - a2
    if combined_coeff <= 0:
        raise ValueError("modelled example add_subtract_standard_form produced a non-positive coefficient")

    digits = len(str(combined_coeff))
    exp = n2 + digits - 1
    mantissa = Fraction(combined_coeff, 10 ** (digits - 1))

    # Independent verification via exact Fraction arithmetic straight from the original inputs.
    val1 = Fraction(a1) * Fraction(10) ** n1
    val2 = Fraction(a2) * Fraction(10) ** n2
    combined_direct = val1 + val2 if op == "+" else val1 - val2
    check_val = mantissa * Fraction(10) ** exp
    if combined_direct != check_val:
        raise ValueError("modelled example add_subtract_standard_form verification failed")

    mantissa_str = _fmt_decimal_fixed(_fraction_to_decimal(mantissa))
    verb = "add" if op == "+" else "subtract"
    teaching_steps = [
        f"Unlike multiplying or dividing, you can't {verb} standard form numbers by combining the "
        "mantissas and powers of 10 separately - the powers of 10 must match first, just like fractions "
        "need a common denominator before they can be added or subtracted.",
        f"Rewrite {a1} × 10^{n1} using the smaller power, 10^{n2}: since 10^{n1} = 10^{shift} × 10^{n2}, "
        f"{a1} × 10^{n1} = {shifted_a1} × 10^{n2}.",
        f"Now both numbers share the same power of 10, so {verb} the coefficients directly: "
        f"{shifted_a1} {op} {a2} = {combined_coeff}, giving {combined_coeff} × 10^{n2}.",
        f"Finally, put this into standard form by moving the decimal point so the mantissa is between "
        f"1 and 10: {combined_coeff} × 10^{n2} = {mantissa_str} × 10^{exp}.",
    ]
    worked_calculation = [
        f"({a1} × 10^{n1}) {op} ({a2} × 10^{n2})",
        f"= ({shifted_a1} × 10^{n2}) {op} ({a2} × 10^{n2})",
        f"= {combined_coeff} × 10^{n2}",
        f"= {mantissa_str} × 10^{exp}",
    ]
    return ModelledExample(
        topic_id="standard_form_add_subtract",
        tier=Tier.HIGHER,
        prompt=f"Work out ({a1} × 10^{n1}) {op} ({a2} × 10^{n2}). Give your answer in standard form.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{mantissa_str} × 10^{exp}",
    )


def generate_modelled_example_standard_form_calculator(tier: Tier, rng: random.Random) -> ModelledExample:
    for _ in range(50):
        op = rng.choice(["multiply", "divide"])
        a1 = _random_calc_mantissa(rng)
        a2 = _random_calc_mantissa(rng)
        n1 = rng.randint(-6, 8)
        n2 = rng.randint(-6, 8)

        raw_mantissa = a1 * a2 if op == "multiply" else a1 / a2
        raw_exp = n1 + n2 if op == "multiply" else n1 - n2

        norm_mantissa, norm_exp = raw_mantissa, raw_exp
        while norm_mantissa >= 10:
            norm_mantissa /= 10
            norm_exp += 1
        while norm_mantissa < 1:
            norm_mantissa *= 10
            norm_exp -= 1

        rounded_mantissa = norm_mantissa.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if rounded_mantissa >= 10:
            rounded_mantissa = Decimal("1.00")
            norm_exp += 1

        if rounded_mantissa == rounded_mantissa.to_integral_value():
            continue  # a "clean" single-digit mantissa isn't what this calculator topic tests - retry
        break
    else:
        raise ValueError("modelled example standard_form_calculator could not find a suitably messy combination")

    # Independent verification (see generate_standard_form_calculator for the full rationale):
    # recompute the true mantissa via exact Fraction arithmetic, renormalise it separately, and
    # re-round it with a second, independently-invoked Decimal.quantize call.
    check_fraction = Fraction(a1) * Fraction(a2) if op == "multiply" else Fraction(a1) / Fraction(a2)
    check_exp = raw_exp
    while check_fraction >= 10:
        check_fraction /= 10
        check_exp += 1
    while check_fraction < 1:
        check_fraction *= 10
        check_exp -= 1
    check_decimal = Decimal(check_fraction.numerator) / Decimal(check_fraction.denominator)
    check_rounded = check_decimal.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if check_rounded >= 10:
        check_rounded = Decimal("1.00")
        check_exp += 1
    if check_rounded != rounded_mantissa or check_exp != norm_exp:
        raise ValueError("modelled example standard_form_calculator verification failed")

    symbol = "×" if op == "multiply" else "÷"
    raw_display = _fmt_decimal_fixed(raw_mantissa.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP))

    teaching_steps = [
        "When a question says you may use a calculator, you don't need to combine the mantissas by "
        "hand - just key in the two mantissas with the correct operation and let the calculator do "
        f"the arithmetic: {_fmt_decimal_fixed(a1)} {symbol} {_fmt_decimal_fixed(a2)} = {raw_display}.",
        f"{'Add' if op == 'multiply' else 'Subtract'} the powers of 10 separately, exactly as you "
        f"would without a calculator: {n1} {'+' if op == 'multiply' else '-'} {n2} = {raw_exp}, giving "
        f"{raw_display} × 10^{raw_exp} so far.",
    ]
    if norm_exp != raw_exp:
        norm_display = _fmt_decimal_fixed(norm_mantissa.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP))
        teaching_steps.append(
            "This isn't in standard form yet, because the mantissa isn't between 1 and 10. Move the "
            f"decimal point and adjust the power of 10 to compensate: {norm_display} × 10^{norm_exp}."
        )
    teaching_steps.append(
        "A calculator's answer often has far more decimal places than you need. Unless the question "
        f"says otherwise, round the mantissa to 3 significant figures: {rounded_mantissa} × 10^{norm_exp}."
    )

    worked_calculation = [
        f"({_fmt_decimal_fixed(a1)} × 10^{n1}) {symbol} ({_fmt_decimal_fixed(a2)} × 10^{n2})",
        f"= {raw_display} × 10^{raw_exp}",
    ]
    if norm_exp != raw_exp:
        norm_display = _fmt_decimal_fixed(norm_mantissa.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP))
        worked_calculation.append(f"= {norm_display} × 10^{norm_exp}")
    worked_calculation.append(f"= {rounded_mantissa} × 10^{norm_exp} (3 s.f.)")

    return ModelledExample(
        topic_id="standard_form_calculator",
        tier=Tier.FOUNDATION,
        prompt=(
            f"Use a calculator to work out ({_fmt_decimal_fixed(a1)} × 10^{n1}) {symbol} "
            f"({_fmt_decimal_fixed(a2)} × 10^{n2}). Give your answer in standard form, rounded to "
            "3 significant figures if necessary."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{rounded_mantissa} × 10^{norm_exp}",
    )


TOPIC_TO_STANDARD_FORM = TopicDefinition(
    id="standard_form_to",
    display_name="Converting to Standard Form",
    description="Write an ordinary number in standard form.",
    generate=generate_to_standard_form,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_to_standard_form,
)

TOPIC_TO_STANDARD_FORM_SMALL = TopicDefinition(
    id="standard_form_to_small",
    display_name="Converting Small Numbers to Standard Form",
    description="Write an ordinary number less than 1 in standard form.",
    generate=generate_to_standard_form_small,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_to_standard_form_small,
)

TOPIC_FROM_STANDARD_FORM_LARGE = TopicDefinition(
    id="standard_form_from_large",
    display_name="Converting from Standard Form (Large Numbers)",
    description="Write a large number given in standard form as an ordinary number.",
    generate=generate_from_standard_form_large,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_from_standard_form_large,
)

TOPIC_FROM_STANDARD_FORM_SMALL = TopicDefinition(
    id="standard_form_from_small",
    display_name="Converting from Standard Form (Small Numbers)",
    description="Write a small number given in standard form as an ordinary number.",
    generate=generate_from_standard_form_small,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_from_standard_form_small,
)

TOPIC_CALCULATOR = TopicDefinition(
    id="standard_form_calculator",
    display_name="Standard Form with a Calculator",
    description="Multiply or divide numbers in standard form using a calculator, rounding to 3 significant figures.",
    generate=generate_standard_form_calculator,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_standard_form_calculator,
)

TOPIC_MULTIPLY_DIVIDE = TopicDefinition(
    id="standard_form_multiply_divide",
    display_name="Multiplying & Dividing in Standard Form",
    description="Multiply or divide two numbers given in standard form.",
    generate=generate_multiply_divide_standard_form,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_multiply_divide_standard_form,
)

TOPIC_MULTIPLY_DIVIDE_FOUNDATION = TopicDefinition(
    id="standard_form_multiply_divide_foundation",
    display_name="Multiplying & Dividing in Standard Form (Foundation)",
    description="Multiply or divide two numbers given in standard form.",
    generate=generate_multiply_divide_standard_form_foundation,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_multiply_divide_standard_form_foundation,
)

TOPIC_ADD_SUBTRACT = TopicDefinition(
    id="standard_form_add_subtract",
    display_name="Adding & Subtracting in Standard Form",
    description="Add or subtract two numbers given in standard form.",
    generate=generate_add_subtract_standard_form,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_add_subtract_standard_form,
)
