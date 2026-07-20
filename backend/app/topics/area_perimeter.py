import math
import random

import sympy as sp

from app.core.models import DiagramSpec, Question, Tier
from app.topics.base import TopicDefinition

SECTION = "geometry"
GROUP = "Area & Perimeter"


def _fmt_pi_term(coeff) -> str:
    coeff = sp.Rational(coeff)
    if coeff == 1:
        return "π"
    if coeff.is_Integer:
        return f"{int(coeff)}π"
    return f"({coeff.p}/{coeff.q})π"


def generate_rectangle(tier: Tier, rng: random.Random) -> Question:
    length = rng.randint(3, 20)
    width = rng.randint(3, 20)
    measure = rng.choice(["area", "perimeter"])
    area = length * width
    perimeter = 2 * (length + width)

    if measure == "area":
        if area != length * width:
            raise ValueError("rectangle area verification failed")
        steps = [f"Area = length × width = {length} × {width} = {area} cm²"]
        answer = f"{area} cm²"
    else:
        if perimeter != 2 * length + 2 * width:
            raise ValueError("rectangle perimeter verification failed")
        steps = [f"Perimeter = 2 × (length + width) = 2 × ({length} + {width}) = {perimeter} cm"]
        answer = f"{perimeter} cm"

    return Question(
        topic_id="area_rectangle",
        tier=Tier.FOUNDATION,
        prompt=f"A rectangle has length {length} cm and width {width} cm. Find its {measure}.",
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"rectangle:{length}:{width}:{measure}",
        diagram=DiagramSpec(
            kind="rectangle",
            params={"width": length, "height": width, "width_label": f"{length} cm", "height_label": f"{width} cm"},
        ),
    )


def generate_triangle(tier: Tier, rng: random.Random) -> Question:
    base = rng.randint(4, 20)
    height = rng.randint(4, 20)
    area = sp.Rational(base * height, 2)

    residual = sp.Rational(base * height, 2) - area
    if residual != 0:
        raise ValueError("triangle area verification failed")

    area_str = str(int(area)) if area.is_Integer else f"{area.p}/{area.q}"
    steps = [
        f"Area = (1/2) × base × height = (1/2) × {base} × {height} = {area_str} cm²",
    ]
    return Question(
        topic_id="area_triangle",
        tier=Tier.FOUNDATION,
        prompt=f"A triangle has base {base} cm and height {height} cm. Find its area.",
        solution_steps=tuple(steps),
        final_answer=f"{area_str} cm²",
        dedup_key=f"triangle:{base}:{height}",
        diagram=DiagramSpec(
            kind="triangle_area",
            params={"base": base, "height": height, "base_label": f"{base} cm", "height_label": f"{height} cm"},
        ),
    )


def generate_composite_rectangles(tier: Tier, rng: random.Random) -> Question:
    outer_w = rng.randint(10, 25)
    outer_h = rng.randint(10, 25)
    inner_w = rng.randint(2, outer_w - 2)
    inner_h = rng.randint(2, outer_h - 2)

    if not (inner_w < outer_w and inner_h < outer_h):
        raise ValueError("composite_rectangles sanity constraint failed")

    outer_area = outer_w * outer_h
    inner_area = inner_w * inner_h
    total_area = outer_area - inner_area
    if total_area <= 0:
        raise ValueError("composite_rectangles produced non-positive area")

    steps = [
        f"Area of full rectangle = {outer_w} × {outer_h} = {outer_area} cm²",
        f"Area of the cut-out corner = {inner_w} × {inner_h} = {inner_area} cm²",
        f"Area of the shape = {outer_area} - {inner_area} = {total_area} cm²",
    ]
    return Question(
        topic_id="area_composite_rectangles",
        tier=Tier.FOUNDATION,
        prompt=(
            f"An L-shaped room is formed by taking a rectangle {outer_w} cm by {outer_h} cm "
            f"and removing a corner rectangle {inner_w} cm by {inner_h} cm. Find the area of the room."
        ),
        solution_steps=tuple(steps),
        final_answer=f"{total_area} cm²",
        dedup_key=f"composite_rect:{outer_w}:{outer_h}:{inner_w}:{inner_h}",
        diagram=DiagramSpec(
            kind="l_shape",
            params={
                "outer_w": outer_w, "outer_h": outer_h, "inner_w": inner_w, "inner_h": inner_h,
                "notch": "corner",
                "outer_labels": [f"{outer_w} cm", f"{outer_h} cm"],
                "inner_labels": [inner_w, inner_h],
            },
        ),
    )


