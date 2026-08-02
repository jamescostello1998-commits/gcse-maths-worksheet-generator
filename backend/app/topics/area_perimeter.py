import math
import random

import sympy as sp

from app.core.models import DiagramSpec, ModelledExample, Question, Tier
from app.topics.base import TopicDefinition
from app.topics.rounding import pick_rounding

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
                "inner_labels": [f"{inner_w} cm", f"{inner_h} cm"],
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
                "inner_labels": [f"{inner_w} cm", f"{inner_h} cm"],
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
    rounding = pick_rounding(rng)

    if measure == "area":
        exact_expr = sp.pi * radius**2
        independent = math.pi * radius**2
        decimal_answer = format(rounding.round_fn(independent), "f")
        steps = [
            f"Area = π × r² = π × {radius}² = π × {radius**2}",
            f"= {decimal_answer} cm² ({rounding.short}, using a calculator value of π)",
        ]
    else:
        exact_expr = 2 * sp.pi * radius
        independent = 2 * math.pi * radius
        decimal_answer = format(rounding.round_fn(independent), "f")
        steps = [
            f"Circumference = 2 × π × r = 2 × π × {radius}",
            f"= {decimal_answer} cm ({rounding.short}, using a calculator value of π)",
        ]

    # Independent check via Python's math.pi (used for `independent`, and
    # hence for the rounded/displayed answer) against sympy's own symbolic
    # pi - a different π source/implementation. Compares full precision
    # (unrounded) values, so the tolerance can stay tight regardless of
    # which display precision was randomly chosen.
    if independent <= 0 or abs(float(sp.N(exact_expr, 15)) - independent) / independent > 1e-9:
        raise ValueError("area_circle_foundation verification failed")

    unit = "cm²" if measure == "area" else "cm"
    return Question(
        topic_id="area_circle_foundation",
        tier=Tier.FOUNDATION,
        prompt=f"A circle has radius {radius} cm. Find its {measure}, correct to {rounding.phrase}.",
        solution_steps=tuple(steps),
        final_answer=f"{decimal_answer} {unit}",
        dedup_key=f"circle_f:{radius}:{measure}",
        diagram=DiagramSpec(kind="circle", params={"radius": radius, "label": f"{radius} cm"}),
    )


