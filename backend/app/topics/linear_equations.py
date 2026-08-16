import random

import sympy as sp

from app.core.models import ModelledExample, Question, Tier
from app.topics.algebra_utils import X, fmt_linear, fmt_num, solve_linear_with_steps
from app.topics.base import TopicDefinition

SECTION = "algebra"
GROUP = "Solving Linear Equations"


def _rand_nonzero(rng: random.Random, lo: int, hi: int) -> int:
    while True:
        v = rng.randint(lo, hi)
        if v != 0:
            return v


def _frac(num, den) -> str:
    return f"\\frac{{{num}}}{{{den}}}"


def _build_one_step(rng: random.Random):
    """Build one of the four one-step equation forms, each with equal (25%)
    probability per question - addition, subtraction, multiplication,
    division. Returns (op, a, disp, steps, solution, lhs, rhs, dedup_key)."""
    op = rng.choice(["add", "sub", "mul", "div"])
    if op == "add":  # x + a = c
        a = rng.randint(1, 15)
        sol = rng.randint(1, 12)
        c = sol + a
        disp = f"{fmt_linear(1, a)} = {fmt_num(c)}"
        steps, solution = solve_linear_with_steps(1, a, 0, c)
        lhs, rhs = X + a, sp.Integer(c)
    elif op == "sub":  # x - a = c
        a = rng.randint(1, 15)
        sol = rng.randint(1, 12)
        c = sol - a
        disp = f"{fmt_linear(1, -a)} = {fmt_num(c)}"
        steps, solution = solve_linear_with_steps(1, -a, 0, c)
        lhs, rhs = X - a, sp.Integer(c)
    elif op == "mul":  # ax = c
        a = _rand_nonzero(rng, 2, 9)
        sol = rng.randint(1, 12)
        c = a * sol
        disp = f"{fmt_linear(a, 0)} = {fmt_num(c)}"
        steps, solution = solve_linear_with_steps(a, 0, 0, c)
        lhs, rhs = a * X, sp.Integer(c)
    else:  # div: x/a = c
        a = _rand_nonzero(rng, 2, 9)
        c = rng.randint(1, 12)
        sol = c * a
        disp = f"{_frac('x', a)} = {fmt_num(c)}"
        steps = [f"Multiply both sides by {a}: x = {c} × {a}", f"x = {sol}"]
        solution = sp.Integer(sol)
        lhs, rhs = X / a, sp.Integer(c)
    key = f"one_step:{op}:{a}:{c}"
    return op, a, disp, steps, solution, lhs, rhs, key


def generate_one_step(tier: Tier, rng: random.Random) -> Question:
    op, _a, disp, steps, solution, lhs, rhs, key = _build_one_step(rng)
    _verify(lhs, rhs, solution, f"one_step_{op}")

    return Question(
        topic_id="linear_one_step_F",
        tier=Tier.FOUNDATION,
        prompt=f"Solve: {disp}",
        solution_steps=tuple(steps),
        final_answer=fmt_num(solution),
        dedup_key=key,
    )


_ONE_STEP_TEACHING = {
    "add": lambda a: (
        f"has had one thing done to it: {a} has been added to it",
        f"The opposite of adding {a} is subtracting {a}, so subtract {a} from both sides of "
        "the equation.",
    ),
    "sub": lambda a: (
        f"has had one thing done to it: {a} has been subtracted from it",
        f"The opposite of subtracting {a} is adding {a}, so add {a} to both sides of the "
        "equation.",
    ),
    "mul": lambda a: (
        f"has had one thing done to it: it's been multiplied by {a}",
        f"The opposite of multiplying by {a} is dividing by {a}, so divide both sides of the "
        f"equation by {a}.",
    ),
    "div": lambda a: (
        f"has had one thing done to it: it's been divided by {a}",
        f"The opposite of dividing by {a} is multiplying by {a}, so multiply both sides of the "
        f"equation by {a}.",
    ),
}


def generate_modelled_example_one_step(tier: Tier, rng: random.Random) -> ModelledExample:
    op, a, disp, steps, solution, lhs, rhs, _key = _build_one_step(rng)
    _verify(lhs, rhs, solution, f"one_step_{op}_modelled")

    what_happened, undo_step = _ONE_STEP_TEACHING[op](a)
    teaching_steps = [
        f"In {disp}, x {what_happened}. Solving an equation means undoing whatever has been "
        "done to x, using the opposite operation.",
        undo_step,
        f"That leaves x on its own, equal to x = {fmt_num(solution)}.",
        f"Check by substituting x = {fmt_num(solution)} back into the original equation - it "
        "should make both sides equal.",
    ]
    worked_calculation = [disp] + list(steps)
    return ModelledExample(
        topic_id="linear_one_step_F",
        tier=Tier.FOUNDATION,
        prompt=f"Solve: {disp}",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=fmt_num(solution),
    )


