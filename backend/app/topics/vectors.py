import random

import sympy as sp

from app.core.models import DiagramSpec, ModelledExample, Question, Tier
from app.topics.base import TopicDefinition

SECTION = "geometry"
GROUP_ARITHMETIC = "Vectors"
GROUP_GEOMETRIC = "Geometric Vectors"

_RATIO_CHOICES = [
    (1, 1), (1, 2), (2, 1), (1, 3), (3, 1), (1, 4), (4, 1), (1, 5), (5, 1),
    (2, 3), (3, 2), (2, 5), (5, 2), (3, 4), (4, 3), (3, 5), (5, 3), (4, 5), (5, 4),
]
_TARGETS = ["OP", "AP", "PB"]


def _fmt_vector(v) -> str:
    return f"({v[0]}, {v[1]})"


def _nonzero_int(rng: random.Random, lo: int, hi: int) -> int:
    while True:
        v = rng.randint(lo, hi)
        if v != 0:
            return v


def _nonzero_pair(rng: random.Random, lo: int, hi: int) -> tuple[int, int]:
    while True:
        x, y = rng.randint(lo, hi), rng.randint(lo, hi)
        if (x, y) != (0, 0):
            return x, y


def _vector_arithmetic(rng: random.Random, *, coord_range: int, k_range, m_range, topic_id: str, tier: Tier) -> Question:
    ax, ay = _nonzero_pair(rng, -coord_range, coord_range)
    bx, by = _nonzero_pair(rng, -coord_range, coord_range)
    k = k_range(rng)
    m = m_range(rng)
    op = rng.choice(["+", "-"])

    if op == "+":
        rx, ry = k * ax + m * bx, k * ay + m * by
    else:
        rx, ry = k * ax - m * bx, k * ay - m * by

    # Independent verification via sympy's Matrix arithmetic - a different library/
    # code path than the manual component-wise arithmetic above.
    A, B = sp.Matrix([ax, ay]), sp.Matrix([bx, by])
    check = k * A + (m * B if op == "+" else -m * B)
    if (int(check[0]), int(check[1])) != (rx, ry):
        raise ValueError("vectors_arithmetic verification failed: sympy cross-check mismatch")

    k_term = "a" if k == 1 else f"{k}a"
    m_term = "b" if m == 1 else f"{m}b"
    expr = f"{k_term} {op} {m_term}"

    steps = [
        f"a = {_fmt_vector((ax, ay))}, b = {_fmt_vector((bx, by))}",
        f"{k_term} = {_fmt_vector((k * ax, k * ay))} and {m_term} = {_fmt_vector((m * bx, m * by))}",
        f"{expr} = {_fmt_vector((rx, ry))}",
    ]
    return Question(
        topic_id=topic_id,
        tier=tier,
        prompt=f"a = {_fmt_vector((ax, ay))} and b = {_fmt_vector((bx, by))}. Find {expr}.",
        solution_steps=tuple(steps),
        final_answer=_fmt_vector((rx, ry)),
        dedup_key=f"vec_arith:{ax}:{ay}:{bx}:{by}:{k}:{m}:{op}",
    )


