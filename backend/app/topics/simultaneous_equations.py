import random

import sympy as sp

from app.core.models import DiagramSpec, ModelledExample, Question, Tier
from app.topics.algebra_utils import fmt_linear
from app.topics.base import TopicDefinition

SECTION = "algebra"
GROUP = "Simultaneous Equations"

Xs, Ys = sp.symbols("x y")

_ITEM_PAIRS = [("pen", "pencil"), ("apple", "banana"), ("cup", "plate"), ("ticket", "programme"), ("rose", "tulip")]


def _rand_nonzero(rng: random.Random, lo: int, hi: int) -> int:
    while True:
        v = rng.randint(lo, hi)
        if v != 0:
            return v


def _fmt_eq_lhs(a: int, b: int) -> str:
    parts = ["x" if a == 1 else f"{a}x"]
    if b > 0:
        parts.append(f"+ {'y' if b == 1 else f'{b}y'}")
    elif b < 0:
        parts.append(f"- {'y' if b == -1 else f'{-b}y'}")
    return " ".join(parts)


def _fmt_pence(p: int) -> str:
    return f"£{p // 100}.{p % 100:02d}"


def _fmt_quad_expr(b: int, c: int) -> str:
    parts = ["x^2"]
    if b != 0:
        term = "x" if abs(b) == 1 else f"{abs(b)}x"
        parts.append(f"{'+' if b > 0 else '-'} {term}")
    if c != 0:
        parts.append(f"{'+' if c > 0 else '-'} {abs(c)}")
    return " ".join(parts)


def _fmt_root_factor(r: int) -> str:
    if r == 0:
        return "x"
    return f"(x - {r})" if r > 0 else f"(x + {-r})"


def generate_common_coefficient(tier: Tier, rng: random.Random) -> Question:
    sol_x = _rand_nonzero(rng, -8, 8)
    sol_y = _rand_nonzero(rng, -8, 8)
    a = rng.randint(1, 6)
    c = rng.randint(1, 6)
    while c == a:
        c = rng.randint(1, 6)
    k = rng.randint(1, 5)
    same_sign = rng.choice([True, False])
    b = k
    d = k if same_sign else -k
    e = a * sol_x + b * sol_y
    f = c * sol_x + d * sol_y

    # Independent verification via sympy's linear solver - a different code path than
    # the elimination steps constructed below.
    solution = sp.solve([sp.Eq(a * Xs + b * Ys, e), sp.Eq(c * Xs + d * Ys, f)], [Xs, Ys])
    if solution.get(Xs) != sol_x or solution.get(Ys) != sol_y:
        raise ValueError("simultaneous_common_coefficient verification failed")

    eq1, eq2 = f"{_fmt_eq_lhs(a, b)} = {e}", f"{_fmt_eq_lhs(c, d)} = {f}"
    op = "Subtract" if same_sign else "Add"
    new_coeff = (a - c) if same_sign else (a + c)
    new_const = (e - f) if same_sign else (e + f)

    steps = [
        f"{eq1}  (1)",
        f"{eq2}  (2)",
        f"{op} the equations to eliminate y: {new_coeff}x = {new_const}, so x = {sol_x}",
        f"Substitute x = {sol_x} into (1): {b}y = {e - a * sol_x}, so y = {sol_y}",
    ]
    return Question(
        topic_id="simultaneous_common_coefficient",
        tier=Tier.FOUNDATION,
        prompt=f"Solve the simultaneous equations: {eq1} and {eq2}",
        solution_steps=tuple(steps),
        final_answer=f"x = {sol_x}, y = {sol_y}",
        dedup_key=f"sim_common:{a}:{b}:{c}:{d}:{e}:{f}",
    )