_TWO_STEP_WEIGHTS = {
    "mul_add": 40,  # ax + b = c      - coefficient of x written first
    "mul_sub": 40,  # ax - b = c      - coefficient of x written first
    "add_first": 10,  # b + ax = c   - constant written first
    "sub_first": 10,  # b - ax = c   - constant written first
}


def _build_two_step(rng: random.Random):
    """Build one of the four two-step equation forms - multiply-then-add,
    multiply-then-subtract, and both of those again with the constant
    written FIRST (b + ax = c, b - ax = c). Weighted so a question starts
    with the coefficient of x (the ax... forms) far more often than with a
    plain number (the b... forms) - see _TWO_STEP_WEIGHTS - since the
    coefficient-first layout is the one students see far more often and the
    reordered form is just occasional extra variety, not equally common.
    The fraction-based two-step forms (x/a +- b = c, (x+p)/a = b, mx/a = c)
    live on the sibling "Two-Step Equations (Fractions)" topic instead - see
    fractional_equations.py. Returns (op, a, b, disp, steps, solution, lhs,
    rhs, dedup_key)."""
    op = rng.choices(list(_TWO_STEP_WEIGHTS), weights=list(_TWO_STEP_WEIGHTS.values()))[0]
    a = _rand_nonzero(rng, 2, 9)
    b = rng.randint(1, 15)
    sol = rng.randint(1, 12)
    ax_part = fmt_linear(a, 0)
    if op == "mul_add":  # ax + b = c
        c = a * sol + b
        disp = f"{fmt_linear(a, b)} = {fmt_num(c)}"
        steps, solution = solve_linear_with_steps(a, b, 0, c)
        lhs, rhs = a * X + b, sp.Integer(c)
    elif op == "mul_sub":  # ax - b = c
        c = a * sol - b
        disp = f"{fmt_linear(a, -b)} = {fmt_num(c)}"
        steps, solution = solve_linear_with_steps(a, -b, 0, c)
        lhs, rhs = a * X - b, sp.Integer(c)
    elif op == "add_first":  # b + ax = c (same algebra as mul_add, reordered)
        c = a * sol + b
        disp = f"{fmt_num(b)} + {ax_part} = {fmt_num(c)}"
        steps, solution = solve_linear_with_steps(a, b, 0, c)
        steps = [disp] + steps[1:]
        lhs, rhs = a * X + b, sp.Integer(c)
    else:  # sub_first: b - ax = c
        c = b - a * sol
        disp = f"{fmt_num(b)} - {ax_part} = {fmt_num(c)}"
        bc = b - c  # == a * sol, by construction
        clear_c_step = (
            f"Subtract {fmt_num(c)} from both sides:" if c > 0 else f"Add {fmt_num(-c)} to both sides:"
        )
        steps = [
            disp,
            f"Add {ax_part} to both sides:",
            f"{fmt_num(b)} = {fmt_num(c)} + {ax_part}",
            clear_c_step,
            f"{fmt_num(bc)} = {ax_part}",
            f"Divide both sides by {fmt_num(a)}:",
            f"x = {fmt_num(sol)}",
        ]
        solution = sp.Integer(sol)
        lhs, rhs = b - a * X, sp.Integer(c)
    key = f"two_step:{op}:{a}:{b}:{c}"
    return op, a, b, disp, steps, solution, lhs, rhs, key


def generate_two_step(tier: Tier, rng: random.Random) -> Question:
    op, _a, _b, disp, steps, solution, lhs, rhs, key = _build_two_step(rng)
    _verify(lhs, rhs, solution, f"two_step_{op}")

    return Question(
        topic_id="linear_two_step_F",
        tier=Tier.FOUNDATION,
        prompt=f"Solve: {disp}",
        solution_steps=tuple(steps),
        final_answer=fmt_num(solution),
        dedup_key=key,
    )


