import math
import random
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction

from app.core.models import ModelledExample, Question, Tier
from app.topics.base import TopicDefinition

SECTION = "number"
GROUP = "Estimation & Bounds"


def _fmt_frac(fr: Fraction) -> str:
    """Render an exact Fraction as a clean integer, terminating decimal, or
    (failing that) a reduced fraction - never a rounded float."""
    if fr.denominator == 1:
        return str(fr.numerator)
    denom = fr.denominator
    while denom % 2 == 0:
        denom //= 2
    while denom % 5 == 0:
        denom //= 5
    if denom != 1:
        return f"{fr.numerator}/{fr.denominator}"
    s = format(Decimal(fr.numerator) / Decimal(fr.denominator), "f")
    return s.rstrip("0").rstrip(".") if "." in s else s


def _round_1dp(fr: Fraction) -> Fraction:
    return Fraction(math.floor(fr * 10 + Fraction(1, 2)), 10)


def _round_to_1sf(value: Decimal) -> Decimal:
    exp = value.adjusted()
    return value.quantize(Decimal(1).scaleb(exp), rounding=ROUND_HALF_UP)


def _round_to_1sf_manual(value: Decimal) -> Fraction:
    """Independent re-derivation of 1-s.f. rounding: counts integer-part
    digits to find the place value, then rounds half-up in exact Fraction
    arithmetic - a different computation path than Decimal.adjusted()+quantize."""
    exp = len(str(int(value))) - 1
    scale = Fraction(10) ** exp
    scaled = Fraction(value) / scale
    return Fraction(math.floor(scaled + Fraction(1, 2))) * scale


def generate_estimation(tier: Tier, rng: random.Random) -> Question:
    a = Decimal(f"{rng.randint(11, 98)}.{rng.randint(0, 9)}")
    b = Decimal(f"{rng.randint(2, 9)}.{rng.randint(0, 9)}")
    c = Decimal(f"{rng.randint(2, 9)}.{rng.randint(0, 9)}")

    rounded_a, rounded_b, rounded_c = _round_to_1sf(a), _round_to_1sf(b), _round_to_1sf(c)

    for original, rounded in ((a, rounded_a), (b, rounded_b), (c, rounded_c)):
        if _round_to_1sf_manual(original) != Fraction(rounded):
            raise ValueError("estimation verification failed: 1 s.f. rounding mismatch")

    exact = Fraction(rounded_a) * Fraction(rounded_b) / Fraction(rounded_c)
    float_check = float(rounded_a) * float(rounded_b) / float(rounded_c)
    if abs(float(exact) - float_check) > 1e-9:
        raise ValueError("estimation verification failed: cross-check mismatch")

    answer = _fmt_frac(exact)
    steps = [
        f"Round each value to 1 significant figure: {a} ≈ {rounded_a}, {b} ≈ {rounded_b}, {c} ≈ {rounded_c}",
        f"({rounded_a} × {rounded_b}) ÷ {rounded_c} = {answer}",
    ]
    return Question(
        topic_id="estimation_rounding",
        tier=Tier.FOUNDATION,
        prompt=f"Work out an estimate for ({a} × {b}) ÷ {c} by rounding each number to 1 significant figure.",
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"estimation:{a}:{b}:{c}",
    )


_PRECISIONS: list[tuple[str, Fraction]] = [
    ("the nearest whole number", Fraction(1)),
    ("the nearest 10", Fraction(10)),
    ("1 decimal place", Fraction(1, 10)),
]