def generate_different_coefficient(tier: Tier, rng: random.Random) -> Question:
    sol_x = _rand_nonzero(rng, -9, 9)
    sol_y = _rand_nonzero(rng, -9, 9)

    for _ in range(100):
        a, b = _rand_nonzero(rng, 2, 5), _rand_nonzero(rng, 2, 5)
        c, d = _rand_nonzero(rng, 2, 5), _rand_nonzero(rng, 2, 5)
        if a * d != b * c and a != c and b != d:
            break
    else:
        raise ValueError("simultaneous_different_coefficient could not find valid coefficients")

    e = a * sol_x + b * sol_y
    f = c * sol_x + d * sol_y

    solution = sp.solve([sp.Eq(a * Xs + b * Ys, e), sp.Eq(c * Xs + d * Ys, f)], [Xs, Ys])
    if solution.get(Xs) != sol_x or solution.get(Ys) != sol_y:
        raise ValueError("simultaneous_different_coefficient verification failed")

    eq1, eq2 = f"{_fmt_eq_lhs(a, b)} = {e}", f"{_fmt_eq_lhs(c, d)} = {f}"
    m1, m2 = d, b  # multiply (1) by d and (2) by b so the y-coefficients match (b*d = d*b)
    new_a1, new_b1, new_e1 = a * m1, b * m1, e * m1
    new_a2, new_b2, new_e2 = c * m2, d * m2, f * m2
    if new_b1 != new_b2:
        raise ValueError("simultaneous_different_coefficient verification failed: y-coefficients do not match")
    new_coeff, new_const = new_a1 - new_a2, new_e1 - new_e2

    steps = [
        f"{eq1}  (1)",
        f"{eq2}  (2)",
        f"(1) × {m1}: {_fmt_eq_lhs(new_a1, new_b1)} = {new_e1}  (3)",
        f"(2) × {m2}: {_fmt_eq_lhs(new_a2, new_b2)} = {new_e2}  (4)",
        f"(3) - (4): {new_coeff}x = {new_const}, so x = {sol_x}",
        f"Substitute x = {sol_x} into (1): {b}y = {e - a * sol_x}, so y = {sol_y}",
    ]
    return Question(
        topic_id="simultaneous_different_coefficient",
        tier=Tier.HIGHER,
        prompt=f"Solve the simultaneous equations: {eq1} and {eq2}",
        solution_steps=tuple(steps),
        final_answer=f"x = {sol_x}, y = {sol_y}",
        dedup_key=f"sim_different:{a}:{b}:{c}:{d}:{e}:{f}",
    )


def generate_forming_and_solving(tier: Tier, rng: random.Random) -> Question:
    price_x = rng.randint(10, 90)
    price_y = rng.randint(10, 90)
    while price_y == price_x:
        price_y = rng.randint(10, 90)

    for _ in range(100):
        n1x, n1y = rng.randint(1, 5), rng.randint(1, 5)
        n2x, n2y = rng.randint(1, 5), rng.randint(1, 5)
        if n1x * n2y != n1y * n2x:
            break
    else:
        raise ValueError("simultaneous_forming_and_solving could not find valid quantities")

    total1 = n1x * price_x + n1y * price_y
    total2 = n2x * price_x + n2y * price_y

    solution = sp.solve([sp.Eq(n1x * Xs + n1y * Ys, total1), sp.Eq(n2x * Xs + n2y * Ys, total2)], [Xs, Ys])
    if solution.get(Xs) != price_x or solution.get(Ys) != price_y:
        raise ValueError("simultaneous_forming_and_solving verification failed")

    item_x, item_y = rng.choice(_ITEM_PAIRS)
    plural_x1, plural_y1 = ("s" if n1x != 1 else ""), ("s" if n1y != 1 else "")
    plural_x2, plural_y2 = ("s" if n2x != 1 else ""), ("s" if n2y != 1 else "")

    prompt = (
        f"{n1x} {item_x}{plural_x1} and {n1y} {item_y}{plural_y1} cost {_fmt_pence(total1)} in total. "
        f"{n2x} {item_x}{plural_x2} and {n2y} {item_y}{plural_y2} cost {_fmt_pence(total2)} in total. "
        f"Form and solve a pair of simultaneous equations to find the cost of one {item_x} and one {item_y}."
    )
    steps = [
        f"Let x = cost of one {item_x} (pence), y = cost of one {item_y} (pence).",
        f"{n1x}x + {n1y}y = {total1}  (1)",
        f"{n2x}x + {n2y}y = {total2}  (2)",
        f"Solving simultaneously: x = {price_x}, y = {price_y}",
    ]
    return Question(
        topic_id="simultaneous_forming_and_solving",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=f"{item_x} = {_fmt_pence(price_x)}, {item_y} = {_fmt_pence(price_y)}",
        dedup_key=f"sim_forming:{item_x}:{item_y}:{n1x}:{n1y}:{n2x}:{n2y}:{price_x}:{price_y}",
    )


