import math
import random
from decimal import ROUND_HALF_UP, Decimal

from app.core.models import DiagramSpec, ModelledExample, Question, Tier
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


def generate_modelled_example_sine_rule(tier: Tier, rng: random.Random) -> ModelledExample:
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

        # Independent verification via coordinate geometry, same cross-check as the
        # real generator: build the triangle from the two angles and side a, then
        # measure side a back out with the distance formula.
        A, B = (0.0, 0.0), (side_c, 0.0)
        C = (side_b * math.cos(rad_A), side_b * math.sin(rad_A))
        if abs(_dist(B, C) - side_a) > 1e-6:
            raise ValueError("modelled example sine_rule verification failed: coordinate cross-check mismatch")

        b_str = _fmt_dec(_round_sf(side_b, 3))

        if shape == "side":
            teaching_steps = [
                "The sine rule links every side of a triangle to the sine of the angle directly "
                "opposite it: a / sin(A) = b / sin(B) = c / sin(C). It's the tool to reach for whenever "
                "you know one full side-angle pair (a matching side and its opposite angle) plus one "
                "more angle or side.",
                f"Here side a = {side_a} cm is opposite angle A = {angle_A}°, and we want side b, which "
                f"is opposite angle B = {angle_B}°. Since we know the pair (a, A) fully, pick the version "
                "of the rule that also involves b and B: a / sin(A) = b / sin(B).",
                "Rearrange to make the side we want, b, the subject, by cross-multiplying and dividing.",
                f"Substitute in the numbers: b = ({side_a} × sin({angle_B}°)) ÷ sin({angle_A}°), which "
                f"evaluates to {b_str} cm once rounded to 3 significant figures as asked.",
            ]
            worked_calculation = [
                "a / sin(A) = b / sin(B)",
                f"b = ({side_a} × sin({angle_B}°)) ÷ sin({angle_A}°)",
                f"b = {b_str} cm",
            ]
            prompt = (
                f"In triangle ABC, angle A = {angle_A}°, angle B = {angle_B}°, and side a = {side_a} cm. "
                "Find the length of side b, correct to 3 significant figures."
            )
            answer = f"{b_str} cm"
            diagram = DiagramSpec(
                kind="general_triangle",
                params={
                    "side_a_label": f"{side_a} cm", "side_b_label": f"{b_str} cm", "side_c_label": None,
                    "angle_A_label": f"{angle_A}°", "angle_B_label": f"{angle_B}°", "angle_C_label": None,
                },
            )
        else:
            ratio = float(b_str) * math.sin(rad_A) / side_a
            if not (-1 <= ratio <= 1):
                continue
            recomputed_B = math.degrees(math.asin(ratio))
            if abs(recomputed_B - angle_B) > 0.5:
                continue

            teaching_steps = [
                "The sine rule links every side of a triangle to the sine of the angle directly "
                "opposite it: sin(A) / a = sin(B) / b = sin(C) / c. It's the tool to reach for whenever "
                "you know one full side-angle pair plus one more side, and want the angle opposite "
                "that other side.",
                f"Here angle A = {angle_A}° and side a = {side_a} cm form a known pair, and we also know "
                f"side b = {b_str} cm, opposite the angle B we want. Use sin(B) / b = sin(A) / a.",
                "Rearrange to make sin(B) the subject by cross-multiplying, then take the inverse sine "
                "at the very end (not before) to avoid rounding errors creeping in early.",
                f"sin(B) = ({b_str} × sin({angle_A}°)) ÷ {side_a}, so B = sin^-1(...) = {angle_B}.0°, "
                "rounded to 1 decimal place.",
            ]
            worked_calculation = [
                "sin(B) / b = sin(A) / a",
                f"sin(B) = ({b_str} × sin({angle_A}°)) ÷ {side_a}",
                f"B = {angle_B}.0°",
            ]
            prompt = (
                f"In triangle ABC, angle A = {angle_A}°, side a = {side_a} cm, and side b = {b_str} cm. "
                "Find angle B, correct to 1 decimal place."
            )
            answer = f"{angle_B}.0°"
            diagram = DiagramSpec(
                kind="general_triangle",
                params={
                    "side_a_label": f"{side_a} cm", "side_b_label": f"{b_str} cm", "side_c_label": None,
                    "angle_A_label": f"{angle_A}°", "angle_B_label": f"{angle_B}.0°", "angle_C_label": None,
                },
            )

        return ModelledExample(
            topic_id="sine_rule",
            tier=Tier.HIGHER,
            prompt=prompt,
            worked_calculation=tuple(worked_calculation),
            teaching_steps=tuple(teaching_steps),
            final_answer=answer,
            diagram=diagram,
        )

    raise ValueError("modelled example sine_rule could not find valid parameters after 50 attempts")


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
            f"A = cos^-1({cos_a_str}) = {_fmt_dec(rounded)}° (1 d.p.)",
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


