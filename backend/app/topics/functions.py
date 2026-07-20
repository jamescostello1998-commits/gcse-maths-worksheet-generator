import random

import sympy as sp

from app.core.models import ModelledExample, Question, Tier
from app.topics.algebra_utils import X, fmt_linear, fmt_num, solve_linear_with_steps
from app.topics.base import TopicDefinition

SECTION = "algebra"
GROUP = "Functions"


def _rand_nonzero(rng: random.Random, lo: int, hi: int) -> int:
    while True:
        v = rng.randint(lo, hi)
        if v != 0:
            return v


def generate_functions_evaluate(tier: Tier, rng: random.Random) -> Question:
    a = _rand_nonzero(rng, -6, 6)
    b = rng.randint(-10, 10)
    shape = rng.choice(["evaluate", "solve"])

    if shape == "evaluate":
        k = rng.randint(-8, 8)
        value = a * k + b

        # Independent verification via sympy substitution into f(x) = ax + b.
        check = int((a * X + b).subs(X, k))
        if check != value:
            raise ValueError("functions_evaluate verification failed")

        steps = [
            f"f({k}) = {a}×({k}) + {b}" if b != 0 else f"f({k}) = {a}×({k})",
            f"f({k}) = {value}",
        ]
        return Question(
            topic_id="functions_evaluate",
            tier=Tier.FOUNDATION,
            prompt=f"f(x) = {fmt_linear(a, b)}. Find f({k}).",
            solution_steps=tuple(steps),
            final_answer=str(value),
            dedup_key=f"func_eval:{a}:{b}:{k}",
        )
    else:
        target = rng.randint(-10, 10)
        steps, solution = solve_linear_with_steps(a, b, 0, target)
        return Question(
            topic_id="functions_evaluate",
            tier=Tier.FOUNDATION,
            prompt=f"f(x) = {fmt_linear(a, b)}. Find the value of x for which f(x) = {target}.",
            solution_steps=tuple(steps),
            final_answer=fmt_num(solution),
            dedup_key=f"func_solve:{a}:{b}:{target}",
        )


def _fmt_inverse(a: int, b: int) -> str:
    inner = f"x - {b}" if b > 0 else (f"x + {-b}" if b < 0 else "x")
    if a == 1:
        return inner
    return f"({inner})/{a}"


def generate_functions_composite_inverse(tier: Tier, rng: random.Random) -> Question:
    shape = rng.choice(["composite", "inverse"])

    if shape == "composite":
        a, b = _rand_nonzero(rng, -6, 6), rng.randint(-8, 8)
        c, d = _rand_nonzero(rng, -6, 6), rng.randint(-8, 8)
        order = rng.choice(["fg", "gf"])

        if order == "fg":
            new_a, new_b = a * c, a * d + b
            residual = sp.expand(a * (c * X + d) + b - (new_a * X + new_b))
            inner_call, outer_coeff, outer_const = fmt_linear(c, d), a, b
            name = "fg"
        else:
            new_a, new_b = c * a, c * b + d
            residual = sp.expand(c * (a * X + b) + d - (new_a * X + new_b))
            inner_call, outer_coeff, outer_const = fmt_linear(a, b), c, d
            name = "gf"

        if residual != 0:
            raise ValueError("functions_composite verification failed")

        steps = [
            f"{name}(x) = {'f' if order == 'fg' else 'g'}({inner_call})",
            f"= {outer_coeff}({inner_call}) + {outer_const}",
            f"= {fmt_linear(new_a, new_b)}",
        ]
        return Question(
            topic_id="functions_composite_inverse",
            tier=Tier.HIGHER,
            prompt=f"f(x) = {fmt_linear(a, b)} and g(x) = {fmt_linear(c, d)}. Find {name}(x).",
            solution_steps=tuple(steps),
            final_answer=fmt_linear(new_a, new_b),
            dedup_key=f"func_composite:{a}:{b}:{c}:{d}:{order}",
        )
    else:
        a = rng.randint(2, 6)
        b = rng.randint(-9, 9)
        inv_str = _fmt_inverse(a, b)

        # Independent verification: substitute the claimed inverse back into f and
        # confirm f(f^-1(x)) simplifies to x, via sympy - a different check than the
        # algebraic rearrangement used to derive the inverse.
        finv_expr = sp.Rational(1, a) * (X - b)
        residual = sp.simplify((a * X + b).subs(X, finv_expr) - X)
        if residual != 0:
            raise ValueError("functions_inverse verification failed")

        steps = [
            f"y = {fmt_linear(a, b)}",
            f"Rearrange to make x the subject: x = (y - {b}) / {a}" if b else f"Rearrange to make x the subject: x = y / {a}",
            f"Swap x and y: f^-1(x) = {inv_str}",
        ]
        return Question(
            topic_id="functions_composite_inverse",
            tier=Tier.HIGHER,
            prompt=f"f(x) = {fmt_linear(a, b)}. Find f^-1(x).",
            solution_steps=tuple(steps),
            final_answer=inv_str,
            dedup_key=f"func_inverse:{a}:{b}",
        )


