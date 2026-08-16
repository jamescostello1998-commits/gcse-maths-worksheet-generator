import dataclasses
import random

import sympy as sp

from app.core.models import DiagramSpec, ModelledExample, Question, Tier
from app.topics.algebra_utils import X, fmt_linear, fmt_num, solve_linear_with_steps
from app.topics.base import TopicDefinition

SECTION = "algebra"
GROUP = "Forming and Solving Equations"

# Shared by the "people" (ages/money) word-problem contexts, Foundation and
# Higher alike - a small name pool for real variety (not the same two names
# every time), and two contexts (ages / money) with their own natural
# relation words ("older"/"younger" reads right for ages; "more"/"less"
# reads right for money - "5 pence older" would be wrong).
_PEOPLE_NAMES = [
    "Alex", "Sam", "Priya", "Jordan", "Maya", "Liam", "Zara", "Ravi", "Ellie", "Noah",
]
_TWO_PERSON_CONTEXTS = [
    {
        "unit": "years old", "diff_unit": "years", "item": "age", "item_plural": "ages",
        "more_word": "older", "less_word": "younger",
    },
    {
        "unit": "pence", "diff_unit": "pence", "item": "amount of money", "item_plural": "amounts of money",
        "more_word": "more", "less_word": "less",
    },
]
_MULTIPLE_WORDS = {2: "double", 3: "three times", 4: "four times"}


# ---------------------------------------------------------------------------
# Foundation: one/two-step equations, positive coefficient throughout.
# ---------------------------------------------------------------------------


def _words_foundation(rng: random.Random) -> Question:
    a = rng.randint(2, 9)
    b = rng.randint(1, 20)
    x_val = rng.randint(1, 20)
    c = a * x_val + b

    solve_steps, solution = solve_linear_with_steps(a, b, 0, c)
    # Independent verification: substitute the claimed solution back into the
    # original "multiply then add" description via sympy, a different path
    # than the manual step-by-step algebra above.
    residual = sp.simplify((a * X + b).subs(X, solution) - c)
    if residual != 0:
        raise ValueError("forming_equations words (foundation) verification failed")

    steps = ["Let the number be x.", f"{fmt_linear(a, b)} = {c}"] + solve_steps[1:]
    return Question(
        topic_id="forming_equations_F",
        tier=Tier.FOUNDATION,
        prompt=(
            f"I think of a number, multiply it by {a} and add {b}. The result is {c}. "
            "Form an equation and solve it to find the number."
        ),
        solution_steps=tuple(steps),
        final_answer=fmt_num(solution),
        dedup_key=f"form_words:{a}:{b}:{c}",
    )


def _people_foundation(rng: random.Random) -> Question:
    """Two people/quantities, one defined relative to the other by a plain
    addition/subtraction ("N years older/younger than", "N pence more/less
    than"), summing to a given total - a genuinely different word-problem
    context from the "think of a number" style above (real GCSE papers use
    both), per direct user request checked against real Corbett Maths
    examples."""
    name1, name2 = rng.sample(_PEOPLE_NAMES, 2)
    ctx = rng.choice(_TWO_PERSON_CONTEXTS)
    k = rng.randint(1, 20)
    is_more = rng.random() < 0.5
    word = ctx["more_word"] if is_more else ctx["less_word"]
    const = k if is_more else -k
    x_val = rng.randint(max(5, k + 1), 40)
    total = x_val + (x_val + const)

    equation_line = f"x + ({fmt_linear(1, const)}) = {total}"
    collect_line = f"{fmt_linear(2, const)} = {total}"
    solve_steps, solution = solve_linear_with_steps(2, const, 0, total)
    # Independent verification: substitute the solution back into BOTH
    # people's own original (unexpanded) values, not the combined 2x+const
    # used to solve it.
    computed = solution + (solution + const)
    if computed != total:
        raise ValueError("forming_equations people (foundation) verification failed")

    steps = [
        f"Let {name1}'s {ctx['item']} be x.",
        equation_line,
        "Collect like terms:",
        collect_line,
    ] + solve_steps[1:]
    prompt = (
        f"{name1} is x {ctx['unit']}.\n"
        f"{name2} is {k} {ctx['diff_unit']} {word} than {name1}.\n"
        f"The sum of their {ctx['item_plural']} is {total}.\n"
        "Form an equation and solve it to find x."
    )
    return Question(
        topic_id="forming_equations_F",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=fmt_num(solution),
        dedup_key=f"form_people:{ctx['unit']}:{k}:{is_more}:{x_val}",
    )


def _consecutive_foundation(rng: random.Random) -> Question:
    """The sum of three consecutive numbers - a classic, distinct GCSE
    forming-equations context (never reduces to a simple "multiply and
    add" or "two people" question), per direct user request."""
    x_val = rng.randint(1, 40)
    total = x_val + (x_val + 1) + (x_val + 2)
    coeff, const = 3, 3

    equation_line = "x + (x + 1) + (x + 2) = " + str(total)
    collect_line = f"{fmt_linear(coeff, const)} = {total}"
    solve_steps, solution = solve_linear_with_steps(coeff, const, 0, total)
    # Independent verification: substitute the solution back into the three
    # original (unexpanded) consecutive terms, not the combined 3x+3.
    computed = solution + (solution + 1) + (solution + 2)
    if computed != total:
        raise ValueError("forming_equations consecutive (foundation) verification failed")

    steps = [
        "Let the first number be x.",
        equation_line,
        "Collect like terms:",
        collect_line,
    ] + solve_steps[1:]
    return Question(
        topic_id="forming_equations_F",
        tier=Tier.FOUNDATION,
        prompt=(
            f"The sum of three consecutive numbers is {total}. Form an equation (using x for "
            "the first number) and solve it to find the three numbers."
        ),
        solution_steps=tuple(steps),
        final_answer=f"{solution}, {solution + 1}, {solution + 2}",
        dedup_key=f"form_consecutive:{x_val}",
    )


def _angle_fact_diagram(fact: str, values: list, labels: list) -> DiagramSpec:
    """Shared by the Foundation (straight/point/triangle) and Higher
    (quadrilateral) angle branches - `values` are the real numeric angle
    values (so the rays/vertices are laid out with correct geometry) while
    `labels` are the pre-formatted display strings, algebraic where
    unknown, per the app's established "pass pre-formatted labels, not
    bare values" convention."""
    if fact == "triangle":
        return DiagramSpec(kind="triangle_angles", params={"angle_labels": labels})
    if fact == "quadrilateral":
        return DiagramSpec(kind="polygon_angles", params={"n_sides": 4, "angle_labels": labels})
    return DiagramSpec(
        kind="angle_line",
        params={"angle_values": values, "labels": labels, "around_point": fact == "point"},
    )