def generate_simultaneous_quadratic(tier: Tier, rng: random.Random) -> Question:
    r1 = _rand_nonzero(rng, -6, 6)
    r2 = _rand_nonzero(rng, -6, 6)
    while r2 == r1:
        r2 = _rand_nonzero(rng, -6, 6)
    B = rng.randint(-4, 4)
    C = rng.randint(-8, 8)
    m = B + r1 + r2
    c = C - r1 * r2

    y1, y2 = m * r1 + c, m * r2 + c
    if y1 != r1**2 + B * r1 + C or y2 != r2**2 + B * r2 + C:
        raise ValueError("simultaneous_quadratic verification failed: curve/line mismatch")

    # Independent verification via sympy's nonlinear solver.
    sol = sp.solve([sp.Eq(Ys, Xs**2 + B * Xs + C), sp.Eq(Ys, m * Xs + c)], [Xs, Ys])
    sol_set = {(int(s[0]), int(s[1])) for s in sol}
    if sol_set != {(r1, y1), (r2, y2)}:
        raise ValueError("simultaneous_quadratic verification failed: sympy cross-check mismatch")

    quad_str, line_str = f"y = {_fmt_quad_expr(B, C)}", f"y = {fmt_linear(m, c)}"
    rearranged_b, rearranged_c = B - m, C - c
    steps = [
        f"Substitute {line_str} into {quad_str}: {fmt_linear(m, c)} = {_fmt_quad_expr(B, C)}",
        f"Rearrange: {_fmt_quad_expr(rearranged_b, rearranged_c)} = 0",
        f"Factorise: {_fmt_root_factor(r1)}{_fmt_root_factor(r2)} = 0",
        f"x = {r1} or x = {r2}",
        f"When x = {r1}, y = {y1}. When x = {r2}, y = {y2}.",
    ]
    return Question(
        topic_id="simultaneous_quadratic",
        tier=Tier.HIGHER,
        prompt=f"Solve the simultaneous equations: {quad_str} and {line_str}",
        solution_steps=tuple(steps),
        final_answer=f"({r1}, {y1}) and ({r2}, {y2})",
        dedup_key=f"sim_quad:{r1}:{r2}:{B}:{C}",
    )


def generate_simultaneous_graphically(tier: Tier, rng: random.Random) -> Question:
    sol_x = rng.randint(-5, 5)
    sol_y = rng.randint(-5, 5)
    m1 = _rand_nonzero(rng, -4, 4)
    c1 = sol_y - m1 * sol_x
    m2 = _rand_nonzero(rng, -4, 4)
    while m2 == m1:
        m2 = _rand_nonzero(rng, -4, 4)
    c2 = sol_y - m2 * sol_x

    solution = sp.solve([sp.Eq(Ys, m1 * Xs + c1), sp.Eq(Ys, m2 * Xs + c2)], [Xs, Ys])
    if solution.get(Xs) != sol_x or solution.get(Ys) != sol_y:
        raise ValueError("simultaneous_graphically verification failed")

    line1, line2 = f"y = {fmt_linear(m1, c1)}", f"y = {fmt_linear(m2, c2)}"
    steps = [
        "The solution to a pair of simultaneous equations is the point where their graphs intersect.",
        f"The lines cross at x = {sol_x}, y = {sol_y}.",
    ]
    return Question(
        topic_id="simultaneous_graphically",
        tier=Tier.FOUNDATION,
        prompt=(
            f"The graphs of {line1} and {line2} are shown below. "
            "Use the graphs to write down the solution to the simultaneous equations."
        ),
        solution_steps=tuple(steps),
        final_answer=f"x = {sol_x}, y = {sol_y}",
        dedup_key=f"sim_graph:{m1}:{c1}:{m2}:{c2}",
        diagram=DiagramSpec(
            kind="linear_graph_pair",
            params={"intersection_label": "?", "label1": line1, "label2": line2},
        ),
    )


