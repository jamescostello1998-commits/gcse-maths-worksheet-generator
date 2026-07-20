import random

import sympy as sp

from app.core.models import DiagramSpec, ModelledExample, Question, Tier
from app.topics.algebra_utils import X, fmt_linear, fmt_num
from app.topics.base import TopicDefinition

SECTION = "algebra"
GROUP_PLOTTING = "Plotting Graphs"
GROUP_LINE_EQUATION = "Equation of a Line"
GROUP_REAL_LIFE = "Real-Life Graphs"
GROUP_TRANSFORMATIONS = "Transformations of Graphs"

PLOTTING_QUESTION_COUNT = 5

_TEST_FN = X**2 + 2 * X - 1  # fixed internal function used only to cross-check transformation rules


def _rand_nonzero(rng: random.Random, lo: int, hi: int) -> int:
    while True:
        v = rng.randint(lo, hi)
        if v != 0:
            return v


def _fmt_quadratic(a: int, b: int, c: int) -> str:
    lead = "x^2" if a == 1 else ("-x^2" if a == -1 else f"{a}x^2")
    parts = [lead]
    if b != 0:
        term = "x" if abs(b) == 1 else f"{abs(b)}x"
        parts.append(f"{'+' if b > 0 else '-'} {term}")
    if c != 0:
        parts.append(f"{'+' if c > 0 else '-'} {abs(c)}")
    return " ".join(parts)


def _fmt_cubic(a: int, b: int) -> str:
    lead = "x^3" if a == 1 else ("-x^3" if a == -1 else f"{a}x^3")
    parts = [lead]
    if b != 0:
        term = "x" if abs(b) == 1 else f"{abs(b)}x"
        parts.append(f"{'+' if b > 0 else '-'} {term}")
    return " ".join(parts)


def _fmt_reciprocal(a: int) -> str:
    return f"{a}/x" if a > 0 else f"-{abs(a)}/x"


def generate_plot_straight_line(tier: Tier, rng: random.Random) -> Question:
    m = _rand_nonzero(rng, -4, 4)
    c = rng.randint(-6, 6)
    xs = list(range(-3, 4))
    ys = [m * x + c for x in xs]

    # Independent check: consecutive differences must all equal the gradient
    # (a different computation path than the direct y = mx + c substitution
    # used to build the table above), and re-deriving (m, c) from just the
    # two endpoints via an independent linear solve must reproduce them.
    diffs = {ys[i + 1] - ys[i] for i in range(len(ys) - 1)}
    if diffs != {m}:
        raise ValueError("plot_straight_line verification failed: non-constant gradient")
    M, C = sp.symbols("M C")
    solved = sp.solve([sp.Eq(M * xs[0] + C, ys[0]), sp.Eq(M * xs[-1] + C, ys[-1])], [M, C])
    if solved.get(M) != m or solved.get(C) != c:
        raise ValueError("plot_straight_line verification failed: endpoint solve mismatch")

    table_points = list(zip(xs, ys))
    x_min, x_max = xs[0] - 1, xs[-1] + 1
    y_min, y_max = min(ys) - 1, max(ys) + 1

    steps = [
        f"Table of values for y = {fmt_linear(m, c)}:",
        "x: " + ", ".join(str(x) for x in xs),
        "y: " + ", ".join(str(y) for y in ys),
        "Plot each (x, y) point and join them with a single ruled straight line.",
    ]
    return Question(
        topic_id="plot_straight_line",
        tier=Tier.FOUNDATION,
        prompt=f"Complete a table of values for y = {fmt_linear(m, c)} for x = -3 to 3, then plot the graph.",
        solution_steps=tuple(steps),
        final_answer=f"Straight line: y = {fmt_linear(m, c)}",
        dedup_key=f"plot_line:{m}:{c}",
        diagram=DiagramSpec(
            kind="function_graph",
            params={
                "kind": "linear", "m": m, "c": c,
                "x_min": x_min, "x_max": x_max, "y_min": y_min, "y_max": y_max,
                "blank": True,
            },
        ),
        solution_diagram=DiagramSpec(
            kind="function_graph",
            params={
                "kind": "linear", "m": m, "c": c,
                "x_min": x_min, "x_max": x_max, "y_min": y_min, "y_max": y_max,
                "table_points": table_points,
            },
        ),
    )


def generate_plot_quadratic(tier: Tier, rng: random.Random) -> Question:
    a = rng.choice([1, -1])
    b = rng.randint(-2, 2)
    c = rng.randint(-4, 4)
    xs = list(range(-3, 4))
    ys = [a * x * x + b * x + c for x in xs]

    # Independent check: for a quadratic sampled at unit steps, the second
    # finite differences must be constant and equal to 2a - a genuinely
    # different method (numerical differencing) than the direct
    # substitution used to build the table above.
    first_diffs = [ys[i + 1] - ys[i] for i in range(len(ys) - 1)]
    second_diffs = {first_diffs[i + 1] - first_diffs[i] for i in range(len(first_diffs) - 1)}
    if second_diffs != {2 * a}:
        raise ValueError("plot_quadratic verification failed: non-constant second difference")

    table_points = list(zip(xs, ys))
    x_min, x_max = xs[0] - 1, xs[-1] + 1
    y_min, y_max = min(ys) - 1, max(ys) + 1

    steps = [
        f"Table of values for y = {_fmt_quadratic(a, b, c)}:",
        "x: " + ", ".join(str(x) for x in xs),
        "y: " + ", ".join(str(y) for y in ys),
        "Plot each (x, y) point and join them with a single smooth curve.",
    ]
    return Question(
        topic_id="plot_quadratic",
        tier=Tier.FOUNDATION,
        prompt=f"Complete a table of values for y = {_fmt_quadratic(a, b, c)} for x = -3 to 3, then plot the graph.",
        solution_steps=tuple(steps),
        final_answer=f"Quadratic curve: y = {_fmt_quadratic(a, b, c)}",
        dedup_key=f"plot_quad:{a}:{b}:{c}",
        diagram=DiagramSpec(
            kind="function_graph",
            params={
                "kind": "quadratic", "a": a, "b": b, "c": c,
                "x_min": x_min, "x_max": x_max, "y_min": y_min, "y_max": y_max,
                "blank": True,
            },
        ),
        solution_diagram=DiagramSpec(
            kind="function_graph",
            params={
                "kind": "quadratic", "a": a, "b": b, "c": c,
                "x_min": x_min, "x_max": x_max, "y_min": y_min, "y_max": y_max,
                "table_points": table_points,
            },
        ),
    )


def generate_plot_cubic(tier: Tier, rng: random.Random) -> Question:
    a = rng.choice([1, -1])
    b = rng.randint(-3, 3)
    xs = list(range(-3, 4))
    ys = [a * x**3 + b * x for x in xs]

    # Independent check: for a cubic sampled at unit steps, the third finite
    # differences must be constant and equal to 6a.
    d1 = [ys[i + 1] - ys[i] for i in range(len(ys) - 1)]
    d2 = [d1[i + 1] - d1[i] for i in range(len(d1) - 1)]
    d3 = {d2[i + 1] - d2[i] for i in range(len(d2) - 1)}
    if d3 != {6 * a}:
        raise ValueError("plot_cubic verification failed: non-constant third difference")

    table_points = list(zip(xs, ys))
    x_min, x_max = xs[0] - 1, xs[-1] + 1
    y_min, y_max = min(ys) - 2, max(ys) + 2

    steps = [
        f"Table of values for y = {_fmt_cubic(a, b)}:",
        "x: " + ", ".join(str(x) for x in xs),
        "y: " + ", ".join(str(y) for y in ys),
        "Plot each (x, y) point and join them with a single smooth curve.",
    ]
    return Question(
        topic_id="plot_cubic",
        tier=Tier.HIGHER,
        prompt=f"Complete a table of values for y = {_fmt_cubic(a, b)} for x = -3 to 3, then plot the graph.",
        solution_steps=tuple(steps),
        final_answer=f"Cubic curve: y = {_fmt_cubic(a, b)}",
        dedup_key=f"plot_cubic:{a}:{b}",
        diagram=DiagramSpec(
            kind="function_graph",
            params={
                "kind": "cubic", "a": a, "b": b,
                "x_min": x_min, "x_max": x_max, "y_min": y_min, "y_max": y_max,
                "blank": True,
            },
        ),
        solution_diagram=DiagramSpec(
            kind="function_graph",
            params={
                "kind": "cubic", "a": a, "b": b,
                "x_min": x_min, "x_max": x_max, "y_min": y_min, "y_max": y_max,
                "table_points": table_points,
            },
        ),
    )