_TWO_STEP_TEACHING = {
    "mul_add": lambda a, b: (
        f"it's multiplied by {a}, and then {b} is added",
        "undo the addition first, then the multiplication",
        [f"Subtract {b} from both sides to undo the '+ {b}'.", f"Divide both sides by {a} to undo the multiplication."],
    ),
    "mul_sub": lambda a, b: (
        f"it's multiplied by {a}, and then {b} is subtracted",
        "undo the subtraction first, then the multiplication",
        [f"Add {b} to both sides to undo the '- {b}'.", f"Divide both sides by {a} to undo the multiplication."],
    ),
    "add_first": lambda a, b: (
        f"it's multiplied by {a}, and {b} is added - just written with the {b} first",
        "the order it's written in doesn't change how to solve it: undo the addition first, then "
        "the multiplication",
        [f"Subtract {b} from both sides to undo the '+ {b}'.", f"Divide both sides by {a} to undo the multiplication."],
    ),
    "sub_first": lambda a, b: (
        f"x is being multiplied by {a} and then subtracted FROM {b} - a trickier order, since x "
        "isn't on its own on one side yet",
        "first add the x-term to both sides so x has a positive coefficient, then treat it like "
        "a normal two-step equation",
        [
            f"Add {a}x to both sides, so the x-term moves across and the {b} is left on its own "
            "on the left.",
            f"Subtract the constant from both sides to leave {a}x on one side by itself.",
            f"Divide both sides by {a} to undo the multiplication.",
        ],
    ),
}


def generate_modelled_example_two_step(tier: Tier, rng: random.Random) -> ModelledExample:
    op, a, b, disp, steps, solution, lhs, rhs, _key = _build_two_step(rng)
    _verify(lhs, rhs, solution, f"two_step_{op}_modelled")

    what_happened, undo_order, undo_lines = _TWO_STEP_TEACHING[op](a, b)
    teaching_steps = [
        f"The equation {disp} has two things attached to x: {what_happened}. To get x on its "
        f"own, {undo_order}.",
        *undo_lines,
        f"That leaves x on its own, equal to x = {fmt_num(solution)}.",
        f"Check by substituting x = {fmt_num(solution)} back into the original equation - it "
        "should make both sides equal.",
    ]
    worked_calculation = list(steps)  # every branch's steps[0] is already the disp line
    return ModelledExample(
        topic_id="linear_two_step_F",
        tier=Tier.FOUNDATION,
        prompt=f"Solve: {disp}",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=fmt_num(solution),
    )


def _signed_term(value, magnitude_str: str) -> str:
    """A term named on its own (not mid-equation), e.g. '5x' or '-2x'."""
    return magnitude_str if value >= 0 else f"-{magnitude_str}"


def _build_multi_step(rng: random.Random):
    """Build a multi-step equation with two x-terms and two constant terms
    in a randomly shuffled order, e.g. '5x + 3 - 2x + 7 = 16' or
    '3 + 5x + 7 - 2x = 16'. coeff1 (the FIRST coefficient of x drawn) always
    stays positive per direct user request; coeff2 (the second) is
    occasionally negative for variety, capped so the two x-terms always
    collect to a positive combined coefficient (never harder than a normal
    two-step equation once collected). const1 always stays positive too, so
    the equation is guaranteed to never start with a '-' sign, whichever of
    coeff1's term / const1 ends up leading - only coeff2/const2 (never the
    leading term) can introduce a genuine negative into the expression.
    Returns (coeff1, coeff2, const1, const2, sol, combined_coeff,
    combined_const, c, lhs_str, prompt, steps, solution, orig_lhs, orig_rhs,
    dedup_key)."""
    coeff1 = rng.randint(2, 6)
    if rng.random() < 0.3:
        coeff2 = -rng.randint(1, coeff1 - 1)
    else:
        coeff2 = rng.randint(2, 6)
    const1 = rng.randint(1, 15)
    const2 = _rand_nonzero(rng, -10, 10)
    sol = rng.randint(1, 12)
    combined_coeff = coeff1 + coeff2
    combined_const = const1 + const2
    c = combined_coeff * sol + combined_const

    t_coeff1 = (coeff1, fmt_linear(coeff1, 0))
    t_const1 = (const1, fmt_num(const1))
    t_coeff2 = (coeff2, fmt_linear(abs(coeff2), 0))
    t_const2 = (const2, fmt_num(abs(const2)))
    leading = rng.choice([t_coeff1, t_const1])  # always non-negative
    remaining = [t for t in (t_coeff1, t_const1, t_coeff2, t_const2) if t is not leading]
    rng.shuffle(remaining)
    order = [leading] + remaining

    parts = [order[0][1]]
    for signed_val, mag_str in order[1:]:
        parts.append(f"+ {mag_str}" if signed_val >= 0 else f"- {mag_str}")
    lhs_str = " ".join(parts)

    coeff2_sign = "+" if coeff2 >= 0 else "-"
    const2_sign = "+" if const2 >= 0 else "-"
    collect_step = (
        f"Collect like terms: {coeff1}x {coeff2_sign} {abs(coeff2)}x = {fmt_linear(combined_coeff, 0)}, "
        f"{fmt_num(const1)} {const2_sign} {fmt_num(abs(const2))} = {fmt_num(combined_const)}"
    )
    solve_steps, solution = solve_linear_with_steps(combined_coeff, combined_const, 0, c)
    steps = [collect_step] + solve_steps

    orig_lhs = coeff1 * X + const1 + coeff2 * X + const2
    orig_rhs = sp.Integer(c)
    prompt = f"Solve: {lhs_str} = {fmt_num(c)}"
    key = f"multi_step:{coeff1}:{const1}:{coeff2}:{const2}:{c}:{lhs_str}"
    return (
        coeff1, coeff2, const1, const2, sol, combined_coeff, combined_const, c,
        lhs_str, prompt, steps, solution, orig_lhs, orig_rhs, key,
    )


