import random

from app.core.models import DiagramSpec, ModelledExample, Question, Tier
from app.topics.base import TopicDefinition

SECTION = "geometry"
GROUP = "Circle Theorems"


def _angle_at_centre(rng: random.Random) -> Question:
    circ_angle = rng.randint(20, 80)
    centre_angle = circ_angle * 2
    if centre_angle != 2 * circ_angle:
        raise ValueError("circle_theorem verification failed: angle at centre")

    if rng.random() < 0.5:
        centre_label, circ_label = "x°", f"{circ_angle}°"
        answer, ask = f"{centre_angle}°", "the angle at the centre, x"
        calc = f"x = 2 × {circ_angle}° = {centre_angle}°"
    else:
        centre_label, circ_label = f"{centre_angle}°", "x°"
        answer, ask = f"{circ_angle}°", "the angle at the circumference, x"
        calc = f"x = {centre_angle}° ÷ 2 = {circ_angle}°"

    steps = [
        "The angle at the centre is twice the angle at the circumference subtended by the same arc.",
        calc,
    ]
    return Question(
        topic_id="circle_theorems",
        tier=Tier.HIGHER,
        prompt=f"A and B are points on a circle with centre O, and C is a point on the major arc. Find {ask}.",
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"circ_centre:{circ_angle}:{centre_label}",
        diagram=DiagramSpec(
            kind="circle_angle_centre",
            params={"centre_label": centre_label, "circumference_label": circ_label},
        ),
    )


def _angle_in_semicircle(rng: random.Random) -> Question:
    given_angle = rng.randint(20, 70)
    unknown_angle = 180 - 90 - given_angle
    if unknown_angle < 10:
        raise ValueError("circle_theorem verification failed: semicircle produced a non-physical angle")
    if given_angle + unknown_angle + 90 != 180:
        raise ValueError("circle_theorem verification failed: semicircle angle sum")

    steps = [
        "AB is a diameter, so the angle in the semicircle, angle ACB, is 90°.",
        f"Angles in triangle ABC sum to 180°: x = 180 - 90 - {given_angle} = {unknown_angle}",
    ]
    return Question(
        topic_id="circle_theorems",
        tier=Tier.HIGHER,
        prompt=(
            "A, B, and C are points on a circle, where AB is a diameter. "
            f"Angle BAC = {given_angle}°. Find angle ABC, x."
        ),
        solution_steps=tuple(steps),
        final_answer=f"{unknown_angle}°",
        dedup_key=f"circ_semi:{given_angle}",
        diagram=DiagramSpec(
            kind="circle_semicircle",
            params={"apex_label": "90°", "angle_a_label": f"{given_angle}°", "angle_b_label": "x°"},
        ),
    )


def _cyclic_quadrilateral(rng: random.Random) -> Question:
    given_angle = rng.randint(60, 120)
    unknown_angle = 180 - given_angle
    if given_angle + unknown_angle != 180:
        raise ValueError("circle_theorem verification failed: cyclic quadrilateral")

    steps = [
        "Opposite angles in a cyclic quadrilateral sum to 180°.",
        f"x = 180 - {given_angle} = {unknown_angle}",
    ]
    return Question(
        topic_id="circle_theorems",
        tier=Tier.HIGHER,
        prompt=f"ABCD is a cyclic quadrilateral. Angle A = {given_angle}°. Find angle C, x, the angle opposite A.",
        solution_steps=tuple(steps),
        final_answer=f"{unknown_angle}°",
        dedup_key=f"circ_cyclic:{given_angle}",
        diagram=DiagramSpec(
            kind="circle_cyclic_quad",
            params={"angle_A_label": f"{given_angle}°", "angle_C_label": "x°"},
        ),
    )


def _two_tangents(rng: random.Random) -> Question:
    given_angle = rng.randint(20, 120)
    unknown_angle = 180 - given_angle
    if unknown_angle <= 0:
        raise ValueError("circle_theorem verification failed: two tangents produced a non-physical angle")
    # Independent check: the quadrilateral OATB has two right angles (radius meets
    # tangent at 90°) plus these two angles, so its interior angles must sum to 360°.
    if 90 + 90 + given_angle + unknown_angle != 360:
        raise ValueError("circle_theorem verification failed: OATB angle sum")

    steps = [
        "TA and TB are tangents, so angle OAT = angle OBT = 90° (radius meets tangent at a right angle).",
        f"Angles in quadrilateral OATB sum to 360°: x = 360 - 90 - 90 - {given_angle} = {unknown_angle}",
    ]
    return Question(
        topic_id="circle_theorems",
        tier=Tier.HIGHER,
        prompt=(
            "TA and TB are tangents to a circle with centre O, touching it at A and B. "
            f"Angle ATB = {given_angle}°. Find angle AOB, x."
        ),
        solution_steps=tuple(steps),
        final_answer=f"{unknown_angle}°",
        dedup_key=f"circ_tangents:{given_angle}",
        diagram=DiagramSpec(
            kind="circle_two_tangents",
            params={"external_label": f"{given_angle}°", "centre_label": "x°"},
        ),
    )


