import random

import sympy as sp
from sympy.parsing.sympy_parser import (
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

from app.core.models import Tier
from app.topics import simplify_expressions

TRIALS = 300

_TRANSFORMS = standard_transformations + (implicit_multiplication_application,)


def test_generator_produces_valid_verified_questions():
    rng = random.Random(510)
    for _ in range(TRIALS):
        q = simplify_expressions.generate_collect_like_terms(Tier.FOUNDATION, rng)
        assert q.tier == Tier.FOUNDATION
        assert q.topic_id == "collect_like_terms_F"
        assert q.prompt and q.solution_steps and q.final_answer


def test_dedup_keys_vary():
    rng = random.Random(511)
    keys = {simplify_expressions.generate_collect_like_terms(Tier.FOUNDATION, rng).dedup_key for _ in range(200)}
    assert len(keys) > 100


def test_answer_is_algebraically_equivalent_to_the_prompt():
    """Parse both the prompt expression and the stated answer with sympy and
    confirm they are the same expression - an independent check of the answer."""
    x, a, b = sp.symbols("x a b")
    local = {"x": x, "a": a, "b": b}
    rng = random.Random(512)
    for _ in range(TRIALS):
        q = simplify_expressions.generate_collect_like_terms(Tier.FOUNDATION, rng)
        prompt_expr = q.prompt.split(" ", 2)[-1] if q.prompt.startswith("Fully") else q.prompt.split(" ", 1)[-1]
        prompt_expr = prompt_expr.replace("^", "**")
        answer_expr = q.final_answer.replace("^", "**")
        parsed_prompt = parse_expr(prompt_expr, local_dict=local, transformations=_TRANSFORMS)
        parsed_answer = parse_expr(answer_expr, local_dict=local, transformations=_TRANSFORMS)
        assert sp.expand(parsed_prompt - parsed_answer) == 0


def test_modelled_example_is_verified():
    rng = random.Random(513)
    for _ in range(TRIALS):
        ex = simplify_expressions.generate_modelled_example_collect_like_terms(Tier.FOUNDATION, rng)
        assert ex.topic_id == "collect_like_terms_F"
        assert len(ex.worked_calculation) >= 2
        assert len(ex.teaching_steps) >= 3
        assert ex.final_answer


def test_topic_metadata():
    t = simplify_expressions.TOPIC_COLLECT_LIKE_TERMS
    assert t.section == "algebra"
    assert t.fixed_tier == Tier.FOUNDATION
    assert t.generate_modelled_example is not None