def generate_modelled_example_common_coefficient(tier: Tier, rng: random.Random) -> ModelledExample:
    sol_x = _rand_nonzero(rng, -8, 8)
    sol_y = _rand_nonzero(rng, -8, 8)
    a = rng.randint(1, 6)
    c = rng.randint(1, 6)
    while c == a:
        c = rng.randint(1, 6)
    k = rng.randint(1, 5)
    same_sign = rng.choice([True, False])
    b = k
    d = k if same_sign else -k
    e = a * sol_x + b * sol_y
    f = c * sol_x + d * sol_y

    solution = sp.solve([sp.Eq(a * Xs + b * Ys, e), sp.Eq(c * Xs + d * Ys, f)], [Xs, Ys])
    if solution.get(Xs) != sol_x or solution.get(Ys) != sol_y:
        raise ValueError("modelled example simultaneous_common_coefficient verification failed")

    eq1, eq2 = f"{_fmt_eq_lhs(a, b)} = {e}", f"{_fmt_eq_lhs(c, d)} = {f}"
    op = "Subtract" if same_sign else "Add"
    new_coeff = (a - c) if same_sign else (a + c)
    new_const = (e - f) if same_sign else (e + f)

    teaching_steps = [
        f"Both equations already have the same y-coefficient size ({b} and {abs(d)}), so we can "
        f"eliminate y in one step without having to scale either equation first.",
        f"{'When the y-coefficients have the same sign, subtracting one equation from the other cancels y.' if same_sign else 'When the y-coefficients have opposite signs, adding the two equations cancels y.'} "
        f"{op} equation (2) {'from' if same_sign else 'to'} equation (1): "
        f"{new_coeff}x = {new_const}, so x = {sol_x}.",
        f"Now substitute x = {sol_x} back into equation (1) to find y: "
        f"{_fmt_eq_lhs(a, b)} becomes {a}×({sol_x}) + {b}y = {e}, so {b}y = {e - a * sol_x}, giving y = {sol_y}.",
        f"Check in equation (2): {c}×({sol_x}) + {d}×({sol_y}) = {c * sol_x + d * sol_y}, which matches "
        f"the right-hand side {f}, confirming the solution.",
    ]
    worked_calculation = [
        f"{eq1}  (1)",
        f"{eq2}  (2)",
        f"{op} (1) and (2): {new_coeff}x = {new_const}",
        f"x = {sol_x}",
        f"y = {sol_y}",
    ]
    return ModelledExample(
        topic_id="simultaneous_common_coefficient",
        tier=Tier.FOUNDATION,
        prompt=f"Solve the simultaneous equations: {eq1} and {eq2}",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"x = {sol_x}, y = {sol_y}",
    )


