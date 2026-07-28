import math
import random
from decimal import ROUND_HALF_UP, Decimal

import sympy as sp

from app.core.models import DiagramSpec, ModelledExample, Question, Tier
from app.topics.base import TopicDefinition

SECTION = "geometry"
GROUP = "3D Shapes"

# All four topics in this module are genuinely Higher-only content on the real
# AQA/Edexcel specs (Foundation stops at prisms/cylinders), so none of them
# get a Foundation sibling.


def _fmt_sig3(expr) -> str:
    """Format a sympy expression rounded to 3 significant figures as a plain
    fixed-point decimal string. sp.N(expr, 3)'s default string form switches
    to scientific notation (e.g. "1.41e+4") once the rounded value has more
    integer digits than the requested precision - confirmed by rendering an
    actual worksheet (e.g. a sphere of radius 15 cm gave a volume of
    "1.41E+4 cm3" instead of "14100 cm3"). This bites several quantities in
    THIS module (sphere/frustum volumes, curved compound-solid volumes) that
    comfortably exceed 999 for the larger end of their random ranges, unlike
    any existing area_perimeter.py topic sp.N(expr, 3) was copied from, none
    of which get that large. Mirrors the fix already applied to
    estimation.py's _round_to_1sf for the same underlying reason (see
    CLAUDE.md's Decimal/scientific-notation gotcha)."""
    value = float(sp.N(expr, 15))
    if value == 0:
        return "0"
    d = Decimal(repr(value))
    exponent = d.adjusted()
    quant = Decimal(1).scaleb(exponent - 2)
    rounded = d.quantize(quant, rounding=ROUND_HALF_UP)
    return format(rounded, "f")


def _frac_str(value) -> str:
    """Format a sympy Rational as a plain integer string when it's whole,
    otherwise as 'p/q' - matches the convention already used for exact
    (non-rounded) areas/volumes elsewhere in this codebase (e.g. triangle
    area in area_perimeter.py)."""
    value = sp.Rational(value)
    return str(int(value)) if value.is_Integer else f"{value.p}/{value.q}"


# ---------------------------------------------------------------------------
# Topic 1: Volume & Surface Area of a Sphere (and hemisphere)
# ---------------------------------------------------------------------------

def generate_volume_surface_area_sphere(tier: Tier, rng: random.Random) -> Question:
    for _ in range(20):
        is_hemisphere = rng.choice([False, True])
        measure = rng.choice(["volume", "surface_area"])
        radius = rng.randint(2, 15)
        if radius >= 2:
            break
    else:
        raise ValueError("volume_surface_area_sphere could not draw a valid radius")

    shape_word = "hemisphere" if is_hemisphere else "sphere"

    if is_hemisphere:
        if measure == "volume":
            exact_expr = sp.Rational(2, 3) * sp.pi * radius**3
            independent = (2 / 3) * math.pi * radius**3
            steps = [f"V = (2/3) × π × r³ = (2/3) × π × {radius}³"]
            unit = "cm³"
        else:
            exact_expr = 3 * sp.pi * radius**2
            independent = 3 * math.pi * radius**2
            steps = [
                "Total surface area = curved surface + flat circular face "
                "= 2 × π × r² + π × r² = 3 × π × r²",
                f"= 3 × π × {radius}²",
            ]
            unit = "cm²"
    else:
        if measure == "volume":
            exact_expr = sp.Rational(4, 3) * sp.pi * radius**3
            independent = (4 / 3) * math.pi * radius**3
            steps = [f"V = (4/3) × π × r³ = (4/3) × π × {radius}³"]
            unit = "cm³"
        else:
            exact_expr = 4 * sp.pi * radius**2
            independent = 4 * math.pi * radius**2
            steps = [f"SA = 4 × π × r² = 4 × π × {radius}²"]
            unit = "cm²"

    decimal_answer = sp.N(exact_expr, 3)
    # Independent check via Python's math.pi - a different pi source/
    # implementation than sympy's symbolic pi used above.
    if independent <= 0 or abs(float(decimal_answer) - independent) / independent > 0.01:
        raise ValueError("volume_surface_area_sphere verification failed")
    decimal_str = _fmt_sig3(exact_expr)

    steps.append(f"= {decimal_str} {unit} (3 s.f.)")

    measure_label = "volume" if measure == "volume" else "total surface area"
    flat_face_note = " (including its flat circular face)" if (is_hemisphere and measure == "surface_area") else ""
    prompt = (
        f"A {shape_word} has radius {radius} cm. Find its {measure_label}{flat_face_note}, "
        "correct to 3 significant figures."
    )

    return Question(
        topic_id="volume_surface_area_sphere",
        tier=Tier.HIGHER,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=f"{decimal_str} {unit}",
        dedup_key=f"sphere:{is_hemisphere}:{measure}:{radius}",
        diagram=DiagramSpec(
            kind="sphere",
            params={"radius_label": f"{radius} cm", "hemisphere": is_hemisphere},
        ),
    )


def generate_modelled_example_volume_surface_area_sphere(tier: Tier, rng: random.Random) -> ModelledExample:
    for _ in range(20):
        is_hemisphere = rng.choice([False, True])
        measure = rng.choice(["volume", "surface_area"])
        radius = rng.randint(2, 15)
        if radius >= 2:
            break
    else:
        raise ValueError("modelled example volume_surface_area_sphere could not draw a valid radius")

    shape_word = "hemisphere" if is_hemisphere else "sphere"

    if is_hemisphere:
        if measure == "volume":
            exact_expr = sp.Rational(2, 3) * sp.pi * radius**3
            independent = (2 / 3) * math.pi * radius**3
            formula_str = "V = (2/3) × π × r³"
            unit = "cm³"
        else:
            exact_expr = 3 * sp.pi * radius**2
            independent = 3 * math.pi * radius**2
            formula_str = "Total SA = 3 × π × r² (curved 2πr² + flat face πr²)"
            unit = "cm²"
    else:
        if measure == "volume":
            exact_expr = sp.Rational(4, 3) * sp.pi * radius**3
            independent = (4 / 3) * math.pi * radius**3
            formula_str = "V = (4/3) × π × r³"
            unit = "cm³"
        else:
            exact_expr = 4 * sp.pi * radius**2
            independent = 4 * math.pi * radius**2
            formula_str = "SA = 4 × π × r²"
            unit = "cm²"

    decimal_answer = sp.N(exact_expr, 3)
    if independent <= 0 or abs(float(decimal_answer) - independent) / independent > 0.01:
        raise ValueError("modelled example volume_surface_area_sphere verification failed")
    decimal_str = _fmt_sig3(exact_expr)

    if is_hemisphere and measure == "volume":
        teaching_steps = [
            "A hemisphere is exactly half of a full sphere, so its volume is half of "
            "(4/3) × π × r³, which simplifies to (2/3) × π × r³.",
            f"Cube the radius first: {radius}³ = {radius**3}.",
            f"Multiply by (2/3) × π on a calculator: (2/3) × π × {radius**3} ≈ {float(exact_expr):.4f}...",
            f"Rounded to 3 significant figures, the volume is {decimal_str} cm³.",
        ]
    elif is_hemisphere:
        teaching_steps = [
            "A hemisphere's surface has two parts: the curved 'dome' part, and the flat "
            "circular face where it was sliced from the full sphere - both must be included "
            "for the TOTAL surface area.",
            f"The curved part is half a sphere's surface: (1/2) × 4 × π × r² = 2 × π × r², "
            f"and the flat circular face is just π × r² - together that's 3 × π × r².",
            f"Substitute the radius: 3 × π × {radius}² = 3 × π × {radius**2}.",
            f"Evaluate on a calculator and round to 3 significant figures: {decimal_str} cm².",
        ]
    elif measure == "volume":
        teaching_steps = [
            "The volume of a sphere is given by the formula V = (4/3) × π × r³, where r is "
            "the radius - note that the radius is CUBED, not squared.",
            f"Cube the radius first: {radius}³ = {radius**3}.",
            f"Multiply by (4/3) × π on a calculator: (4/3) × π × {radius**3} ≈ {float(exact_expr):.4f}...",
            f"Rounded to 3 significant figures, the volume is {decimal_str} cm³.",
        ]
    else:
        teaching_steps = [
            "The surface area of a sphere is given by the formula SA = 4 × π × r², where r "
            "is the radius.",
            f"Square the radius first: {radius}² = {radius**2}.",
            f"Multiply by 4 × π on a calculator: 4 × π × {radius**2} ≈ {float(exact_expr):.4f}...",
            f"Rounded to 3 significant figures, the surface area is {decimal_str} cm².",
        ]

    worked_calculation = [formula_str, f"= {decimal_str} {unit} (3 s.f.)"]

    measure_label = "volume" if measure == "volume" else "total surface area"
    flat_face_note = " (including its flat circular face)" if (is_hemisphere and measure == "surface_area") else ""
    prompt = (
        f"A {shape_word} has radius {radius} cm. Find its {measure_label}{flat_face_note}, "
        "correct to 3 significant figures."
    )

    return ModelledExample(
        topic_id="volume_surface_area_sphere",
        tier=Tier.HIGHER,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{decimal_str} {unit}",
        diagram=DiagramSpec(
            kind="sphere",
            params={"radius_label": f"{radius} cm", "hemisphere": is_hemisphere},
        ),
    )