def generate_modelled_example_circle_foundation(tier: Tier, rng: random.Random) -> ModelledExample:
    radius = rng.randint(3, 15)
    measure = rng.choice(["area", "circumference"])
    rounding = pick_rounding(rng)

    if measure == "area":
        exact_expr = sp.pi * radius**2
        independent = math.pi * radius**2
        decimal_answer = format(rounding.round_fn(independent), "f")
        teaching_steps = [
            "The area of a circle is A = π × r². Here we're using the calculator's decimal "
            "value of π (3.14159...) instead of leaving π symbolically, since the question "
            "asks for a rounded answer.",
            f"Square the radius: {radius}² = {radius**2}.",
            f"Multiply by π on a calculator: π × {radius**2} = {float(exact_expr):.5f}...",
            f"Round to {rounding.phrase}: {decimal_answer} cm².",
        ]
        worked_calculation = [
            "Area = π × r²",
            f"= π × {radius}²",
            f"= {decimal_answer} cm² ({rounding.short})",
        ]
    else:
        exact_expr = 2 * sp.pi * radius
        independent = 2 * math.pi * radius
        decimal_answer = format(rounding.round_fn(independent), "f")
        teaching_steps = [
            "The circumference is C = 2 × π × r. As with the area, here we use π's decimal "
            "calculator value rather than leaving π symbolically, since a rounded answer "
            "is wanted.",
            f"Double the radius: 2 × {radius} = {2 * radius}.",
            f"Multiply by π on a calculator: π × {2 * radius} = {float(exact_expr):.5f}...",
            f"Round to {rounding.phrase}: {decimal_answer} cm.",
        ]
        worked_calculation = [
            "Circumference = 2 × π × r",
            f"= 2 × π × {radius}",
            f"= {decimal_answer} cm ({rounding.short})",
        ]

    # Independent check via Python's math.pi against sympy's own symbolic pi -
    # compares full precision, so the tolerance stays tight regardless of
    # which display precision was randomly chosen.
    if independent <= 0 or abs(float(sp.N(exact_expr, 15)) - independent) / independent > 1e-9:
        raise ValueError("modelled example area_circle_foundation verification failed")

    unit = "cm²" if measure == "area" else "cm"
    return ModelledExample(
        topic_id="area_circle_foundation",
        tier=Tier.FOUNDATION,
        prompt=f"A circle has radius {radius} cm. Find its {measure}, correct to {rounding.phrase}.",
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
        tier=Tier.FOUNDATION,
        prompt=(
            f"A shape is made from a rectangle {width} cm by {height} cm with a semicircle "
            f"of diameter {width} cm attached to one side. Find the total area, correct to 3 s.f."
        ),
        solution_steps=tuple(steps),
        final_answer=f"≈ {approx_total} cm²",
        dedup_key=f"semicircle_compound:{width}:{height}",
        diagram=DiagramSpec(
            kind="rectangle_semicircle",
            params={
                "width": width, "height": height, "radius": radius,
                "width_label": f"{width} cm", "height_label": f"{height} cm",
            },
        ),
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
        tier=Tier.FOUNDATION,
        prompt=(
            f"A shape is made from a rectangle {width} cm by {height} cm with a semicircle "
            f"of diameter {width} cm attached to one side. Find the total area, correct to 3 s.f."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"≈ {approx_total} cm²",
        diagram=DiagramSpec(
            kind="rectangle_semicircle",
            params={
                "width": width, "height": height, "radius": radius,
                "width_label": f"{width} cm", "height_label": f"{height} cm",
            },
        ),
    )


def generate_semicircle_compound_higher(tier: Tier, rng: random.Random) -> Question:
    width = rng.randrange(6, 21, 2)  # even, so the radius is a whole number
    height = rng.randint(5, 20)
    radius = width // 2

    if width % 2 != 0:
        raise ValueError("semicircle_compound_higher requires an even width")

    rect_area = width * height
    semicircle_coeff = sp.Rational(radius**2, 2)

    # Independent check: a full circle of this radius would have area pi*r^2,
    # so the semicircle should be exactly half that.
    full_circle_coeff = sp.Rational(radius**2)
    if full_circle_coeff / 2 != semicircle_coeff:
        raise ValueError("semicircle_compound_higher verification failed")

    pi_term = _fmt_pi_term(semicircle_coeff)
    steps = [
        f"Area of rectangle = {width} × {height} = {rect_area} cm²",
        f"Radius of semicircle = {width} ÷ 2 = {radius} cm",
        f"Area of semicircle = (1/2) × π × {radius}² = {pi_term} cm²",
        f"Total area = {rect_area} + {pi_term} cm² (exact form)",
    ]
    return Question(
        topic_id="area_semicircle_compound_higher",
        tier=Tier.HIGHER,
        prompt=(
            f"A shape is made from a rectangle {width} cm by {height} cm with a semicircle "
            f"of diameter {width} cm attached to one side. Find the total area, giving your "
            "answer in terms of π."
        ),
        solution_steps=tuple(steps),
        final_answer=f"({rect_area} + {pi_term}) cm²",
        dedup_key=f"semicircle_compound_h:{width}:{height}",
        diagram=DiagramSpec(
            kind="rectangle_semicircle",
            params={
                "width": width, "height": height, "radius": radius,
                "width_label": f"{width} cm", "height_label": f"{height} cm",
            },
        ),
    )


def generate_modelled_example_semicircle_compound_higher(tier: Tier, rng: random.Random) -> ModelledExample:
    width = rng.randrange(6, 21, 2)
    height = rng.randint(5, 20)
    radius = width // 2

    if width % 2 != 0:
        raise ValueError("modelled example semicircle_compound_higher requires an even width")

    rect_area = width * height
    semicircle_coeff = sp.Rational(radius**2, 2)

    full_circle_coeff = sp.Rational(radius**2)
    if full_circle_coeff / 2 != semicircle_coeff:
        raise ValueError("modelled example semicircle_compound_higher verification failed")

    pi_term = _fmt_pi_term(semicircle_coeff)
    teaching_steps = [
        "This shape is made of a rectangle and a semicircle joined together, so the total area is "
        "the sum of the two separate areas - and because the question asks for an exact answer, "
        "π is kept as a symbol throughout rather than rounded to a decimal.",
        f"The rectangle's area is straightforward: {width} × {height} = {rect_area} cm².",
        f"The semicircle's diameter matches the rectangle's width, {width} cm, so its radius is "
        f"half of that: {width} ÷ 2 = {radius} cm. A full circle of that radius would have area "
        f"π × {radius}² = {_fmt_pi_term(full_circle_coeff)} cm², so the semicircle - being half a "
        f"circle - has area {pi_term} cm².",
        f"Add the two areas together, keeping π as a symbol: {rect_area} + {pi_term} cm². Since "
        "the two terms (a whole number and a multiple of π) can't be combined into one, this exact "
        "form is the final answer - do not round it to a decimal.",
    ]
    worked_calculation = [
        f"Rectangle area = {width} × {height} = {rect_area} cm²",
        f"Semicircle radius = {width} ÷ 2 = {radius} cm",
        f"Semicircle area = (1/2) × π × {radius}² = {pi_term} cm²",
        f"Total = {rect_area} + {pi_term} cm² (exact form)",
    ]
    return ModelledExample(
        topic_id="area_semicircle_compound_higher",
        tier=Tier.HIGHER,
        prompt=(
            f"A shape is made from a rectangle {width} cm by {height} cm with a semicircle "
            f"of diameter {width} cm attached to one side. Find the total area, giving your "
            "answer in terms of π."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"({rect_area} + {pi_term}) cm²",
        diagram=DiagramSpec(
            kind="rectangle_semicircle",
            params={
                "width": width, "height": height, "radius": radius,
                "width_label": f"{width} cm", "height_label": f"{height} cm",
            },
        ),
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
                "inner_labels": [f"{inner_w} cm", f"{inner_h} cm"],
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
                "inner_labels": [f"{inner_w} cm", f"{inner_h} cm"],
            },
        ),
    )


