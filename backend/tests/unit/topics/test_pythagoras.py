import random

from app.core.models import Tier
from app.topics import pythagoras

TRIALS = 200

GENERATORS = [
    (pythagoras.generate_hypotenuse_triple, Tier.FOUNDATION),
    (pythagoras.generate_hypotenuse_decimal, Tier.FOUNDATION),
    (pythagoras.generate_shorter_leg, Tier.FOUNDATION),
    (pythagoras.generate_surd_hypotenuse, Tier.HIGHER),
    (pythagoras.generate_ladder_context, Tier.HIGHER),
]


def test_all_generators_produce_valid_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(60)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_all_generators_attach_a_right_triangle_diagram_with_exactly_one_unknown():
    for generate, tier in GENERATORS:
        rng = random.Random(61)
        q = generate(tier, rng)
        assert q.diagram is not None
        assert q.diagram.kind == "right_triangle"
        labels = [q.diagram.params["leg1_label"], q.diagram.params["leg2_label"], q.diagram.params["hyp_label"]]
        assert labels.count("?") == 1


def test_simplify_surd():
    assert pythagoras._simplify_surd(50) == (5, 2)
    assert pythagoras._simplify_surd(9) == (3, 1)
    assert pythagoras._simplify_surd(8) == (2, 2)
    assert pythagoras._simplify_surd(7) == (1, 7)


def test_dedup_keys_vary_per_generator():
    # Triple-based generators draw from only 8 primitive triples x a small k range,
    # so this uses a lower bar than other topic files' equivalent test.
    for generate, tier in GENERATORS:
        rng = random.Random(62)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 15


def test_topic_definitions_have_expected_metadata():
    topics = [
        pythagoras.TOPIC_HYPOTENUSE_TRIPLE,
        pythagoras.TOPIC_HYPOTENUSE_DECIMAL,
        pythagoras.TOPIC_SHORTER_LEG,
        pythagoras.TOPIC_SURD_HYPOTENUSE,
        pythagoras.TOPIC_LADDER_CONTEXT,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 5
    for t in topics:
        assert t.section == "geometry"
        assert t.group == "Pythagoras' Theorem"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)
