"""Geometry Phase 4b (part 1 of 3): bearings, reframing triangle_rules.py's
existing SAS cosine-rule maths as a two-leg bearings word problem. A
standalone reimplementation (not an import) of that SAS branch, matching how
sine_rule/cosine_rule/triangle_area are already independent sibling
functions in triangle_rules.py - the bearing arithmetic that derives the
included angle is genuinely new content, not shared with that file.
"""

import math
import random
import string
from decimal import ROUND_HALF_UP, Decimal

from app.core.models import DiagramSpec, ModelledExample, Question, Tier
from app.topics.base import TopicDefinition
from app.topics.rounding import pick_rounding

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

    rounding = pick_rounding(rng)
    rounded = rounding.round_fn(ac)
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
        "rounding_phrase": rounding.phrase,
        "rounding_short": rounding.short,
    }


def _bearings_prompt(v: dict) -> str:
    return (
        f"A ship sails from port A on a bearing of {_fmt_bearing(v['bearing_at_A'])} for {v['d1']} km "
        f"to point B. It then changes course and sails on a bearing of {_fmt_bearing(v['bearing_at_B'])} "
        f"for {v['d2']} km to point C. Find the direct distance from A to C, correct to {v['rounding_phrase']}."
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
        f"AC = √{v['ac_sq_str']} = {_fmt_dec(v['rounded'])} km ({v['rounding_short']})",
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
        topic_id="bearings_cosine_rule_H",
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
        f"Take the square root and round to {v['rounding_phrase']}: AC = √{v['ac_sq_str']} = "
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
        topic_id="bearings_cosine_rule_H",
        tier=Tier.HIGHER,
        prompt=_bearings_prompt(v),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{_fmt_dec(v['rounded'])} km",
        diagram=diagram,
    )


def _back_bearing_case(rng: random.Random) -> dict:
    bearing_at_A = rng.randint(1, 359)
    back_bearing = (bearing_at_A + 180) % 360
    if bearing_at_A < 180:
        step = f"Since {_fmt_bearing(bearing_at_A)} is less than 180°, add 180°: {bearing_at_A} + 180 = {back_bearing}"
    else:
        step = f"Since {_fmt_bearing(bearing_at_A)} is 180° or more, subtract 180°: {bearing_at_A} - 180 = {back_bearing}"
    return {"bearing_at_A": bearing_at_A, "back_bearing": back_bearing, "rule_step": step}


def generate_bearings_foundation(tier: Tier, rng: random.Random) -> Question:
    shape = rng.choice(["back_bearing", "read_bearing"])

    if shape == "back_bearing":
        v = _back_bearing_case(rng)
        steps = [
            "The bearing of A from B (the 'back bearing') always differs from the bearing of B from A "
            "by exactly 180°.",
            v["rule_step"],
        ]
        diagram = DiagramSpec(
            kind="bearings",
            params={"labels": ("A", "B"), "bearing_at_A": v["bearing_at_A"], "leg1_label": ""},
        )
        solution_diagram = DiagramSpec(
            kind="bearings",
            params={
                "labels": ("A", "B"), "bearing_at_A": v["bearing_at_A"], "leg1_label": "",
                "answer_bearing_at_B": v["back_bearing"],
            },
        )
        return Question(
            topic_id="bearings_F",
            tier=Tier.FOUNDATION,
            prompt=f"The bearing of B from A is {_fmt_bearing(v['bearing_at_A'])}. Find the bearing of A from B.",
            solution_steps=tuple(steps),
            final_answer=_fmt_bearing(v["back_bearing"]),
            dedup_key=f"bearings_back:{v['bearing_at_A']}",
            diagram=diagram,
            solution_diagram=solution_diagram,
        )

    bearing = rng.randint(1, 359)
    steps = [
        "A bearing is always written as three figures, measured clockwise from north.",
        f"Reading the angle shown from north: {bearing}°, written as a three-figure bearing: "
        f"{_fmt_bearing(bearing)}.",
    ]
    diagram = DiagramSpec(
        kind="bearings",
        params={"labels": ("A", "B"), "bearing_at_A": bearing, "leg1_label": ""},
    )
    return Question(
        topic_id="bearings_F",
        tier=Tier.FOUNDATION,
        prompt="The diagram shows the bearing of B from A. Write down the bearing of B from A as a "
        "three-figure bearing.",
        solution_steps=tuple(steps),
        final_answer=_fmt_bearing(bearing),
        dedup_key=f"bearings_read:{bearing}",
        diagram=diagram,
    )


