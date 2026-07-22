import random

import sympy as sp

from app.core.models import ModelledExample, Question, Tier
from app.topics.algebra_utils import fmt_num
from app.topics.base import TopicDefinition

SECTION = "number"
GROUP = "Order of Operations (BIDMAS)"


def _to_sympy_str(expr_str: str) -> str:
    """Convert the display form of an expression (×, ÷, ^) into a string sympy's own
    parser can evaluate (*, /, **) - used as an independent check of the manual,
    step-by-step BIDMAS evaluation each shape below builds by hand."""
    return expr_str.replace("×", "*").replace("÷", "/").replace("^", "**")


def _build_shape_a(rng: random.Random):
    """a + b × (c - d)^2 ÷ e  -  brackets, indices, multiplication, division, addition."""
    a = rng.randint(1, 20)
    c = rng.randint(2, 9)
    d = rng.randint(1, c - 1)
    # e is picked first, then b is forced to be a multiple of e, guaranteeing the
    # division step lands on a whole number - matching real BIDMAS worksheets,
    # which never leave the student with a stray fraction from the ÷ step.
    e = rng.randint(2, 9)
    b = e * rng.randint(1, 2)

    bracket_val = sp.Integer(c - d)
    power_val = bracket_val**2
    mul_val = b * power_val
    div_val = sp.Rational(mul_val, e)
    result = a + div_val

    expr_str = f"{a} + {b} × ({c} - {d})^2 ÷ {e}"
    steps = [
        f"Brackets: ({c} - {d}) = {bracket_val}",
        f"Indices: {bracket_val}^2 = {power_val}",
        f"Multiplication: {b} × {power_val} = {mul_val}",
        f"Division: {mul_val} ÷ {e} = {fmt_num(div_val)}",
        f"Addition: {a} + {fmt_num(div_val)} = {fmt_num(result)}",
    ]
    dedup_key = f"bidmas:a:{a}:{b}:{c}:{d}:{e}"
    return expr_str, steps, result, dedup_key


def _build_shape_b(rng: random.Random):
    """(a + b) × c - d ÷ e  -  brackets, addition, multiplication, division, subtraction."""
    a = rng.randint(1, 9)
    b = rng.randint(1, 9)
    c = rng.randint(2, 9)
    # e is picked first, then d is forced to be a multiple of e, guaranteeing the
    # division step lands on a whole number.
    e = rng.randint(2, 9)
    d = e * rng.randint(1, 3)

    bracket_val = a + b
    mul_val = bracket_val * c
    div_val = sp.Rational(d, e)
    result = mul_val - div_val

    expr_str = f"({a} + {b}) × {c} - {d} ÷ {e}"
    steps = [
        f"Brackets: ({a} + {b}) = {bracket_val}",
        f"Multiplication: {bracket_val} × {c} = {mul_val}",
        f"Division: {d} ÷ {e} = {fmt_num(div_val)}",
        f"Subtraction: {mul_val} - {fmt_num(div_val)} = {fmt_num(result)}",
    ]
    dedup_key = f"bidmas:b:{a}:{b}:{c}:{d}:{e}"
    return expr_str, steps, result, dedup_key


def _build_shape_c(rng: random.Random):
    """a^2 + b × c - d ÷ e  -  indices, addition, multiplication, subtraction, division."""
    a = rng.randint(2, 9)
    b = rng.randint(2, 9)
    c = rng.randint(2, 9)
    # e is picked first, then d is forced to be a multiple of e, guaranteeing the
    # division step lands on a whole number.
    e = rng.randint(2, 9)
    d = e * rng.randint(1, 3)

    a_sq = a**2
    mul_val = b * c
    div_val = sp.Rational(d, e)
    add_val = a_sq + mul_val
    result = add_val - div_val

    expr_str = f"{a}^2 + {b} × {c} - {d} ÷ {e}"
    steps = [
        f"Indices: {a}^2 = {a_sq}",
        f"Multiplication: {b} × {c} = {mul_val}",
        f"Division: {d} ÷ {e} = {fmt_num(div_val)}",
        f"Addition: {a_sq} + {mul_val} = {add_val}",
        f"Subtraction: {add_val} - {fmt_num(div_val)} = {fmt_num(result)}",
    ]
    dedup_key = f"bidmas:c:{a}:{b}:{c}:{d}:{e}"
    return expr_str, steps, result, dedup_key


