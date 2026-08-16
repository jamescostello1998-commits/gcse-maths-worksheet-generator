import random

import sympy as sp

from app.core.models import DiagramSpec, ModelledExample, Question, Tier
from app.topics.algebra_utils import X, fmt_linear, solve_linear_with_steps
from app.topics.base import TopicDefinition

SECTION = "geometry"
GROUP = "Angles"

# How often the Higher straight-line/around-a-point/triangle angle topics
# use MULTIPLE algebraic terms (e.g. "(2x+25)deg and (x-10)deg on a straight
# line", or a triangle with all 3 angles algebraic) instead of the original
# always-exactly-one-algebraic-term form - real GCSE papers mix both, per
# direct user request (confirmed against real Corbett Maths examples).
_MULTI_ALGEBRAIC_CHANCE = 0.4


def _build_multi_algebraic_angles(rng: random.Random, n_algebraic: int, n_known: int, target: int, known_range=(15, 90)):
    """Shared by the Higher straight-line/around-a-point/triangle "multiple
    algebraic terms" branches: picks n_known plain numeric angles and
    n_algebraic (coeff, const) expressions that all sum exactly to `target`.
    Coefficients are small positive integers (2-5), matching this file's
    existing single-algebraic-term convention. Returns (known, terms, x_val,
    combined_coeff, combined_const) where combined_coeff/combined_const
    describe the SUM of the algebraic terms only (not the known ones)."""
    for _ in range(300):
        known = [rng.randint(*known_range) for _ in range(n_known)]
        x_val = rng.randint(2, 20)
        coeffs = [rng.randint(2, 5) for _ in range(n_algebraic)]
        combined_coeff = sum(coeffs)
        remaining = target - sum(known)
        consts = [rng.randint(-15, 15) for _ in range(n_algebraic - 1)]
        last_const = remaining - combined_coeff * x_val - sum(consts)
        consts.append(last_const)
        terms = list(zip(coeffs, consts))
        values = [c * x_val + k for c, k in terms]
        min_val = 5
        max_val = remaining - min_val * (n_algebraic - 1)
        if all(min_val <= v <= max_val for v in values) and all(min_val <= k <= target - min_val for k in known):
            return known, terms, x_val, combined_coeff, sum(consts)
    raise ValueError("could not build multi-algebraic angle terms")


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
        topic_id="angles_straight_line_F",
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


def generate_modelled_example_straight_line(tier: Tier, rng: random.Random) -> ModelledExample:
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
        raise ValueError("modelled example straight_line generation produced an invalid missing angle")

    given_str = ", ".join(f"{a}°" for a in given)
    teaching_steps = [
        "Whenever a set of angles sit together on a single straight line, they always add up "
        "to exactly 180° - this is one of the basic angle facts, because a straight line is "
        "itself a 180° angle.",
        f"Here we're given {n - 1} of the angles: {given_str}. Add those together first: "
        f"{' + '.join(str(a) for a in given)} = {sum(given)}.",
        f"Since the whole straight line totals 180°, whatever is left over must be the missing "
        f"angle: x = 180 - {sum(given)} = {missing}.",
        f"Check it makes sense: {given_str} and {missing}° together give "
        f"{sum(given) + missing}°, which is 180° as required.",
    ]
    worked_calculation = [
        f"{' + '.join(str(a) for a in given)} + x = 180",
        f"{sum(given)} + x = 180",
        f"x = 180 - {sum(given)} = {missing}",
    ]
    return ModelledExample(
        topic_id="angles_straight_line_F",
        tier=Tier.FOUNDATION,
        prompt=f"The angles {given_str} and x° lie on a straight line. Find x.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=str(missing),
        diagram=DiagramSpec(
            kind="angle_line",
            params={
                "angle_values": given + [missing],
                "labels": [f"{a}°" for a in given] + ["x"],
                "around_point": False,
            },
        ),
    )


def generate_straight_line_higher(tier: Tier, rng: random.Random) -> Question:
    if rng.random() < _MULTI_ALGEBRAIC_CHANCE:
        _known, terms, _x_val, combined_coeff, combined_const = _build_multi_algebraic_angles(
            rng, n_algebraic=2, n_known=0, target=180
        )
        exprs = [fmt_linear(c, k) for c, k in terms]
        solve_steps, solution = solve_linear_with_steps(combined_coeff, combined_const, 0, 180)
        check_total = sum(int((c * X + k).subs(X, solution)) for c, k in terms)
        if check_total != 180:
            raise ValueError("straight_line_higher (multi) verification failed")

        equation_line = f"({exprs[0]}) + ({exprs[1]}) = 180"
        simplified_line = f"{fmt_linear(combined_coeff, combined_const)} = 180"
        steps = [
            "Angles on a straight line sum to 180°.",
            equation_line,
            "Collect like terms:",
            simplified_line,
        ] + solve_steps[1:]
        values = [c * _x_val + k for c, k in terms]
        return Question(
            topic_id="angles_straight_line_H",
            tier=Tier.HIGHER,
            prompt=f"The angles ({exprs[0]})° and ({exprs[1]})° lie on a straight line. Find x.",
            solution_steps=tuple(steps),
            final_answer=str(solution),
            dedup_key=f"straight_line_h_multi:{terms}",
            diagram=DiagramSpec(
                kind="angle_line",
                params={
                    "angle_values": values,
                    "labels": [f"({e})°" for e in exprs],
                    "around_point": False,
                },
            ),
        )

    known = rng.randint(20, 150)
    coeff = rng.choice([2, 3, 4, 5])
    x_sol = rng.randint(1, 20)
    target = 180 - known
    const = target - coeff * x_sol

    solve_steps, solution = solve_linear_with_steps(coeff, const, 0, target)
    residual = sp.simplify((coeff * X + const).subs(X, solution) - target)
    if residual != 0:
        raise ValueError("straight_line_higher verification failed")

    steps = ["Angles on a straight line sum to 180°."] + solve_steps
    return Question(
        topic_id="angles_straight_line_H",
        tier=Tier.HIGHER,
        prompt=f"The angles {known}° and ({fmt_linear(coeff, const)})° lie on a straight line. Find x.",
        solution_steps=tuple(steps),
        final_answer=str(solution),
        dedup_key=f"straight_line_h:{known}:{coeff}:{const}",
        diagram=DiagramSpec(
            kind="angle_line",
            params={
                "angle_values": [known, target],
                "labels": [f"{known}°", f"({fmt_linear(coeff, const)})°"],
                "around_point": False,
            },
        ),
    )


