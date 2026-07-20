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


MODELLED_EXAMPLE_GENERATORS = [
    (quadratic_graphs.generate_modelled_example_completing_the_square, Tier.HIGHER, "completing_the_square"),
    (quadratic_graphs.generate_modelled_example_turning_point, Tier.HIGHER, "turning_point_of_graph"),
]


def test_all_topics_have_modelled_example_wired():
    for t in (quadratic_graphs.TOPIC_COMPLETING_THE_SQUARE, quadratic_graphs.TOPIC_TURNING_POINT):
        assert t.generate_modelled_example is not None


def test_modelled_example_generators_produce_verified_examples():
    for generate, tier, topic_id in MODELLED_EXAMPLE_GENERATORS:
        rng = random.Random(230)
        for _ in range(TRIALS):
            example = generate(tier, rng)
            assert example.topic_id == topic_id
            assert example.prompt
            assert len(example.worked_calculation) >= 2
            assert len(example.teaching_steps) >= 3
            assert example.final_answer


def test_modelled_example_turning_point_has_a_parabola_diagram():
    rng = random.Random(231)
    for _ in range(TRIALS):
        example = quadratic_graphs.generate_modelled_example_turning_point(Tier.HIGHER, rng)
        assert example.diagram is not None
        assert example.diagram.kind == "parabola"
        assert example.diagram.params["vertex_label"] == example.final_answer
