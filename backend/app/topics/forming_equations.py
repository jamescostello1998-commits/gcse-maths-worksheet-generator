import dataclasses
import random

import sympy as sp

from app.core.models import ModelledExample, Question, Tier
from app.topics.algebra_utils import X, fmt_linear, fmt_num, solve_linear_with_steps
from app.topics.base import TopicDefinition

SECTION = "algebra"
GROUP = "Forming and Solving Equations"


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
        topic_id="forming_equations_foundation",
        tier=Tier.FOUNDATION,
        prompt=(
            f"I think of a number, multiply it by {a} and add {b}. The result is {c}. "
            "Form an equation and solve it to find the number."
        ),
        solution_steps=tuple(steps),
        final_answer=fmt_num(solution),
        dedup_key=f"form_words:{a}:{b}:{c}",
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
        topic_id="forming_equations_foundation",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=fmt_num(solution),
        dedup_key=f"form_angle:{fact}:{coeff}:{const}:{'-'.join(map(str, known))}",
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

        prompt = (
            f"A rectangle has one side of length {m} cm and the other side of length "
            f"({other_expr}) cm. The perimeter of the rectangle is {total} cm. "
            "Form an equation and solve it to find x."
        )
        equation_line = f"2({other_expr}) + 2({m}) = {total}"
        steps = ["Perimeter = 2 × (sum of two different side lengths)."] + [equation_line] + solve_steps
        dedup_key = f"form_area:perimeter:{m}:{k}:{x_val}"
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

        prompt = (
            f"A rectangle has one side of length {m} cm and the other side of length x cm. "
            f"The area of the rectangle is {total} cm². Form an equation and solve it to find x."
        )
        equation_line = f"{m}x = {total}"
        steps = ["Area of a rectangle = length × width."] + [equation_line] + solve_steps
        dedup_key = f"form_area:area:{m}:{x_val}"

    return Question(
        topic_id="forming_equations_foundation",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=fmt_num(solution),
        dedup_key=dedup_key,
    )


def generate_forming_equations_foundation(tier: Tier, rng: random.Random) -> Question:
    context = rng.choice(["words", "angles", "area"])
    if context == "words":
        q = _words_foundation(rng)
    elif context == "angles":
        q = _angles_foundation(rng)
    else:
        q = _area_foundation(rng)
    return dataclasses.replace(q, topic_id="forming_equations_foundation", tier=Tier.FOUNDATION)


# ---------------------------------------------------------------------------
# Higher: brackets, x-terms to collect, harder geometric contexts.
# ---------------------------------------------------------------------------


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
        topic_id="forming_equations_higher",
        tier=Tier.HIGHER,
        prompt=(
            f"I think of a number. I {add_or_sub} to it, then multiply the result by {a}. "
            f"The answer is {c}. Form an equation and solve it to find the number."
        ),
        solution_steps=tuple(steps),
        final_answer=fmt_num(solution),
        dedup_key=f"form_words_h:{a}:{b}:{c}",
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
        topic_id="forming_equations_higher",
        tier=Tier.HIGHER,
        prompt=(
            f"A quadrilateral has angles {known[0]}°, {known[1]}°, ({expr1})°, and ({expr2})°. "
            "Form an equation and solve it to find x."
        ),
        solution_steps=tuple(steps),
        final_answer=fmt_num(solution),
        dedup_key=f"form_angle_h:{c1}:{d1}:{c2}:{d2}:{known[0]}:{known[1]}",
    )


def _area_higher(rng: random.Random) -> Question:
    shape = rng.choice(["perimeter", "area"])
    if shape == "perimeter":
        m = rng.randint(3, 15)
        n = rng.randint(3, 15)
        k = rng.randint(1, 10)
        x_val = rng.randint(2, 20)
        total = 2 * m + 2 * n + 2 * (x_val + k)

        coeff, const = 2, 2 * m + 2 * n + 2 * k
        solve_steps, solution = solve_linear_with_steps(coeff, const, 0, total)
        # Independent verification: substitute back into the original
        # (unexpanded) composite perimeter formula.
        computed = 2 * m + 2 * n + 2 * (solution + k)
        if computed != total:
            raise ValueError("forming_equations area (higher, perimeter) verification failed")

        prompt = (
            f"A composite shape's perimeter is made up of two sides of length {m} cm, "
            f"two sides of length {n} cm, and two sides of length (x + {k}) cm. "
            f"The total perimeter is {total} cm. Form an equation and solve it to find x."
        )
        equation_line = f"2({m}) + 2({n}) + 2(x + {k}) = {total}"
        steps = [
            "Perimeter = sum of all side lengths.",
            equation_line,
            "Expand the bracket and collect the constants:",
        ] + solve_steps
        dedup_key = f"form_area_h:perimeter:{m}:{n}:{k}:{x_val}"
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

        prompt = (
            f"A rectangle has one side of length {m} cm and the other side of length "
            f"(x + {k}) cm. The area of the rectangle is {total} cm². "
            "Form an equation and solve it to find x."
        )
        equation_line = f"{m}(x + {k}) = {total}"
        steps = ["Area of a rectangle = length × width.", equation_line, "Expand the bracket:"] + solve_steps
        dedup_key = f"form_area_h:area:{m}:{k}:{x_val}"

    return Question(
        topic_id="forming_equations_higher",
        tier=Tier.HIGHER,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=fmt_num(solution),
        dedup_key=dedup_key,
    )