def _modelled_vector_arithmetic(rng: random.Random, *, coord_range: int, k_range, m_range, topic_id: str, tier: Tier) -> ModelledExample:
    ax, ay = _nonzero_pair(rng, -coord_range, coord_range)
    bx, by = _nonzero_pair(rng, -coord_range, coord_range)
    k = k_range(rng)
    m = m_range(rng)
    op = rng.choice(["+", "-"])

    if op == "+":
        rx, ry = k * ax + m * bx, k * ay + m * by
    else:
        rx, ry = k * ax - m * bx, k * ay - m * by

    # Independent verification via sympy's Matrix arithmetic, same cross-check as the
    # real generator - a different library/code path than the manual arithmetic above.
    A, B = sp.Matrix([ax, ay]), sp.Matrix([bx, by])
    check = k * A + (m * B if op == "+" else -m * B)
    if (int(check[0]), int(check[1])) != (rx, ry):
        raise ValueError("modelled example vectors_arithmetic verification failed: sympy cross-check mismatch")

    k_term = "a" if k == 1 else f"{k}a"
    m_term = "b" if m == 1 else f"{m}b"
    expr = f"{k_term} {op} {m_term}"
    verb = "adding" if op == "+" else "subtracting"

    teaching_steps = [
        "A vector is scaled by multiplying every one of its components by the same number, and two "
        "vectors are combined by adding or subtracting matching components separately - x with x, "
        "and y with y.",
        f"First scale each vector on its own. {k_term} means multiply every component of a by {k}, "
        f"giving {_fmt_vector((k * ax, k * ay))}. Similarly {m_term} means multiply every component "
        f"of b by {m}, giving {_fmt_vector((m * bx, m * by))}.",
        f"Now combine the two scaled vectors component-by-component, {verb} the x-components together "
        "and the y-components together.",
        f"This gives the final answer, {_fmt_vector((rx, ry))}.",
    ]
    worked_calculation = [
        f"a = {_fmt_vector((ax, ay))}, b = {_fmt_vector((bx, by))}",
        f"{k_term} = {_fmt_vector((k * ax, k * ay))}, {m_term} = {_fmt_vector((m * bx, m * by))}",
        f"{expr} = {_fmt_vector((rx, ry))}",
    ]
    return ModelledExample(
        topic_id=topic_id,
        tier=tier,
        prompt=f"a = {_fmt_vector((ax, ay))} and b = {_fmt_vector((bx, by))}. Find {expr}.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=_fmt_vector((rx, ry)),
    )


def generate_modelled_example_vectors_arithmetic_foundation(tier: Tier, rng: random.Random) -> ModelledExample:
    return _modelled_vector_arithmetic(
        rng,
        coord_range=8,
        k_range=lambda r: r.randint(1, 4),
        m_range=lambda r: r.randint(1, 4),
        topic_id="vectors_arithmetic_foundation",
        tier=Tier.FOUNDATION,
    )


def generate_modelled_example_vectors_arithmetic_higher(tier: Tier, rng: random.Random) -> ModelledExample:
    return _modelled_vector_arithmetic(
        rng,
        coord_range=12,
        k_range=lambda r: _nonzero_int(r, -5, 5),
        m_range=lambda r: _nonzero_int(r, -5, 5),
        topic_id="vectors_arithmetic_higher",
        tier=Tier.HIGHER,
    )


def generate_vectors_arithmetic_foundation(tier: Tier, rng: random.Random) -> Question:
    return _vector_arithmetic(
        rng,
        coord_range=8,
        k_range=lambda r: r.randint(1, 4),
        m_range=lambda r: r.randint(1, 4),
        topic_id="vectors_arithmetic_foundation",
        tier=Tier.FOUNDATION,
    )


def generate_vectors_arithmetic_higher(tier: Tier, rng: random.Random) -> Question:
    return _vector_arithmetic(
        rng,
        coord_range=12,
        k_range=lambda r: _nonzero_int(r, -5, 5),
        m_range=lambda r: _nonzero_int(r, -5, 5),
        topic_id="vectors_arithmetic_higher",
        tier=Tier.HIGHER,
    )


def _fmt_magnitude(mag: sp.Rational, letter: str) -> str:
    if mag == 1:
        return letter
    if mag.is_Integer:
        return f"{int(mag)}{letter}"
    return f"({mag.p}/{mag.q}){letter}"


def _fmt_signed_term(coeff: sp.Rational, letter: str, is_first: bool) -> str:
    if coeff == 0:
        return ""
    term = _fmt_magnitude(abs(coeff), letter)
    if is_first:
        return f"-{term}" if coeff < 0 else term
    return f"{'-' if coeff < 0 else '+'} {term}"


def _fmt_vector_expr(coeff_a: sp.Rational, coeff_b: sp.Rational) -> str:
    parts = [p for p in [_fmt_signed_term(coeff_a, "a", is_first=True)] if p]
    b_term = _fmt_signed_term(coeff_b, "b", is_first=not parts)
    if b_term:
        parts.append(b_term)
    return " ".join(parts) if parts else "0"