def _angle_same_segment(rng: random.Random) -> Question:
    given_angle = rng.randint(20, 80)
    unknown_angle = given_angle
    if unknown_angle != given_angle:
        raise ValueError("circle_theorem verification failed: angles in the same segment")

    if rng.random() < 0.5:
        c_label, d_label = f"{given_angle}°", "x°"
        ask = "angle ADB, x"
    else:
        c_label, d_label = "x°", f"{given_angle}°"
        ask = "angle ACB, x"

    steps = [
        "Angles in the same segment, subtended by the same chord (here AB), are equal.",
        f"x = {given_angle}°",
    ]
    return Question(
        topic_id="circle_theorems",
        tier=Tier.HIGHER,
        prompt=(
            "A, B, C, and D are points on a circle, where C and D are on the same arc, both subtending "
            f"the chord AB. Find {ask}."
        ),
        solution_steps=tuple(steps),
        final_answer=f"{unknown_angle}°",
        dedup_key=f"circ_same_seg:{given_angle}:{c_label}",
        diagram=DiagramSpec(
            kind="circle_same_segment",
            params={"angle_c_label": c_label, "angle_d_label": d_label},
        ),
    )


def _alternate_segment(rng: random.Random) -> Question:
    given_angle = rng.randint(20, 80)
    unknown_angle = given_angle
    if unknown_angle != given_angle:
        raise ValueError("circle_theorem verification failed: alternate segment theorem")

    if rng.random() < 0.5:
        tangent_label, segment_label = f"{given_angle}°", "x°"
        ask = "angle QRP, x"
    else:
        tangent_label, segment_label = "x°", f"{given_angle}°"
        ask = "the angle between the tangent and the chord PQ, x"

    steps = [
        "The alternate segment theorem: the angle between a tangent and a chord equals the angle "
        "subtended by that chord in the alternate segment.",
        f"x = {given_angle}°",
    ]
    return Question(
        topic_id="circle_theorems",
        tier=Tier.HIGHER,
        prompt=(
            "PQ is a chord of a circle, with a tangent at P. R is a point on "
            f"the circle in the alternate segment. Find {ask}."
        ),
        solution_steps=tuple(steps),
        final_answer=f"{unknown_angle}°",
        dedup_key=f"circ_alt_seg:{given_angle}:{tangent_label}",
        diagram=DiagramSpec(
            kind="circle_alternate_segment",
            params={"tangent_angle_label": tangent_label, "segment_angle_label": segment_label},
        ),
    )


_SHAPES = [
    _angle_at_centre,
    _angle_in_semicircle,
    _cyclic_quadrilateral,
    _two_tangents,
    _angle_same_segment,
    _alternate_segment,
]


def generate_circle_theorem(tier: Tier, rng: random.Random) -> Question:
    shape = rng.choice(_SHAPES)
    return shape(rng)


def _modelled_angle_at_centre(rng: random.Random) -> ModelledExample:
    circ_angle = rng.randint(20, 80)
    centre_angle = circ_angle * 2
    if centre_angle != 2 * circ_angle:
        raise ValueError("modelled example circle_theorem verification failed: angle at centre")

    if rng.random() < 0.5:
        centre_label, circ_label = "x°", f"{circ_angle}°"
        answer, ask = f"{centre_angle}°", "the angle at the centre, x"
        worked_calculation = [f"x = 2 × {circ_angle}°", f"x = {centre_angle}°"]
        teaching_steps = [
            "The angle at the centre theorem says the angle at the centre of a circle is always "
            "exactly double the angle at the circumference, provided both angles are subtended by "
            "(stand on) the same arc.",
            f"Here the angle at the circumference is given as {circ_angle}°, and we want the angle "
            "at the centre - since the centre angle is the bigger one, we double rather than halve.",
            f"x = 2 × {circ_angle}° = {centre_angle}°.",
        ]
    else:
        centre_label, circ_label = f"{centre_angle}°", "x°"
        answer, ask = f"{circ_angle}°", "the angle at the circumference, x"
        worked_calculation = [f"x = {centre_angle}° ÷ 2", f"x = {circ_angle}°"]
        teaching_steps = [
            "The angle at the centre theorem says the angle at the centre of a circle is always "
            "exactly double the angle at the circumference, provided both angles are subtended by "
            "(stand on) the same arc.",
            f"Here the angle at the centre is given as {centre_angle}°, and we want the angle at the "
            "circumference - since the circumference angle is the smaller one, we halve rather than "
            "double.",
            f"x = {centre_angle}° ÷ 2 = {circ_angle}°.",
        ]

    return ModelledExample(
        topic_id="circle_theorems",
        tier=Tier.HIGHER,
        prompt=f"A and B are points on a circle with centre O, and C is a point on the major arc. Find {ask}.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
        diagram=DiagramSpec(
            kind="circle_angle_centre",
            params={"centre_label": centre_label, "circumference_label": circ_label},
        ),
    )