def generate_error_interval(tier: Tier, rng: random.Random) -> Question:
    label, precision = rng.choice(_PRECISIONS)
    half = precision / 2

    if precision == Fraction(1):
        v = Fraction(rng.randint(20, 200))
    elif precision == Fraction(10):
        v = Fraction(rng.randint(2, 40) * 10)
    else:
        v = Fraction(rng.randint(20, 200), 10)

    lower, upper = v - half, v + half

    # Independent verification via a different property than the subtraction/addition
    # used to build lower/upper: the interval must be symmetric about v and exactly
    # one precision wide.
    if lower + upper != 2 * v:
        raise ValueError("error_interval verification failed: not symmetric about v")
    if upper - lower != precision:
        raise ValueError("error_interval verification failed: wrong interval width")

    v_str, lower_str, upper_str = _fmt_frac(v), _fmt_frac(lower), _fmt_frac(upper)
    steps = [
        f"{v_str} is rounded to {label}, so x can be up to half of that precision above or below {v_str}.",
        f"Lower bound: {v_str} - {_fmt_frac(half)} = {lower_str}",
        f"Upper bound: {v_str} + {_fmt_frac(half)} = {upper_str}",
    ]
    answer = f"{lower_str} ≤ x < {upper_str}"
    return Question(
        topic_id="error_interval",
        tier=Tier.FOUNDATION,
        prompt=f"A number, x, is {v_str} rounded to {label}. Write down the error interval for x.",
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"error_interval:{label}:{v_str}",
    )


def generate_bounds_calculation(tier: Tier, rng: random.Random) -> Question:
    shape = rng.choice(["area", "speed"])
    bound_type = rng.choice(["upper", "lower"])
    half = Fraction(1, 2)

    if shape == "area":
        length = rng.randint(8, 40)
        width = rng.randint(5, 30)
        lower_l, upper_l = length - half, length + half
        lower_w, upper_w = width - half, width + half

        if bound_type == "upper":
            use_l, use_w = upper_l, upper_w
        else:
            use_l, use_w = lower_l, lower_w
        result = use_l * use_w

        # Independent verification: the chosen combination must be the true
        # extremum among all four corner combinations, not just "the formula".
        candidates = [lower_l * lower_w, lower_l * upper_w, upper_l * lower_w, upper_l * upper_w]
        expected = max(candidates) if bound_type == "upper" else min(candidates)
        if result != expected:
            raise ValueError("bounds_calculation verification failed: area not the true extremum")

        answer = f"{_fmt_frac(result)} cm²"
        steps = [
            f"Length: {length} cm (to the nearest cm) gives {_fmt_frac(lower_l)} ≤ length < {_fmt_frac(upper_l)}",
            f"Width: {width} cm (to the nearest cm) gives {_fmt_frac(lower_w)} ≤ width < {_fmt_frac(upper_w)}",
            f"For the {bound_type} bound of the area, use the {bound_type} bound of each measurement: "
            f"{_fmt_frac(use_l)} × {_fmt_frac(use_w)} = {answer}",
        ]
        prompt = (
            f"A rectangle has length {length} cm and width {width} cm, both measured to the nearest cm. "
            f"Calculate the {bound_type} bound for the area of the rectangle."
        )
        dedup_key = f"bounds_area:{bound_type}:{length}:{width}"
    else:
        distance = rng.randint(50, 300)
        time = rng.randint(4, 20)
        lower_d, upper_d = distance - half, distance + half
        lower_t, upper_t = time - half, time + half

        if bound_type == "upper":
            use_d, use_t = upper_d, lower_t
        else:
            use_d, use_t = lower_d, upper_t
        exact = use_d / use_t

        candidates = [lower_d / lower_t, lower_d / upper_t, upper_d / lower_t, upper_d / upper_t]
        expected = max(candidates) if bound_type == "upper" else min(candidates)
        if exact != expected:
            raise ValueError("bounds_calculation verification failed: speed not the true extremum")

        rounded = _round_1dp(exact)
        if abs(rounded - exact) > Fraction(1, 20):
            raise ValueError("bounds_calculation verification failed: rounding out of range")

        answer = f"{_fmt_frac(rounded)} km/h (to 1 d.p.)"
        steps = [
            f"Distance: {distance} km (to the nearest km) gives {_fmt_frac(lower_d)} ≤ distance < {_fmt_frac(upper_d)}",
            f"Time: {time} hours (to the nearest hour) gives {_fmt_frac(lower_t)} ≤ time < {_fmt_frac(upper_t)}",
            f"For the {bound_type} bound of the speed, divide the "
            + (
                "upper bound of distance by the lower bound of time"
                if bound_type == "upper"
                else "lower bound of distance by the upper bound of time"
            )
            + f": {_fmt_frac(use_d)} ÷ {_fmt_frac(use_t)} = {_fmt_frac(exact)} ≈ {_fmt_frac(rounded)} km/h",
        ]
        prompt = (
            f"A car travels {distance} km (to the nearest km) in {time} hours (to the nearest hour). "
            f"Calculate the {bound_type} bound for the average speed of the car, to 1 decimal place."
        )
        dedup_key = f"bounds_speed:{bound_type}:{distance}:{time}"

    return Question(
        topic_id="bounds_calculation",
        tier=Tier.HIGHER,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=dedup_key,
    )


