import math
import random
from decimal import ROUND_HALF_UP, Decimal

import sympy as sp

from app.core.models import DiagramSpec, ModelledExample, Question, Tier
from app.topics.base import TopicDefinition

SECTION = "geometry"
GROUP = "3D Shapes"

_MEASURE_LABEL = {"volume": "volume", "surface_area": "total surface area"}


def _round_to_3sf(value: float) -> Decimal:
    """Round a float to 3 significant figures, always displaying as a plain
    fixed-point decimal string - sympy's sp.N(expr, 3) switches to scientific
    notation (e.g. "1.02E+3") for values >= 1000, which is exactly the
    _round_to_1sf bug already documented and fixed in estimation.py. Cylinder/
    cone volumes and surface areas comfortably reach into the thousands, so
    this project's own documented fix pattern is reused here rather than
    calling sp.N directly for display."""
    d = Decimal(str(value))
    exp = d.adjusted()
    quantized = d.quantize(Decimal(1).scaleb(exp - 2), rounding=ROUND_HALF_UP)
    return Decimal(format(quantized, "f"))


def _fmt_pi_term(coeff) -> str:
    coeff = sp.Rational(coeff)
    if coeff == 1:
        return "π"
    if coeff.is_Integer:
        return f"{int(coeff)}π"
    return f"({coeff.p}/{coeff.q})π"


# ---------------------------------------------------------------------------
# Cylinder - Foundation (calculator/decimal answers)
# ---------------------------------------------------------------------------


def generate_volume_surface_area_cylinder_foundation(tier: Tier, rng: random.Random) -> Question:
    radius = rng.randint(2, 12)
    height = rng.randint(3, 20)
    measure = rng.choice(["volume", "surface_area"])

    if measure == "volume":
        exact_expr = sp.pi * radius**2 * height
        value = float(exact_expr)
        decimal_answer = _round_to_3sf(value)
        independent = math.pi * radius**2 * height
        steps = [
            f"Volume = π × r² × h = π × {radius}² × {height}",
            f"= {decimal_answer} cm³ (3 s.f., using a calculator value of π)",
        ]
        unit = "cm³"
    else:
        exact_expr = 2 * sp.pi * radius**2 + 2 * sp.pi * radius * height
        value = float(exact_expr)
        decimal_answer = _round_to_3sf(value)
        independent = 2 * math.pi * radius**2 + 2 * math.pi * radius * height
        steps = [
            f"Surface area = 2πr² + 2πrh = (2 × π × {radius}²) + (2 × π × {radius} × {height})",
            f"= {decimal_answer} cm² (3 s.f., using a calculator value of π)",
        ]
        unit = "cm²"

    # Independent check via Python's math.pi - a different π source/implementation
    # than sympy's symbolic pi used above (matches area_circle_foundation's style).
    if abs(value - independent) / independent > 0.01:
        raise ValueError("volume_surface_area_cylinder_foundation verification failed")

    return Question(
        topic_id="volume_surface_area_cylinder_foundation",
        tier=Tier.FOUNDATION,
        prompt=(
            f"A cylinder has radius {radius} cm and height {height} cm. Find its "
            f"{_MEASURE_LABEL[measure]}, correct to 3 significant figures."
        ),
        solution_steps=tuple(steps),
        final_answer=f"{decimal_answer} {unit}",
        dedup_key=f"cyl_f:{radius}:{height}:{measure}",
        diagram=DiagramSpec(
            kind="cylinder",
            params={"radius_label": f"{radius} cm", "height_label": f"{height} cm"},
        ),
    )