def generate_multi_step(tier: Tier, rng: random.Random) -> Question:
    (
        coeff1, coeff2, const1, const2, sol, combined_coeff, combined_const, c,
        lhs_str, prompt, steps, solution, orig_lhs, orig_rhs, key,
    ) = _build_multi_step(rng)
    _verify(orig_lhs, orig_rhs, solution, "multi_step")

    return Question(
        topic_id="linear_multi_step_F",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=fmt_num(solution),
        dedup_key=key,
    )


def generate_modelled_example_multi_step(tier: Tier, rng: random.Random) -> ModelledExample:
    (
        coeff1, coeff2, const1, const2, sol, combined_coeff, combined_const, c,
        lhs_str, prompt, steps, solution, orig_lhs, orig_rhs, _key,
    ) = _build_multi_step(rng)
    _verify(orig_lhs, orig_rhs, solution, "multi_step_modelled")

    coeff2_named = _signed_term(coeff2, f"{abs(coeff2)}x")
    coeff2_sign = "+" if coeff2 >= 0 else "-"
    const2_sign = "+" if const2 >= 0 else "-"
    teaching_steps = [
        f"Before this looks like a familiar two-step equation, notice x appears twice - in {coeff1}x "
        f"and {coeff2_named}. The first job with any equation like this is to collect like terms so "
        "there's only one x term to deal with, wherever in the equation each term happens to be written.",
        f"Collect the x terms together: {coeff1}x {coeff2_sign} {abs(coeff2)}x = {fmt_linear(combined_coeff, 0)}. "
        f"Collect the number terms together too: {const1} {const2_sign} {abs(const2)} = {combined_const}. "
        f"The equation now reads {fmt_linear(combined_coeff, combined_const)} = {c}.",
        f"This is now a two-step equation, so solve it the usual way: subtract {fmt_num(combined_const)} "
        f"from both sides to get {fmt_linear(combined_coeff, 0)} = {c - combined_const}, then divide "
        f"both sides by {combined_coeff} to get x = {sol}.",
        f"Check by substituting x = {sol} into the original equation - it should make both sides equal.",
    ]
    worked_calculation = [
        lhs_str + f" = {fmt_num(c)}",
        f"{fmt_linear(combined_coeff, combined_const)} = {c}",
        f"{fmt_linear(combined_coeff, 0)} = {c - combined_const}",
        f"x = {sol}",
    ]
    return ModelledExample(
        topic_id="linear_multi_step_F",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=fmt_num(sol),
    )


def generate_both_sides(tier: Tier, rng: random.Random) -> Question:
    a = _rand_nonzero(rng, -9, 9)
    c = _rand_nonzero(rng, -9, 9)
    while c == a:
        c = _rand_nonzero(rng, -9, 9)
    sol = _rand_nonzero(rng, -10, 10)
    b = rng.randint(-15, 15)
    d = a * sol + b - c * sol

    orig_lhs = a * X + b
    orig_rhs = c * X + d
    steps, solution = solve_linear_with_steps(a, b, c, d)
    _verify(orig_lhs, orig_rhs, solution, "both_sides")

    return Question(
        topic_id="linear_both_sides_H",
        tier=Tier.HIGHER,
        prompt=f"Solve: {fmt_linear(a, b)} = {fmt_linear(c, d)}",
        solution_steps=tuple(steps),
        final_answer=fmt_num(solution),
        dedup_key=f"both_sides:{a}:{b}:{c}:{d}",
    )