def generate_modelled_example_functions_evaluate(tier: Tier, rng: random.Random) -> ModelledExample:
    a = _rand_nonzero(rng, -6, 6)
    b = rng.randint(-10, 10)
    shape = rng.choice(["evaluate", "solve"])

    if shape == "evaluate":
        k = rng.randint(-8, 8)
        value = a * k + b
        check = int((a * X + b).subs(X, k))
        if check != value:
            raise ValueError("modelled example functions_evaluate verification failed")

        teaching_steps = [
            f"f(x) = {fmt_linear(a, b)} is just a rule for turning an input into an output: whatever "
            "number goes in for x, multiply it by the coefficient and add the constant. Writing f(k) "
            "means 'apply that rule to the input k'.",
            f"To find f({k}), substitute x = {k} into the rule wherever x appears: "
            f"f({k}) = {a}×({k}){' + ' + str(b) if b > 0 else (' - ' + str(abs(b)) if b < 0 else '')}.",
            f"Work out the arithmetic: {a}×({k}) = {a * k}"
            + (f", then {'+' if b >= 0 else '-'} {abs(b)} gives {value}." if b != 0 else f", giving {value}."),
        ]
        worked_calculation = [
            f"f(x) = {fmt_linear(a, b)}",
            f"f({k}) = {a}×({k}){' + ' + str(b) if b > 0 else (' - ' + str(abs(b)) if b < 0 else '')}",
            f"= {value}",
        ]
        return ModelledExample(
            topic_id="functions_evaluate",
            tier=Tier.FOUNDATION,
            prompt=f"f(x) = {fmt_linear(a, b)}. Find f({k}).",
            worked_calculation=tuple(worked_calculation),
            teaching_steps=tuple(teaching_steps),
            final_answer=str(value),
        )
    else:
        target = rng.randint(-10, 10)
        solve_steps, solution = solve_linear_with_steps(a, b, 0, target)
        residual = sp.simplify((a * X + b).subs(X, solution) - target)
        if residual != 0:
            raise ValueError("modelled example functions_evaluate (solve) verification failed")

        teaching_steps = [
            f"f(x) = {fmt_linear(a, b)} tells us how to turn an input x into an output. This time we're "
            f"told the output is {target}, and asked to work backwards to find the input x - that "
            "turns the problem into an ordinary equation to solve.",
            f"Set the function's rule equal to the target output: {fmt_linear(a, b)} = {target}.",
            "Solve this equation for x exactly as you would any other linear equation, undoing the "
            "operations applied to x in reverse order.",
            f"This gives x = {fmt_num(solution)}.",
        ]
        worked_calculation = [
            f"f(x) = {fmt_linear(a, b)}",
            f"{fmt_linear(a, b)} = {target}",
            f"x = {fmt_num(solution)}",
        ]
        return ModelledExample(
            topic_id="functions_evaluate",
            tier=Tier.FOUNDATION,
            prompt=f"f(x) = {fmt_linear(a, b)}. Find the value of x for which f(x) = {target}.",
            worked_calculation=tuple(worked_calculation),
            teaching_steps=tuple(teaching_steps),
            final_answer=fmt_num(solution),
        )