def _build_shape_d(rng: random.Random):
    """a - b ÷ c × (d + e)  -  brackets, addition, division, multiplication, subtraction."""
    a = rng.randint(10, 30)
    # c is picked first, then b is forced to be a multiple of c, guaranteeing the
    # division step lands on a whole number.
    c = rng.randint(2, 9)
    b = c * rng.randint(1, 3)
    d = rng.randint(1, 9)
    e = rng.randint(1, 9)

    bracket_val = d + e
    div_val = sp.Rational(b, c)
    div_mul_val = div_val * bracket_val
    result = a - div_mul_val

    expr_str = f"{a} - {b} ÷ {c} × ({d} + {e})"
    steps = [
        f"Brackets: ({d} + {e}) = {bracket_val}",
        f"Division and multiplication have equal priority, so work left to right: "
        f"{b} ÷ {c} = {fmt_num(div_val)}, then × {bracket_val} = {fmt_num(div_mul_val)}",
        f"Subtraction: {a} - {fmt_num(div_mul_val)} = {fmt_num(result)}",
    ]
    dedup_key = f"bidmas:d:{a}:{b}:{c}:{d}:{e}"
    return expr_str, steps, result, dedup_key


_SHAPE_BUILDERS = [_build_shape_a, _build_shape_b, _build_shape_c, _build_shape_d]


def generate_bidmas(tier: Tier, rng: random.Random) -> Question:
    builder = rng.choice(_SHAPE_BUILDERS)
    expr_str, steps, result, dedup_key = builder(rng)

    # Independent verification: evaluate the same expression a second, genuinely different
    # way - via sympy's own parser and operator-precedence rules - rather than the manual
    # BIDMAS step-by-step evaluation used to build `result`/`steps` above.
    sympy_val = sp.sympify(_to_sympy_str(expr_str))
    if sp.simplify(sympy_val - result) != 0:
        raise ValueError(f"bidmas verification failed for expression: {expr_str}")

    return Question(
        topic_id="bidmas",
        tier=Tier.FOUNDATION,
        prompt=f"Work out {expr_str}. Use the correct order of operations.",
        solution_steps=tuple(steps),
        final_answer=fmt_num(result),
        dedup_key=dedup_key,
    )


def _build_teaching_shape_a(rng: random.Random):
    a = rng.randint(1, 20)
    c = rng.randint(2, 9)
    d = rng.randint(1, c - 1)
    # e is picked first, then b is forced to be a multiple of e, guaranteeing the
    # division step lands on a whole number - matching real BIDMAS worksheets,
    # which never leave the student with a stray fraction from the ÷ step.
    e = rng.randint(2, 9)
    b = e * rng.randint(1, 2)

    bracket_val = sp.Integer(c - d)
    power_val = bracket_val**2
    mul_val = b * power_val
    div_val = sp.Rational(mul_val, e)
    result = a + div_val

    expr_str = f"{a} + {b} × ({c} - {d})^2 ÷ {e}"
    teaching_steps = [
        f"BIDMAS tells us the order to work through a mixed expression like {expr_str}: Brackets first, "
        "then Indices, then Division and Multiplication (left to right), then Addition and Subtraction "
        "(left to right).",
        f"Start with the brackets: ({c} - {d}) = {bracket_val}.",
        f"Next come indices: {bracket_val}^2 = {power_val}.",
        f"Now division and multiplication, working left to right: {b} × {power_val} = {mul_val}, then "
        f"{mul_val} ÷ {e} = {fmt_num(div_val)}.",
        f"Finally, addition: {a} + {fmt_num(div_val)} = {fmt_num(result)}.",
    ]
    worked_calculation = [
        f"{expr_str}",
        f"= {a} + {b} × {power_val} ÷ {e}",
        f"= {a} + {fmt_num(div_val)}",
        f"= {fmt_num(result)}",
    ]
    return expr_str, teaching_steps, worked_calculation, result


def _build_teaching_shape_b(rng: random.Random):
    a = rng.randint(1, 9)
    b = rng.randint(1, 9)
    c = rng.randint(2, 9)
    # e is picked first, then d is forced to be a multiple of e, guaranteeing the
    # division step lands on a whole number.
    e = rng.randint(2, 9)
    d = e * rng.randint(1, 3)

    bracket_val = a + b
    mul_val = bracket_val * c
    div_val = sp.Rational(d, e)
    result = mul_val - div_val

    expr_str = f"({a} + {b}) × {c} - {d} ÷ {e}"
    teaching_steps = [
        f"BIDMAS tells us the order to work through a mixed expression like {expr_str}: Brackets first, "
        "then Indices, then Division and Multiplication (left to right), then Addition and Subtraction "
        "(left to right).",
        f"There's no power here, so after the brackets we go straight to multiplication/division. "
        f"Brackets: ({a} + {b}) = {bracket_val}.",
        f"Multiplication and division, left to right: {bracket_val} × {c} = {mul_val}, and separately "
        f"{d} ÷ {e} = {fmt_num(div_val)}.",
        f"Finally, subtraction: {mul_val} - {fmt_num(div_val)} = {fmt_num(result)}.",
    ]
    worked_calculation = [
        f"{expr_str}",
        f"= {mul_val} - {fmt_num(div_val)}",
        f"= {fmt_num(result)}",
    ]
    return expr_str, teaching_steps, worked_calculation, result