# ---------------------------------------------------------------------------
# Topic 2: Volume & Surface Area of a (square-based) Pyramid
# ---------------------------------------------------------------------------

def generate_volume_surface_area_pyramid(tier: Tier, rng: random.Random) -> Question:
    for _ in range(20):
        base = rng.randint(4, 16)
        height = rng.randint(3, 20)
        if base > 0 and height > 0:
            break
    else:
        raise ValueError("volume_surface_area_pyramid could not draw valid dimensions")

    measure = rng.choice(["volume", "surface_area"])

    # Slant height of a TRIANGULAR FACE (apex straight down to the midpoint of
    # a base edge) - Pythagoras on the pyramid's vertical height and half the
    # base side.
    l_exact = sp.sqrt(height**2 + sp.Rational(base, 2) ** 2)
    l_float_from_sympy = float(sp.N(l_exact, 10))
    # Independent check (a): re-derive l via a second, plain math.sqrt-based
    # float computation rather than sympy's symbolic sqrt.
    l_float_independent = math.sqrt(height**2 + (base / 2) ** 2)
    if abs(l_float_from_sympy - l_float_independent) > 1e-6:
        raise ValueError("volume_surface_area_pyramid slant height verification failed")

    # Volume doesn't involve l (no sqrt), so it's exact - give it as an exact
    # integer/fraction with no rounding. Surface area DOES involve l, which is
    # often irrational, so that one is rounded to 3 s.f. instead. (Design
    # choice, kept consistent throughout this generator.)
    volume_exact = sp.Rational(base**2 * height, 3)
    # Independent check: a different grouping of the same formula (multiply
    # the base area by height/3 as a fraction, instead of dividing the whole
    # product by 3), plus a fully separate plain-float computation.
    volume_regrouped = sp.Rational(base, 1) ** 2 * sp.Rational(height, 3)
    volume_float_independent = (1 / 3) * base**2 * height
    if volume_regrouped != volume_exact or abs(float(volume_exact) - volume_float_independent) > 1e-6:
        raise ValueError("volume_surface_area_pyramid volume verification failed")

    sa_exact = base**2 + 2 * base * l_exact
    sa_decimal = sp.N(sa_exact, 3)
    # Independent check (b): recompute total surface area via a fully
    # separate math-library float computation against the sympy-based one.
    sa_float_independent = base**2 + 2 * base * l_float_independent
    if abs(float(sa_decimal) - sa_float_independent) / sa_float_independent > 0.01:
        raise ValueError("volume_surface_area_pyramid surface area verification failed")

    if measure == "volume":
        vol_str = _frac_str(volume_exact)
        steps = [
            f"Volume = (1/3) × base² × height = (1/3) × {base}² × {height}",
            f"= {vol_str} cm³",
        ]
        final_answer = f"{vol_str} cm³"
        prompt = (
            f"A square-based pyramid has a base of side {base} cm and a perpendicular height "
            f"of {height} cm. Find its volume."
        )
    else:
        l_display = _fmt_sig3(l_exact)
        sa_display = _fmt_sig3(sa_exact)
        steps = [
            f"Slant height l = √(height² + (base ÷ 2)²) = √({height}² + ({base} ÷ 2)²) ≈ {l_display} cm",
            f"Surface area = base² + 2 × base × l = {base}² + 2 × {base} × {l_display}",
            f"= {sa_display} cm² (3 s.f.)",
        ]
        final_answer = f"{sa_display} cm²"
        prompt = (
            f"A square-based pyramid has a base of side {base} cm and a perpendicular height "
            f"of {height} cm. Find its total surface area, correct to 3 significant figures."
        )

    diagram_params = {"base_label": f"{base} cm", "height_label": f"{height} cm"}
    if measure == "surface_area":
        diagram_params["slant_label"] = f"{l_float_independent:.2f} cm"

    return Question(
        topic_id="volume_surface_area_pyramid",
        tier=Tier.HIGHER,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=final_answer,
        dedup_key=f"pyramid:{base}:{height}:{measure}",
        diagram=DiagramSpec(kind="pyramid", params=diagram_params),
    )


def generate_modelled_example_volume_surface_area_pyramid(tier: Tier, rng: random.Random) -> ModelledExample:
    for _ in range(20):
        base = rng.randint(4, 16)
        height = rng.randint(3, 20)
        if base > 0 and height > 0:
            break
    else:
        raise ValueError("modelled example volume_surface_area_pyramid could not draw valid dimensions")

    measure = rng.choice(["volume", "surface_area"])

    l_exact = sp.sqrt(height**2 + sp.Rational(base, 2) ** 2)
    l_float_from_sympy = float(sp.N(l_exact, 10))
    l_float_independent = math.sqrt(height**2 + (base / 2) ** 2)
    if abs(l_float_from_sympy - l_float_independent) > 1e-6:
        raise ValueError("modelled example volume_surface_area_pyramid slant height verification failed")

    volume_exact = sp.Rational(base**2 * height, 3)
    volume_regrouped = sp.Rational(base, 1) ** 2 * sp.Rational(height, 3)
    volume_float_independent = (1 / 3) * base**2 * height
    if volume_regrouped != volume_exact or abs(float(volume_exact) - volume_float_independent) > 1e-6:
        raise ValueError("modelled example volume_surface_area_pyramid volume verification failed")

    sa_exact = base**2 + 2 * base * l_exact
    sa_decimal = sp.N(sa_exact, 3)
    sa_float_independent = base**2 + 2 * base * l_float_independent
    if abs(float(sa_decimal) - sa_float_independent) / sa_float_independent > 0.01:
        raise ValueError("modelled example volume_surface_area_pyramid surface area verification failed")

    if measure == "volume":
        vol_str = _frac_str(volume_exact)
        teaching_steps = [
            "The volume of any pyramid is (1/3) × base area × perpendicular height - it's "
            "exactly a third of the prism that would fit around it with the same base and "
            "height.",
            f"Here the base is a square of side {base} cm, so the base area is {base}² = "
            f"{base**2} cm².",
            f"Multiply the base area by the height and divide by 3: ({base**2} × {height}) ÷ 3 "
            f"= {vol_str}.",
            f"So the volume is {vol_str} cm³ - notice this is exact, since no square roots "
            "were needed to find it.",
        ]
        worked_calculation = [
            "Volume = (1/3) × base² × height",
            f"= (1/3) × {base}² × {height}",
            f"= {vol_str} cm³",
        ]
        final_answer = f"{vol_str} cm³"
        prompt = (
            f"A square-based pyramid has a base of side {base} cm and a perpendicular height "
            f"of {height} cm. Find its volume."
        )
    else:
        l_display = _fmt_sig3(l_exact)
        sa_display = _fmt_sig3(sa_exact)
        teaching_steps = [
            "Surface area needs the slant height of each triangular face - NOT the vertical "
            "height of the pyramid itself. That slant height runs from the apex down to the "
            "midpoint of a base edge, forming a right-angled triangle with the vertical height "
            "and half the base length, so Pythagoras finds it.",
            f"Half the base is {base} ÷ 2 = {base / 2} cm, so l = √(height² + (base/2)²) = "
            f"√({height}² + {base / 2}²) ≈ {l_display} cm.",
            f"The base contributes {base}² = {base**2} cm², and the four triangular faces "
            f"together contribute 2 × base × l = 2 × {base} × {l_display}.",
            f"Add the base and the four faces together: {base**2} + 2 × {base} × {l_display} "
            f"≈ {sa_display} cm² (3 s.f.).",
        ]
        worked_calculation = [
            f"l = √({height}² + ({base}/2)²) ≈ {l_display} cm",
            "Surface area = base² + 2 × base × l",
            f"= {base}² + 2 × {base} × {l_display}",
            f"= {sa_display} cm² (3 s.f.)",
        ]
        final_answer = f"{sa_display} cm²"
        prompt = (
            f"A square-based pyramid has a base of side {base} cm and a perpendicular height "
            f"of {height} cm. Find its total surface area, correct to 3 significant figures."
        )

    diagram_params = {"base_label": f"{base} cm", "height_label": f"{height} cm"}
    if measure == "surface_area":
        diagram_params["slant_label"] = f"{l_float_independent:.2f} cm"

    return ModelledExample(
        topic_id="volume_surface_area_pyramid",
        tier=Tier.HIGHER,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=final_answer,
        diagram=DiagramSpec(kind="pyramid", params=diagram_params),
    )


