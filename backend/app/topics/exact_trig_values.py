"""Exact trigonometric values (Higher only): recalling sin/cos/tan at the
special angles 0°/30°/45°/60°/90° without a calculator, and using them to find
a missing side of a right-angled triangle in exact (surd) form rather than a
rounded decimal. Unlike trigonometry.py's missing-side/angle topics, these
angles are never a continuous random range - they're always one of the five
special angles, so the values come from a small hardcoded lookup table rather
than a calculator call.
"""

import math
import random

import sympy as sp

from app.core.models import DiagramSpec, ModelledExample, Question, Tier
from app.topics.base import TopicDefinition

SECTION = "geometry"
GROUP = "Trigonometry"

# (ratio, angle) -> (num, den, radicand), meaning value = (num/den) * sqrt(radicand),
# with radicand always already square-free. tan(90) is intentionally excluded
# (undefined).
EXACT_VALUES: dict[tuple[str, int], tuple[int, int, int]] = {
    ("sin", 0): (0, 1, 1), ("sin", 30): (1, 2, 1), ("sin", 45): (1, 2, 2),
    ("sin", 60): (1, 2, 3), ("sin", 90): (1, 1, 1),
    ("cos", 0): (1, 1, 1), ("cos", 30): (1, 2, 3), ("cos", 45): (1, 2, 2),
    ("cos", 60): (1, 2, 1), ("cos", 90): (0, 1, 1),
    ("tan", 0): (0, 1, 1), ("tan", 30): (1, 3, 3), ("tan", 45): (1, 1, 1),
    ("tan", 60): (1, 1, 3),
}

_TRIG_FN = {"sin": sp.sin, "cos": sp.cos, "tan": sp.tan}
_MATH_FN = {"sin": math.sin, "cos": math.cos, "tan": math.tan}
_ROLE_NAME = {"opp": "opposite", "adj": "adjacent", "hyp": "hypotenuse"}

_SIDE_SHAPES = ["hyp_opp", "hyp_adj", "adj_opp", "opp_adj", "adj_hyp", "opp_hyp"]
_SHAPE_RATIO = {
    "hyp_opp": "sin", "hyp_adj": "cos", "adj_opp": "tan",
    "opp_adj": "tan", "adj_hyp": "cos", "opp_hyp": "sin",
}
_SHAPE_ROLES = {
    "hyp_opp": ("hyp", "opp"), "hyp_adj": ("hyp", "adj"), "adj_opp": ("adj", "opp"),
    "opp_adj": ("opp", "adj"), "adj_hyp": ("adj", "hyp"), "opp_hyp": ("opp", "hyp"),
}
_MULTIPLY_SHAPES = {"hyp_opp", "hyp_adj", "adj_opp"}


def _fmt_exact(num: int, den: int, rad: int) -> str:
    g = math.gcd(num, den)
    if g:
        num, den = num // g, den // g
    if num == 0:
        return "0"
    if rad == 1:
        return str(num) if den == 1 else f"{num}/{den}"
    surd = f"√{rad}" if num == 1 else f"{num}√{rad}"
    # A coefficient-1 surd over an integer (e.g. "√3/2") is a single
    # already-clear unit mathtext.py deliberately leaves as flat text (see
    # its "Surd-over-integer gotcha"), but a computed coefficient > 1 (e.g.
    # "5√3/2") is not auto-detected at all and would render as an ugly flat
    # slash - use the explicit \frac{}{} marker for that case.
    if den == 1:
        return surd
    return f"{surd}/{den}" if num == 1 else f"\\frac{{{surd}}}{{{den}}}"


def _verify_exact(ratio: str, angle_deg: int, num: int, den: int, rad: int) -> None:
    """Independent check: re-derive the value from sympy's own trig evaluation,
    rather than re-checking against the same hardcoded table it came from."""
    expected = sp.simplify(_TRIG_FN[ratio](sp.rad(angle_deg)))
    candidate = sp.Rational(num, den) * sp.sqrt(rad)
    if sp.simplify(expected - candidate) != 0:
        raise ValueError(f"exact_trig_values: verification failed for {ratio}({angle_deg}°)")


for (_ratio, _angle), (_num, _den, _rad) in EXACT_VALUES.items():
    _verify_exact(_ratio, _angle, _num, _den, _rad)