def generate_forming_equations_higher(tier: Tier, rng: random.Random) -> Question:
    context = rng.choice(["words", "angles", "area"])
    if context == "words":
        q = _words_higher(rng)
    elif context == "angles":
        q = _angles_higher(rng)
    else:
        q = _area_higher(rng)
    return dataclasses.replace(q, topic_id="forming_equations_higher", tier=Tier.HIGHER)


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
        topic_id="forming_equations_foundation",
        tier=Tier.FOUNDATION,
        prompt=(
            f"I think of a number, multiply it by {a} and add {b}. The result is {c}. "
            "Form an equation and solve it to find the number."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=fmt_num(solution),
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
        topic_id="forming_equations_foundation",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=fmt_num(solution),
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

        prompt = (
            f"A rectangle has one side of length {m} cm and the other side of length "
            f"({other_expr}) cm. The perimeter of the rectangle is {total} cm. "
            "Form an equation and solve it to find x."
        )
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
    else:
        m = rng.randint(3, 12)
        x_val = rng.randint(2, 20)
        total = m * x_val

        coeff, const = m, 0
        solve_steps, solution = solve_linear_with_steps(coeff, const, 0, total)
        computed = m * solution
        if computed != total:
            raise ValueError("modelled example forming_equations area (foundation, area) verification failed")

        prompt = (
            f"A rectangle has one side of length {m} cm and the other side of length x cm. "
            f"The area of the rectangle is {total} cm². Form an equation and solve it to find x."
        )
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

    return ModelledExample(
        topic_id="forming_equations_foundation",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=fmt_num(solution),
    )


def generate_modelled_example_forming_equations_foundation(tier: Tier, rng: random.Random) -> ModelledExample:
    context = rng.choice(["words", "angles", "area"])
    if context == "words":
        example = _modelled_words_foundation(rng)
    elif context == "angles":
        example = _modelled_angles_foundation(rng)
    else:
        example = _modelled_area_foundation(rng)
    return dataclasses.replace(example, topic_id="forming_equations_foundation", tier=Tier.FOUNDATION)


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
        topic_id="forming_equations_higher",
        tier=Tier.HIGHER,
        prompt=(
            f"I think of a number. I {add_or_sub} to it, then multiply the result by {a}. "
            f"The answer is {c}. Form an equation and solve it to find the number."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=fmt_num(solution),
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
        topic_id="forming_equations_higher",
        tier=Tier.HIGHER,
        prompt=(
            f"A quadrilateral has angles {known[0]}°, {known[1]}°, ({expr1})°, and ({expr2})°. "
            "Form an equation and solve it to find x."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=fmt_num(solution),
    )


def _modelled_area_higher(rng: random.Random) -> ModelledExample:
    shape = rng.choice(["perimeter", "area"])
    if shape == "perimeter":
        m = rng.randint(3, 15)
        n = rng.randint(3, 15)
        k = rng.randint(1, 10)
        x_val = rng.randint(2, 20)
        total = 2 * m + 2 * n + 2 * (x_val + k)

        coeff, const = 2, 2 * m + 2 * n + 2 * k
        solve_steps, solution = solve_linear_with_steps(coeff, const, 0, total)
        computed = 2 * m + 2 * n + 2 * (solution + k)
        if computed != total:
            raise ValueError("modelled example forming_equations area (higher, perimeter) verification failed")

        prompt = (
            f"A composite shape's perimeter is made up of two sides of length {m} cm, "
            f"two sides of length {n} cm, and two sides of length (x + {k}) cm. "
            f"The total perimeter is {total} cm. Form an equation and solve it to find x."
        )
        equation_line = f"2({m}) + 2({n}) + 2(x + {k}) = {total}"
        expanded_line = f"{fmt_linear(coeff, const)} = {total}"
        teaching_steps = [
            "A composite shape's perimeter is still just the sum of every side length around "
            "the outside - here that's three pairs of sides, one pair given as a bracketed "
            "expression.",
            f"Write down the full perimeter sum and set it equal to the total we're given: "
            f"{equation_line}.",
            f"Expand the bracket (2 × x and 2 × {k}) and collect all the plain-number terms "
            f"together, leaving a simple equation: {expanded_line}.",
            f"Solve for x to get x = {fmt_num(solution)}.",
            f"Check by substituting back into the original, unexpanded formula: "
            f"2×{m} + 2×{n} + 2×({fmt_num(solution)} + {k}) = {total}.",
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

        prompt = (
            f"A rectangle has one side of length {m} cm and the other side of length "
            f"(x + {k}) cm. The area of the rectangle is {total} cm². "
            "Form an equation and solve it to find x."
        )
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

    return ModelledExample(
        topic_id="forming_equations_higher",
        tier=Tier.HIGHER,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=fmt_num(solution),
    )


def generate_modelled_example_forming_equations_higher(tier: Tier, rng: random.Random) -> ModelledExample:
    context = rng.choice(["words", "angles", "area"])
    if context == "words":
        example = _modelled_words_higher(rng)
    elif context == "angles":
        example = _modelled_angles_higher(rng)
    else:
        example = _modelled_area_higher(rng)
    return dataclasses.replace(example, topic_id="forming_equations_higher", tier=Tier.HIGHER)


TOPIC_FORMING_EQUATIONS_FOUNDATION = TopicDefinition(
    id="forming_equations_foundation",
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
    id="forming_equations_higher",
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