def _angles_foundation(rng: random.Random) -> Question:
    fact = rng.choice(["straight", "point", "triangle"])
    if fact == "straight":
        target, n_known, fact_text = 180, 1, "Angles on a straight line sum to 180°."
    elif fact == "point":
        target, n_known, fact_text = 360, rng.choice([1, 2]), "Angles around a point sum to 360°."
    else:
        target, n_known, fact_text = 180, 2, "Angles in a triangle sum to 180°."

    for _ in range(300):
        coeff = rng.randint(1, 5)
        x_val = rng.randint(2, 20)
        known = [rng.randint(15, 90) for _ in range(n_known)]
        const = target - coeff * x_val - sum(known)
        algebraic_angle = coeff * x_val + const
        if 5 <= algebraic_angle <= target - 10 and all(5 <= k <= target - 10 for k in known):
            break
    else:
        raise ValueError("forming_equations angle (foundation) generation failed")

    expr = fmt_linear(coeff, const)
    target_eq = target - sum(known)

    solve_steps, solution = solve_linear_with_steps(coeff, const, 0, target_eq)
    # Independent verification: substitute the solution back into every angle
    # expression and confirm the angles genuinely sum to the fact's total -
    # a different check than the algebra used to isolate x.
    check_total = sum(known) + int((coeff * X + const).subs(X, solution))
    if check_total != target:
        raise ValueError("forming_equations angle (foundation) verification failed")

    if fact == "straight":
        prompt = (
            f"Two angles on a straight line are {known[0]}° and ({expr})°. "
            "Form an equation and solve it to find x."
        )
    elif fact == "point":
        known_text = " and ".join(f"{k}°" for k in known)
        prompt = (
            f"The angles {known_text} and ({expr})° lie around a point. "
            "Form an equation and solve it to find x."
        )
    else:
        prompt = (
            f"A triangle has angles {known[0]}°, {known[1]}°, and ({expr})°. "
            "Form an equation and solve it to find x."
        )

    sum_parts = [str(k) for k in known] + [f"({expr})"]
    equation_line = " + ".join(sum_parts) + f" = {target}"
    steps = [fact_text, equation_line] + solve_steps
    return Question(
        topic_id="forming_equations_F",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=fmt_num(solution),
        dedup_key=f"form_angle:{fact}:{coeff}:{const}:{'-'.join(map(str, known))}",
        diagram=_angle_fact_diagram(
            fact, known + [algebraic_angle], [f"{k}°" for k in known] + [f"({expr})°"]
        ),
    )


def _area_foundation(rng: random.Random) -> Question:
    shape = rng.choice(["perimeter", "area"])
    if shape == "perimeter":
        m = rng.randint(3, 15)
        k = rng.randint(0, 10)
        x_val = rng.randint(2, 20)
        other_expr = f"x + {k}" if k > 0 else "x"
        other_val = x_val + k
        total = 2 * (other_val + m)

        coeff, const = 2, 2 * k + 2 * m
        solve_steps, solution = solve_linear_with_steps(coeff, const, 0, total)
        # Independent verification: substitute the solution back into the
        # original perimeter formula directly, not via the solved equation.
        computed = 2 * ((solution + k) + m)
        if computed != total:
            raise ValueError("forming_equations area (foundation, perimeter) verification failed")

        prompt = f"The perimeter of the rectangle shown is {total} cm. Form an equation and solve it to find x."
        equation_line = f"2({other_expr}) + 2({m}) = {total}"
        steps = ["Perimeter = 2 × (sum of two different side lengths)."] + [equation_line] + solve_steps
        dedup_key = f"form_area:perimeter:{m}:{k}:{x_val}"
        diagram = DiagramSpec(
            kind="rectangle",
            params={
                "width": other_val, "height": m,
                "width_label": f"({other_expr}) cm", "height_label": f"{m} cm",
            },
        )
    else:
        m = rng.randint(3, 12)
        x_val = rng.randint(2, 20)
        total = m * x_val

        coeff, const = m, 0
        solve_steps, solution = solve_linear_with_steps(coeff, const, 0, total)
        # Independent verification: substitute back into the area formula.
        computed = m * solution
        if computed != total:
            raise ValueError("forming_equations area (foundation, area) verification failed")

        prompt = f"The area of the rectangle shown is {total} cm². Form an equation and solve it to find x."
        equation_line = f"{m}x = {total}"
        steps = ["Area of a rectangle = length × width."] + [equation_line] + solve_steps
        dedup_key = f"form_area:area:{m}:{x_val}"
        diagram = DiagramSpec(
            kind="rectangle",
            params={"width": x_val, "height": m, "width_label": "x cm", "height_label": f"{m} cm"},
        )

    return Question(
        topic_id="forming_equations_F",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=fmt_num(solution),
        dedup_key=dedup_key,
        diagram=diagram,
    )


def generate_forming_equations_foundation(tier: Tier, rng: random.Random) -> Question:
    context = rng.choice(["words", "people", "consecutive", "angles", "area"])
    if context == "words":
        q = _words_foundation(rng)
    elif context == "people":
        q = _people_foundation(rng)
    elif context == "consecutive":
        q = _consecutive_foundation(rng)
    elif context == "angles":
        q = _angles_foundation(rng)
    else:
        q = _area_foundation(rng)
    return dataclasses.replace(q, topic_id="forming_equations_F", tier=Tier.FOUNDATION)


# ---------------------------------------------------------------------------
# Higher: brackets, x-terms to collect, harder geometric contexts.
# ---------------------------------------------------------------------------


def _l_shape_perimeter_diagram(m: int, n: int, k: int, x_val: int) -> DiagramSpec:
    """The Higher perimeter scenario's shape is an L-shape whose bottom
    width is the algebraic (x + k) - a real, correctly-drawable L-shape
    (perimeter = 2 x outer width + 2 x outer height) rather than an
    abstract "three independent side pairs" description with no actual
    polygon behind it. The notch height is set to exactly m, so the
    right-hand edge is genuinely split by the notch into two real
    segments of length n (upper) and m (lower) - each labelled directly,
    rather than showing a single misleading "(m + n) cm" combined label
    that reads like unevaluated arithmetic. The notch width is purely
    illustrative (it doesn't affect the perimeter)."""
    outer_w, outer_h = x_val + k, m + n
    inner_w = max(1, min(outer_w - 1, round(outer_w * 0.35)))
    inner_h = m
    return DiagramSpec(
        kind="l_shape",
        params={
            "outer_w": outer_w, "outer_h": outer_h, "inner_w": inner_w, "inner_h": inner_h,
            "notch": "corner",
            "outer_labels": [f"(x + {k}) cm", f"({m} + {n}) cm"],
            "right_labels": [f"{n} cm", f"{m} cm"],
        },
    )


_POLYGON_NAMES = {5: "pentagon", 6: "hexagon", 7: "heptagon", 8: "octagon"}


def _fmt_xk(k: int) -> str:
    return f"(x + {k})" if k > 0 else "x"


