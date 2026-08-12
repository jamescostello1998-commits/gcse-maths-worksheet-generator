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
        topic_id="bidmas_F",
        tier=Tier.FOUNDATION,
        prompt=f"Work out {expr_str}.",
        solution_steps=tuple(steps),
        final_answer=fmt_num(result),
        dedup_key=dedup_key,
    )


# --- Simpler 2-or-3-operation shapes (the "BIDMAS (2 or 3 operations)" topic) -
# The shapes above (generate_bidmas) all combine 4-5 operations; these use only
# two or three, as a gentler introduction to the order of operations. Every
# division is set up to land on a whole number and every subtraction to stay
# non-negative, matching how real Foundation worksheets phrase these.


def _simple_mul_add(rng: random.Random):
    """a + b × c  (2 operations)."""
    a, b, c = rng.randint(1, 20), rng.randint(2, 9), rng.randint(2, 9)
    mul = b * c
    result = a + mul
    expr = f"{a} + {b} × {c}"
    steps = [f"Multiplication: {b} × {c} = {mul}", f"Addition: {a} + {mul} = {result}"]
    return expr, steps, sp.Integer(result), f"bidmas_s:muladd:{a}:{b}:{c}"


def _simple_mul_sub(rng: random.Random):
    """a × b - c  (2 operations)."""
    a, b = rng.randint(2, 9), rng.randint(2, 9)
    mul = a * b
    c = rng.randint(1, mul)
    result = mul - c
    expr = f"{a} × {b} - {c}"
    steps = [f"Multiplication: {a} × {b} = {mul}", f"Subtraction: {mul} - {c} = {result}"]
    return expr, steps, sp.Integer(result), f"bidmas_s:mulsub:{a}:{b}:{c}"


def _simple_div_add(rng: random.Random):
    """a + b ÷ c  (2 operations), b a multiple of c."""
    a, c = rng.randint(1, 20), rng.randint(2, 9)
    b = c * rng.randint(2, 6)
    div = b // c
    result = a + div
    expr = f"{a} + {b} ÷ {c}"
    steps = [f"Division: {b} ÷ {c} = {div}", f"Addition: {a} + {div} = {result}"]
    return expr, steps, sp.Integer(result), f"bidmas_s:divadd:{a}:{b}:{c}"


def _simple_index_add(rng: random.Random):
    """a^2 + b  (2 operations)."""
    a, b = rng.randint(2, 9), rng.randint(1, 20)
    sq = a * a
    result = sq + b
    expr = f"{a}^2 + {b}"
    steps = [f"Indices: {a}^2 = {sq}", f"Addition: {sq} + {b} = {result}"]
    return expr, steps, sp.Integer(result), f"bidmas_s:idxadd:{a}:{b}"


def _simple_bracket_mul(rng: random.Random):
    """(a + b) × c  (2 operations)."""
    a, b, c = rng.randint(1, 9), rng.randint(1, 9), rng.randint(2, 9)
    br = a + b
    result = br * c
    expr = f"({a} + {b}) × {c}"
    steps = [f"Brackets: ({a} + {b}) = {br}", f"Multiplication: {br} × {c} = {result}"]
    return expr, steps, sp.Integer(result), f"bidmas_s:brmul:{a}:{b}:{c}"


def _simple_mul_add_sub(rng: random.Random):
    """a + b × c - d  (3 operations)."""
    a, b, c = rng.randint(1, 15), rng.randint(2, 9), rng.randint(2, 9)
    mul = b * c
    d = rng.randint(1, a + mul)
    result = a + mul - d
    expr = f"{a} + {b} × {c} - {d}"
    steps = [
        f"Multiplication: {b} × {c} = {mul}",
        f"Addition and subtraction, left to right: {a} + {mul} = {a + mul}, then - {d} = {result}",
    ]
    return expr, steps, sp.Integer(result), f"bidmas_s:muladdsub:{a}:{b}:{c}:{d}"


def _simple_index_mul_add(rng: random.Random):
    """a^2 + b × c  (3 operations)."""
    a, b, c = rng.randint(2, 7), rng.randint(2, 9), rng.randint(2, 9)
    sq = a * a
    mul = b * c
    result = sq + mul
    expr = f"{a}^2 + {b} × {c}"
    steps = [
        f"Indices: {a}^2 = {sq}",
        f"Multiplication: {b} × {c} = {mul}",
        f"Addition: {sq} + {mul} = {result}",
    ]
    return expr, steps, sp.Integer(result), f"bidmas_s:idxmuladd:{a}:{b}:{c}"


def _simple_bracket_mul_sub(rng: random.Random):
    """(a + b) × c - d  (3 operations)."""
    a, b, c = rng.randint(1, 9), rng.randint(1, 9), rng.randint(2, 9)
    br = a + b
    mul = br * c
    d = rng.randint(1, mul)
    result = mul - d
    expr = f"({a} + {b}) × {c} - {d}"
    steps = [
        f"Brackets: ({a} + {b}) = {br}",
        f"Multiplication: {br} × {c} = {mul}",
        f"Subtraction: {mul} - {d} = {result}",
    ]
    return expr, steps, sp.Integer(result), f"bidmas_s:brmulsub:{a}:{b}:{c}:{d}"


