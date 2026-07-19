import random

from app.core.models import Tier
from app.topics import quadratic_graphs

TRIALS = 200

GENERATORS = [
    (quadratic_graphs.generate_completing_the_square, Tier.HIGHER),
    (quadratic_graphs.generate_turning_point, Tier.HIGHER),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(130)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_turning_point_has_a_parabola_diagram():
    rng = random.Random(131)
    for _ in range(TRIALS):
        q = quadratic_graphs.generate_turning_point(Tier.HIGHER, rng)
        assert q.diagram is not None
        assert q.diagram.kind == "parabola"
        assert q.diagram.params["vertex_label"] == q.final_answer


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(132)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 40


def test_topic_definitions_have_expected_metadata():
    topics = [quadratic_graphs.TOPIC_COMPLETING_THE_SQUARE, quadratic_graphs.TOPIC_TURNING_POINT]
    ids = {t.id for t in topics}
    assert len(ids) == 2
    for t in topics:
        assert t.section == "algebra"
        assert t.fixed_tier == Tier.HIGHER
    assert quadratic_graphs.TOPIC_COMPLETING_THE_SQUARE.group == "Completing the Square"
    assert quadratic_graphs.TOPIC_TURNING_POINT.group == "Turning Point of a Graph"
