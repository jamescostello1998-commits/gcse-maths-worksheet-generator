import math
import random
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction

from app.core.models import Question, Tier
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


TOPIC_ROUND_DP = TopicDefinition(
    id="decimals_round_dp",
    display_name="Rounding to Decimal Places",
    description="Round a number to a given number of decimal places.",
    generate=generate_round_to_decimal_places,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
)

TOPIC_ROUND_SF = TopicDefinition(
    id="decimals_round_sf",
    display_name="Rounding to Significant Figures",
    description="Round a number to a given number of significant figures.",
    generate=generate_round_to_significant_figures,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
)

TOPIC_ORDERING = TopicDefinition(
    id="decimals_ordering",
    display_name="Ordering Decimals, Fractions & Percentages",
    description="Order a mixed list of decimals, fractions, and percentages.",
    generate=generate_ordering,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
)

TOPIC_RECURRING_TO_FRACTION = TopicDefinition(
    id="decimals_recurring_to_fraction",
    display_name="Recurring Decimals to Fractions",
    description="Convert a recurring decimal to a fraction in its simplest form.",
    generate=generate_recurring_decimal_to_fraction,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
)
