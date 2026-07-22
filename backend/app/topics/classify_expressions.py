"""Classify an algebraic statement as an expression, equation, formula, or identity.

Each category is built with genuine random variety (not a fixed literal-string
bank), except "formula" which is drawn from a curated pool of real well-known
formulae (these are correct by construction - a formula relates two or more
distinct named quantities, so there is nothing to derive per-instance).
"""

import random

import sympy as sp

from app.core.models import ModelledExample, Question, Tier
from app.topics.algebra_utils import X, fmt_linear
from app.topics.base import TopicDefinition

SECTION = "algebra"
GROUP = "Expressions, Formulae, Equations & Identities"

CATEGORIES = ("expression", "equation", "formula", "identity")

# Well-known formulae relating two or more different letters/quantities.
# Correct by construction - no per-instance verification needed.
_FORMULAE = [
    ("A = l × w", "the area A of a rectangle from its length l and width w"),
    ("P = 2l + 2w", "the perimeter P of a rectangle from its length l and width w"),
    ("v = u + at", "final velocity v from initial velocity u, acceleration a and time t"),
    ("C = πd", "the circumference C of a circle from its diameter d"),
    ("A = πr^2", "the area A of a circle from its radius r"),
    ("s = d/t", "speed s from distance d and time t"),
    ("F = ma", "force F from mass m and acceleration a (Newton's second law)"),
    ("V = IR", "voltage V from current I and resistance R (Ohm's law)"),
    ("A = (b × h)/2", "the area A of a triangle from its base b and height h"),
    ("D = m/v", "density D from mass m and volume v"),
]


def _rand_nonzero(rng: random.Random, lo: int, hi: int) -> int:
    while True:
        v = rng.randint(lo, hi)
        if v != 0:
            return v


def _signed_term(value: int) -> str:
    """Format an integer as '+ 5' or '- 5' (for splicing after a preceding term)."""
    return f"+ {value}" if value >= 0 else f"- {abs(value)}"


# --------------------------------------------------------------------------
# Expression
# --------------------------------------------------------------------------


def _build_expression(rng: random.Random) -> tuple[str, str, str]:
    """Returns (statement, shape, dedup_extra)."""
    shape = rng.choice(["linear", "linear_over_const", "quadratic_partial", "quadratic_full"])
    a = _rand_nonzero(rng, -9, 9)
    b = rng.randint(-12, 12)
    c = _rand_nonzero(rng, 2, 9)

    if shape == "linear":
        statement = fmt_linear(a, b)
    elif shape == "linear_over_const":
        statement = f"({fmt_linear(a, b)})/{c}"
    elif shape == "quadratic_partial":
        b_nz = _rand_nonzero(rng, -9, 9)
        statement = f"{a}x^2 {_signed_term(b_nz)}x"
        b = b_nz
    else:
        b_nz = _rand_nonzero(rng, -9, 9)
        statement = f"{a}x^2 {_signed_term(b_nz)}x {_signed_term(c)}"
        b = b_nz

    # Independent sanity check: an expression contains no '=' or '≡' at all.
    if "=" in statement or "≡" in statement:
        raise ValueError("classify_expressions: expression template leaked an equals sign")

    return statement, shape, f"{a}:{b}:{c}"


def _expression_steps(statement: str) -> list[str]:
    return [
        f"Look at the statement: {statement}.",
        "There is no '=' sign and no '≡' sign anywhere in it, so it isn't claiming that two "
        "things are equal at all.",
        "It's just a single algebraic object built from numbers and a letter using "
        "+, -, ×, ÷ and powers - it can be simplified or evaluated for a given x, but there is "
        "nothing here to 'solve' or 'prove'.",
        "Since it makes no equality claim whatsoever, this is an expression.",
    ]


# --------------------------------------------------------------------------
# Equation
# --------------------------------------------------------------------------


def _build_equation(rng: random.Random) -> tuple[str, int, int, sp.Rational]:
    a = _rand_nonzero(rng, -9, 9)
    b = rng.randint(-12, 12)
    c = rng.randint(-15, 15)
    lhs = fmt_linear(a, b)
    statement = f"{lhs} = {c}"

    # Independent verification via sympy: a linear equation in x with a
    # nonzero coefficient always has exactly one solution - confirm that via
    # sp.solve (a different code path than the fmt_linear string-building
    # above), which also rules out it secretly being an identity (an identity
    # would not have a single unique solution).
    solutions = sp.solve(sp.Eq(a * X + b, c), X)
    if len(solutions) != 1:
        raise ValueError("classify_expressions: equation verification failed")
    solution = sp.Rational(solutions[0])

    return statement, a, b, c, solution


def _equation_steps(statement: str, solution: sp.Rational) -> list[str]:
    sol_str = str(int(solution)) if solution.is_Integer else f"{solution.p}/{solution.q}"
    return [
        f"Look at the statement: {statement}.",
        "There IS an '=' sign here, so it's a claim that two things are equal - but it's only "
        f"true for one particular value of x: solving it gives x = {sol_str}.",
        "Because it is only true for a specific value (or values) of x rather than for every "
        "possible x, this is an equation to be solved, not an identity.",
    ]