def _build_perimeter_higher(rng: random.Random):
    """Build one of 6 Higher perimeter-forming-equation shapes: the
    original L-shape (one algebraic side), or 5 new ones added per direct
    user request (checked against real Corbett Maths examples) - a
    rectangle/parallelogram with two independently algebraic sides
    (x+b and x+d), an isosceles triangle (two equal x+k sides + a
    different base), a right-angled triangle with three independently
    algebraic sides, and a regular polygon with one algebraic side (all
    sides equal, so one label is enough). Every new shape's sides use a
    plain "x + k" form (coefficient 1) - deliberately simpler than also
    varying the coefficient, to keep this batch's construction/
    verification straightforward. Returns (shape_desc, equation_line,
    expand_step, coeff, const, total, solve_steps, solution, dedup_key,
    diagram)."""
    shape = rng.choice(["l_shape", "rectangle", "isosceles", "parallelogram", "right_triangle", "polygon"])
    x_val = rng.randint(2, 20)

    if shape == "l_shape":
        m = rng.randint(3, 15)
        n = rng.randint(3, 15)
        k = rng.randint(1, 10)
        total = 2 * m + 2 * n + 2 * (x_val + k)
        coeff, const = 2, 2 * m + 2 * n + 2 * k
        shape_desc = "L-shape"
        equation_line = f"2(x + {k}) + 2({m} + {n}) = {total}"
        expand_step = f"Expand the bracket (2 × x and 2 × {k}) and collect the constants:"
        dedup_key = f"perim_h:l_shape:{m}:{n}:{k}:{x_val}"
        diagram = _l_shape_perimeter_diagram(m, n, k, x_val)
    elif shape == "rectangle":
        b = rng.randint(1, 10)
        e = rng.randint(1, 10)
        while e == b:
            e = rng.randint(1, 10)
        total = 2 * (x_val + b) + 2 * (x_val + e)
        coeff, const = 4, 2 * (b + e)
        shape_desc = "rectangle"
        equation_line = f"2(x + {b}) + 2(x + {e}) = {total}"
        expand_step = "Expand both brackets and collect like terms:"
        dedup_key = f"perim_h:rectangle:{b}:{e}:{x_val}"
        diagram = DiagramSpec(
            kind="rectangle",
            params={
                "width": x_val + b, "height": x_val + e,
                "width_label": f"(x + {b}) cm", "height_label": f"(x + {e}) cm",
            },
        )
    elif shape == "isosceles":
        k = rng.randint(1, 10)
        m = rng.randint(0, 10)
        while m == k:
            m = rng.randint(0, 10)
        total = 2 * (x_val + k) + (x_val + m)
        coeff, const = 3, 2 * k + m
        equal_label = f"(x + {k}) cm"
        base_label = f"{_fmt_xk(m)} cm"
        shape_desc = "isosceles triangle"
        equation_line = f"(x + {k}) + (x + {k}) + {_fmt_xk(m)} = {total}"
        expand_step = "Collect like terms:"
        dedup_key = f"perim_h:isosceles:{k}:{m}:{x_val}"
        diagram = DiagramSpec(
            kind="general_triangle",
            params={"side_a_label": equal_label, "side_b_label": equal_label, "side_c_label": base_label},
        )
    elif shape == "parallelogram":
        b = rng.randint(1, 10)
        s = rng.randint(1, 10)
        while s == b:
            s = rng.randint(1, 10)
        total = 2 * (x_val + b) + 2 * (x_val + s)
        coeff, const = 4, 2 * (b + s)
        shape_desc = "parallelogram"
        equation_line = f"2(x + {b}) + 2(x + {s}) = {total}"
        expand_step = "Expand both brackets and collect like terms:"
        dedup_key = f"perim_h:parallelogram:{b}:{s}:{x_val}"
        diagram = DiagramSpec(
            kind="parallelogram_perimeter",
            params={"base_label": f"(x + {b}) cm", "side_label": f"(x + {s}) cm"},
        )
    elif shape == "right_triangle":
        p, q, r = rng.sample(range(0, 11), 3)
        total = (x_val + p) + (x_val + q) + (x_val + r)
        coeff, const = 3, p + q + r
        shape_desc = "right-angled triangle"
        equation_line = f"{_fmt_xk(p)} + {_fmt_xk(q)} + {_fmt_xk(r)} = {total}"
        expand_step = "Collect like terms:"
        dedup_key = f"perim_h:right_triangle:{p}:{q}:{r}:{x_val}"
        diagram = DiagramSpec(
            kind="right_triangle",
            params={
                "leg1_label": f"{_fmt_xk(p)} cm", "leg2_label": f"{_fmt_xk(q)} cm",
                "hyp_label": f"{_fmt_xk(r)} cm",
            },
        )
    else:  # polygon
        n_sides = rng.choice([5, 6, 7, 8])
        k = rng.randint(1, 10)
        total = n_sides * (x_val + k)
        coeff, const = n_sides, n_sides * k
        shape_desc = f"regular {_POLYGON_NAMES[n_sides]}"
        equation_line = f"{n_sides}(x + {k}) = {total}"
        expand_step = f"Expand the bracket ({n_sides} × x and {n_sides} × {k}):"
        dedup_key = f"perim_h:polygon:{n_sides}:{k}:{x_val}"
        diagram = DiagramSpec(
            kind="regular_polygon_side", params={"n_sides": n_sides, "side_label": f"(x + {k}) cm"}
        )

    solve_steps, solution = solve_linear_with_steps(coeff, const, 0, total)
    # Independent verification: substitute the SOLVED value back into each
    # shape's own original (unexpanded) perimeter formula, not the combined
    # coeff/const used to solve it.
    if shape == "l_shape":
        computed = 2 * m + 2 * n + 2 * (solution + k)
    elif shape == "rectangle":
        computed = 2 * (solution + b) + 2 * (solution + e)
    elif shape == "isosceles":
        computed = 2 * (solution + k) + (solution + m)
    elif shape == "parallelogram":
        computed = 2 * (solution + b) + 2 * (solution + s)
    elif shape == "right_triangle":
        computed = (solution + p) + (solution + q) + (solution + r)
    else:
        computed = n_sides * (solution + k)
    if computed != total:
        raise ValueError(f"forming_equations perimeter (higher, {shape}) verification failed")

    return shape, shape_desc, equation_line, expand_step, coeff, const, total, solve_steps, solution, dedup_key, diagram


def _words_higher(rng: random.Random) -> Question:
    a = rng.randint(2, 9)
    b = rng.randint(-15, 15)
    while b == 0:
        b = rng.randint(-15, 15)
    x_val = rng.randint(1, 20)
    c = a * (x_val + b)

    inner = f"x + {b}" if b > 0 else f"x - {-b}"
    add_or_sub = f"add {b}" if b > 0 else f"subtract {-b}"
    equation_line = f"{a}({inner}) = {c}"

    solve_steps, solution = solve_linear_with_steps(a, a * b, 0, c)
    # Independent verification: substitute the solution back into the
    # original bracketed expression a(x + b), not the expanded form used to
    # solve it.
    computed = a * (solution + b)
    if computed != c:
        raise ValueError("forming_equations words (higher) verification failed")

    steps = ["Let the number be x.", equation_line, "Expand the bracket:"] + solve_steps
    return Question(
        topic_id="forming_equations_H",
        tier=Tier.HIGHER,
        prompt=(
            f"I think of a number. I {add_or_sub} to it, then multiply the result by {a}. "
            f"The answer is {c}. Form an equation and solve it to find the number."
        ),
        solution_steps=tuple(steps),
        final_answer=fmt_num(solution),
        dedup_key=f"form_words_h:{a}:{b}:{c}",
    )


