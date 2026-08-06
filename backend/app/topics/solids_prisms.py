import random

from app.core.models import DiagramSpec, ModelledExample, Question, Tier
from app.topics.base import TopicDefinition

SECTION = "geometry"
GROUP = "3D Shapes"

# A small set of integer Pythagorean triples used as the right-angled
# cross-section of the triangular prism, scaled by a random small integer
# factor so the two legs and hypotenuse are always whole numbers (needed for
# a clean surface-area calculation without introducing surds).
_TRIPLES = [(3, 4, 5), (6, 8, 10), (5, 12, 13), (9, 12, 15), (8, 15, 17)]


def _measure_label(measure: str) -> str:
    return "volume" if measure == "volume" else "surface area"


# ---------------------------------------------------------------------------
# Cuboid
# ---------------------------------------------------------------------------


def generate_volume_surface_area_cuboid(tier: Tier, rng: random.Random) -> Question:
    length = rng.randint(3, 15)
    width = rng.randint(3, 15)
    height = rng.randint(3, 15)
    measure = rng.choice(["volume", "surface_area"])

    volume = length * width * height
    # Independent check: recompute the product in a different grouping/order
    # (width x height x length) rather than length x width x height.
    volume_check = width * height * length
    if volume_check != volume:
        raise ValueError("volume_surface_area_cuboid volume verification failed")

    surface_area = 2 * (length * width + length * height + width * height)
    # Independent check: sum all 6 individual face areas one at a time,
    # rather than the compact 2 x (lw + lh + wh) formula used for the
    # displayed steps - a genuinely different computation path.
    face_areas = [
        length * width, length * width,
        length * height, length * height,
        width * height, width * height,
    ]
    surface_area_check = sum(face_areas)
    if surface_area_check != surface_area:
        raise ValueError("volume_surface_area_cuboid surface area verification failed")

    if measure == "volume":
        steps = [
            f"Volume = length × width × height = {length} × {width} × {height} = {volume} cm³",
        ]
        answer = f"{volume} cm³"
    else:
        steps = [
            f"Surface area = 2 × (lw + lh + wh) "
            f"= 2 × ({length}×{width} + {length}×{height} + {width}×{height})",
            f"= 2 × ({length * width} + {length * height} + {width * height}) = {surface_area} cm²",
        ]
        answer = f"{surface_area} cm²"

    return Question(
        topic_id="volume_surface_area_cuboid",
        tier=Tier.FOUNDATION,
        prompt=(
            f"A cuboid has length {length} cm, width {width} cm and height {height} cm. "
            f"Find its {_measure_label(measure)}."
        ),
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"cuboid:{length}:{width}:{height}:{measure}",
        diagram=DiagramSpec(
            kind="cuboid",
            params={
                "width_label": f"{width} cm",
                "height_label": f"{height} cm",
                "length_label": f"{length} cm",
            },
        ),
    )


