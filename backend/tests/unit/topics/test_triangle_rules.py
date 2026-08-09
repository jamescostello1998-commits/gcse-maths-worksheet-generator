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


MODELLED_TOPICS = [
    triangle_rules.TOPIC_SINE_RULE,
    triangle_rules.TOPIC_COSINE_RULE,
    triangle_rules.TOPIC_TRIANGLE_AREA,
]

MODELLED_GENERATORS = [
    (triangle_rules.generate_modelled_example_sine_rule, Tier.HIGHER, "sine_rule_H"),
    (triangle_rules.generate_modelled_example_cosine_rule, Tier.HIGHER, "cosine_rule_H"),
    (triangle_rules.generate_modelled_example_triangle_area, Tier.HIGHER, "triangle_area_sine_rule_H"),
]


def test_topics_have_a_modelled_example_generator_wired_up():
    for t in MODELLED_TOPICS:
        assert t.generate_modelled_example is not None


def test_decimal_topics_reach_all_three_rounding_phrasings():
    """sine_rule/cosine_rule only reach pick_rounding via their "side" shape
    (the "angle" shape always states 1 d.p., a genuine angle answer excluded
    from pick_rounding by design - see rounding.py's own docstring); triangle_area
    always reaches it. 400 trials per generator comfortably covers the ~50%
    chance of landing on the "side" shape for sine_rule/cosine_rule."""
    generators = [
        triangle_rules.generate_sine_rule,
        triangle_rules.generate_cosine_rule,
        triangle_rules.generate_triangle_area,
    ]
    phrasings = {"1 decimal place", "2 decimal places", "3 significant figures"}
    for generate in generators:
        rng = random.Random(850)
        seen = set()
        for _ in range(400):
            q = generate(Tier.HIGHER, rng)
            seen |= {p for p in phrasings if p in q.prompt}
        assert seen == phrasings


def test_modelled_examples_are_valid():
    for generate, tier, topic_id in MODELLED_GENERATORS:
        rng = random.Random(200)
        for _ in range(TRIALS):
            ex = generate(tier, rng)
            assert ex.topic_id == topic_id
            assert ex.tier == tier
            assert ex.prompt
            assert len(ex.worked_calculation) >= 2
            assert len(ex.teaching_steps) >= 3
            assert ex.final_answer
            assert ex.diagram is not None
            assert ex.diagram.kind == "general_triangle"
