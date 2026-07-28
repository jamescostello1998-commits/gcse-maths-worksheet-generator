"""Geometry Phase 4b (part 1 of 3): bearings, reframing triangle_rules.py's
existing SAS cosine-rule maths as a two-leg bearings word problem. A
standalone reimplementation (not an import) of that SAS branch, matching how
sine_rule/cosine_rule/triangle_area are already independent sibling
functions in triangle_rules.py - the bearing arithmetic that derives the
included angle is genuinely new content, not shared with that file.
"""

import math
import random
from decimal import ROUND_HALF_UP, Decimal

from app.core.models import DiagramSpec, ModelledExample, Question, Tier
from app.topics.base import TopicDefinition

SECTION = "geometry"
GROUP_BEARINGS = "Bearings"


def _fmt_dec(d: Decimal) -> str:
    return format(d, "f")


def _round_sf(value: float, sig_figs: int) -> Decimal:
    d = Decimal(str(value))
    if d == 0:
        return d
    exp = d.adjusted()
    return d.quantize(Decimal(1).scaleb(exp - sig_figs + 1), rounding=ROUND_HALF_UP)


def _fmt_bearing(deg: int) -> str:
    return f"{deg:03d}°"


def _bearings_triangle(bearing_at_A: int, bearing_at_B: int, d1: int, d2: int) -> tuple:
    """Coordinates built directly from the given bearings/distances (north =
    +y), for independent verification - a different route than the
    bearing-subtraction arithmetic shown in the solution steps."""
    def unit_vector(bearing_deg: float) -> tuple:
        rad = math.radians(bearing_deg)
        return (math.sin(rad), math.cos(rad))

    A = (0.0, 0.0)
    ux, uy = unit_vector(bearing_at_A)
    B = (A[0] + d1 * ux, A[1] + d1 * uy)
    vx, vy = unit_vector(bearing_at_B)
    C = (B[0] + d2 * vx, B[1] + d2 * vy)
    return A, B, C


def _verify_bearings(A: tuple, B: tuple, C: tuple, angle_b_interior: int, ac: float, label: str) -> None:
    # Stage 1: recompute the interior angle at B via vector geometry (dot
    # product) and compare to the value the bearings were back-solved from -
    # a different route than that bearing-subtraction arithmetic.
    v1 = (A[0] - B[0], A[1] - B[1])
    v2 = (C[0] - B[0], C[1] - B[1])
    dot = v1[0] * v2[0] + v1[1] * v2[1]
    check_angle = math.degrees(math.acos(dot / (math.hypot(*v1) * math.hypot(*v2))))
    if abs(check_angle - angle_b_interior) > 1e-6:
        raise ValueError(f"{label} verification failed: interior angle mismatch")

    # Stage 2: measure |AC| directly from the coordinates and compare to the
    # cosine-rule result - the same coordinate cross-check idiom cosine_rule
    # itself uses.
    measured_ac = math.hypot(C[0] - A[0], C[1] - A[1])
    if abs(measured_ac - ac) > 1e-6:
        raise ValueError(f"{label} verification failed: coordinate cross-check mismatch")


def _build_bearings_question(rng: random.Random) -> dict:
    """Shared parameter generation + maths for both the real generator and
    the modelled example - the two differ only in how they present it."""
    bearing_at_A = rng.randint(1, 359)
    angle_b_interior = rng.randint(20, 150)
    turn_side = rng.choice([1, -1])
    bearing_at_B = (bearing_at_A + 180 + turn_side * angle_b_interior) % 360
    d1, d2 = rng.randint(5, 30), rng.randint(5, 30)

    A, B, C = _bearings_triangle(bearing_at_A, bearing_at_B, d1, d2)

    rad_B = math.radians(angle_b_interior)
    ac_sq = d1 * d1 + d2 * d2 - 2 * d1 * d2 * math.cos(rad_B)
    ac = math.sqrt(ac_sq)

    _verify_bearings(A, B, C, angle_b_interior, ac, "bearings_cosine_rule")

    rounded = _round_sf(ac, 3)
    back_bearing = (bearing_at_A + 180) % 360
    ac_sq_str = _fmt_dec(_round_sf(ac_sq, 4))

    return {
        "bearing_at_A": bearing_at_A,
        "bearing_at_B": bearing_at_B,
        "back_bearing": back_bearing,
        "angle_b_interior": angle_b_interior,
        "d1": d1,
        "d2": d2,
        "ac_sq_str": ac_sq_str,
        "rounded": rounded,
    }


def _bearings_prompt(v: dict) -> str:
    return (
        f"A ship sails from port A on a bearing of {_fmt_bearing(v['bearing_at_A'])} for {v['d1']} km "
        f"to point B. It then changes course and sails on a bearing of {_fmt_bearing(v['bearing_at_B'])} "
        f"for {v['d2']} km to point C. Find the direct distance from A to C, correct to 3 significant figures."
    )