def _simple_bracket_sub_mul_add(rng: random.Random):
    """a + b × (c - d)  (3 operations)."""
    a, b, c = rng.randint(1, 20), rng.randint(2, 9), rng.randint(2, 9)
    d = rng.randint(1, c - 1)
    br = c - d
    mul = b * br
    result = a + mul
    expr = f"{a} + {b} × ({c} - {d})"
    steps = [
        f"Brackets: ({c} - {d}) = {br}",
        f"Multiplication: {b} × {br} = {mul}",
        f"Addition: {a} + {mul} = {result}",
    ]
    return expr, steps, sp.Integer(result), f"bidmas_s:brsubmuladd:{a}:{b}:{c}:{d}"


_SIMPLE_SHAPE_BUILDERS = [
    _simple_mul_add, _simple_mul_sub, _simple_div_add, _simple_index_add, _simple_bracket_mul,
    _simple_mul_add_sub, _simple_index_mul_add, _simple_bracket_mul_sub, _simple_bracket_sub_mul_add,
]


def generate_bidmas_simple(tier: Tier, rng: random.Random) -> Question:
    builder = rng.choice(_SIMPLE_SHAPE_BUILDERS)
    expr_str, steps, result, dedup_key = builder(rng)

    # Independent verification via sympy's own parser/precedence, as generate_bidmas does.
    sympy_val = sp.sympify(_to_sympy_str(expr_str))
    if sp.simplify(sympy_val - result) != 0:
        raise ValueError(f"bidmas_simple verification failed for expression: {expr_str}")

    return Question(
        topic_id="bidmas_two_three_F",
        tier=Tier.FOUNDATION,
        prompt=f"Work out {expr_str}.",
        solution_steps=tuple(steps),
        final_answer=fmt_num(result),
        dedup_key=dedup_key,
    )


def _simple_teach_mul_add(rng: random.Random):
    a, b, c = rng.randint(1, 20), rng.randint(2, 9), rng.randint(2, 9)
    mul = b * c
    result = a + mul
    expr = f"{a} + {b} × {c}"
    teaching = [
        "BIDMAS gives the order to work through an expression: Brackets, Indices, Division and "
        "Multiplication (left to right), then Addition and Subtraction (left to right).",
        f"In {expr} there are no brackets or indices, so the multiplication is done before the addition.",
        f"Multiplication first: {b} × {c} = {mul}.",
        f"Then the addition: {a} + {mul} = {result}.",
    ]
    worked = [expr, f"= {a} + {mul}", f"= {result}"]
    return expr, teaching, worked, sp.Integer(result)


def _simple_teach_bracket_mul_sub(rng: random.Random):
    a, b, c = rng.randint(1, 9), rng.randint(1, 9), rng.randint(2, 9)
    br = a + b
    mul = br * c
    d = rng.randint(1, mul)
    result = mul - d
    expr = f"({a} + {b}) × {c} - {d}"
    teaching = [
        "BIDMAS gives the order to work through an expression: Brackets, Indices, Division and "
        "Multiplication (left to right), then Addition and Subtraction (left to right).",
        f"Do the brackets first: ({a} + {b}) = {br}.",
        f"Then the multiplication: {br} × {c} = {mul}.",
        f"Finally the subtraction: {mul} - {d} = {result}.",
    ]
    worked = [expr, f"= {mul} - {d}", f"= {result}"]
    return expr, teaching, worked, sp.Integer(result)


def _simple_teach_index_mul_add(rng: random.Random):
    a, b, c = rng.randint(2, 7), rng.randint(2, 9), rng.randint(2, 9)
    sq = a * a
    mul = b * c
    result = sq + mul
    expr = f"{a}^2 + {b} × {c}"
    teaching = [
        "BIDMAS gives the order to work through an expression: Brackets, Indices, Division and "
        "Multiplication (left to right), then Addition and Subtraction (left to right).",
        f"There are no brackets, so start with the index: {a}^2 = {sq}.",
        f"Then the multiplication: {b} × {c} = {mul}.",
        f"Finally the addition: {sq} + {mul} = {result}.",
    ]
    worked = [expr, f"= {sq} + {mul}", f"= {result}"]
    return expr, teaching, worked, sp.Integer(result)


_SIMPLE_TEACHING_BUILDERS = [_simple_teach_mul_add, _simple_teach_bracket_mul_sub, _simple_teach_index_mul_add]


def generate_modelled_example_bidmas_simple(tier: Tier, rng: random.Random) -> ModelledExample:
    builder = rng.choice(_SIMPLE_TEACHING_BUILDERS)
    expr_str, teaching_steps, worked_calculation, result = builder(rng)

    sympy_val = sp.sympify(_to_sympy_str(expr_str))
    if sp.simplify(sympy_val - result) != 0:
        raise ValueError(f"modelled example bidmas_simple verification failed for expression: {expr_str}")

    return ModelledExample(
        topic_id="bidmas_two_three_F",
        tier=Tier.FOUNDATION,
        prompt=f"Work out {expr_str}.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=fmt_num(result),
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
        topic_id="bidmas_F",
        tier=Tier.FOUNDATION,
        prompt=f"Work out {expr_str}.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=fmt_num(result),
    )


TOPIC_BIDMAS_SIMPLE = TopicDefinition(
    id="bidmas_two_three_F",
    display_name="BIDMAS (2 or 3 operations)",
    description="Evaluate an expression using two or three operations in the correct order (BIDMAS).",
    generate=generate_bidmas_simple,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_bidmas_simple,
)


TOPIC_BIDMAS = TopicDefinition(
    id="bidmas_F",
    display_name="BIDMAS (4+ operations)",
    description="Evaluate an expression combining brackets, indices, and the four operations (four or more operations) using the correct order of operations.",
    generate=generate_bidmas,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_bidmas,
)