def generate_subtract_compound_foundation(tier: Tier, rng: random.Random) -> Question:
    outer_w = rng.randint(6, 15)
    outer_h = rng.randint(6, 15)
    inner_w = rng.randint(2, outer_w - 2)
    inner_h = rng.randint(2, outer_h - 2)

    if not (inner_w < outer_w and inner_h < outer_h):
        raise ValueError("subtract_compound_foundation sanity constraint failed")

    outer_area = outer_w * outer_h
    inner_area = inner_w * inner_h
    total_area = outer_area - inner_area
    if total_area <= 0:
        raise ValueError("subtract_compound_foundation produced non-positive area")

    steps = [
        f"Area of large rectangle = {outer_w} × {outer_h} = {outer_area} cm²",
        f"Area of rectangular hole = {inner_w} × {inner_h} = {inner_area} cm²",
        f"Remaining area = {outer_area} - {inner_area} = {total_area} cm²",
    ]
    return Question(
        topic_id="area_subtract_compound_foundation",
        tier=Tier.FOUNDATION,
        prompt=(
            f"A rectangular sheet of card {outer_w} cm by {outer_h} cm has a rectangular hole "
            f"{inner_w} cm by {inner_h} cm cut from its centre. Find the remaining area."
        ),
        solution_steps=tuple(steps),
        final_answer=f"{total_area} cm²",
        dedup_key=f"subtract_compound_f:{outer_w}:{outer_h}:{inner_w}:{inner_h}",
        diagram=DiagramSpec(
            kind="l_shape",
            params={
                "outer_w": outer_w, "outer_h": outer_h, "inner_w": inner_w, "inner_h": inner_h,
                "notch": "center",
                "outer_labels": [f"{outer_w} cm", f"{outer_h} cm"],
                "inner_labels": [f"{inner_w} cm", f"{inner_h} cm"],
            },
        ),
    )


def generate_modelled_example_subtract_compound_foundation(tier: Tier, rng: random.Random) -> ModelledExample:
    outer_w = rng.randint(6, 15)
    outer_h = rng.randint(6, 15)
    inner_w = rng.randint(2, outer_w - 2)
    inner_h = rng.randint(2, outer_h - 2)

    if not (inner_w < outer_w and inner_h < outer_h):
        raise ValueError("modelled example subtract_compound_foundation sanity constraint failed")

    outer_area = outer_w * outer_h
    inner_area = inner_w * inner_h
    total_area = outer_area - inner_area
    if total_area <= 0:
        raise ValueError("modelled example subtract_compound_foundation produced non-positive area")

    # Independent check: re-derive the remaining area by splitting the L-shaped
    # remainder into a top/bottom band plus a side column, rather than
    # subtracting the hole's area from the sheet's area directly.
    band_h = outer_h - inner_h
    band_area = outer_w * band_h
    side_w = outer_w - inner_w
    side_area = side_w * inner_h
    if band_area + side_area != total_area:
        raise ValueError("modelled example subtract_compound_foundation cross-check failed")

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
        topic_id="area_subtract_compound_foundation",
        tier=Tier.FOUNDATION,
        prompt=(
            f"A rectangular sheet of card {outer_w} cm by {outer_h} cm has a rectangular hole "
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
                "inner_labels": [f"{inner_w} cm", f"{inner_h} cm"],
            },
        ),
    )


def _shoelace_area(vertices: list[tuple[int, int]]) -> int:
    """Shoelace formula on integer vertex coordinates - an independent
    coordinate-geometry cross-check (matching the convention already used in
    vectors.py/triangle_rules.py), distinct from a direct formula restatement."""
    n = len(vertices)
    total = sum(
        vertices[i][0] * vertices[(i + 1) % n][1] - vertices[(i + 1) % n][0] * vertices[i][1]
        for i in range(n)
    )
    return abs(total) // 2


def generate_area_parallelogram(tier: Tier, rng: random.Random) -> Question:
    base = rng.randint(5, 20)
    height = rng.randint(3, 15)
    area = base * height

    # Shearing the top edge by any offset doesn't change the shoelace area, so
    # this is a genuinely different route from the base x height formula below.
    slant = rng.randint(1, base)
    if _shoelace_area([(0, 0), (base, 0), (base + slant, height), (slant, height)]) != area:
        raise ValueError("area_parallelogram verification failed")

    steps = [f"Area = base × height = {base} × {height} = {area} cm²"]
    return Question(
        topic_id="area_parallelogram",
        tier=Tier.FOUNDATION,
        prompt=f"A parallelogram has a base of {base} cm and a perpendicular height of {height} cm. Find its area.",
        solution_steps=tuple(steps),
        final_answer=f"{area} cm²",
        dedup_key=f"parallelogram:{base}:{height}",
        diagram=DiagramSpec(
            kind="parallelogram",
            params={"base": base, "height": height, "base_label": f"{base} cm", "height_label": f"{height} cm"},
        ),
    )