def _people_higher(rng: random.Random) -> Question:
    """Three people/quantities: one defined additively relative to the
    first ("N years older/younger than"), one defined MULTIPLICATIVELY
    ("double"/"three times" the first) - genuinely harder than Foundation's
    2-person, additive-only version, per direct user request checked
    against real Corbett Maths examples."""
    name1, name2, name3 = rng.sample(_PEOPLE_NAMES, 3)
    ctx = rng.choice(_TWO_PERSON_CONTEXTS)
    k = rng.randint(1, 20)
    is_more = rng.random() < 0.5
    second_word = ctx["more_word"] if is_more else ctx["less_word"]
    second_const = k if is_more else -k
    m = rng.choice([2, 3, 4])
    mult_word = _MULTIPLE_WORDS[m]

    x_val = rng.randint(max(5, k + 1), 30)
    second_val = x_val + second_const
    third_val = m * x_val
    total = x_val + second_val + third_val
    coeff, const = 2 + m, second_const

    equation_line = f"x + ({fmt_linear(1, second_const)}) + {m}x = {total}"
    collect_line = f"{fmt_linear(coeff, const)} = {total}"
    solve_steps, solution = solve_linear_with_steps(coeff, const, 0, total)
    # Independent verification: substitute the solution back into each
    # person's own original (unexpanded) value, not the combined coeff/const.
    computed = solution + (solution + second_const) + m * solution
    if computed != total:
        raise ValueError("forming_equations people (higher) verification failed")

    steps = [
        f"Let {name1}'s {ctx['item']} be x.",
        equation_line,
        "Collect like terms:",
        collect_line,
    ] + solve_steps[1:]
    prompt = (
        f"{name1} is x {ctx['unit']}.\n"
        f"{name2} is {k} {ctx['diff_unit']} {second_word} than {name1}.\n"
        f"{name3} has {mult_word} {name1}'s {ctx['item']}.\n"
        f"The total of their {ctx['item_plural']} is {total}.\n"
        "Form an equation and solve it to find x."
    )
    return Question(
        topic_id="forming_equations_H",
        tier=Tier.HIGHER,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=fmt_num(solution),
        dedup_key=f"form_people_h:{ctx['unit']}:{k}:{is_more}:{m}:{x_val}",
    )


def _consecutive_higher(rng: random.Random) -> Question:
    """Five consecutive numbers, or three consecutive EVEN numbers - a
    genuinely different/harder variant than Foundation's 3-consecutive-
    numbers version (a longer run, or a non-1 step size), per direct user
    request."""
    kind = rng.choice(["five", "even"])
    if kind == "five":
        n, step, desc = 5, 1, "five consecutive numbers"
    else:
        n, step, desc = 3, 2, "three consecutive even numbers"

    x_val = rng.randint(1, 40)
    if kind == "even" and x_val % 2 != 0:
        x_val += 1

    total = sum(x_val + i * step for i in range(n))
    coeff = n
    const = total - coeff * x_val

    equation_line = " + ".join(_fmt_xk(i * step) for i in range(n)) + f" = {total}"
    collect_line = f"{fmt_linear(coeff, const)} = {total}"
    solve_steps, solution = solve_linear_with_steps(coeff, const, 0, total)
    # Independent verification: substitute the solution back into every
    # original (unexpanded) term, not the combined coeff/const.
    computed = sum(solution + i * step for i in range(n))
    if computed != total:
        raise ValueError("forming_equations consecutive (higher) verification failed")

    steps = [
        "Let the first number be x.",
        equation_line,
        "Collect like terms:",
        collect_line,
    ] + solve_steps[1:]
    values = [solution + i * step for i in range(n)]
    return Question(
        topic_id="forming_equations_H",
        tier=Tier.HIGHER,
        prompt=(
            f"The sum of {desc} is {total}. Form an equation (using x for the first number) "
            "and solve it to find the numbers."
        ),
        solution_steps=tuple(steps),
        final_answer=", ".join(str(v) for v in values),
        dedup_key=f"form_consecutive_h:{kind}:{x_val}",
    )


def _angles_higher(rng: random.Random) -> Question:
    target = 360
    for _ in range(300):
        c1 = rng.randint(1, 4)
        c2 = rng.randint(1, 4)
        x_val = rng.randint(2, 20)
        known = [rng.randint(20, 100) for _ in range(2)]
        d1 = rng.randint(-20, 20)
        combined_const_needed = target - sum(known) - (c1 + c2) * x_val
        d2 = combined_const_needed - d1

        angle1 = c1 * x_val + d1
        angle2 = c2 * x_val + d2
        if (
            5 <= angle1 <= target - 20
            and 5 <= angle2 <= target - 20
            and all(5 <= k <= target - 20 for k in known)
        ):
            break
    else:
        raise ValueError("forming_equations angle (higher) generation failed")

    combined_coeff = c1 + c2
    combined_const = d1 + d2
    target_eq = target - sum(known)
    expr1 = fmt_linear(c1, d1)
    expr2 = fmt_linear(c2, d2)

    solve_steps, solution = solve_linear_with_steps(combined_coeff, combined_const, 0, target_eq)
    # Independent verification: substitute the solution back into both
    # algebraic angle expressions individually and confirm the full
    # quadrilateral genuinely sums to 360 - a different check than the
    # combined single-equation algebra used to solve it.
    check_total = (
        known[0] + known[1] + int((c1 * X + d1).subs(X, solution)) + int((c2 * X + d2).subs(X, solution))
    )
    if check_total != target:
        raise ValueError("forming_equations angle (higher) verification failed")

    equation_line = f"{known[0]} + {known[1]} + ({expr1}) + ({expr2}) = {target}"
    simplified_line = f"{fmt_linear(combined_coeff, combined_const)} = {target_eq}"
    steps = [
        "Angles in a quadrilateral sum to 360°.",
        equation_line,
        "Collect the x-terms and constants together:",
        simplified_line,
    ] + solve_steps[1:]
    return Question(
        topic_id="forming_equations_H",
        tier=Tier.HIGHER,
        prompt=(
            f"A quadrilateral has angles {known[0]}°, {known[1]}°, ({expr1})°, and ({expr2})°. "
            "Form an equation and solve it to find x."
        ),
        solution_steps=tuple(steps),
        final_answer=fmt_num(solution),
        dedup_key=f"form_angle_h:{c1}:{d1}:{c2}:{d2}:{known[0]}:{known[1]}",
        diagram=_angle_fact_diagram(
            "quadrilateral",
            [known[0], known[1], angle1, angle2],
            [f"{known[0]}°", f"{known[1]}°", f"({expr1})°", f"({expr2})°"],
        ),
    )


