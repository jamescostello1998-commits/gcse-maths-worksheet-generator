import random

from app.core.models import Tier
from app.topics import triangle_rules

TRIALS = 200

GENERATORS = [
    (triangle_rules.generate_sine_rule, Tier.HIGHER),
    (triangle_rules.generate_cosine_rule, Tier.HIGHER),
    (triangle_rules.generate_triangle_area, Tier.HIGHER),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(80)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer
            assert q.diagram is not None
            assert q.diagram.kind == "general_triangle"


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(81)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 30


def test_topic_definitions_have_expected_metadata():
    topics = [
        triangle_rules.TOPIC_SINE_RULE,
        triangle_rules.TOPIC_COSINE_RULE,
        triangle_rules.TOPIC_TRIANGLE_AREA,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 3
    for t in topics:
        assert t.section == "geometry"
        assert t.fixed_tier == Tier.HIGHER
    assert triangle_rules.TOPIC_SINE_RULE.group == "Sine Rule"
    assert triangle_rules.TOPIC_COSINE_RULE.group == "Cosine Rule"
    assert triangle_rules.TOPIC_TRIANGLE_AREA.group == "Area of a Triangle"
