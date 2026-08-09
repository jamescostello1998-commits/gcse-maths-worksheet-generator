"""3D Pythagoras and 3D trigonometry (Higher only): finding the space diagonal
of a cuboid, and the angle between that diagonal and the cuboid's base. Both
share the same cuboid-dimension generation, so they live in one file.
"""

import math
import random
from decimal import ROUND_HALF_UP, Decimal

from app.core.models import DiagramSpec, ModelledExample, Question, Tier
from app.topics.base import TopicDefinition
from app.topics.rounding import pick_rounding

SECTION = "geometry"
GROUP_PYTHAGORAS = "Pythagoras' Theorem"
GROUP_TRIG = "Trigonometry"


def _round_dp(value: float, dp: int) -> Decimal:
    return Decimal(str(value)).quantize(Decimal(1).scaleb(-dp), rounding=ROUND_HALF_UP)


def _cuboid_dims(rng: random.Random) -> tuple[int, int, int]:
    """Random cuboid dimensions, rerolling away from the rare case where the
    space diagonal happens to be a perfect square (keeping the answer always
    decimal, matching this app's established convention for genuinely
    irrational real-world 3D results - see solids_cylinders_cones.py)."""
    for _ in range(100):
        l, w, h = rng.randint(3, 15), rng.randint(3, 15), rng.randint(3, 15)
        sum_sq = l * l + w * w + h * h
        if math.isqrt(sum_sq) ** 2 != sum_sq:
            return l, w, h
    raise ValueError("solids_3d_trig: could not find a non-perfect-square cuboid")


# ---------------------------------------------------------------------------
# 3D Pythagoras
# ---------------------------------------------------------------------------


def generate_3d_pythagoras(tier: Tier, rng: random.Random) -> Question:
    l, w, h = _cuboid_dims(rng)
    base_diag_sq = l * l + w * w
    space_diag = math.sqrt(base_diag_sq + h * h)

    # Independent verification: the direct 3D coordinate distance formula -
    # a genuinely different code path than the two sequential sqrt()
    # applications used to build the displayed steps. Compares full-precision
    # raw values only, unrelated to which display precision is chosen below,
    # so needs no change for the rounding rollout.
    check = math.dist((0, 0, 0), (l, w, h))
    if abs(space_diag - check) > 1e-9:
        raise ValueError("3d_pythagoras: verification failed")

    rounding = pick_rounding(rng)
    rounded = format(rounding.round_fn(space_diag), "f")

    steps = [
        f"First find the diagonal across the base: base diagonal² = l² + w² = {l}² + {w}² = {base_diag_sq}.",
        f"Then apply Pythagoras again using the height: ag² = base diagonal² + h² = {base_diag_sq} + {h}² = {base_diag_sq + h * h}.",
        f"ag = √{base_diag_sq + h * h} = {rounded} cm ({rounding.short})",
    ]
    return Question(
        topic_id="pythagoras_3d",
        tier=Tier.HIGHER,
        prompt=(
            f"A cuboid has length {l} cm, width {w} cm and height {h} cm. Find the length of the "
            "diagonal ag that runs from one corner of the cuboid to the opposite corner, correct "
            f"to {rounding.phrase}."
        ),
        solution_steps=tuple(steps),
        final_answer=f"{rounded} cm",
        dedup_key=f"3d_pyth:{l}:{w}:{h}",
        diagram=DiagramSpec(
            kind="cuboid",
            params={
                "length_label": f"{l} cm",
                "width_label": f"{w} cm",
                "height_label": f"{h} cm",
                "show_diagonal": True,
                "vertex_labels": ["a", "b", "c", "d", "e", "f", "g", "h"],
            },
        ),
    )