def generate_modelled_example_both_sides(tier: Tier, rng: random.Random) -> ModelledExample:
    a = _rand_nonzero(rng, -9, 9)
    c = _rand_nonzero(rng, -9, 9)
    while c == a:
        c = _rand_nonzero(rng, -9, 9)
    sol = _rand_nonzero(rng, -10, 10)
    b = rng.randint(-15, 15)
    d = a * sol + b - c * sol

    orig_lhs = a * X + b
    orig_rhs = c * X + d
    residual = sp.simplify(orig_lhs.subs(X, sol) - orig_rhs.subs(X, sol))
    if residual != 0:
        raise ValueError("modelled example both_sides verification failed")

    new_coeff = a - c
    new_const = d - b
    teaching_steps = [
        f"This equation has an x term on both sides - {a}x on the left and {c}x on the right - so "
        "before we can isolate x, every x term needs to be brought together onto one side.",
        f"Subtract {fmt_num(c)}x from both sides to remove the x term from the right-hand side: "
        f"{fmt_linear(new_coeff, b)} = {fmt_num(d)}.",
        f"Now subtract {fmt_num(b)} from both sides to leave the x term on its own: "
        f"{fmt_linear(new_coeff, 0)} = {fmt_num(new_const)}.",
        f"Divide both sides by {fmt_num(new_coeff)}: x = {fmt_num(new_const)} ÷ {fmt_num(new_coeff)} "
        f"= {sol}.",
        f"Check by substituting x = {sol} into both sides of the original equation: left-hand side = "
        f"{a}×({sol}) + {b} = {a * sol + b}; right-hand side = {c}×({sol}) + {d} = {c * sol + d}. Both "
        "sides agree, so the solution is correct.",
    ]
    worked_calculation = [
        f"{fmt_linear(a, b)} = {fmt_linear(c, d)}",
        f"{fmt_linear(new_coeff, b)} = {fmt_num(d)}",
        f"{fmt_linear(new_coeff, 0)} = {fmt_num(new_const)}",
        f"x = {sol}",
    ]
    return ModelledExample(
        topic_id="linear_both_sides_H",
        tier=Tier.HIGHER,
        prompt=f"Solve: {fmt_linear(a, b)} = {fmt_linear(c, d)}",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=fmt_num(sol),
    )


def generate_both_sides_foundation(tier: Tier, rng: random.Random) -> Question:
    # Same shape as generate_both_sides but with positive coefficients and a
    # positive solution, so a Foundation student never has to juggle a negative
    # coefficient of x - this is Foundation-tier content on the real GCSE specs,
    # just with friendlier numbers than the Higher version above.
    a = rng.randint(2, 6)
    c = rng.randint(2, 6)
    while c == a:
        c = rng.randint(2, 6)
    sol = rng.randint(1, 10)
    b = rng.randint(0, 12)
    d = a * sol + b - c * sol

    orig_lhs = a * X + b
    orig_rhs = c * X + d
    steps, solution = solve_linear_with_steps(a, b, c, d)
    _verify(orig_lhs, orig_rhs, solution, "both_sides_foundation")

    return Question(
        topic_id="linear_both_sides_F",
        tier=Tier.FOUNDATION,
        prompt=f"Solve: {fmt_linear(a, b)} = {fmt_linear(c, d)}",
        solution_steps=tuple(steps),
        final_answer=fmt_num(solution),
        dedup_key=f"both_sides_f:{a}:{b}:{c}:{d}",
    )