def generate_modelled_example_estimation(tier: Tier, rng: random.Random) -> ModelledExample:
    a = Decimal(f"{rng.randint(11, 98)}.{rng.randint(0, 9)}")
    b = Decimal(f"{rng.randint(2, 9)}.{rng.randint(0, 9)}")
    c = Decimal(f"{rng.randint(2, 9)}.{rng.randint(0, 9)}")

    rounded_a, rounded_b, rounded_c = _round_to_1sf(a), _round_to_1sf(b), _round_to_1sf(c)

    for original, rounded in ((a, rounded_a), (b, rounded_b), (c, rounded_c)):
        if _round_to_1sf_manual(original) != Fraction(rounded):
            raise ValueError("modelled example estimation verification failed: 1 s.f. rounding mismatch")

    exact = Fraction(rounded_a) * Fraction(rounded_b) / Fraction(rounded_c)
    float_check = float(rounded_a) * float(rounded_b) / float(rounded_c)
    if abs(float(exact) - float_check) > 1e-9:
        raise ValueError("modelled example estimation verification failed: cross-check mismatch")

    answer = _fmt_frac(exact)
    teaching_steps = [
        f"An estimate replaces awkward decimals with simpler, rounded numbers that are much easier to "
        f"calculate with by hand, at the cost of a small amount of accuracy. Each of {a}, {b}, and {c} "
        "should be rounded to 1 significant figure - just its first non-zero digit, with every digit "
        "after it rounded away to zero.",
        f"{a} rounds to {rounded_a}, {b} rounds to {rounded_b}, and {c} rounds to {rounded_c} - in each "
        "case, look at the digit right after the first significant figure to decide whether it rounds "
        "up or stays the same.",
        "These rounded values are now simple enough to combine without a calculator: multiply the two "
        "rounded numbers on top, then divide by the rounded number on the bottom, following the same "
        "order as the original calculation.",
        f"({rounded_a} × {rounded_b}) ÷ {rounded_c} = {answer}. This is only an estimate, not the exact "
        "answer, because each original number was rounded before the calculation was carried out.",
    ]
    worked_calculation = [
        f"{a} ≈ {rounded_a}, {b} ≈ {rounded_b}, {c} ≈ {rounded_c}",
        f"({rounded_a} × {rounded_b}) ÷ {rounded_c}",
        f"= {answer}",
    ]
    return ModelledExample(
        topic_id="estimation_rounding",
        tier=Tier.FOUNDATION,
        prompt=f"Work out an estimate for ({a} × {b}) ÷ {c} by rounding each number to 1 significant figure.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
    )