def generate_modelled_example_cosine_rule(tier: Tier, rng: random.Random) -> ModelledExample:
    shape = rng.choice(["side", "angle"])

    if shape == "side":
        b, c = rng.randint(5, 30), rng.randint(5, 30)
        angle_A = rng.randint(20, 150)
        rad_A = math.radians(angle_A)
        a_sq = b * b + c * c - 2 * b * c * math.cos(rad_A)
        side_a = math.sqrt(a_sq)

        # Independent verification via coordinate geometry, same cross-check as the
        # real generator: place the known angle A between the two known sides, then
        # measure side a with the distance formula.
        B, C = (c, 0.0), (b * math.cos(rad_A), b * math.sin(rad_A))
        if abs(_dist(B, C) - side_a) > 1e-6:
            raise ValueError("modelled example cosine_rule verification failed: coordinate cross-check mismatch")

        rounded = _round_sf(side_a, 3)
        a_sq_str = _fmt_dec(_round_sf(a_sq, 4))
        teaching_steps = [
            "The cosine rule finds a missing side when you know the other two sides and the angle "
            "trapped between them (the 'included' angle) - a case the sine rule can't reach directly, "
            "since no side-angle pair is fully known yet.",
            f"Substitute the two known sides b = {b} cm, c = {c} cm, and the included angle A = "
            f"{angle_A}° into a² = b² + c² - 2bc cos(A).",
            f"Work through the right-hand side one term at a time: {b}² + {c}² - 2×{b}×{c}×cos({angle_A}°) "
            f"= {a_sq_str}. This is a², not a - don't forget the final step.",
            f"Take the square root to undo the squaring: a = √{a_sq_str} = {_fmt_dec(rounded)} cm, "
            "rounded to 3 significant figures as the question asks.",
        ]
        worked_calculation = [
            "a² = b² + c² - 2bc cos(A)",
            f"a² = {b}² + {c}² - 2×{b}×{c}×cos({angle_A}°) = {a_sq_str}",
            f"a = √{a_sq_str} = {_fmt_dec(rounded)} cm",
        ]
        prompt = (
            f"In triangle ABC, side b = {b} cm, side c = {c} cm, and the angle between them, "
            f"angle A = {angle_A}°. Find the length of side a, correct to 3 significant figures."
        )
        answer = f"{_fmt_dec(rounded)} cm"
        diagram = DiagramSpec(
            kind="general_triangle",
            params={
                "side_a_label": f"{_fmt_dec(rounded)} cm", "side_b_label": f"{b} cm", "side_c_label": f"{c} cm",
                "angle_A_label": f"{angle_A}°", "angle_B_label": None, "angle_C_label": None,
            },
        )
    else:
        for _ in range(200):
            a, b, c = rng.randint(5, 25), rng.randint(5, 25), rng.randint(5, 25)
            if a + b > c and a + c > b and b + c > a:
                break
        else:
            raise ValueError("modelled example cosine_rule could not find a valid triangle")

        cos_A = (b * b + c * c - a * a) / (2 * b * c)
        if not (-1 <= cos_A <= 1):
            raise ValueError("modelled example cosine_rule produced an invalid cosine value")
        angle_A = math.degrees(math.acos(cos_A))

        # Independent verification via coordinate geometry (SSS construction), same
        # cross-check as the real generator: build the triangle from the three side
        # lengths alone, then measure angle A with the dot-product formula.
        B, C = (0.0, 0.0), (a, 0.0)
        ax = (a * a + c * c - b * b) / (2 * a)
        ay_sq = c * c - ax * ax
        if ay_sq < 0:
            raise ValueError("modelled example cosine_rule verification failed: degenerate triangle")
        A = (ax, math.sqrt(ay_sq))
        v1, v2 = (B[0] - A[0], B[1] - A[1]), (C[0] - A[0], C[1] - A[1])
        dot = v1[0] * v2[0] + v1[1] * v2[1]
        check_angle = math.degrees(math.acos(dot / (math.hypot(*v1) * math.hypot(*v2))))
        if abs(check_angle - angle_A) > 1e-6:
            raise ValueError("modelled example cosine_rule verification failed: coordinate cross-check mismatch")

        rounded = _round_dp(angle_A, 1)
        cos_a_str = _fmt_dec(_round_sf(cos_A, 4))
        teaching_steps = [
            "When you know all three sides of a triangle but no angles, rearrange the cosine rule so "
            "cos(A) is the subject instead of a: cos(A) = (b² + c² - a²) ÷ (2bc).",
            f"Substitute the three sides - remembering a = {a} cm is always the side opposite the "
            f"angle you're solving for: cos(A) = ({b}² + {c}² - {a}²) ÷ (2×{b}×{c}).",
            f"Evaluate the fraction to get cos(A) = {cos_a_str}.",
            f"Undo the cosine with inverse cosine (cos^-1) to recover the angle itself: "
            f"A = cos^-1({cos_a_str}) = {_fmt_dec(rounded)}°, rounded to 1 decimal place.",
        ]
        worked_calculation = [
            "cos(A) = (b² + c² - a²) ÷ (2bc)",
            f"cos(A) = ({b}² + {c}² - {a}²) ÷ (2×{b}×{c}) = {cos_a_str}",
            f"A = cos^-1({cos_a_str}) = {_fmt_dec(rounded)}°",
        ]
        prompt = (
            f"In triangle ABC, side a = {a} cm, side b = {b} cm, and side c = {c} cm. "
            "Find angle A, correct to 1 decimal place."
        )
        answer = f"{_fmt_dec(rounded)}°"
        diagram = DiagramSpec(
            kind="general_triangle",
            params={
                "side_a_label": f"{a} cm", "side_b_label": f"{b} cm", "side_c_label": f"{c} cm",
                "angle_A_label": f"{_fmt_dec(rounded)}°", "angle_B_label": None, "angle_C_label": None,
            },
        )

    return ModelledExample(
        topic_id="cosine_rule",
        tier=Tier.HIGHER,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
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


def generate_modelled_example_triangle_area(tier: Tier, rng: random.Random) -> ModelledExample:
    a, b = rng.randint(5, 25), rng.randint(5, 25)
    angle_C = rng.randint(20, 160)
    rad_C = math.radians(angle_C)
    area = 0.5 * a * b * math.sin(rad_C)

    # Independent verification via the shoelace formula, same cross-check as the real
    # generator: place the shared vertex C at the origin with sides a and b (CB and
    # CA) at the given angle, then compute the triangle's area from the coordinates.
    C0, B, A = (0.0, 0.0), (a, 0.0), (b * math.cos(rad_C), b * math.sin(rad_C))
    shoelace_area = abs(C0[0] * (B[1] - A[1]) + B[0] * (A[1] - C0[1]) + A[0] * (C0[1] - B[1])) / 2
    if abs(shoelace_area - area) > 1e-6:
        raise ValueError("modelled example triangle_area verification failed: shoelace cross-check mismatch")

    rounded = _round_sf(area, 3)
    teaching_steps = [
        "The usual triangle area formula, Area = (1/2) × base × height, needs a height measured at a "
        "right angle to the base - but if you only know two sides and the angle between them, there's "
        "a version that skips finding the height altogether: Area = (1/2) × a × b × sin(C).",
        f"Here a = {a} cm and b = {b} cm are the two known sides, and C = {angle_C}° is the included "
        "angle - the angle at the vertex where those two sides meet, not one of the other two angles.",
        f"Substitute the values straight into the formula: Area = 0.5 × {a} × {b} × sin({angle_C}°).",
        f"Evaluating gives {_fmt_dec(rounded)} cm², rounded to 3 significant figures as asked.",
    ]
    worked_calculation = [
        "Area = (1/2) × a × b × sin(C)",
        f"Area = 0.5 × {a} × {b} × sin({angle_C}°) = {_fmt_dec(rounded)} cm²",
    ]
    return ModelledExample(
        topic_id="triangle_area_sine_rule",
        tier=Tier.HIGHER,
        prompt=(
            f"Triangle ABC has side a = {a} cm, side b = {b} cm, and the angle between them, "
            f"angle C = {angle_C}°. Find the area of the triangle, correct to 3 significant figures."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{_fmt_dec(rounded)} cm²",
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
    generate_modelled_example=generate_modelled_example_sine_rule,
)

TOPIC_COSINE_RULE = TopicDefinition(
    id="cosine_rule",
    display_name="Cosine Rule",
    description="Use the cosine rule to find a missing side or angle in a non-right-angled triangle.",
    generate=generate_cosine_rule,
    section=SECTION,
    group=GROUP_COSINE,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_cosine_rule,
)

TOPIC_TRIANGLE_AREA = TopicDefinition(
    id="triangle_area_sine_rule",
    display_name="Area of a Triangle",
    description="Find the area of a triangle using Area = (1/2)ab sin(C).",
    generate=generate_triangle_area,
    section=SECTION,
    group=GROUP_AREA,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_triangle_area,
)