def generate_modelled_example_area_parallelogram(tier: Tier, rng: random.Random) -> ModelledExample:
    base = rng.randint(5, 20)
    height = rng.randint(3, 15)
    area = base * height

    slant = rng.randint(1, base)
    if _shoelace_area([(0, 0), (base, 0), (base + slant, height), (slant, height)]) != area:
        raise ValueError("modelled example area_parallelogram verification failed")

    teaching_steps = [
        "A parallelogram's area is the SAME as a rectangle with the same base and perpendicular "
        "height - imagine slicing a triangle off one slanted end and sliding it across to the "
        "other end, which turns the parallelogram into a rectangle without changing its area.",
        f"The base is {base} cm and the perpendicular height (measured straight up from the base, "
        f"not along the slanted side) is {height} cm.",
        f"Area = base × height = {base} × {height} = {area} cm².",
    ]
    worked_calculation = [f"Area = {base} × {height}", f"= {area} cm²"]
    return ModelledExample(
        topic_id="area_parallelogram",
        tier=Tier.FOUNDATION,
        prompt=f"A parallelogram has a base of {base} cm and a perpendicular height of {height} cm. Find its area.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{area} cm²",
        diagram=DiagramSpec(
            kind="parallelogram",
            params={"base": base, "height": height, "base_label": f"{base} cm", "height_label": f"{height} cm"},
        ),
    )


def generate_area_trapezium(tier: Tier, rng: random.Random) -> Question:
    a = rng.randint(4, 12)
    b = rng.randint(a + 2, 20)
    height = rng.randint(3, 12)
    while ((a + b) * height) % 2 != 0:
        height = rng.randint(3, 12)
    area = (a + b) * height // 2

    slant = rng.randint(0, b - a)
    if _shoelace_area([(0, 0), (b, 0), (slant + a, height), (slant, height)]) != area:
        raise ValueError("area_trapezium verification failed")

    steps = [f"Area = ½ × (a + b) × height = ½ × ({a} + {b}) × {height} = {area} cm²"]
    return Question(
        topic_id="area_trapezium",
        tier=Tier.FOUNDATION,
        prompt=(
            f"A trapezium has parallel sides of length {a} cm and {b} cm, and a perpendicular "
            f"height of {height} cm. Find its area."
        ),
        solution_steps=tuple(steps),
        final_answer=f"{area} cm²",
        dedup_key=f"trapezium:{a}:{b}:{height}",
        diagram=DiagramSpec(
            kind="trapezium",
            params={"a": a, "b": b, "height": height, "a_label": f"{a} cm", "b_label": f"{b} cm", "height_label": f"{height} cm"},
        ),
    )