def generate_modelled_example_error_interval(tier: Tier, rng: random.Random) -> ModelledExample:
    label, precision = rng.choice(_PRECISIONS)
    half = precision / 2

    if precision == Fraction(1):
        v = Fraction(rng.randint(20, 200))
    elif precision == Fraction(10):
        v = Fraction(rng.randint(2, 40) * 10)
    else:
        v = Fraction(rng.randint(20, 200), 10)

    lower, upper = v - half, v + half

    if lower + upper != 2 * v:
        raise ValueError("modelled example error_interval verification failed: not symmetric about v")
    if upper - lower != precision:
        raise ValueError("modelled example error_interval verification failed: wrong interval width")

    v_str, half_str, lower_str, upper_str = _fmt_frac(v), _fmt_frac(half), _fmt_frac(lower), _fmt_frac(upper)
    teaching_steps = [
        f"When a number has been rounded to {label}, the true (exact) value could be anything that "
        f"rounds to the stated value of {v_str} - not just {v_str} itself. The error interval describes "
        "the full range of possible true values that all round to the given number.",
        f"The true value can be at most half of the rounding precision away from {v_str}, in either "
        f"direction, because anything further away would round to a different value instead. Half of "
        f"the precision here is {half_str}.",
        f"Subtracting gives the lower bound: {v_str} - {half_str} = {lower_str}. This value IS included "
        f"in the interval, because it rounds back up to {v_str}.",
        f"Adding gives the upper bound: {v_str} + {half_str} = {upper_str}. This value is NOT included - "
        "it's the exact point where the number would round up to the next value instead - so the upper "
        "bound always uses a strict inequality.",
    ]
    worked_calculation = [
        f"x rounds to {v_str} ({label})",
        f"lower: {v_str} - {half_str} = {lower_str}",
        f"upper: {v_str} + {half_str} = {upper_str}",
    ]
    answer = f"{lower_str} ≤ x < {upper_str}"
    return ModelledExample(
        topic_id="error_interval",
        tier=Tier.FOUNDATION,
        prompt=f"A number, x, is {v_str} rounded to {label}. Write down the error interval for x.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
    )


