import math
import random
from decimal import ROUND_HALF_UP, Decimal

from app.core.models import DiagramSpec, Question, Tier
from app.topics.base import TopicDefinition

SECTION = "geometry"
GROUP_SINE = "Sine Rule"
GROUP_COSINE = "Cosine Rule"
GROUP_AREA = "Area of a Triangle"


def _fmt_dec(d: Decimal) -> str:
    return format(d, "f")


def _round_sf(value: float, sig_figs: int) -> Decimal:
    d = Decimal(str(value))
    if d == 0:
        return d
    exp = d.adjusted()
    return d.quantize(Decimal(1).scaleb(exp - sig_figs + 1), rounding=ROUND_HALF_UP)


def _round_dp(value: float, dp: int) -> Decimal:
    return Decimal(str(value)).quantize(Decimal(1).scaleb(-dp), rounding=ROUND_HALF_UP)


def _dist(p, q) -> float:
    return math.hypot(p[0] - q[0], p[1] - q[1])


def generate_sine_rule(tier: Tier, rng: random.Random) -> Question:
    shape = rng.choice(["side", "angle"])

    for _ in range(50):
        angle_A = rng.randint(30, 110)
        b_upper = 89 if shape == "angle" else min(129, 165 - angle_A)
        angle_B = rng.randint(20, max(20, min(b_upper, 165 - angle_A)))
        angle_C = 180 - angle_A - angle_B
        if angle_C < 10:
            continue
        side_a = rng.randint(5, 30)

        rad_A, rad_B = math.radians(angle_A), math.radians(angle_B)
        side_b = side_a * math.sin(rad_B) / math.sin(rad_A)
        side_c = side_a * math.sin(math.radians(angle_C)) / math.sin(rad_A)

        # Independent verification via coordinate geometry: build the triangle from
        # the two angles and side a directly, then measure side a back out with the
        # distance formula - a different computation path than the sine-rule algebra.
        A, B = (0.0, 0.0), (side_c, 0.0)
        C = (side_b * math.cos(rad_A), side_b * math.sin(rad_A))
        if abs(_dist(B, C) - side_a) > 1e-6:
            raise ValueError("sine_rule verification failed: coordinate cross-check mismatch")

        b_str = _fmt_dec(_round_sf(side_b, 3))

        if shape == "side":
            steps = [
                "Use the sine rule: a / sin(A) = b / sin(B)",
                f"b = ({side_a} × sin({angle_B}°)) ÷ sin({angle_A}°) = {b_str} cm (3 s.f.)",
            ]
            prompt = (
                f"In triangle ABC, angle A = {angle_A}°, angle B = {angle_B}°, and side a = {side_a} cm. "
                "Find the length of side b, correct to 3 significant figures."
            )
            answer = f"{b_str} cm"
            dedup_key = f"sine_rule_side:{angle_A}:{angle_B}:{side_a}"
            diagram = DiagramSpec(
                kind="general_triangle",
                params={
                    "side_a_label": f"{side_a} cm", "side_b_label": "x cm", "side_c_label": None,
                    "angle_A_label": f"{angle_A}°", "angle_B_label": f"{angle_B}°", "angle_C_label": None,
                },
            )
        else:
            # Verify that solving from the *rounded* side b (what a student would
            # actually use) is still close to angle_B - not an exact match (3 s.f.
            # rounding of b shifts the recovered angle slightly, same as in any real
            # mark scheme), but it guards against the ratio landing outside sin's
            # domain or wildly off. Reroll the whole triangle if it doesn't hold.
            ratio = float(b_str) * math.sin(rad_A) / side_a
            if not (-1 <= ratio <= 1):
                continue
            recomputed_B = math.degrees(math.asin(ratio))
            if abs(recomputed_B - angle_B) > 0.5:
                continue

            steps = [
                "Use the sine rule: sin(B) / b = sin(A) / a",
                f"sin(B) = ({b_str} × sin({angle_A}°)) ÷ {side_a}",
                f"B = {angle_B}.0° (1 d.p.)",
            ]
            prompt = (
                f"In triangle ABC, angle A = {angle_A}°, side a = {side_a} cm, and side b = {b_str} cm. "
                "Find angle B, correct to 1 decimal place."
            )
            answer = f"{angle_B}.0°"
            dedup_key = f"sine_rule_angle:{angle_A}:{side_a}:{b_str}"
            diagram = DiagramSpec(
                kind="general_triangle",
                params={
                    "side_a_label": f"{side_a} cm", "side_b_label": f"{b_str} cm", "side_c_label": None,
                    "angle_A_label": f"{angle_A}°", "angle_B_label": "x°", "angle_C_label": None,
                },
            )

        return Question(
            topic_id="sine_rule",
            tier=Tier.HIGHER,
            prompt=prompt,
            solution_steps=tuple(steps),
            final_answer=answer,
            dedup_key=dedup_key,
            diagram=diagram,
        )

    raise ValueError("sine_rule could not find valid parameters after 50 attempts")


