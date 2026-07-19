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