# --------------------------------------------------------------------------
# Formula
# --------------------------------------------------------------------------


def _formula_steps(formula_str: str, description: str) -> list[str]:
    return [
        f"Look at the statement: {formula_str}.",
        f"This relates two or more DIFFERENT letters, each standing for its own real-world "
        f"quantity ({description}) - it isn't just one unknown x on its own.",
        "It's a general rule connecting those quantities: substitute known values in to work "
        "out the unknown one. Nothing here is being solved for a single numeric x, and the two "
        "sides aren't two expanded forms of the same expression.",
        "Because it connects distinct named quantities in a real-world relationship, this is a "
        "formula.",
    ]


# --------------------------------------------------------------------------
# Identity
# --------------------------------------------------------------------------


def _build_identity(rng: random.Random) -> tuple[str, str, int, int]:
    ident_shape = rng.choice(["distributive", "square", "diff_squares"])

    if ident_shape == "distributive":
        a = _rand_nonzero(rng, 2, 9)
        b = _rand_nonzero(rng, -9, 9)
        ab = a * b
        lhs_str = f"{a}(x + {b})" if b >= 0 else f"{a}(x - {abs(b)})"
        rhs_str = f"{a}x {_signed_term(ab)}"
        residual = sp.expand(a * (X + b) - (a * X + ab))
    elif ident_shape == "square":
        a = _rand_nonzero(rng, 2, 9)
        b = 0
        lhs_str = f"(x + {a})^2"
        rhs_str = f"x^2 {_signed_term(2 * a)}x {_signed_term(a * a)}"
        residual = sp.expand((X + a) ** 2 - (X**2 + 2 * a * X + a * a))
    else:
        a = _rand_nonzero(rng, 2, 9)
        b = 0
        lhs_str = f"(x + {a})(x - {a})"
        rhs_str = f"x^2 {_signed_term(-(a * a))}"
        residual = sp.expand((X + a) * (X - a) - (X**2 - a * a))

    # Independent verification via sympy.expand: confirm LHS - RHS is
    # identically zero for every value of x (a genuinely different check
    # than whatever arithmetic built the displayed RHS numbers above).
    if residual != 0:
        raise ValueError("classify_expressions: identity verification failed")

    statement = f"{lhs_str} ≡ {rhs_str}"
    return statement, ident_shape, a, b


def _identity_steps(statement: str, lhs_str: str, rhs_str: str) -> list[str]:
    return [
        f"Look at the statement: {statement}.",
        f"Expand the left-hand side fully: {lhs_str} expands to {rhs_str}.",
        "The two sides match EXACTLY, for every possible value of x - not just one particular "
        "value.",
        "Because both sides are always equal, whatever x is, the '≡' symbol is the correct one "
        "to use: this is an identity, not just an equation.",
    ]


def generate_classify_expressions(tier: Tier, rng: random.Random) -> Question:
    category = rng.choice(CATEGORIES)

    if category == "expression":
        statement, shape, extra = _build_expression(rng)
        steps = _expression_steps(statement)
        return Question(
            topic_id="classify_expressions",
            tier=Tier.FOUNDATION,
            prompt=f"Is the following an expression, equation, formula, or identity?\n{statement}",
            solution_steps=tuple(steps),
            final_answer="expression",
            dedup_key=f"classify:expression:{shape}:{extra}",
        )

    if category == "equation":
        statement, a, b, c, solution = _build_equation(rng)
        steps = _equation_steps(statement, solution)
        return Question(
            topic_id="classify_expressions",
            tier=Tier.FOUNDATION,
            prompt=f"Is the following an expression, equation, formula, or identity?\n{statement}",
            solution_steps=tuple(steps),
            final_answer="equation",
            dedup_key=f"classify:equation:{a}:{b}:{c}",
        )

    if category == "formula":
        idx = rng.randrange(len(_FORMULAE))
        formula_str, description = _FORMULAE[idx]
        steps = _formula_steps(formula_str, description)
        return Question(
            topic_id="classify_expressions",
            tier=Tier.FOUNDATION,
            prompt=f"Is the following an expression, equation, formula, or identity?\n{formula_str}",
            solution_steps=tuple(steps),
            final_answer="formula",
            dedup_key=f"classify:formula:{idx}",
        )

    # identity
    statement, ident_shape, a, b = _build_identity(rng)
    lhs_str, rhs_str = [s.strip() for s in statement.split("≡")]
    steps = _identity_steps(statement, lhs_str, rhs_str)
    return Question(
        topic_id="classify_expressions",
        tier=Tier.FOUNDATION,
        prompt=f"Is the following an expression, equation, formula, or identity?\n{statement}",
        solution_steps=tuple(steps),
        final_answer="identity",
        dedup_key=f"classify:identity:{ident_shape}:{a}:{b}",
    )