def generate_geometric_vectors(tier: Tier, rng: random.Random) -> Question:
    m, n = rng.choice(_RATIO_CHOICES)
    target = rng.choice(_TARGETS)
    t = sp.Rational(m, m + n)

    # Coefficients of a, b for O, A, B, and P as positions in the {a, b} basis.
    O_pos, A_pos, B_pos = (sp.Integer(0), sp.Integer(0)), (sp.Integer(1), sp.Integer(0)), (sp.Integer(0), sp.Integer(1))
    P_pos = (1 - t, t)
    positions = {"O": O_pos, "A": A_pos, "B": B_pos, "P": P_pos}

    start, end = target[0], target[1]
    coeff_a = positions[end][0] - positions[start][0]
    coeff_b = positions[end][1] - positions[start][1]

    # Independent verification via numeric coordinate substitution: place a and b as
    # concrete 2D vectors (not symbols), compute P's actual coordinates from the ratio,
    # then check the symbolic coefficients reconstruct the same target vector - a
    # different method than the position-vector algebra above.
    a_num, b_num = (1.0, 0.0), (0.0, 2.0)
    o_num = (0.0, 0.0)
    p_num = (
        a_num[0] + float(t) * (b_num[0] - a_num[0]),
        a_num[1] + float(t) * (b_num[1] - a_num[1]),
    )
    coord_map = {"O": o_num, "A": a_num, "B": b_num, "P": p_num}
    target_num = (coord_map[end][0] - coord_map[start][0], coord_map[end][1] - coord_map[start][1])
    reconstructed = (float(coeff_a) * a_num[0] + float(coeff_b) * b_num[0], float(coeff_a) * a_num[1] + float(coeff_b) * b_num[1])
    if abs(reconstructed[0] - target_num[0]) > 1e-9 or abs(reconstructed[1] - target_num[1]) > 1e-9:
        raise ValueError("geometric_vectors verification failed: coordinate cross-check mismatch")

    point_label = "M" if m == n else "P"
    vec_name = {"OP": f"O{point_label}", "AP": f"A{point_label}", "PB": f"{point_label}B"}[target]
    answer = _fmt_vector_expr(coeff_a, coeff_b)

    steps = [
        "AB = OB - OA = b - a",
        f"A{point_label} = ({m}/{m + n})AB = ({m}/{m + n})(b - a)",
    ]
    if target == "OP":
        steps.append(f"{vec_name} = OA + A{point_label} = a + ({m}/{m + n})(b - a) = {answer}")
    elif target == "AP":
        steps.append(f"{vec_name} = ({m}/{m + n})(b - a) = {answer}")
    else:
        steps.append(f"{vec_name} = OB - O{point_label} = {answer}")

    return Question(
        topic_id="geometric_vectors",
        tier=Tier.HIGHER,
        prompt=(
            f"OAB is a triangle with OA = a and OB = b. Point {point_label} lies on AB such that "
            f"A{point_label}:{point_label}B = {m}:{n}. Find the vector {vec_name} in terms of "
            "a and b, giving your answer in its simplest form."
        ),
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"geo_vec:{m}:{n}:{target}",
        diagram=DiagramSpec(
            kind="vector_triangle",
            params={"ratio": [m, n], "point_label": point_label, "a_label": "a", "b_label": "b", "origin_label": "O"},
        ),
    )