def generate_exact_trig_values(tier: Tier, rng: random.Random) -> Question:
    ratio, angle = rng.choice(list(EXACT_VALUES.keys()))
    num, den, rad = EXACT_VALUES[(ratio, angle)]
    _verify_exact(ratio, angle, num, den, rad)
    display = _fmt_exact(num, den, rad)

    steps = [
        "Recall the exact-value triangles: 30°-60°-90° (sides 1, √3, 2) and "
        "45°-45°-90° (sides 1, 1, √2) - no calculator needed for these special angles.",
        f"{ratio}({angle}°) = {display}",
    ]
    return Question(
        topic_id="exact_trig_values",
        tier=Tier.HIGHER,
        prompt=f"Write down the exact value of {ratio}({angle}°).",
        solution_steps=tuple(steps),
        final_answer=display,
        dedup_key=f"exact_trig:{ratio}:{angle}",
    )


def generate_modelled_example_exact_trig_values(tier: Tier, rng: random.Random) -> ModelledExample:
    ratio, angle = rng.choice(list(EXACT_VALUES.keys()))
    num, den, rad = EXACT_VALUES[(ratio, angle)]
    _verify_exact(ratio, angle, num, den, rad)
    display = _fmt_exact(num, den, rad)

    teaching_steps = [
        "Some angles - 0°, 30°, 45°, 60°, 90° - have trig ratios that come out to a clean, "
        "exact fraction or surd rather than a messy decimal, so exam questions expect you to "
        "recall them rather than reach for a calculator.",
        "These all come from two special right-angled triangles: a 30°-60°-90° triangle with "
        "sides 1, √3 and 2 (from splitting an equilateral triangle in half), and a 45°-45°-90° "
        "triangle with sides 1, 1 and √2 (from splitting a square along its diagonal).",
        f"Reading the {ratio} ratio off the {angle}° triangle gives {ratio}({angle}°) = {display} "
        "exactly - not a rounded decimal approximation.",
        "It's worth learning the whole table (sin/cos/tan of 0°, 30°, 45°, 60°, 90°), since "
        "these values also feed straight into 'exact trig values in triangles' questions.",
    ]
    worked_calculation = [
        "Special-angle triangle: 30°-60°-90° (sides 1, √3, 2) or 45°-45°-90° (sides 1, 1, √2)",
        f"{ratio}({angle}°) = {display}",
    ]
    return ModelledExample(
        topic_id="exact_trig_values",
        tier=Tier.HIGHER,
        prompt=f"Write down the exact value of {ratio}({angle}°).",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=display,
    )


def _exact_triangle_value(shape: str, angle: int, given: int) -> tuple[int, int, int]:
    """Return (num, den, rad) for the unknown side as an exact Fraction*sqrt(rad)."""
    ratio = _SHAPE_RATIO[shape]
    num, den, rad = EXACT_VALUES[(ratio, angle)]
    if shape in _MULTIPLY_SHAPES:
        unknown_num, unknown_den = given * num, den
    else:
        # unknown = given / ((num/den)*sqrt(rad)) = given*den*sqrt(rad) / (num*rad),
        # rationalising the denominator.
        unknown_num, unknown_den = given * den, num * rad
    g = math.gcd(unknown_num, unknown_den)
    return unknown_num // g, unknown_den // g, rad


def _verify_triangle_value(shape: str, angle: int, given: int, num: int, den: int, rad: int) -> None:
    """Independent check: compare the hand-derived exact value (as a float)
    against a raw floating-point trig computation of the same triangle - a
    genuinely different computation path (symbolic-table composition vs. raw
    float trig), not "multiply by the same lookup value twice."""
    exact_float = (num / den) * math.sqrt(rad)
    trig_fn = _MATH_FN[_SHAPE_RATIO[shape]]
    rad_angle = math.radians(angle)
    if shape in _MULTIPLY_SHAPES:
        raw_float = given * trig_fn(rad_angle)
    else:
        raw_float = given / trig_fn(rad_angle)
    if abs(exact_float - raw_float) > 1e-9:
        raise ValueError("exact_trig_values_triangles: verification failed")