def generate_plot_reciprocal(tier: Tier, rng: random.Random) -> Question:
    magnitude = rng.choice([12, 24, 36, 48])
    sign = rng.choice([1, -1])
    a = magnitude * sign
    xs = [-4, -3, -2, -1, 1, 2, 3, 4]
    ys = [a // x for x in xs]

    # Independent check: cross-multiplication x * y == a for every table
    # point - a different method than the division used to build the table.
    if any(x * y != a for x, y in zip(xs, ys)):
        raise ValueError("plot_reciprocal verification failed: cross-multiplication mismatch")

    table_points = list(zip(xs, ys))
    y_bound = max(abs(y) for y in ys) + 2

    steps = [
        f"Table of values for y = {_fmt_reciprocal(a)}:",
        "x: " + ", ".join(str(x) for x in xs),
        "y: " + ", ".join(str(y) for y in ys),
        "Plot each (x, y) point. The graph has two separate curved branches and never touches x = 0.",
    ]
    return Question(
        topic_id="plot_reciprocal",
        tier=Tier.HIGHER,
        prompt=(
            f"Complete a table of values for y = {_fmt_reciprocal(a)} for x = -4, -3, -2, -1, 1, 2, 3, 4, "
            "then plot the graph."
        ),
        solution_steps=tuple(steps),
        final_answer=f"Reciprocal curve: y = {_fmt_reciprocal(a)}",
        dedup_key=f"plot_recip:{a}",
        diagram=DiagramSpec(
            kind="function_graph",
            params={
                "kind": "reciprocal", "a": a,
                "x_min": -4, "x_max": 4, "y_min": -y_bound, "y_max": y_bound,
                "blank": True,
            },
        ),
        solution_diagram=DiagramSpec(
            kind="function_graph",
            params={
                "kind": "reciprocal", "a": a,
                "x_min": -4, "x_max": 4, "y_min": -y_bound, "y_max": y_bound,
                "table_points": table_points,
            },
        ),
    )


def generate_plot_distance_time(tier: Tier, rng: random.Random) -> Question:
    distance = rng.choice([4, 5, 6, 8, 10])
    t_out = rng.choice([10, 15, 20, 25])
    t_rest = rng.choice([5, 10, 15])
    t_back = rng.choice([10, 15, 20, 25, 30])
    t1, t2, t3 = t_out, t_out + t_rest, t_out + t_rest + t_back
    points = [(0, 0), (t1, distance), (t2, distance), (t3, 0)]

    # Independent check: total distance travelled (there and back) computed
    # by doubling the one-way distance must equal the sum of the absolute
    # distance changes across every leg of the journey - a different method.
    direct_total = 2 * distance
    leg_total = sum(abs(points[i + 1][1] - points[i][1]) for i in range(len(points) - 1))
    if direct_total != leg_total:
        raise ValueError("plot_distance_time verification failed: total distance mismatch")

    steps = [
        f"Set out at 0 minutes, 0 km. Travel at a constant speed, arriving at {distance} km after {t1} minutes.",
        f"Stay at {distance} km until {t2} minutes.",
        f"Return at a constant speed to 0 km, arriving home at {t3} minutes.",
        "Plot these points and join each stage with a straight line segment.",
        f"Total distance travelled = {distance} km out + {distance} km back = {direct_total} km",
    ]
    return Question(
        topic_id="plot_distance_time",
        tier=Tier.FOUNDATION,
        prompt=(
            f"A cyclist leaves home at 0 minutes. They cycle at a constant speed, reaching a shop {distance} km "
            f"away after {t1} minutes. They stay at the shop until {t2} minutes, then cycle straight back home at "
            f"a constant speed, arriving home at {t3} minutes. Draw a distance-time graph to show this journey, "
            "and find the total distance travelled."
        ),
        solution_steps=tuple(steps),
        final_answer=f"{direct_total} km",
        dedup_key=f"plot_dt:{distance}:{t_out}:{t_rest}:{t_back}",
        diagram=DiagramSpec(
            kind="piecewise_graph",
            params={
                "points": points, "x_max": t3 + 5, "y_max": distance + 2,
                "x_label": "Time (minutes)", "y_label": "Distance (km)",
                "blank": True,
            },
        ),
        solution_diagram=DiagramSpec(
            kind="piecewise_graph",
            params={
                "points": points, "x_max": t3 + 5, "y_max": distance + 2,
                "x_label": "Time (minutes)", "y_label": "Distance (km)",
            },
        ),
    )


def generate_line_equation_from_graph(tier: Tier, rng: random.Random) -> Question:
    m = _rand_nonzero(rng, -4, 4)
    c = rng.randint(-6, 6)
    x1 = rng.randint(-4, -1)
    x2 = rng.randint(1, 4)
    y1, y2 = m * x1 + c, m * x2 + c

    # Independent check: re-derive (m, c) from just the two marked points via
    # an independent symbolic solve, rather than the formula used above.
    M, C = sp.symbols("M C")
    solved = sp.solve([sp.Eq(M * x1 + C, y1), sp.Eq(M * x2 + C, y2)], [M, C])
    if solved.get(M) != m or solved.get(C) != c:
        raise ValueError("line_equation_from_graph verification failed")

    x_min, x_max = x1 - 1, x2 + 1
    end_ys = [m * x_min + c, m * x_max + c, y1, y2]
    y_min, y_max = min(end_ys) - 1, max(end_ys) + 1

    steps = [
        f"Gradient = rise/run = ({y2} - {y1}) / ({x2} - {x1}) = {m}",
        f"Using y = mx + c with the point ({x1}, {y1}): {y1} = {m}×({x1}) + c, so c = {c}",
        f"Equation of the line: y = {fmt_linear(m, c)}",
    ]
    return Question(
        topic_id="line_equation_from_graph",
        tier=Tier.FOUNDATION,
        prompt="The graph shows a straight line. Find the equation of the line in the form y = mx + c.",
        solution_steps=tuple(steps),
        final_answer=f"y = {fmt_linear(m, c)}",
        dedup_key=f"line_from_graph:{m}:{c}:{x1}:{x2}",
        diagram=DiagramSpec(
            kind="function_graph",
            params={
                "kind": "linear", "m": m, "c": c,
                "x_min": x_min, "x_max": x_max, "y_min": y_min, "y_max": y_max,
                "table_points": [[x1, y1], [x2, y2]],
            },
        ),
    )


def generate_parallel_lines_equation(tier: Tier, rng: random.Random) -> Question:
    m = _rand_nonzero(rng, -5, 5)
    c1 = rng.randint(-8, 8)
    x0 = _rand_nonzero(rng, -6, 6)
    y0 = rng.randint(-10, 10)
    while y0 == m * x0 + c1:
        y0 = rng.randint(-10, 10)
    c2 = y0 - m * x0

    # Independent check: re-derive c2 via a separate symbolic solve of the
    # "point lies on the new line" condition, rather than direct arithmetic.
    C = sp.symbols("C")
    solved = sp.solve(sp.Eq(m * x0 + C, y0), C)
    if solved[0] != c2:
        raise ValueError("parallel_lines_equation verification failed")

    steps = [
        f"Parallel lines have the same gradient, so m = {m}.",
        f"Substitute ({x0}, {y0}) into y = {m}x + c: {y0} = {m}×({x0}) + c, so c = {c2}",
        f"Equation of the line: y = {fmt_linear(m, c2)}",
    ]
    return Question(
        topic_id="parallel_lines_equation",
        tier=Tier.FOUNDATION,
        prompt=(
            f"A line is parallel to y = {fmt_linear(m, c1)} and passes through the point ({x0}, {y0}). "
            "Find the equation of the line."
        ),
        solution_steps=tuple(steps),
        final_answer=f"y = {fmt_linear(m, c2)}",
        dedup_key=f"parallel:{m}:{c1}:{x0}:{y0}",
    )


def generate_perpendicular_lines_equation(tier: Tier, rng: random.Random) -> Question:
    m1 = _rand_nonzero(rng, -5, 5)
    c1 = rng.randint(-8, 8)
    m2 = sp.Rational(-1, m1)
    x0 = _rand_nonzero(rng, -6, 6)
    y0 = rng.randint(-10, 10)
    c2 = sp.Rational(y0) - m2 * x0

    # Independent check: the product of perpendicular gradients must be -1
    # (a different fact than the substitution used to find c2), and the
    # point must satisfy the new line.
    if sp.simplify(m1 * m2 + 1) != 0:
        raise ValueError("perpendicular_lines_equation verification failed: gradients not perpendicular")
    if sp.simplify(m2 * x0 + c2 - y0) != 0:
        raise ValueError("perpendicular_lines_equation verification failed: point does not satisfy new line")

    steps = [
        f"Perpendicular gradients multiply to give -1: m × {m1} = -1, so m = {fmt_num(m2)}",
        f"Substitute ({x0}, {y0}) into y = {fmt_num(m2)}x + c: {y0} = {fmt_num(m2)}×({x0}) + c, so c = {fmt_num(c2)}",
        f"Equation of the line: y = {fmt_linear(m2, c2)}",
    ]
    return Question(
        topic_id="perpendicular_lines_equation",
        tier=Tier.HIGHER,
        prompt=(
            f"A line is perpendicular to y = {fmt_linear(m1, c1)} and passes through the point ({x0}, {y0}). "
            "Find the equation of the line."
        ),
        solution_steps=tuple(steps),
        final_answer=f"y = {fmt_linear(m2, c2)}",
        dedup_key=f"perp:{m1}:{c1}:{x0}:{y0}",
    )


def generate_distance_time_interpret(tier: Tier, rng: random.Random) -> Question:
    distance = rng.choice([4, 5, 6, 8, 9, 10, 12])
    t_out = rng.choice([10, 15, 20, 24, 25, 30])
    t_rest = rng.choice([5, 10, 15, 20])
    t_back = rng.choice([10, 15, 20, 25, 30, 40])
    t1, t2, t3 = t_out, t_out + t_rest, t_out + t_rest + t_back
    points = [(0, 0), (t1, distance), (t2, distance), (t3, 0)]
    question_kind = rng.choice(["outbound_speed", "rest_duration", "total_distance", "average_speed"])

    # Independent check: outbound speed via distance/time in hours, cross-checked
    # by converting minutes to hours first (a different order of operations).
    outbound_speed_kmh = sp.Rational(distance, t_out) * 60
    outbound_speed_check = sp.Rational(distance) / sp.Rational(t_out, 60)
    if sp.simplify(outbound_speed_kmh - outbound_speed_check) != 0:
        raise ValueError("distance_time_interpret verification failed: outbound speed mismatch")

    # Independent check: total distance via doubling vs summing leg-by-leg changes.
    total_distance = 2 * distance
    leg_total = sum(abs(points[i + 1][1] - points[i][1]) for i in range(len(points) - 1))
    if total_distance != leg_total:
        raise ValueError("distance_time_interpret verification failed: total distance mismatch")

    average_speed_kmh = sp.Rational(total_distance, t3) * 60

    diagram = DiagramSpec(
        kind="piecewise_graph",
        params={
            "points": points, "x_max": t3 + 5, "y_max": distance + 2,
            "x_label": "Time (minutes)", "y_label": "Distance (km)",
        },
    )

    if question_kind == "outbound_speed":
        prompt = (
            "The distance-time graph shows a delivery van's journey. Find its speed during the outbound leg "
            "of the journey, in km/h."
        )
        steps = [
            f"Outbound: {distance} km in {t_out} minutes = {distance} km in {fmt_num(sp.Rational(t_out, 60))} hours",
            f"Speed = distance ÷ time = {distance} ÷ {fmt_num(sp.Rational(t_out, 60))} = {fmt_num(outbound_speed_kmh)} km/h",
        ]
        final_answer = f"{fmt_num(outbound_speed_kmh)} km/h"
    elif question_kind == "rest_duration":
        prompt = "The distance-time graph shows a delivery van's journey. For how many minutes was the van stationary?"
        steps = [
            f"The graph is flat (constant distance = {distance} km) between {t1} and {t2} minutes.",
            f"Stationary time = {t2} - {t1} = {t_rest} minutes",
        ]
        final_answer = f"{t_rest} minutes"
    elif question_kind == "total_distance":
        prompt = "The distance-time graph shows a delivery van's journey. Find the total distance travelled."
        steps = [
            f"Distance out = {distance} km. Distance back = {distance} km.",
            f"Total distance travelled = {distance} + {distance} = {total_distance} km",
        ]
        final_answer = f"{total_distance} km"
    else:
        prompt = (
            "The distance-time graph shows a delivery van's journey. Find the average speed for the whole "
            "journey, in km/h."
        )
        steps = [
            f"Total distance = {total_distance} km. Total time = {t3} minutes = {fmt_num(sp.Rational(t3, 60))} hours.",
            f"Average speed = {total_distance} ÷ {fmt_num(sp.Rational(t3, 60))} = {fmt_num(average_speed_kmh)} km/h",
        ]
        final_answer = f"{fmt_num(average_speed_kmh)} km/h"

    return Question(
        topic_id="distance_time_interpret",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=final_answer,
        dedup_key=f"dt_interpret:{distance}:{t_out}:{t_rest}:{t_back}:{question_kind}",
        diagram=diagram,
    )


def generate_velocity_time_interpret(tier: Tier, rng: random.Random) -> Question:
    v_max = rng.choice([10, 12, 15, 20, 24, 30])
    t1 = rng.choice([5, 8, 10, 12])
    t2 = rng.choice([10, 15, 20, 25])
    t3 = rng.choice([5, 8, 10, 12])
    t_const_end, t_end = t1 + t2, t1 + t2 + t3
    points = [(0, 0), (t1, v_max), (t_const_end, v_max), (t_end, 0)]
    question_kind = rng.choice(["acceleration", "deceleration", "distance_constant", "distance_total"])

    # Independent check: acceleration via direct division, cross-checked by
    # an independent symbolic solve of "the two endpoints lie on v = a*t".
    accel = sp.Rational(v_max, t1)
    A = sp.symbols("A")
    solved = sp.solve(sp.Eq(A * t1, v_max), A)
    if solved[0] != accel:
        raise ValueError("velocity_time_interpret verification failed: acceleration mismatch")
    decel = sp.Rational(v_max, t3)

    dist_const = v_max * t2
    dist_accel = sp.Rational(v_max, 2) * t1
    dist_decel = sp.Rational(v_max, 2) * t3
    dist_total_direct = dist_accel + dist_const + dist_decel

    # Independent check: the whole velocity-time shape is a single trapezium
    # with parallel sides t_end (along v = 0) and t2 (along v = v_max) - a
    # genuinely different decomposition than summing three separate pieces.
    dist_total_check = sp.Rational(1, 2) * (t_end + t2) * v_max
    if sp.simplify(dist_total_direct - dist_total_check) != 0:
        raise ValueError("velocity_time_interpret verification failed: total distance mismatch")

    diagram = DiagramSpec(
        kind="piecewise_graph",
        params={
            "points": points, "x_max": t_end + 5, "y_max": v_max + 5,
            "x_label": "Time (s)", "y_label": "Velocity (m/s)",
        },
    )

    if question_kind == "acceleration":
        prompt = "The velocity-time graph shows a car's journey. Find its acceleration during the first phase."
        steps = [
            f"Acceleration = change in velocity ÷ time = {v_max} ÷ {t1} = {fmt_num(accel)} m/s^2",
        ]
        final_answer = f"{fmt_num(accel)} m/s^2"
    elif question_kind == "deceleration":
        prompt = "The velocity-time graph shows a car's journey. Find its deceleration during the final phase."
        steps = [
            f"Deceleration = change in velocity ÷ time = {v_max} ÷ {t3} = {fmt_num(decel)} m/s^2",
        ]
        final_answer = f"{fmt_num(decel)} m/s^2"
    elif question_kind == "distance_constant":
        prompt = (
            "The velocity-time graph shows a car's journey. Find the distance travelled while the car "
            "travels at constant velocity."
        )
        steps = [
            "Distance = area under the graph = base × height (a rectangle)",
            f"Distance = {t2} × {v_max} = {dist_const} m",
        ]
        final_answer = f"{dist_const} m"
    else:
        prompt = "The velocity-time graph shows a car's journey. Find the total distance travelled."
        steps = [
            "Total distance = total area under the graph (a trapezium)",
            f"Distance = ½ × ({t_end} + {t2}) × {v_max} = {fmt_num(dist_total_direct)} m",
        ]
        final_answer = f"{fmt_num(dist_total_direct)} m"

    return Question(
        topic_id="velocity_time_interpret",
        tier=Tier.HIGHER,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=final_answer,
        dedup_key=f"vt_interpret:{v_max}:{t1}:{t2}:{t3}:{question_kind}",
        diagram=diagram,
    )


_TRANSFORM_KINDS = ["translate_up", "translate_down", "translate_left", "translate_right", "reflect_x", "reflect_y"]


def _transform_notation(kind: str, shift: int) -> str:
    return {
        "translate_up": f"y = f(x) + {shift}",
        "translate_down": f"y = f(x) - {shift}",
        "translate_left": f"y = f(x + {shift})",
        "translate_right": f"y = f(x - {shift})",
        "reflect_x": "y = -f(x)",
        "reflect_y": "y = f(-x)",
    }[kind]


def _transform_description(kind: str, shift: int) -> str:
    return {
        "translate_up": f"Translation by vector (0, {shift})",
        "translate_down": f"Translation by vector (0, -{shift})",
        "translate_left": f"Translation by vector (-{shift}, 0)",
        "translate_right": f"Translation by vector ({shift}, 0)",
        "reflect_x": "Reflection in the x-axis",
        "reflect_y": "Reflection in the y-axis",
    }[kind]


def _transform_notation_expr(kind: str, shift: int):
    return {
        "translate_up": _TEST_FN + shift,
        "translate_down": _TEST_FN - shift,
        "translate_left": _TEST_FN.subs(X, X + shift),
        "translate_right": _TEST_FN.subs(X, X - shift),
        "reflect_x": -_TEST_FN,
        "reflect_y": _TEST_FN.subs(X, -X),
    }[kind]


def _transform_point(kind: str, shift: int, x0, y0):
    return {
        "translate_up": (x0, y0 + shift),
        "translate_down": (x0, y0 - shift),
        "translate_left": (x0 - shift, y0),
        "translate_right": (x0 + shift, y0),
        "reflect_x": (x0, -y0),
        "reflect_y": (-x0, y0),
    }[kind]


def generate_graph_transformations(tier: Tier, rng: random.Random) -> Question:
    kind = rng.choice(_TRANSFORM_KINDS)
    shift = rng.randint(1, 8) if kind.startswith("translate") else 0
    direction = rng.choice(["equation_to_description", "description_to_equation"])

    notation = _transform_notation(kind, shift)
    description = _transform_description(kind, shift)

    # Independent check: transform a concrete test point via pure geometry
    # (the point-map above) and, separately, via the algebraic notation
    # (substituting into a fixed internal test function) - two different
    # representations of the same transformation that must agree.
    test_x0 = sp.Integer(2)
    y0 = _TEST_FN.subs(X, test_x0)
    target_x, target_y = _transform_point(kind, shift, test_x0, y0)
    notation_expr = _transform_notation_expr(kind, shift)
    computed_y = notation_expr.subs(X, target_x)
    if sp.simplify(computed_y - target_y) != 0:
        raise ValueError("graph_transformations verification failed: notation/point-map mismatch")

    diagram = DiagramSpec(
        kind="graph_transformation",
        params={"transform": kind, "shift": shift, "original_label": "y = f(x)", "transformed_label": notation},
    )

    if direction == "equation_to_description":
        prompt = (
            f"The graph of y = f(x) is transformed to give the graph of {notation}. "
            "Describe this transformation fully."
        )
        final_answer = description
    else:
        prompt = (
            f"The graph of y = f(x) undergoes a {description[0].lower()}{description[1:]}. "
            "Write down the equation of the transformed graph in terms of f(x)."
        )
        final_answer = notation

    steps = [f"{notation} corresponds to a {description[0].lower()}{description[1:]}."]
    return Question(
        topic_id="graph_transformations",
        tier=Tier.HIGHER,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=final_answer,
        dedup_key=f"transform:{kind}:{shift}:{direction}",
        diagram=diagram,
    )


def generate_modelled_example_plot_straight_line(tier: Tier, rng: random.Random) -> ModelledExample:
    m = _rand_nonzero(rng, -4, 4)
    c = rng.randint(-6, 6)
    xs = list(range(-3, 4))
    ys = [m * x + c for x in xs]

    diffs = {ys[i + 1] - ys[i] for i in range(len(ys) - 1)}
    if diffs != {m}:
        raise ValueError("modelled example plot_straight_line verification failed")

    table_points = list(zip(xs, ys))
    x_min, x_max = xs[0] - 1, xs[-1] + 1
    y_min, y_max = min(ys) - 1, max(ys) + 1

    teaching_steps = [
        f"To plot a graph from an equation, first build a table of values: choose several x-values, "
        f"and work out the matching y using the equation y = {fmt_linear(m, c)}.",
        "Substitute each x-value from -3 to 3 into the equation in turn: "
        + ", ".join(f"x={x}: y={m}×{x}{'+' if c >= 0 else '-'}{abs(c)}={y}" for x, y in zip(xs[:3], ys[:3]))
        + ", and so on for the rest.",
        "Plot each (x, y) pair as a point on the axes. Since y = mx + c is a straight-line equation, "
        "all the points will line up exactly - join them with a single ruled straight line, extending "
        "it right across the grid.",
    ]
    worked_calculation = [
        f"y = {fmt_linear(m, c)}",
        "x: " + ", ".join(str(x) for x in xs),
        "y: " + ", ".join(str(y) for y in ys),
    ]
    return ModelledExample(
        topic_id="plot_straight_line",
        tier=Tier.FOUNDATION,
        prompt=f"Complete a table of values for y = {fmt_linear(m, c)} for x = -3 to 3, then plot the graph.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"Straight line: y = {fmt_linear(m, c)}",
        diagram=DiagramSpec(
            kind="function_graph",
            params={
                "kind": "linear", "m": m, "c": c,
                "x_min": x_min, "x_max": x_max, "y_min": y_min, "y_max": y_max,
                "table_points": table_points,
            },
        ),
    )


def generate_modelled_example_plot_quadratic(tier: Tier, rng: random.Random) -> ModelledExample:
    a = rng.choice([1, -1])
    b = rng.randint(-2, 2)
    c = rng.randint(-4, 4)
    xs = list(range(-3, 4))
    ys = [a * x * x + b * x + c for x in xs]

    first_diffs = [ys[i + 1] - ys[i] for i in range(len(ys) - 1)]
    second_diffs = {first_diffs[i + 1] - first_diffs[i] for i in range(len(first_diffs) - 1)}
    if second_diffs != {2 * a}:
        raise ValueError("modelled example plot_quadratic verification failed")

    table_points = list(zip(xs, ys))
    x_min, x_max = xs[0] - 1, xs[-1] + 1
    y_min, y_max = min(ys) - 1, max(ys) + 1

    teaching_steps = [
        f"To plot a curve from an equation, build a table of values by substituting each x from -3 to 3 "
        f"into y = {_fmt_quadratic(a, b, c)}.",
        "Working through a few: "
        + ", ".join(f"x={x}: y={y}" for x, y in list(zip(xs, ys))[:3])
        + ", and so on across the full range.",
        "Plot each (x, y) pair. Unlike a straight line, a quadratic doesn't form a straight path - "
        "join the points with a single smooth curve (not straight segments), giving the characteristic "
        "U-shape (or n-shape if the x^2 coefficient is negative).",
    ]
    worked_calculation = [
        f"y = {_fmt_quadratic(a, b, c)}",
        "x: " + ", ".join(str(x) for x in xs),
        "y: " + ", ".join(str(y) for y in ys),
    ]
    return ModelledExample(
        topic_id="plot_quadratic",
        tier=Tier.FOUNDATION,
        prompt=f"Complete a table of values for y = {_fmt_quadratic(a, b, c)} for x = -3 to 3, then plot the graph.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"Quadratic curve: y = {_fmt_quadratic(a, b, c)}",
        diagram=DiagramSpec(
            kind="function_graph",
            params={
                "kind": "quadratic", "a": a, "b": b, "c": c,
                "x_min": x_min, "x_max": x_max, "y_min": y_min, "y_max": y_max,
                "table_points": table_points,
            },
        ),
    )


def generate_modelled_example_plot_cubic(tier: Tier, rng: random.Random) -> ModelledExample:
    a = rng.choice([1, -1])
    b = rng.randint(-3, 3)
    xs = list(range(-3, 4))
    ys = [a * x**3 + b * x for x in xs]

    d1 = [ys[i + 1] - ys[i] for i in range(len(ys) - 1)]
    d2 = [d1[i + 1] - d1[i] for i in range(len(d1) - 1)]
    d3 = {d2[i + 1] - d2[i] for i in range(len(d2) - 1)}
    if d3 != {6 * a}:
        raise ValueError("modelled example plot_cubic verification failed")

    table_points = list(zip(xs, ys))
    x_min, x_max = xs[0] - 1, xs[-1] + 1
    y_min, y_max = min(ys) - 2, max(ys) + 2

    teaching_steps = [
        f"As with any graph, start with a table of values: substitute each x from -3 to 3 into "
        f"y = {_fmt_cubic(a, b)}, remembering x^3 grows much faster than x^2 or x as x gets large.",
        "Working through a few: "
        + ", ".join(f"x={x}: y={y}" for x, y in list(zip(xs, ys))[:3])
        + ", and so on across the full range.",
        "Plot each (x, y) pair and join them with a single smooth curve. A cubic typically has an "
        "S-like shape with one 'wiggle' rather than the simple U-shape of a quadratic.",
    ]
    worked_calculation = [
        f"y = {_fmt_cubic(a, b)}",
        "x: " + ", ".join(str(x) for x in xs),
        "y: " + ", ".join(str(y) for y in ys),
    ]
    return ModelledExample(
        topic_id="plot_cubic",
        tier=Tier.HIGHER,
        prompt=f"Complete a table of values for y = {_fmt_cubic(a, b)} for x = -3 to 3, then plot the graph.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"Cubic curve: y = {_fmt_cubic(a, b)}",
        diagram=DiagramSpec(
            kind="function_graph",
            params={
                "kind": "cubic", "a": a, "b": b,
                "x_min": x_min, "x_max": x_max, "y_min": y_min, "y_max": y_max,
                "table_points": table_points,
            },
        ),
    )


def generate_modelled_example_plot_reciprocal(tier: Tier, rng: random.Random) -> ModelledExample:
    magnitude = rng.choice([12, 24, 36, 48])
    sign = rng.choice([1, -1])
    a = magnitude * sign
    xs = [-4, -3, -2, -1, 1, 2, 3, 4]
    ys = [a // x for x in xs]

    if any(x * y != a for x, y in zip(xs, ys)):
        raise ValueError("modelled example plot_reciprocal verification failed")

    table_points = list(zip(xs, ys))
    y_bound = max(abs(y) for y in ys) + 2

    teaching_steps = [
        f"Build a table of values for y = {_fmt_reciprocal(a)}, substituting each x-value in turn - "
        "note that x = 0 is skipped entirely, since dividing by 0 is undefined.",
        "Working through a few: "
        + ", ".join(f"x={x}: y={a}÷{x}={y}" for x, y in list(zip(xs, ys))[:3])
        + ", and so on for the rest.",
        "Plot each (x, y) pair. Because x = 0 can never be used, the graph splits into two separate "
        "curved branches (one where x is positive, one where x is negative) that both get closer and "
        "closer to the axes without ever touching them.",
    ]
    worked_calculation = [
        f"y = {_fmt_reciprocal(a)}",
        "x: " + ", ".join(str(x) for x in xs),
        "y: " + ", ".join(str(y) for y in ys),
    ]
    return ModelledExample(
        topic_id="plot_reciprocal",
        tier=Tier.HIGHER,
        prompt=(
            f"Complete a table of values for y = {_fmt_reciprocal(a)} for x = -4, -3, -2, -1, 1, 2, 3, 4, "
            "then plot the graph."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"Reciprocal curve: y = {_fmt_reciprocal(a)}",
        diagram=DiagramSpec(
            kind="function_graph",
            params={
                "kind": "reciprocal", "a": a,
                "x_min": -4, "x_max": 4, "y_min": -y_bound, "y_max": y_bound,
                "table_points": table_points,
            },
        ),
    )


def generate_modelled_example_plot_distance_time(tier: Tier, rng: random.Random) -> ModelledExample:
    distance = rng.choice([4, 5, 6, 8, 10])
    t_out = rng.choice([10, 15, 20, 25])
    t_rest = rng.choice([5, 10, 15])
    t_back = rng.choice([10, 15, 20, 25, 30])
    t1, t2, t3 = t_out, t_out + t_rest, t_out + t_rest + t_back
    points = [(0, 0), (t1, distance), (t2, distance), (t3, 0)]

    direct_total = 2 * distance
    leg_total = sum(abs(points[i + 1][1] - points[i][1]) for i in range(len(points) - 1))
    if direct_total != leg_total:
        raise ValueError("modelled example plot_distance_time verification failed")

    teaching_steps = [
        "A distance-time graph is built stage by stage: work out what happens to the distance during "
        "each part of the journey, and plot a straight line segment for each one.",
        f"Stage 1: sets out at (0 minutes, 0 km), travelling at a constant speed, arriving at "
        f"({t1}, {distance}). Stage 2: stays at {distance} km (a flat, horizontal line, since distance "
        f"isn't changing) until ({t2}, {distance}). Stage 3: returns at a constant speed back to "
        f"({t3}, 0).",
        "Join each pair of points with a straight line segment - the steepness (gradient) of each "
        "segment represents the speed during that stage, and a flat segment always means stationary.",
        f"Total distance travelled = distance out + distance back = {distance} + {distance} = {direct_total} km.",
    ]
    worked_calculation = [
        f"(0, 0) → ({t1}, {distance}) → ({t2}, {distance}) → ({t3}, 0)",
        f"Total distance = {distance} + {distance} = {direct_total} km",
    ]
    return ModelledExample(
        topic_id="plot_distance_time",
        tier=Tier.FOUNDATION,
        prompt=(
            f"A cyclist leaves home at 0 minutes. They cycle at a constant speed, reaching a shop {distance} km "
            f"away after {t1} minutes. They stay at the shop until {t2} minutes, then cycle straight back home at "
            f"a constant speed, arriving home at {t3} minutes. Draw a distance-time graph to show this journey, "
            "and find the total distance travelled."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{direct_total} km",
        diagram=DiagramSpec(
            kind="piecewise_graph",
            params={
                "points": points, "x_max": t3 + 5, "y_max": distance + 2,
                "x_label": "Time (minutes)", "y_label": "Distance (km)",
            },
        ),
    )


def generate_modelled_example_line_equation_from_graph(tier: Tier, rng: random.Random) -> ModelledExample:
    m = _rand_nonzero(rng, -4, 4)
    c = rng.randint(-6, 6)
    x1 = rng.randint(-4, -1)
    x2 = rng.randint(1, 4)
    y1, y2 = m * x1 + c, m * x2 + c

    M, C = sp.symbols("M C")
    solved = sp.solve([sp.Eq(M * x1 + C, y1), sp.Eq(M * x2 + C, y2)], [M, C])
    if solved.get(M) != m or solved.get(C) != c:
        raise ValueError("modelled example line_equation_from_graph verification failed")

    x_min, x_max = x1 - 1, x2 + 1
    end_ys = [m * x_min + c, m * x_max + c, y1, y2]
    y_min, y_max = min(end_ys) - 1, max(end_ys) + 1

    teaching_steps = [
        "A straight line's equation y = mx + c is fully determined by two things: its gradient m and "
        f"its y-intercept c. Both can be read from any two clearly marked points on the line, here "
        f"({x1}, {y1}) and ({x2}, {y2}).",
        f"Find the gradient using rise over run between the two points: "
        f"m = ({y2} - {y1}) / ({x2} - {x1}) = {m}.",
        f"Substitute one of the points and the gradient into y = mx + c to find c: using ({x1}, {y1}), "
        f"{y1} = {m}×({x1}) + c, so c = {c}.",
        f"So the equation of the line is y = {fmt_linear(m, c)}.",
    ]
    worked_calculation = [
        f"m = ({y2} - {y1}) / ({x2} - {x1}) = {m}",
        f"{y1} = {m}×({x1}) + c",
        f"c = {c}",
        f"y = {fmt_linear(m, c)}",
    ]
    return ModelledExample(
        topic_id="line_equation_from_graph",
        tier=Tier.FOUNDATION,
        prompt="The graph shows a straight line. Find the equation of the line in the form y = mx + c.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"y = {fmt_linear(m, c)}",
        diagram=DiagramSpec(
            kind="function_graph",
            params={
                "kind": "linear", "m": m, "c": c,
                "x_min": x_min, "x_max": x_max, "y_min": y_min, "y_max": y_max,
                "table_points": [[x1, y1], [x2, y2]],
            },
        ),
    )


def generate_modelled_example_parallel_lines_equation(tier: Tier, rng: random.Random) -> ModelledExample:
    m = _rand_nonzero(rng, -5, 5)
    c1 = rng.randint(-8, 8)
    x0 = _rand_nonzero(rng, -6, 6)
    y0 = rng.randint(-10, 10)
    while y0 == m * x0 + c1:
        y0 = rng.randint(-10, 10)
    c2 = y0 - m * x0

    C = sp.symbols("C")
    solved = sp.solve(sp.Eq(m * x0 + C, y0), C)
    if solved[0] != c2:
        raise ValueError("modelled example parallel_lines_equation verification failed")

    teaching_steps = [
        "Parallel lines never meet, which means they always slope in exactly the same direction - so "
        "two parallel lines always share the same gradient m, even though they have different "
        "y-intercepts.",
        f"Since our new line is parallel to y = {fmt_linear(m, c1)}, it must have the same gradient: m = {m}.",
        f"To find the new line's intercept c, use the fact that the line passes through ({x0}, {y0}): "
        f"substitute into y = {m}x + c to get {y0} = {m}×({x0}) + c, so c = {c2}.",
        f"So the equation of the new line is y = {fmt_linear(m, c2)}.",
    ]
    worked_calculation = [
        f"m = {m} (same as the given line)",
        f"{y0} = {m}×({x0}) + c",
        f"c = {c2}",
        f"y = {fmt_linear(m, c2)}",
    ]
    return ModelledExample(
        topic_id="parallel_lines_equation",
        tier=Tier.FOUNDATION,
        prompt=(
            f"A line is parallel to y = {fmt_linear(m, c1)} and passes through the point ({x0}, {y0}). "
            "Find the equation of the line."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"y = {fmt_linear(m, c2)}",
    )


def generate_modelled_example_perpendicular_lines_equation(tier: Tier, rng: random.Random) -> ModelledExample:
    m1 = _rand_nonzero(rng, -5, 5)
    c1 = rng.randint(-8, 8)
    m2 = sp.Rational(-1, m1)
    x0 = _rand_nonzero(rng, -6, 6)
    y0 = rng.randint(-10, 10)
    c2 = sp.Rational(y0) - m2 * x0

    if sp.simplify(m1 * m2 + 1) != 0:
        raise ValueError("modelled example perpendicular_lines_equation verification failed: gradients")
    if sp.simplify(m2 * x0 + c2 - y0) != 0:
        raise ValueError("modelled example perpendicular_lines_equation verification failed: point")

    teaching_steps = [
        "Two lines are perpendicular when they meet at a right angle. There's a neat algebraic rule "
        f"for this: perpendicular gradients always multiply to give -1.",
        f"Since our new line is perpendicular to y = {fmt_linear(m1, c1)}, its gradient m must satisfy "
        f"m × {m1} = -1, so m = -1/{m1} = {fmt_num(m2)} (the negative reciprocal of {m1}).",
        f"To find the intercept c, use the fact the line passes through ({x0}, {y0}): substitute into "
        f"y = {fmt_num(m2)}x + c to get {y0} = {fmt_num(m2)}×({x0}) + c, so c = {fmt_num(c2)}.",
        f"So the equation of the new line is y = {fmt_linear(m2, c2)}.",
    ]
    worked_calculation = [
        f"m × {m1} = -1, so m = {fmt_num(m2)}",
        f"{y0} = {fmt_num(m2)}×({x0}) + c",
        f"c = {fmt_num(c2)}",
        f"y = {fmt_linear(m2, c2)}",
    ]
    return ModelledExample(
        topic_id="perpendicular_lines_equation",
        tier=Tier.HIGHER,
        prompt=(
            f"A line is perpendicular to y = {fmt_linear(m1, c1)} and passes through the point ({x0}, {y0}). "
            "Find the equation of the line."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"y = {fmt_linear(m2, c2)}",
    )


def generate_modelled_example_distance_time_interpret(tier: Tier, rng: random.Random) -> ModelledExample:
    distance = rng.choice([4, 5, 6, 8, 9, 10, 12])
    t_out = rng.choice([10, 15, 20, 24, 25, 30])
    t_rest = rng.choice([5, 10, 15, 20])
    t_back = rng.choice([10, 15, 20, 25, 30, 40])
    t1, t2, t3 = t_out, t_out + t_rest, t_out + t_rest + t_back
    points = [(0, 0), (t1, distance), (t2, distance), (t3, 0)]
    question_kind = rng.choice(["outbound_speed", "rest_duration", "total_distance", "average_speed"])

    outbound_speed_kmh = sp.Rational(distance, t_out) * 60
    outbound_speed_check = sp.Rational(distance) / sp.Rational(t_out, 60)
    if sp.simplify(outbound_speed_kmh - outbound_speed_check) != 0:
        raise ValueError("modelled example distance_time_interpret verification failed: outbound speed")

    total_distance = 2 * distance
    leg_total = sum(abs(points[i + 1][1] - points[i][1]) for i in range(len(points) - 1))
    if total_distance != leg_total:
        raise ValueError("modelled example distance_time_interpret verification failed: total distance")

    average_speed_kmh = sp.Rational(total_distance, t3) * 60

    diagram = DiagramSpec(
        kind="piecewise_graph",
        params={
            "points": points, "x_max": t3 + 5, "y_max": distance + 2,
            "x_label": "Time (minutes)", "y_label": "Distance (km)",
        },
    )

    if question_kind == "outbound_speed":
        prompt = (
            "The distance-time graph shows a delivery van's journey. Find its speed during the outbound leg "
            "of the journey, in km/h."
        )
        teaching_steps = [
            "Speed is distance ÷ time, but the graph's time axis is in minutes while speed in km/h needs "
            "time in hours - so the units must be converted first.",
            f"The outbound leg covers {distance} km in {t_out} minutes. Convert {t_out} minutes to hours: "
            f"{t_out} ÷ 60 = {fmt_num(sp.Rational(t_out, 60))} hours.",
            f"Speed = distance ÷ time = {distance} ÷ {fmt_num(sp.Rational(t_out, 60))} = "
            f"{fmt_num(outbound_speed_kmh)} km/h.",
        ]
        worked_calculation = [
            f"{t_out} min = {fmt_num(sp.Rational(t_out, 60))} h",
            f"Speed = {distance} ÷ {fmt_num(sp.Rational(t_out, 60))}",
            f"= {fmt_num(outbound_speed_kmh)} km/h",
        ]
        final_answer = f"{fmt_num(outbound_speed_kmh)} km/h"
    elif question_kind == "rest_duration":
        prompt = "The distance-time graph shows a delivery van's journey. For how many minutes was the van stationary?"
        teaching_steps = [
            "On a distance-time graph, a flat (horizontal) section means the distance isn't changing - "
            "in other words, the object is stationary.",
            f"The graph is flat at a constant {distance} km between {t1} minutes and {t2} minutes.",
            f"Stationary time = {t2} - {t1} = {t_rest} minutes.",
        ]
        worked_calculation = [f"Flat between {t1} and {t2} minutes", f"{t2} - {t1} = {t_rest} minutes"]
        final_answer = f"{t_rest} minutes"
    elif question_kind == "total_distance":
        prompt = "The distance-time graph shows a delivery van's journey. Find the total distance travelled."
        teaching_steps = [
            "Total distance travelled adds up every leg of the journey, regardless of direction - unlike "
            "displacement, a return trip does NOT cancel out to zero.",
            f"Distance out = {distance} km. Distance back = {distance} km (the same distance, travelled "
            "in the opposite direction).",
            f"Total distance travelled = {distance} + {distance} = {total_distance} km.",
        ]
        worked_calculation = [f"Distance out = {distance} km, distance back = {distance} km", f"{distance} + {distance} = {total_distance} km"]
        final_answer = f"{total_distance} km"
    else:
        prompt = (
            "The distance-time graph shows a delivery van's journey. Find the average speed for the whole "
            "journey, in km/h."
        )
        teaching_steps = [
            "Average speed over a whole journey is total distance ÷ total time - it doesn't matter that "
            "the speed varied or that the van stopped partway, only the overall totals matter.",
            f"Total distance = {total_distance} km. Total time = {t3} minutes = "
            f"{fmt_num(sp.Rational(t3, 60))} hours.",
            f"Average speed = {total_distance} ÷ {fmt_num(sp.Rational(t3, 60))} = "
            f"{fmt_num(average_speed_kmh)} km/h.",
        ]
        worked_calculation = [
            f"{t3} min = {fmt_num(sp.Rational(t3, 60))} h",
            f"Average speed = {total_distance} ÷ {fmt_num(sp.Rational(t3, 60))}",
            f"= {fmt_num(average_speed_kmh)} km/h",
        ]
        final_answer = f"{fmt_num(average_speed_kmh)} km/h"

    return ModelledExample(
        topic_id="distance_time_interpret",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=final_answer,
        diagram=diagram,
    )


def generate_modelled_example_velocity_time_interpret(tier: Tier, rng: random.Random) -> ModelledExample:
    v_max = rng.choice([10, 12, 15, 20, 24, 30])
    t1 = rng.choice([5, 8, 10, 12])
    t2 = rng.choice([10, 15, 20, 25])
    t3 = rng.choice([5, 8, 10, 12])
    t_const_end, t_end = t1 + t2, t1 + t2 + t3
    points = [(0, 0), (t1, v_max), (t_const_end, v_max), (t_end, 0)]
    question_kind = rng.choice(["acceleration", "deceleration", "distance_constant", "distance_total"])

    accel = sp.Rational(v_max, t1)
    A = sp.symbols("A")
    solved = sp.solve(sp.Eq(A * t1, v_max), A)
    if solved[0] != accel:
        raise ValueError("modelled example velocity_time_interpret verification failed: acceleration")
    decel = sp.Rational(v_max, t3)

    dist_const = v_max * t2
    dist_accel = sp.Rational(v_max, 2) * t1
    dist_decel = sp.Rational(v_max, 2) * t3
    dist_total_direct = dist_accel + dist_const + dist_decel

    dist_total_check = sp.Rational(1, 2) * (t_end + t2) * v_max
    if sp.simplify(dist_total_direct - dist_total_check) != 0:
        raise ValueError("modelled example velocity_time_interpret verification failed: total distance")

    diagram = DiagramSpec(
        kind="piecewise_graph",
        params={
            "points": points, "x_max": t_end + 5, "y_max": v_max + 5,
            "x_label": "Time (s)", "y_label": "Velocity (m/s)",
        },
    )

    if question_kind == "acceleration":
        prompt = "The velocity-time graph shows a car's journey. Find its acceleration during the first phase."
        teaching_steps = [
            "On a velocity-time graph, the gradient (steepness) of a section represents acceleration - "
            "how quickly velocity is changing.",
            f"During the first phase, velocity rises from 0 to {v_max} m/s over {t1} seconds.",
            f"Acceleration = change in velocity ÷ time taken = {v_max} ÷ {t1} = {fmt_num(accel)} m/s^2.",
        ]
        worked_calculation = ["Acceleration = Δvelocity ÷ time", f"= {v_max} ÷ {t1} = {fmt_num(accel)} m/s^2"]
        final_answer = f"{fmt_num(accel)} m/s^2"
    elif question_kind == "deceleration":
        prompt = "The velocity-time graph shows a car's journey. Find its deceleration during the final phase."
        teaching_steps = [
            "Deceleration is just negative acceleration - the same gradient calculation, but for a "
            "phase where velocity is decreasing back towards 0.",
            f"During the final phase, velocity falls from {v_max} m/s to 0 over {t3} seconds.",
            f"Deceleration = change in velocity ÷ time taken = {v_max} ÷ {t3} = {fmt_num(decel)} m/s^2.",
        ]
        worked_calculation = ["Deceleration = Δvelocity ÷ time", f"= {v_max} ÷ {t3} = {fmt_num(decel)} m/s^2"]
        final_answer = f"{fmt_num(decel)} m/s^2"
    elif question_kind == "distance_constant":
        prompt = (
            "The velocity-time graph shows a car's journey. Find the distance travelled while the car "
            "travels at constant velocity."
        )
        teaching_steps = [
            "On a velocity-time graph, distance travelled is represented by the area underneath the "
            "graph, not the gradient - this is because area = (roughly) speed × time, which is distance.",
            f"During the constant-velocity phase, the graph is a horizontal line at {v_max} m/s lasting "
            f"{t2} seconds, so the area underneath is a rectangle.",
            f"Distance = base × height = {t2} × {v_max} = {dist_const} m.",
        ]
        worked_calculation = ["Distance = base × height", f"= {t2} × {v_max} = {dist_const} m"]
        final_answer = f"{dist_const} m"
    else:
        prompt = "The velocity-time graph shows a car's journey. Find the total distance travelled."
        teaching_steps = [
            "The total distance travelled is the total area under the whole velocity-time graph. Here "
            "the graph's outline (from (0,0) up to the plateau and back down to 0) forms a single "
            "trapezium shape.",
            f"A trapezium's area is ½ × (sum of parallel sides) × height. The two parallel sides here "
            f"are the total time {t_end} s (along the bottom) and the constant-speed time {t2} s (along "
            f"the top), with height {v_max} m/s.",
            f"Distance = ½ × ({t_end} + {t2}) × {v_max} = {fmt_num(dist_total_direct)} m.",
        ]
        worked_calculation = [
            "Distance = ½ × (sum of parallel sides) × height",
            f"= ½ × ({t_end} + {t2}) × {v_max}",
            f"= {fmt_num(dist_total_direct)} m",
        ]
        final_answer = f"{fmt_num(dist_total_direct)} m"

    return ModelledExample(
        topic_id="velocity_time_interpret",
        tier=Tier.HIGHER,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=final_answer,
        diagram=diagram,
    )


def generate_modelled_example_graph_transformations(tier: Tier, rng: random.Random) -> ModelledExample:
    kind = rng.choice(_TRANSFORM_KINDS)
    shift = rng.randint(1, 8) if kind.startswith("translate") else 0
    direction = rng.choice(["equation_to_description", "description_to_equation"])

    notation = _transform_notation(kind, shift)
    description = _transform_description(kind, shift)

    test_x0 = sp.Integer(2)
    y0 = _TEST_FN.subs(X, test_x0)
    target_x, target_y = _transform_point(kind, shift, test_x0, y0)
    notation_expr = _transform_notation_expr(kind, shift)
    computed_y = notation_expr.subs(X, target_x)
    if sp.simplify(computed_y - target_y) != 0:
        raise ValueError("modelled example graph_transformations verification failed")

    diagram = DiagramSpec(
        kind="graph_transformation",
        params={"transform": kind, "shift": shift, "original_label": "y = f(x)", "transformed_label": notation},
    )

    lower_description = description[0].lower() + description[1:]
    teaching_steps = [
        "Function notation gives a shorthand for describing how a graph moves or flips, without needing "
        "to know the actual formula for f(x).",
        f"{notation} means {lower_description}: "
        + (
            f"adding a number outside the function (after f(x)) shifts the whole graph vertically."
            if kind in ("translate_up", "translate_down")
            else (
                "adding or subtracting a number inside the brackets (to x itself) shifts the graph "
                "horizontally - and counterintuitively, f(x + shift) moves LEFT, not right."
                if kind in ("translate_left", "translate_right")
                else (
                    "putting a minus sign outside the function flips every y-value to its negative, "
                    "reflecting the graph in the x-axis."
                    if kind == "reflect_x"
                    else "putting a minus sign on x flips the graph left-right, reflecting it in the y-axis."
                )
            )
        ),
        f"So {notation} corresponds to a {lower_description}.",
    ]
    worked_calculation = [
        f"{notation}",
        f"= {lower_description}",
    ]

    if direction == "equation_to_description":
        prompt = (
            f"The graph of y = f(x) is transformed to give the graph of {notation}. "
            "Describe this transformation fully."
        )
        final_answer = description
    else:
        prompt = (
            f"The graph of y = f(x) undergoes a {lower_description}. "
            "Write down the equation of the transformed graph in terms of f(x)."
        )
        final_answer = notation

    return ModelledExample(
        topic_id="graph_transformations",
        tier=Tier.HIGHER,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=final_answer,
        diagram=diagram,
    )


TOPIC_PLOT_STRAIGHT_LINE = TopicDefinition(
    id="plot_straight_line",
    display_name="Plotting Straight Line Graphs",
    description="Complete a table of values and plot a straight line graph on the axes provided. (5 questions)",
    generate=generate_plot_straight_line,
    section=SECTION,
    group=GROUP_PLOTTING,
    fixed_tier=Tier.FOUNDATION,
    question_count=PLOTTING_QUESTION_COUNT,
    generate_modelled_example=generate_modelled_example_plot_straight_line,
)

TOPIC_PLOT_QUADRATIC = TopicDefinition(
    id="plot_quadratic",
    display_name="Plotting Quadratic Graphs",
    description="Complete a table of values and plot a quadratic graph on the axes provided. (5 questions)",
    generate=generate_plot_quadratic,
    section=SECTION,
    group=GROUP_PLOTTING,
    fixed_tier=Tier.FOUNDATION,
    question_count=PLOTTING_QUESTION_COUNT,
    generate_modelled_example=generate_modelled_example_plot_quadratic,
)

TOPIC_PLOT_CUBIC = TopicDefinition(
    id="plot_cubic",
    display_name="Plotting Cubic Graphs",
    description="Complete a table of values and plot a cubic graph on the axes provided. (5 questions)",
    generate=generate_plot_cubic,
    section=SECTION,
    group=GROUP_PLOTTING,
    fixed_tier=Tier.HIGHER,
    question_count=PLOTTING_QUESTION_COUNT,
    generate_modelled_example=generate_modelled_example_plot_cubic,
)

TOPIC_PLOT_RECIPROCAL = TopicDefinition(
    id="plot_reciprocal",
    display_name="Plotting Reciprocal Graphs",
    description="Complete a table of values and plot a reciprocal graph on the axes provided. (5 questions)",
    generate=generate_plot_reciprocal,
    section=SECTION,
    group=GROUP_PLOTTING,
    fixed_tier=Tier.HIGHER,
    question_count=PLOTTING_QUESTION_COUNT,
    generate_modelled_example=generate_modelled_example_plot_reciprocal,
)

TOPIC_PLOT_DISTANCE_TIME = TopicDefinition(
    id="plot_distance_time",
    display_name="Plotting Distance-Time Graphs",
    description="Draw a distance-time graph from a description of a journey, on the axes provided. (5 questions)",
    generate=generate_plot_distance_time,
    section=SECTION,
    group=GROUP_PLOTTING,
    fixed_tier=Tier.FOUNDATION,
    question_count=PLOTTING_QUESTION_COUNT,
    generate_modelled_example=generate_modelled_example_plot_distance_time,
)

TOPIC_LINE_EQUATION_FROM_GRAPH = TopicDefinition(
    id="line_equation_from_graph",
    display_name="Equation of a Line from a Graph",
    description="Read the gradient and intercept from a graph to find the equation of a straight line.",
    generate=generate_line_equation_from_graph,
    section=SECTION,
    group=GROUP_LINE_EQUATION,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_line_equation_from_graph,
)

TOPIC_PARALLEL_LINES_EQUATION = TopicDefinition(
    id="parallel_lines_equation",
    display_name="Parallel Lines",
    description="Find the equation of a line parallel to a given line through a given point.",
    generate=generate_parallel_lines_equation,
    section=SECTION,
    group=GROUP_LINE_EQUATION,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_parallel_lines_equation,
)

TOPIC_PERPENDICULAR_LINES_EQUATION = TopicDefinition(
    id="perpendicular_lines_equation",
    display_name="Perpendicular Lines",
    description="Find the equation of a line perpendicular to a given line through a given point.",
    generate=generate_perpendicular_lines_equation,
    section=SECTION,
    group=GROUP_LINE_EQUATION,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_perpendicular_lines_equation,
)

TOPIC_DISTANCE_TIME_INTERPRET = TopicDefinition(
    id="distance_time_interpret",
    display_name="Interpreting Distance-Time Graphs",
    description="Read speeds, rest periods, and total distance from a distance-time graph.",
    generate=generate_distance_time_interpret,
    section=SECTION,
    group=GROUP_REAL_LIFE,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_distance_time_interpret,
)

TOPIC_VELOCITY_TIME_INTERPRET = TopicDefinition(
    id="velocity_time_interpret",
    display_name="Interpreting Velocity-Time Graphs",
    description="Find acceleration (gradient) and distance travelled (area) from a velocity-time graph.",
    generate=generate_velocity_time_interpret,
    section=SECTION,
    group=GROUP_REAL_LIFE,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_velocity_time_interpret,
)

TOPIC_GRAPH_TRANSFORMATIONS = TopicDefinition(
    id="graph_transformations",
    display_name="Transformations of Graphs",
    description="Translate or reflect the graph of y = f(x) and describe or write the resulting equation.",
    generate=generate_graph_transformations,
    section=SECTION,
    group=GROUP_TRANSFORMATIONS,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_graph_transformations,
)