def generate_modelled_example_both_sides_foundation(tier: Tier, rng: random.Random) -> ModelledExample:
    a = rng.randint(2, 6)
    c = rng.randint(2, 6)
    while c == a:
        c = rng.randint(2, 6)
    sol = rng.randint(1, 10)
    b = rng.randint(0, 12)
    d = a * sol + b - c * sol

    orig_lhs = a * X + b
    orig_rhs = c * X + d
    residual = sp.simplify(orig_lhs.subs(X, sol) - orig_rhs.subs(X, sol))
    if residual != 0:
        raise ValueError("modelled example both_sides_foundation verification failed")

    new_coeff = a - c
    new_const = d - b
    teaching_steps = [
        f"This equation has x on both sides - {a}x on the left and {c}x on the right - so before we can "
        "solve for x, we need to get every x term onto the same side.",
        f"Subtract {fmt_num(c)}x from both sides to remove the x term from the right-hand side: "
        f"{fmt_linear(new_coeff, b)} = {fmt_num(d)}.",
        f"Subtract {fmt_num(b)} from both sides to leave the x term on its own: "
        f"{fmt_linear(new_coeff, 0)} = {fmt_num(new_const)}.",
        f"Divide both sides by {fmt_num(new_coeff)}: x = {fmt_num(new_const)} ÷ {fmt_num(new_coeff)} "
        f"= {sol}.",
        f"Check by substituting x = {sol} into both sides of the original equation: left-hand side = "
        f"{a}×{sol} + {b} = {a * sol + b}; right-hand side = {c}×{sol} + {d} = {c * sol + d}. Both "
        "sides match, so the solution is correct.",
    ]
    worked_calculation = [
        f"{fmt_linear(a, b)} = {fmt_linear(c, d)}",
        f"{fmt_linear(new_coeff, b)} = {fmt_num(d)}",
        f"{fmt_linear(new_coeff, 0)} = {fmt_num(new_const)}",
        f"x = {sol}",
    ]
    return ModelledExample(
        topic_id="linear_both_sides_F",
        tier=Tier.FOUNDATION,
        prompt=f"Solve: {fmt_linear(a, b)} = {fmt_linear(c, d)}",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=fmt_num(sol),
    )


def _build_brackets(rng: random.Random):
    """Build linear_brackets_H content - either a single bracket
    (a(bx+c) = d, ~30% of the time) or, more often (~70%, per direct user
    request for "more double bracket questions"), two DIFFERENT brackets
    combined with +/- (a(bx+c) +- e(fx+g) = d). The solution is weighted
    ~80% positive / ~20% negative (was an unweighted ~50/50 split before,
    per direct user feedback that Higher's answers skewed negative too
    often). Returns (shape, disp, pre_steps, solve_steps, solution,
    orig_lhs, orig_rhs, dedup_key) - pre_steps is the expand[/collect] work
    (1 line for "single", 2 for "double"); solve_steps is the usual
    solve_linear_with_steps output for what's left once pre_steps is done."""
    sol = rng.randint(1, 8) if rng.random() < 0.8 else -rng.randint(1, 8)

    if rng.random() < 0.3:
        shape = "single"
        a = rng.randint(2, 6)
        b = rng.randint(2, 6)
        c = rng.randint(-8, 8)
        d = a * (b * sol + c)
        bracket_str = fmt_linear(b, c)
        disp = f"{a}({bracket_str}) = {fmt_num(d)}"
        expand_step = f"Expand the bracket: {a}({bracket_str}) = {fmt_linear(a * b, a * c)}"
        solve_steps, solution = solve_linear_with_steps(a * b, a * c, 0, d)
        pre_steps = [expand_step]
        orig_lhs = a * (b * X + c)
        key = f"brackets_h_single:{a}:{b}:{c}:{d}"
    else:
        shape = "double"
        for _ in range(50):
            a = rng.randint(2, 6)
            b = rng.randint(2, 6)
            c = rng.randint(-8, 8)
            e = rng.randint(2, 6)
            f = rng.randint(2, 6)
            g = rng.randint(-8, 8)
            op = rng.choice(["+", "-"])
            # Subtracting a whole bracket flips the sign of BOTH its expanded
            # terms, not just the leading one - e.g. "- 6(2x + 7)" expands to
            # "- 12x - 42", not "- 12x + 42". second_coeff/second_const are
            # each already correctly signed relative to zero, so they can be
            # joined onto the first bracket's expansion term-by-term below.
            second_coeff = e * f if op == "+" else -(e * f)
            if a * b + second_coeff != 0:
                break
        else:
            raise ValueError("could not build a valid double-bracket equation")
        second_const = e * g if op == "+" else -(e * g)
        combined_coeff = a * b + second_coeff
        combined_const = a * c + second_const
        d = combined_coeff * sol + combined_const

        bracket1_str = fmt_linear(b, c)
        bracket2_str = fmt_linear(f, g)
        disp = f"{a}({bracket1_str}) {op} {e}({bracket2_str}) = {fmt_num(d)}"

        expanded_parts = [fmt_linear(a * b, a * c)]
        for val, mag_str in ((second_coeff, fmt_linear(abs(second_coeff), 0)), (second_const, fmt_num(abs(second_const)))):
            if val != 0:
                expanded_parts.append(f"+ {mag_str}" if val >= 0 else f"- {mag_str}")
        expanded_full = " ".join(expanded_parts)

        expand_step = f"Expand both brackets: {a}({bracket1_str}) {op} {e}({bracket2_str}) = {expanded_full}"
        collect_step = f"Collect like terms: {expanded_full} = {fmt_linear(combined_coeff, combined_const)}"
        solve_steps, solution = solve_linear_with_steps(combined_coeff, combined_const, 0, d)
        pre_steps = [expand_step, collect_step]
        orig_lhs = a * (b * X + c) + (e * (f * X + g) if op == "+" else -(e * (f * X + g)))
        key = f"brackets_h_double:{a}:{b}:{c}:{op}:{e}:{f}:{g}:{d}"

    orig_rhs = sp.Integer(d)
    return shape, disp, pre_steps, solve_steps, solution, orig_lhs, orig_rhs, key