def generate_modelled_example_volume_surface_area_cylinder_foundation(
    tier: Tier, rng: random.Random
) -> ModelledExample:
    radius = rng.randint(2, 12)
    height = rng.randint(3, 20)
    measure = rng.choice(["volume", "surface_area"])

    if measure == "volume":
        exact_expr = sp.pi * radius**2 * height
        value = float(exact_expr)
        decimal_answer = _round_to_3sf(value)
        independent = math.pi * radius**2 * height
        teaching_steps = [
            "A cylinder is just a circle 'stretched out' into a prism - its volume is the area of "
            "the circular cross-section multiplied by the height, the same idea used for any prism.",
            f"The base area is π × r² = π × {radius}² = π × {radius**2}.",
            f"Multiply the base area by the height: π × {radius**2} × {height} ≈ {value:.5f}...",
            f"Round to 3 significant figures: {decimal_answer} cm³.",
        ]
        worked_calculation = [
            "Volume = π × r² × h",
            f"= π × {radius}² × {height}",
            f"= {decimal_answer} cm³ (3 s.f.)",
        ]
        unit = "cm³"
    else:
        exact_expr = 2 * sp.pi * radius**2 + 2 * sp.pi * radius * height
        value = float(exact_expr)
        decimal_answer = _round_to_3sf(value)
        independent = 2 * math.pi * radius**2 + 2 * math.pi * radius * height
        teaching_steps = [
            "A cylinder's total surface area is made of three pieces: the two circular ends "
            "(top and bottom) plus the curved side, which unrolls flat into a rectangle.",
            f"The two circular ends together give 2 × π × r² = 2 × π × {radius}² = 2 × π × {radius**2}.",
            f"The curved side unrolls into a rectangle of width equal to the circle's circumference "
            f"and height {height} cm, giving 2 × π × {radius} × {height}.",
            f"Add the two parts together: (2 × π × {radius**2}) + (2 × π × {radius} × {height}) "
            f"≈ {decimal_answer} cm² (3 s.f.).",
        ]
        worked_calculation = [
            "Surface area = 2πr² + 2πrh",
            f"= (2 × π × {radius}²) + (2 × π × {radius} × {height})",
            f"= {decimal_answer} cm² (3 s.f.)",
        ]
        unit = "cm²"

    if abs(value - independent) / independent > 0.01:
        raise ValueError("modelled example volume_surface_area_cylinder_foundation verification failed")

    return ModelledExample(
        topic_id="volume_surface_area_cylinder_foundation",
        tier=Tier.FOUNDATION,
        prompt=(
            f"A cylinder has radius {radius} cm and height {height} cm. Find its "
            f"{_MEASURE_LABEL[measure]}, correct to 3 significant figures."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{decimal_answer} {unit}",
        diagram=DiagramSpec(
            kind="cylinder",
            params={"radius_label": f"{radius} cm", "height_label": f"{height} cm"},
        ),
    )


# ---------------------------------------------------------------------------
# Cylinder - Higher (exact pi form)
# ---------------------------------------------------------------------------


def generate_volume_surface_area_cylinder(tier: Tier, rng: random.Random) -> Question:
    radius = rng.randint(2, 12)
    height = rng.randint(3, 20)
    measure = rng.choice(["volume", "surface_area"])

    if measure == "volume":
        coeff = sp.Rational(radius**2 * height)
        exact_expr = coeff * sp.pi

        # Independent check: recompute via the base circle's area as its own
        # quantity, then multiply by height - a genuinely different route
        # (two separate steps) from the single combined coefficient above.
        base_area_coeff = sp.Rational(radius**2)
        volume_alt = base_area_coeff * sp.pi * height
        if sp.simplify(volume_alt - exact_expr) != 0:
            raise ValueError("volume_surface_area_cylinder volume verification failed")

        answer = f"{_fmt_pi_term(coeff)} cm³"
        steps = [
            f"Volume = π × r² × h = π × {radius}² × {height}",
            f"= {answer}",
        ]
    else:
        coeff = sp.Rational(2 * radius**2 + 2 * radius * height)
        exact_expr = coeff * sp.pi

        # Independent check: two genuinely different algebraic groupings of the
        # same total surface area formula.
        alt = 2 * sp.pi * radius * (radius + height)
        if sp.simplify(alt - exact_expr) != 0:
            raise ValueError("volume_surface_area_cylinder surface area verification failed")

        answer = f"{_fmt_pi_term(coeff)} cm²"
        steps = [
            f"Surface area = 2πr(r + h) = 2 × π × {radius} × ({radius} + {height})",
            f"= {answer}",
        ]

    return Question(
        topic_id="volume_surface_area_cylinder",
        tier=Tier.HIGHER,
        prompt=(
            f"A cylinder has radius {radius} cm and height {height} cm. Find the exact "
            f"{_MEASURE_LABEL[measure]}, in terms of π."
        ),
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"cyl_h:{radius}:{height}:{measure}",
        diagram=DiagramSpec(
            kind="cylinder",
            params={"radius_label": f"{radius} cm", "height_label": f"{height} cm"},
        ),
    )


def generate_modelled_example_volume_surface_area_cylinder(tier: Tier, rng: random.Random) -> ModelledExample:
    radius = rng.randint(2, 12)
    height = rng.randint(3, 20)
    measure = rng.choice(["volume", "surface_area"])

    if measure == "volume":
        coeff = sp.Rational(radius**2 * height)
        exact_expr = coeff * sp.pi

        base_area_coeff = sp.Rational(radius**2)
        volume_alt = base_area_coeff * sp.pi * height
        if sp.simplify(volume_alt - exact_expr) != 0:
            raise ValueError("modelled example volume_surface_area_cylinder volume verification failed")

        answer = f"{_fmt_pi_term(coeff)} cm³"
        teaching_steps = [
            "Keeping the answer exact means leaving π symbolic instead of using a rounded "
            "calculator value - work out the numerical coefficient first, then attach π at the end.",
            f"The base circle's area is π × {radius}² = π × {radius**2}.",
            f"Multiply by the height, keeping π symbolic throughout: π × {radius**2} × {height} "
            f"= {answer}.",
        ]
        worked_calculation = [
            "Volume = π × r² × h",
            f"= π × {radius}² × {height}",
            f"= {answer}",
        ]
    else:
        coeff = sp.Rational(2 * radius**2 + 2 * radius * height)
        exact_expr = coeff * sp.pi

        alt = 2 * sp.pi * radius * (radius + height)
        if sp.simplify(alt - exact_expr) != 0:
            raise ValueError("modelled example volume_surface_area_cylinder surface area verification failed")

        answer = f"{_fmt_pi_term(coeff)} cm²"
        teaching_steps = [
            "The total surface area is the two circular ends plus the curved side, factorised "
            "here as 2πr(r + h) - and since the answer must be exact, π stays as a symbol "
            "throughout rather than being rounded to a decimal.",
            f"Add the radius and height inside the bracket first: {radius} + {height} = {radius + height}.",
            f"Multiply everything together, keeping π symbolic: 2 × π × {radius} × {radius + height} "
            f"= {answer}.",
        ]
        worked_calculation = [
            "Surface area = 2πr(r + h)",
            f"= 2 × π × {radius} × ({radius} + {height})",
            f"= {answer}",
        ]

    return ModelledExample(
        topic_id="volume_surface_area_cylinder",
        tier=Tier.HIGHER,
        prompt=(
            f"A cylinder has radius {radius} cm and height {height} cm. Find the exact "
            f"{_MEASURE_LABEL[measure]}, in terms of π."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
        diagram=DiagramSpec(
            kind="cylinder",
            params={"radius_label": f"{radius} cm", "height_label": f"{height} cm"},
        ),
    )


# ---------------------------------------------------------------------------
# Cone - Higher only (decimal answers, 3 s.f.)
# ---------------------------------------------------------------------------


def generate_volume_surface_area_cone(tier: Tier, rng: random.Random) -> Question:
    for _ in range(20):
        branch = rng.choice(["slant_given", "derive_slant"])
        measure = rng.choice(["volume", "surface_area"])
        radius = rng.randint(2, 10)

        if branch == "slant_given":
            slant = rng.randint(radius + 2, radius + 20)
            candidate_height = math.sqrt(slant**2 - radius**2)
            if candidate_height > 0.5:
                break
        else:
            height = rng.randint(3, 20)
            candidate_slant = math.sqrt(radius**2 + height**2)
            if candidate_slant - radius > 0.5:
                break
    else:
        raise ValueError("volume_surface_area_cone could not find a valid non-degenerate configuration")

    if branch == "slant_given":
        # Independent check: cross-check the derived height's square against
        # slant^2 - radius^2 via a second math.sqrt-based float computation,
        # not just trusting the sqrt used to build height in the first place.
        height = math.sqrt(slant**2 - radius**2)
        height_check = math.sqrt(float(slant**2 - radius**2))
        if abs(height - height_check) / height_check > 0.01:
            raise ValueError("volume_surface_area_cone height derivation verification failed")
        diagram = DiagramSpec(
            kind="cone",
            params={"radius_label": f"{radius} cm", "slant_label": f"{slant} cm"},
        )
        solution_diagram = None
        given_desc = f"radius {radius} cm and slant height {slant} cm"
    else:
        slant = math.sqrt(radius**2 + height**2)
        slant_check = math.sqrt(float(radius**2 + height**2))
        if abs(slant - slant_check) / slant_check > 0.01:
            raise ValueError("volume_surface_area_cone slant derivation verification failed")
        diagram = DiagramSpec(
            kind="cone",
            params={
                "radius_label": f"{radius} cm",
                "height_label": f"{height} cm",
                "show_height_triangle": True,
            },
        )
        solution_diagram = DiagramSpec(
            kind="cone",
            params={
                "radius_label": f"{radius} cm",
                "height_label": f"{height} cm",
                "show_height_triangle": True,
                "slant_label": f"{slant:.2f} cm",
            },
        )
        given_desc = f"radius {radius} cm and (perpendicular) height {height} cm"

    if measure == "volume":
        exact_expr = sp.Rational(1, 3) * sp.pi * radius**2 * height
        value = float(exact_expr)
        decimal_answer = _round_to_3sf(value)
        independent = (1 / 3) * math.pi * radius**2 * height
        if abs(value - independent) / independent > 0.01:
            raise ValueError("volume_surface_area_cone volume verification failed")
        steps = [
            f"Volume = (1/3) × π × r² × h = (1/3) × π × {radius}² × {height:.3f}",
            f"= {decimal_answer} cm³ (3 s.f., using a calculator value of π)",
        ]
        answer = f"{decimal_answer} cm³"
    else:
        exact_expr = sp.pi * radius * (radius + slant)
        value = float(exact_expr)
        decimal_answer = _round_to_3sf(value)
        independent = math.pi * radius * (radius + slant)
        if abs(value - independent) / independent > 0.01:
            raise ValueError("volume_surface_area_cone surface area verification failed")
        steps = [
            f"Surface area = πr² + πrl = πr(r + l) = π × {radius} × ({radius} + {slant:.3f})",
            f"= {decimal_answer} cm² (3 s.f., using a calculator value of π)",
        ]
        answer = f"{decimal_answer} cm²"

    dedup_value = slant if branch == "slant_given" else height
    return Question(
        topic_id="volume_surface_area_cone",
        tier=Tier.HIGHER,
        prompt=(
            f"A cone has {given_desc}. Find its {_MEASURE_LABEL[measure]}, correct to "
            "3 significant figures."
        ),
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"cone:{branch}:{radius}:{round(dedup_value, 3)}:{measure}",
        diagram=diagram,
        solution_diagram=solution_diagram,
    )


def generate_modelled_example_volume_surface_area_cone(tier: Tier, rng: random.Random) -> ModelledExample:
    for _ in range(20):
        branch = rng.choice(["slant_given", "derive_slant"])
        measure = rng.choice(["volume", "surface_area"])
        radius = rng.randint(2, 10)

        if branch == "slant_given":
            slant = rng.randint(radius + 2, radius + 20)
            candidate_height = math.sqrt(slant**2 - radius**2)
            if candidate_height > 0.5:
                break
        else:
            height = rng.randint(3, 20)
            candidate_slant = math.sqrt(radius**2 + height**2)
            if candidate_slant - radius > 0.5:
                break
    else:
        raise ValueError(
            "modelled example volume_surface_area_cone could not find a valid non-degenerate configuration"
        )

    if branch == "slant_given":
        height = math.sqrt(slant**2 - radius**2)
        height_check = math.sqrt(float(slant**2 - radius**2))
        if abs(height - height_check) / height_check > 0.01:
            raise ValueError("modelled example volume_surface_area_cone height derivation verification failed")
        diagram = DiagramSpec(
            kind="cone",
            params={"radius_label": f"{radius} cm", "slant_label": f"{slant} cm"},
        )
        given_desc = f"radius {radius} cm and slant height {slant} cm"
        setup_teaching = [
            f"Here the slant height ({slant} cm) is given directly, so no Pythagoras is needed to "
            "find it - but the perpendicular height would need Pythagoras if it were wanted instead."
        ]
    else:
        slant = math.sqrt(radius**2 + height**2)
        slant_check = math.sqrt(float(radius**2 + height**2))
        if abs(slant - slant_check) / slant_check > 0.01:
            raise ValueError("modelled example volume_surface_area_cone slant derivation verification failed")
        diagram = DiagramSpec(
            kind="cone",
            params={
                "radius_label": f"{radius} cm",
                "height_label": f"{height} cm",
                "show_height_triangle": True,
            },
        )
        given_desc = f"radius {radius} cm and (perpendicular) height {height} cm"
        setup_teaching = [
            f"The slant height isn't given directly here, so first use Pythagoras on the "
            f"right-angled triangle formed by the radius and the perpendicular height: "
            f"l = √(r² + h²) = √({radius}² + {height}²) ≈ {slant:.3f} cm.",
        ]

    if measure == "volume":
        exact_expr = sp.Rational(1, 3) * sp.pi * radius**2 * height
        value = float(exact_expr)
        decimal_answer = _round_to_3sf(value)
        independent = (1 / 3) * math.pi * radius**2 * height
        if abs(value - independent) / independent > 0.01:
            raise ValueError("modelled example volume_surface_area_cone volume verification failed")
        teaching_steps = setup_teaching + [
            "A cone's volume is exactly one third of the cylinder that would exactly enclose it - "
            "same base radius, same height.",
            f"The enclosing cylinder's volume is π × r² × h = π × {radius}² × {height:.3f}; the "
            f"cone is one third of that.",
            f"(1/3) × π × {radius}² × {height:.3f} ≈ {decimal_answer} cm³ (3 s.f.).",
        ]
        worked_calculation = [
            "Volume = (1/3) × π × r² × h",
            f"= (1/3) × π × {radius}² × {height:.3f}",
            f"= {decimal_answer} cm³ (3 s.f.)",
        ]
        answer = f"{decimal_answer} cm³"
    else:
        exact_expr = sp.pi * radius * (radius + slant)
        value = float(exact_expr)
        decimal_answer = _round_to_3sf(value)
        independent = math.pi * radius * (radius + slant)
        if abs(value - independent) / independent > 0.01:
            raise ValueError("modelled example volume_surface_area_cone surface area verification failed")
        teaching_steps = setup_teaching + [
            "A cone's total surface area has two parts: the circular base (πr²) and the curved "
            "surface, which unrolls into πrl - together that factorises as πr(r + l).",
            f"Add the radius and slant height inside the bracket: {radius} + {slant:.3f} "
            f"≈ {radius + slant:.3f}.",
            f"Multiply by π × r: π × {radius} × {radius + slant:.3f} ≈ {decimal_answer} cm² (3 s.f.).",
        ]
        worked_calculation = [
            "Surface area = πr(r + l)",
            f"= π × {radius} × ({radius} + {slant:.3f})",
            f"= {decimal_answer} cm² (3 s.f.)",
        ]
        answer = f"{decimal_answer} cm²"

    return ModelledExample(
        topic_id="volume_surface_area_cone",
        tier=Tier.HIGHER,
        prompt=(
            f"A cone has {given_desc}. Find its {_MEASURE_LABEL[measure]}, correct to "
            "3 significant figures."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
        diagram=diagram,
    )


TOPIC_VOLUME_SURFACE_AREA_CYLINDER_FOUNDATION = TopicDefinition(
    id="volume_surface_area_cylinder_foundation",
    display_name="Volume & Surface Area of a Cylinder (Calculator)",
    description="Find the volume or total surface area of a cylinder, giving a decimal answer.",
    generate=generate_volume_surface_area_cylinder_foundation,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_volume_surface_area_cylinder_foundation,
)

TOPIC_VOLUME_SURFACE_AREA_CYLINDER = TopicDefinition(
    id="volume_surface_area_cylinder",
    display_name="Volume & Surface Area of a Cylinder",
    description="Find the exact volume or total surface area of a cylinder, in terms of π.",
    generate=generate_volume_surface_area_cylinder,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_volume_surface_area_cylinder,
)

TOPIC_VOLUME_SURFACE_AREA_CONE = TopicDefinition(
    id="volume_surface_area_cone",
    display_name="Volume & Surface Area of a Cone",
    description=(
        "Find the volume or total surface area of a cone, given either the slant height or "
        "the perpendicular height."
    ),
    generate=generate_volume_surface_area_cone,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_volume_surface_area_cone,
    preamble_lines=(
        "Volume of a cone = (1/3) × π × r² × h",
        "Surface area of a cone = πr(r + l), where l is the slant height",
    ),
)