def generate_modelled_example_geometric_vectors(tier: Tier, rng: random.Random) -> ModelledExample:
    m, n = rng.choice(_RATIO_CHOICES)
    target = rng.choice(_TARGETS)
    t = sp.Rational(m, m + n)

    O_pos, A_pos, B_pos = (sp.Integer(0), sp.Integer(0)), (sp.Integer(1), sp.Integer(0)), (sp.Integer(0), sp.Integer(1))
    P_pos = (1 - t, t)
    positions = {"O": O_pos, "A": A_pos, "B": B_pos, "P": P_pos}

    start, end = target[0], target[1]
    coeff_a = positions[end][0] - positions[start][0]
    coeff_b = positions[end][1] - positions[start][1]

    # Independent verification via numeric coordinate substitution, same cross-check
    # as the real generator: place a and b as concrete 2D vectors, compute P's actual
    # coordinates from the ratio, then check the symbolic coefficients reconstruct the
    # same target vector.
    a_num, b_num = (1.0, 0.0), (0.0, 2.0)
    o_num = (0.0, 0.0)
    p_num = (
        a_num[0] + float(t) * (b_num[0] - a_num[0]),
        a_num[1] + float(t) * (b_num[1] - a_num[1]),
    )
    coord_map = {"O": o_num, "A": a_num, "B": b_num, "P": p_num}
    target_num = (coord_map[end][0] - coord_map[start][0], coord_map[end][1] - coord_map[start][1])
    reconstructed = (float(coeff_a) * a_num[0] + float(coeff_b) * b_num[0], float(coeff_a) * a_num[1] + float(coeff_b) * b_num[1])
    if abs(reconstructed[0] - target_num[0]) > 1e-9 or abs(reconstructed[1] - target_num[1]) > 1e-9:
        raise ValueError("modelled example geometric_vectors verification failed: coordinate cross-check mismatch")

    point_label = "M" if m == n else "P"
    vec_name = {"OP": f"O{point_label}", "AP": f"A{point_label}", "PB": f"{point_label}B"}[target]
    answer = _fmt_vector_expr(coeff_a, coeff_b)

    teaching_steps = [
        "The key idea is that any point sitting on a straight line between two other points can be "
        "written as a fraction of the way along the vector connecting them - so the first job is "
        "always to find that connecting vector.",
        "AB = OB - OA = b - a, since travelling from A to B is the same as undoing the trip from O to "
        "A, then making the trip from O to B.",
        f"{point_label} divides AB in the ratio {m}:{n}, so it sits ({m}/{m + n}) of the way from A to "
        f"B: A{point_label} = ({m}/{m + n})AB = ({m}/{m + n})(b - a).",
    ]
    worked_calculation = [
        "AB = OB - OA = b - a",
        f"A{point_label} = ({m}/{m + n})(b - a)",
    ]
    if target == "OP":
        teaching_steps.append(
            f"To reach {vec_name} starting from the origin O, first travel to A (that's vector a), "
            f"then continue along A{point_label}: {vec_name} = OA + A{point_label} = "
            f"a + ({m}/{m + n})(b - a) = {answer}."
        )
        worked_calculation.append(f"{vec_name} = a + ({m}/{m + n})(b - a) = {answer}")
    elif target == "AP":
        teaching_steps.append(
            f"{vec_name} IS the vector A{point_label} that was just found, so no extra work is needed "
            f"here: {vec_name} = ({m}/{m + n})(b - a) = {answer}."
        )
        worked_calculation.append(f"{vec_name} = {answer}")
    else:
        teaching_steps.append(
            f"{vec_name} is whatever is left of the journey from {point_label} to B, which is the "
            f"whole trip OB minus the part already travelled, O{point_label}: "
            f"{vec_name} = OB - O{point_label} = {answer}."
        )
        worked_calculation.append(f"{vec_name} = OB - O{point_label} = {answer}")

    return ModelledExample(
        topic_id="geometric_vectors",
        tier=Tier.HIGHER,
        prompt=(
            f"OAB is a triangle with OA = a and OB = b. Point {point_label} lies on AB such that "
            f"A{point_label}:{point_label}B = {m}:{n}. Find the vector {vec_name} in terms of "
            "a and b, giving your answer in its simplest form."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
        diagram=DiagramSpec(
            kind="vector_triangle",
            params={"ratio": [m, n], "point_label": point_label, "a_label": "a", "b_label": "b", "origin_label": "O"},
        ),
    )


TOPIC_VECTORS_ARITHMETIC_FOUNDATION = TopicDefinition(
    id="vectors_arithmetic_foundation",
    display_name="Vector Arithmetic",
    description="Add, subtract, and scale column vectors.",
    generate=generate_vectors_arithmetic_foundation,
    section=SECTION,
    group=GROUP_ARITHMETIC,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_vectors_arithmetic_foundation,
)

TOPIC_VECTORS_ARITHMETIC_HIGHER = TopicDefinition(
    id="vectors_arithmetic_higher",
    display_name="Vector Arithmetic",
    description="Add, subtract, and scale column vectors, including negative scalars.",
    generate=generate_vectors_arithmetic_higher,
    section=SECTION,
    group=GROUP_ARITHMETIC,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_vectors_arithmetic_higher,
)

TOPIC_GEOMETRIC_VECTORS = TopicDefinition(
    id="geometric_vectors",
    display_name="Vector Geometry",
    description="Express a vector between two points on a triangle in terms of given position vectors.",
    generate=generate_geometric_vectors,
    section=SECTION,
    group=GROUP_GEOMETRIC,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_geometric_vectors,
)