def generate_cosine_rule(tier: Tier, rng: random.Random) -> Question:
    shape = rng.choice(["side", "angle"])

    if shape == "side":
        b, c = rng.randint(5, 30), rng.randint(5, 30)
        angle_A = rng.randint(20, 150)
        rad_A = math.radians(angle_A)
        a_sq = b * b + c * c - 2 * b * c * math.cos(rad_A)
        side_a = math.sqrt(a_sq)

        # Independent verification via coordinate geometry: place the known angle A
        # between the two known sides, then measure side a with the distance formula.
        B, C = (c, 0.0), (b * math.cos(rad_A), b * math.sin(rad_A))
        if abs(_dist(B, C) - side_a) > 1e-6:
            raise ValueError("cosine_rule verification failed: coordinate cross-check mismatch")

        rounded = _round_sf(side_a, 3)
        a_sq_str = _fmt_dec(_round_sf(a_sq, 4))
        steps = [
            "Use the cosine rule: a² = b² + c² - 2bc cos(A)",
            f"a² = {b}² + {c}² - 2×{b}×{c}×cos({angle_A}°) = {a_sq_str}",
            f"a = √{a_sq_str} = {_fmt_dec(rounded)} cm (3 s.f.)",
        ]
        prompt = (
            f"In triangle ABC, side b = {b} cm, side c = {c} cm, and the angle between them, "
            f"angle A = {angle_A}°. Find the length of side a, correct to 3 significant figures."
        )
        answer = f"{_fmt_dec(rounded)} cm"
        dedup_key = f"cosine_rule_side:{b}:{c}:{angle_A}"
        diagram = DiagramSpec(
            kind="general_triangle",
            params={
                "side_a_label": "x cm", "side_b_label": f"{b} cm", "side_c_label": f"{c} cm",
                "angle_A_label": f"{angle_A}°", "angle_B_label": None, "angle_C_label": None,
            },
        )
    else:
        for _ in range(200):
            a, b, c = rng.randint(5, 25), rng.randint(5, 25), rng.randint(5, 25)
            if a + b > c and a + c > b and b + c > a:
                break
        else:
            raise ValueError("cosine_rule could not find a valid triangle")

        cos_A = (b * b + c * c - a * a) / (2 * b * c)
        if not (-1 <= cos_A <= 1):
            raise ValueError("cosine_rule produced an invalid cosine value")
        angle_A = math.degrees(math.acos(cos_A))

        # Independent verification via coordinate geometry (SSS construction): build
        # the triangle from the three side lengths alone, then measure angle A with
        # the dot-product formula - a different computation path than cos(A) above.
        B, C = (0.0, 0.0), (a, 0.0)
        ax = (a * a + c * c - b * b) / (2 * a)
        ay_sq = c * c - ax * ax
        if ay_sq < 0:
            raise ValueError("cosine_rule verification failed: degenerate triangle")
        A = (ax, math.sqrt(ay_sq))
        v1, v2 = (B[0] - A[0], B[1] - A[1]), (C[0] - A[0], C[1] - A[1])
        dot = v1[0] * v2[0] + v1[1] * v2[1]
        check_angle = math.degrees(math.acos(dot / (math.hypot(*v1) * math.hypot(*v2))))
        if abs(check_angle - angle_A) > 1e-6:
            raise ValueError("cosine_rule verification failed: coordinate cross-check mismatch")

        rounded = _round_dp(angle_A, 1)
        cos_a_str = _fmt_dec(_round_sf(cos_A, 4))
        steps = [
            "Use the cosine rule: cos(A) = (b² + c² - a²) ÷ (2bc)",
            f"cos(A) = ({b}² + {c}² - {a}²) ÷ (2×{b}×{c}) = {cos_a_str}",
            f"A = cos⁻¹({cos_a_str}) = {_fmt_dec(rounded)}° (1 d.p.)",
        ]
        prompt = (
            f"In triangle ABC, side a = {a} cm, side b = {b} cm, and side c = {c} cm. "
            "Find angle A, correct to 1 decimal place."
        )
        answer = f"{_fmt_dec(rounded)}°"
        dedup_key = f"cosine_rule_angle:{a}:{b}:{c}"
        diagram = DiagramSpec(
            kind="general_triangle",
            params={
                "side_a_label": f"{a} cm", "side_b_label": f"{b} cm", "side_c_label": f"{c} cm",
                "angle_A_label": "x°", "angle_B_label": None, "angle_C_label": None,
            },
        )

    return Question(
        topic_id="cosine_rule",
        tier=Tier.HIGHER,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=dedup_key,
        diagram=diagram,
    )


