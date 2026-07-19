import random

import sympy as sp

from app.core.models import DiagramSpec, Question, Tier
from app.topics.algebra_utils import X, fmt_linear, solve_linear_with_steps
from app.topics.base import TopicDefinition

SECTION = "geometry"
GROUP = "Angles"


def generate_straight_line(tier: Tier, rng: random.Random) -> Question:
    n = rng.choice([2, 3])
    given: list[int] = []
    remaining = 180
    for i in range(n - 1):
        max_for_this = remaining - 10 * (n - 1 - i)
        angle = rng.randint(10, max(10, min(150, max_for_this)))
        given.append(angle)
        remaining -= angle
    missing = 180 - sum(given)
    if missing < 10:
        raise ValueError("straight_line generation produced an invalid missing angle")

    given_str = ", ".join(f"{a}°" for a in given)
    steps = [
        "Angles on a straight line sum to 180°.",
        f"x = 180 - ({' + '.join(str(a) for a in given)}) = 180 - {sum(given)} = {missing}",
    ]
    return Question(
        topic_id="angles_straight_line",
        tier=Tier.FOUNDATION,
        prompt=f"The angles {given_str} and x° lie on a straight line. Find x.",
        solution_steps=tuple(steps),
        final_answer=str(missing),
        dedup_key=f"straight_line:{given}",
        diagram=DiagramSpec(
            kind="angle_line",
            params={
                "angle_values": given + [missing],
                "labels": [f"{a}°" for a in given] + ["x"],
                "around_point": False,
            },
        ),
    )


def generate_around_point(tier: Tier, rng: random.Random) -> Question:
    n = rng.choice([3, 4])
    given: list[int] = []
    remaining = 360
    for i in range(n - 1):
        max_for_this = remaining - 10 * (n - 1 - i)
        angle = rng.randint(10, max(10, min(150, max_for_this)))
        given.append(angle)
        remaining -= angle
    missing = 360 - sum(given)
    if missing < 10:
        raise ValueError("around_point generation produced an invalid missing angle")

    given_str = ", ".join(f"{a}°" for a in given)
    steps = [
        "Angles around a point sum to 360°.",
        f"x = 360 - ({' + '.join(str(a) for a in given)}) = 360 - {sum(given)} = {missing}",
    ]
    return Question(
        topic_id="angles_around_point",
        tier=Tier.FOUNDATION,
        prompt=f"The angles {given_str} and x° are angles around a point. Find x.",
        solution_steps=tuple(steps),
        final_answer=str(missing),
        dedup_key=f"around_point:{given}",
        diagram=DiagramSpec(
            kind="angle_line",
            params={
                "angle_values": given + [missing],
                "labels": [f"{a}°" for a in given] + ["x"],
                "around_point": True,
            },
        ),
    )


def generate_triangle_angles(tier: Tier, rng: random.Random) -> Question:
    a = rng.randint(20, 120)
    b = rng.randint(20, min(120, 160 - a))
    missing = 180 - a - b
    if missing < 10:
        raise ValueError("triangle_angles generation produced an invalid missing angle")

    steps = [
        "Angles in a triangle sum to 180°.",
        f"x = 180 - ({a} + {b}) = 180 - {a + b} = {missing}",
    ]
    return Question(
        topic_id="angles_triangle",
        tier=Tier.FOUNDATION,
        prompt=f"A triangle has angles {a}°, {b}°, and x°. Find x.",
        solution_steps=tuple(steps),
        final_answer=str(missing),
        dedup_key=f"triangle_angles:{a}:{b}",
        diagram=DiagramSpec(kind="triangle_angles", params={"angle_labels": [f"{a}°", f"{b}°", "x"]}),
    )


def generate_parallel_lines(tier: Tier, rng: random.Random) -> Question:
    fact = rng.choice(["corresponding", "alternate", "co_interior"])
    known = rng.randint(30, 150)
    target = known if fact in ("corresponding", "alternate") else 180 - known
    coeff = rng.choice([2, 3, 4, 5])
    x_sol = rng.randint(1, 20)
    const = target - coeff * x_sol

    fact_text = {
        "corresponding": "Corresponding angles are equal.",
        "alternate": "Alternate angles are equal.",
        "co_interior": "Co-interior angles sum to 180°.",
    }[fact]
    relation = {
        "corresponding": "are corresponding angles",
        "alternate": "are alternate angles",
        "co_interior": "are co-interior angles",
    }[fact]

    solve_steps, solution = solve_linear_with_steps(coeff, const, 0, target)
    residual = sp.simplify((coeff * X + const).subs(X, solution) - target)
    if residual != 0:
        raise ValueError("parallel_lines verification failed")

    prompt = (
        f"A line crosses two parallel lines. The angle {known}° and the angle "
        f"({fmt_linear(coeff, const)})° {relation}. Find x."
    )
    steps = [fact_text] + solve_steps
    return Question(
        topic_id="angles_parallel_lines",
        tier=Tier.HIGHER,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=str(solution),
        dedup_key=f"parallel_lines:{fact}:{known}:{coeff}:{const}",
        diagram=DiagramSpec(
            kind="parallel_lines",
            params={"known_label": f"{known}°", "unknown_label": "x", "relation": fact},
        ),
    )