def generate_brackets(tier: Tier, rng: random.Random) -> Question:
    shape, disp, pre_steps, solve_steps, solution, orig_lhs, orig_rhs, key = _build_brackets(rng)
    _verify(orig_lhs, orig_rhs, solution, f"brackets_{shape}")

    return Question(
        topic_id="linear_brackets_H",
        tier=Tier.HIGHER,
        prompt=f"Solve: {disp}",
        solution_steps=tuple(pre_steps + solve_steps),
        final_answer=fmt_num(solution),
        dedup_key=key,
    )


def generate_modelled_example_brackets(tier: Tier, rng: random.Random) -> ModelledExample:
    shape, disp, pre_steps, solve_steps, solution, orig_lhs, orig_rhs, _key = _build_brackets(rng)
    _verify(orig_lhs, orig_rhs, solution, f"brackets_{shape}_modelled")

    if shape == "single":
        teaching_intro = (
            "There's a bracket in this equation, and before we can solve for x we need to get rid of "
            "it - the number outside the bracket must be multiplied by everything inside it."
        )
        expand_summary = pre_steps[0].removeprefix("Expand the bracket: ") + "."
    else:
        teaching_intro = (
            "There are two brackets in this equation, each with its own number outside it - expand "
            "both brackets first, multiplying each one's outside number by everything inside it, "
            "before doing anything else."
        )
        expand_summary = (
            pre_steps[0].removeprefix("Expand both brackets: ")
            + ", then collect the x terms and number terms together: "
            + pre_steps[1].removeprefix("Collect like terms: ")
            + "."
        )
    teaching_steps = [
        teaching_intro,
        f"Expanding gives {expand_summary}",
        f"This is now a normal equation, so solve it the usual way: {'  '.join(solve_steps[1:])}",
        f"Check by substituting x = {fmt_num(solution)} back into the original equation - it should "
        "make both sides equal.",
    ]
    worked_calculation = [disp] + pre_steps + solve_steps
    return ModelledExample(
        topic_id="linear_brackets_H",
        tier=Tier.HIGHER,
        prompt=f"Solve: {disp}",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=fmt_num(solution),
    )


def _build_brackets_foundation(rng: random.Random):
    """Build a(bx + c) = d, b always positive (never a negative coefficient),
    c occasionally negative (~30% chance) so the bracket itself contains a
    subtraction, e.g. '3(2x - 5) = 6' - capped so the bracket's own value
    (bx + c) always stays positive, keeping d positive too and avoiding an
    extra layer of sign confusion on top of the new negative-inside-brackets
    skill. ~10% of the time the equation is written with the plain target
    number first, d = a(bx + c), instead of the usual a(bx + c) = d order.
    Returns (a, b, c, d, sol, bracket_str, disp, steps, solution, orig_lhs,
    orig_rhs, dedup_key)."""
    a = rng.randint(2, 5)
    b = rng.randint(2, 5)
    sol = rng.randint(1, 8)
    if rng.random() < 0.3:
        max_neg = max(1, min(8, b * sol - 1))
        c = -rng.randint(1, max_neg)
    else:
        c = rng.randint(0, 8)
    d = a * (b * sol + c)

    bracket_str = fmt_linear(b, c)
    swapped = rng.random() < 0.10
    disp = f"{fmt_num(d)} = {a}({bracket_str})" if swapped else f"{a}({bracket_str}) = {fmt_num(d)}"

    orig_lhs = a * (b * X + c)
    orig_rhs = sp.Integer(d)
    expand_step = f"Expand the bracket: {a}({bracket_str}) = {fmt_linear(a * b, a * c)}"
    solve_steps, solution = solve_linear_with_steps(a * b, a * c, 0, d)
    steps = [expand_step] + solve_steps
    key = f"brackets_f:{a}:{b}:{c}:{d}:{swapped}"
    return a, b, c, d, sol, bracket_str, disp, steps, solution, orig_lhs, orig_rhs, key