def _build_teaching_shape_c(rng: random.Random):
    a = rng.randint(2, 9)
    b = rng.randint(2, 9)
    c = rng.randint(2, 9)
    # e is picked first, then d is forced to be a multiple of e, guaranteeing the
    # division step lands on a whole number.
    e = rng.randint(2, 9)
    d = e * rng.randint(1, 3)

    a_sq = a**2
    mul_val = b * c
    div_val = sp.Rational(d, e)
    add_val = a_sq + mul_val
    result = add_val - div_val

    expr_str = f"{a}^2 + {b} × {c} - {d} ÷ {e}"
    teaching_steps = [
        f"BIDMAS tells us the order to work through a mixed expression like {expr_str}: Brackets first, "
        "then Indices, then Division and Multiplication (left to right), then Addition and Subtraction "
        "(left to right).",
        f"There are no brackets this time, so start with indices: {a}^2 = {a_sq}.",
        f"Next, multiplication and division, left to right: {b} × {c} = {mul_val}, and separately "
        f"{d} ÷ {e} = {fmt_num(div_val)}.",
        f"Finally, addition and subtraction, left to right: {a_sq} + {mul_val} = {add_val}, then "
        f"{add_val} - {fmt_num(div_val)} = {fmt_num(result)}.",
    ]
    worked_calculation = [
        f"{expr_str}",
        f"= {a_sq} + {mul_val} - {fmt_num(div_val)}",
        f"= {add_val} - {fmt_num(div_val)}",
        f"= {fmt_num(result)}",
    ]
    return expr_str, teaching_steps, worked_calculation, result


def _build_teaching_shape_d(rng: random.Random):
    a = rng.randint(10, 30)
    # c is picked first, then b is forced to be a multiple of c, guaranteeing the
    # division step lands on a whole number.
    c = rng.randint(2, 9)
    b = c * rng.randint(1, 3)
    d = rng.randint(1, 9)
    e = rng.randint(1, 9)

    bracket_val = d + e
    div_val = sp.Rational(b, c)
    div_mul_val = div_val * bracket_val
    result = a - div_mul_val

    expr_str = f"{a} - {b} ÷ {c} × ({d} + {e})"
    teaching_steps = [
        f"BIDMAS tells us the order to work through a mixed expression like {expr_str}: Brackets first, "
        "then Indices, then Division and Multiplication (left to right), then Addition and Subtraction "
        "(left to right).",
        f"Start with the brackets: ({d} + {e}) = {bracket_val}.",
        f"Division and multiplication have EQUAL priority, so - unlike brackets/indices/addition/"
        f"subtraction, which each have their own single step - when both appear together they're worked "
        f"left to right, in the order they're written: first {b} ÷ {c} = {fmt_num(div_val)}, then "
        f"× {bracket_val} = {fmt_num(div_mul_val)}.",
        f"Finally, subtraction: {a} - {fmt_num(div_mul_val)} = {fmt_num(result)}.",
    ]
    worked_calculation = [
        f"{expr_str}",
        f"= {a} - {fmt_num(div_val)} × {bracket_val}",
        f"= {a} - {fmt_num(div_mul_val)}",
        f"= {fmt_num(result)}",
    ]
    return expr_str, teaching_steps, worked_calculation, result


_TEACHING_SHAPE_BUILDERS = [
    _build_teaching_shape_a,
    _build_teaching_shape_b,
    _build_teaching_shape_c,
    _build_teaching_shape_d,
]


def generate_modelled_example_bidmas(tier: Tier, rng: random.Random) -> ModelledExample:
    builder = rng.choice(_TEACHING_SHAPE_BUILDERS)
    expr_str, teaching_steps, worked_calculation, result = builder(rng)

    # Independent verification: evaluate the same expression a second, genuinely different
    # way - via sympy's own parser and operator-precedence rules - rather than the manual
    # BIDMAS step-by-step evaluation used to build `result`/`worked_calculation` above.
    sympy_val = sp.sympify(_to_sympy_str(expr_str))
    if sp.simplify(sympy_val - result) != 0:
        raise ValueError(f"modelled example bidmas verification failed for expression: {expr_str}")

    return ModelledExample(
        topic_id="bidmas",
        tier=Tier.FOUNDATION,
        prompt=f"Work out {expr_str}. Use the correct order of operations.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=fmt_num(result),
    )


TOPIC_BIDMAS = TopicDefinition(
    id="bidmas",
    display_name="Order of Operations (BIDMAS)",
    description="Evaluate an expression combining brackets, indices, and the four operations using the correct order of operations.",
    generate=generate_bidmas,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_bidmas,
)