def generate_bearings(tier: Tier, rng: random.Random) -> Question:
    v = _build_bearings_question(rng)
    steps = [
        f"The back bearing of A from B is {_fmt_bearing(v['bearing_at_A'])} + 180° = "
        f"{_fmt_bearing(v['back_bearing'])}.",
        f"Angle ABC is the difference between this back bearing and the bearing of C from B: "
        f"angle ABC = {v['angle_b_interior']}°.",
        "Use the cosine rule: AC² = AB² + BC² - 2×AB×BC×cos(ABC)",
        f"AC² = {v['d1']}² + {v['d2']}² - 2×{v['d1']}×{v['d2']}×"
        f"cos({v['angle_b_interior']}°) = {v['ac_sq_str']}",
        f"AC = √{v['ac_sq_str']} = {_fmt_dec(v['rounded'])} km (3 s.f.)",
    ]
    diagram = DiagramSpec(
        kind="bearings",
        params={
            "labels": ("A", "B", "C"),
            "bearing_at_A": v["bearing_at_A"],
            "bearing_at_B": v["bearing_at_B"],
            "leg1_label": f"{v['d1']} km",
            "leg2_label": f"{v['d2']} km",
            "unknown_label": "x km",
        },
    )
    return Question(
        topic_id="bearings_cosine_rule",
        tier=Tier.HIGHER,
        prompt=_bearings_prompt(v),
        solution_steps=tuple(steps),
        final_answer=f"{_fmt_dec(v['rounded'])} km",
        dedup_key=f"bearings_cosine_rule:{v['bearing_at_A']}:{v['bearing_at_B']}:{v['d1']}:{v['d2']}",
        diagram=diagram,
    )


def generate_modelled_example_bearings(tier: Tier, rng: random.Random) -> ModelledExample:
    v = _build_bearings_question(rng)
    teaching_steps = [
        "Bearings problems like this one are really a cosine-rule question in disguise - the two legs of "
        "the journey are two sides of a triangle, and the angle between them (the 'included' angle) has to "
        "be worked out from the bearings before the cosine rule can be used at all.",
        f"Find the back bearing of A from B by adding 180° to the outward bearing: "
        f"{_fmt_bearing(v['bearing_at_A'])} + 180° = {_fmt_bearing(v['back_bearing'])}. This gives the "
        "direction you would look in from B to see back the way you came.",
        f"The angle at B, between the path back to A and the path onward to C, is the difference between "
        f"this back bearing and the bearing to C: angle ABC = {v['angle_b_interior']}°.",
        f"Now it is an ordinary SAS cosine-rule triangle: two sides AB = {v['d1']} km, BC = {v['d2']} km, "
        f"and the included angle {v['angle_b_interior']}° between them. Substitute into "
        f"AC² = AB² + BC² - 2×AB×BC×cos(ABC), giving AC² = "
        f"{v['d1']}² + {v['d2']}² - 2×{v['d1']}×{v['d2']}×cos({v['angle_b_interior']}°) "
        f"= {v['ac_sq_str']}.",
        f"Take the square root and round to 3 significant figures: AC = √{v['ac_sq_str']} = "
        f"{_fmt_dec(v['rounded'])} km.",
    ]
    worked_calculation = [
        f"Back bearing at B = {_fmt_bearing(v['bearing_at_A'])} + 180° = {_fmt_bearing(v['back_bearing'])}",
        f"Angle ABC = {v['angle_b_interior']}°",
        "AC² = AB² + BC² - 2×AB×BC×cos(ABC)",
        f"AC² = {v['d1']}² + {v['d2']}² - 2×{v['d1']}×{v['d2']}×"
        f"cos({v['angle_b_interior']}°) = {v['ac_sq_str']}",
        f"AC = √{v['ac_sq_str']} = {_fmt_dec(v['rounded'])} km",
    ]
    diagram = DiagramSpec(
        kind="bearings",
        params={
            "labels": ("A", "B", "C"),
            "bearing_at_A": v["bearing_at_A"],
            "bearing_at_B": v["bearing_at_B"],
            "leg1_label": f"{v['d1']} km",
            "leg2_label": f"{v['d2']} km",
            "unknown_label": f"{_fmt_dec(v['rounded'])} km",
        },
    )
    return ModelledExample(
        topic_id="bearings_cosine_rule",
        tier=Tier.HIGHER,
        prompt=_bearings_prompt(v),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{_fmt_dec(v['rounded'])} km",
        diagram=diagram,
    )


TOPIC_BEARINGS_COSINE_RULE = TopicDefinition(
    id="bearings_cosine_rule",
    display_name="Bearings",
    description=(
        "Use the cosine rule to find the direct distance between two points, given bearings and "
        "distances for a two-leg journey."
    ),
    generate=generate_bearings,
    section=SECTION,
    group=GROUP_BEARINGS,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_bearings,
)