def generate_modelled_example_bounds_calculation(tier: Tier, rng: random.Random) -> ModelledExample:
    shape = rng.choice(["area", "speed"])
    bound_type = rng.choice(["upper", "lower"])
    half = Fraction(1, 2)

    if shape == "area":
        length = rng.randint(8, 40)
        width = rng.randint(5, 30)
        lower_l, upper_l = length - half, length + half
        lower_w, upper_w = width - half, width + half

        if bound_type == "upper":
            use_l, use_w = upper_l, upper_w
        else:
            use_l, use_w = lower_l, lower_w
        result = use_l * use_w

        candidates = [lower_l * lower_w, lower_l * upper_w, upper_l * lower_w, upper_l * upper_w]
        expected = max(candidates) if bound_type == "upper" else min(candidates)
        if result != expected:
            raise ValueError("modelled example bounds_calculation verification failed: area not the true extremum")

        answer = f"{_fmt_frac(result)} cm²"
        teaching_steps = [
            f"Both the length ({length} cm) and width ({width} cm) have been rounded, so each one hides "
            "a small range of possible true values. To find the extreme (largest or smallest) possible "
            "area, the extreme values of length and width must be combined, not just the rounded values.",
            f"Rounding to the nearest cm means the true length lies between {_fmt_frac(lower_l)} cm and "
            f"{_fmt_frac(upper_l)} cm, and the true width lies between {_fmt_frac(lower_w)} cm and "
            f"{_fmt_frac(upper_w)} cm.",
            "Since area = length × width and both factors are positive, the "
            f"{bound_type} bound of the area comes from multiplying the {bound_type} bound of each "
            "measurement together - "
            + (
                "the biggest possible length combined with the biggest possible width gives the biggest possible area"
                if bound_type == "upper"
                else "the smallest possible length combined with the smallest possible width gives the smallest possible area"
            )
            + ".",
            f"{_fmt_frac(use_l)} × {_fmt_frac(use_w)} = {answer}.",
        ]
        worked_calculation = [
            f"length: {_fmt_frac(lower_l)} to {_fmt_frac(upper_l)} cm; width: {_fmt_frac(lower_w)} to {_fmt_frac(upper_w)} cm",
            f"{_fmt_frac(use_l)} × {_fmt_frac(use_w)}",
            f"= {answer}",
        ]
        prompt = (
            f"A rectangle has length {length} cm and width {width} cm, both measured to the nearest cm. "
            f"Calculate the {bound_type} bound for the area of the rectangle."
        )
    else:
        distance = rng.randint(50, 300)
        time = rng.randint(4, 20)
        lower_d, upper_d = distance - half, distance + half
        lower_t, upper_t = time - half, time + half

        if bound_type == "upper":
            use_d, use_t = upper_d, lower_t
        else:
            use_d, use_t = lower_d, upper_t
        exact = use_d / use_t

        candidates = [lower_d / lower_t, lower_d / upper_t, upper_d / lower_t, upper_d / upper_t]
        expected = max(candidates) if bound_type == "upper" else min(candidates)
        if exact != expected:
            raise ValueError("modelled example bounds_calculation verification failed: speed not the true extremum")

        rounded = _round_1dp(exact)
        if abs(rounded - exact) > Fraction(1, 20):
            raise ValueError("modelled example bounds_calculation verification failed: rounding out of range")

        answer = f"{_fmt_frac(rounded)} km/h (to 1 d.p.)"
        teaching_steps = [
            f"Speed = distance ÷ time, and both the distance ({distance} km) and time ({time} hours) here "
            "have been rounded, so extra care is needed: for a division, the biggest result doesn't come "
            "from combining the biggest possible values of both parts.",
            f"The true distance lies between {_fmt_frac(lower_d)} km and {_fmt_frac(upper_d)} km, and the "
            f"true time lies between {_fmt_frac(lower_t)} hours and {_fmt_frac(upper_t)} hours.",
            "To get the largest possible speed, divide the largest possible distance by the SMALLEST "
            "possible time (dividing by a smaller number gives a bigger answer); to get the smallest "
            "possible speed, do the opposite - divide the smallest distance by the largest time.",
            f"For the {bound_type} bound here, that means dividing the "
            + ("upper bound of distance by the lower bound of time" if bound_type == "upper" else "lower bound of distance by the upper bound of time")
            + f": {_fmt_frac(use_d)} ÷ {_fmt_frac(use_t)} = {_fmt_frac(exact)}, which rounds to "
            f"{_fmt_frac(rounded)} km/h to 1 decimal place.",
        ]
        worked_calculation = [
            f"distance: {_fmt_frac(lower_d)} to {_fmt_frac(upper_d)} km; time: {_fmt_frac(lower_t)} to {_fmt_frac(upper_t)} hours",
            f"{_fmt_frac(use_d)} ÷ {_fmt_frac(use_t)}",
            f"= {_fmt_frac(exact)}",
            f"≈ {_fmt_frac(rounded)} km/h",
        ]
        prompt = (
            f"A car travels {distance} km (to the nearest km) in {time} hours (to the nearest hour). "
            f"Calculate the {bound_type} bound for the average speed of the car, to 1 decimal place."
        )

    return ModelledExample(
        topic_id="bounds_calculation",
        tier=Tier.HIGHER,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
    )


TOPIC_ESTIMATION = TopicDefinition(
    id="estimation_rounding",
    display_name="Estimating Calculations",
    description="Estimate the value of a calculation by rounding each number to 1 significant figure.",
    generate=generate_estimation,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_estimation,
)

TOPIC_ERROR_INTERVAL = TopicDefinition(
    id="error_interval",
    display_name="Error Intervals",
    description="Write the error interval for a value given to a stated degree of accuracy.",
    generate=generate_error_interval,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_error_interval,
)

TOPIC_BOUNDS = TopicDefinition(
    id="bounds_calculation",
    display_name="Bounds of Calculations",
    description="Find the upper or lower bound of a quantity calculated from rounded measurements.",
    generate=generate_bounds_calculation,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_bounds_calculation,
)