# ---------------------------------------------------------------------------
# Topic 3: Volume & Surface Area of a (cone-based) Frustum
# ---------------------------------------------------------------------------

def _frustum_values(rng: random.Random):
    for _ in range(20):
        R = rng.randint(6, 15)
        r = rng.randint(2, R - 2)
        h = rng.randint(3, 15)
        # R - r is guaranteed >= 2 by construction above, so H = R*h/(R-r)
        # never divides by zero - kept as an explicit sanity check anyway
        # (cheap insurance per this codebase's retry-loop convention).
        if R > r and h > 0:
            return R, r, h
    raise ValueError("frustum_volume_surface_area could not draw valid dimensions")


def generate_frustum_volume_surface_area(tier: Tier, rng: random.Random) -> Question:
    R, r, h = _frustum_values(rng)
    measure = rng.choice(["volume", "surface_area"])

    # --- Volume, verified via two genuinely different derivations ---
    # Method 1: extend the frustum to the full (imaginary) cone via similar
    # triangles, then subtract the small cone that was removed.
    H = sp.Rational(R * h, R - r)
    small_h = H - h
    big_cone_volume = sp.Rational(1, 3) * sp.pi * R**2 * H
    small_cone_volume = sp.Rational(1, 3) * sp.pi * r**2 * small_h
    volume_method_1 = big_cone_volume - small_cone_volume

    # Method 2: the closed-form frustum volume formula.
    volume_method_2 = sp.Rational(1, 3) * sp.pi * h * (R**2 + R * r + r**2)

    if sp.simplify(volume_method_1 - volume_method_2) != 0:
        raise ValueError("frustum_volume_surface_area: the two volume derivations disagree")

    volume_exact = volume_method_2
    volume_decimal = sp.N(volume_exact, 3)
    volume_float_independent = math.pi * h * (R**2 + R * r + r**2) / 3
    if abs(float(volume_decimal) - volume_float_independent) / volume_float_independent > 0.01:
        raise ValueError("frustum_volume_surface_area volume verification failed")

    # --- Surface area ---
    # Slant height uses the frustum's OWN vertical height and the radius
    # difference - NOT the full cone's slant height.
    l_exact = sp.sqrt(h**2 + (R - r) ** 2)
    l_float_from_sympy = float(sp.N(l_exact, 10))
    l_float_independent = math.sqrt(h**2 + (R - r) ** 2)
    if abs(l_float_from_sympy - l_float_independent) > 1e-6:
        raise ValueError("frustum_volume_surface_area slant height verification failed")

    total_sa_exact = sp.pi * (R + r) * l_exact + sp.pi * R**2 + sp.pi * r**2
    sa_decimal = sp.N(total_sa_exact, 3)
    sa_float_independent = math.pi * (R + r) * l_float_independent + math.pi * R**2 + math.pi * r**2
    if abs(float(sa_decimal) - sa_float_independent) / sa_float_independent > 0.01:
        raise ValueError("frustum_volume_surface_area surface area verification failed")

    if measure == "volume":
        volume_display = _fmt_sig3(volume_exact)
        steps = [
            f"Full cone height H = R × h ÷ (R - r) = {R} × {h} ÷ ({R} - {r}) = {sp.N(H, 4)} cm (similar triangles)",
            f"Big cone volume = (1/3) × π × R² × H, small cone volume = (1/3) × π × r² × (H - h)",
            f"Frustum volume = (1/3) × π × h × (R² + Rr + r²) = (1/3) × π × {h} × "
            f"({R}² + {R}×{r} + {r}²)",
            f"= {volume_display} cm³ (3 s.f.)",
        ]
        final_answer = f"{volume_display} cm³"
        prompt = (
            f"A frustum is formed from a cone with a bottom radius of {R} cm and a top radius "
            f"of {r} cm, and a vertical height of {h} cm. Find its volume, correct to 3 "
            "significant figures."
        )
    else:
        l_display = _fmt_sig3(l_exact)
        sa_display = _fmt_sig3(total_sa_exact)
        steps = [
            f"Slant height l = √(h² + (R - r)²) = √({h}² + ({R} - {r})²) ≈ {l_display} cm",
            f"Curved surface area = π × (R + r) × l = π × ({R} + {r}) × {l_display}",
            f"Total surface area = curved + both circular ends = π(R + r)l + πR² + πr²",
            f"= {sa_display} cm² (3 s.f.)",
        ]
        final_answer = f"{sa_display} cm²"
        prompt = (
            f"A frustum is formed from a cone with a bottom radius of {R} cm and a top radius "
            f"of {r} cm, and a vertical height of {h} cm. Find its total surface area, correct "
            "to 3 significant figures."
        )

    return Question(
        topic_id="frustum_volume_surface_area",
        tier=Tier.HIGHER,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=final_answer,
        dedup_key=f"frustum:{R}:{r}:{h}:{measure}",
        diagram=DiagramSpec(
            kind="frustum",
            params={
                "radius_bottom_label": f"{R} cm",
                "radius_top_label": f"{r} cm",
                "height_label": f"{h} cm",
            },
        ),
    )