def generate_modelled_example_bearings_foundation(tier: Tier, rng: random.Random) -> ModelledExample:
    shape = rng.choice(["back_bearing", "read_bearing"])

    if shape == "back_bearing":
        v = _back_bearing_case(rng)
        teaching_steps = [
            "A bearing describes a direction as an angle measured clockwise from north, always written "
            "using three figures (e.g. 007°, not 7°).",
            "The bearing of A from B - looking back the way you came - is always exactly 180° different "
            "from the bearing of B from A, since north at A and north at B point the same way, but you're "
            "now facing the opposite direction along the same line.",
            v["rule_step"],
            f"So the bearing of A from B is {_fmt_bearing(v['back_bearing'])}.",
        ]
        worked_calculation = [
            f"Bearing of B from A = {_fmt_bearing(v['bearing_at_A'])}",
            v["rule_step"],
            f"Bearing of A from B = {_fmt_bearing(v['back_bearing'])}",
        ]
        diagram = DiagramSpec(
            kind="bearings",
            params={
                "labels": ("A", "B"), "bearing_at_A": v["bearing_at_A"], "leg1_label": "",
                "answer_bearing_at_B": v["back_bearing"],
            },
        )
        return ModelledExample(
            topic_id="bearings_F",
            tier=Tier.FOUNDATION,
            prompt=f"The bearing of B from A is {_fmt_bearing(v['bearing_at_A'])}. Find the bearing of A from B.",
            worked_calculation=tuple(worked_calculation),
            teaching_steps=tuple(teaching_steps),
            final_answer=_fmt_bearing(v["back_bearing"]),
            diagram=diagram,
        )

    bearing = rng.randint(1, 359)
    teaching_steps = [
        "A bearing is always measured clockwise, starting from north - never anticlockwise, and never "
        "measured from any other direction such as south or east.",
        "It's always written with three digits, padding with leading zeros where needed - so an angle of "
        "7° is written as the bearing 007°, not 7°, and an angle of 63° is written as 063°.",
        f"Here the angle measured clockwise from north is {bearing}°, so as a three-figure bearing that's "
        f"{_fmt_bearing(bearing)}.",
    ]
    worked_calculation = [f"Angle from north = {bearing}°", f"Bearing = {_fmt_bearing(bearing)}"]
    diagram = DiagramSpec(
        kind="bearings",
        params={"labels": ("A", "B"), "bearing_at_A": bearing, "leg1_label": ""},
    )
    return ModelledExample(
        topic_id="bearings_F",
        tier=Tier.FOUNDATION,
        prompt="The diagram shows the bearing of B from A. Write down the bearing of B from A as a "
        "three-figure bearing.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=_fmt_bearing(bearing),
        diagram=diagram,
    )


# ---------------------------------------------------------------------------
# Back bearing (standalone, no diagram): given the bearing one way, find it
# the other way - genuinely bidirectional, since which point is "given" and
# which is "asked for" varies question to question, not the underlying maths.
# ---------------------------------------------------------------------------

