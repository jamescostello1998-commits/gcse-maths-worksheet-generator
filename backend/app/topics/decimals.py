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