def generate_modelled_example_frustum_volume_surface_area(tier: Tier, rng: random.Random) -> ModelledExample:
    R, r, h = _frustum_values(rng)
    measure = rng.choice(["volume", "surface_area"])

    H = sp.Rational(R * h, R - r)
    small_h = H - h
    big_cone_volume = sp.Rational(1, 3) * sp.pi * R**2 * H
    small_cone_volume = sp.Rational(1, 3) * sp.pi * r**2 * small_h
    volume_method_1 = big_cone_volume - small_cone_volume
    volume_method_2 = sp.Rational(1, 3) * sp.pi * h * (R**2 + R * r + r**2)
    if sp.simplify(volume_method_1 - volume_method_2) != 0:
        raise ValueError("modelled example frustum_volume_surface_area: volume derivations disagree")

    volume_exact = volume_method_2
    volume_decimal = sp.N(volume_exact, 3)
    volume_float_independent = math.pi * h * (R**2 + R * r + r**2) / 3
    if abs(float(volume_decimal) - volume_float_independent) / volume_float_independent > 0.01:
        raise ValueError("modelled example frustum_volume_surface_area volume verification failed")

    l_exact = sp.sqrt(h**2 + (R - r) ** 2)
    l_float_from_sympy = float(sp.N(l_exact, 10))
    l_float_independent = math.sqrt(h**2 + (R - r) ** 2)
    if abs(l_float_from_sympy - l_float_independent) > 1e-6:
        raise ValueError("modelled example frustum_volume_surface_area slant height verification failed")

    total_sa_exact = sp.pi * (R + r) * l_exact + sp.pi * R**2 + sp.pi * r**2
    sa_decimal = sp.N(total_sa_exact, 3)
    sa_float_independent = math.pi * (R + r) * l_float_independent + math.pi * R**2 + math.pi * r**2
    if abs(float(sa_decimal) - sa_float_independent) / sa_float_independent > 0.01:
        raise ValueError("modelled example frustum_volume_surface_area surface area verification failed")

    similar_triangles_intro = (
        "A frustum is what's left when the pointed tip is sliced off a cone. If you extended "
        "the slanted sides of the frustum back up, they'd meet at a point and rebuild that "
        "missing tip - and because the sides are straight lines, the small triangle formed by "
        "the missing tip is just a scaled-down copy of the whole original triangle. That "
        "'same shape, different size' relationship is called similar triangles, and it's what "
        "lets us work out the height of the (imaginary) full cone even though we're only told "
        "the frustum's own measurements."
    )

    if measure == "volume":
        volume_display = _fmt_sig3(volume_exact)
        teaching_steps = [
            similar_triangles_intro,
            f"Using similar triangles, the full cone's height works out as H = R × h ÷ (R - r) "
            f"= {R} × {h} ÷ ({R} - {r}) = {sp.N(H, 4)} cm, so the missing tip's height is "
            f"H - h = {sp.N(small_h, 4)} cm.",
            "Rather than trust that route alone, there's also a ready-made closed-form "
            "formula for a frustum's volume, (1/3) × π × h × (R² + Rr + r²) - and reassuringly, "
            "both methods give exactly the same answer, which is a good way to check your work "
            "in an exam if you have time.",
            f"Substituting the numbers into the closed-form formula: (1/3) × π × {h} × "
            f"({R}² + {R}×{r} + {r}²) ≈ {volume_display} cm³ (3 s.f.).",
        ]
        worked_calculation = [
            f"Volume = (1/3) × π × h × (R² + Rr + r²)",
            f"= (1/3) × π × {h} × ({R}² + {R}×{r} + {r}²)",
            f"≈ {volume_display} cm³ (3 s.f.)",
        ]
        final_answer = f"{volume_display} cm³"
        prompt = (
            f"A frustum is formed from a cone with a bottom radius of {R} cm and a top radius "
            f"of {r} cm, and a vertical height of {h} cm. Find its volume, correct to 3 "
            "significant figures."
        )
    else:
        l_display = _fmt_sig3(l_exact)
        sa_display = _fmt_sig3(total_sa_exact)
        teaching_steps = [
            "A frustum's total surface area has three parts: the curved sloped surface, the "
            "large circular bottom, and the smaller circular top.",
            f"The slant height (the length of the sloped surface, measured along it - not the "
            f"vertical height) comes from Pythagoras using the frustum's own height and the "
            f"difference between the two radii: l = √(h² + (R - r)²) = √({h}² + ({R} - {r})²) "
            f"≈ {l_display} cm.",
            f"The curved surface area is π × (R + r) × l = π × ({R} + {r}) × {l_display}, and "
            f"the two circular ends contribute π × R² and π × r² respectively.",
            f"Add all three parts together: π({R}+{r})({l_display}) + π×{R}² + π×{r}² ≈ "
            f"{sa_display} cm² (3 s.f.).",
        ]
        worked_calculation = [
            f"l = √({h}² + ({R}-{r})²) ≈ {l_display} cm",
            "Total SA = π(R + r)l + πR² + πr²",
            f"= π({R}+{r})({l_display}) + π×{R}² + π×{r}²",
            f"≈ {sa_display} cm² (3 s.f.)",
        ]
        final_answer = f"{sa_display} cm²"
        prompt = (
            f"A frustum is formed from a cone with a bottom radius of {R} cm and a top radius "
            f"of {r} cm, and a vertical height of {h} cm. Find its total surface area, correct "
            "to 3 significant figures."
        )

    return ModelledExample(
        topic_id="frustum_volume_surface_area",
        tier=Tier.HIGHER,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=final_answer,
        diagram=DiagramSpec(
            kind="frustum",
            params={
                "radius_bottom_label": f"{R} cm",
                "radius_top_label": f"{r} cm",
                "height_label": f"{h} cm",
            },
        ),
    )


# ---------------------------------------------------------------------------
# Topic 4: Compound 3D Shapes (volume)
# ---------------------------------------------------------------------------