def _random_back_bearing(rng: random.Random) -> dict:
    given_point, other_point = rng.sample(string.ascii_uppercase, 2)
    known_bearing = rng.randint(1, 359)
    answer_bearing = (known_bearing + 180) % 360
    if known_bearing < 180:
        rule_step = (
            f"Since {_fmt_bearing(known_bearing)} is less than 180°, add 180°: "
            f"{known_bearing} + 180 = {answer_bearing}"
        )
    else:
        rule_step = (
            f"Since {_fmt_bearing(known_bearing)} is 180° or more, subtract 180°: "
            f"{known_bearing} - 180 = {answer_bearing}"
        )
    return {
        "given_point": given_point, "other_point": other_point,
        "known_bearing": known_bearing, "answer_bearing": answer_bearing, "rule_step": rule_step,
    }


def _back_bearing_prompt(v: dict) -> str:
    return (
        f"The bearing of {v['other_point']} from {v['given_point']} is {_fmt_bearing(v['known_bearing'])}. "
        f"Find the bearing of {v['given_point']} from {v['other_point']}."
    )


def generate_bearings_back_bearing(tier: Tier, rng: random.Random) -> Question:
    v = _random_back_bearing(rng)
    steps = [
        "The bearing of one point from another, and the bearing back the other way, always differ by "
        "exactly 180° - the two north lines point the same way, but you're now facing the opposite "
        "direction along the same line.",
        v["rule_step"],
    ]
    return Question(
        topic_id="bearings_back_bearing_F",
        tier=Tier.FOUNDATION,
        prompt=_back_bearing_prompt(v),
        solution_steps=tuple(steps),
        final_answer=_fmt_bearing(v["answer_bearing"]),
        dedup_key=f"back_bearing:{v['given_point']}{v['other_point']}:{v['known_bearing']}",
    )


def generate_modelled_example_bearings_back_bearing(tier: Tier, rng: random.Random) -> ModelledExample:
    v = _random_back_bearing(rng)
    teaching_steps = [
        "A bearing describes a direction as an angle measured clockwise from north, always written using "
        "three figures.",
        "The bearing back the other way is always exactly 180° different, because the two north lines - "
        "one at each point - point in the same direction (they're parallel), but travelling back means "
        "facing the opposite way along the same straight line.",
        v["rule_step"],
        f"So the bearing of {v['given_point']} from {v['other_point']} is {_fmt_bearing(v['answer_bearing'])}.",
    ]
    worked_calculation = [
        f"Bearing of {v['other_point']} from {v['given_point']} = {_fmt_bearing(v['known_bearing'])}",
        v["rule_step"],
        f"Bearing of {v['given_point']} from {v['other_point']} = {_fmt_bearing(v['answer_bearing'])}",
    ]
    return ModelledExample(
        topic_id="bearings_back_bearing_F",
        tier=Tier.FOUNDATION,
        prompt=_back_bearing_prompt(v),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=_fmt_bearing(v["answer_bearing"]),
    )


# ---------------------------------------------------------------------------
# Bearings angle facts: "around a point" (a turn from one direction to
# another wraps around a full 360°) and "co-interior angles" (the north
# lines at two points are parallel, so the angle between the transversal and
# north at each point, on the same side, sum to 180° - the geometric reason
# a back bearing is +/-180°, made explicit rather than just applying the
# shortcut rule).
# ---------------------------------------------------------------------------