def generate_modelled_example_functions_composite_inverse(tier: Tier, rng: random.Random) -> ModelledExample:
    shape = rng.choice(["composite", "inverse"])

    if shape == "composite":
        a, b = _rand_nonzero(rng, -6, 6), rng.randint(-8, 8)
        c, d = _rand_nonzero(rng, -6, 6), rng.randint(-8, 8)
        order = rng.choice(["fg", "gf"])

        if order == "fg":
            new_a, new_b = a * c, a * d + b
            residual = sp.expand(a * (c * X + d) + b - (new_a * X + new_b))
            inner_call, outer_coeff, outer_const = fmt_linear(c, d), a, b
            outer_name, inner_name = "f", "g"
        else:
            new_a, new_b = c * a, c * b + d
            residual = sp.expand(c * (a * X + b) + d - (new_a * X + new_b))
            inner_call, outer_coeff, outer_const = fmt_linear(a, b), c, d
            outer_name, inner_name = "g", "f"

        if residual != 0:
            raise ValueError("modelled example functions_composite verification failed")

        name = order
        teaching_steps = [
            f"{name}(x) means 'do {inner_name} first, then feed the result into {outer_name}'. So the "
            f"first job is to write down what's inside: {inner_name}(x) = {inner_call}.",
            f"Now apply {outer_name} to that whole expression, treating {inner_call} as the input: "
            f"{name}(x) = {outer_coeff}({inner_call}){' + ' + str(outer_const) if outer_const > 0 else (' - ' + str(abs(outer_const)) if outer_const < 0 else '')}.",
            f"Expand the bracket and collect like terms: {outer_coeff}×{inner_call.replace(' ', '')} "
            f"gives {new_a}x plus a constant, simplifying to {fmt_linear(new_a, new_b)}.",
        ]
        worked_calculation = [
            f"{name}(x) = {outer_name}({inner_call})",
            f"= {outer_coeff}({inner_call}){' + ' + str(outer_const) if outer_const > 0 else (' - ' + str(abs(outer_const)) if outer_const < 0 else '')}",
            f"= {fmt_linear(new_a, new_b)}",
        ]
        return ModelledExample(
            topic_id="functions_composite_inverse",
            tier=Tier.HIGHER,
            prompt=f"f(x) = {fmt_linear(a, b)} and g(x) = {fmt_linear(c, d)}. Find {name}(x).",
            worked_calculation=tuple(worked_calculation),
            teaching_steps=tuple(teaching_steps),
            final_answer=fmt_linear(new_a, new_b),
        )
    else:
        a = rng.randint(2, 6)
        b = rng.randint(-9, 9)
        inv_str = _fmt_inverse(a, b)

        finv_expr = sp.Rational(1, a) * (X - b)
        residual = sp.simplify((a * X + b).subs(X, finv_expr) - X)
        if residual != 0:
            raise ValueError("modelled example functions_inverse verification failed")

        teaching_steps = [
            f"The inverse function f^-1(x) undoes whatever f(x) does - it takes an output back to the "
            "input that produced it. The standard method is to write y = f(x), rearrange to make x "
            "the subject, then swap the letters x and y around.",
            f"Write y = {fmt_linear(a, b)}.",
            (f"Rearrange to make x the subject: subtract {b} from both sides then divide by {a}, "
             f"giving x = (y - {b})/{a}."
             if b else f"Rearrange to make x the subject: divide both sides by {a}, giving x = y/{a}."),
            f"Swap x and y (since f^-1 takes an x-input now): f^-1(x) = {inv_str}.",
        ]
        worked_calculation = [
            f"y = {fmt_linear(a, b)}",
            f"x = (y - {b})/{a}" if b else f"x = y/{a}",
            f"f^-1(x) = {inv_str}",
        ]
        return ModelledExample(
            topic_id="functions_composite_inverse",
            tier=Tier.HIGHER,
            prompt=f"f(x) = {fmt_linear(a, b)}. Find f^-1(x).",
            worked_calculation=tuple(worked_calculation),
            teaching_steps=tuple(teaching_steps),
            final_answer=inv_str,
        )


TOPIC_FUNCTIONS_EVALUATE = TopicDefinition(
    id="functions_evaluate",
    display_name="Function Notation",
    description="Evaluate a linear function, or solve for x given f(x).",
    generate=generate_functions_evaluate,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_functions_evaluate,
)

TOPIC_FUNCTIONS_COMPOSITE_INVERSE = TopicDefinition(
    id="functions_composite_inverse",
    display_name="Composite and Inverse Functions",
    description="Find a composite function fg(x) or gf(x), or the inverse function f^-1(x).",
    generate=generate_functions_composite_inverse,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_functions_composite_inverse,
)