def generate_modelled_example_area_trapezium(tier: Tier, rng: random.Random) -> ModelledExample:
    a = rng.randint(4, 12)
    b = rng.randint(a + 2, 20)
    height = rng.randint(3, 12)
    while ((a + b) * height) % 2 != 0:
        height = rng.randint(3, 12)
    area = (a + b) * height // 2

    slant = rng.randint(0, b - a)
    if _shoelace_area([(0, 0), (b, 0), (slant + a, height), (slant, height)]) != area:
        raise ValueError("modelled example area_trapezium verification failed")

    teaching_steps = [
        "A trapezium has one pair of parallel sides, usually of different lengths - the formula "
        "averages those two lengths first, then multiplies by the perpendicular height, as if the "
        "trapezium were a rectangle with that 'average' width.",
        f"The parallel sides are {a} cm and {b} cm, so their average is ({a} + {b}) ÷ 2.",
        f"Multiply that average by the perpendicular height, {height} cm: "
        f"Area = ½ × ({a} + {b}) × {height} = {area} cm².",
    ]
    worked_calculation = [f"Area = ½ × ({a} + {b}) × {height}", f"= {area} cm²"]
    return ModelledExample(
        topic_id="area_trapezium",
        tier=Tier.FOUNDATION,
        prompt=(
            f"A trapezium has parallel sides of length {a} cm and {b} cm, and a perpendicular "
            f"height of {height} cm. Find its area."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{area} cm²",
        diagram=DiagramSpec(
            kind="trapezium",
            params={"a": a, "b": b, "height": height, "a_label": f"{a} cm", "b_label": f"{b} cm", "height_label": f"{height} cm"},
        ),
    )


def _mixed_compound_values(rng: random.Random):
    width = rng.randint(10, 20)
    height = rng.randint(6, 15)
    roof_height = rng.randint(3, 10)
    cut_radius = rng.randint(2, min(width, height) // 2)
    return width, height, roof_height, cut_radius


def generate_area_mixed_compound(tier: Tier, rng: random.Random) -> Question:
    width, height, roof_height, cut_radius = _mixed_compound_values(rng)

    rect_area = width * height
    triangle_area = sp.Rational(width * roof_height, 2)
    cut_area_exact = sp.pi * cut_radius**2 / 4
    total_exact = rect_area + triangle_area - cut_area_exact
    decimal_answer = sp.N(total_exact, 3)

    # Independent check: recompute the quarter-circle cut via Python's math.pi -
    # a different π implementation than sympy's symbolic pi used above.
    independent_cut = math.pi * cut_radius**2 / 4
    independent_total = rect_area + float(triangle_area) - independent_cut
    if abs(float(decimal_answer) - independent_total) / independent_total > 0.01:
        raise ValueError("area_mixed_compound verification failed")

    cut_area_decimal = sp.N(cut_area_exact, 3)
    steps = [
        f"Rectangle area = {width} × {height} = {rect_area} cm²",
        f"Triangle roof area = ½ × {width} × {roof_height} = {triangle_area} cm²",
        f"Quarter-circle cut area = (π × {cut_radius}²) ÷ 4 ≈ {cut_area_decimal} cm²",
        f"Total area = {rect_area} + {triangle_area} - {cut_area_decimal} ≈ {decimal_answer} cm²",
    ]
    return Question(
        topic_id="area_mixed_compound",
        tier=Tier.HIGHER,
        prompt=(
            f"A shape is made from a rectangle {width} cm by {height} cm, with a triangular roof of "
            f"height {roof_height} cm on top, and a quarter-circle of radius {cut_radius} cm cut from "
            "one bottom corner. Find the total area, correct to 3 significant figures."
        ),
        solution_steps=tuple(steps),
        final_answer=f"{decimal_answer} cm²",
        dedup_key=f"mixed_compound:{width}:{height}:{roof_height}:{cut_radius}",
        diagram=DiagramSpec(
            kind="mixed_compound",
            params={
                "width": width, "height": height, "roof_height": roof_height, "cut_radius": cut_radius,
                "width_label": f"{width} cm", "height_label": f"{height} cm",
                "roof_label": f"{roof_height} cm", "cut_label": f"{cut_radius} cm",
            },
        ),
    )


def generate_modelled_example_area_mixed_compound(tier: Tier, rng: random.Random) -> ModelledExample:
    width, height, roof_height, cut_radius = _mixed_compound_values(rng)

    rect_area = width * height
    triangle_area = sp.Rational(width * roof_height, 2)
    cut_area_exact = sp.pi * cut_radius**2 / 4
    total_exact = rect_area + triangle_area - cut_area_exact
    decimal_answer = sp.N(total_exact, 3)

    independent_cut = math.pi * cut_radius**2 / 4
    independent_total = rect_area + float(triangle_area) - independent_cut
    if abs(float(decimal_answer) - independent_total) / independent_total > 0.01:
        raise ValueError("modelled example area_mixed_compound verification failed")

    cut_area_decimal = sp.N(cut_area_exact, 3)
    teaching_steps = [
        "A compound shape like this is split into simple pieces you already know the area of, added "
        "together where a piece is present, and subtracted where a piece has been removed.",
        f"The rectangle contributes {width} × {height} = {rect_area} cm².",
        f"The triangular roof adds ½ × {width} × {roof_height} = {triangle_area} cm² on top.",
        f"The quarter-circle cut removes (π × {cut_radius}²) ÷ 4 ≈ {cut_area_decimal} cm² from a corner.",
        f"Total = {rect_area} + {triangle_area} - {cut_area_decimal} ≈ {decimal_answer} cm².",
    ]
    worked_calculation = [
        f"{rect_area} + {triangle_area} - {cut_area_decimal}",
        f"≈ {decimal_answer} cm²",
    ]
    return ModelledExample(
        topic_id="area_mixed_compound",
        tier=Tier.HIGHER,
        prompt=(
            f"A shape is made from a rectangle {width} cm by {height} cm, with a triangular roof of "
            f"height {roof_height} cm on top, and a quarter-circle of radius {cut_radius} cm cut from "
            "one bottom corner. Find the total area, correct to 3 significant figures."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{decimal_answer} cm²",
        diagram=DiagramSpec(
            kind="mixed_compound",
            params={
                "width": width, "height": height, "roof_height": roof_height, "cut_radius": cut_radius,
                "width_label": f"{width} cm", "height_label": f"{height} cm",
                "roof_label": f"{roof_height} cm", "cut_label": f"{cut_radius} cm",
            },
        ),
    )


def _sector_diagram(angle: int, radius: int) -> DiagramSpec:
    return DiagramSpec(kind="sector", params={"angle": angle, "radius_label": f"{radius} cm", "angle_label": f"{angle}°"})


def generate_arc_length_foundation(tier: Tier, rng: random.Random) -> Question:
    radius = rng.randint(3, 15)
    angle = rng.randint(10, 350)
    rounding = pick_rounding(rng)

    exact_expr = sp.Rational(angle, 360) * 2 * sp.pi * radius
    independent = (angle / 360) * 2 * math.pi * radius
    if independent <= 0 or abs(float(sp.N(exact_expr, 15)) - independent) / independent > 1e-9:
        raise ValueError("arc_length_foundation verification failed")

    # Independent cross-check via the sector-area formula: sector area = ½ × arc
    # length × r, so arc length = 2 × sector area ÷ r - a genuinely different
    # formula route from (θ ÷ 360) × 2 × π × r above.
    sector_area_exact = sp.Rational(angle, 360) * sp.pi * radius**2
    arc_from_area = sp.N(2 * sector_area_exact / radius, 6)
    if abs(float(arc_from_area) - float(sp.N(exact_expr, 6))) / float(sp.N(exact_expr, 6)) > 1e-6:
        raise ValueError("arc_length_foundation cross-formula verification failed")

    decimal_answer = format(rounding.round_fn(independent), "f")
    steps = [
        f"Arc length = (θ ÷ 360) × 2 × π × r = ({angle} ÷ 360) × 2 × π × {radius}",
        f"= {decimal_answer} cm ({rounding.short}, using a calculator value of π)",
    ]
    return Question(
        topic_id="arc_length_foundation",
        tier=Tier.FOUNDATION,
        prompt=(
            f"A sector of a circle has radius {radius} cm and angle {angle}°. Find the arc length, "
            f"correct to {rounding.phrase}."
        ),
        solution_steps=tuple(steps),
        final_answer=f"{decimal_answer} cm",
        dedup_key=f"arc_f:{radius}:{angle}",
        diagram=_sector_diagram(angle, radius),
    )


def generate_modelled_example_arc_length_foundation(tier: Tier, rng: random.Random) -> ModelledExample:
    radius = rng.randint(3, 15)
    angle = rng.randint(10, 350)
    rounding = pick_rounding(rng)

    exact_expr = sp.Rational(angle, 360) * 2 * sp.pi * radius
    independent = (angle / 360) * 2 * math.pi * radius
    if independent <= 0 or abs(float(sp.N(exact_expr, 15)) - independent) / independent > 1e-9:
        raise ValueError("modelled example arc_length_foundation verification failed")

    decimal_answer = format(rounding.round_fn(independent), "f")
    teaching_steps = [
        "An arc is just a fraction of the full circumference - work out what fraction of the full "
        "360° the sector's angle takes up, then apply that same fraction to the whole circumference.",
        f"The angle is {angle}°, so the fraction is {angle} ÷ 360.",
        f"The full circumference would be 2 × π × {radius}. Multiply by the fraction: "
        f"({angle} ÷ 360) × 2 × π × {radius} ≈ {decimal_answer} cm.",
    ]
    worked_calculation = [f"({angle} ÷ 360) × 2 × π × {radius}", f"≈ {decimal_answer} cm"]
    return ModelledExample(
        topic_id="arc_length_foundation",
        tier=Tier.FOUNDATION,
        prompt=(
            f"A sector of a circle has radius {radius} cm and angle {angle}°. Find the arc length, "
            f"correct to {rounding.phrase}."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{decimal_answer} cm",
        diagram=_sector_diagram(angle, radius),
    )


def generate_arc_length(tier: Tier, rng: random.Random) -> Question:
    radius = rng.randint(3, 15)
    angle = rng.choice(range(15, 360, 15))

    coeff = sp.Rational(angle, 360) * 2 * radius
    exact_expr = coeff * sp.pi

    sector_area_exact = sp.Rational(angle, 360) * sp.pi * radius**2
    arc_from_area = sp.simplify(2 * sector_area_exact / radius)
    if sp.simplify(arc_from_area - exact_expr) != 0:
        raise ValueError("arc_length verification failed")

    answer = f"{_fmt_pi_term(coeff)} cm"
    steps = [
        f"Arc length = (θ ÷ 360) × 2 × π × r = ({angle} ÷ 360) × 2 × π × {radius}",
        f"= {answer}",
    ]
    return Question(
        topic_id="arc_length",
        tier=Tier.HIGHER,
        prompt=f"A sector of a circle has radius {radius} cm and angle {angle}°. Find the exact arc length, in terms of π.",
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"arc_h:{radius}:{angle}",
        diagram=_sector_diagram(angle, radius),
    )


def generate_modelled_example_arc_length(tier: Tier, rng: random.Random) -> ModelledExample:
    radius = rng.randint(3, 15)
    angle = rng.choice(range(15, 360, 15))

    coeff = sp.Rational(angle, 360) * 2 * radius
    exact_expr = coeff * sp.pi

    sector_area_exact = sp.Rational(angle, 360) * sp.pi * radius**2
    arc_from_area = sp.simplify(2 * sector_area_exact / radius)
    if sp.simplify(arc_from_area - exact_expr) != 0:
        raise ValueError("modelled example arc_length verification failed")

    answer = f"{_fmt_pi_term(coeff)} cm"
    teaching_steps = [
        "Keeping the answer exact means leaving π in the answer rather than using a calculator "
        "decimal value for it - work with the fraction of the circle first, then attach π at the end.",
        f"The angle {angle}° out of 360° gives the fraction {angle}/360.",
        f"Multiply that fraction by the full circumference 2 × π × {radius}, keeping π symbolic "
        f"throughout: {answer}.",
    ]
    worked_calculation = [f"({angle}/360) × 2 × π × {radius}", f"= {answer}"]
    return ModelledExample(
        topic_id="arc_length",
        tier=Tier.HIGHER,
        prompt=f"A sector of a circle has radius {radius} cm and angle {angle}°. Find the exact arc length, in terms of π.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
        diagram=_sector_diagram(angle, radius),
    )


def generate_area_sector_foundation(tier: Tier, rng: random.Random) -> Question:
    radius = rng.randint(3, 15)
    angle = rng.randint(10, 350)
    rounding = pick_rounding(rng)

    exact_expr = sp.Rational(angle, 360) * sp.pi * radius**2
    independent = (angle / 360) * math.pi * radius**2
    if independent <= 0 or abs(float(sp.N(exact_expr, 15)) - independent) / independent > 1e-9:
        raise ValueError("area_sector_foundation verification failed")

    # Independent cross-check via the arc-length formula: area = ½ × arc length × r.
    arc_length_exact = sp.Rational(angle, 360) * 2 * sp.pi * radius
    area_from_arc = sp.N(arc_length_exact * radius / 2, 6)
    if abs(float(area_from_arc) - float(sp.N(exact_expr, 6))) / float(sp.N(exact_expr, 6)) > 1e-6:
        raise ValueError("area_sector_foundation cross-formula verification failed")

    decimal_answer = format(rounding.round_fn(independent), "f")
    steps = [
        f"Area = (θ ÷ 360) × π × r² = ({angle} ÷ 360) × π × {radius}²",
        f"= {decimal_answer} cm² ({rounding.short}, using a calculator value of π)",
    ]
    return Question(
        topic_id="area_sector_foundation",
        tier=Tier.FOUNDATION,
        prompt=(
            f"A sector of a circle has radius {radius} cm and angle {angle}°. Find the area of the "
            f"sector, correct to {rounding.phrase}."
        ),
        solution_steps=tuple(steps),
        final_answer=f"{decimal_answer} cm²",
        dedup_key=f"sector_f:{radius}:{angle}",
        diagram=_sector_diagram(angle, radius),
    )


def generate_modelled_example_area_sector_foundation(tier: Tier, rng: random.Random) -> ModelledExample:
    radius = rng.randint(3, 15)
    angle = rng.randint(10, 350)
    rounding = pick_rounding(rng)

    exact_expr = sp.Rational(angle, 360) * sp.pi * radius**2
    independent = (angle / 360) * math.pi * radius**2
    if independent <= 0 or abs(float(sp.N(exact_expr, 15)) - independent) / independent > 1e-9:
        raise ValueError("modelled example area_sector_foundation verification failed")

    decimal_answer = format(rounding.round_fn(independent), "f")
    teaching_steps = [
        "A sector is a 'slice' of the circle - work out what fraction of the full 360° the sector's "
        "angle takes up, then apply that same fraction to the whole circle's area.",
        f"The angle is {angle}°, so the fraction is {angle} ÷ 360.",
        f"The full circle's area would be π × {radius}². Multiply by the fraction: "
        f"({angle} ÷ 360) × π × {radius}² ≈ {decimal_answer} cm².",
    ]
    worked_calculation = [f"({angle} ÷ 360) × π × {radius}²", f"≈ {decimal_answer} cm²"]
    return ModelledExample(
        topic_id="area_sector_foundation",
        tier=Tier.FOUNDATION,
        prompt=(
            f"A sector of a circle has radius {radius} cm and angle {angle}°. Find the area of the "
            f"sector, correct to {rounding.phrase}."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{decimal_answer} cm²",
        diagram=_sector_diagram(angle, radius),
    )


def generate_area_sector(tier: Tier, rng: random.Random) -> Question:
    radius = rng.randint(3, 15)
    angle = rng.choice(range(15, 360, 15))

    coeff = sp.Rational(angle, 360) * radius**2
    exact_expr = coeff * sp.pi

    arc_length_exact = sp.Rational(angle, 360) * 2 * sp.pi * radius
    area_from_arc = sp.simplify(arc_length_exact * radius / 2)
    if sp.simplify(area_from_arc - exact_expr) != 0:
        raise ValueError("area_sector verification failed")

    answer = f"{_fmt_pi_term(coeff)} cm²"
    steps = [
        f"Area = (θ ÷ 360) × π × r² = ({angle} ÷ 360) × π × {radius}²",
        f"= {answer}",
    ]
    return Question(
        topic_id="area_sector",
        tier=Tier.HIGHER,
        prompt=f"A sector of a circle has radius {radius} cm and angle {angle}°. Find the exact area of the sector, in terms of π.",
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"sector_h:{radius}:{angle}",
        diagram=_sector_diagram(angle, radius),
    )


def generate_modelled_example_area_sector(tier: Tier, rng: random.Random) -> ModelledExample:
    radius = rng.randint(3, 15)
    angle = rng.choice(range(15, 360, 15))

    coeff = sp.Rational(angle, 360) * radius**2
    exact_expr = coeff * sp.pi

    arc_length_exact = sp.Rational(angle, 360) * 2 * sp.pi * radius
    area_from_arc = sp.simplify(arc_length_exact * radius / 2)
    if sp.simplify(area_from_arc - exact_expr) != 0:
        raise ValueError("modelled example area_sector verification failed")

    answer = f"{_fmt_pi_term(coeff)} cm²"
    teaching_steps = [
        "Keeping the answer exact means leaving π in the answer rather than using a calculator "
        "decimal value for it - work with the fraction of the circle first, then attach π at the end.",
        f"The angle {angle}° out of 360° gives the fraction {angle}/360.",
        f"Multiply that fraction by the full circle's area π × {radius}², keeping π symbolic "
        f"throughout: {answer}.",
    ]
    worked_calculation = [f"({angle}/360) × π × {radius}²", f"= {answer}"]
    return ModelledExample(
        topic_id="area_sector",
        tier=Tier.HIGHER,
        prompt=f"A sector of a circle has radius {radius} cm and angle {angle}°. Find the exact area of the sector, in terms of π.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
        diagram=_sector_diagram(angle, radius),
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
    display_name="Semicircle Compound Shapes (Calculator)",
    description="Find the area of a rectangle with a semicircle attached, giving a decimal answer.",
    generate=generate_semicircle_compound,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_semicircle_compound,
)

TOPIC_SEMICIRCLE_COMPOUND_HIGHER = TopicDefinition(
    id="area_semicircle_compound_higher",
    display_name="Semicircle Compound Shapes",
    description="Find the area of a rectangle with a semicircle attached, in terms of π.",
    generate=generate_semicircle_compound_higher,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_semicircle_compound_higher,
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

TOPIC_SUBTRACT_COMPOUND_FOUNDATION = TopicDefinition(
    id="area_subtract_compound_foundation",
    display_name="Subtractive Compound Shapes (Foundation)",
    description="Find the remaining area after a rectangular hole is cut from a larger rectangle.",
    generate=generate_subtract_compound_foundation,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_subtract_compound_foundation,
)

TOPIC_PARALLELOGRAM = TopicDefinition(
    id="area_parallelogram",
    display_name="Parallelograms",
    description="Find the area of a parallelogram given its base and perpendicular height.",
    generate=generate_area_parallelogram,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_area_parallelogram,
)

TOPIC_TRAPEZIUM = TopicDefinition(
    id="area_trapezium",
    display_name="Trapeziums",
    description="Find the area of a trapezium given its parallel sides and perpendicular height.",
    generate=generate_area_trapezium,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_area_trapezium,
)

TOPIC_MIXED_COMPOUND = TopicDefinition(
    id="area_mixed_compound",
    display_name="Mixed Compound Shapes",
    description="Find the area of a shape combining a rectangle, a triangle, and a quarter-circle cut.",
    generate=generate_area_mixed_compound,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_area_mixed_compound,
)

TOPIC_ARC_LENGTH_FOUNDATION = TopicDefinition(
    id="arc_length_foundation",
    display_name="Arc Length (Calculator)",
    description="Find the length of an arc of a circle, giving a decimal answer.",
    generate=generate_arc_length_foundation,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_arc_length_foundation,
)

TOPIC_ARC_LENGTH = TopicDefinition(
    id="arc_length",
    display_name="Arc Length",
    description="Find the exact length of an arc of a circle, in terms of π.",
    generate=generate_arc_length,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_arc_length,
)

TOPIC_AREA_SECTOR_FOUNDATION = TopicDefinition(
    id="area_sector_foundation",
    display_name="Area of a Sector (Calculator)",
    description="Find the area of a sector of a circle, giving a decimal answer.",
    generate=generate_area_sector_foundation,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_area_sector_foundation,
)

TOPIC_AREA_SECTOR = TopicDefinition(
    id="area_sector",
    display_name="Area of a Sector",
    description="Find the exact area of a sector of a circle, in terms of π.",
    generate=generate_area_sector,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_area_sector,
)
