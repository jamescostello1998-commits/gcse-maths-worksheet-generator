import math
import random

from app.core.models import Tier
from app.topics import circle_equation

TRIALS = 300

GENERATORS = [
    (circle_equation.generate_circle_equation, Tier.HIGHER),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(900)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer
            assert q.diagram is not None
            assert q.diagram.kind == "loci_construction"
            assert q.diagram.params["circle"]["centre"] == (0, 0)


def test_tangent_line_is_genuinely_tangent_to_the_circle():
    # Independent re-check (distance from origin to the claimed tangent line
    # equals the circle's radius), separate from the generator's own
    # verification, using the actual returned final_answer string.
    rng = random.Random(901)
    seen_tangent = False
    for _ in range(TRIALS):
        q = circle_equation.generate_circle_equation(Tier.HIGHER, rng)
        if "tangent" not in q.prompt:
            continue
        seen_tangent = True
        # final_answer looks like "3x + 4y = 25" or "3x - 4y = 25"
        lhs, rhs = q.final_answer.split("=")
        r_sq = float(rhs.strip())
        parts = lhs.replace("-", "+-").split("+")
        coeffs = {}
        for part in parts:
            part = part.strip()
            if not part:
                continue
            if part.endswith("x"):
                coeffs["a"] = float(part[:-1] or "1")
            elif part.endswith("y"):
                coeffs["b"] = float(part[:-1].replace(" ", "") or "1")
        a, b = coeffs["a"], coeffs["b"]
        distance = abs(r_sq) / math.hypot(a, b)
        r = math.sqrt(r_sq)
        assert abs(distance - r) < 1e-6
    assert seen_tangent


def test_dedup_keys_vary_widely():
    rng = random.Random(902)
    keys = {circle_equation.generate_circle_equation(Tier.HIGHER, rng).dedup_key for _ in range(TRIALS)}
    assert len(keys) > 50


def test_topic_definition_metadata():
    t = circle_equation.TOPIC_CIRCLE_EQUATION
    assert t.id == "circle_equation"
    assert t.section == "algebra"
    assert t.group == "Equation of a Circle"
    assert t.fixed_tier == Tier.HIGHER
    assert t.generate_modelled_example is not None


def test_modelled_examples_are_valid():
    rng = random.Random(903)
    for _ in range(TRIALS):
        ex = circle_equation.generate_modelled_example_circle_equation(Tier.HIGHER, rng)
        assert ex.topic_id == "circle_equation"
        assert ex.tier == Tier.HIGHER
        assert ex.prompt
        assert len(ex.worked_calculation) >= 2
        assert len(ex.teaching_steps) >= 3
        assert ex.final_answer
