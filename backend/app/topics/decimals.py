import math
import random
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction

from app.core.models import ModelledExample, Question, Tier
from app.topics.base import TopicDefinition

SECTION = "number"
GROUP = "Decimals"

RECURRING_DENOMINATORS = [3, 6, 7, 9, 11, 12, 13, 15, 18, 22]


def _fmt_decimal_fixed(d: Decimal) -> str:
    return format(d, "f")


def _round_half_up_fraction(value: Fraction, dp: int) -> Fraction:
    scale = 10**dp
    return Fraction(math.floor(value * scale + Fraction(1, 2)), scale)


def generate_round_to_decimal_places(tier: Tier, rng: random.Random) -> Question:
    integer_part = rng.randint(1, 99)
    frac_digits = [rng.randint(0, 9) for _ in range(3)]
    value = Decimal(f"{integer_part}.{''.join(map(str, frac_digits))}")
    round_to = rng.randint(1, 2)

    quantize_exp = Decimal(1).scaleb(-round_to)
    correct = value.quantize(quantize_exp, rounding=ROUND_HALF_UP)

    # Independent verification via exact Fraction arithmetic (separate path from Decimal.quantize).
    value_fraction = Fraction(str(value))
    manual = _round_half_up_fraction(value_fraction, round_to)
    if manual != Fraction(correct):
        raise ValueError("round_to_decimal_places verification failed")

    deciding_digit = frac_digits[round_to] if round_to < len(frac_digits) else 0
    direction = "up" if deciding_digit >= 5 else "down"
    plural = "s" if round_to != 1 else ""
    steps = [
        f"Look at the digit after the {round_to} decimal place{plural} we want: {deciding_digit}, so round {direction}.",
        f"{value} rounded to {round_to} decimal place{plural} = {_fmt_decimal_fixed(correct)}",
    ]
    return Question(
        topic_id="decimals_round_dp",
        tier=Tier.FOUNDATION,
        prompt=f"Round {value} to {round_to} decimal place{plural}.",
        solution_steps=tuple(steps),
        final_answer=_fmt_decimal_fixed(correct),
        dedup_key=f"round_dp:{value}:{round_to}",
    )


def generate_round_to_significant_figures(tier: Tier, rng: random.Random) -> Question:
    integer_part = rng.randint(0, 999)
    frac_digits = [rng.randint(0, 9) for _ in range(3)]
    value = Decimal(f"{integer_part}.{''.join(map(str, frac_digits))}")
    if value == 0:
        value = Decimal("1.234")
    sig_figs = rng.choice([1, 2, 3])

    d = value.adjusted()
    quantize_exp = Decimal(1).scaleb(d - sig_figs + 1)
    rounded = value.quantize(quantize_exp, rounding=ROUND_HALF_UP)

    # Independent verification: the rounded value must lie within half a unit-in-the-last-place
    # of the original value (a proximity invariant, checked via a different computation than quantize).
    half_ulp = Decimal(1).scaleb(d - sig_figs + 1) / 2
    if abs(rounded - value) > half_ulp + Decimal("1e-12"):
        raise ValueError("round_to_significant_figures verification failed")

    plural = "s" if sig_figs != 1 else ""
    steps = [
        f"Identify the first {sig_figs} significant figure{plural} of {value}.",
        f"{value} rounded to {sig_figs} significant figure{plural} = {_fmt_decimal_fixed(rounded)}",
    ]
    return Question(
        topic_id="decimals_round_sf",
        tier=Tier.FOUNDATION,
        prompt=f"Round {value} to {sig_figs} significant figure{plural}.",
        solution_steps=tuple(steps),
        final_answer=_fmt_decimal_fixed(rounded),
        dedup_key=f"round_sf:{value}:{sig_figs}",
    )


def generate_ordering(tier: Tier, rng: random.Random) -> Question:
    ks = rng.sample(range(5, 96), 4)
    formats = [rng.choice(["decimal", "fraction", "percent"]) for _ in ks]

    display_strs = []
    for k, fmt in zip(ks, formats):
        if fmt == "percent":
            display_strs.append(f"{k}%")
        elif fmt == "decimal":
            display_strs.append(_fmt_decimal_fixed(Decimal(k) / 100))
        else:
            frac = Fraction(k, 100)
            display_strs.append(f"{frac.numerator}/{frac.denominator}")

    # Independent verification: parse each display string back to a Fraction using
    # format-specific parsing logic and confirm it reconstructs the original k/100 exactly.
    for display, k in zip(display_strs, ks):
        if display.endswith("%"):
            parsed = Fraction(int(display[:-1]), 100)
        elif "/" in display:
            num, den = display.split("/")
            parsed = Fraction(int(num), int(den))
        else:
            parsed = Fraction(display)
        if parsed != Fraction(k, 100):
            raise ValueError("ordering verification failed")

    order = sorted(range(4), key=lambda i: ks[i])
    ordered_display = [display_strs[i] for i in order]
    common_form = ", ".join(f"{display_strs[i]} = {float(Fraction(ks[i], 100)):.2f}" for i in range(4))

    steps = [
        f"Convert each value to a decimal: {common_form}",
        f"Order from smallest to largest: {', '.join(ordered_display)}",
    ]
    return Question(
        topic_id="decimals_ordering",
        tier=Tier.FOUNDATION,
        prompt=f"Write these values in order, starting with the smallest: {', '.join(display_strs)}",
        solution_steps=tuple(steps),
        final_answer=", ".join(ordered_display),
        dedup_key=f"ordering:{sorted(ks)}:{formats}",
    )