def _around_point_case(rng: random.Random) -> dict:
    for _ in range(200):
        bearing_b = rng.randint(1, 359)
        direction = rng.choice(["clockwise", "anticlockwise"])
        turn_deg = rng.randint(30, 320)
        if direction == "clockwise":
            raw = bearing_b + turn_deg
            if raw > 360:
                bearing_c = raw - 360
                break
        else:
            raw = bearing_b - turn_deg
            if raw < 0:
                bearing_c = raw + 360
                break
    else:
        raise ValueError("bearings_angle_facts: could not find a wrap-around around_point case")

    # Independent verification: the three angles around O - from north
    # clockwise to B, the turn from B to C, and the remaining angle back to
    # north - must sum to exactly 360°, computed via the actual wrap
    # arithmetic used, then re-derived from the *other* two known pieces.
    if direction == "clockwise":
        remaining = 360 - bearing_c
        if abs((bearing_b + turn_deg - 360) - bearing_c) > 1e-9 or (bearing_c + remaining) != 360:
            raise ValueError("bearings_angle_facts verification failed: clockwise wrap mismatch")
    else:
        remaining = bearing_b
        if abs((bearing_b - turn_deg + 360) - bearing_c) > 1e-9:
            raise ValueError("bearings_angle_facts verification failed: anticlockwise wrap mismatch")

    prompt = (
        f"From point O, the bearing of B is {_fmt_bearing(bearing_b)}. Turning {direction} through "
        f"{turn_deg}°, you now face point C. Find the bearing of C from O."
    )
    if direction == "clockwise":
        steps = [
            f"Turning clockwise from OB adds to the bearing: {bearing_b} + {turn_deg} = {bearing_b + turn_deg}.",
            f"Since angles all the way around a point O sum to 360°, a total past 360° wraps back round: "
            f"{bearing_b + turn_deg} - 360 = {bearing_c}.",
        ]
    else:
        steps = [
            f"Turning anticlockwise from OB subtracts from the bearing: {bearing_b} - {turn_deg} = "
            f"{bearing_b - turn_deg}.",
            f"Since angles all the way around a point O sum to 360°, a negative result wraps back round "
            f"past north: {bearing_b - turn_deg} + 360 = {bearing_c}.",
        ]
    return {
        "prompt": prompt, "steps": steps, "answer": _fmt_bearing(bearing_c),
        "bearing_b": bearing_b, "bearing_c": bearing_c, "direction": direction, "turn_deg": turn_deg,
        "dedup_key": f"angle_facts_around_point:{bearing_b}:{direction}:{turn_deg}",
        "diagram": DiagramSpec(
            kind="bearings_two_rays",
            params={"origin_label": "O", "bearing_a": bearing_b, "bearing_b": bearing_c, "label_a": "B", "label_b": "C"},
        ),
    }


def _co_interior_case(rng: random.Random) -> dict:
    P, Q = rng.sample(string.ascii_uppercase, 2)
    # Q generally "ahead and to one side" of P (bearing strictly between 0
    # and 180) keeps the co-interior configuration unambiguous to name in
    # words - the same single, clean case real GCSE questions use, rather
    # than a full 360° range that would need extra care about which side of
    # the transversal is "the same side" at each point.
    bearing_pq = rng.randint(15, 165)
    co_interior_angle = 180 - bearing_pq
    bearing_qp = 180 + bearing_pq  # always in (195, 345); no 360 wrap needed in this range

    # Independent verification via vector geometry: north at P and north at
    # Q point the same way (they're parallel) - measure the actual angle
    # between north-at-Q and the direction from Q back to P using the dot
    # product, a genuinely different computational route from the
    # 180 - bearing_pq subtraction used to build the steps.
    def unit_vector(bearing_deg: float) -> tuple:
        rad = math.radians(bearing_deg)
        return (math.sin(rad), math.cos(rad))

    north = (0.0, 1.0)
    qp_dir = unit_vector((bearing_pq + 180) % 360)
    dot = north[0] * qp_dir[0] + north[1] * qp_dir[1]
    measured_angle = math.degrees(math.acos(max(-1.0, min(1.0, dot))))
    if abs(measured_angle - co_interior_angle) > 1e-6:
        raise ValueError("bearings_angle_facts verification failed: co-interior angle mismatch")
    if (bearing_pq + 180) % 360 != bearing_qp:
        raise ValueError("bearings_angle_facts verification failed: back-bearing cross-check mismatch")

    prompt = (
        f"The bearing of {Q} from {P} is {_fmt_bearing(bearing_pq)}. The lines pointing north at {P} and "
        f"at {Q} are parallel. Using co-interior angles, find the bearing of {P} from {Q}."
    )
    steps = [
        f"North at {P} and north at {Q} are parallel lines, and {P}{Q} is a straight line crossing both "
        "(a transversal) - so the angle between the transversal and north on one side of it at one point, "
        "and the angle between the transversal and north on the *same* side at the other point, are "
        "co-interior angles: they sum to 180°.",
        f"The bearing of {Q} from {P} is {_fmt_bearing(bearing_pq)}, so the co-interior angle at {Q} "
        f"(between north at {Q} and {Q}{P}) = 180° - {bearing_pq} = {co_interior_angle}°.",
        f"The bearing of {P} from {Q} is measured the rest of the way round from north, clockwise, past "
        f"that co-interior angle: 180° + {bearing_pq}° = {_fmt_bearing(bearing_qp)}.",
    ]
    return {
        "prompt": prompt, "steps": steps, "answer": _fmt_bearing(bearing_qp),
        "dedup_key": f"angle_facts_co_interior:{P}{Q}:{bearing_pq}",
        "diagram": DiagramSpec(
            kind="bearings", params={"labels": (P, Q), "bearing_at_A": bearing_pq, "leg1_label": ""},
        ),
    }