def generate_exact_trig_values_triangles(tier: Tier, rng: random.Random) -> Question:
    angle = rng.choice([30, 45, 60])
    given = rng.randint(2, 12)
    shape = rng.choice(_SIDE_SHAPES)
    ratio = _SHAPE_RATIO[shape]
    known_role, unknown_role = _SHAPE_ROLES[shape]

    unknown_num, unknown_den, rad = _exact_triangle_value(shape, angle, given)
    _verify_triangle_value(shape, angle, given, unknown_num, unknown_den, rad)
    display = _fmt_exact(unknown_num, unknown_den, rad)

    labels = {"adj": None, "opp": None, "hyp": None}
    labels[known_role] = f"{given} cm"
    labels[unknown_role] = "x cm"

    op = "×" if shape in _MULTIPLY_SHAPES else "÷"
    exact_ratio_str = _fmt_exact(*EXACT_VALUES[(ratio, angle)])
    steps = [
        f"We know the {_ROLE_NAME[known_role]} and want the {_ROLE_NAME[unknown_role]}, so use "
        f"{ratio}({angle}°) = {exact_ratio_str} - its exact value, not a decimal approximation.",
        f"x = {given} {op} {exact_ratio_str} = {display} cm",
    ]
    return Question(
        topic_id="exact_trig_values_triangles",
        tier=Tier.HIGHER,
        prompt="In the right-angled triangle shown, find the exact length of x. Give your answer in surd form where appropriate.",
        solution_steps=tuple(steps),
        final_answer=f"{display} cm",
        dedup_key=f"exact_trig_tri:{shape}:{angle}:{given}",
        diagram=DiagramSpec(
            kind="trig_triangle",
            params={
                "adjacent_label": labels["adj"],
                "opposite_label": labels["opp"],
                "hyp_label": labels["hyp"],
                "angle_label": f"{angle}°",
            },
        ),
    )


def generate_modelled_example_exact_trig_values_triangles(tier: Tier, rng: random.Random) -> ModelledExample:
    angle = rng.choice([30, 45, 60])
    given = rng.randint(2, 12)
    shape = rng.choice(_SIDE_SHAPES)
    ratio = _SHAPE_RATIO[shape]
    known_role, unknown_role = _SHAPE_ROLES[shape]

    unknown_num, unknown_den, rad = _exact_triangle_value(shape, angle, given)
    _verify_triangle_value(shape, angle, given, unknown_num, unknown_den, rad)
    display = _fmt_exact(unknown_num, unknown_den, rad)

    labels = {"adj": None, "opp": None, "hyp": None}
    labels[known_role] = f"{given} cm"
    labels[unknown_role] = "x cm"

    op = "×" if shape in _MULTIPLY_SHAPES else "÷"
    exact_ratio_str = _fmt_exact(*EXACT_VALUES[(ratio, angle)])
    is_multiply = shape in _MULTIPLY_SHAPES

    teaching_steps = [
        f"This triangle uses the special angle {angle}°, so instead of a decimal from a "
        f"calculator, {ratio}({angle}°) has a clean exact value: {exact_ratio_str}.",
        f"SOH CAH TOA tells us {ratio} links the {_ROLE_NAME[known_role]} and the "
        f"{_ROLE_NAME[unknown_role]}.",
        (
            f"Since the {_ROLE_NAME[known_role]} is the one being multiplied in that ratio, "
            f"x = {given} × {exact_ratio_str} directly, with no rearranging needed."
            if is_multiply else
            f"The {_ROLE_NAME[known_role]} isn't in the position the ratio naturally gives us, "
            f"so we rearrange first: x = {given} ÷ {exact_ratio_str}."
        ),
        f"Multiplying/dividing surds keeps the answer exact: x = {display} cm - leave it in "
        "this surd form rather than converting to a decimal, since the question asks for an "
        "exact answer.",
    ]
    worked_calculation = [
        f"x = {given} {op} {exact_ratio_str}",
        f"x = {display} cm",
    ]
    return ModelledExample(
        topic_id="exact_trig_values_triangles",
        tier=Tier.HIGHER,
        prompt="In the right-angled triangle shown, find the exact length of x. Give your answer in surd form where appropriate.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{display} cm",
        diagram=DiagramSpec(
            kind="trig_triangle",
            params={
                "adjacent_label": labels["adj"],
                "opposite_label": labels["opp"],
                "hyp_label": labels["hyp"],
                "angle_label": f"{angle}°",
            },
        ),
    )


TOPIC_EXACT_TRIG_VALUES = TopicDefinition(
    id="exact_trig_values",
    display_name="Exact Trig Values",
    description="Recall the exact value of sin, cos or tan at 0°, 30°, 45°, 60° or 90°, without a calculator.",
    generate=generate_exact_trig_values,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    question_count=len(EXACT_VALUES),
    generate_modelled_example=generate_modelled_example_exact_trig_values,
)

TOPIC_EXACT_TRIG_VALUES_TRIANGLES = TopicDefinition(
    id="exact_trig_values_triangles",
    display_name="Exact Trig Values in Triangles",
    description="Use the exact trig values at 30°, 45° and 60° to find a missing side of a right-angled triangle in surd form.",
    generate=generate_exact_trig_values_triangles,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_exact_trig_values_triangles,
)