def _decimal_expansion(p: int, q: int, max_digits: int = 20):
    p = p % q
    seen: dict[int, int] = {}
    digits: list[int] = []
    while p != 0 and p not in seen and len(digits) < max_digits:
        seen[p] = len(digits)
        p *= 10
        digits.append(p // q)
        p %= q
    if p == 0:
        return digits, None
    start = seen[p]
    return digits[:start], digits[start:]


def generate_recurring_decimal_to_fraction(tier: Tier, rng: random.Random) -> Question:
    for _ in range(100):
        q = rng.choice(RECURRING_DENOMINATORS)
        p = rng.randint(1, q - 1)
        if math.gcd(p, q) == 1:
            non_recurring, recurring = _decimal_expansion(p, q)
            if recurring is not None:
                break
    else:
        raise ValueError("recurring_decimal_to_fraction could not find valid parameters")

    n, r = len(non_recurring), len(recurring)
    prefix_val = int("".join(map(str, non_recurring))) if non_recurring else 0
    full_val = int("".join(map(str, non_recurring + recurring)))
    numerator = full_val - prefix_val
    denominator = 10 ** (n + r) - 10**n
    derived = Fraction(numerator, denominator)

    if derived != Fraction(p, q):
        raise ValueError("recurring_decimal_to_fraction verification failed")

    prefix_str = "".join(map(str, non_recurring))
    recurring_str = "".join(map(str, recurring))
    display_str = f"0.{prefix_str}({recurring_str})"

    steps = [
        f"Let x = {display_str}",
        "Multiply x by a power of 10 so the recurring parts line up, then subtract to eliminate the recurring part.",
        f"This gives x = {numerator}/{denominator}",
        f"Simplify: {p}/{q}",
    ]
    return Question(
        topic_id="decimals_recurring_to_fraction",
        tier=Tier.HIGHER,
        prompt=f"The recurring decimal {display_str} can be written as a fraction. Find this fraction in its simplest form.",
        solution_steps=tuple(steps),
        final_answer=f"{p}/{q}",
        dedup_key=f"recurring:{p}:{q}",
    )


SINGLE_DIGIT_RECURRING_DENOMINATORS = [3, 9]
TWO_DIGIT_RECURRING_DENOMINATORS = [11, 33, 99]


def generate_recurring_decimal_single_digit(tier: Tier, rng: random.Random) -> Question:
    for _ in range(50):
        q = rng.choice(SINGLE_DIGIT_RECURRING_DENOMINATORS)
        p = rng.randint(1, q - 1)
        if math.gcd(p, q) != 1:
            continue
        non_recurring, recurring = _decimal_expansion(p, q)
        if recurring is not None and not non_recurring and len(recurring) == 1:
            break
    else:
        raise ValueError("recurring_decimal_single_digit could not find valid parameters")

    digit = recurring[0]
    display_str = f"0.({digit})"

    # Independent verification: a single purely-recurring digit d means the decimal equals
    # d/9 exactly - a separate closed-form derivation from the digit-counting expansion above.
    # Confirm it matches the originally-chosen p/q, then round-trip the reduced fraction back
    # through the same digit-expansion helper and confirm it reproduces the same single
    # repeating digit.
    derived = Fraction(digit, 9)
    if derived != Fraction(p, q):
        raise ValueError("recurring_decimal_single_digit verification failed")
    check_non_recurring, check_recurring = _decimal_expansion(p, q)
    if check_non_recurring or check_recurring != [digit]:
        raise ValueError("recurring_decimal_single_digit round-trip verification failed")

    steps = [
        f"Let x = {display_str}, so 10x = {digit}.{digit}{digit}{digit}... "
        "(only one digit repeats, so multiply by 10 to shift it one place)",
        f"Subtract: 10x - x = {digit} - 0, so 9x = {digit}",
        f"x = {digit}/9 = {p}/{q}",
    ]
    return Question(
        topic_id="recurring_decimal_single_digit",
        tier=Tier.FOUNDATION,
        prompt=f"The recurring decimal {display_str} can be written as a fraction. Find this fraction in its simplest form.",
        solution_steps=tuple(steps),
        final_answer=f"{p}/{q}",
        dedup_key=f"recurring_1d:{p}:{q}",
    )


def generate_recurring_decimal_two_digit(tier: Tier, rng: random.Random) -> Question:
    for _ in range(50):
        q = rng.choice(TWO_DIGIT_RECURRING_DENOMINATORS)
        p = rng.randint(1, q - 1)
        if math.gcd(p, q) != 1:
            continue
        non_recurring, recurring = _decimal_expansion(p, q)
        if recurring is not None and not non_recurring and len(recurring) == 2:
            break
    else:
        raise ValueError("recurring_decimal_two_digit could not find valid parameters")

    block = "".join(map(str, recurring))
    display_str = f"0.({block})"

    # Independent verification: a purely-recurring two-digit block "ab" means the decimal
    # equals ab/99 exactly - a separate closed-form derivation from the digit-counting
    # expansion above. Confirm it matches the originally-chosen p/q, then round-trip the
    # reduced fraction back through the digit-expansion helper and confirm it reproduces
    # the same two-digit repeating block.
    block_value = int(block)
    derived = Fraction(block_value, 99)
    if derived != Fraction(p, q):
        raise ValueError("recurring_decimal_two_digit verification failed")
    check_non_recurring, check_recurring = _decimal_expansion(p, q)
    if check_non_recurring or check_recurring != recurring:
        raise ValueError("recurring_decimal_two_digit round-trip verification failed")

    steps = [
        f"Let x = {display_str}, so 100x = {block}.{block}{block}... "
        "(two digits repeat, so multiply by 100 to shift a full block)",
        f"Subtract: 100x - x = {block_value} - 0, so 99x = {block_value}",
        f"x = {block_value}/99 = {p}/{q}",
    ]
    return Question(
        topic_id="recurring_decimal_two_digit",
        tier=Tier.HIGHER,
        prompt=f"The recurring decimal {display_str} can be written as a fraction. Find this fraction in its simplest form.",
        solution_steps=tuple(steps),
        final_answer=f"{p}/{q}",
        dedup_key=f"recurring_2d:{p}:{q}",
    )


def _rand_decimal(rng: random.Random, dp: int, int_lo: int = 1, int_hi: int = 99) -> Decimal:
    int_part = rng.randint(int_lo, int_hi)
    frac_part = rng.randint(0, 10**dp - 1)
    return Decimal(f"{int_part}.{str(frac_part).zfill(dp)}")


def generate_decimals_add_subtract(tier: Tier, rng: random.Random) -> Question:
    dp1 = rng.choice([1, 2])
    dp2 = rng.choice([1, 2])
    v1 = _rand_decimal(rng, dp1)
    v2 = _rand_decimal(rng, dp2)
    op = rng.choice(["+", "-"])
    if op == "-" and v1 < v2:
        v1, v2 = v2, v1

    result = v1 + v2 if op == "+" else v1 - v2

    # Independent verification via exact Fraction arithmetic - a different exact path than
    # Decimal's own +/- operators.
    f1, f2 = Fraction(str(v1)), Fraction(str(v2))
    check = f1 + f2 if op == "+" else f1 - f2
    if check != Fraction(str(result)):
        raise ValueError("decimals_add_subtract verification failed")

    steps = [
        "Line up the decimal points, padding with a zero so both numbers have the same number of decimal places.",
        f"{v1} {op} {v2} = {result}",
    ]
    return Question(
        topic_id="decimals_add_subtract",
        tier=Tier.FOUNDATION,
        prompt=f"Work out {v1} {op} {v2}.",
        solution_steps=tuple(steps),
        final_answer=_fmt_decimal_fixed(result),
        dedup_key=f"add_sub_dec:{v1}:{v2}:{op}",
    )


def generate_decimals_multiply(tier: Tier, rng: random.Random) -> Question:
    dp1 = rng.choice([1, 2])
    dp2 = rng.choice([1, 2])
    v1 = _rand_decimal(rng, dp1, int_lo=1, int_hi=20)
    v2 = _rand_decimal(rng, dp2, int_lo=1, int_hi=20)

    result = v1 * v2

    # Independent verification via exact Fraction arithmetic - a different exact path than
    # Decimal multiplication.
    check = Fraction(str(v1)) * Fraction(str(v2))
    if check != Fraction(str(result)):
        raise ValueError("decimals_multiply verification failed")

    int1 = int(v1 * (10**dp1))
    int2 = int(v2 * (10**dp2))
    total_dp = dp1 + dp2
    product_int = int1 * int2

    steps = [
        f"Ignore the decimal points and multiply the whole numbers: {int1} × {int2} = {product_int}",
        f"Count the total decimal places in the question: {dp1} + {dp2} = {total_dp}",
        f"Place the decimal point {total_dp} place{'s' if total_dp != 1 else ''} from the right: {result}",
    ]
    return Question(
        topic_id="decimals_multiply",
        tier=Tier.FOUNDATION,
        prompt=f"Work out {v1} × {v2}.",
        solution_steps=tuple(steps),
        final_answer=_fmt_decimal_fixed(result),
        dedup_key=f"multiply_dec:{v1}:{v2}",
    )


def generate_dividing_decimals(tier: Tier, rng: random.Random) -> Question:
    shape = rng.choice(["by_integer", "by_decimal"])

    if shape == "by_integer":
        divisor = rng.randint(2, 12)
        quotient = Decimal(f"{rng.randint(2, 20)}.{rng.randint(0, 9)}")
        dividend = quotient * divisor

        # Independent check via exact Fraction arithmetic (a different path than Decimal multiplication).
        check = Fraction(str(dividend)) / Fraction(divisor)
        if check != Fraction(str(quotient)):
            raise ValueError("dividing_decimals verification failed")

        steps = [f"{dividend} ÷ {divisor} = {quotient}"]
        dedup_key = f"div_int:{dividend}:{divisor}"
    else:
        dp = rng.choice([1, 2])
        scale = 10**dp
        divisor_int = rng.randint(2, 9)
        quotient = rng.randint(2, 15)
        dividend_int = quotient * divisor_int
        divisor = Decimal(divisor_int) / Decimal(scale)
        dividend = Decimal(dividend_int) / Decimal(scale)

        # Independent check via exact Fraction arithmetic on the original (unscaled) decimals.
        check = Fraction(str(dividend)) / Fraction(str(divisor))
        if check != Fraction(quotient):
            raise ValueError("dividing_decimals verification failed")

        steps = [
            f"Multiply both numbers by {scale} so the divisor becomes a whole number: "
            f"{dividend} × {scale} = {dividend_int}, {divisor} × {scale} = {divisor_int}",
            f"{dividend_int} ÷ {divisor_int} = {quotient}",
        ]
        dedup_key = f"div_dec:{dividend}:{divisor}"

    return Question(
        topic_id="decimals_divide",
        tier=Tier.FOUNDATION,
        prompt=f"Work out {dividend} ÷ {divisor}.",
        solution_steps=tuple(steps),
        final_answer=str(quotient),
        dedup_key=dedup_key,
    )


_POWER_OF_TEN_SHIFT = {10: 1, 100: 2, 1000: 3}


def generate_powers_of_ten(tier: Tier, rng: random.Random) -> Question:
    power = rng.choice([10, 100, 1000])
    shift = _POWER_OF_TEN_SHIFT[power]
    op = rng.choice(["multiply", "divide"])
    if rng.choice([True, False]):
        value = Decimal(f"{rng.randint(1, 99)}.{rng.randint(1, 99):02d}")
    else:
        value = Decimal(rng.randint(1, 999))

    result = value.scaleb(shift if op == "multiply" else -shift)

    # Independent check via exact Fraction arithmetic (a different path than Decimal.scaleb).
    frac_result = Fraction(str(value)) * power if op == "multiply" else Fraction(str(value)) / power
    if frac_result != Fraction(str(result)):
        raise ValueError("powers_of_ten verification failed")

    sign = "×" if op == "multiply" else "÷"
    direction = "right" if op == "multiply" else "left"
    plural = "s" if shift != 1 else ""
    steps = [
        f"{'Multiplying' if op == 'multiply' else 'Dividing'} by {power} moves the decimal point "
        f"{shift} place{plural} to the {direction}.",
        f"{_fmt_decimal_fixed(value)} {sign} {power} = {_fmt_decimal_fixed(result)}",
    ]
    return Question(
        topic_id="number_powers_of_ten",
        tier=Tier.FOUNDATION,
        prompt=f"Work out {_fmt_decimal_fixed(value)} {sign} {power}.",
        solution_steps=tuple(steps),
        final_answer=_fmt_decimal_fixed(result),
        dedup_key=f"pow10:{value}:{power}:{op}",
    )


def generate_modelled_example_round_to_decimal_places(tier: Tier, rng: random.Random) -> ModelledExample:
    integer_part = rng.randint(1, 99)
    frac_digits = [rng.randint(0, 9) for _ in range(3)]
    value = Decimal(f"{integer_part}.{''.join(map(str, frac_digits))}")
    round_to = rng.randint(1, 2)

    quantize_exp = Decimal(1).scaleb(-round_to)
    correct = value.quantize(quantize_exp, rounding=ROUND_HALF_UP)

    # Independent verification via exact Fraction arithmetic (separate path from Decimal.quantize).
    value_fraction = Fraction(str(value))
    manual = _round_half_up_fraction(value_fraction, round_to)
    if manual != Fraction(correct):
        raise ValueError("modelled example round_to_decimal_places verification failed")

    deciding_digit = frac_digits[round_to] if round_to < len(frac_digits) else 0
    direction = "up" if deciding_digit >= 5 else "down"
    plural = "s" if round_to != 1 else ""
    kept_digits = "".join(map(str, frac_digits[:round_to])) or "(none)"

    teaching_steps = [
        f"To round {value} to {round_to} decimal place{plural}, first count {round_to} digit{plural} "
        f"after the decimal point — these are the digits we plan to keep: {kept_digits}.",
        f"Then look at the very next digit along after those — this is the 'decider' digit. Here "
        f"it's {deciding_digit}.",
        "If the decider digit is 5 or more, round the last kept digit up by 1; if it's 4 or less, "
        f"leave the last kept digit as it is. Since the decider here is {deciding_digit}, we round {direction}.",
        f"All digits after the {round_to} decimal place{plural} we're keeping are then dropped "
        f"completely, giving {_fmt_decimal_fixed(correct)}.",
    ]
    worked_calculation = [
        f"{value} to {round_to} d.p.",
        f"decider digit = {deciding_digit} -> round {direction}",
        f"= {_fmt_decimal_fixed(correct)}",
    ]
    return ModelledExample(
        topic_id="decimals_round_dp",
        tier=Tier.FOUNDATION,
        prompt=f"Round {value} to {round_to} decimal place{plural}.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=_fmt_decimal_fixed(correct),
    )


def generate_modelled_example_round_to_significant_figures(tier: Tier, rng: random.Random) -> ModelledExample:
    integer_part = rng.randint(0, 999)
    frac_digits = [rng.randint(0, 9) for _ in range(3)]
    value = Decimal(f"{integer_part}.{''.join(map(str, frac_digits))}")
    if value == 0:
        value = Decimal("1.234")
    sig_figs = rng.choice([1, 2, 3])

    d = value.adjusted()
    quantize_exp = Decimal(1).scaleb(d - sig_figs + 1)
    rounded = value.quantize(quantize_exp, rounding=ROUND_HALF_UP)

    # Independent verification: the rounded value must lie within half a unit-in-the-last-place
    # of the original value (a proximity invariant, checked via a different computation than quantize).
    half_ulp = Decimal(1).scaleb(d - sig_figs + 1) / 2
    if abs(rounded - value) > half_ulp + Decimal("1e-12"):
        raise ValueError("modelled example round_to_significant_figures verification failed")

    plural = "s" if sig_figs != 1 else ""
    teaching_steps = [
        f"Significant figures are counted starting from the first non-zero digit in the number, "
        f"reading left to right — leading zeros never count. So for {value}, we count "
        f"{sig_figs} figure{plural} onward from that first non-zero digit.",
        f"To round to {sig_figs} significant figure{plural}, identify the last figure we're keeping, "
        "then look at the next digit along to decide whether it rounds up or stays the same — exactly "
        "the same rule as decimal places: 5 or more rounds up, 4 or less stays the same.",
        "Any digits after the significant figures we're keeping are dropped, but if the last kept "
        "figure sits to the left of the decimal point, we replace the dropped digits with zeros as "
        "placeholders so the number keeps the correct overall size.",
        f"Applying this to {value} with {sig_figs} significant figure{plural} gives "
        f"{_fmt_decimal_fixed(rounded)}.",
    ]
    worked_calculation = [
        f"{value} to {sig_figs} s.f.",
        f"first {sig_figs} significant figure{plural}",
        f"= {_fmt_decimal_fixed(rounded)}",
    ]
    return ModelledExample(
        topic_id="decimals_round_sf",
        tier=Tier.FOUNDATION,
        prompt=f"Round {value} to {sig_figs} significant figure{plural}.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=_fmt_decimal_fixed(rounded),
    )


def generate_modelled_example_ordering(tier: Tier, rng: random.Random) -> ModelledExample:
    ks = rng.sample(range(5, 96), 4)
    formats = [rng.choice(["decimal", "fraction", "percent"]) for _ in ks]

    display_strs = []
    for k, fmt in zip(ks, formats):
        if fmt == "percent":
            display_strs.append(f"{k}%")
        elif fmt == "decimal":
            display_strs.append(_fmt_decimal_fixed(Decimal(k) / 100))
        else:
            frac = Fraction(k, 100)
            display_strs.append(f"{frac.numerator}/{frac.denominator}")

    # Independent verification: parse each display string back to a Fraction using
    # format-specific parsing logic and confirm it reconstructs the original k/100 exactly.
    for display, k in zip(display_strs, ks):
        if display.endswith("%"):
            parsed = Fraction(int(display[:-1]), 100)
        elif "/" in display:
            num, den = display.split("/")
            parsed = Fraction(int(num), int(den))
        else:
            parsed = Fraction(display)
        if parsed != Fraction(k, 100):
            raise ValueError("modelled example ordering verification failed")

    order = sorted(range(4), key=lambda i: ks[i])
    ordered_display = [display_strs[i] for i in order]
    conversions = [f"{display_strs[i]} = {float(Fraction(ks[i], 100)):.2f}" for i in range(4)]

    teaching_steps = [
        "These values are given in a mix of formats — percentages, fractions, and decimals — and it's "
        "not safe to compare them directly while they're in different forms, so the first step is "
        "always to convert every value into the SAME format. Decimals are usually the easiest common "
        "format to compare.",
        "To convert a percentage to a decimal, divide by 100. To convert a fraction to a decimal, "
        "divide the numerator by the denominator.",
        f"Converting each value here: {', '.join(conversions)}.",
        "Now that every value is a decimal, compare them place by place (ones, then tenths, then "
        "hundredths) to put them in order from smallest to largest.",
        "Finally, write the answer using each value's ORIGINAL format — we only converted to decimals "
        "to compare them, not to change how the answer should be presented.",
    ]
    worked_calculation = [
        f"{', '.join(display_strs)}",
        f"= {', '.join(conversions)}",
        f"order: {', '.join(ordered_display)}",
    ]
    return ModelledExample(
        topic_id="decimals_ordering",
        tier=Tier.FOUNDATION,
        prompt=f"Write these values in order, starting with the smallest: {', '.join(display_strs)}",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=", ".join(ordered_display),
    )


def generate_modelled_example_recurring_decimal_to_fraction(tier: Tier, rng: random.Random) -> ModelledExample:
    for _ in range(100):
        q = rng.choice(RECURRING_DENOMINATORS)
        p = rng.randint(1, q - 1)
        if math.gcd(p, q) == 1:
            non_recurring, recurring = _decimal_expansion(p, q)
            if recurring is not None:
                break
    else:
        raise ValueError("modelled example recurring_decimal_to_fraction could not find valid parameters")

    n, r = len(non_recurring), len(recurring)
    prefix_val = int("".join(map(str, non_recurring))) if non_recurring else 0
    full_val = int("".join(map(str, non_recurring + recurring)))
    numerator = full_val - prefix_val
    denominator = 10 ** (n + r) - 10**n
    derived = Fraction(numerator, denominator)

    if derived != Fraction(p, q):
        raise ValueError("modelled example recurring_decimal_to_fraction verification failed")

    prefix_str = "".join(map(str, non_recurring))
    recurring_str = "".join(map(str, recurring))
    display_str = f"0.{prefix_str}({recurring_str})"
    shift_small = 10**n
    shift_large = 10 ** (n + r)

    teaching_steps = [
        "Recurring decimals can't be converted to fractions just by reading off digits, because they "
        f"go on forever — instead there's an algebraic trick. Start by calling the decimal x, so "
        f"x = {display_str}.",
        f"Multiply x by a power of 10 so the decimal point sits just before the recurring block starts: "
        f"{shift_small} × x shifts the point past the non-recurring part.",
        f"Multiply x by a bigger power of 10 so the decimal point sits one full recurring block further "
        f"along: {shift_large} × x shifts the point past one whole extra repeat of the recurring block. "
        "Crucially, both of these still have exactly the same recurring digits continuing forever after "
        "their decimal point.",
        f"Subtracting the smaller multiple from the larger one cancels the recurring tail completely "
        f"(since it's identical in both), leaving a normal, finite equation: "
        f"({shift_large} - {shift_small})x = {full_val} - {prefix_val} = {numerator}.",
        f"Divide both sides by {denominator} to get x on its own, then simplify the fraction: "
        f"x = {numerator}/{denominator} = {p}/{q}.",
    ]
    worked_calculation = [
        f"x = {display_str}",
        f"{shift_large}x - {shift_small}x = {full_val} - {prefix_val}",
        f"{shift_large - shift_small}x = {numerator}",
        f"x = {numerator}/{denominator}",
        f"= {p}/{q}",
    ]
    return ModelledExample(
        topic_id="decimals_recurring_to_fraction",
        tier=Tier.HIGHER,
        prompt=f"The recurring decimal {display_str} can be written as a fraction. Find this fraction in its simplest form.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{p}/{q}",
    )


def generate_modelled_example_recurring_decimal_single_digit(tier: Tier, rng: random.Random) -> ModelledExample:
    for _ in range(50):
        q = rng.choice(SINGLE_DIGIT_RECURRING_DENOMINATORS)
        p = rng.randint(1, q - 1)
        if math.gcd(p, q) != 1:
            continue
        non_recurring, recurring = _decimal_expansion(p, q)
        if recurring is not None and not non_recurring and len(recurring) == 1:
            break
    else:
        raise ValueError("modelled example recurring_decimal_single_digit could not find valid parameters")

    digit = recurring[0]
    display_str = f"0.({digit})"

    derived = Fraction(digit, 9)
    if derived != Fraction(p, q):
        raise ValueError("modelled example recurring_decimal_single_digit verification failed")
    check_non_recurring, check_recurring = _decimal_expansion(p, q)
    if check_non_recurring or check_recurring != [digit]:
        raise ValueError("modelled example recurring_decimal_single_digit round-trip verification failed")

    teaching_steps = [
        f"A recurring decimal like {display_str} repeats the same digit forever, and there's a neat "
        "algebraic trick to turn it into a fraction. Start by calling the whole decimal x, so "
        f"x = {display_str}.",
        f"Since only ONE digit repeats, multiply x by 10 - this shifts the decimal point one place, "
        f"landing it right after the next copy of the repeating digit: 10x = {digit}.{digit}{digit}{digit}...",
        f"Both x and 10x still have the exact same digit {digit} repeating forever after their decimal "
        f"point, so subtracting x from 10x cancels the recurring part completely, leaving a normal, "
        f"finite equation: 10x - x = {digit} - 0, i.e. 9x = {digit}.",
        f"Divide both sides by 9 to get x on its own: x = {digit}/9, then simplify if possible - here "
        f"that gives x = {p}/{q}.",
    ]
    worked_calculation = [
        f"x = {display_str}",
        f"10x - x = {digit}",
        f"9x = {digit}",
        f"x = {digit}/9",
    ]
    if f"{p}/{q}" != f"{digit}/9":
        worked_calculation.append(f"= {p}/{q}")

    return ModelledExample(
        topic_id="recurring_decimal_single_digit",
        tier=Tier.FOUNDATION,
        prompt=f"The recurring decimal {display_str} can be written as a fraction. Find this fraction in its simplest form.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{p}/{q}",
    )


def generate_modelled_example_recurring_decimal_two_digit(tier: Tier, rng: random.Random) -> ModelledExample:
    for _ in range(50):
        q = rng.choice(TWO_DIGIT_RECURRING_DENOMINATORS)
        p = rng.randint(1, q - 1)
        if math.gcd(p, q) != 1:
            continue
        non_recurring, recurring = _decimal_expansion(p, q)
        if recurring is not None and not non_recurring and len(recurring) == 2:
            break
    else:
        raise ValueError("modelled example recurring_decimal_two_digit could not find valid parameters")

    block = "".join(map(str, recurring))
    display_str = f"0.({block})"
    block_value = int(block)

    derived = Fraction(block_value, 99)
    if derived != Fraction(p, q):
        raise ValueError("modelled example recurring_decimal_two_digit verification failed")
    check_non_recurring, check_recurring = _decimal_expansion(p, q)
    if check_non_recurring or check_recurring != recurring:
        raise ValueError("modelled example recurring_decimal_two_digit round-trip verification failed")

    teaching_steps = [
        f"This decimal, {display_str}, repeats a whole BLOCK of two digits ('{block}') forever, rather "
        f"than just one digit - the same algebraic trick still works, we just need to shift by a full "
        f"block instead of a single place. Start by calling the decimal x, so x = {display_str}.",
        f"Multiply x by 100 (not 10) so the decimal point shifts past one entire two-digit block: "
        f"100x = {block}.{block}{block}...",
        f"Both x and 100x have the identical two-digit block repeating forever afterwards, so "
        f"subtracting x from 100x cancels the recurring part completely: 100x - x = {block_value} - 0, "
        f"i.e. 99x = {block_value}.",
        f"Divide both sides by 99 to get x on its own: x = {block_value}/99, then simplify - here that "
        f"gives x = {p}/{q}.",
    ]
    worked_calculation = [
        f"x = {display_str}",
        f"100x - x = {block_value}",
        f"99x = {block_value}",
        f"x = {block_value}/99",
    ]
    if f"{p}/{q}" != f"{block_value}/99":
        worked_calculation.append(f"= {p}/{q}")

    return ModelledExample(
        topic_id="recurring_decimal_two_digit",
        tier=Tier.HIGHER,
        prompt=f"The recurring decimal {display_str} can be written as a fraction. Find this fraction in its simplest form.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{p}/{q}",
    )


def generate_modelled_example_decimals_add_subtract(tier: Tier, rng: random.Random) -> ModelledExample:
    dp1 = rng.choice([1, 2])
    dp2 = rng.choice([1, 2])
    v1 = _rand_decimal(rng, dp1)
    v2 = _rand_decimal(rng, dp2)
    op = rng.choice(["+", "-"])
    if op == "-" and v1 < v2:
        v1, v2 = v2, v1

    result = v1 + v2 if op == "+" else v1 - v2

    f1, f2 = Fraction(str(v1)), Fraction(str(v2))
    check = f1 + f2 if op == "+" else f1 - f2
    if check != Fraction(str(result)):
        raise ValueError("modelled example decimals_add_subtract verification failed")

    verb = "add" if op == "+" else "subtract"
    teaching_steps = [
        f"To {verb} decimals, the golden rule is to line up the decimal points first, so that digits in "
        "the same place-value column (ones with ones, tenths with tenths, hundredths with hundredths) "
        "are combined together.",
        f"{v1} and {v2} don't have the same number of decimal places, so pad the shorter one with a "
        "trailing zero - this doesn't change its value at all, it just makes the columns line up neatly.",
        f"Now {verb} column by column exactly as you would with whole numbers, carrying or borrowing "
        "between columns as needed, and put the decimal point in the answer directly below the others.",
        f"{v1} {op} {v2} = {result}.",
    ]
    worked_calculation = [
        f"{v1} {op} {v2}",
        f"= {result}",
    ]
    return ModelledExample(
        topic_id="decimals_add_subtract",
        tier=Tier.FOUNDATION,
        prompt=f"Work out {v1} {op} {v2}.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=_fmt_decimal_fixed(result),
    )


def generate_modelled_example_decimals_multiply(tier: Tier, rng: random.Random) -> ModelledExample:
    dp1 = rng.choice([1, 2])
    dp2 = rng.choice([1, 2])
    v1 = _rand_decimal(rng, dp1, int_lo=1, int_hi=20)
    v2 = _rand_decimal(rng, dp2, int_lo=1, int_hi=20)

    result = v1 * v2

    check = Fraction(str(v1)) * Fraction(str(v2))
    if check != Fraction(str(result)):
        raise ValueError("modelled example decimals_multiply verification failed")

    int1 = int(v1 * (10**dp1))
    int2 = int(v2 * (10**dp2))
    total_dp = dp1 + dp2
    product_int = int1 * int2
    plural = "s" if total_dp != 1 else ""

    teaching_steps = [
        f"Multiplying decimals directly is awkward, so the standard trick is to ignore the decimal "
        f"points completely first and multiply the digits as if they were whole numbers: "
        f"{int1} × {int2} = {product_int}.",
        f"While we ignored the decimal points, we didn't lose that information - we just need to put it "
        f"back at the end. Count the TOTAL number of decimal places across both original numbers: "
        f"{v1} has {dp1} and {v2} has {dp2}, giving {total_dp} in total.",
        f"Place the decimal point in {product_int} so that the answer has exactly {total_dp} decimal "
        f"place{plural} - counting {total_dp} digit{plural} in from the right-hand end.",
        f"So {v1} × {v2} = {result}.",
    ]
    worked_calculation = [
        f"{v1} × {v2}",
        f"= {int1} × {int2}",
        f"= {product_int}",
        f"= {result}",
    ]
    return ModelledExample(
        topic_id="decimals_multiply",
        tier=Tier.FOUNDATION,
        prompt=f"Work out {v1} × {v2}.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=_fmt_decimal_fixed(result),
    )


def generate_modelled_example_dividing_decimals(tier: Tier, rng: random.Random) -> ModelledExample:
    shape = rng.choice(["by_integer", "by_decimal"])

    if shape == "by_integer":
        divisor = rng.randint(2, 12)
        quotient = Decimal(f"{rng.randint(2, 20)}.{rng.randint(0, 9)}")
        dividend = quotient * divisor

        # Independent check via exact Fraction arithmetic (a different path than Decimal multiplication).
        check = Fraction(str(dividend)) / Fraction(divisor)
        if check != Fraction(str(quotient)):
            raise ValueError("modelled example dividing_decimals verification failed")

        teaching_steps = [
            "Dividing a decimal by a whole number works just like ordinary short/long division — the "
            f"decimal point in the answer lines up directly above the decimal point in {dividend}.",
            f"Divide as normal, digit by digit, exactly as you would for {dividend} ÷ {divisor} if "
            "there were no decimal point at all, then place the decimal point in the answer directly "
            "above where it is in the dividend.",
            f"{dividend} ÷ {divisor} = {quotient}.",
        ]
        worked_calculation = [
            f"{dividend} ÷ {divisor}",
            f"= {quotient}",
        ]
        prompt = f"Work out {dividend} ÷ {divisor}."
        final_answer = str(quotient)
    else:
        dp = rng.choice([1, 2])
        scale = 10**dp
        divisor_int = rng.randint(2, 9)
        quotient = rng.randint(2, 15)
        dividend_int = quotient * divisor_int
        divisor = Decimal(divisor_int) / Decimal(scale)
        dividend = Decimal(dividend_int) / Decimal(scale)

        # Independent check via exact Fraction arithmetic on the original (unscaled) decimals.
        check = Fraction(str(dividend)) / Fraction(str(divisor))
        if check != Fraction(quotient):
            raise ValueError("modelled example dividing_decimals verification failed")

        teaching_steps = [
            "Dividing by a decimal is awkward, so the standard trick is to turn the divisor into a "
            "whole number first. To do that, multiply BOTH the dividend and the divisor by the same "
            "power of 10 — this doesn't change the answer, since scaling the top and bottom of a "
            "division by the same amount leaves the result unchanged.",
            f"Here the divisor {divisor} needs multiplying by {scale} to become the whole number "
            f"{divisor_int}, so we multiply {dividend} by {scale} too, giving {dividend_int}.",
            f"Now it's a straightforward whole-number-divisor division: "
            f"{dividend_int} ÷ {divisor_int} = {quotient}.",
            f"So the original division {dividend} ÷ {divisor} also equals {quotient}.",
        ]
        worked_calculation = [
            f"{dividend} ÷ {divisor}",
            f"= ({dividend}×{scale}) ÷ ({divisor}×{scale})",
            f"= {dividend_int} ÷ {divisor_int}",
            f"= {quotient}",
        ]
        prompt = f"Work out {dividend} ÷ {divisor}."
        final_answer = str(quotient)

    return ModelledExample(
        topic_id="decimals_divide",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=final_answer,
    )


def generate_modelled_example_powers_of_ten(tier: Tier, rng: random.Random) -> ModelledExample:
    power = rng.choice([10, 100, 1000])
    shift = _POWER_OF_TEN_SHIFT[power]
    op = rng.choice(["multiply", "divide"])
    if rng.choice([True, False]):
        value = Decimal(f"{rng.randint(1, 99)}.{rng.randint(1, 99):02d}")
    else:
        value = Decimal(rng.randint(1, 999))

    result = value.scaleb(shift if op == "multiply" else -shift)

    # Independent check via exact Fraction arithmetic (a different path than Decimal.scaleb).
    frac_result = Fraction(str(value)) * power if op == "multiply" else Fraction(str(value)) / power
    if frac_result != Fraction(str(result)):
        raise ValueError("modelled example powers_of_ten verification failed")

    sign = "×" if op == "multiply" else "÷"
    direction = "right" if op == "multiply" else "left"
    plural = "s" if shift != 1 else ""

    teaching_steps = [
        "Multiplying by a power of 10 makes a number bigger by shifting every digit to the left; "
        "dividing by a power of 10 makes a number smaller by shifting every digit to the right. The "
        f"number of places shifted matches the number of zeros in the power of 10 — {power} has "
        f"{shift} zero{plural}, so we shift {shift} place{plural}.",
        f"Here we're {'multiplying' if op == 'multiply' else 'dividing'} by {power}, so every digit in "
        f"{_fmt_decimal_fixed(value)} moves {shift} place{plural} to the {direction} — equivalently, "
        f"think of it as the decimal point moving {shift} place{plural} to the {direction} instead.",
        "If there aren't enough digits to fill the gap, extra zeros are used as placeholders so every "
        "digit still ends up in its correct place-value column.",
        f"So {_fmt_decimal_fixed(value)} {sign} {power} = {_fmt_decimal_fixed(result)}.",
    ]
    worked_calculation = [
        f"{_fmt_decimal_fixed(value)} {sign} {power}",
        f"move decimal point {shift} place{plural} {direction}",
        f"= {_fmt_decimal_fixed(result)}",
    ]
    return ModelledExample(
        topic_id="number_powers_of_ten",
        tier=Tier.FOUNDATION,
        prompt=f"Work out {_fmt_decimal_fixed(value)} {sign} {power}.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=_fmt_decimal_fixed(result),
    )


TOPIC_ROUND_DP = TopicDefinition(
    id="decimals_round_dp",
    display_name="Rounding to Decimal Places",
    description="Round a number to a given number of decimal places.",
    generate=generate_round_to_decimal_places,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_round_to_decimal_places,
)

TOPIC_ROUND_SF = TopicDefinition(
    id="decimals_round_sf",
    display_name="Rounding to Significant Figures",
    description="Round a number to a given number of significant figures.",
    generate=generate_round_to_significant_figures,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_round_to_significant_figures,
)

TOPIC_ORDERING = TopicDefinition(
    id="decimals_ordering",
    display_name="Ordering Decimals, Fractions & Percentages",
    description="Order a mixed list of decimals, fractions, and percentages.",
    generate=generate_ordering,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_ordering,
)

TOPIC_RECURRING_TO_FRACTION = TopicDefinition(
    id="decimals_recurring_to_fraction",
    display_name="Recurring Decimals to Fractions",
    description="Convert a recurring decimal to a fraction in its simplest form.",
    generate=generate_recurring_decimal_to_fraction,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_recurring_decimal_to_fraction,
)

TOPIC_DIVIDE = TopicDefinition(
    id="decimals_divide",
    display_name="Dividing Decimals",
    description="Divide a decimal by a whole number, or by another decimal.",
    generate=generate_dividing_decimals,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_dividing_decimals,
)

TOPIC_POWERS_OF_TEN = TopicDefinition(
    id="number_powers_of_ten",
    display_name="Multiplying & Dividing by Powers of 10",
    description="Multiply or divide a number by 10, 100, or 1000.",
    generate=generate_powers_of_ten,
    section=SECTION,
    group="Multiplying & Dividing by Powers of 10",
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_powers_of_ten,
)

TOPIC_ADD_SUBTRACT = TopicDefinition(
    id="decimals_add_subtract",
    display_name="Adding and Subtracting Decimals",
    description="Add or subtract two decimals with a mixed number of decimal places.",
    generate=generate_decimals_add_subtract,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_decimals_add_subtract,
)

TOPIC_MULTIPLY = TopicDefinition(
    id="decimals_multiply",
    display_name="Multiplying Decimals",
    description="Multiply two decimals together.",
    generate=generate_decimals_multiply,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_decimals_multiply,
)

# Only 8 distinct (numerator, denominator) pairs exist for a purely-recurring single-digit
# decimal with no non-recurring prefix (reduced denominator must divide 9 - see the
# generator's docstring-style comment above), so question_count is capped well below the
# usual 20-question default, matching the precedent set by the Plotting Graphs topics
# (see CLAUDE.md's "Watch the dedup-key state space" note).
TOPIC_RECURRING_SINGLE_DIGIT = TopicDefinition(
    id="recurring_decimal_single_digit",
    display_name="Recurring Decimals to Fractions (One Digit)",
    description="Convert a purely recurring decimal with a single repeating digit to a fraction.",
    generate=generate_recurring_decimal_single_digit,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    question_count=6,
    generate_modelled_example=generate_modelled_example_recurring_decimal_single_digit,
)

TOPIC_RECURRING_TWO_DIGIT = TopicDefinition(
    id="recurring_decimal_two_digit",
    display_name="Recurring Decimals to Fractions (Two Digits)",
    description="Convert a purely recurring decimal with a two-digit repeating block to a fraction.",
    generate=generate_recurring_decimal_two_digit,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_recurring_decimal_two_digit,
)