def generate_modelled_example_different_coefficient(tier: Tier, rng: random.Random) -> ModelledExample:
    sol_x = _rand_nonzero(rng, -9, 9)
    sol_y = _rand_nonzero(rng, -9, 9)

    for _ in range(100):
        a, b = _rand_nonzero(rng, 2, 5), _rand_nonzero(rng, 2, 5)
        c, d = _rand_nonzero(rng, 2, 5), _rand_nonzero(rng, 2, 5)
        if a * d != b * c and a != c and b != d:
            break
    else:
        raise ValueError("modelled example simultaneous_different_coefficient could not find valid coefficients")

    e = a * sol_x + b * sol_y
    f = c * sol_x + d * sol_y

    solution = sp.solve([sp.Eq(a * Xs + b * Ys, e), sp.Eq(c * Xs + d * Ys, f)], [Xs, Ys])
    if solution.get(Xs) != sol_x or solution.get(Ys) != sol_y:
        raise ValueError("modelled example simultaneous_different_coefficient verification failed")

    eq1, eq2 = f"{_fmt_eq_lhs(a, b)} = {e}", f"{_fmt_eq_lhs(c, d)} = {f}"
    m1, m2 = d, b
    new_a1, new_b1, new_e1 = a * m1, b * m1, e * m1
    new_a2, new_b2, new_e2 = c * m2, d * m2, f * m2
    if new_b1 != new_b2:
        raise ValueError("modelled example simultaneous_different_coefficient verification failed: y mismatch")
    new_coeff, new_const = new_a1 - new_a2, new_e1 - new_e2

    teaching_steps = [
        f"Here neither the x-coefficients ({a}, {c}) nor the y-coefficients ({b}, {d}) match, so before "
        "we can eliminate a variable by adding or subtracting, we need to scale the equations so one "
        "pair of coefficients becomes equal.",
        f"Multiply equation (1) by {m1} and equation (2) by {m2} - chosen so that both equations end up "
        f"with the same y-coefficient ({b}×{m1} = {d}×{m2} = {new_b1}).",
        f"(1)×{m1} gives {_fmt_eq_lhs(new_a1, new_b1)} = {new_e1}. (2)×{m2} gives "
        f"{_fmt_eq_lhs(new_a2, new_b2)} = {new_e2}.",
        f"Now the y-coefficients match, so subtract to eliminate y: {new_coeff}x = {new_const}, so "
        f"x = {sol_x}. Substitute back into equation (1) to get {b}y = {e - a * sol_x}, so y = {sol_y}.",
    ]
    worked_calculation = [
        f"{eq1}  (1)",
        f"{eq2}  (2)",
        f"(1)×{m1}: {_fmt_eq_lhs(new_a1, new_b1)} = {new_e1}",
        f"(2)×{m2}: {_fmt_eq_lhs(new_a2, new_b2)} = {new_e2}",
        f"Subtract: {new_coeff}x = {new_const}",
        f"x = {sol_x}, y = {sol_y}",
    ]
    return ModelledExample(
        topic_id="simultaneous_different_coefficient",
        tier=Tier.HIGHER,
        prompt=f"Solve the simultaneous equations: {eq1} and {eq2}",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"x = {sol_x}, y = {sol_y}",
    )


def generate_modelled_example_forming_and_solving(tier: Tier, rng: random.Random) -> ModelledExample:
    price_x = rng.randint(10, 90)
    price_y = rng.randint(10, 90)
    while price_y == price_x:
        price_y = rng.randint(10, 90)

    for _ in range(100):
        n1x, n1y = rng.randint(1, 5), rng.randint(1, 5)
        n2x, n2y = rng.randint(1, 5), rng.randint(1, 5)
        if n1x * n2y != n1y * n2x:
            break
    else:
        raise ValueError("modelled example simultaneous_forming_and_solving could not find valid quantities")

    total1 = n1x * price_x + n1y * price_y
    total2 = n2x * price_x + n2y * price_y

    solution = sp.solve([sp.Eq(n1x * Xs + n1y * Ys, total1), sp.Eq(n2x * Xs + n2y * Ys, total2)], [Xs, Ys])
    if solution.get(Xs) != price_x or solution.get(Ys) != price_y:
        raise ValueError("modelled example simultaneous_forming_and_solving verification failed")

    item_x, item_y = rng.choice(_ITEM_PAIRS)
    plural_x1, plural_y1 = ("s" if n1x != 1 else ""), ("s" if n1y != 1 else "")
    plural_x2, plural_y2 = ("s" if n2x != 1 else ""), ("s" if n2y != 1 else "")

    prompt = (
        f"{n1x} {item_x}{plural_x1} and {n1y} {item_y}{plural_y1} cost {_fmt_pence(total1)} in total. "
        f"{n2x} {item_x}{plural_x2} and {n2y} {item_y}{plural_y2} cost {_fmt_pence(total2)} in total. "
        f"Form and solve a pair of simultaneous equations to find the cost of one {item_x} and one {item_y}."
    )
    m1, m2 = n2y, n1y
    new_a1, new_e1 = n1x * m1, total1 * m1
    new_a2, new_e2 = n2x * m2, total2 * m2
    new_coeff, new_const = new_a1 - new_a2, new_e1 - new_e2

    teaching_steps = [
        f"The words describe two unknown prices, so start by naming them: let x = cost of one {item_x} "
        f"in pence, and y = cost of one {item_y} in pence.",
        f"Turn each sentence into an equation: '{n1x} {item_x}{plural_x1} and {n1y} {item_y}{plural_y1} "
        f"cost {_fmt_pence(total1)}' becomes {n1x}x + {n1y}y = {total1}. The second sentence becomes "
        f"{n2x}x + {n2y}y = {total2}.",
        "These are just an ordinary pair of simultaneous equations now, so solve them by scaling and "
        "eliminating one variable as usual.",
        f"Scaling and eliminating y gives x = {price_x} and y = {price_y}, i.e. one {item_x} costs "
        f"{_fmt_pence(price_x)} and one {item_y} costs {_fmt_pence(price_y)}.",
    ]
    worked_calculation = [
        f"{n1x}x + {n1y}y = {total1}  (1)",
        f"{n2x}x + {n2y}y = {total2}  (2)",
        f"(1)×{m1} - (2)×{m2}: {new_coeff}x = {new_const}",
        f"x = {price_x}, y = {price_y}",
    ]
    return ModelledExample(
        topic_id="simultaneous_forming_and_solving",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{item_x} = {_fmt_pence(price_x)}, {item_y} = {_fmt_pence(price_y)}",
    )