def generate_compound_3d_volume(tier: Tier, rng: random.Random) -> Question:
    for _ in range(20):
        variant = rng.choice(["cylinder_hemisphere", "cone_hemisphere", "cuboid_pyramid"])
        if variant in ("cylinder_hemisphere", "cone_hemisphere", "cuboid_pyramid"):
            break
    else:
        raise ValueError("compound_3d_volume could not draw a valid variant")

    if variant == "cylinder_hemisphere":
        radius = rng.randint(2, 10)
        cyl_height = rng.randint(3, 20)

        cyl_vol_exact = sp.pi * radius**2 * cyl_height
        hemi_vol_exact = sp.Rational(2, 3) * sp.pi * radius**3
        volume_exact = cyl_vol_exact + hemi_vol_exact
        decimal_answer = sp.N(volume_exact, 3)

        independent_cyl = math.pi * radius**2 * cyl_height
        independent_hemi = (2 / 3) * math.pi * radius**3
        independent_total = independent_cyl + independent_hemi
        if abs(float(decimal_answer) - independent_total) / independent_total > 0.01:
            raise ValueError("compound_3d_volume (cylinder_hemisphere) verification failed")
        decimal_str = _fmt_sig3(volume_exact)

        steps = [
            f"Cylinder volume = π × r² × h = π × {radius}² × {cyl_height}",
            f"Hemisphere volume = (2/3) × π × r³ = (2/3) × π × {radius}³",
            f"Total volume = cylinder + hemisphere ≈ {decimal_str} cm³ (3 s.f.)",
        ]
        prompt = (
            f"A capsule-shaped solid is made from a cylinder of radius {radius} cm and height "
            f"{cyl_height} cm, with a hemisphere of the same radius attached to one end. Find "
            "the total volume, correct to 3 significant figures."
        )
        dedup_key = f"compound3d:cyl_hemi:{radius}:{cyl_height}"
        diagram = DiagramSpec(
            kind="compound_3d",
            params={
                "variant": "cylinder_hemisphere",
                "radius_label": f"{radius} cm",
                "height_label": f"{cyl_height} cm",
            },
        )
        final_answer = f"{decimal_str} cm³"

    elif variant == "cone_hemisphere":
        radius = rng.randint(2, 10)
        cone_height = rng.randint(3, 20)

        cone_vol_exact = sp.Rational(1, 3) * sp.pi * radius**2 * cone_height
        hemi_vol_exact = sp.Rational(2, 3) * sp.pi * radius**3
        volume_exact = cone_vol_exact + hemi_vol_exact
        decimal_answer = sp.N(volume_exact, 3)

        independent_cone = (1 / 3) * math.pi * radius**2 * cone_height
        independent_hemi = (2 / 3) * math.pi * radius**3
        independent_total = independent_cone + independent_hemi
        if abs(float(decimal_answer) - independent_total) / independent_total > 0.01:
            raise ValueError("compound_3d_volume (cone_hemisphere) verification failed")
        decimal_str = _fmt_sig3(volume_exact)

        steps = [
            f"Cone volume = (1/3) × π × r² × h = (1/3) × π × {radius}² × {cone_height}",
            f"Hemisphere volume = (2/3) × π × r³ = (2/3) × π × {radius}³",
            f"Total volume = cone + hemisphere ≈ {decimal_str} cm³ (3 s.f.)",
        ]
        prompt = (
            f"An ice-cream-shaped solid is made from a cone of radius {radius} cm and height "
            f"{cone_height} cm, with a hemisphere of the same radius attached to its open end. "
            "Find the total volume, correct to 3 significant figures."
        )
        dedup_key = f"compound3d:cone_hemi:{radius}:{cone_height}"
        diagram = DiagramSpec(
            kind="compound_3d",
            params={
                "variant": "cone_hemisphere",
                "radius_label": f"{radius} cm",
                "cone_height_label": f"{cone_height} cm",
            },
        )
        final_answer = f"{decimal_str} cm³"

    else:  # cuboid_pyramid
        base = rng.randint(4, 16)
        box_height = rng.randint(3, 15)
        roof_height = rng.randint(2, 10)

        # Independent check: recompute the cuboid volume via explicit
        # repeated multiplication (base * base * box_height) rather than
        # base**2 * box_height - a different grouping/order of operations.
        cuboid_volume = base**2 * box_height
        cuboid_volume_independent = (base * base) * box_height
        if cuboid_volume_independent != cuboid_volume:
            raise ValueError("compound_3d_volume (cuboid_pyramid) cuboid cross-check failed")

        # Same idea for the pyramid: multiply the base area by height/3 as a
        # fraction, instead of dividing the whole numerator by 3.
        pyramid_volume = sp.Rational(base**2 * roof_height, 3)
        pyramid_volume_regrouped = sp.Rational(base, 1) ** 2 * sp.Rational(roof_height, 3)
        if pyramid_volume_regrouped != pyramid_volume:
            raise ValueError("compound_3d_volume (cuboid_pyramid) pyramid cross-check failed")

        total_volume = cuboid_volume + pyramid_volume
        vol_str = _frac_str(total_volume)

        steps = [
            f"Cuboid volume = base² × height = {base}² × {box_height} = {cuboid_volume} cm³",
            f"Pyramid volume = (1/3) × base² × height = (1/3) × {base}² × {roof_height} = {pyramid_volume} cm³",
            f"Total volume = {cuboid_volume} + {pyramid_volume} = {vol_str} cm³",
        ]
        prompt = (
            f"A silo-shaped solid is made from a cuboid with a square base of side {base} cm "
            f"and height {box_height} cm, with a square-based pyramid of height {roof_height} cm "
            "on top (sharing the same square base). Find the total volume."
        )
        dedup_key = f"compound3d:cuboid_pyr:{base}:{box_height}:{roof_height}"
        diagram = DiagramSpec(
            kind="compound_3d",
            params={
                "variant": "cuboid_pyramid",
                "base_label": f"{base} cm",
                "roof_height_label": f"{roof_height} cm",
            },
        )
        final_answer = f"{vol_str} cm³"

    return Question(
        topic_id="compound_3d_volume",
        tier=Tier.HIGHER,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=final_answer,
        dedup_key=dedup_key,
        diagram=diagram,
    )


def generate_modelled_example_compound_3d_volume(tier: Tier, rng: random.Random) -> ModelledExample:
    for _ in range(20):
        variant = rng.choice(["cylinder_hemisphere", "cone_hemisphere", "cuboid_pyramid"])
        if variant in ("cylinder_hemisphere", "cone_hemisphere", "cuboid_pyramid"):
            break
    else:
        raise ValueError("modelled example compound_3d_volume could not draw a valid variant")

    if variant == "cylinder_hemisphere":
        radius = rng.randint(2, 10)
        cyl_height = rng.randint(3, 20)

        cyl_vol_exact = sp.pi * radius**2 * cyl_height
        hemi_vol_exact = sp.Rational(2, 3) * sp.pi * radius**3
        volume_exact = cyl_vol_exact + hemi_vol_exact
        decimal_answer = sp.N(volume_exact, 3)

        independent_cyl = math.pi * radius**2 * cyl_height
        independent_hemi = (2 / 3) * math.pi * radius**3
        independent_total = independent_cyl + independent_hemi
        if abs(float(decimal_answer) - independent_total) / independent_total > 0.01:
            raise ValueError("modelled example compound_3d_volume (cylinder_hemisphere) verification failed")
        decimal_str = _fmt_sig3(volume_exact)
        cyl_vol_str = _fmt_sig3(cyl_vol_exact)
        hemi_vol_str = _fmt_sig3(hemi_vol_exact)

        teaching_steps = [
            "A compound solid made of two joined shapes has a total volume that's simply the "
            "sum of the two separate volumes - there's no overlap to worry about with volume "
            "(unlike surface area, where the joining face has to be excluded).",
            f"The cylindrical part has volume π × r² × h = π × {radius}² × {cyl_height} ≈ "
            f"{cyl_vol_str} cm³.",
            f"The hemisphere on the end has volume (2/3) × π × r³ = (2/3) × π × {radius}³ ≈ "
            f"{hemi_vol_str} cm³.",
            f"Add the two parts together: {cyl_vol_str} + {hemi_vol_str} "
            f"≈ {decimal_str} cm³ (3 s.f.).",
        ]
        worked_calculation = [
            f"Cylinder = π × {radius}² × {cyl_height} ≈ {cyl_vol_str} cm³",
            f"Hemisphere = (2/3) × π × {radius}³ ≈ {hemi_vol_str} cm³",
            f"Total ≈ {decimal_str} cm³",
        ]
        prompt = (
            f"A capsule-shaped solid is made from a cylinder of radius {radius} cm and height "
            f"{cyl_height} cm, with a hemisphere of the same radius attached to one end. Find "
            "the total volume, correct to 3 significant figures."
        )
        final_answer = f"{decimal_str} cm³"
        diagram = DiagramSpec(
            kind="compound_3d",
            params={
                "variant": "cylinder_hemisphere",
                "radius_label": f"{radius} cm",
                "height_label": f"{cyl_height} cm",
            },
        )

    elif variant == "cone_hemisphere":
        radius = rng.randint(2, 10)
        cone_height = rng.randint(3, 20)

        cone_vol_exact = sp.Rational(1, 3) * sp.pi * radius**2 * cone_height
        hemi_vol_exact = sp.Rational(2, 3) * sp.pi * radius**3
        volume_exact = cone_vol_exact + hemi_vol_exact
        decimal_answer = sp.N(volume_exact, 3)

        independent_cone = (1 / 3) * math.pi * radius**2 * cone_height
        independent_hemi = (2 / 3) * math.pi * radius**3
        independent_total = independent_cone + independent_hemi
        if abs(float(decimal_answer) - independent_total) / independent_total > 0.01:
            raise ValueError("modelled example compound_3d_volume (cone_hemisphere) verification failed")
        decimal_str = _fmt_sig3(volume_exact)
        cone_vol_str = _fmt_sig3(cone_vol_exact)
        hemi_vol_str = _fmt_sig3(hemi_vol_exact)

        teaching_steps = [
            "This 'ice-cream' shape is a cone with a hemisphere sitting on its open end - "
            "again, the total volume is just the two separate volumes added together.",
            f"The cone's volume is (1/3) × π × r² × h = (1/3) × π × {radius}² × {cone_height} "
            f"≈ {cone_vol_str} cm³.",
            f"The hemisphere's volume is (2/3) × π × r³ = (2/3) × π × {radius}³ ≈ "
            f"{hemi_vol_str} cm³.",
            f"Add the two parts: {cone_vol_str} + {hemi_vol_str} ≈ "
            f"{decimal_str} cm³ (3 s.f.).",
        ]
        worked_calculation = [
            f"Cone = (1/3) × π × {radius}² × {cone_height} ≈ {cone_vol_str} cm³",
            f"Hemisphere = (2/3) × π × {radius}³ ≈ {hemi_vol_str} cm³",
            f"Total ≈ {decimal_str} cm³",
        ]
        prompt = (
            f"An ice-cream-shaped solid is made from a cone of radius {radius} cm and height "
            f"{cone_height} cm, with a hemisphere of the same radius attached to its open end. "
            "Find the total volume, correct to 3 significant figures."
        )
        final_answer = f"{decimal_str} cm³"
        diagram = DiagramSpec(
            kind="compound_3d",
            params={
                "variant": "cone_hemisphere",
                "radius_label": f"{radius} cm",
                "cone_height_label": f"{cone_height} cm",
            },
        )

    else:  # cuboid_pyramid
        base = rng.randint(4, 16)
        box_height = rng.randint(3, 15)
        roof_height = rng.randint(2, 10)

        cuboid_volume = base**2 * box_height
        cuboid_volume_independent = (base * base) * box_height
        if cuboid_volume_independent != cuboid_volume:
            raise ValueError("modelled example compound_3d_volume (cuboid_pyramid) cuboid cross-check failed")

        pyramid_volume = sp.Rational(base**2 * roof_height, 3)
        pyramid_volume_regrouped = sp.Rational(base, 1) ** 2 * sp.Rational(roof_height, 3)
        if pyramid_volume_regrouped != pyramid_volume:
            raise ValueError("modelled example compound_3d_volume (cuboid_pyramid) pyramid cross-check failed")

        total_volume = cuboid_volume + pyramid_volume
        vol_str = _frac_str(total_volume)

        teaching_steps = [
            "This 'silo' shape is a cuboid with a square-based pyramid sitting on top, sharing "
            "the same square base - so, as with the other two variants, the total volume is "
            "the sum of the two separate volumes.",
            f"The cuboid's volume is base² × height = {base}² × {box_height} = {cuboid_volume} cm³.",
            f"The pyramid's volume is (1/3) × base² × height = (1/3) × {base}² × {roof_height} "
            f"= {pyramid_volume} cm³ - notice it uses the SAME base² as the cuboid, since they "
            "share a footprint, but its own separate roof height.",
            f"Add the two together: {cuboid_volume} + {pyramid_volume} = {vol_str} cm³.",
        ]
        worked_calculation = [
            f"Cuboid = {base}² × {box_height} = {cuboid_volume} cm³",
            f"Pyramid = (1/3) × {base}² × {roof_height} = {pyramid_volume} cm³",
            f"Total = {cuboid_volume} + {pyramid_volume} = {vol_str} cm³",
        ]
        prompt = (
            f"A silo-shaped solid is made from a cuboid with a square base of side {base} cm "
            f"and height {box_height} cm, with a square-based pyramid of height {roof_height} cm "
            "on top (sharing the same square base). Find the total volume."
        )
        final_answer = f"{vol_str} cm³"
        diagram = DiagramSpec(
            kind="compound_3d",
            params={
                "variant": "cuboid_pyramid",
                "base_label": f"{base} cm",
                "roof_height_label": f"{roof_height} cm",
            },
        )

    return ModelledExample(
        topic_id="compound_3d_volume",
        tier=Tier.HIGHER,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=final_answer,
        diagram=diagram,
    )