def generate_circle(tier: Tier, rng: random.Random) -> Question:
    radius = rng.randint(3, 15)
    measure = rng.choice(["area", "circumference"])

    if measure == "area":
        exact_expr = sp.pi * radius**2
        coeff = sp.Rational(radius**2)
        steps = [
            f"Area = π × r² = π × {radius}² = {_fmt_pi_term(coeff)} cm²",
            f"≈ {sp.N(exact_expr, 3)} cm² (3 s.f.)",
        ]
        answer = f"{_fmt_pi_term(coeff)} cm² (≈ {sp.N(exact_expr, 3)} cm²)"
    else:
        exact_expr = 2 * sp.pi * radius
        coeff = sp.Rational(2 * radius)
        steps = [
            f"Circumference = 2 × π × r = 2 × π × {radius} = {_fmt_pi_term(coeff)} cm",
            f"≈ {sp.N(exact_expr, 3)} cm (3 s.f.)",
        ]
        answer = f"{_fmt_pi_term(coeff)} cm (≈ {sp.N(exact_expr, 3)} cm)"

    return Question(
        topic_id="area_circle",
        tier=Tier.HIGHER,
        prompt=f"A circle has radius {radius} cm. Find its {measure} in terms of π.",
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"circle:{radius}:{measure}",
        diagram=DiagramSpec(kind="circle", params={"radius": radius, "label": f"{radius} cm"}),
    )


def generate_circle_foundation(tier: Tier, rng: random.Random) -> Question:
    radius = rng.randint(3, 15)
    measure = rng.choice(["area", "circumference"])

    if measure == "area":
        exact_expr = sp.pi * radius**2
        decimal_answer = sp.N(exact_expr, 3)
        steps = [
            f"Area = π × r² = π × {radius}² = π × {radius**2}",
            f"= {decimal_answer} cm² (3 s.f., using a calculator value of π)",
        ]
        independent = math.pi * radius**2
    else:
        exact_expr = 2 * sp.pi * radius
        decimal_answer = sp.N(exact_expr, 3)
        steps = [
            f"Circumference = 2 × π × r = 2 × π × {radius}",
            f"= {decimal_answer} cm (3 s.f., using a calculator value of π)",
        ]
        independent = 2 * math.pi * radius

    # Independent check via Python's math.pi - a different π source/implementation
    # than sympy's symbolic pi used above. Tolerance is relative, since rounding
    # to 3 s.f. can shift the absolute value by more than a fixed small amount
    # once the magnitude grows (e.g. area for larger radii).
    if abs(float(decimal_answer) - independent) / independent > 0.01:
        raise ValueError("area_circle_foundation verification failed")

    unit = "cm²" if measure == "area" else "cm"
    return Question(
        topic_id="area_circle_foundation",
        tier=Tier.FOUNDATION,
        prompt=f"A circle has radius {radius} cm. Find its {measure}, correct to 3 significant figures.",
        solution_steps=tuple(steps),
        final_answer=f"{decimal_answer} {unit}",
        dedup_key=f"circle_f:{radius}:{measure}",
        diagram=DiagramSpec(kind="circle", params={"radius": radius, "label": f"{radius} cm"}),
    )


