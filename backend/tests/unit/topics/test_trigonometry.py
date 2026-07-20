import random

from app.core.models import Tier
from app.topics import trigonometry

TRIALS = 200

GENERATORS = [
    (trigonometry.generate_missing_side_foundation, Tier.FOUNDATION),
    (trigonometry.generate_missing_side_higher, Tier.HIGHER),
    (trigonometry.generate_missing_angle_foundation, Tier.FOUNDATION),
    (trigonometry.generate_missing_angle_higher, Tier.HIGHER),
    (trigonometry.generate_mixed, Tier.HIGHER),
]

MODELLED_EXAMPLE_GENERATORS = [
    (trigonometry.generate_modelled_example_missing_side_foundation, Tier.FOUNDATION, "trig_missing_side_foundation"),
    (trigonometry.generate_modelled_example_missing_side_higher, Tier.HIGHER, "trig_missing_side_higher"),
    (trigonometry.generate_modelled_example_missing_angle_foundation, Tier.FOUNDATION, "trig_missing_angle_foundation"),
    (trigonometry.generate_modelled_example_missing_angle_higher, Tier.HIGHER, "trig_missing_angle_higher"),
    (trigonometry.generate_modelled_example_mixed, Tier.HIGHER, "trig_mixed"),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(70)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer
            assert q.diagram is not None
            assert q.diagram.kind == "trig_triangle"


def test_foundation_side_never_requires_rearranging():
    rng = random.Random(71)
    for _ in range(TRIALS):
        q = trigonometry.generate_missing_side_foundation(Tier.FOUNDATION, rng)
        # The Foundation shape set (hyp_opp, hyp_adj, adj_opp) never has the
        # hypotenuse as the unknown, so a student never needs to rearrange the
        # ratio - the unknown is always a straightforward multiplication.
        assert q.diagram.params["hyp_label"] != "x cm"


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(72)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 30


def test_topic_definitions_have_expected_metadata():
    topics = [
        trigonometry.TOPIC_MISSING_SIDE_FOUNDATION,
        trigonometry.TOPIC_MISSING_SIDE_HIGHER,
        trigonometry.TOPIC_MISSING_ANGLE_FOUNDATION,
        trigonometry.TOPIC_MISSING_ANGLE_HIGHER,
        trigonometry.TOPIC_MIXED,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 5
    for t in topics:
        assert t.section == "geometry"
        assert t.group == "Trigonometry"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)


def test_topic_definitions_have_modelled_examples_wired_up():
    topics = [
        trigonometry.TOPIC_MISSING_SIDE_FOUNDATION,
        trigonometry.TOPIC_MISSING_SIDE_HIGHER,
        trigonometry.TOPIC_MISSING_ANGLE_FOUNDATION,
        trigonometry.TOPIC_MISSING_ANGLE_HIGHER,
        trigonometry.TOPIC_MIXED,
    ]
    for t in topics:
        assert t.generate_modelled_example is not None


def test_modelled_examples_produce_valid_verified_examples():
    for generate, tier, topic_id in MODELLED_EXAMPLE_GENERATORS:
        rng = random.Random(73)
        for _ in range(TRIALS):
            example = generate(tier, rng)
            assert example.topic_id == topic_id
            assert example.tier == tier
            assert example.prompt
            assert len(example.worked_calculation) >= 2
            assert len(example.teaching_steps) >= 3
            assert example.final_answer
            assert example.diagram is not None
            assert example.diagram.kind == "trig_triangle"