def generate_modelled_example_3d_pythagoras(tier: Tier, rng: random.Random) -> ModelledExample:
    l, w, h = _cuboid_dims(rng)
    base_diag_sq = l * l + w * w
    space_diag = math.sqrt(base_diag_sq + h * h)

    check = math.dist((0, 0, 0), (l, w, h))
    if abs(space_diag - check) > 1e-9:
        raise ValueError("modelled example 3d_pythagoras: verification failed")

    rounding = pick_rounding(rng)
    rounded = format(rounding.round_fn(space_diag), "f")

    teaching_steps = [
        "A 3D diagonal like ag can't be found in one step - it needs Pythagoras applied twice, "
        "once across the base and once up through the cuboid's height.",
        f"Step 1: find the diagonal across the base rectangle (length {l} cm by width {w} cm). "
        f"This diagonal² = l² + w² = {l}² + {w}² = {base_diag_sq}.",
        f"Step 2: that base diagonal, the height ({h} cm), and ag itself form a second right-angled "
        f"triangle - so ag² = base diagonal² + h² = {base_diag_sq} + {h}² = {base_diag_sq + h * h}.",
        f"ag = √{base_diag_sq + h * h} ≈ {rounded} cm ({rounding.short}) - always take the square "
        "root right at the end, not partway through.",
    ]
    worked_calculation = [
        f"base diagonal² = {l}² + {w}² = {base_diag_sq}",
        f"ag² = {base_diag_sq} + {h}² = {base_diag_sq + h * h}",
        f"ag = {rounded} cm ({rounding.short})",
    ]
    return ModelledExample(
        topic_id="pythagoras_3d",
        tier=Tier.HIGHER,
        prompt=(
            f"A cuboid has length {l} cm, width {w} cm and height {h} cm. Find the length of the "
            "diagonal ag that runs from one corner of the cuboid to the opposite corner, correct "
            f"to {rounding.phrase}."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{rounded} cm",
        diagram=DiagramSpec(
            kind="cuboid",
            params={
                "length_label": f"{l} cm",
                "width_label": f"{w} cm",
                "height_label": f"{h} cm",
                "show_diagonal": True,
                "vertex_labels": ["a", "b", "c", "d", "e", "f", "g", "h"],
            },
        ),
    )


# ---------------------------------------------------------------------------
# 3D Trigonometry
# ---------------------------------------------------------------------------


def generate_3d_trigonometry(tier: Tier, rng: random.Random) -> Question:
    l, w, h = _cuboid_dims(rng)
    base_diag = math.sqrt(l * l + w * w)
    angle = math.degrees(math.atan(h / base_diag))
    rounded = _round_dp(angle, 1)

    # Independent verification: the 3D vector dot-product/acos formula between
    # the space diagonal (l, w, h) and its base projection (l, w, 0) - a
    # genuinely different computation than the atan(h/base_diag) used to
    # build the displayed steps.
    dot = l * l + w * w
    norm_diag = math.hypot(l, w, h)
    norm_base = math.hypot(l, w)
    check_angle = math.degrees(math.acos(dot / (norm_diag * norm_base)))
    if abs(angle - check_angle) > 1e-6:
        raise ValueError("3d_trigonometry: verification failed")

    steps = [
        f"First find the diagonal across the base: base diagonal = √(l² + w²) = √({l}² + {w}²) "
        f"= {base_diag:.3f} cm - this is the projection of ag onto the base.",
        f"The angle between ag and the base, height and base diagonal form a right-angled "
        f"triangle: tan(angle) = height ÷ base diagonal = {h} ÷ {base_diag:.3f}.",
        f"angle = tan^-1({h} ÷ {base_diag:.3f}) = {rounded}° (1 d.p.)",
    ]
    return Question(
        topic_id="trig_3d",
        tier=Tier.HIGHER,
        prompt=(
            f"A cuboid has length {l} cm, width {w} cm and height {h} cm. Find the angle between "
            "the diagonal ag (from one corner to the opposite corner) and the base of the cuboid, "
            "correct to 1 decimal place."
        ),
        solution_steps=tuple(steps),
        final_answer=f"{rounded}°",
        dedup_key=f"3d_trig:{l}:{w}:{h}",
        diagram=DiagramSpec(
            kind="cuboid",
            params={
                "length_label": f"{l} cm",
                "width_label": f"{w} cm",
                "height_label": f"{h} cm",
                "show_diagonal": True,
                "vertex_labels": ["a", "b", "c", "d", "e", "f", "g", "h"],
            },
        ),
    )


def generate_modelled_example_3d_trigonometry(tier: Tier, rng: random.Random) -> ModelledExample:
    l, w, h = _cuboid_dims(rng)
    base_diag = math.sqrt(l * l + w * w)
    angle = math.degrees(math.atan(h / base_diag))
    rounded = _round_dp(angle, 1)

    dot = l * l + w * w
    norm_diag = math.hypot(l, w, h)
    norm_base = math.hypot(l, w)
    check_angle = math.degrees(math.acos(dot / (norm_diag * norm_base)))
    if abs(angle - check_angle) > 1e-6:
        raise ValueError("modelled example 3d_trigonometry: verification failed")

    teaching_steps = [
        "The angle between a 3D diagonal and the base is found by dropping a right-angled "
        "triangle down onto the base: the diagonal ag, its 'shadow' on the base (the base "
        "diagonal), and the vertical height h.",
        f"First find that base diagonal, the shadow's length: √(l² + w²) = √({l}² + {w}²) "
        f"≈ {base_diag:.3f} cm.",
        f"The height h = {h} cm is opposite the angle we want, and the base diagonal is adjacent "
        f"to it, so tan(angle) = {h} ÷ {base_diag:.3f}.",
        f"Apply tan^-1 to both sides: angle = tan^-1({h} ÷ {base_diag:.3f}) ≈ {rounded}° (1 d.p.).",
    ]
    worked_calculation = [
        f"base diagonal = √({l}² + {w}²) = {base_diag:.3f} cm",
        f"tan(angle) = {h} ÷ {base_diag:.3f}",
        f"angle = {rounded}° (1 d.p.)",
    ]
    return ModelledExample(
        topic_id="trig_3d",
        tier=Tier.HIGHER,
        prompt=(
            f"A cuboid has length {l} cm, width {w} cm and height {h} cm. Find the angle between "
            "the diagonal ag (from one corner to the opposite corner) and the base of the cuboid, "
            "correct to 1 decimal place."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{rounded}°",
        diagram=DiagramSpec(
            kind="cuboid",
            params={
                "length_label": f"{l} cm",
                "width_label": f"{w} cm",
                "height_label": f"{h} cm",
                "show_diagonal": True,
                "vertex_labels": ["a", "b", "c", "d", "e", "f", "g", "h"],
            },
        ),
    )


TOPIC_3D_PYTHAGORAS = TopicDefinition(
    id="pythagoras_3d",
    display_name="3D Pythagoras",
    description="Find the length of the space diagonal of a cuboid using Pythagoras' theorem twice.",
    generate=generate_3d_pythagoras,
    section=SECTION,
    group=GROUP_PYTHAGORAS,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_3d_pythagoras,
)

TOPIC_3D_TRIGONOMETRY = TopicDefinition(
    id="trig_3d",
    display_name="3D Trigonometry",
    description="Find the angle between a cuboid's space diagonal and its base.",
    generate=generate_3d_trigonometry,
    section=SECTION,
    group=GROUP_TRIG,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_3d_trigonometry,
)
