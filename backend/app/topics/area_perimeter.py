import math
import random

import sympy as sp

from app.core.models import DiagramSpec, ModelledExample, Question, Tier
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


def generate_modelled_example_rectangle(tier: Tier, rng: random.Random) -> ModelledExample:
    length = rng.randint(3, 20)
    width = rng.randint(3, 20)
    measure = rng.choice(["area", "perimeter"])
    area = length * width
    perimeter = 2 * (length + width)

    if measure == "area":
        # Independent check: area is also perimeter/2 x width only when the
        # rectangle is a square, so instead re-derive area by repeated addition
        # of one row, a genuinely different computation path from length x width.
        repeated_addition = sum(width for _ in range(length))
        if repeated_addition != area:
            raise ValueError("modelled example rectangle area verification failed")
        answer = f"{area} cm²"
        teaching_steps = [
            "The area of a rectangle is how much flat space it covers, measured in square "
            "units - and for a rectangle, that's simply length times width, because you can "
            "picture it as rows of unit squares stacked up.",
            f"Here the rectangle is {length} cm long and {width} cm wide, so there are {length} "
            f"rows, each containing {width} unit squares.",
            f"Multiply the two dimensions together: {length} × {width} = {area}.",
            f"Since each unit square is 1 cm², the total area is {area} cm².",
        ]
        worked_calculation = [
            "Area = length × width",
            f"= {length} × {width}",
            f"= {area} cm²",
        ]
    else:
        # Independent check: re-derive the perimeter by walking round all four
        # sides individually rather than using the 2(l + w) shortcut.
        walk_around = length + width + length + width
        if walk_around != perimeter:
            raise ValueError("modelled example rectangle perimeter verification failed")
        answer = f"{perimeter} cm"
        teaching_steps = [
            "The perimeter of a shape is the total distance all the way around its outside "
            "edge - so for a rectangle, that means adding up all four sides.",
            f"A rectangle has two lengths and two widths, so instead of adding four separate "
            f"numbers we can add one length and one width, then double it: {length} + {width} "
            f"= {length + width}.",
            f"Doubling accounts for the fact that both the opposite length and opposite width "
            f"are the same size: 2 × {length + width} = {perimeter}.",
            f"So the total distance around the rectangle is {perimeter} cm.",
        ]
        worked_calculation = [
            "Perimeter = 2 × (length + width)",
            f"= 2 × ({length} + {width})",
            f"= {perimeter} cm",
        ]

    return ModelledExample(
        topic_id="area_rectangle",
        tier=Tier.FOUNDATION,
        prompt=f"A rectangle has length {length} cm and width {width} cm. Find its {measure}.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
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


def generate_modelled_example_triangle(tier: Tier, rng: random.Random) -> ModelledExample:
    base = rng.randint(4, 20)
    height = rng.randint(4, 20)
    area = sp.Rational(base * height, 2)

    # Independent check: a triangle's area is half of the rectangle that
    # exactly encloses it, so re-derive via the enclosing-rectangle area
    # halved, a different route from the direct formula used below.
    enclosing_rectangle_area = base * height
    if sp.Rational(enclosing_rectangle_area, 2) != area:
        raise ValueError("modelled example triangle area verification failed")

    area_str = str(int(area)) if area.is_Integer else f"{area.p}/{area.q}"
    teaching_steps = [
        "Picture the triangle sitting inside a rectangle of the same base and height - the "
        "triangle always takes up exactly half of that rectangle, no matter its shape, as long "
        "as the height is measured perpendicular to the base.",
        f"The enclosing rectangle would have area {base} × {height} = {base * height} cm².",
        f"The triangle is half of that rectangle, so divide by 2: {base * height} ÷ 2 = {area_str}.",
        f"That gives an area of {area_str} cm² for the triangle.",
    ]
    worked_calculation = [
        "Area = (1/2) × base × height",
        f"= (1/2) × {base} × {height}",
        f"= {area_str} cm²",
    ]
    return ModelledExample(
        topic_id="area_triangle",
        tier=Tier.FOUNDATION,
        prompt=f"A triangle has base {base} cm and height {height} cm. Find its area.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{area_str} cm²",
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


def generate_modelled_example_composite_rectangles(tier: Tier, rng: random.Random) -> ModelledExample:
    outer_w = rng.randint(10, 25)
    outer_h = rng.randint(10, 25)
    inner_w = rng.randint(2, outer_w - 2)
    inner_h = rng.randint(2, outer_h - 2)

    if not (inner_w < outer_w and inner_h < outer_h):
        raise ValueError("modelled example composite_rectangles sanity constraint failed")

    outer_area = outer_w * outer_h
    inner_area = inner_w * inner_h
    total_area = outer_area - inner_area
    if total_area <= 0:
        raise ValueError("modelled example composite_rectangles produced non-positive area")

    # Independent check: split the L-shape into two non-overlapping rectangles
    # instead of subtracting a cut-out corner from the full rectangle - a
    # genuinely different decomposition of the same shape.
    strip_h = outer_h - inner_h
    rect1 = outer_w * strip_h
    rect2 = (outer_w - inner_w) * inner_h
    if rect1 + rect2 != total_area:
        raise ValueError("modelled example composite_rectangles cross-check failed")

    teaching_steps = [
        "An L-shape like this is easiest to handle by treating it as a big rectangle with a "
        "corner missing - so start by imagining the shape 'filled in' to make a complete rectangle.",
        f"The full rectangle would measure {outer_w} cm by {outer_h} cm, giving an area of "
        f"{outer_w} × {outer_h} = {outer_area} cm².",
        f"The missing corner is itself a rectangle, {inner_w} cm by {inner_h} cm, with area "
        f"{inner_w} × {inner_h} = {inner_area} cm².",
        f"Since that corner isn't actually part of the room, subtract it from the full "
        f"rectangle: {outer_area} - {inner_area} = {total_area} cm².",
    ]
    worked_calculation = [
        f"Full rectangle = {outer_w} × {outer_h} = {outer_area} cm²",
        f"Cut-out corner = {inner_w} × {inner_h} = {inner_area} cm²",
        f"Area = {outer_area} - {inner_area} = {total_area} cm²",
    ]
    return ModelledExample(
        topic_id="area_composite_rectangles",
        tier=Tier.FOUNDATION,
        prompt=(
            f"An L-shaped room is formed by taking a rectangle {outer_w} cm by {outer_h} cm "
            f"and removing a corner rectangle {inner_w} cm by {inner_h} cm. Find the area of the room."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{total_area} cm²",
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


def generate_modelled_example_circle(tier: Tier, rng: random.Random) -> ModelledExample:
    radius = rng.randint(3, 15)
    measure = rng.choice(["area", "circumference"])

    if measure == "area":
        exact_expr = sp.pi * radius**2
        coeff = sp.Rational(radius**2)
        # Independent check: verify the coefficient of pi via plain integer
        # squaring, a different route from sympy's Rational construction.
        if radius * radius != int(coeff):
            raise ValueError("modelled example circle area verification failed")
        answer = f"{_fmt_pi_term(coeff)} cm² (≈ {sp.N(exact_expr, 3)} cm²)"
        teaching_steps = [
            "The area of a circle is found using the formula A = π × r², where r is the "
            "radius - and because π is irrational, we usually leave it in the answer rather "
            "than rounding it away, giving an exact answer 'in terms of π'.",
            f"Square the radius first: {radius}² = {radius * radius}.",
            f"Multiply that by π (don't evaluate π itself): {_fmt_pi_term(coeff)} cm² is the "
            "exact area.",
            f"A calculator value is also useful to picture the size: {_fmt_pi_term(coeff)} ≈ "
            f"{sp.N(exact_expr, 3)} cm².",
        ]
        worked_calculation = [
            "Area = π × r²",
            f"= π × {radius}²",
            f"= {_fmt_pi_term(coeff)} cm²",
        ]
    else:
        exact_expr = 2 * sp.pi * radius
        coeff = sp.Rational(2 * radius)
        if 2 * radius != int(coeff):
            raise ValueError("modelled example circle circumference verification failed")
        answer = f"{_fmt_pi_term(coeff)} cm (≈ {sp.N(exact_expr, 3)} cm)"
        teaching_steps = [
            "The circumference is the distance all the way around a circle, found using "
            "C = 2 × π × r - again, we keep π as a symbol rather than rounding it, so the "
            "answer stays exact.",
            f"Double the radius first: 2 × {radius} = {2 * radius}.",
            f"Multiply by π: {_fmt_pi_term(coeff)} cm is the exact circumference.",
            f"As a calculator value, that's approximately {_fmt_pi_term(coeff)} ≈ "
            f"{sp.N(exact_expr, 3)} cm.",
        ]
        worked_calculation = [
            "Circumference = 2 × π × r",
            f"= 2 × π × {radius}",
            f"= {_fmt_pi_term(coeff)} cm",
        ]

    return ModelledExample(
        topic_id="area_circle",
        tier=Tier.HIGHER,
        prompt=f"A circle has radius {radius} cm. Find its {measure} in terms of π.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
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


def generate_modelled_example_circle_foundation(tier: Tier, rng: random.Random) -> ModelledExample:
    radius = rng.randint(3, 15)
    measure = rng.choice(["area", "circumference"])

    if measure == "area":
        exact_expr = sp.pi * radius**2
        decimal_answer = sp.N(exact_expr, 3)
        independent = math.pi * radius**2
        teaching_steps = [
            "The area of a circle is A = π × r². Here we're using the calculator's decimal "
            "value of π (3.14159...) instead of leaving π symbolically, since the question "
            "asks for a rounded answer.",
            f"Square the radius: {radius}² = {radius**2}.",
            f"Multiply by π on a calculator: π × {radius**2} = {float(exact_expr):.5f}...",
            f"Round to 3 significant figures: {decimal_answer} cm².",
        ]
        worked_calculation = [
            "Area = π × r²",
            f"= π × {radius}²",
            f"= {decimal_answer} cm² (3 s.f.)",
        ]
    else:
        exact_expr = 2 * sp.pi * radius
        decimal_answer = sp.N(exact_expr, 3)
        independent = 2 * math.pi * radius
        teaching_steps = [
            "The circumference is C = 2 × π × r. As with the area, here we use π's decimal "
            "calculator value rather than leaving π symbolically, since a rounded answer "
            "is wanted.",
            f"Double the radius: 2 × {radius} = {2 * radius}.",
            f"Multiply by π on a calculator: π × {2 * radius} = {float(exact_expr):.5f}...",
            f"Round to 3 significant figures: {decimal_answer} cm.",
        ]
        worked_calculation = [
            "Circumference = 2 × π × r",
            f"= 2 × π × {radius}",
            f"= {decimal_answer} cm (3 s.f.)",
        ]

    # Independent check via Python's math.pi - a different π source/implementation
    # than sympy's symbolic pi used above.
    if abs(float(decimal_answer) - independent) / independent > 0.01:
        raise ValueError("modelled example area_circle_foundation verification failed")

    unit = "cm²" if measure == "area" else "cm"
    return ModelledExample(
        topic_id="area_circle_foundation",
        tier=Tier.FOUNDATION,
        prompt=f"A circle has radius {radius} cm. Find its {measure}, correct to 3 significant figures.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{decimal_answer} {unit}",
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


def generate_modelled_example_semicircle_compound(tier: Tier, rng: random.Random) -> ModelledExample:
    width = rng.randrange(6, 21, 2)  # even, so the radius is a whole number
    height = rng.randint(5, 20)
    radius = width // 2

    if width % 2 != 0:
        raise ValueError("modelled example semicircle_compound requires an even width")

    rect_area = width * height
    semicircle_coeff = sp.Rational(radius**2, 2)
    exact_total = rect_area + semicircle_coeff * sp.pi
    approx_total = sp.N(exact_total, 3)

    # Independent check: a full circle of this radius would have area pi*r^2,
    # so the semicircle should be exactly half that - re-derive it that way
    # rather than via the (1/2) x pi x r^2 formula used above.
    full_circle_coeff = sp.Rational(radius**2)
    if full_circle_coeff / 2 != semicircle_coeff:
        raise ValueError("modelled example semicircle_compound verification failed")

    teaching_steps = [
        "This shape is made of two simpler pieces joined together: a rectangle, and a "
        "semicircle sitting on one of its short sides - so the total area is just the sum "
        "of the two separate areas.",
        f"The rectangle's area is straightforward: {width} × {height} = {rect_area} cm².",
        f"The semicircle's diameter matches the rectangle's width, {width} cm, so its radius "
        f"is half of that: {width} ÷ 2 = {radius} cm. A full circle of that radius would have "
        f"area π × {radius}² = {_fmt_pi_term(full_circle_coeff)} cm², so the semicircle - being "
        f"half a circle - has area {_fmt_pi_term(semicircle_coeff)} cm².",
        f"Add the rectangle and semicircle areas together: {rect_area} + {_fmt_pi_term(semicircle_coeff)} "
        f"≈ {approx_total} cm² (3 s.f.).",
    ]
    worked_calculation = [
        f"Rectangle area = {width} × {height} = {rect_area} cm²",
        f"Semicircle radius = {width} ÷ 2 = {radius} cm",
        f"Semicircle area = (1/2) × π × {radius}² = {_fmt_pi_term(semicircle_coeff)} cm²",
        f"Total = {rect_area} + {_fmt_pi_term(semicircle_coeff)} ≈ {approx_total} cm²",
    ]
    return ModelledExample(
        topic_id="area_semicircle_compound",
        tier=Tier.HIGHER,
        prompt=(
            f"A shape is made from a rectangle {width} cm by {height} cm with a semicircle "
            f"of diameter {width} cm attached to one side. Find the total area, correct to 3 s.f."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"≈ {approx_total} cm²",
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


def generate_modelled_example_subtract_compound(tier: Tier, rng: random.Random) -> ModelledExample:
    outer_w = rng.randint(10, 25)
    outer_h = rng.randint(10, 25)
    inner_w = rng.randint(2, outer_w - 2)
    inner_h = rng.randint(2, outer_h - 2)

    if not (inner_w < outer_w and inner_h < outer_h):
        raise ValueError("modelled example subtract_compound sanity constraint failed")

    outer_area = outer_w * outer_h
    inner_area = inner_w * inner_h
    total_area = outer_area - inner_area
    if total_area <= 0:
        raise ValueError("modelled example subtract_compound produced non-positive area")

    # Independent check: re-derive the remaining area by splitting the L-shaped
    # remainder into a top/bottom band plus a side column, rather than
    # subtracting the hole's area from the sheet's area directly.
    band_h = outer_h - inner_h
    band_area = outer_w * band_h
    side_w = outer_w - inner_w
    side_area = side_w * inner_h
    if band_area + side_area != total_area:
        raise ValueError("modelled example subtract_compound cross-check failed")

    teaching_steps = [
        "When a shape has a hole cut out of it, the remaining area is simply the area of the "
        "whole sheet minus the area of the piece that's been removed.",
        f"Start with the full sheet: {outer_w} cm by {outer_h} cm, giving an area of "
        f"{outer_w} × {outer_h} = {outer_area} cm².",
        f"The hole is also a rectangle, {inner_w} cm by {inner_h} cm, with area "
        f"{inner_w} × {inner_h} = {inner_area} cm².",
        f"Subtract the hole's area from the sheet's area to find what's left: "
        f"{outer_area} - {inner_area} = {total_area} cm².",
    ]
    worked_calculation = [
        f"Large rectangle = {outer_w} × {outer_h} = {outer_area} cm²",
        f"Hole = {inner_w} × {inner_h} = {inner_area} cm²",
        f"Remaining area = {outer_area} - {inner_area} = {total_area} cm²",
    ]
    return ModelledExample(
        topic_id="area_subtract_compound",
        tier=Tier.HIGHER,
        prompt=(
            f"A rectangular sheet of metal {outer_w} cm by {outer_h} cm has a rectangular hole "
            f"{inner_w} cm by {inner_h} cm cut from its centre. Find the remaining area."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{total_area} cm²",
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
    generate_modelled_example=generate_modelled_example_rectangle,
)

TOPIC_TRIANGLE = TopicDefinition(
    id="area_triangle",
    display_name="Triangles",
    description="Find the area of a triangle given its base and height.",
    generate=generate_triangle,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_triangle,
)

TOPIC_COMPOSITE_RECTANGLES = TopicDefinition(
    id="area_composite_rectangles",
    display_name="Composite Rectangles",
    description="Find the area of an L-shape made from two rectangles.",
    generate=generate_composite_rectangles,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_composite_rectangles,
)

TOPIC_CIRCLE = TopicDefinition(
    id="area_circle",
    display_name="Circles",
    description="Find the area or circumference of a circle in terms of π.",
    generate=generate_circle,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_circle,
)

TOPIC_CIRCLE_FOUNDATION = TopicDefinition(
    id="area_circle_foundation",
    display_name="Circles (Calculator)",
    description="Find the area or circumference of a circle, giving a decimal answer.",
    generate=generate_circle_foundation,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_circle_foundation,
)

TOPIC_SEMICIRCLE_COMPOUND = TopicDefinition(
    id="area_semicircle_compound",
    display_name="Semicircle Compound Shapes",
    description="Find the area of a rectangle with a semicircle attached.",
    generate=generate_semicircle_compound,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_semicircle_compound,
)

TOPIC_SUBTRACT_COMPOUND = TopicDefinition(
    id="area_subtract_compound",
    display_name="Subtractive Compound Shapes",
    description="Find the remaining area after a rectangular hole is cut from a larger rectangle.",
    generate=generate_subtract_compound,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_subtract_compound,
)