def generate_exterior_angle(tier: Tier, rng: random.Random) -> Question:
    known_interior = rng.randint(20, 70)
    coeff = rng.choice([2, 3, 4, 5])
    x_sol = rng.randint(1, 20)
    other_interior_value = rng.randint(10, 70)
    const = other_interior_value - coeff * x_sol
    exterior = known_interior + other_interior_value
    if exterior >= 180:
        raise ValueError("exterior_angle generated a non-physical exterior angle")

    solve_steps, solution = solve_linear_with_steps(coeff, const, 0, exterior - known_interior)
    residual = sp.simplify((coeff * X + const).subs(X, solution) - other_interior_value)
    if residual != 0:
        raise ValueError("exterior_angle verification failed")

    prompt = (
        f"An exterior angle of a triangle is {exterior}°. The two remote interior angles are "
        f"{known_interior}° and ({fmt_linear(coeff, const)})°. Find x."
    )
    steps = [
        "The exterior angle of a triangle equals the sum of the two remote interior angles.",
    ] + solve_steps
    return Question(
        topic_id="angles_exterior",
        tier=Tier.HIGHER,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=str(solution),
        dedup_key=f"exterior_angle:{known_interior}:{coeff}:{const}:{exterior}",
        diagram=DiagramSpec(
            kind="exterior_triangle",
            params={
                "interior1_label": f"{known_interior}°",
                "interior2_label": f"({fmt_linear(coeff, const)})°",
                "exterior_label": f"{exterior}°",
            },
        ),
    )


def generate_polygon_interior(tier: Tier, rng: random.Random) -> Question:
    for _ in range(200):
        n = rng.randint(5, 8)
        total = (n - 2) * 180
        other_angle_value = rng.randint(100, 150)
        remaining_total = other_angle_value * (n - 1)
        algebraic_value = total - remaining_total
        if 20 <= algebraic_value <= 170:
            break
    else:
        raise ValueError("polygon_interior could not find valid parameters")

    coeff = rng.choice([2, 3, 4, 5])
    x_sol = rng.randint(1, 20)
    const = algebraic_value - coeff * x_sol

    solve_steps, solution = solve_linear_with_steps(coeff, const, 0, algebraic_value)
    total_check = other_angle_value * (n - 1) + int((coeff * X + const).subs(X, solution))
    if total_check != total:
        raise ValueError("polygon_interior verification failed")

    prompt = (
        f"A polygon has {n} sides. {n - 1} of its interior angles are each {other_angle_value}°, "
        f"and the remaining interior angle is ({fmt_linear(coeff, const)})°. Find x."
    )
    steps = [
        f"Sum of interior angles = (n - 2) × 180 = ({n} - 2) × 180 = {total}°",
        f"Sum of the {n - 1} equal angles = {n - 1} × {other_angle_value} = {remaining_total}°",
        f"Remaining angle = {total} - {remaining_total} = {algebraic_value}°",
    ] + solve_steps
    return Question(
        topic_id="angles_polygon_interior",
        tier=Tier.HIGHER,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=str(solution),
        dedup_key=f"polygon_interior:{n}:{other_angle_value}:{coeff}:{const}",
        diagram=DiagramSpec(
            kind="polygon",
            params={"n_sides": n, "marked_angle_label": f"({fmt_linear(coeff, const)})°"},
        ),
    )


TOPIC_STRAIGHT_LINE = TopicDefinition(
    id="angles_straight_line",
    display_name="On a Straight Line",
    description="Find a missing angle on a straight line (angles sum to 180°).",
    generate=generate_straight_line,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
)

TOPIC_AROUND_POINT = TopicDefinition(
    id="angles_around_point",
    display_name="Around a Point",
    description="Find a missing angle around a point (angles sum to 360°).",
    generate=generate_around_point,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
)

TOPIC_TRIANGLE = TopicDefinition(
    id="angles_triangle",
    display_name="In a Triangle",
    description="Find a missing angle in a triangle (angles sum to 180°).",
    generate=generate_triangle_angles,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
)

TOPIC_PARALLEL_LINES = TopicDefinition(
    id="angles_parallel_lines",
    display_name="Parallel Lines",
    description="Use corresponding, alternate, and co-interior angle facts to solve for x.",
    generate=generate_parallel_lines,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
)

TOPIC_EXTERIOR = TopicDefinition(
    id="angles_exterior",
    display_name="Exterior Angle",
    description="Use the exterior angle theorem to solve for x.",
    generate=generate_exterior_angle,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
)

TOPIC_POLYGON_INTERIOR = TopicDefinition(
    id="angles_polygon_interior",
    display_name="Polygon Interior Angles",
    description="Use the polygon interior angle sum formula to solve for x.",
    generate=generate_polygon_interior,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
)