# ---------------------------------------------------------------------------
# Topic 5: Compound 3D Shapes (surface area)
# ---------------------------------------------------------------------------
# Unlike volume, surface area must exclude the internal "join" face shared by
# the two component solids (e.g. the flat circle where a hemisphere meets a
# cylinder) - the exact problem compound_3d_volume's original design
# deliberately avoided. All three variants below end up as rounded 3-s.f.
# decimals (unlike compound_3d_volume, where cuboid_pyramid alone was exact)
# since this topic's cuboid_pyramid slant height is routinely irrational -
# matches the sibling standalone pyramid topic's own surface-area branch,
# which accepts the same trade-off for the same reason.

def generate_compound_3d_surface_area(tier: Tier, rng: random.Random) -> Question:
    for _ in range(20):
        variant = rng.choice(["cylinder_hemisphere", "cone_hemisphere", "cuboid_pyramid"])
        if variant in ("cylinder_hemisphere", "cone_hemisphere", "cuboid_pyramid"):
            break
    else:
        raise ValueError("compound_3d_surface_area could not draw a valid variant")

    if variant == "cylinder_hemisphere":
        radius = rng.randint(2, 10)
        cyl_height = rng.randint(3, 20)

        # Exposed surface: cylinder's curved side + cylinder's own flat
        # bottom + hemisphere's curved surface. NOT included: the cylinder's
        # top (covered by the hemisphere) or the hemisphere's flat face
        # (glued to the cylinder top) - both are internal.
        sa_exact = 2 * sp.pi * radius * cyl_height + 3 * sp.pi * radius**2
        decimal_answer = sp.N(sa_exact, 3)

        independent_total = 2 * math.pi * radius * cyl_height + 3 * math.pi * radius**2
        if abs(float(decimal_answer) - independent_total) / independent_total > 0.01:
            raise ValueError("compound_3d_surface_area (cylinder_hemisphere) verification failed")
        decimal_str = _fmt_sig3(sa_exact)

        steps = [
            f"Cylinder curved surface = 2 × π × r × h = 2 × π × {radius} × {cyl_height}",
            f"Cylinder base = π × r² = π × {radius}² (the top is covered by the hemisphere, "
            "so it's excluded)",
            f"Hemisphere curved surface = 2 × π × r² = 2 × π × {radius}² (its flat face is "
            "glued to the cylinder, so it's excluded too)",
            f"Total surface area ≈ {decimal_str} cm² (3 s.f.)",
        ]
        prompt = (
            f"A capsule-shaped solid is made from a cylinder of radius {radius} cm and height "
            f"{cyl_height} cm, with a hemisphere of the same radius attached to one end. Find "
            "the total surface area, correct to 3 significant figures."
        )
        dedup_key = f"compound3d_sa:cyl_hemi:{radius}:{cyl_height}"
        diagram = DiagramSpec(
            kind="compound_3d",
            params={
                "variant": "cylinder_hemisphere",
                "radius_label": f"{radius} cm",
                "height_label": f"{cyl_height} cm",
            },
        )
        final_answer = f"{decimal_str} cm²"

    elif variant == "cone_hemisphere":
        radius = rng.randint(2, 10)
        cone_height = rng.randint(3, 20)

        l_exact = sp.sqrt(radius**2 + cone_height**2)
        l_float_from_sympy = float(sp.N(l_exact, 10))
        # Independent check (a): re-derive l via a second, plain math.sqrt-based
        # float computation rather than sympy's symbolic sqrt.
        l_float_independent = math.sqrt(radius**2 + cone_height**2)
        if abs(l_float_from_sympy - l_float_independent) > 1e-6:
            raise ValueError("compound_3d_surface_area (cone_hemisphere) slant height verification failed")

        # Exposed surface: cone's curved side + hemisphere's curved surface.
        # NOT included: the cone has no base circle here (its open end is
        # where the hemisphere attaches), and the hemisphere's flat face is
        # glued on - both internal.
        sa_exact = sp.pi * radius * l_exact + 2 * sp.pi * radius**2
        decimal_answer = sp.N(sa_exact, 3)

        # Independent check (b): recompute total surface area via a fully
        # separate math-library float computation against the sympy-based one.
        sa_float_independent = math.pi * radius * l_float_independent + 2 * math.pi * radius**2
        if abs(float(decimal_answer) - sa_float_independent) / sa_float_independent > 0.01:
            raise ValueError("compound_3d_surface_area (cone_hemisphere) verification failed")
        decimal_str = _fmt_sig3(sa_exact)
        l_display = _fmt_sig3(l_exact)

        steps = [
            f"Slant height l = √(r² + h²) = √({radius}² + {cone_height}²) ≈ {l_display} cm",
            f"Cone curved surface = π × r × l = π × {radius} × {l_display}",
            f"Hemisphere curved surface = 2 × π × r² = 2 × π × {radius}² (the cone's base and "
            "the hemisphere's flat face are both glued together internally, so neither is exposed)",
            f"Total surface area ≈ {decimal_str} cm² (3 s.f.)",
        ]
        prompt = (
            f"An ice-cream-shaped solid is made from a cone of radius {radius} cm and height "
            f"{cone_height} cm, with a hemisphere of the same radius attached to its open end. "
            "Find the total surface area, correct to 3 significant figures."
        )
        dedup_key = f"compound3d_sa:cone_hemi:{radius}:{cone_height}"
        diagram = DiagramSpec(
            kind="compound_3d",
            params={
                "variant": "cone_hemisphere",
                "radius_label": f"{radius} cm",
                "cone_height_label": f"{cone_height} cm",
            },
        )
        final_answer = f"{decimal_str} cm²"

    else:  # cuboid_pyramid
        base = rng.randint(4, 16)
        box_height = rng.randint(3, 15)
        roof_height = rng.randint(2, 10)

        slant_exact = sp.sqrt(roof_height**2 + sp.Rational(base, 2) ** 2)
        slant_float_from_sympy = float(sp.N(slant_exact, 10))
        slant_float_independent = math.sqrt(roof_height**2 + (base / 2) ** 2)
        if abs(slant_float_from_sympy - slant_float_independent) > 1e-6:
            raise ValueError("compound_3d_surface_area (cuboid_pyramid) slant height verification failed")

        # Exposed surface: cuboid's 4 vertical faces + cuboid's own bottom +
        # pyramid's 4 triangular faces. NOT included: the cuboid's top and the
        # pyramid's own base - the same square, entirely internal between the
        # two solids.
        sa_exact = 4 * base * box_height + base**2 + 2 * base * slant_exact
        decimal_answer = sp.N(sa_exact, 3)

        sa_float_independent = 4 * base * box_height + base**2 + 2 * base * slant_float_independent
        if abs(float(decimal_answer) - sa_float_independent) / sa_float_independent > 0.01:
            raise ValueError("compound_3d_surface_area (cuboid_pyramid) verification failed")
        decimal_str = _fmt_sig3(sa_exact)
        slant_display = _fmt_sig3(slant_exact)

        steps = [
            f"Slant height of a triangular face l = √(roof height² + (base ÷ 2)²) = "
            f"√({roof_height}² + ({base} ÷ 2)²) ≈ {slant_display} cm",
            f"Cuboid's 4 vertical faces = 4 × base × height = 4 × {base} × {box_height}",
            f"Cuboid's base = base² = {base}² (the top is covered by the pyramid, and the "
            "pyramid's own base is the same internal square, so neither is exposed)",
            f"Pyramid's 4 triangular faces = 2 × base × l = 2 × {base} × {slant_display}",
            f"Total surface area ≈ {decimal_str} cm² (3 s.f.)",
        ]
        prompt = (
            f"A silo-shaped solid is made from a cuboid with a square base of side {base} cm "
            f"and height {box_height} cm, with a square-based pyramid of height {roof_height} cm "
            "on top (sharing the same square base). Find the total surface area, correct to 3 "
            "significant figures."
        )
        dedup_key = f"compound3d_sa:cuboid_pyr:{base}:{box_height}:{roof_height}"
        diagram = DiagramSpec(
            kind="compound_3d",
            params={
                "variant": "cuboid_pyramid",
                "base_label": f"{base} cm",
                "roof_height_label": f"{roof_height} cm",
            },
        )
        final_answer = f"{decimal_str} cm²"

    return Question(
        topic_id="compound_3d_surface_area",
        tier=Tier.HIGHER,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=final_answer,
        dedup_key=dedup_key,
        diagram=diagram,
    )