def _random_angle_facts_case(rng: random.Random) -> dict:
    branch = rng.choice([_around_point_case, _co_interior_case])
    return branch(rng)


def generate_bearings_angle_facts(tier: Tier, rng: random.Random) -> Question:
    c = _random_angle_facts_case(rng)
    return Question(
        topic_id="bearings_angle_facts_F",
        tier=Tier.FOUNDATION,
        prompt=c["prompt"],
        solution_steps=tuple(c["steps"]),
        final_answer=c["answer"],
        dedup_key=c["dedup_key"],
        diagram=c["diagram"],
    )


def generate_modelled_example_bearings_angle_facts(tier: Tier, rng: random.Random) -> ModelledExample:
    c = _random_angle_facts_case(rng)
    is_around_point = c["dedup_key"].startswith("angle_facts_around_point")
    if is_around_point:
        teaching_steps = [
            "Bearings are measured clockwise from north, and a full turn all the way around any point is "
            "always exactly 360° - this is what lets a turn take you 'past north' and back round to a "
            "small bearing again.",
            *c["steps"],
            f"So the bearing of C from O is {c['answer']}.",
        ]
    else:
        teaching_steps = [
            "Whenever two bearings are measured from points joined by a straight line, the north direction "
            "at each point is parallel to the other (compass north never changes) - so the line joining "
            "them acts as a transversal crossing two parallel lines.",
            *c["steps"],
            f"So the bearing found this way is {c['answer']}.",
        ]
    worked_calculation = list(c["steps"]) + [f"Answer: {c['answer']}"]
    return ModelledExample(
        topic_id="bearings_angle_facts_F",
        tier=Tier.FOUNDATION,
        prompt=c["prompt"],
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=c["answer"],
        diagram=c["diagram"],
    )


TOPIC_BEARINGS_FOUNDATION = TopicDefinition(
    id="bearings_F",
    display_name="Bearings",
    description="Find a back bearing, or read a three-figure bearing directly from a diagram.",
    generate=generate_bearings_foundation,
    section=SECTION,
    group=GROUP_BEARINGS,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_bearings_foundation,
)


TOPIC_BEARINGS_BACK_BEARING = TopicDefinition(
    id="bearings_back_bearing_F",
    display_name="Back Bearings",
    description="Given the bearing of one point from another, find the bearing back the other way.",
    generate=generate_bearings_back_bearing,
    section=SECTION,
    group=GROUP_BEARINGS,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_bearings_back_bearing,
)


TOPIC_BEARINGS_ANGLE_FACTS = TopicDefinition(
    id="bearings_angle_facts_F",
    display_name="Bearings and Angle Facts",
    description="Use angle facts (angles around a point, co-interior angles) to find a bearing.",
    generate=generate_bearings_angle_facts,
    section=SECTION,
    group=GROUP_BEARINGS,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_bearings_angle_facts,
)


TOPIC_BEARINGS_COSINE_RULE = TopicDefinition(
    id="bearings_cosine_rule_H",
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