def generate_triangle_area(tier: Tier, rng: random.Random) -> Question:
    a, b = rng.randint(5, 25), rng.randint(5, 25)
    angle_C = rng.randint(20, 160)
    rad_C = math.radians(angle_C)
    area = 0.5 * a * b * math.sin(rad_C)

    # Independent verification via the shoelace formula: place the shared vertex C at
    # the origin with sides a and b (CB and CA) at the given angle, then compute the
    # triangle's area from the three coordinates directly.
    C0, B, A = (0.0, 0.0), (a, 0.0), (b * math.cos(rad_C), b * math.sin(rad_C))
    shoelace_area = abs(C0[0] * (B[1] - A[1]) + B[0] * (A[1] - C0[1]) + A[0] * (C0[1] - B[1])) / 2
    if abs(shoelace_area - area) > 1e-6:
        raise ValueError("triangle_area verification failed: shoelace cross-check mismatch")

    rounded = _round_sf(area, 3)
    steps = [
        "Use Area = (1/2) × a × b × sin(C)",
        f"Area = 0.5 × {a} × {b} × sin({angle_C}°) = {_fmt_dec(rounded)} cm² (3 s.f.)",
    ]
    return Question(
        topic_id="triangle_area_sine_rule",
        tier=Tier.HIGHER,
        prompt=(
            f"Triangle ABC has side a = {a} cm, side b = {b} cm, and the angle between them, "
            f"angle C = {angle_C}°. Find the area of the triangle, correct to 3 significant figures."
        ),
        solution_steps=tuple(steps),
        final_answer=f"{_fmt_dec(rounded)} cm²",
        dedup_key=f"triangle_area:{a}:{b}:{angle_C}",
        diagram=DiagramSpec(
            kind="general_triangle",
            params={
                "side_a_label": f"{a} cm", "side_b_label": f"{b} cm", "side_c_label": None,
                "angle_A_label": None, "angle_B_label": None, "angle_C_label": f"{angle_C}°",
            },
        ),
    )


TOPIC_SINE_RULE = TopicDefinition(
    id="sine_rule",
    display_name="Sine Rule",
    description="Use the sine rule to find a missing side or angle in a non-right-angled triangle.",
    generate=generate_sine_rule,
    section=SECTION,
    group=GROUP_SINE,
    fixed_tier=Tier.HIGHER,
)

TOPIC_COSINE_RULE = TopicDefinition(
    id="cosine_rule",
    display_name="Cosine Rule",
    description="Use the cosine rule to find a missing side or angle in a non-right-angled triangle.",
    generate=generate_cosine_rule,
    section=SECTION,
    group=GROUP_COSINE,
    fixed_tier=Tier.HIGHER,
)

TOPIC_TRIANGLE_AREA = TopicDefinition(
    id="triangle_area_sine_rule",
    display_name="Area of a Triangle",
    description="Find the area of a triangle using Area = (1/2)ab sin(C).",
    generate=generate_triangle_area,
    section=SECTION,
    group=GROUP_AREA,
    fixed_tier=Tier.HIGHER,
)