def generate_modelled_example_compound_3d_surface_area(tier: Tier, rng: random.Random) -> ModelledExample:
    for _ in range(20):
        variant = rng.choice(["cylinder_hemisphere", "cone_hemisphere", "cuboid_pyramid"])
        if variant in ("cylinder_hemisphere", "cone_hemisphere", "cuboid_pyramid"):
            break
    else:
        raise ValueError("modelled example compound_3d_surface_area could not draw a valid variant")

    if variant == "cylinder_hemisphere":
        radius = rng.randint(2, 10)
        cyl_height = rng.randint(3, 20)

        sa_exact = 2 * sp.pi * radius * cyl_height + 3 * sp.pi * radius**2
        decimal_answer = sp.N(sa_exact, 3)

        independent_total = 2 * math.pi * radius * cyl_height + 3 * math.pi * radius**2
        if abs(float(decimal_answer) - independent_total) / independent_total > 0.01:
            raise ValueError("modelled example compound_3d_surface_area (cylinder_hemisphere) verification failed")
        decimal_str = _fmt_sig3(sa_exact)
        curved_str = _fmt_sig3(2 * sp.pi * radius * cyl_height)
        base_str = _fmt_sig3(sp.pi * radius**2)
        hemi_str = _fmt_sig3(2 * sp.pi * radius**2)

        teaching_steps = [
            "For a compound solid's surface area, only the faces you can actually see or touch "
            "from outside count - anywhere two parts are glued together, that shared face is "
            "hidden inside the solid and must be left out entirely.",
            f"The cylinder contributes its curved side, 2 × π × r × h = 2 × π × {radius} × "
            f"{cyl_height} ≈ {curved_str} cm², and its own flat bottom, π × r² = π × {radius}² "
            f"≈ {base_str} cm² - but NOT its top, since the hemisphere is glued there.",
            f"The hemisphere contributes only its curved surface, 2 × π × r² = 2 × π × "
            f"{radius}² ≈ {hemi_str} cm² - its flat circular face is the one glued to the "
            "cylinder's top, so it's hidden and doesn't count.",
            f"Add the three exposed pieces together: {curved_str} + {base_str} + {hemi_str} "
            f"≈ {decimal_str} cm² (3 s.f.).",
        ]
        worked_calculation = [
            f"Cylinder curved = 2 × π × {radius} × {cyl_height} ≈ {curved_str} cm²",
            f"Cylinder base = π × {radius}² ≈ {base_str} cm²",
            f"Hemisphere curved = 2 × π × {radius}² ≈ {hemi_str} cm²",
            f"Total ≈ {decimal_str} cm²",
        ]
        prompt = (
            f"A capsule-shaped solid is made from a cylinder of radius {radius} cm and height "
            f"{cyl_height} cm, with a hemisphere of the same radius attached to one end. Find "
            "the total surface area, correct to 3 significant figures."
        )
        final_answer = f"{decimal_str} cm²"
        diagram = DiagramSpec(
            kind="compound_3d",
            params={
                "variant": "cylinder_hemisphere",
                "radius_label": f"{radius} cm",
                "height_label": f"{cyl_height} cm",
            },
        )

    elif variant == "cone_hemisphere":
        radius = rng.randint(2, 10)
        cone_height = rng.randint(3, 20)

        l_exact = sp.sqrt(radius**2 + cone_height**2)
        l_float_from_sympy = float(sp.N(l_exact, 10))
        l_float_independent = math.sqrt(radius**2 + cone_height**2)
        if abs(l_float_from_sympy - l_float_independent) > 1e-6:
            raise ValueError(
                "modelled example compound_3d_surface_area (cone_hemisphere) slant height verification failed"
            )

        sa_exact = sp.pi * radius * l_exact + 2 * sp.pi * radius**2
        decimal_answer = sp.N(sa_exact, 3)

        sa_float_independent = math.pi * radius * l_float_independent + 2 * math.pi * radius**2
        if abs(float(decimal_answer) - sa_float_independent) / sa_float_independent > 0.01:
            raise ValueError("modelled example compound_3d_surface_area (cone_hemisphere) verification failed")
        decimal_str = _fmt_sig3(sa_exact)
        l_display = _fmt_sig3(l_exact)
        cone_str = _fmt_sig3(sp.pi * radius * l_exact)
        hemi_str = _fmt_sig3(2 * sp.pi * radius**2)

        teaching_steps = [
            "As with any compound solid, only the outside-facing surfaces count - wherever the "
            "cone and hemisphere are glued together, that shared circular face is hidden inside "
            "and must be left out.",
            f"First find the cone's slant height using Pythagoras: l = √(r² + h²) = "
            f"√({radius}² + {cone_height}²) ≈ {l_display} cm.",
            f"The cone contributes its curved surface, π × r × l = π × {radius} × {l_display} "
            f"≈ {cone_str} cm² - it has no base circle exposed here, since that's exactly where "
            "the hemisphere attaches.",
            f"The hemisphere contributes only its curved surface, 2 × π × r² = 2 × π × "
            f"{radius}² ≈ {hemi_str} cm² - its flat face is glued to the cone, so it's hidden.",
            f"Add the two exposed pieces: {cone_str} + {hemi_str} ≈ {decimal_str} cm² (3 s.f.).",
        ]
        worked_calculation = [
            f"l = √({radius}² + {cone_height}²) ≈ {l_display} cm",
            f"Cone curved = π × {radius} × {l_display} ≈ {cone_str} cm²",
            f"Hemisphere curved = 2 × π × {radius}² ≈ {hemi_str} cm²",
            f"Total ≈ {decimal_str} cm²",
        ]
        prompt = (
            f"An ice-cream-shaped solid is made from a cone of radius {radius} cm and height "
            f"{cone_height} cm, with a hemisphere of the same radius attached to its open end. "
            "Find the total surface area, correct to 3 significant figures."
        )
        final_answer = f"{decimal_str} cm²"
        diagram = DiagramSpec(
            kind="compound_3d",
            params={
                "variant": "cone_hemisphere",
                "radius_label": f"{radius} cm",
                "cone_height_label": f"{cone_height} cm",
            },
        )

    else:  # cuboid_pyramid
        base = rng.randint(4, 16)
        box_height = rng.randint(3, 15)
        roof_height = rng.randint(2, 10)

        slant_exact = sp.sqrt(roof_height**2 + sp.Rational(base, 2) ** 2)
        slant_float_from_sympy = float(sp.N(slant_exact, 10))
        slant_float_independent = math.sqrt(roof_height**2 + (base / 2) ** 2)
        if abs(slant_float_from_sympy - slant_float_independent) > 1e-6:
            raise ValueError(
                "modelled example compound_3d_surface_area (cuboid_pyramid) slant height verification failed"
            )

        sa_exact = 4 * base * box_height + base**2 + 2 * base * slant_exact
        decimal_answer = sp.N(sa_exact, 3)

        sa_float_independent = 4 * base * box_height + base**2 + 2 * base * slant_float_independent
        if abs(float(decimal_answer) - sa_float_independent) / sa_float_independent > 0.01:
            raise ValueError("modelled example compound_3d_surface_area (cuboid_pyramid) verification failed")
        decimal_str = _fmt_sig3(sa_exact)
        slant_display = _fmt_sig3(slant_exact)
        sides_val = 4 * base * box_height
        pyramid_faces_str = _fmt_sig3(2 * base * slant_exact)

        teaching_steps = [
            "Again, only the outside-facing surfaces count - the cuboid's top and the pyramid's "
            "base are the same square sitting between the two solids, entirely hidden, so both "
            "are left out.",
            f"The cuboid contributes its 4 vertical sides, 4 × base × height = 4 × {base} × "
            f"{box_height} = {sides_val} cm², plus its own bottom, base² = {base}² = "
            f"{base**2} cm² - but not its top.",
            f"The pyramid's slant height (apex to the midpoint of a base edge) comes from "
            f"Pythagoras: l = √(roof height² + (base ÷ 2)²) = √({roof_height}² + "
            f"({base} ÷ 2)²) ≈ {slant_display} cm.",
            f"The pyramid contributes its 4 triangular faces, 2 × base × l = 2 × {base} × "
            f"{slant_display} ≈ {pyramid_faces_str} cm² - but not its own base, since that's "
            "the same square already counted as the cuboid's bottom.",
            f"Add the exposed pieces together: {sides_val} + {base**2} + {pyramid_faces_str} "
            f"≈ {decimal_str} cm² (3 s.f.).",
        ]
        worked_calculation = [
            f"Cuboid sides = 4 × {base} × {box_height} = {sides_val} cm²",
            f"Cuboid base = {base}² = {base**2} cm²",
            f"l = √({roof_height}² + ({base} ÷ 2)²) ≈ {slant_display} cm",
            f"Pyramid faces = 2 × {base} × {slant_display} ≈ {pyramid_faces_str} cm²",
            f"Total ≈ {decimal_str} cm²",
        ]
        prompt = (
            f"A silo-shaped solid is made from a cuboid with a square base of side {base} cm "
            f"and height {box_height} cm, with a square-based pyramid of height {roof_height} cm "
            "on top (sharing the same square base). Find the total surface area, correct to 3 "
            "significant figures."
        )
        final_answer = f"{decimal_str} cm²"
        diagram = DiagramSpec(
            kind="compound_3d",
            params={
                "variant": "cuboid_pyramid",
                "base_label": f"{base} cm",
                "roof_height_label": f"{roof_height} cm",
            },
        )

    return ModelledExample(
        topic_id="compound_3d_surface_area",
        tier=Tier.HIGHER,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=final_answer,
        diagram=diagram,
    )