def generate_brackets_foundation(tier: Tier, rng: random.Random) -> Question:
    a, b, c, d, sol, bracket_str, disp, steps, solution, orig_lhs, orig_rhs, key = _build_brackets_foundation(rng)
    _verify(orig_lhs, orig_rhs, solution, "brackets_foundation")

    return Question(
        topic_id="linear_brackets_F",
        tier=Tier.FOUNDATION,
        prompt=f"Solve: {disp}",
        solution_steps=tuple(steps),
        final_answer=fmt_num(solution),
        dedup_key=key,
    )


def generate_modelled_example_brackets_foundation(tier: Tier, rng: random.Random) -> ModelledExample:
    a, b, c, d, sol, bracket_str, disp, _steps, solution, orig_lhs, orig_rhs, _key = _build_brackets_foundation(rng)
    _verify(orig_lhs, orig_rhs, solution, "brackets_foundation_modelled")

    expanded_coeff, expanded_const = a * b, a * c
    const_sign = "+" if c >= 0 else "-"
    teaching_steps = [
        f"There's a bracket in this equation, and before we can solve for x we need to get rid of it - "
        f"the number {a} outside the bracket must be multiplied by everything inside it.",
        f"Expand the bracket: {a}({bracket_str}) = {a}×{fmt_linear(b, 0)} {const_sign} {a}×{abs(c)} = "
        f"{fmt_linear(expanded_coeff, expanded_const)}. The equation is now "
        f"{fmt_linear(expanded_coeff, expanded_const)} = {d}, a normal two-step equation.",
        f"Subtract {fmt_num(expanded_const)} from both sides: {fmt_linear(expanded_coeff, 0)} = "
        f"{d - expanded_const}. Then divide both sides by {expanded_coeff}: x = {sol}.",
        f"Check by substituting x = {sol} back into the original equation - it should make both sides equal.",
    ]
    worked_calculation = [
        disp,
        f"{fmt_linear(expanded_coeff, expanded_const)} = {d}",
        f"{fmt_linear(expanded_coeff, 0)} = {d - expanded_const}",
        f"x = {sol}",
    ]
    return ModelledExample(
        topic_id="linear_brackets_F",
        tier=Tier.FOUNDATION,
        prompt=f"Solve: {disp}",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=fmt_num(sol),
    )


def _verify(orig_lhs, orig_rhs, solution, shape: str) -> None:
    residual = sp.simplify(orig_lhs.subs(X, solution) - orig_rhs.subs(X, solution))
    if residual != 0:
        raise ValueError(
            f"Generated linear equation failed verification (shape={shape}, residual={residual})."
        )


TOPIC_ONE_STEP = TopicDefinition(
    id="linear_one_step_F",
    display_name="One-Step Equations",
    description="Solve simple equations of the form x + a = c, x - a = c, ax = c, or x/a = c.",
    generate=generate_one_step,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_one_step,
)

TOPIC_TWO_STEP = TopicDefinition(
    id="linear_two_step_F",
    display_name="Two-Step Equations",
    description=(
        "Solve equations of the form ax + b = c or ax - b = c, including with the constant "
        "written first (b + ax = c or b - ax = c)."
    ),
    generate=generate_two_step,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_two_step,
)

TOPIC_MULTI_STEP = TopicDefinition(
    id="linear_multi_step_F",
    display_name="Multi-Step Equations",
    description="Collect like terms on one side before solving.",
    generate=generate_multi_step,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_multi_step,
)

TOPIC_BOTH_SIDES_FOUNDATION = TopicDefinition(
    id="linear_both_sides_F",
    display_name="Unknowns on Both Sides",
    description="Solve equations with the unknown appearing on both sides.",
    generate=generate_both_sides_foundation,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_both_sides_foundation,
)

TOPIC_BOTH_SIDES = TopicDefinition(
    id="linear_both_sides_H",
    display_name="Unknowns on Both Sides",
    description="Solve equations with the unknown appearing on both sides, including negative coefficients.",
    generate=generate_both_sides,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_both_sides,
)

TOPIC_BRACKETS_FOUNDATION = TopicDefinition(
    id="linear_brackets_F",
    display_name="Equations with Brackets",
    description="Expand a bracket before solving the equation.",
    generate=generate_brackets_foundation,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_brackets_foundation,
)

TOPIC_BRACKETS = TopicDefinition(
    id="linear_brackets_H",
    display_name="Equations with Brackets",
    description="Expand a bracket before solving the equation, including negative terms.",
    generate=generate_brackets,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_brackets,
)