def _modelled_angle_in_semicircle(rng: random.Random) -> ModelledExample:
    given_angle = rng.randint(20, 70)
    unknown_angle = 180 - 90 - given_angle
    if unknown_angle < 10:
        raise ValueError("modelled example circle_theorem verification failed: semicircle produced a non-physical angle")
    if given_angle + unknown_angle + 90 != 180:
        raise ValueError("modelled example circle_theorem verification failed: semicircle angle sum")

    teaching_steps = [
        "Whenever a triangle is drawn inside a circle with one of its sides as a diameter, the angle "
        "at the third vertex (the one opposite the diameter) is always exactly 90° - this is the "
        "angle in a semicircle theorem.",
        f"AB is given as a diameter here, so angle ACB = 90° immediately - no calculation needed for "
        "that part.",
        "The three angles of triangle ABC must still sum to 180° like any triangle, so the remaining "
        "angle is found by subtracting the two we already know from 180°.",
        f"x = 180 - 90 - {given_angle} = {unknown_angle}°.",
    ]
    worked_calculation = [
        f"90 + {given_angle} + x = 180",
        f"x = 180 - 90 - {given_angle}",
        f"x = {unknown_angle}",
    ]
    return ModelledExample(
        topic_id="circle_theorems",
        tier=Tier.HIGHER,
        prompt=(
            "A, B, and C are points on a circle, where AB is a diameter. "
            f"Angle BAC = {given_angle}°. Find angle ABC, x."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{unknown_angle}°",
        diagram=DiagramSpec(
            kind="circle_semicircle",
            params={"apex_label": "90°", "angle_a_label": f"{given_angle}°", "angle_b_label": f"{unknown_angle}°"},
        ),
    )


def _modelled_cyclic_quadrilateral(rng: random.Random) -> ModelledExample:
    given_angle = rng.randint(60, 120)
    unknown_angle = 180 - given_angle
    if given_angle + unknown_angle != 180:
        raise ValueError("modelled example circle_theorem verification failed: cyclic quadrilateral")

    teaching_steps = [
        "A cyclic quadrilateral is a four-sided shape whose four corners all lie on the same circle. "
        "A special property of these shapes - one that doesn't hold for quadrilaterals in general - "
        "is that each pair of opposite angles always adds up to 180°.",
        "Angle A and angle C sit opposite each other in quadrilateral ABCD, so they must be a pair "
        "that sums to 180°.",
        f"We're given angle A = {given_angle}°, so angle C = 180 - {given_angle} = {unknown_angle}°.",
    ]
    worked_calculation = [
        f"{given_angle} + x = 180",
        f"x = {unknown_angle}",
    ]
    return ModelledExample(
        topic_id="circle_theorems",
        tier=Tier.HIGHER,
        prompt=f"ABCD is a cyclic quadrilateral. Angle A = {given_angle}°. Find angle C, x, the angle opposite A.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{unknown_angle}°",
        diagram=DiagramSpec(
            kind="circle_cyclic_quad",
            params={"angle_A_label": f"{given_angle}°", "angle_C_label": f"{unknown_angle}°"},
        ),
    )


def _modelled_two_tangents(rng: random.Random) -> ModelledExample:
    given_angle = rng.randint(20, 120)
    unknown_angle = 180 - given_angle
    if unknown_angle <= 0:
        raise ValueError("modelled example circle_theorem verification failed: two tangents produced a non-physical angle")
    # Independent check: the quadrilateral OATB has two right angles (radius meets
    # tangent at 90°) plus these two angles, so its interior angles must sum to 360°.
    if 90 + 90 + given_angle + unknown_angle != 360:
        raise ValueError("modelled example circle_theorem verification failed: OATB angle sum")

    teaching_steps = [
        "A tangent to a circle always meets the radius drawn to its point of contact at a right "
        "angle - this holds wherever a tangent touches a circle.",
        f"TA and TB are tangents here, touching the circle at A and B, so angle OAT = angle OBT = 90°, "
        "no matter what the other angles turn out to be.",
        "OATB is a four-sided shape, and like any quadrilateral its four interior angles must sum "
        "to 360°.",
        f"x = 360 - 90 - 90 - {given_angle} = {unknown_angle}°.",
    ]
    worked_calculation = [
        f"90 + 90 + {given_angle} + x = 360",
        f"x = 360 - 180 - {given_angle}",
        f"x = {unknown_angle}",
    ]
    return ModelledExample(
        topic_id="circle_theorems",
        tier=Tier.HIGHER,
        prompt=(
            "TA and TB are tangents to a circle with centre O, touching it at A and B. "
            f"Angle ATB = {given_angle}°. Find angle AOB, x."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{unknown_angle}°",
        diagram=DiagramSpec(
            kind="circle_two_tangents",
            params={"external_label": f"{given_angle}°", "centre_label": f"{unknown_angle}°"},
        ),
    )


def _modelled_angle_same_segment(rng: random.Random) -> ModelledExample:
    given_angle = rng.randint(20, 80)
    unknown_angle = given_angle
    if unknown_angle != given_angle:
        raise ValueError("modelled example circle_theorem verification failed: angles in the same segment")

    if rng.random() < 0.5:
        c_label, d_label = f"{given_angle}°", "x°"
        ask = "angle ADB, x"
    else:
        c_label, d_label = "x°", f"{given_angle}°"
        ask = "angle ACB, x"

    teaching_steps = [
        "Angles in the same segment theorem: if two points are on the same arc of a circle, the angles "
        "they make when looking at the same chord are always equal - both angles are said to be "
        "\"subtended by\" that chord.",
        "Here C and D both sit on the same arc and both look at the chord AB, so angle ACB and angle "
        "ADB must be equal to each other, no matter where exactly C and D sit on that arc.",
        f"Since one of the two angles is given as {given_angle}°, the other one, x, must equal it "
        "exactly - there's no further calculation needed once you recognise the theorem applies.",
        f"x = {given_angle}°.",
    ]
    worked_calculation = [
        "angle ADB = angle ACB (angles in the same segment)",
        f"x = {given_angle}°",
    ]
    return ModelledExample(
        topic_id="circle_theorems",
        tier=Tier.HIGHER,
        prompt=(
            "A, B, C, and D are points on a circle, where C and D are on the same arc, both subtending "
            f"the chord AB. Find {ask}."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{unknown_angle}°",
        diagram=DiagramSpec(
            kind="circle_same_segment",
            params={"angle_c_label": c_label, "angle_d_label": d_label},
        ),
    )


def _modelled_alternate_segment(rng: random.Random) -> ModelledExample:
    given_angle = rng.randint(20, 80)
    unknown_angle = given_angle
    if unknown_angle != given_angle:
        raise ValueError("modelled example circle_theorem verification failed: alternate segment theorem")

    if rng.random() < 0.5:
        tangent_label, segment_label = f"{given_angle}°", "x°"
        ask = "angle QRP, x"
    else:
        tangent_label, segment_label = "x°", f"{given_angle}°"
        ask = "the angle between the tangent and the chord PQ, x"

    teaching_steps = [
        "The alternate segment theorem links a tangent to a circle with a chord drawn from the same "
        "point of contact: the angle between the tangent and the chord is always equal to the angle "
        "the chord makes at a point on the far arc - the \"alternate segment\", meaning the segment on "
        "the other side of the chord from the angle between the tangent and chord.",
        "Here the tangent touches the circle at P and PQ is the chord, so the angle between them (at P) "
        "is equal to angle QRP, the angle the same chord PQ makes at R, a point on the alternate segment.",
        f"Since one of these two equal angles is given as {given_angle}°, the other, x, must equal it "
        "exactly.",
        f"x = {given_angle}°.",
    ]
    worked_calculation = [
        "tangent-chord angle at P = angle QRP (alternate segment theorem)",
        f"x = {given_angle}°",
    ]
    return ModelledExample(
        topic_id="circle_theorems",
        tier=Tier.HIGHER,
        prompt=(
            "PQ is a chord of a circle, with a tangent at P. R is a point on "
            f"the circle in the alternate segment. Find {ask}."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{unknown_angle}°",
        diagram=DiagramSpec(
            kind="circle_alternate_segment",
            params={"tangent_angle_label": tangent_label, "segment_angle_label": segment_label},
        ),
    )


_MODELLED_SHAPES = [
    _modelled_angle_at_centre,
    _modelled_angle_in_semicircle,
    _modelled_cyclic_quadrilateral,
    _modelled_two_tangents,
    _modelled_angle_same_segment,
    _modelled_alternate_segment,
]


def generate_modelled_example_circle_theorem(tier: Tier, rng: random.Random) -> ModelledExample:
    shape = rng.choice(_MODELLED_SHAPES)
    return shape(rng)


TOPIC_CIRCLE_THEOREMS = TopicDefinition(
    id="circle_theorems",
    display_name="Circle Theorems",
    description="Apply circle theorems (angle at centre, angle in a semicircle, cyclic quadrilaterals, tangents, angles in the same segment, alternate segment) to find a missing angle.",
    generate=generate_circle_theorem,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_circle_theorem,
)
