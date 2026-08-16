import random
import re

import sympy as sp
from sympy.parsing.sympy_parser import implicit_multiplication_application, parse_expr, standard_transformations

from app.core.models import Tier
from app.topics import linear_equations

_NEGATIVE_COEFF_RE = re.compile(r"-\s*\d*x\b")
_PARSE_TRANSFORMS = standard_transformations + (implicit_multiplication_application,)

TRIALS = 200

GENERATORS = [
    (linear_equations.generate_one_step, Tier.FOUNDATION),
    (linear_equations.generate_two_step, Tier.FOUNDATION),
    (linear_equations.generate_multi_step, Tier.FOUNDATION),
    (linear_equations.generate_both_sides_foundation, Tier.FOUNDATION),
    (linear_equations.generate_brackets_foundation, Tier.FOUNDATION),
    (linear_equations.generate_both_sides, Tier.HIGHER),
    (linear_equations.generate_brackets, Tier.HIGHER),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(1)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert len(q.solution_steps) >= 2
            assert q.final_answer


def test_final_answer_always_parses_as_rational():
    rng = random.Random(3)
    for generate, tier in GENERATORS:
        for _ in range(TRIALS):
            q = generate(tier, rng)
            parsed = sp.Rational(q.final_answer) if "/" in q.final_answer else sp.Integer(q.final_answer)
            assert parsed.is_rational


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(4)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 50


def test_foundation_generators_never_produce_negative_coefficient():
    # Both linear_one_step_F and linear_two_step_F legitimately include a
    # "... - a = c" subtraction form, so a bare "-" can appear in the LHS -
    # what must never appear (outside two_step's deliberate "sub_first"
    # branch, b - ax = c, checked separately below) is a negative
    # x-COEFFICIENT ("-3x"), which is distinct from a subtracted constant
    # ("x - 11" / "5x - 11").
    rng = random.Random(5)
    for _ in range(TRIALS):
        q = linear_equations.generate_one_step(Tier.FOUNDATION, rng)
        assert not _NEGATIVE_COEFF_RE.search(q.prompt.split("=")[0])

    rng = random.Random(5)
    for _ in range(TRIALS):
        op, _a, _b, disp, *_rest = linear_equations._build_two_step(rng)
        if op == "sub_first":
            continue
        assert not _NEGATIVE_COEFF_RE.search(disp.split("=")[0])


def test_two_step_sub_first_shows_constant_minus_coefficient_x():
    # b - ax = c is only ever written that specific way round (never with
    # the negative coefficient floating elsewhere in the expression).
    rng = random.Random(11)
    seen = False
    for _ in range(TRIALS * 10):
        op, a, b, disp, *_rest = linear_equations._build_two_step(rng)
        if op != "sub_first":
            continue
        seen = True
        lhs = disp.split("=")[0].strip()
        assert lhs == f"{b} - {a}x" or lhs == f"{b} - x"
    assert seen


def test_one_step_covers_all_four_operations_roughly_evenly():
    rng = random.Random(6)
    ops = {"add": 0, "sub": 0, "mul": 0, "div": 0}
    n = 2000
    for _ in range(n):
        op, *_rest = linear_equations._build_one_step(rng)
        ops[op] += 1
    # Each operation is chosen with equal (25%) probability - allow generous
    # slack for random variance rather than pinning an exact count.
    for op, count in ops.items():
        assert n * 0.15 < count < n * 0.35, f"{op} appeared {count}/{n} times"


def test_two_step_covers_all_four_forms_weighted_toward_coefficient_first():
    rng = random.Random(9)
    ops = {"mul_add": 0, "mul_sub": 0, "add_first": 0, "sub_first": 0}
    n = 4000
    for _ in range(n):
        op, *_rest = linear_equations._build_two_step(rng)
        ops[op] += 1
    # All four forms still appear (real variety), but the coefficient-first
    # forms (ax +- b = c) should together dominate over the constant-first
    # forms (b +- ax = c) - see _TWO_STEP_WEIGHTS (40:40:10:10).
    coeff_first = ops["mul_add"] + ops["mul_sub"]
    const_first = ops["add_first"] + ops["sub_first"]
    assert coeff_first > const_first * 3
    for op, count in ops.items():
        assert count > 0, f"{op} never appeared in {n} trials"


def test_both_sides_higher_constant_first_variety_and_correctness():
    # A side is only ever displayed constant-first ("15 - x") when its own
    # coefficient is negative - a positive-coefficient side always stays
    # coefficient-first ("8x - 1"), matching real GCSE convention.
    rng = random.Random(31)
    n = 1500
    swapped_seen = False
    for _ in range(n):
        a, b, c, d, _sol, disp, _steps, _solution, orig_lhs, orig_rhs, _key = (
            linear_equations._build_both_sides(rng)
        )
        lhs_text, rhs_text = disp.split(" = ")
        if lhs_text == linear_equations._fmt_side_constant_first(a, b):
            assert a < 0 and b > 0  # only swapped when coeff<0 AND the constant is positive
            swapped_seen = True
        if rhs_text == linear_equations._fmt_side_constant_first(c, d):
            assert c < 0 and d > 0
            swapped_seen = True
        # Whatever the display order, it must describe the true equation.
        parsed_lhs = parse_expr(lhs_text, transformations=_PARSE_TRANSFORMS, local_dict={"x": sp.Symbol("x")})
        parsed_rhs = parse_expr(rhs_text, transformations=_PARSE_TRANSFORMS, local_dict={"x": sp.Symbol("x")})
        assert sp.simplify(parsed_lhs - orig_lhs) == 0
        assert sp.simplify(parsed_rhs - orig_rhs) == 0
    assert swapped_seen


def test_multi_step_never_starts_negative_but_coeff2_sometimes_is():
    rng = random.Random(13)
    n = 1000
    negative_coeff2_seen = False
    leading_terms = set()
    for _ in range(n):
        (
            coeff1, coeff2, _const1, _const2, _sol, combined_coeff, _combined_const, _c,
            lhs_str, _prompt, _steps, _solution, _orig_lhs, _orig_rhs, _key,
        ) = linear_equations._build_multi_step(rng)
        assert not lhs_str.startswith("-")
        assert combined_coeff > 0
        assert coeff1 > 0
        if coeff2 < 0:
            negative_coeff2_seen = True
        leading_terms.add(lhs_str.split(" ")[0])
    assert negative_coeff2_seen
    # Real order variety: the leading term isn't always the same value.
    assert len(leading_terms) > 5


def test_brackets_foundation_has_negative_inside_and_swapped_order_variety():
    rng = random.Random(17)
    n = 1500
    negative_inside_seen = False
    swapped_seen = False
    for _ in range(n):
        a, b, c, d, _sol, _bracket_str, disp, _steps, _solution, _lhs, _rhs, _key = (
            linear_equations._build_brackets_foundation(rng)
        )
        assert b > 0  # never a negative coefficient
        assert d > 0
        if c < 0:
            negative_inside_seen = True
        if disp.startswith(f"{d} = "):
            swapped_seen = True
    assert negative_inside_seen
    assert swapped_seen


def test_brackets_higher_more_double_than_single_and_fewer_negative_answers():
    rng = random.Random(23)
    n = 2000
    shapes = {"single": 0, "double": 0}
    negative_sol = 0
    for _ in range(n):
        shape, _disp, _pre, _solve, solution, *_rest = linear_equations._build_brackets(rng)
        shapes[shape] += 1
        if solution < 0:
            negative_sol += 1
    # Double-bracket should clearly dominate (~70/30 per direct user request).
    assert shapes["double"] > shapes["single"] * 1.5
    # Negative answers should be a clear minority now (~20%, was ~50%).
    assert negative_sol < n * 0.3


def test_brackets_double_expand_and_collect_steps_are_mathematically_correct():
    # Regression test for a real bug: the "Expand both brackets"/"Collect like
    # terms" DISPLAY text for the subtraction case ("a(...) - e(...)") only
    # flipped the sign of the second bracket's x-term, not its constant too
    # (e.g. showed "...- 12x + 42" when the true expansion is "...- 12x - 42").
    # The final numeric answer was always correct (computed independently of
    # the display string), so this class of bug is invisible to any check
    # that only looks at the final answer - it has to compare the displayed
    # expression's own mathematical meaning against the true original one.
    rng = random.Random(29)
    checked = 0
    for _ in range(600):
        shape, disp, pre_steps, solve_steps, solution, orig_lhs, orig_rhs, key = linear_equations._build_brackets(
            rng
        )
        if shape != "double":
            continue
        checked += 1
        expand_rhs_text = pre_steps[0].split(" = ", 1)[1]
        collect_lhs_text = pre_steps[1].split(" = ", 1)[0].removeprefix("Collect like terms: ")
        for text in (expand_rhs_text, collect_lhs_text):
            parsed = parse_expr(text, transformations=_PARSE_TRANSFORMS, local_dict={"x": sp.Symbol("x")})
            assert sp.simplify(parsed - orig_lhs) == 0, f"{text!r} does not match the true expression"
    assert checked > 100


def test_topic_definitions_have_expected_metadata():
    topics = [
        linear_equations.TOPIC_ONE_STEP,
        linear_equations.TOPIC_TWO_STEP,
        linear_equations.TOPIC_MULTI_STEP,
        linear_equations.TOPIC_BOTH_SIDES_FOUNDATION,
        linear_equations.TOPIC_BRACKETS_FOUNDATION,
        linear_equations.TOPIC_BOTH_SIDES,
        linear_equations.TOPIC_BRACKETS,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 7
    for t in topics:
        assert t.section == "algebra"
        assert t.group == "Solving Linear Equations"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)


def test_all_topics_have_modelled_example_wired():
    topics = [
        linear_equations.TOPIC_ONE_STEP,
        linear_equations.TOPIC_TWO_STEP,
        linear_equations.TOPIC_MULTI_STEP,
        linear_equations.TOPIC_BOTH_SIDES_FOUNDATION,
        linear_equations.TOPIC_BRACKETS_FOUNDATION,
        linear_equations.TOPIC_BOTH_SIDES,
        linear_equations.TOPIC_BRACKETS,
    ]
    for t in topics:
        assert t.generate_modelled_example is not None


MODELLED_EXAMPLE_GENERATORS = [
    (linear_equations.generate_modelled_example_one_step, Tier.FOUNDATION, "linear_one_step_F"),
    (linear_equations.generate_modelled_example_two_step, Tier.FOUNDATION, "linear_two_step_F"),
    (linear_equations.generate_modelled_example_multi_step, Tier.FOUNDATION, "linear_multi_step_F"),
    (
        linear_equations.generate_modelled_example_both_sides_foundation,
        Tier.FOUNDATION,
        "linear_both_sides_F",
    ),
    (
        linear_equations.generate_modelled_example_brackets_foundation,
        Tier.FOUNDATION,
        "linear_brackets_F",
    ),
    (linear_equations.generate_modelled_example_both_sides, Tier.HIGHER, "linear_both_sides_H"),
    (linear_equations.generate_modelled_example_brackets, Tier.HIGHER, "linear_brackets_H"),
]


def test_modelled_example_generators_produce_verified_examples():
    for generate_modelled_example, tier, topic_id in MODELLED_EXAMPLE_GENERATORS:
        rng = random.Random(201)
        for _ in range(TRIALS):
            example = generate_modelled_example(tier, rng)
            assert example.topic_id == topic_id
            assert example.prompt
            assert len(example.worked_calculation) >= 2
            assert len(example.teaching_steps) >= 3
            assert example.final_answer
