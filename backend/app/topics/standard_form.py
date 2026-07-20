import random
from decimal import Decimal
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


def generate_from_standard_form(tier: Tier, rng: random.Random) -> Question:
    a = _random_mantissa(rng)
    n = rng.choice(list(range(-5, -1)) + list(range(2, 7)))
    ordinary = a * Decimal(10) ** n

    if not (Decimal(1) <= a < Decimal(10)) or a * Decimal(10) ** n != ordinary:
        raise ValueError("from_standard_form verification failed")

    direction = "right" if n > 0 else "left"
    steps = [
        f"Multiply {_fmt_decimal_fixed(a)} by 10^{n}, which means moving the decimal point {abs(n)} place(s) {direction}.",
        f"{_fmt_decimal_fixed(a)} × 10^{n} = {_fmt_decimal_fixed(ordinary)}",
    ]
    return Question(
        topic_id="standard_form_from",
        tier=Tier.FOUNDATION,
        prompt=f"Write {_fmt_decimal_fixed(a)} × 10^{n} as an ordinary number.",
        solution_steps=tuple(steps),
        final_answer=_fmt_decimal_fixed(ordinary),
        dedup_key=f"from_standard:{a}:{n}",
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


def generate_modelled_example_from_standard_form(tier: Tier, rng: random.Random) -> ModelledExample:
    a = _random_mantissa(rng)
    n = rng.choice(list(range(-5, -1)) + list(range(2, 7)))
    ordinary = a * Decimal(10) ** n

    if not (Decimal(1) <= a < Decimal(10)) or a * Decimal(10) ** n != ordinary:
        raise ValueError("modelled example from_standard_form verification failed")

    direction = "right" if n > 0 else "left"
    teaching_steps = [
        f"{_fmt_decimal_fixed(a)} × 10^{n} means multiplying {_fmt_decimal_fixed(a)} by 10, {abs(n)} "
        "times over (or, if the power is negative, dividing by 10 that many times). Multiplying by 10 "
        "moves the decimal point one place to the right; dividing by 10 moves it one place to the left.",
        f"Since the power here is {n}, the decimal point moves {abs(n)} place(s) to the {direction}.",
        f"Count out {abs(n)} places from where the decimal point currently sits in {_fmt_decimal_fixed(a)}, "
        "filling in zeros as placeholders wherever there are no digits left to move past.",
        f"This gives {_fmt_decimal_fixed(a)} × 10^{n} = {_fmt_decimal_fixed(ordinary)}.",
    ]
    worked_calculation = [
        f"{_fmt_decimal_fixed(a)} × 10^{n}",
        f"= {_fmt_decimal_fixed(ordinary)}",
    ]
    return ModelledExample(
        topic_id="standard_form_from",
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

TOPIC_FROM_STANDARD_FORM = TopicDefinition(
    id="standard_form_from",
    display_name="Converting from Standard Form",
    description="Write a number given in standard form as an ordinary number.",
    generate=generate_from_standard_form,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_from_standard_form,
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