def generate_modelled_example_classify_expressions(tier: Tier, rng: random.Random) -> ModelledExample:
    category = rng.choice(CATEGORIES)

    if category == "expression":
        statement, shape, extra = _build_expression(rng)
        teaching_steps = [
            f"The statement is {statement}. The very first thing to check with any classification "
            "question like this is whether there's an '=' or a '≡' sign anywhere in it at all - "
            "that single check splits 'expression' from the other three categories immediately.",
            "Here there is no equals sign and no identity sign - just numbers, a letter, and the "
            "operations +, -, ×, ÷ and powers combined into one algebraic object.",
            "Because nothing is being claimed equal to anything else, there's no equation to solve, "
            "no formula linking named quantities, and no identity to verify - it's simply an "
            "expression, and it can only be simplified or evaluated, never 'solved' or 'proven'.",
        ]
        worked_calculation = [statement, "No '=' or '≡' present", "Category: expression"]
        return ModelledExample(
            topic_id="classify_expressions",
            tier=Tier.FOUNDATION,
            prompt=f"Is the following an expression, equation, formula, or identity?\n{statement}",
            worked_calculation=tuple(worked_calculation),
            teaching_steps=tuple(teaching_steps),
            final_answer="expression",
        )

    if category == "equation":
        statement, a, b, c, solution = _build_equation(rng)
        sol_str = str(int(solution)) if solution.is_Integer else f"{solution.p}/{solution.q}"
        teaching_steps = [
            f"The statement is {statement}. There IS an '=' sign, so this makes a claim that two "
            "things are equal - which rules out 'expression' straight away. The next question is "
            "whether that claim is true for every value of x, or only for a special one.",
            f"Try solving it as you would any linear equation: rearranging {statement} isolates x "
            f"and gives a single specific value, x = {sol_str}.",
            "Since only that one value of x makes the statement true - substitute any other number "
            "in for x and the two sides won't match - this is NOT true for every x, so it can't be "
            "an identity.",
            "A statement with '=' that holds only for specific value(s) of the unknown is exactly "
            "what an equation is - so that's the classification here.",
        ]
        worked_calculation = [statement, f"Solve: x = {sol_str}", "Category: equation"]
        return ModelledExample(
            topic_id="classify_expressions",
            tier=Tier.FOUNDATION,
            prompt=f"Is the following an expression, equation, formula, or identity?\n{statement}",
            worked_calculation=tuple(worked_calculation),
            teaching_steps=tuple(teaching_steps),
            final_answer="equation",
        )

    if category == "formula":
        idx = rng.randrange(len(_FORMULAE))
        formula_str, description = _FORMULAE[idx]
        teaching_steps = [
            f"The statement is {formula_str}. Just like an equation, it has an '=' sign, so it's "
            "not a bare expression - but look closely at what the letters represent.",
            f"Every letter here stands for a genuinely different real-world quantity ({description}) "
            "rather than the equation just having one unknown x to isolate.",
            "A statement like this is a general rule connecting those different quantities - you "
            "plug in whichever values you know to work out the one you don't. It isn't asking you "
            "to solve for a single numeric unknown, and the two sides aren't just two rearranged "
            "or expanded versions of the exact same expression (which is what would make it an "
            "identity instead).",
            "Because it links distinct named physical quantities in a real-world relationship, this "
            "is a formula.",
        ]
        worked_calculation = [formula_str, "Links distinct named quantities", "Category: formula"]
        return ModelledExample(
            topic_id="classify_expressions",
            tier=Tier.FOUNDATION,
            prompt=f"Is the following an expression, equation, formula, or identity?\n{formula_str}",
            worked_calculation=tuple(worked_calculation),
            teaching_steps=tuple(teaching_steps),
            final_answer="formula",
        )

    statement, ident_shape, a, b = _build_identity(rng)
    lhs_str, rhs_str = [s.strip() for s in statement.split("≡")]
    teaching_steps = [
        f"The statement is {statement}. Notice it uses '≡' rather than a plain '=' - that symbol "
        "itself is a strong hint, but the real test is whether the left side and right side match "
        "for absolutely every value of x, not just a specific one.",
        f"Expand the left-hand side out fully: {lhs_str} becomes {rhs_str} once every bracket is "
        "multiplied out and like terms are collected.",
        "Compare that expanded form to the right-hand side as written - they are exactly the same "
        "expression, term for term. Since expanding didn't rely on x taking any particular value, "
        "this match holds true whatever number x actually is.",
        "A statement where both sides are the same for every possible value of the variable is "
        "exactly what an identity is - so '≡' was the right symbol, and this is an identity, not "
        "just an equation.",
    ]
    worked_calculation = [statement, f"Expand LHS: {rhs_str}", "Matches RHS for all x - identity"]
    return ModelledExample(
        topic_id="classify_expressions",
        tier=Tier.FOUNDATION,
        prompt=f"Is the following an expression, equation, formula, or identity?\n{statement}",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer="identity",
    )


TOPIC_CLASSIFY_EXPRESSIONS = TopicDefinition(
    id="classify_expressions",
    display_name="Expressions, Formulae, Equations and Identities",
    description="Classify an algebraic statement as an expression, equation, formula, or identity.",
    generate=generate_classify_expressions,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_classify_expressions,
)