def generate_modelled_example_simultaneous_quadratic(tier: Tier, rng: random.Random) -> ModelledExample:
    r1 = _rand_nonzero(rng, -6, 6)
    r2 = _rand_nonzero(rng, -6, 6)
    while r2 == r1:
        r2 = _rand_nonzero(rng, -6, 6)
    B = rng.randint(-4, 4)
    C = rng.randint(-8, 8)
    m = B + r1 + r2
    c = C - r1 * r2

    y1, y2 = m * r1 + c, m * r2 + c
    if y1 != r1**2 + B * r1 + C or y2 != r2**2 + B * r2 + C:
        raise ValueError("modelled example simultaneous_quadratic verification failed")

    sol = sp.solve([sp.Eq(Ys, Xs**2 + B * Xs + C), sp.Eq(Ys, m * Xs + c)], [Xs, Ys])
    sol_set = {(int(s[0]), int(s[1])) for s in sol}
    if sol_set != {(r1, y1), (r2, y2)}:
        raise ValueError("modelled example simultaneous_quadratic verification failed: sympy cross-check")

    quad_str, line_str = f"y = {_fmt_quad_expr(B, C)}", f"y = {fmt_linear(m, c)}"
    rearranged_b, rearranged_c = B - m, C - c

    teaching_steps = [
        "Where a straight line and a curve meet, both equations must give the same y for the same x, "
        "so the standard method is to substitute one equation into the other, turning two equations "
        "into a single equation in x alone.",
        f"Substitute the line {line_str} into the curve {quad_str} (replacing y in the curve's equation): "
        f"{fmt_linear(m, c)} = {_fmt_quad_expr(B, C)}.",
        f"Rearrange everything onto one side so it equals zero: {_fmt_quad_expr(rearranged_b, rearranged_c)} = 0. "
        f"This factorises as {_fmt_root_factor(r1)}{_fmt_root_factor(r2)} = 0, giving x = {r1} or x = {r2} "
        "- a quadratic generally has two intersection points, not one.",
        f"Finally, find the matching y-value for each x by substituting back into the line (the simpler "
        f"equation): when x = {r1}, y = {y1}; when x = {r2}, y = {y2}.",
    ]
    worked_calculation = [
        f"{fmt_linear(m, c)} = {_fmt_quad_expr(B, C)}",
        f"{_fmt_quad_expr(rearranged_b, rearranged_c)} = 0",
        f"{_fmt_root_factor(r1)}{_fmt_root_factor(r2)} = 0",
        f"x = {r1} or x = {r2}",
        f"({r1}, {y1}) and ({r2}, {y2})",
    ]
    return ModelledExample(
        topic_id="simultaneous_quadratic",
        tier=Tier.HIGHER,
        prompt=f"Solve the simultaneous equations: {quad_str} and {line_str}",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"({r1}, {y1}) and ({r2}, {y2})",
    )