def generate_modelled_example_straight_line_higher(tier: Tier, rng: random.Random) -> ModelledExample:
    if rng.random() < _MULTI_ALGEBRAIC_CHANCE:
        _known, terms, _x_val, combined_coeff, combined_const = _build_multi_algebraic_angles(
            rng, n_algebraic=2, n_known=0, target=180
        )
        exprs = [fmt_linear(c, k) for c, k in terms]
        solve_steps, solution = solve_linear_with_steps(combined_coeff, combined_const, 0, 180)
        check_total = sum(int((c * X + k).subs(X, solution)) for c, k in terms)
        if check_total != 180:
            raise ValueError("modelled example straight_line_higher (multi) verification failed")

        equation_line = f"({exprs[0]}) + ({exprs[1]}) = 180"
        simplified_line = f"{fmt_linear(combined_coeff, combined_const)} = 180"
        teaching_steps = [
            "Angles on a straight line always add up to 180° - this still holds even when "
            "MULTIPLE of the angles are written as algebraic expressions instead of plain numbers.",
            f"Add the two expressions together and set the total equal to 180°: {equation_line}.",
            f"Collect the x-terms and constants together so only one term needs solving: "
            f"{simplified_line}.",
            f"Solve that equation for x the usual way, to get x = {solution}.",
            "Check your answer makes sense: substitute x back into both expressions and confirm "
            "they genuinely add up to 180°.",
        ]
        values = [c * _x_val + k for c, k in terms]
        worked_calculation = [equation_line, simplified_line, f"x = {solution}"]
        return ModelledExample(
            topic_id="angles_straight_line_H",
            tier=Tier.HIGHER,
            prompt=f"The angles ({exprs[0]})° and ({exprs[1]})° lie on a straight line. Find x.",
            worked_calculation=tuple(worked_calculation),
            teaching_steps=tuple(teaching_steps),
            final_answer=str(solution),
            diagram=DiagramSpec(
                kind="angle_line",
                params={
                    "angle_values": values,
                    "labels": [f"({e})°" for e in exprs],
                    "around_point": False,
                },
            ),
        )

    known = rng.randint(20, 150)
    coeff = rng.choice([2, 3, 4, 5])
    x_sol = rng.randint(1, 20)
    target = 180 - known
    const = target - coeff * x_sol

    solve_steps, solution = solve_linear_with_steps(coeff, const, 0, target)
    residual = sp.simplify((coeff * X + const).subs(X, solution) - target)
    if residual != 0:
        raise ValueError("modelled example straight_line_higher verification failed")

    teaching_steps = [
        "Angles on a straight line always add up to 180° - this still holds even when one of "
        "the angles is written as an algebraic expression instead of a plain number.",
        f"Here the two angles are {known}° and ({fmt_linear(coeff, const)})°, and together they "
        f"must total 180°, so we can set up an equation: {known} + {fmt_linear(coeff, const)} = 180, "
        f"which simplifies to {fmt_linear(coeff, const + known)} = 180.",
        f"Rearrange and solve for x the usual way, subtracting {const + known} then dividing by "
        f"{coeff}, to get x = {solution}.",
        f"Check: substituting x = {solution} back in gives ({fmt_linear(coeff, const)}) = {target}, "
        f"and {known} + {target} = 180 as required.",
    ]
    worked_calculation = [
        f"{known} + {fmt_linear(coeff, const)} = 180",
        f"{fmt_linear(coeff, const)} = {target}",
        f"x = {solution}",
    ]
    return ModelledExample(
        topic_id="angles_straight_line_H",
        tier=Tier.HIGHER,
        prompt=f"The angles {known}° and ({fmt_linear(coeff, const)})° lie on a straight line. Find x.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=str(solution),
        diagram=DiagramSpec(
            kind="angle_line",
            params={
                "angle_values": [known, target],
                "labels": [f"{known}°", f"({fmt_linear(coeff, const)})°"],
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
        topic_id="angles_around_point_F",
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


def generate_modelled_example_around_point(tier: Tier, rng: random.Random) -> ModelledExample:
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
        raise ValueError("modelled example around_point generation produced an invalid missing angle")

    given_str = ", ".join(f"{a}°" for a in given)
    teaching_steps = [
        "Angles that meet at a single point and go all the way around it always add up to "
        "360° - a full turn - because going all the way round a point is one complete rotation.",
        f"We're given {n - 1} of the angles: {given_str}. Add these together: "
        f"{' + '.join(str(a) for a in given)} = {sum(given)}.",
        f"The full set of angles must total 360°, so subtract the sum of the known angles from "
        f"360 to find the missing one: x = 360 - {sum(given)} = {missing}.",
        f"As a check, all the angles together give {sum(given) + missing}°, which is a full "
        "turn as expected.",
    ]
    worked_calculation = [
        f"{' + '.join(str(a) for a in given)} + x = 360",
        f"{sum(given)} + x = 360",
        f"x = 360 - {sum(given)} = {missing}",
    ]
    return ModelledExample(
        topic_id="angles_around_point_F",
        tier=Tier.FOUNDATION,
        prompt=f"The angles {given_str} and x° are angles around a point. Find x.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=str(missing),
        diagram=DiagramSpec(
            kind="angle_line",
            params={
                "angle_values": given + [missing],
                "labels": [f"{a}°" for a in given] + ["x"],
                "around_point": True,
            },
        ),
    )


def generate_around_point_higher(tier: Tier, rng: random.Random) -> Question:
    if rng.random() < _MULTI_ALGEBRAIC_CHANCE:
        n = rng.choice([3, 4])
        known, terms, _x_val, combined_coeff, combined_const = _build_multi_algebraic_angles(
            rng, n_algebraic=2, n_known=n - 2, target=360
        )
        exprs = [fmt_linear(c, k) for c, k in terms]
        target_eq = 360 - sum(known)
        solve_steps, solution = solve_linear_with_steps(combined_coeff, combined_const, 0, target_eq)
        check_total = sum(known) + sum(int((c * X + k).subs(X, solution)) for c, k in terms)
        if check_total != 360:
            raise ValueError("around_point_higher (multi) verification failed")

        known_str = ", ".join(f"{a}°" for a in known)
        expr_str = " and ".join(f"({e})°" for e in exprs)
        parts_str = (known_str + ", " if known_str else "") + expr_str
        equation_line = (
            (" + ".join(str(a) for a in known) + " + " if known else "")
            + " + ".join(f"({e})" for e in exprs)
            + " = 360"
        )
        simplified_line = f"{fmt_linear(combined_coeff, combined_const)} = {target_eq}"
        steps = [
            "Angles around a point sum to 360°.",
            equation_line,
            "Collect like terms:",
            simplified_line,
        ] + solve_steps[1:]
        values = known + [c * _x_val + k for c, k in terms]
        return Question(
            topic_id="angles_around_point_H",
            tier=Tier.HIGHER,
            prompt=f"The angles {parts_str} are angles around a point. Find x.",
            solution_steps=tuple(steps),
            final_answer=str(solution),
            dedup_key=f"around_point_h_multi:{known}:{terms}",
            diagram=DiagramSpec(
                kind="angle_line",
                params={
                    "angle_values": values,
                    "labels": [f"{a}°" for a in known] + [f"({e})°" for e in exprs],
                    "around_point": True,
                },
            ),
        )

    n = rng.choice([3, 4])
    given: list[int] = []
    remaining = 360
    for i in range(n - 1):
        max_for_this = remaining - 10 * (n - 1 - i)
        angle = rng.randint(10, max(10, min(150, max_for_this)))
        given.append(angle)
        remaining -= angle
    target = 360 - sum(given)
    if target < 10:
        raise ValueError("around_point_higher generation produced an invalid target angle")

    coeff = rng.choice([2, 3, 4, 5])
    x_sol = rng.randint(1, 20)
    const = target - coeff * x_sol

    solve_steps, solution = solve_linear_with_steps(coeff, const, 0, target)
    residual = sp.simplify((coeff * X + const).subs(X, solution) - target)
    if residual != 0:
        raise ValueError("around_point_higher verification failed")

    given_str = ", ".join(f"{a}°" for a in given)
    steps = ["Angles around a point sum to 360°."] + solve_steps
    return Question(
        topic_id="angles_around_point_H",
        tier=Tier.HIGHER,
        prompt=(
            f"The angles {given_str} and ({fmt_linear(coeff, const)})° are angles around a "
            "point. Find x."
        ),
        solution_steps=tuple(steps),
        final_answer=str(solution),
        dedup_key=f"around_point_h:{given}:{coeff}:{const}",
        diagram=DiagramSpec(
            kind="angle_line",
            params={
                "angle_values": given + [target],
                "labels": [f"{a}°" for a in given] + [f"({fmt_linear(coeff, const)})°"],
                "around_point": True,
            },
        ),
    )


def generate_modelled_example_around_point_higher(tier: Tier, rng: random.Random) -> ModelledExample:
    if rng.random() < _MULTI_ALGEBRAIC_CHANCE:
        n = rng.choice([3, 4])
        known, terms, _x_val, combined_coeff, combined_const = _build_multi_algebraic_angles(
            rng, n_algebraic=2, n_known=n - 2, target=360
        )
        exprs = [fmt_linear(c, k) for c, k in terms]
        target_eq = 360 - sum(known)
        solve_steps, solution = solve_linear_with_steps(combined_coeff, combined_const, 0, target_eq)
        check_total = sum(known) + sum(int((c * X + k).subs(X, solution)) for c, k in terms)
        if check_total != 360:
            raise ValueError("modelled example around_point_higher (multi) verification failed")

        known_str = ", ".join(f"{a}°" for a in known)
        expr_str = " and ".join(f"({e})°" for e in exprs)
        parts_str = (known_str + ", " if known_str else "") + expr_str
        equation_line = (
            (" + ".join(str(a) for a in known) + " + " if known else "")
            + " + ".join(f"({e})" for e in exprs)
            + " = 360"
        )
        simplified_line = f"{fmt_linear(combined_coeff, combined_const)} = {target_eq}"
        teaching_steps = [
            "Angles that meet at a single point and go all the way around it always add up to "
            "360° - a full turn - and that's still true even when MULTIPLE of the angles are "
            "written algebraically instead of as plain numbers.",
            f"Add every angle together and set the total equal to 360°: {equation_line}.",
            f"Collect the x-terms and constants together: {simplified_line}.",
            f"Solve that equation for x the usual way, to get x = {solution}.",
        ]
        values = known + [c * _x_val + k for c, k in terms]
        worked_calculation = [equation_line, simplified_line, f"x = {solution}"]
        return ModelledExample(
            topic_id="angles_around_point_H",
            tier=Tier.HIGHER,
            prompt=f"The angles {parts_str} are angles around a point. Find x.",
            worked_calculation=tuple(worked_calculation),
            teaching_steps=tuple(teaching_steps),
            final_answer=str(solution),
            diagram=DiagramSpec(
                kind="angle_line",
                params={
                    "angle_values": values,
                    "labels": [f"{a}°" for a in known] + [f"({e})°" for e in exprs],
                    "around_point": True,
                },
            ),
        )

    n = rng.choice([3, 4])
    given: list[int] = []
    remaining = 360
    for i in range(n - 1):
        max_for_this = remaining - 10 * (n - 1 - i)
        angle = rng.randint(10, max(10, min(150, max_for_this)))
        given.append(angle)
        remaining -= angle
    target = 360 - sum(given)
    if target < 10:
        raise ValueError("modelled example around_point_higher generation produced an invalid target angle")

    coeff = rng.choice([2, 3, 4, 5])
    x_sol = rng.randint(1, 20)
    const = target - coeff * x_sol

    solve_steps, solution = solve_linear_with_steps(coeff, const, 0, target)
    residual = sp.simplify((coeff * X + const).subs(X, solution) - target)
    if residual != 0:
        raise ValueError("modelled example around_point_higher verification failed")

    given_str = ", ".join(f"{a}°" for a in given)
    teaching_steps = [
        "Angles that meet at a single point and go all the way around it always add up to 360° "
        "- a full turn - and that's still true even when one of the angles is written "
        "algebraically instead of as a plain number.",
        f"Add up the {n - 1} known angles: {' + '.join(str(a) for a in given)} = {sum(given)}.",
        f"Since everything must total 360°, the algebraic angle must be worth "
        f"360 - {sum(given)} = {target}: ({fmt_linear(coeff, const)}) = {target}.",
        f"Solve that equation for x the usual way, isolating x on one side, to get x = {solution}.",
    ]
    worked_calculation = [
        f"{' + '.join(str(a) for a in given)} + ({fmt_linear(coeff, const)}) = 360",
        f"{fmt_linear(coeff, const)} = {target}",
        f"x = {solution}",
    ]
    return ModelledExample(
        topic_id="angles_around_point_H",
        tier=Tier.HIGHER,
        prompt=(
            f"The angles {given_str} and ({fmt_linear(coeff, const)})° are angles around a "
            "point. Find x."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=str(solution),
        diagram=DiagramSpec(
            kind="angle_line",
            params={
                "angle_values": given + [target],
                "labels": [f"{a}°" for a in given] + [f"({fmt_linear(coeff, const)})°"],
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
        topic_id="angles_triangle_F",
        tier=Tier.FOUNDATION,
        prompt=f"A triangle has angles {a}°, {b}°, and x°. Find x.",
        solution_steps=tuple(steps),
        final_answer=str(missing),
        dedup_key=f"triangle_angles:{a}:{b}",
        diagram=DiagramSpec(kind="triangle_angles", params={"angle_labels": [f"{a}°", f"{b}°", "x"]}),
    )


def generate_modelled_example_triangle_angles(tier: Tier, rng: random.Random) -> ModelledExample:
    a = rng.randint(20, 120)
    b = rng.randint(20, min(120, 160 - a))
    missing = 180 - a - b
    if missing < 10:
        raise ValueError("modelled example triangle_angles generation produced an invalid missing angle")

    teaching_steps = [
        "Every triangle's three interior angles always add up to 180° - this is a fixed geometric "
        "fact that's true for every triangle, no matter its shape or size.",
        f"Here we're told two of the three angles: {a}° and {b}°. Add them together first: "
        f"{a} + {b} = {a + b}°.",
        f"Since all three angles must total 180°, the missing angle is whatever is left over: "
        f"x = 180 - {a + b} = {missing}°.",
        f"Check by adding all three together: {a} + {b} + {missing} = {a + b + missing}°, "
        "which is 180° as expected.",
    ]
    worked_calculation = [
        f"{a} + {b} + x = 180",
        f"{a + b} + x = 180",
        f"x = 180 - {a + b}",
        f"x = {missing}",
    ]
    return ModelledExample(
        topic_id="angles_triangle_F",
        tier=Tier.FOUNDATION,
        prompt=f"A triangle has angles {a}°, {b}°, and x°. Find x.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=str(missing),
        diagram=DiagramSpec(kind="triangle_angles", params={"angle_labels": [f"{a}°", f"{b}°", "x"]}),
    )


def generate_triangle_angles_higher(tier: Tier, rng: random.Random) -> Question:
    if rng.random() < _MULTI_ALGEBRAIC_CHANCE:
        _known, terms, _x_val, combined_coeff, combined_const = _build_multi_algebraic_angles(
            rng, n_algebraic=3, n_known=0, target=180
        )
        exprs = [fmt_linear(c, k) for c, k in terms]
        solve_steps, solution = solve_linear_with_steps(combined_coeff, combined_const, 0, 180)
        check_total = sum(int((c * X + k).subs(X, solution)) for c, k in terms)
        if check_total != 180:
            raise ValueError("triangle_angles_higher (multi) verification failed")

        equation_line = " + ".join(f"({e})" for e in exprs) + " = 180"
        simplified_line = f"{fmt_linear(combined_coeff, combined_const)} = 180"
        steps = [
            "Angles in a triangle sum to 180°.",
            equation_line,
            "Collect like terms:",
            simplified_line,
        ] + solve_steps[1:]
        return Question(
            topic_id="angles_triangle_H",
            tier=Tier.HIGHER,
            prompt=f"A triangle has angles ({exprs[0]})°, ({exprs[1]})°, and ({exprs[2]})°. Find x.",
            solution_steps=tuple(steps),
            final_answer=str(solution),
            dedup_key=f"triangle_angles_h_multi:{terms}",
            diagram=DiagramSpec(
                kind="triangle_angles", params={"angle_labels": [f"({e})°" for e in exprs]}
            ),
        )

    a = rng.randint(20, 100)
    b = rng.randint(20, min(100, 160 - a))
    target = 180 - a - b
    if target < 10:
        raise ValueError("triangle_angles_higher generated an invalid target angle")

    coeff = rng.choice([2, 3, 4, 5])
    x_sol = rng.randint(1, 20)
    const = target - coeff * x_sol

    solve_steps, solution = solve_linear_with_steps(coeff, const, 0, target)
    residual = sp.simplify((coeff * X + const).subs(X, solution) - target)
    if residual != 0:
        raise ValueError("triangle_angles_higher verification failed")

    steps = ["Angles in a triangle sum to 180°."] + solve_steps
    return Question(
        topic_id="angles_triangle_H",
        tier=Tier.HIGHER,
        prompt=f"A triangle has angles {a}°, {b}°, and ({fmt_linear(coeff, const)})°. Find x.",
        solution_steps=tuple(steps),
        final_answer=str(solution),
        dedup_key=f"triangle_angles_h:{a}:{b}:{coeff}:{const}",
        diagram=DiagramSpec(
            kind="triangle_angles",
            params={"angle_labels": [f"{a}°", f"{b}°", f"({fmt_linear(coeff, const)})°"]},
        ),
    )


def generate_modelled_example_triangle_angles_higher(tier: Tier, rng: random.Random) -> ModelledExample:
    if rng.random() < _MULTI_ALGEBRAIC_CHANCE:
        _known, terms, _x_val, combined_coeff, combined_const = _build_multi_algebraic_angles(
            rng, n_algebraic=3, n_known=0, target=180
        )
        exprs = [fmt_linear(c, k) for c, k in terms]
        solve_steps, solution = solve_linear_with_steps(combined_coeff, combined_const, 0, 180)
        check_total = sum(int((c * X + k).subs(X, solution)) for c, k in terms)
        if check_total != 180:
            raise ValueError("modelled example triangle_angles_higher (multi) verification failed")

        equation_line = " + ".join(f"({e})" for e in exprs) + " = 180"
        simplified_line = f"{fmt_linear(combined_coeff, combined_const)} = 180"
        teaching_steps = [
            "Every triangle's three interior angles always add up to 180° - this still holds "
            "even when ALL THREE angles are written as algebraic expressions instead of plain "
            "numbers.",
            f"Add all three expressions together and set the total equal to 180°: {equation_line}.",
            f"Collect the x-terms and constants together so only one term needs solving: "
            f"{simplified_line}.",
            f"Solve that equation for x the usual way, to get x = {solution}.",
            "Check your answer makes sense: substitute x back into every expression and confirm "
            "they genuinely add up to 180°.",
        ]
        worked_calculation = [equation_line, simplified_line, f"x = {solution}"]
        return ModelledExample(
            topic_id="angles_triangle_H",
            tier=Tier.HIGHER,
            prompt=f"A triangle has angles ({exprs[0]})°, ({exprs[1]})°, and ({exprs[2]})°. Find x.",
            worked_calculation=tuple(worked_calculation),
            teaching_steps=tuple(teaching_steps),
            final_answer=str(solution),
            diagram=DiagramSpec(
                kind="triangle_angles", params={"angle_labels": [f"({e})°" for e in exprs]}
            ),
        )

    a = rng.randint(20, 100)
    b = rng.randint(20, min(100, 160 - a))
    target = 180 - a - b
    if target < 10:
        raise ValueError("modelled example triangle_angles_higher generated an invalid target angle")

    coeff = rng.choice([2, 3, 4, 5])
    x_sol = rng.randint(1, 20)
    const = target - coeff * x_sol

    solve_steps, solution = solve_linear_with_steps(coeff, const, 0, target)
    residual = sp.simplify((coeff * X + const).subs(X, solution) - target)
    if residual != 0:
        raise ValueError("modelled example triangle_angles_higher verification failed")

    teaching_steps = [
        "Every triangle's three interior angles always add up to 180° - and that still applies "
        "even when one of the angles is given as an algebraic expression rather than a number.",
        f"Add the two known angles together: {a} + {b} = {a + b}°.",
        f"Since all three angles must total 180°, the algebraic angle must be worth "
        f"180 - {a + b} = {target}: ({fmt_linear(coeff, const)}) = {target}.",
        f"Solve that equation for x the usual way, isolating x on one side, to get x = {solution}.",
    ]
    worked_calculation = [
        f"{a} + {b} + ({fmt_linear(coeff, const)}) = 180",
        f"{fmt_linear(coeff, const)} = {target}",
        f"x = {solution}",
    ]
    return ModelledExample(
        topic_id="angles_triangle_H",
        tier=Tier.HIGHER,
        prompt=f"A triangle has angles {a}°, {b}°, and ({fmt_linear(coeff, const)})°. Find x.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=str(solution),
        diagram=DiagramSpec(
            kind="triangle_angles",
            params={"angle_labels": [f"{a}°", f"{b}°", f"({fmt_linear(coeff, const)})°"]},
        ),
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
        topic_id="angles_parallel_lines_H",
        tier=Tier.HIGHER,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=str(solution),
        dedup_key=f"parallel_lines:{fact}:{known}:{coeff}:{const}",
        diagram=DiagramSpec(
            kind="parallel_lines",
            params={
                "known_label": f"{known}°",
                "unknown_label": f"({fmt_linear(coeff, const)})°",
                "relation": fact,
                "known_value": known,
                "x_frac": rng.choice([0.32, 0.38, 0.44]),
            },
        ),
    )


def generate_modelled_example_parallel_lines(tier: Tier, rng: random.Random) -> ModelledExample:
    fact = rng.choice(["corresponding", "alternate", "co_interior"])
    known = rng.randint(30, 150)
    target = known if fact in ("corresponding", "alternate") else 180 - known
    coeff = rng.choice([2, 3, 4, 5])
    x_sol = rng.randint(1, 20)
    const = target - coeff * x_sol

    fact_text = {
        "corresponding": "Corresponding angles are equal - they sit in the same position at "
        "each intersection, like two Fs stacked on top of each other.",
        "alternate": "Alternate angles are equal - they sit on opposite sides of the crossing "
        "line, between the two parallel lines, forming a Z shape.",
        "co_interior": "Co-interior angles sum to 180° - they sit on the same side of the "
        "crossing line, between the two parallel lines, forming a C or U shape.",
    }[fact]
    relation = {
        "corresponding": "are corresponding angles",
        "alternate": "are alternate angles",
        "co_interior": "are co-interior angles",
    }[fact]

    solve_steps, solution = solve_linear_with_steps(coeff, const, 0, target)
    residual = sp.simplify((coeff * X + const).subs(X, solution) - target)
    if residual != 0:
        raise ValueError("modelled example parallel_lines verification failed")

    teaching_steps = [
        "When a line crosses a pair of parallel lines, it creates several pairs of equal or "
        "related angles - which pair applies here depends on the two angles' positions "
        "relative to the parallel lines and the crossing line.",
        fact_text,
        f"That means {known}° and ({fmt_linear(coeff, const)})° {relation}, so we can set up an "
        f"equation: {fmt_linear(coeff, const)} = {target}.",
        f"Solve that equation for x the usual way, isolating x on one side, to get x = {solution}.",
    ]
    worked_calculation = [
        f"{fmt_linear(coeff, const)} = {target}",
        f"{fmt_linear(coeff, 0)} = {target - const}",
        f"x = {solution}",
    ]
    prompt = (
        f"A line crosses two parallel lines. The angle {known}° and the angle "
        f"({fmt_linear(coeff, const)})° {relation}. Find x."
    )
    return ModelledExample(
        topic_id="angles_parallel_lines_H",
        tier=Tier.HIGHER,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=str(solution),
        diagram=DiagramSpec(
            kind="parallel_lines",
            params={
                "known_label": f"{known}°",
                "unknown_label": f"({fmt_linear(coeff, const)})°",
                "relation": fact,
                "known_value": known,
                "x_frac": rng.choice([0.32, 0.38, 0.44]),
            },
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
        topic_id="angles_exterior_H",
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
                "interior1_value": known_interior,
                "shape_variant": rng.choice([0, 1]),
            },
        ),
    )


def generate_modelled_example_exterior_angle(tier: Tier, rng: random.Random) -> ModelledExample:
    known_interior = rng.randint(20, 70)
    coeff = rng.choice([2, 3, 4, 5])
    x_sol = rng.randint(1, 20)
    other_interior_value = rng.randint(10, 70)
    const = other_interior_value - coeff * x_sol
    exterior = known_interior + other_interior_value
    if exterior >= 180:
        raise ValueError("modelled example exterior_angle generated a non-physical exterior angle")

    solve_steps, solution = solve_linear_with_steps(coeff, const, 0, exterior - known_interior)
    residual = sp.simplify((coeff * X + const).subs(X, solution) - other_interior_value)
    if residual != 0:
        raise ValueError("modelled example exterior_angle verification failed")

    teaching_steps = [
        "If you extend one side of a triangle beyond a vertex, the angle formed outside the "
        "triangle is called an exterior angle - and there's a useful shortcut for finding it: "
        "it always equals the sum of the two interior angles that are NOT next to it (the "
        "'remote' interior angles).",
        f"Here the exterior angle is {exterior}° and one of the remote interior angles is "
        f"{known_interior}°, so the other remote interior angle, ({fmt_linear(coeff, const)})°, "
        f"must make up the rest: {exterior} - {known_interior} = {exterior - known_interior}.",
        f"Set up the equation ({fmt_linear(coeff, const)}) = {exterior - known_interior} and "
        "solve it the usual way to isolate x.",
        f"That gives x = {solution}.",
    ]
    worked_calculation = [
        f"{fmt_linear(coeff, const)} = {exterior - known_interior}",
        f"{fmt_linear(coeff, 0)} = {exterior - known_interior - const}",
        f"x = {solution}",
    ]
    prompt = (
        f"An exterior angle of a triangle is {exterior}°. The two remote interior angles are "
        f"{known_interior}° and ({fmt_linear(coeff, const)})°. Find x."
    )
    return ModelledExample(
        topic_id="angles_exterior_H",
        tier=Tier.HIGHER,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=str(solution),
        diagram=DiagramSpec(
            kind="exterior_triangle",
            params={
                "interior1_label": f"{known_interior}°",
                "interior2_label": f"({fmt_linear(coeff, const)})°",
                "exterior_label": f"{exterior}°",
                "interior1_value": known_interior,
                "shape_variant": rng.choice([0, 1]),
            },
        ),
    )


def generate_parallel_lines_foundation(tier: Tier, rng: random.Random) -> Question:
    fact = rng.choice(["corresponding", "alternate", "co_interior"])
    known = rng.randint(30, 150)
    target = known if fact in ("corresponding", "alternate") else 180 - known

    # Independent check: the target angle must be a valid angle (a sanity
    # bound distinct from the direct lookup used to compute it above).
    if not (0 < target < 180):
        raise ValueError("parallel_lines_foundation verification failed: angle out of range")

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

    steps = [fact_text, f"x = {target}"]
    return Question(
        topic_id="angles_parallel_lines_F",
        tier=Tier.FOUNDATION,
        prompt=f"A line crosses two parallel lines. The angle {known}° and the angle x° {relation}. Find x.",
        solution_steps=tuple(steps),
        final_answer=str(target),
        dedup_key=f"parallel_lines_f:{fact}:{known}",
        diagram=DiagramSpec(
            kind="parallel_lines",
            params={
                "known_label": f"{known}°", "unknown_label": "x", "relation": fact,
                "known_value": known, "x_frac": rng.choice([0.32, 0.38, 0.44]),
            },
        ),
    )


def generate_modelled_example_parallel_lines_foundation(tier: Tier, rng: random.Random) -> ModelledExample:
    fact = rng.choice(["corresponding", "alternate", "co_interior"])
    known = rng.randint(30, 150)
    target = known if fact in ("corresponding", "alternate") else 180 - known

    # Independent check: the target angle must be a valid angle (a sanity
    # bound distinct from the direct lookup used to compute it above).
    if not (0 < target < 180):
        raise ValueError("modelled example parallel_lines_foundation verification failed: angle out of range")

    fact_text = {
        "corresponding": "Corresponding angles are equal - they sit in the same position at "
        "each intersection, like two Fs stacked on top of each other.",
        "alternate": "Alternate angles are equal - they sit on opposite sides of the crossing "
        "line, between the two parallel lines, forming a Z shape.",
        "co_interior": "Co-interior angles sum to 180° - they sit on the same side of the "
        "crossing line, between the two parallel lines, forming a C or U shape.",
    }[fact]
    relation = {
        "corresponding": "are corresponding angles",
        "alternate": "are alternate angles",
        "co_interior": "are co-interior angles",
    }[fact]

    if fact == "co_interior":
        final_step = f"Since the two angles sum to 180°, x = 180 - {known} = {target}."
        worked_calculation = [f"x + {known} = 180", f"x = {target}"]
    else:
        final_step = f"Since the two angles are equal, x = {target}."
        worked_calculation = [f"x = {known}", f"x = {target}"]

    teaching_steps = [
        "When a line crosses a pair of parallel lines, it creates several pairs of related "
        "angles - spotting which pair you have tells you exactly how the two angles are linked.",
        fact_text,
        f"Here x° and {known}° {relation}, so we can use that fact directly without any "
        "algebra.",
        final_step,
    ]
    return ModelledExample(
        topic_id="angles_parallel_lines_F",
        tier=Tier.FOUNDATION,
        prompt=f"A line crosses two parallel lines. The angle {known}° and the angle x° {relation}. Find x.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=str(target),
        diagram=DiagramSpec(
            kind="parallel_lines",
            params={
                "known_label": f"{known}°", "unknown_label": "x", "relation": fact,
                "known_value": known, "x_frac": rng.choice([0.32, 0.38, 0.44]),
            },
        ),
    )


def generate_exterior_foundation(tier: Tier, rng: random.Random) -> Question:
    a = rng.randint(20, 70)
    b = rng.randint(20, 70)
    exterior = a + b
    if exterior >= 180:
        raise ValueError("exterior_foundation generated a non-physical exterior angle")

    # Independent check: the exterior angle also equals 180 minus the third
    # (remote) interior angle of the triangle - a different derivation than
    # the direct sum-of-remote-angles theorem used above.
    third_interior = 180 - a - b
    if third_interior <= 0:
        raise ValueError("exterior_foundation verification failed: non-physical triangle")
    if 180 - third_interior != exterior:
        raise ValueError("exterior_foundation verification failed")

    steps = [
        "The exterior angle of a triangle equals the sum of the two remote interior angles.",
        f"x = {a} + {b} = {exterior}",
    ]
    return Question(
        topic_id="angles_exterior_F",
        tier=Tier.FOUNDATION,
        prompt=f"An exterior angle of a triangle is x°. The two remote interior angles are {a}° and {b}°. Find x.",
        solution_steps=tuple(steps),
        final_answer=str(exterior),
        dedup_key=f"exterior_f:{a}:{b}",
        diagram=DiagramSpec(
            kind="exterior_triangle",
            params={
                "interior1_label": f"{a}°", "interior2_label": f"{b}°", "exterior_label": "x",
                "interior1_value": a, "shape_variant": rng.choice([0, 1]),
            },
        ),
    )


def generate_modelled_example_exterior_foundation(tier: Tier, rng: random.Random) -> ModelledExample:
    a = rng.randint(20, 70)
    b = rng.randint(20, 70)
    exterior = a + b
    if exterior >= 180:
        raise ValueError("modelled example exterior_foundation generated a non-physical exterior angle")

    # Independent check: the exterior angle also equals 180 minus the third
    # (remote) interior angle of the triangle - a different derivation than
    # the direct sum-of-remote-angles theorem used above.
    third_interior = 180 - a - b
    if third_interior <= 0:
        raise ValueError("modelled example exterior_foundation verification failed: non-physical triangle")
    if 180 - third_interior != exterior:
        raise ValueError("modelled example exterior_foundation verification failed")

    teaching_steps = [
        "If you extend one side of a triangle beyond a vertex, the angle formed outside is "
        "called an exterior angle. There's a handy rule: it always equals the sum of the two "
        "interior angles that aren't next to it (the 'remote' interior angles).",
        f"Here the two remote interior angles are {a}° and {b}°, so add them together: "
        f"{a} + {b} = {exterior}.",
        f"That sum, {exterior}°, is exactly the exterior angle x - no rearranging needed, "
        "just apply the rule directly.",
        f"As a check: the third interior angle of the triangle is 180 - {a} - {b} = "
        f"{third_interior}°, and 180 - {third_interior} = {exterior} too, confirming the answer.",
    ]
    worked_calculation = [
        f"x = {a} + {b}",
        f"x = {exterior}",
    ]
    return ModelledExample(
        topic_id="angles_exterior_F",
        tier=Tier.FOUNDATION,
        prompt=f"An exterior angle of a triangle is x°. The two remote interior angles are {a}° and {b}°. Find x.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=str(exterior),
        diagram=DiagramSpec(
            kind="exterior_triangle",
            params={
                "interior1_label": f"{a}°", "interior2_label": f"{b}°", "exterior_label": "x",
                "interior1_value": a, "shape_variant": rng.choice([0, 1]),
            },
        ),
    )


_REGULAR_POLYGON_SIDES = [n for n in range(3, 91) if 360 % n == 0]


def generate_polygon_interior_foundation(tier: Tier, rng: random.Random) -> Question:
    n = rng.choice(_REGULAR_POLYGON_SIDES)
    measure = rng.choice(["interior_sum", "interior_angle", "exterior_angle"])
    total = (n - 2) * 180

    # Independent check: the interior angle via total ÷ n must match 180
    # minus the exterior angle (360 ÷ n) - a different derivation (the
    # exterior-angle-sum method) than the direct division used above.
    if total % n != 0 or 360 % n != 0:
        raise ValueError("polygon_interior_foundation verification failed: n does not divide evenly")
    interior = total // n
    exterior = 360 // n
    if 180 - exterior != interior:
        raise ValueError("polygon_interior_foundation verification failed")

    diagram = None
    if measure == "interior_sum":
        prompt = f"A polygon has {n} sides. Find the sum of its interior angles."
        steps = [f"Sum of interior angles = (n - 2) × 180 = ({n} - 2) × 180 = {total}°"]
        answer = f"{total}°"
    elif measure == "interior_angle":
        prompt = f"A regular polygon has {n} sides. Find the size of one interior angle."
        steps = [
            f"Sum of interior angles = (n - 2) × 180 = ({n} - 2) × 180 = {total}°",
            f"This is a regular polygon, so each interior angle = {total} ÷ {n} = {interior}°",
        ]
        answer = f"{interior}°"
        diagram = DiagramSpec(kind="polygon", params={"n_sides": min(n, 12), "marked_angle_label": "?"})
    else:
        prompt = f"A regular polygon has {n} sides. Find the size of one exterior angle."
        steps = [f"Exterior angles of a regular polygon sum to 360°: each exterior angle = 360 ÷ {n} = {exterior}°"]
        answer = f"{exterior}°"
        diagram = DiagramSpec(
            kind="polygon", params={"n_sides": min(n, 12), "marked_angle_label": "?", "mode": "exterior"}
        )

    return Question(
        topic_id="angles_polygon_interior_F",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"polygon_interior_f:{n}:{measure}",
        diagram=diagram,
    )


def generate_modelled_example_polygon_interior_foundation(tier: Tier, rng: random.Random) -> ModelledExample:
    n = rng.choice(_REGULAR_POLYGON_SIDES)
    measure = rng.choice(["interior_sum", "interior_angle", "exterior_angle"])
    total = (n - 2) * 180

    # Independent check: the interior angle via total ÷ n must match 180
    # minus the exterior angle (360 ÷ n) - a different derivation (the
    # exterior-angle-sum method) than the direct division used above.
    if total % n != 0 or 360 % n != 0:
        raise ValueError("modelled example polygon_interior_foundation verification failed: n does not divide evenly")
    interior = total // n
    exterior = 360 // n
    if 180 - exterior != interior:
        raise ValueError("modelled example polygon_interior_foundation verification failed")

    diagram = None
    if measure == "interior_sum":
        prompt = f"A polygon has {n} sides. Find the sum of its interior angles."
        teaching_steps = [
            "Any polygon can be split into triangles by drawing diagonals from one vertex - and "
            "since every triangle's angles sum to 180°, counting those triangles tells us the "
            f"total for the whole polygon.",
            f"A polygon with n sides can always be split into (n - 2) triangles. Here n = {n}, "
            f"so that's {n} - 2 = {n - 2} triangles.",
            f"Each triangle contributes 180°, so multiply: {n - 2} × 180 = {total}.",
            f"So the interior angles of this {n}-sided polygon sum to {total}°.",
        ]
        worked_calculation = [
            f"Sum = (n - 2) × 180",
            f"= ({n} - 2) × 180",
            f"= {total}°",
        ]
        answer = f"{total}°"
    elif measure == "interior_angle":
        prompt = f"A regular polygon has {n} sides. Find the size of one interior angle."
        teaching_steps = [
            "First find the total of all the interior angles, then - because this polygon is "
            "regular, meaning every angle is identical - share that total equally between the "
            "sides.",
            f"Sum of interior angles = (n - 2) × 180 = ({n} - 2) × 180 = {total}°.",
            f"Since all {n} interior angles are equal, divide the total by {n}: "
            f"{total} ÷ {n} = {interior}.",
            f"So each interior angle of this regular {n}-sided polygon is {interior}°.",
        ]
        worked_calculation = [
            f"Sum = ({n} - 2) × 180 = {total}°",
            f"One angle = {total} ÷ {n}",
            f"= {interior}°",
        ]
        answer = f"{interior}°"
        diagram = DiagramSpec(kind="polygon", params={"n_sides": min(n, 12), "marked_angle_label": "?"})
    else:
        prompt = f"A regular polygon has {n} sides. Find the size of one exterior angle."
        teaching_steps = [
            "The exterior angles of any polygon - the angles you'd turn through walking around "
            "the outside - always add up to exactly 360°, a full turn, no matter how many sides "
            "the polygon has.",
            f"Since this polygon is regular, all {n} exterior angles are equal, so share the "
            f"360° equally between them.",
            f"Divide: 360 ÷ {n} = {exterior}.",
            f"So each exterior angle of this regular {n}-sided polygon is {exterior}°.",
        ]
        worked_calculation = [
            f"One exterior angle = 360 ÷ {n}",
            f"= {exterior}°",
        ]
        answer = f"{exterior}°"
        diagram = DiagramSpec(
            kind="polygon", params={"n_sides": min(n, 12), "marked_angle_label": "?", "mode": "exterior"}
        )

    return ModelledExample(
        topic_id="angles_polygon_interior_F",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
        diagram=diagram,
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
        topic_id="angles_polygon_interior_H",
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


def generate_modelled_example_polygon_interior(tier: Tier, rng: random.Random) -> ModelledExample:
    for _ in range(200):
        n = rng.randint(5, 8)
        total = (n - 2) * 180
        other_angle_value = rng.randint(100, 150)
        remaining_total = other_angle_value * (n - 1)
        algebraic_value = total - remaining_total
        if 20 <= algebraic_value <= 170:
            break
    else:
        raise ValueError("modelled example polygon_interior could not find valid parameters")

    coeff = rng.choice([2, 3, 4, 5])
    x_sol = rng.randint(1, 20)
    const = algebraic_value - coeff * x_sol

    solve_steps, solution = solve_linear_with_steps(coeff, const, 0, algebraic_value)
    total_check = other_angle_value * (n - 1) + int((coeff * X + const).subs(X, solution))
    if total_check != total:
        raise ValueError("modelled example polygon_interior verification failed")

    teaching_steps = [
        "For any polygon, the interior angles always add up to (n - 2) × 180°, where n is the "
        f"number of sides. Here n = {n}, so the total is ({n} - 2) × 180 = {total}°.",
        f"We're told {n - 1} of the angles are each {other_angle_value}°, so together they "
        f"account for {n - 1} × {other_angle_value} = {remaining_total}° of that total.",
        f"Whatever is left over must belong to the final angle: {total} - {remaining_total} = "
        f"{algebraic_value}°, so ({fmt_linear(coeff, const)})° = {algebraic_value}°.",
        f"Solve that equation for x the usual way to get x = {solution}.",
    ]
    worked_calculation = [
        f"({fmt_linear(coeff, const)}) = {total} - {remaining_total} = {algebraic_value}",
        f"{fmt_linear(coeff, 0)} = {algebraic_value - const}",
        f"x = {solution}",
    ]
    prompt = (
        f"A polygon has {n} sides. {n - 1} of its interior angles are each {other_angle_value}°, "
        f"and the remaining interior angle is ({fmt_linear(coeff, const)})°. Find x."
    )
    return ModelledExample(
        topic_id="angles_polygon_interior_H",
        tier=Tier.HIGHER,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=str(solution),
        diagram=DiagramSpec(
            kind="polygon",
            params={"n_sides": n, "marked_angle_label": f"({fmt_linear(coeff, const)})°"},
        ),
    )


TOPIC_STRAIGHT_LINE = TopicDefinition(
    id="angles_straight_line_F",
    display_name="On a Straight Line",
    description="Find a missing angle on a straight line (angles sum to 180°).",
    generate=generate_straight_line,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_straight_line,
)

TOPIC_STRAIGHT_LINE_HIGHER = TopicDefinition(
    id="angles_straight_line_H",
    display_name="On a Straight Line (Algebraic)",
    description="Form and solve a linear equation from angles on a straight line.",
    generate=generate_straight_line_higher,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_straight_line_higher,
)

TOPIC_AROUND_POINT = TopicDefinition(
    id="angles_around_point_F",
    display_name="Around a Point",
    description="Find a missing angle around a point (angles sum to 360°).",
    generate=generate_around_point,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_around_point,
)

TOPIC_AROUND_POINT_HIGHER = TopicDefinition(
    id="angles_around_point_H",
    display_name="Around a Point (Algebraic)",
    description="Form and solve a linear equation from angles around a point.",
    generate=generate_around_point_higher,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_around_point_higher,
)

TOPIC_TRIANGLE = TopicDefinition(
    id="angles_triangle_F",
    display_name="In a Triangle",
    description="Find a missing angle in a triangle (angles sum to 180°).",
    generate=generate_triangle_angles,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_triangle_angles,
)

TOPIC_TRIANGLE_HIGHER = TopicDefinition(
    id="angles_triangle_H",
    display_name="In a Triangle (Algebraic)",
    description="Form and solve a linear equation from the angles in a triangle.",
    generate=generate_triangle_angles_higher,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_triangle_angles_higher,
)

TOPIC_PARALLEL_LINES_FOUNDATION = TopicDefinition(
    id="angles_parallel_lines_F",
    display_name="Parallel Lines (Foundation)",
    description="Use corresponding, alternate, and co-interior angle facts to find a missing angle directly.",
    generate=generate_parallel_lines_foundation,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_parallel_lines_foundation,
)

TOPIC_PARALLEL_LINES = TopicDefinition(
    id="angles_parallel_lines_H",
    display_name="Parallel Lines",
    description="Use corresponding, alternate, and co-interior angle facts to solve for x.",
    generate=generate_parallel_lines,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_parallel_lines,
)

TOPIC_EXTERIOR_FOUNDATION = TopicDefinition(
    id="angles_exterior_F",
    display_name="Exterior Angle (Foundation)",
    description="Use the exterior angle theorem to find a missing angle directly.",
    generate=generate_exterior_foundation,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_exterior_foundation,
)

TOPIC_EXTERIOR = TopicDefinition(
    id="angles_exterior_H",
    display_name="Exterior Angle",
    description="Use the exterior angle theorem to solve for x.",
    generate=generate_exterior_angle,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_exterior_angle,
)

TOPIC_POLYGON_INTERIOR_FOUNDATION = TopicDefinition(
    id="angles_polygon_interior_F",
    display_name="Polygon Angles (Foundation)",
    description="Find the sum of interior angles, one interior angle, or one exterior angle of a regular polygon.",
    generate=generate_polygon_interior_foundation,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_polygon_interior_foundation,
)

TOPIC_POLYGON_INTERIOR = TopicDefinition(
    id="angles_polygon_interior_H",
    display_name="Polygon Interior Angles",
    description="Use the polygon interior angle sum formula to solve for x.",
    generate=generate_polygon_interior,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_polygon_interior,
)