def _area_higher(rng: random.Random) -> Question:
    shape = rng.choice(["perimeter", "area"])
    if shape == "perimeter":
        _shape, shape_desc, equation_line, expand_step, _coeff, _const, total, solve_steps, solution, dedup_key, diagram = (
            _build_perimeter_higher(rng)
        )
        prompt = f"The perimeter of the {shape_desc} shown is {total} cm. Form an equation and solve it to find x."
        steps = [
            "Perimeter = sum of the side lengths shown.",
            equation_line,
            expand_step,
        ] + solve_steps
    else:
        m = rng.randint(3, 12)
        k = rng.randint(1, 10)
        x_val = rng.randint(2, 20)
        total = m * (x_val + k)

        coeff, const = m, m * k
        solve_steps, solution = solve_linear_with_steps(coeff, const, 0, total)
        # Independent verification: substitute back into the original
        # (unexpanded) area formula m(x + k).
        computed = m * (solution + k)
        if computed != total:
            raise ValueError("forming_equations area (higher, area) verification failed")

        prompt = f"The area of the rectangle shown is {total} cm². Form an equation and solve it to find x."
        equation_line = f"{m}(x + {k}) = {total}"
        steps = ["Area of a rectangle = length × width.", equation_line, "Expand the bracket:"] + solve_steps
        dedup_key = f"form_area_h:area:{m}:{k}:{x_val}"
        diagram = DiagramSpec(
            kind="rectangle",
            params={
                "width": x_val + k, "height": m,
                "width_label": f"(x + {k}) cm", "height_label": f"{m} cm",
            },
        )

    return Question(
        topic_id="forming_equations_H",
        tier=Tier.HIGHER,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=fmt_num(solution),
        dedup_key=dedup_key,
        diagram=diagram,
    )


def generate_forming_equations_higher(tier: Tier, rng: random.Random) -> Question:
    context = rng.choice(["words", "people", "consecutive", "angles", "area"])
    if context == "words":
        q = _words_higher(rng)
    elif context == "people":
        q = _people_higher(rng)
    elif context == "consecutive":
        q = _consecutive_higher(rng)
    elif context == "angles":
        q = _angles_higher(rng)
    else:
        q = _area_higher(rng)
    return dataclasses.replace(q, topic_id="forming_equations_H", tier=Tier.HIGHER)


# ---------------------------------------------------------------------------
# Modelled examples (foundation)
# ---------------------------------------------------------------------------