def generate_modelled_example_volume_surface_area_cuboid(tier: Tier, rng: random.Random) -> ModelledExample:
    length = rng.randint(3, 15)
    width = rng.randint(3, 15)
    height = rng.randint(3, 15)
    measure = rng.choice(["volume", "surface_area"])

    volume = length * width * height
    volume_check = width * height * length
    if volume_check != volume:
        raise ValueError("modelled example volume_surface_area_cuboid volume verification failed")

    surface_area = 2 * (length * width + length * height + width * height)
    face_areas = [
        length * width, length * width,
        length * height, length * height,
        width * height, width * height,
    ]
    surface_area_check = sum(face_areas)
    if surface_area_check != surface_area:
        raise ValueError("modelled example volume_surface_area_cuboid surface area verification failed")

    if measure == "volume":
        teaching_steps = [
            "A cuboid's volume tells you how much space it fills, measured in cubic units - "
            "picture it built from unit cubes stacked into layers, where each layer is a "
            "rectangle of unit squares and there are several identical layers stacked on top "
            "of each other.",
            f"Each layer covers length × width = {length} × {width} = {length * width} unit "
            "squares.",
            f"There are {height} such layers stacked up (one for every cm of height), so "
            f"multiply by the height: {length * width} × {height} = {volume}.",
            f"Since each unit cube is 1 cm³, the total volume is {volume} cm³.",
        ]
        worked_calculation = [
            "Volume = length × width × height",
            f"= {length} × {width} × {height}",
            f"= {volume} cm³",
        ]
        answer = f"{volume} cm³"
    else:
        teaching_steps = [
            "A cuboid has 6 rectangular faces, arranged in 3 matching pairs (front/back, "
            "top/bottom, left/right) - the surface area is the total area of all 6 faces "
            "added together.",
            f"The front and back faces each measure {length} cm by {width} cm, giving "
            f"2 × ({length} × {width}) = {2 * length * width} cm² between the two of them.",
            f"The top and bottom faces each measure {length} cm by {height} cm, giving "
            f"2 × ({length} × {height}) = {2 * length * height} cm².",
            f"The two side faces each measure {width} cm by {height} cm, giving "
            f"2 × ({width} × {height}) = {2 * width * height} cm².",
            f"Add all three pairs together: {2 * length * width} + {2 * length * height} + "
            f"{2 * width * height} = {surface_area} cm².",
        ]
        worked_calculation = [
            "Surface area = 2 × (lw + lh + wh)",
            f"= 2 × ({length * width} + {length * height} + {width * height})",
            f"= {surface_area} cm²",
        ]
        answer = f"{surface_area} cm²"

    return ModelledExample(
        topic_id="volume_surface_area_cuboid",
        tier=Tier.FOUNDATION,
        prompt=(
            f"A cuboid has length {length} cm, width {width} cm and height {height} cm. "
            f"Find its {_measure_label(measure)}."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
        diagram=DiagramSpec(
            kind="cuboid",
            params={
                "width_label": f"{width} cm",
                "height_label": f"{height} cm",
                "length_label": f"{length} cm",
            },
        ),
    )


# ---------------------------------------------------------------------------
# Cube
# ---------------------------------------------------------------------------


def generate_volume_surface_area_cube(tier: Tier, rng: random.Random) -> Question:
    side = rng.randint(2, 20)
    measure = rng.choice(["volume", "surface_area"])

    volume = side ** 3
    # Independent check: recompute the volume via repeated addition of the
    # base face's area, side times - a genuinely different (loop-based)
    # computation path from the exponentiation used for the displayed steps.
    volume_check = sum(side * side for _ in range(side))
    if volume_check != volume:
        raise ValueError("volume_surface_area_cube volume verification failed")

    surface_area = 6 * side ** 2
    # Independent check: sum 6 individual face areas rather than the compact
    # 6 x side^2 formula.
    face_areas = [side * side for _ in range(6)]
    surface_area_check = sum(face_areas)
    if surface_area_check != surface_area:
        raise ValueError("volume_surface_area_cube surface area verification failed")

    if measure == "volume":
        steps = [f"Volume = side³ = {side}³ = {volume} cm³"]
        answer = f"{volume} cm³"
    else:
        steps = [f"Surface area = 6 × side² = 6 × {side}² = 6 × {side ** 2} = {surface_area} cm²"]
        answer = f"{surface_area} cm²"

    return Question(
        topic_id="volume_surface_area_cube",
        tier=Tier.FOUNDATION,
        prompt=f"A cube has side length {side} cm. Find its {_measure_label(measure)}.",
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"cube:{side}:{measure}",
        diagram=DiagramSpec(
            kind="cuboid",
            params={
                "width_label": f"{side} cm",
                "height_label": f"{side} cm",
                "length_label": f"{side} cm",
                "is_cube": True,
            },
        ),
    )


def generate_modelled_example_volume_surface_area_cube(tier: Tier, rng: random.Random) -> ModelledExample:
    side = rng.randint(2, 20)
    measure = rng.choice(["volume", "surface_area"])

    volume = side ** 3
    volume_check = sum(side * side for _ in range(side))
    if volume_check != volume:
        raise ValueError("modelled example volume_surface_area_cube volume verification failed")

    surface_area = 6 * side ** 2
    face_areas = [side * side for _ in range(6)]
    surface_area_check = sum(face_areas)
    if surface_area_check != surface_area:
        raise ValueError("modelled example volume_surface_area_cube surface area verification failed")

    if measure == "volume":
        teaching_steps = [
            "A cube is just a cuboid where every edge is the same length, so its volume "
            "formula simplifies from length x width x height down to side x side x side, "
            "written as side³.",
            f"Here every edge is {side} cm, so the volume is {side} × {side} × {side}.",
            f"Multiplying those three equal numbers together gives {volume}.",
            f"So the cube's volume is {volume} cm³.",
        ]
        worked_calculation = [
            "Volume = side³",
            f"= {side}³",
            f"= {volume} cm³",
        ]
        answer = f"{volume} cm³"
    else:
        teaching_steps = [
            "A cube has 6 identical square faces, since every edge is the same length - so "
            "the surface area is just 6 lots of one face's area.",
            f"One face is a {side} cm by {side} cm square, with area {side}² = {side ** 2} cm².",
            f"There are 6 identical faces, so multiply by 6: 6 × {side ** 2} = {surface_area}.",
            f"So the total surface area is {surface_area} cm².",
        ]
        worked_calculation = [
            "Surface area = 6 × side²",
            f"= 6 × {side}²",
            f"= {surface_area} cm²",
        ]
        answer = f"{surface_area} cm²"

    return ModelledExample(
        topic_id="volume_surface_area_cube",
        tier=Tier.FOUNDATION,
        prompt=f"A cube has side length {side} cm. Find its {_measure_label(measure)}.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
        diagram=DiagramSpec(
            kind="cuboid",
            params={
                "width_label": f"{side} cm",
                "height_label": f"{side} cm",
                "length_label": f"{side} cm",
                "is_cube": True,
            },
        ),
    )


# ---------------------------------------------------------------------------
# Triangular prism
# ---------------------------------------------------------------------------


def _triangular_prism_values(rng: random.Random):
    p0, q0, hyp0 = rng.choice(_TRIPLES)
    scale = rng.randint(1, 3)
    p, q, hyp = p0 * scale, q0 * scale, hyp0 * scale
    length = rng.randint(4, 20)
    measure = rng.choice(["volume", "surface_area"])
    return p, q, hyp, length, measure


def generate_volume_surface_area_triangular_prism(tier: Tier, rng: random.Random) -> Question:
    p, q, hyp, length, measure = _triangular_prism_values(rng)

    # Sanity check: the cross-section really is right-angled.
    if hyp ** 2 != p ** 2 + q ** 2:
        raise ValueError("volume_surface_area_triangular_prism triangle is not right-angled")
    if (p * q) % 2 != 0:
        raise ValueError("volume_surface_area_triangular_prism cross-section area is not a whole number")

    cross_section_area = p * q // 2
    volume = cross_section_area * length
    # Independent check: recompute the volume in a different grouping/order
    # (multiply length in first, then halve) rather than
    # cross_section_area * length.
    volume_check = (length * p * q) // 2
    if volume_check != volume:
        raise ValueError("volume_surface_area_triangular_prism volume verification failed")

    surface_area = p * q + (p + q + hyp) * length
    # Independent check: sum the two triangular ends and all three
    # rectangular faces individually, rather than factoring the perimeter
    # out as (p + q + hyp) x length.
    end_faces = 2 * cross_section_area
    rect_p = p * length
    rect_q = q * length
    rect_hyp = hyp * length
    surface_area_check = end_faces + rect_p + rect_q + rect_hyp
    if surface_area_check != surface_area:
        raise ValueError("volume_surface_area_triangular_prism surface area verification failed")

    if measure == "volume":
        steps = [
            f"Cross-section area = (1/2) × {p} × {q} = {cross_section_area} cm²",
            f"Volume = cross-section area × length = {cross_section_area} × {length} = {volume} cm³",
        ]
        answer = f"{volume} cm³"
    else:
        steps = [
            f"Area of the two triangular ends = 2 × (1/2) × {p} × {q} = {p * q} cm²",
            f"Perimeter of the triangular cross-section = {p} + {q} + {hyp} = {p + q + hyp} cm",
            f"Area of the three rectangular faces = {p + q + hyp} × {length} = {(p + q + hyp) * length} cm²",
            f"Surface area = {p * q} + {(p + q + hyp) * length} = {surface_area} cm²",
        ]
        answer = f"{surface_area} cm²"

    return Question(
        topic_id="volume_surface_area_triangular_prism",
        tier=Tier.FOUNDATION,
        prompt=(
            f"A triangular prism has a right-angled triangular cross-section with sides {p} cm "
            f"and {q} cm (hypotenuse {hyp} cm), and length {length} cm. Find its "
            f"{_measure_label(measure)}."
        ),
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"tri_prism:{p}:{q}:{hyp}:{length}:{measure}",
        diagram=DiagramSpec(
            kind="triangular_prism",
            params={
                "base_label": f"{p} cm",
                "triangle_height_label": f"{q} cm",
                "length_label": f"{length} cm",
            },
        ),
    )


def generate_modelled_example_volume_surface_area_triangular_prism(
    tier: Tier, rng: random.Random
) -> ModelledExample:
    p, q, hyp, length, measure = _triangular_prism_values(rng)

    if hyp ** 2 != p ** 2 + q ** 2:
        raise ValueError("modelled example volume_surface_area_triangular_prism triangle is not right-angled")
    if (p * q) % 2 != 0:
        raise ValueError(
            "modelled example volume_surface_area_triangular_prism cross-section area is not a whole number"
        )

    cross_section_area = p * q // 2
    volume = cross_section_area * length
    volume_check = (length * p * q) // 2
    if volume_check != volume:
        raise ValueError("modelled example volume_surface_area_triangular_prism volume verification failed")

    surface_area = p * q + (p + q + hyp) * length
    end_faces = 2 * cross_section_area
    rect_p = p * length
    rect_q = q * length
    rect_hyp = hyp * length
    surface_area_check = end_faces + rect_p + rect_q + rect_hyp
    if surface_area_check != surface_area:
        raise ValueError("modelled example volume_surface_area_triangular_prism surface area verification failed")

    if measure == "volume":
        teaching_steps = [
            "A prism's volume is always the area of its cross-section (the shape you'd see "
            "if you sliced straight through it) multiplied by its length - here the "
            "cross-section is a right-angled triangle.",
            f"The triangle's two shorter sides are {p} cm and {q} cm, at right angles to each other, so "
            f"its area is (1/2) × {p} × {q} = {cross_section_area} cm².",
            f"The prism stretches out {length} cm long, so multiply the cross-section area by "
            f"the length: {cross_section_area} × {length} = {volume}.",
            f"So the volume of the prism is {volume} cm³.",
        ]
        worked_calculation = [
            "Volume = cross-section area × length",
            f"= {cross_section_area} × {length}",
            f"= {volume} cm³",
        ]
        answer = f"{volume} cm³"
    else:
        teaching_steps = [
            "A triangular prism's surface area is made up of two triangular end faces (the "
            "front and back) plus three rectangular faces running along its length, one for "
            "each side of the triangle.",
            f"The two triangular ends together have area 2 × (1/2) × {p} × {q} = {p * q} cm², "
            "since two identical right-angled triangles make a rectangle.",
            f"The three sides of the triangle - the two shorter sides and the hypotenuse - have total "
            f"length {p} + {q} + {hyp} = {p + q + hyp} cm; each becomes a rectangular face that "
            f"long and {length} cm wide (the prism's length), giving a combined area of "
            f"{p + q + hyp} × {length} = {(p + q + hyp) * length} cm².",
            f"Add the triangular ends and the rectangular faces together: {p * q} + "
            f"{(p + q + hyp) * length} = {surface_area} cm².",
        ]
        worked_calculation = [
            f"Triangular ends = {p * q} cm²",
            f"Rectangular faces = ({p} + {q} + {hyp}) × {length} = {(p + q + hyp) * length} cm²",
            f"Surface area = {p * q} + {(p + q + hyp) * length} = {surface_area} cm²",
        ]
        answer = f"{surface_area} cm²"

    return ModelledExample(
        topic_id="volume_surface_area_triangular_prism",
        tier=Tier.FOUNDATION,
        prompt=(
            f"A triangular prism has a right-angled triangular cross-section with sides {p} cm "
            f"and {q} cm (hypotenuse {hyp} cm), and length {length} cm. Find its "
            f"{_measure_label(measure)}."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
        diagram=DiagramSpec(
            kind="triangular_prism",
            params={
                "base_label": f"{p} cm",
                "triangle_height_label": f"{q} cm",
                "length_label": f"{length} cm",
            },
        ),
    )


# ---------------------------------------------------------------------------
# Topic definitions
# ---------------------------------------------------------------------------

TOPIC_CUBOID = TopicDefinition(
    id="volume_surface_area_cuboid",
    display_name="Volume & Surface Area of a Cuboid",
    description="Find the volume or surface area of a cuboid given its length, width and height.",
    generate=generate_volume_surface_area_cuboid,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_volume_surface_area_cuboid,
)

TOPIC_CUBE = TopicDefinition(
    id="volume_surface_area_cube",
    display_name="Volume & Surface Area of a Cube",
    description="Find the volume or surface area of a cube given its side length.",
    generate=generate_volume_surface_area_cube,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_volume_surface_area_cube,
)

TOPIC_TRIANGULAR_PRISM = TopicDefinition(
    id="volume_surface_area_triangular_prism",
    display_name="Volume & Surface Area of a Triangular Prism",
    description=(
        "Find the volume or surface area of a triangular prism with a right-angled "
        "triangular cross-section."
    ),
    generate=generate_volume_surface_area_triangular_prism,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_volume_surface_area_triangular_prism,
)