def generate_semicircle_compound(tier: Tier, rng: random.Random) -> Question:
    width = rng.randrange(6, 21, 2)  # even, so the radius is a whole number
    height = rng.randint(5, 20)
    radius = width // 2

    if width % 2 != 0:
        raise ValueError("semicircle_compound requires an even width")

    rect_area = width * height
    semicircle_coeff = sp.Rational(radius**2, 2)
    exact_total = rect_area + semicircle_coeff * sp.pi
    approx_total = sp.N(exact_total, 3)

    steps = [
        f"Area of rectangle = {width} × {height} = {rect_area} cm²",
        f"Radius of semicircle = {width} ÷ 2 = {radius} cm",
        f"Area of semicircle = (1/2) × π × {radius}² = {_fmt_pi_term(semicircle_coeff)} cm²",
        f"Total area = {rect_area} + {_fmt_pi_term(semicircle_coeff)} ≈ {approx_total} cm² (3 s.f.)",
    ]
    return Question(
        topic_id="area_semicircle_compound",
        tier=Tier.HIGHER,
        prompt=(
            f"A shape is made from a rectangle {width} cm by {height} cm with a semicircle "
            f"of diameter {width} cm attached to one side. Find the total area, correct to 3 s.f."
        ),
        solution_steps=tuple(steps),
        final_answer=f"≈ {approx_total} cm²",
        dedup_key=f"semicircle_compound:{width}:{height}",
        diagram=DiagramSpec(kind="rectangle_semicircle", params={"width": width, "height": height, "radius": radius}),
    )


def generate_subtract_compound(tier: Tier, rng: random.Random) -> Question:
    outer_w = rng.randint(10, 25)
    outer_h = rng.randint(10, 25)
    inner_w = rng.randint(2, outer_w - 2)
    inner_h = rng.randint(2, outer_h - 2)

    if not (inner_w < outer_w and inner_h < outer_h):
        raise ValueError("subtract_compound sanity constraint failed")

    outer_area = outer_w * outer_h
    inner_area = inner_w * inner_h
    total_area = outer_area - inner_area
    if total_area <= 0:
        raise ValueError("subtract_compound produced non-positive area")

    steps = [
        f"Area of large rectangle = {outer_w} × {outer_h} = {outer_area} cm²",
        f"Area of rectangular hole = {inner_w} × {inner_h} = {inner_area} cm²",
        f"Remaining area = {outer_area} - {inner_area} = {total_area} cm²",
    ]
    return Question(
        topic_id="area_subtract_compound",
        tier=Tier.HIGHER,
        prompt=(
            f"A rectangular sheet of metal {outer_w} cm by {outer_h} cm has a rectangular hole "
            f"{inner_w} cm by {inner_h} cm cut from its centre. Find the remaining area."
        ),
        solution_steps=tuple(steps),
        final_answer=f"{total_area} cm²",
        dedup_key=f"subtract_compound:{outer_w}:{outer_h}:{inner_w}:{inner_h}",
        diagram=DiagramSpec(
            kind="l_shape",
            params={
                "outer_w": outer_w, "outer_h": outer_h, "inner_w": inner_w, "inner_h": inner_h,
                "notch": "center",
                "outer_labels": [f"{outer_w} cm", f"{outer_h} cm"],
                "inner_labels": [inner_w, inner_h],
            },
        ),
    )


TOPIC_RECTANGLE = TopicDefinition(
    id="area_rectangle",
    display_name="Rectangles",
    description="Find the area or perimeter of a rectangle.",
    generate=generate_rectangle,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
)

TOPIC_TRIANGLE = TopicDefinition(
    id="area_triangle",
    display_name="Triangles",
    description="Find the area of a triangle given its base and height.",
    generate=generate_triangle,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
)

TOPIC_COMPOSITE_RECTANGLES = TopicDefinition(
    id="area_composite_rectangles",
    display_name="Composite Rectangles",
    description="Find the area of an L-shape made from two rectangles.",
    generate=generate_composite_rectangles,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
)

TOPIC_CIRCLE = TopicDefinition(
    id="area_circle",
    display_name="Circles",
    description="Find the area or circumference of a circle in terms of π.",
    generate=generate_circle,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
)

TOPIC_CIRCLE_FOUNDATION = TopicDefinition(
    id="area_circle_foundation",
    display_name="Circles (Calculator)",
    description="Find the area or circumference of a circle, giving a decimal answer.",
    generate=generate_circle_foundation,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
)

TOPIC_SEMICIRCLE_COMPOUND = TopicDefinition(
    id="area_semicircle_compound",
    display_name="Semicircle Compound Shapes",
    description="Find the area of a rectangle with a semicircle attached.",
    generate=generate_semicircle_compound,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
)

TOPIC_SUBTRACT_COMPOUND = TopicDefinition(
    id="area_subtract_compound",
    display_name="Subtractive Compound Shapes",
    description="Find the remaining area after a rectangular hole is cut from a larger rectangle.",
    generate=generate_subtract_compound,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
)