def _modelled_words_foundation(rng: random.Random) -> ModelledExample:
    a = rng.randint(2, 9)
    b = rng.randint(1, 20)
    x_val = rng.randint(1, 20)
    c = a * x_val + b

    solve_steps, solution = solve_linear_with_steps(a, b, 0, c)
    residual = sp.simplify((a * X + b).subs(X, solution) - c)
    if residual != 0:
        raise ValueError("modelled example forming_equations words (foundation) verification failed")

    teaching_steps = [
        "The phrase 'I think of a number' means we don't know the number yet, so give it a "
        "letter - call it x. Everything the question describes happening to the number "
        "becomes an operation on x.",
        f"'Multiply it by {a} and add {b}' translates directly into the expression "
        f"{fmt_linear(a, b)}. Since we're told the result is {c}, that expression must equal {c}.",
        f"That gives the equation {fmt_linear(a, b)} = {c}, which is solved exactly like any "
        "other linear equation: undo the operations in reverse order (subtract, then divide).",
        f"This gives x = {fmt_num(solution)} - and you can check it's right by putting {fmt_num(solution)} "
        f"back into the original description: {a} × {fmt_num(solution)} + {b} = {c}.",
    ]
    worked_calculation = [
        f"{fmt_linear(a, b)} = {c}",
        f"{fmt_num(a)}x = {c - b}",
        f"x = {fmt_num(solution)}",
    ]
    return ModelledExample(
        topic_id="forming_equations_F",
        tier=Tier.FOUNDATION,
        prompt=(
            f"I think of a number, multiply it by {a} and add {b}. The result is {c}. "
            "Form an equation and solve it to find the number."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=fmt_num(solution),
    )


def _modelled_people_foundation(rng: random.Random) -> ModelledExample:
    name1, name2 = rng.sample(_PEOPLE_NAMES, 2)
    ctx = rng.choice(_TWO_PERSON_CONTEXTS)
    k = rng.randint(1, 20)
    is_more = rng.random() < 0.5
    word = ctx["more_word"] if is_more else ctx["less_word"]
    const = k if is_more else -k
    x_val = rng.randint(max(5, k + 1), 40)
    total = x_val + (x_val + const)

    equation_line = f"x + ({fmt_linear(1, const)}) = {total}"
    collect_line = f"{fmt_linear(2, const)} = {total}"
    solve_steps, solution = solve_linear_with_steps(2, const, 0, total)
    computed = solution + (solution + const)
    if computed != total:
        raise ValueError("modelled example forming_equations people (foundation) verification failed")

    teaching_steps = [
        f"{name1}'s {ctx['item']} is unknown, so give it a letter - call it x. Every other "
        f"person's {ctx['item']} can then be written in terms of x.",
        f"{name2} is {k} {ctx['diff_unit']} {word} than {name1}, so {name2}'s {ctx['item']} is "
        f"{fmt_linear(1, const)}.",
        f"The two {ctx['item_plural']} add up to the given total, so: {equation_line}. Collecting "
        f"like terms gives {collect_line}.",
        f"Solve for x to get x = {fmt_num(solution)}.",
        f"Check by substituting back: {name1}'s {ctx['item']} is {fmt_num(solution)} and "
        f"{name2}'s is {fmt_num(solution + const)}, which together make {total}.",
    ]
    worked_calculation = [equation_line, collect_line, f"x = {fmt_num(solution)}"]
    prompt = (
        f"{name1} is x {ctx['unit']}.\n"
        f"{name2} is {k} {ctx['diff_unit']} {word} than {name1}.\n"
        f"The sum of their {ctx['item_plural']} is {total}.\n"
        "Form an equation and solve it to find x."
    )
    return ModelledExample(
        topic_id="forming_equations_F",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=fmt_num(solution),
    )


def _modelled_consecutive_foundation(rng: random.Random) -> ModelledExample:
    x_val = rng.randint(1, 40)
    total = x_val + (x_val + 1) + (x_val + 2)
    coeff, const = 3, 3

    equation_line = "x + (x + 1) + (x + 2) = " + str(total)
    collect_line = f"{fmt_linear(coeff, const)} = {total}"
    solve_steps, solution = solve_linear_with_steps(coeff, const, 0, total)
    computed = solution + (solution + 1) + (solution + 2)
    if computed != total:
        raise ValueError("modelled example forming_equations consecutive (foundation) verification failed")

    teaching_steps = [
        "Consecutive numbers just mean one after another, each 1 more than the last - so if "
        "the first is x, the next two are x + 1 and x + 2.",
        f"They add up to the given total, so: {equation_line}. Collecting like terms gives "
        f"{collect_line}.",
        f"Solve for x to get x = {fmt_num(solution)}.",
        f"So the three numbers are {solution}, {solution + 1}, and {solution + 2} - check "
        f"they really do add up to {total}.",
    ]
    worked_calculation = [equation_line, collect_line, f"x = {fmt_num(solution)}"]
    return ModelledExample(
        topic_id="forming_equations_F",
        tier=Tier.FOUNDATION,
        prompt=(
            f"The sum of three consecutive numbers is {total}. Form an equation (using x for "
            "the first number) and solve it to find the three numbers."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{solution}, {solution + 1}, {solution + 2}",
    )


def _modelled_angles_foundation(rng: random.Random) -> ModelledExample:
    fact = rng.choice(["straight", "point", "triangle"])
    if fact == "straight":
        target, n_known, fact_text = 180, 1, "angles on a straight line always sum to 180°"
    elif fact == "point":
        target, n_known, fact_text = 360, rng.choice([1, 2]), "angles around a point always sum to 360°"
    else:
        target, n_known, fact_text = 180, 2, "angles in a triangle always sum to 180°"

    for _ in range(300):
        coeff = rng.randint(1, 5)
        x_val = rng.randint(2, 20)
        known = [rng.randint(15, 90) for _ in range(n_known)]
        const = target - coeff * x_val - sum(known)
        algebraic_angle = coeff * x_val + const
        if 5 <= algebraic_angle <= target - 10 and all(5 <= k <= target - 10 for k in known):
            break
    else:
        raise ValueError("modelled example forming_equations angle (foundation) generation failed")

    expr = fmt_linear(coeff, const)
    target_eq = target - sum(known)
    solve_steps, solution = solve_linear_with_steps(coeff, const, 0, target_eq)
    check_total = sum(known) + int((coeff * X + const).subs(X, solution))
    if check_total != target:
        raise ValueError("modelled example forming_equations angle (foundation) verification failed")

    if fact == "straight":
        prompt = (
            f"Two angles on a straight line are {known[0]}° and ({expr})°. "
            "Form an equation and solve it to find x."
        )
    elif fact == "point":
        known_text = " and ".join(f"{k}°" for k in known)
        prompt = (
            f"The angles {known_text} and ({expr})° lie around a point. "
            "Form an equation and solve it to find x."
        )
    else:
        prompt = (
            f"A triangle has angles {known[0]}°, {known[1]}°, and ({expr})°. "
            "Form an equation and solve it to find x."
        )

    sum_parts = [str(k) for k in known] + [f"({expr})"]
    equation_line = " + ".join(sum_parts) + f" = {target}"

    teaching_steps = [
        f"Start from the underlying geometric fact: {fact_text}. That fact is what lets us "
        "write down an equation at all - without it we'd have no relationship connecting the "
        "angles together.",
        f"Add up every angle, including the algebraic one, and set the total equal to {target}: "
        f"{equation_line}.",
        f"Combine the known numbers on the left so only the algebraic part is left needing "
        f"solving: {expr} = {target_eq}.",
        f"Solve that simple equation for x, undoing the multiplication and any constant, to get "
        f"x = {fmt_num(solution)}.",
        "Always check your answer makes sense: substitute x back into every angle expression and "
        f"confirm they genuinely add up to {target}°.",
    ]
    worked_calculation = [equation_line, f"{expr} = {target_eq}", f"x = {fmt_num(solution)}"]
    return ModelledExample(
        topic_id="forming_equations_F",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=fmt_num(solution),
        diagram=_angle_fact_diagram(
            fact, known + [algebraic_angle], [f"{k}°" for k in known] + [f"({expr})°"]
        ),
    )


def _modelled_area_foundation(rng: random.Random) -> ModelledExample:
    shape = rng.choice(["perimeter", "area"])
    if shape == "perimeter":
        m = rng.randint(3, 15)
        k = rng.randint(0, 10)
        x_val = rng.randint(2, 20)
        other_expr = f"x + {k}" if k > 0 else "x"
        other_val = x_val + k
        total = 2 * (other_val + m)

        coeff, const = 2, 2 * k + 2 * m
        solve_steps, solution = solve_linear_with_steps(coeff, const, 0, total)
        computed = 2 * ((solution + k) + m)
        if computed != total:
            raise ValueError("modelled example forming_equations area (foundation, perimeter) verification failed")

        prompt = f"The perimeter of the rectangle shown is {total} cm. Form an equation and solve it to find x."
        equation_line = f"2({other_expr}) + 2({m}) = {total}"
        teaching_steps = [
            "The perimeter of a rectangle is the total distance all the way around it - twice "
            "one side plus twice the other, since opposite sides are equal.",
            f"Write down the perimeter formula using the two given side expressions, and set it "
            f"equal to the perimeter we're told: {equation_line}.",
            "Solve this the same way as any linear equation - divide out the common factor of 2 "
            "first, or expand the brackets, then isolate x.",
            f"This gives x = {fmt_num(solution)}. Check by substituting back into the original "
            f"perimeter formula: 2 × ({fmt_num(solution)} + {k}) + 2 × {m} = {total}.",
        ]
        worked_calculation = [equation_line, f"2x = {total - 2 * k - 2 * m}", f"x = {fmt_num(solution)}"]
        diagram = DiagramSpec(
            kind="rectangle",
            params={
                "width": other_val, "height": m,
                "width_label": f"({other_expr}) cm", "height_label": f"{m} cm",
            },
        )
    else:
        m = rng.randint(3, 12)
        x_val = rng.randint(2, 20)
        total = m * x_val

        coeff, const = m, 0
        solve_steps, solution = solve_linear_with_steps(coeff, const, 0, total)
        computed = m * solution
        if computed != total:
            raise ValueError("modelled example forming_equations area (foundation, area) verification failed")

        prompt = f"The area of the rectangle shown is {total} cm². Form an equation and solve it to find x."
        equation_line = f"{m}x = {total}"
        teaching_steps = [
            "The area of a rectangle is length × width - here one side is a known number and "
            "the other is the unknown x.",
            f"Multiply the two side lengths together and set the result equal to the given area: "
            f"{equation_line}.",
            f"Solve for x by dividing both sides by {m}, giving x = {fmt_num(solution)}.",
            f"Check by substituting back: {m} × {fmt_num(solution)} = {total}, which matches the "
            "area we were given.",
        ]
        worked_calculation = [equation_line, f"x = {total}/{m}", f"x = {fmt_num(solution)}"]
        diagram = DiagramSpec(
            kind="rectangle",
            params={"width": x_val, "height": m, "width_label": "x cm", "height_label": f"{m} cm"},
        )

    return ModelledExample(
        topic_id="forming_equations_F",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=fmt_num(solution),
        diagram=diagram,
    )


def generate_modelled_example_forming_equations_foundation(tier: Tier, rng: random.Random) -> ModelledExample:
    context = rng.choice(["words", "people", "consecutive", "angles", "area"])
    if context == "words":
        example = _modelled_words_foundation(rng)
    elif context == "people":
        example = _modelled_people_foundation(rng)
    elif context == "consecutive":
        example = _modelled_consecutive_foundation(rng)
    elif context == "angles":
        example = _modelled_angles_foundation(rng)
    else:
        example = _modelled_area_foundation(rng)
    return dataclasses.replace(example, topic_id="forming_equations_F", tier=Tier.FOUNDATION)


# ---------------------------------------------------------------------------
# Modelled examples (higher)
# ---------------------------------------------------------------------------


def _modelled_words_higher(rng: random.Random) -> ModelledExample:
    a = rng.randint(2, 9)
    b = rng.randint(-15, 15)
    while b == 0:
        b = rng.randint(-15, 15)
    x_val = rng.randint(1, 20)
    c = a * (x_val + b)

    inner = f"x + {b}" if b > 0 else f"x - {-b}"
    add_or_sub = f"add {b}" if b > 0 else f"subtract {-b}"
    equation_line = f"{a}({inner}) = {c}"

    solve_steps, solution = solve_linear_with_steps(a, a * b, 0, c)
    computed = a * (solution + b)
    if computed != c:
        raise ValueError("modelled example forming_equations words (higher) verification failed")

    teaching_steps = [
        "As before, call the unknown number x. This time the description has two operations "
        "applied in a particular order, and the second one (multiplying) applies to the whole "
        "result of the first, so it needs brackets.",
        f"'{add_or_sub.capitalize()} to it, then multiply the result by {a}' becomes the bracketed "
        f"expression {a}({inner}), which must equal {c}: {equation_line}.",
        f"Expand the bracket first, multiplying {a} by each term inside it, before doing any "
        f"further rearranging - this turns it into an ordinary equation of the form ax + b = c.",
        f"Solving that expanded equation gives x = {fmt_num(solution)}.",
        f"Check by substituting back into the original bracketed form, not the expanded one: "
        f"{a} × ({fmt_num(solution)} {'+' if b > 0 else '-'} {abs(b)}) = {c}.",
    ]
    worked_calculation = [equation_line, f"{fmt_linear(a, a * b)} = {c}", f"x = {fmt_num(solution)}"]
    return ModelledExample(
        topic_id="forming_equations_H",
        tier=Tier.HIGHER,
        prompt=(
            f"I think of a number. I {add_or_sub} to it, then multiply the result by {a}. "
            f"The answer is {c}. Form an equation and solve it to find the number."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=fmt_num(solution),
    )


def _modelled_people_higher(rng: random.Random) -> ModelledExample:
    name1, name2, name3 = rng.sample(_PEOPLE_NAMES, 3)
    ctx = rng.choice(_TWO_PERSON_CONTEXTS)
    k = rng.randint(1, 20)
    is_more = rng.random() < 0.5
    second_word = ctx["more_word"] if is_more else ctx["less_word"]
    second_const = k if is_more else -k
    m = rng.choice([2, 3, 4])
    mult_word = _MULTIPLE_WORDS[m]

    x_val = rng.randint(max(5, k + 1), 30)
    second_val = x_val + second_const
    third_val = m * x_val
    total = x_val + second_val + third_val
    coeff, const = 2 + m, second_const

    equation_line = f"x + ({fmt_linear(1, second_const)}) + {m}x = {total}"
    collect_line = f"{fmt_linear(coeff, const)} = {total}"
    solve_steps, solution = solve_linear_with_steps(coeff, const, 0, total)
    computed = solution + (solution + second_const) + m * solution
    if computed != total:
        raise ValueError("modelled example forming_equations people (higher) verification failed")

    teaching_steps = [
        f"{name1}'s {ctx['item']} is unknown, so call it x. {name2}'s is additive (x plus or "
        f"minus a number) and {name3}'s is multiplicative ({mult_word} x) - both need writing "
        "in terms of x before anything can be added together.",
        f"{name2} is {k} {ctx['diff_unit']} {second_word} than {name1}, so {name2}'s {ctx['item']} "
        f"is {fmt_linear(1, second_const)}. {name3} has {mult_word} {name1}'s {ctx['item']}, "
        f"so {name3}'s is {m}x.",
        f"All three add up to the given total: {equation_line}. Collecting like terms gives "
        f"{collect_line}.",
        f"Solve for x to get x = {fmt_num(solution)}.",
        "Check by substituting back into each person's own expression and confirming they "
        "genuinely add up to the given total.",
    ]
    worked_calculation = [equation_line, collect_line, f"x = {fmt_num(solution)}"]
    prompt = (
        f"{name1} is x {ctx['unit']}.\n"
        f"{name2} is {k} {ctx['diff_unit']} {second_word} than {name1}.\n"
        f"{name3} has {mult_word} {name1}'s {ctx['item']}.\n"
        f"The total of their {ctx['item_plural']} is {total}.\n"
        "Form an equation and solve it to find x."
    )
    return ModelledExample(
        topic_id="forming_equations_H",
        tier=Tier.HIGHER,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=fmt_num(solution),
    )


def _modelled_consecutive_higher(rng: random.Random) -> ModelledExample:
    kind = rng.choice(["five", "even"])
    if kind == "five":
        n, step, desc = 5, 1, "five consecutive numbers"
    else:
        n, step, desc = 3, 2, "three consecutive even numbers"

    x_val = rng.randint(1, 40)
    if kind == "even" and x_val % 2 != 0:
        x_val += 1

    total = sum(x_val + i * step for i in range(n))
    coeff = n
    const = total - coeff * x_val

    equation_line = " + ".join(_fmt_xk(i * step) for i in range(n)) + f" = {total}"
    collect_line = f"{fmt_linear(coeff, const)} = {total}"
    solve_steps, solution = solve_linear_with_steps(coeff, const, 0, total)
    computed = sum(solution + i * step for i in range(n))
    if computed != total:
        raise ValueError("modelled example forming_equations consecutive (higher) verification failed")

    values = [solution + i * step for i in range(n)]
    step_desc = "1 more than the last" if step == 1 else f"{step} more than the last"
    teaching_steps = [
        f"Consecutive{' even' if kind == 'even' else ''} numbers each go up by {step} from "
        f"the last, so if the first is x, the rest are x + {step}, x + {2 * step}, and so on "
        f"({step_desc}).",
        f"They all add up to the given total, so: {equation_line}. Collecting like terms "
        f"gives {collect_line}.",
        f"Solve for x to get x = {fmt_num(solution)}.",
        f"So the numbers are {', '.join(str(v) for v in values)} - check they really do add "
        f"up to {total}.",
    ]
    worked_calculation = [equation_line, collect_line, f"x = {fmt_num(solution)}"]
    return ModelledExample(
        topic_id="forming_equations_H",
        tier=Tier.HIGHER,
        prompt=(
            f"The sum of {desc} is {total}. Form an equation (using x for the first number) "
            "and solve it to find the numbers."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=", ".join(str(v) for v in values),
    )


def _modelled_angles_higher(rng: random.Random) -> ModelledExample:
    target = 360
    for _ in range(300):
        c1 = rng.randint(1, 4)
        c2 = rng.randint(1, 4)
        x_val = rng.randint(2, 20)
        known = [rng.randint(20, 100) for _ in range(2)]
        d1 = rng.randint(-20, 20)
        combined_const_needed = target - sum(known) - (c1 + c2) * x_val
        d2 = combined_const_needed - d1

        angle1 = c1 * x_val + d1
        angle2 = c2 * x_val + d2
        if (
            5 <= angle1 <= target - 20
            and 5 <= angle2 <= target - 20
            and all(5 <= k <= target - 20 for k in known)
        ):
            break
    else:
        raise ValueError("modelled example forming_equations angle (higher) generation failed")

    combined_coeff = c1 + c2
    combined_const = d1 + d2
    target_eq = target - sum(known)
    expr1 = fmt_linear(c1, d1)
    expr2 = fmt_linear(c2, d2)

    solve_steps, solution = solve_linear_with_steps(combined_coeff, combined_const, 0, target_eq)
    check_total = (
        known[0] + known[1] + int((c1 * X + d1).subs(X, solution)) + int((c2 * X + d2).subs(X, solution))
    )
    if check_total != target:
        raise ValueError("modelled example forming_equations angle (higher) verification failed")

    equation_line = f"{known[0]} + {known[1]} + ({expr1}) + ({expr2}) = {target}"
    simplified_line = f"{fmt_linear(combined_coeff, combined_const)} = {target_eq}"

    teaching_steps = [
        "A quadrilateral's four interior angles always sum to 360° - the same underlying idea "
        "as a triangle summing to 180°, just with one more side and one more angle.",
        f"This time two of the four angles are algebraic expressions rather than just one, so "
        f"adding everything together gives two separate x-terms: {equation_line}.",
        f"Collect the x-terms together ({c1}x + {c2}x = {combined_coeff}x) and the constants "
        f"together, to simplify down to a single equation: {simplified_line}.",
        f"Solve that equation for x in the usual way to get x = {fmt_num(solution)}.",
        "It's worth checking this properly: substitute x back into both algebraic angle "
        f"expressions separately, then add all four angles together and confirm the total is "
        f"genuinely {target}°.",
    ]
    worked_calculation = [equation_line, simplified_line, f"x = {fmt_num(solution)}"]
    return ModelledExample(
        topic_id="forming_equations_H",
        tier=Tier.HIGHER,
        prompt=(
            f"A quadrilateral has angles {known[0]}°, {known[1]}°, ({expr1})°, and ({expr2})°. "
            "Form an equation and solve it to find x."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=fmt_num(solution),
        diagram=_angle_fact_diagram(
            "quadrilateral",
            [known[0], known[1], angle1, angle2],
            [f"{known[0]}°", f"{known[1]}°", f"({expr1})°", f"({expr2})°"],
        ),
    )


def _modelled_area_higher(rng: random.Random) -> ModelledExample:
    shape = rng.choice(["perimeter", "area"])
    if shape == "perimeter":
        _shape, shape_desc, equation_line, expand_step, coeff, const, total, _solve_steps, solution, _dedup_key, diagram = (
            _build_perimeter_higher(rng)
        )
        prompt = f"The perimeter of the {shape_desc} shown is {total} cm. Form an equation and solve it to find x."
        expanded_line = f"{fmt_linear(coeff, const)} = {total}"
        teaching_steps = [
            f"A {shape_desc}'s perimeter is just the sum of its side lengths - here some of "
            "those sides are algebraic expressions instead of plain numbers, but the idea is "
            "exactly the same.",
            f"Write down that perimeter sum and set it equal to the total we're given: "
            f"{equation_line}.",
            f"{expand_step} {expanded_line}.",
            f"Solve for x to get x = {fmt_num(solution)}.",
            "Check by substituting back into the original, unexpanded formula for each side.",
        ]
        worked_calculation = [equation_line, expanded_line, f"x = {fmt_num(solution)}"]
    else:
        m = rng.randint(3, 12)
        k = rng.randint(1, 10)
        x_val = rng.randint(2, 20)
        total = m * (x_val + k)

        coeff, const = m, m * k
        solve_steps, solution = solve_linear_with_steps(coeff, const, 0, total)
        computed = m * (solution + k)
        if computed != total:
            raise ValueError("modelled example forming_equations area (higher, area) verification failed")

        prompt = f"The area of the rectangle shown is {total} cm². Form an equation and solve it to find x."
        equation_line = f"{m}(x + {k}) = {total}"
        expanded_line = f"{fmt_linear(coeff, const)} = {total}"
        teaching_steps = [
            "Area is length × width, exactly as before - but now one of the sides is itself a "
            "bracketed expression, so multiplying it by the other side needs expanding.",
            f"Write the area formula and set it equal to the total area: {equation_line}.",
            f"Expand the bracket ({m} × x and {m} × {k}) to get an ordinary linear equation: "
            f"{expanded_line}.",
            f"Solve for x, giving x = {fmt_num(solution)}.",
            f"Check by substituting back into the original bracketed formula: "
            f"{m} × ({fmt_num(solution)} + {k}) = {total}.",
        ]
        worked_calculation = [equation_line, expanded_line, f"x = {fmt_num(solution)}"]
        diagram = DiagramSpec(
            kind="rectangle",
            params={
                "width": x_val + k, "height": m,
                "width_label": f"(x + {k}) cm", "height_label": f"{m} cm",
            },
        )

    return ModelledExample(
        topic_id="forming_equations_H",
        tier=Tier.HIGHER,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=fmt_num(solution),
        diagram=diagram,
    )


def generate_modelled_example_forming_equations_higher(tier: Tier, rng: random.Random) -> ModelledExample:
    context = rng.choice(["words", "people", "consecutive", "angles", "area"])
    if context == "words":
        example = _modelled_words_higher(rng)
    elif context == "people":
        example = _modelled_people_higher(rng)
    elif context == "consecutive":
        example = _modelled_consecutive_higher(rng)
    elif context == "angles":
        example = _modelled_angles_higher(rng)
    else:
        example = _modelled_area_higher(rng)
    return dataclasses.replace(example, topic_id="forming_equations_H", tier=Tier.HIGHER)


TOPIC_FORMING_EQUATIONS_FOUNDATION = TopicDefinition(
    id="forming_equations_F",
    display_name="Forming and Solving Equations",
    description=(
        "Translate a word problem, angle fact, or area/perimeter fact into a linear equation "
        "and solve it (one/two-step equations)."
    ),
    generate=generate_forming_equations_foundation,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_forming_equations_foundation,
)

TOPIC_FORMING_EQUATIONS_HIGHER = TopicDefinition(
    id="forming_equations_H",
    display_name="Forming and Solving Equations (Higher)",
    description=(
        "Translate a word problem, angle fact, or area/perimeter fact into a linear equation "
        "requiring brackets or collecting terms, and solve it."
    ),
    generate=generate_forming_equations_higher,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_forming_equations_higher,
)