def generate_modelled_example_simultaneous_graphically(tier: Tier, rng: random.Random) -> ModelledExample:
    sol_x = rng.randint(-5, 5)
    sol_y = rng.randint(-5, 5)
    m1 = _rand_nonzero(rng, -4, 4)
    c1 = sol_y - m1 * sol_x
    m2 = _rand_nonzero(rng, -4, 4)
    while m2 == m1:
        m2 = _rand_nonzero(rng, -4, 4)
    c2 = sol_y - m2 * sol_x

    solution = sp.solve([sp.Eq(Ys, m1 * Xs + c1), sp.Eq(Ys, m2 * Xs + c2)], [Xs, Ys])
    if solution.get(Xs) != sol_x or solution.get(Ys) != sol_y:
        raise ValueError("modelled example simultaneous_graphically verification failed")

    line1, line2 = f"y = {fmt_linear(m1, c1)}", f"y = {fmt_linear(m2, c2)}"
    teaching_steps = [
        "Every point on a graph's line satisfies that line's equation. Where two lines cross, that single "
        "point lies on both lines at once - so it must satisfy both equations simultaneously, which is "
        "exactly what we're looking for.",
        "This means the solution to a pair of simultaneous equations can simply be read off as the "
        "coordinates of the point where their two graphs intersect - no algebra required.",
        f"Reading the graph, the two lines cross at the point ({sol_x}, {sol_y}).",
        f"So the solution is x = {sol_x}, y = {sol_y}.",
    ]
    worked_calculation = [
        f"{line1}",
        f"{line2}",
        f"Intersection: ({sol_x}, {sol_y})",
    ]
    return ModelledExample(
        topic_id="simultaneous_graphically",
        tier=Tier.FOUNDATION,
        prompt=(
            f"The graphs of {line1} and {line2} are shown below. "
            "Use the graphs to write down the solution to the simultaneous equations."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"x = {sol_x}, y = {sol_y}",
        diagram=DiagramSpec(
            kind="linear_graph_pair",
            params={"intersection_label": f"({sol_x}, {sol_y})", "label1": line1, "label2": line2},
        ),
    )


TOPIC_COMMON_COEFFICIENT = TopicDefinition(
    id="simultaneous_common_coefficient",
    display_name="Common Coefficient",
    description="Solve simultaneous equations where a coefficient already matches, by adding or subtracting.",
    generate=generate_common_coefficient,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_common_coefficient,
)

TOPIC_DIFFERENT_COEFFICIENT = TopicDefinition(
    id="simultaneous_different_coefficient",
    display_name="Different Coefficients",
    description="Solve simultaneous equations by scaling one or both equations before eliminating.",
    generate=generate_different_coefficient,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_different_coefficient,
)

TOPIC_FORMING_AND_SOLVING = TopicDefinition(
    id="simultaneous_forming_and_solving",
    display_name="Forming and Solving",
    description="Form a pair of simultaneous equations from a worded context, then solve them.",
    generate=generate_forming_and_solving,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_forming_and_solving,
)

TOPIC_QUADRATIC = TopicDefinition(
    id="simultaneous_quadratic",
    display_name="Quadratic Simultaneous Equations",
    description="Solve a linear equation simultaneously with a quadratic equation.",
    generate=generate_simultaneous_quadratic,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_simultaneous_quadratic,
)

TOPIC_GRAPHICALLY = TopicDefinition(
    id="simultaneous_graphically",
    display_name="Solving Graphically",
    description="Read the solution to a pair of simultaneous linear equations from their graphs.",
    generate=generate_simultaneous_graphically,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_simultaneous_graphically,
)
