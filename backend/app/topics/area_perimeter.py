import random

import sympy as sp

from app.core.models import Question, Tier
from app.topics.base import TopicDefinition

TOPIC_ID = "area_perimeter"


def _fmt_pi_term(coeff) -> str:
    coeff = sp.Rational(coeff)
    if coeff == 1:
        return "π"
    if coeff.is_Integer:
        return f"{int(coeff)}π"
    return f"({coeff.p}/{coeff.q})π"


def _generate_rectangle(rng: random.Random) -> Question:
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
        topic_id=TOPIC_ID,
        tier=Tier.FOUNDATION,
        prompt=f"A rectangle has length {length} cm and width {width} cm. Find its {measure}.",
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"rectangle:{length}:{width}:{measure}",
    )


def _generate_triangle(rng: random.Random) -> Question:
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
        topic_id=TOPIC_ID,
        tier=Tier.FOUNDATION,
        prompt=f"A triangle has base {base} cm and height {height} cm. Find its area.",
        solution_steps=tuple(steps),
        final_answer=f"{area_str} cm²",
        dedup_key=f"triangle:{base}:{height}",
    )


def _generate_composite_rectangles(rng: random.Random) -> Question:
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
        topic_id=TOPIC_ID,
        tier=Tier.FOUNDATION,
        prompt=(
            f"An L-shaped room is formed by taking a rectangle {outer_w} cm by {outer_h} cm "
            f"and removing a corner rectangle {inner_w} cm by {inner_h} cm. Find the area of the room."
        ),
        solution_steps=tuple(steps),
        final_answer=f"{total_area} cm²",
        dedup_key=f"composite_rect:{outer_w}:{outer_h}:{inner_w}:{inner_h}",
    )


def _generate_circle(rng: random.Random) -> Question:
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
        topic_id=TOPIC_ID,
        tier=Tier.HIGHER,
        prompt=f"A circle has radius {radius} cm. Find its {measure} in terms of π.",
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"circle:{radius}:{measure}",
    )


def _generate_semicircle_compound(rng: random.Random) -> Question:
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
        topic_id=TOPIC_ID,
        tier=Tier.HIGHER,
        prompt=(
            f"A shape is made from a rectangle {width} cm by {height} cm with a semicircle "
            f"of diameter {width} cm attached to one side. Find the total area, correct to 3 s.f."
        ),
        solution_steps=tuple(steps),
        final_answer=f"≈ {approx_total} cm²",
        dedup_key=f"semicircle_compound:{width}:{height}",
    )


def _generate_subtract_compound(rng: random.Random) -> Question:
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
        topic_id=TOPIC_ID,
        tier=Tier.HIGHER,
        prompt=(
            f"A rectangular sheet of metal {outer_w} cm by {outer_h} cm has a rectangular hole "
            f"{inner_w} cm by {inner_h} cm cut from its centre. Find the remaining area."
        ),
        solution_steps=tuple(steps),
        final_answer=f"{total_area} cm²",
        dedup_key=f"subtract_compound:{outer_w}:{outer_h}:{inner_w}:{inner_h}",
    )


def generate(tier: Tier, rng: random.Random) -> Question:
    if tier == Tier.FOUNDATION:
        shape = rng.choice(["rectangle", "triangle", "composite_rectangles"])
        if shape == "rectangle":
            return _generate_rectangle(rng)
        if shape == "triangle":
            return _generate_triangle(rng)
        return _generate_composite_rectangles(rng)
    shape = rng.choice(["circle", "semicircle_compound", "subtract_compound"])
    if shape == "circle":
        return _generate_circle(rng)
    if shape == "semicircle_compound":
        return _generate_semicircle_compound(rng)
    return _generate_subtract_compound(rng)


TOPIC = TopicDefinition(
    id=TOPIC_ID,
    display_name="Area & Perimeter",
    description="Areas and perimeters of rectangles, triangles, circles, and compound shapes.",
    generate=generate,
)
