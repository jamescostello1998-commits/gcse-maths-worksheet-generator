import random

from app.core.models import Tier
from app.topics import simultaneous_equations

TRIALS = 200

GENERATORS = [
    (simultaneous_equations.generate_common_coefficient, Tier.FOUNDATION),
    (simultaneous_equations.generate_different_coefficient, Tier.HIGHER),
    (simultaneous_equations.generate_forming_and_solving, Tier.FOUNDATION),
    (simultaneous_equations.generate_simultaneous_quadratic, Tier.HIGHER),
    (simultaneous_equations.generate_simultaneous_graphically, Tier.FOUNDATION),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(140)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_graphically_diagram_does_not_reveal_the_answer():
    rng = random.Random(141)
    for _ in range(TRIALS):
        q = simultaneous_equations.generate_simultaneous_graphically(Tier.FOUNDATION, rng)
        assert q.diagram is not None
        assert q.diagram.kind == "linear_graph_pair"
        assert q.diagram.params["intersection_label"] == "?"


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(142)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 40


def test_topic_definitions_have_expected_metadata():
    topics = [
        simultaneous_equations.TOPIC_COMMON_COEFFICIENT,
        simultaneous_equations.TOPIC_DIFFERENT_COEFFICIENT,
        simultaneous_equations.TOPIC_FORMING_AND_SOLVING,
        simultaneous_equations.TOPIC_QUADRATIC,
        simultaneous_equations.TOPIC_GRAPHICALLY,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 5
    for t in topics:
        assert t.section == "algebra"
        assert t.group == "Simultaneous Equations"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)


MODELLED_EXAMPLE_GENERATORS = [
    (simultaneous_equations.generate_modelled_example_common_coefficient, Tier.FOUNDATION, "simultaneous_common_coefficient"),
    (simultaneous_equations.generate_modelled_example_different_coefficient, Tier.HIGHER, "simultaneous_different_coefficient"),
    (simultaneous_equations.generate_modelled_example_forming_and_solving, Tier.FOUNDATION, "simultaneous_forming_and_solving"),
    (simultaneous_equations.generate_modelled_example_simultaneous_quadratic, Tier.HIGHER, "simultaneous_quadratic"),
    (simultaneous_equations.generate_modelled_example_simultaneous_graphically, Tier.FOUNDATION, "simultaneous_graphically"),
]


def test_all_topics_have_modelled_example_wired():
    topics = [
        simultaneous_equations.TOPIC_COMMON_COEFFICIENT,
        simultaneous_equations.TOPIC_DIFFERENT_COEFFICIENT,
        simultaneous_equations.TOPIC_FORMING_AND_SOLVING,
        simultaneous_equations.TOPIC_QUADRATIC,
        simultaneous_equations.TOPIC_GRAPHICALLY,
    ]
    for t in topics:
        assert t.generate_modelled_example is not None


def test_modelled_example_generators_produce_verified_examples():
    for generate, tier, topic_id in MODELLED_EXAMPLE_GENERATORS:
        rng = random.Random(240)
        for _ in range(TRIALS):
            example = generate(tier, rng)
            assert example.topic_id == topic_id
            assert example.prompt
            assert len(example.worked_calculation) >= 2
            assert len(example.teaching_steps) >= 3
            assert example.final_answer


def test_modelled_example_graphically_diagram_reveals_the_answer():
    rng = random.Random(241)
    for _ in range(TRIALS):
        example = simultaneous_equations.generate_modelled_example_simultaneous_graphically(Tier.FOUNDATION, rng)
        assert example.diagram is not None
        assert example.diagram.kind == "linear_graph_pair"
        assert example.diagram.params["intersection_label"] != "?"
        assert example.diagram.params["intersection_label"].startswith("(")