# ---------------------------------------------------------------------------
# Topic definitions
# ---------------------------------------------------------------------------

TOPIC_VOLUME_SURFACE_AREA_SPHERE = TopicDefinition(
    id="volume_surface_area_sphere",
    display_name="Volume & Surface Area of a Sphere",
    description="Find the volume or total surface area of a sphere or hemisphere.",
    generate=generate_volume_surface_area_sphere,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_volume_surface_area_sphere,
)

TOPIC_VOLUME_SURFACE_AREA_PYRAMID = TopicDefinition(
    id="volume_surface_area_pyramid",
    display_name="Volume & Surface Area of a Pyramid",
    description="Find the volume or total surface area of a square-based pyramid.",
    generate=generate_volume_surface_area_pyramid,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_volume_surface_area_pyramid,
)

TOPIC_FRUSTUM_VOLUME_SURFACE_AREA = TopicDefinition(
    id="frustum_volume_surface_area",
    display_name="Volume & Surface Area of a Frustum",
    description="Find the volume or total surface area of a cone-based frustum.",
    generate=generate_frustum_volume_surface_area,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_frustum_volume_surface_area,
)

TOPIC_COMPOUND_3D_VOLUME = TopicDefinition(
    id="compound_3d_volume",
    display_name="Compound 3D Shapes (Volume)",
    description="Find the volume of a compound solid made from two joined 3D shapes.",
    generate=generate_compound_3d_volume,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_compound_3d_volume,
)

TOPIC_COMPOUND_3D_SURFACE_AREA = TopicDefinition(
    id="compound_3d_surface_area",
    display_name="Compound 3D Shapes (Surface Area)",
    description="Find the surface area of a compound solid made from two joined 3D shapes.",
    generate=generate_compound_3d_surface_area,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_compound_3d_surface_area,
)
