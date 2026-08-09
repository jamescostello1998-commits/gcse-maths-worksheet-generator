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
    (pythagoras.generate_ladder_context_foundation, Tier.FOUNDATION),
]

MODELLED_EXAMPLE_GENERATORS = [
    (pythagoras.generate_modelled_example_hypotenuse_triple, Tier.FOUNDATION, "pythagoras_hypotenuse_triple_F"),
    (pythagoras.generate_modelled_example_hypotenuse_decimal, Tier.FOUNDATION, "pythagoras_hypotenuse_decimal_F"),
    (pythagoras.generate_modelled_example_shorter_leg, Tier.FOUNDATION, "pythagoras_shorter_leg_F"),
    (pythagoras.generate_modelled_example_surd_hypotenuse, Tier.HIGHER, "pythagoras_surd_hypotenuse_H"),
    (pythagoras.generate_modelled_example_ladder_context, Tier.HIGHER, "pythagoras_ladder_context_H"),
    (
        pythagoras.generate_modelled_example_ladder_context_foundation,
        Tier.FOUNDATION,
        "pythagoras_ladder_context_F",
    ),
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
    # The two ladder-context generators deliberately have NO diagram (text
    # only, per direct user request) - excluded from this check.
    ladder_generators = {pythagoras.generate_ladder_context, pythagoras.generate_ladder_context_foundation}
    for generate, tier in GENERATORS:
        if generate in ladder_generators:
            continue
        rng = random.Random(61)
        q = generate(tier, rng)
        assert q.diagram is not None
        assert q.diagram.kind == "right_triangle"
        labels = [q.diagram.params["leg1_label"], q.diagram.params["leg2_label"], q.diagram.params["hyp_label"]]
        assert labels.count("x") == 1


def test_ladder_context_generators_have_no_diagram():
    for generate, tier in [
        (pythagoras.generate_ladder_context, Tier.HIGHER),
        (pythagoras.generate_ladder_context_foundation, Tier.FOUNDATION),
    ]:
        rng = random.Random(61)
        for _ in range(50):
            q = generate(tier, rng)
            assert q.diagram is None


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
        pythagoras.TOPIC_LADDER_CONTEXT_FOUNDATION,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 6
    for t in topics:
        assert t.section == "geometry"
        assert t.group == "Pythagoras' Theorem"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)
    assert pythagoras.TOPIC_LADDER_CONTEXT_FOUNDATION.fixed_tier == Tier.FOUNDATION


def test_topic_definitions_have_modelled_examples_wired_up():
    topics = [
        pythagoras.TOPIC_HYPOTENUSE_TRIPLE,
        pythagoras.TOPIC_HYPOTENUSE_DECIMAL,
        pythagoras.TOPIC_SHORTER_LEG,
        pythagoras.TOPIC_SURD_HYPOTENUSE,
        pythagoras.TOPIC_LADDER_CONTEXT,
        pythagoras.TOPIC_LADDER_CONTEXT_FOUNDATION,
    ]
    for t in topics:
        assert t.generate_modelled_example is not None


def test_ladder_context_higher_always_gives_a_surd_answer():
    rng = random.Random(64)
    for _ in range(TRIALS):
        q = pythagoras.generate_ladder_context(Tier.HIGHER, rng)
        assert "√" in q.final_answer


def test_ladder_context_foundation_always_gives_a_whole_number_answer():
    rng = random.Random(65)
    for _ in range(TRIALS):
        q = pythagoras.generate_ladder_context_foundation(Tier.FOUNDATION, rng)
        value = q.final_answer.replace(" m", "")
        assert value.isdigit()


def test_modelled_examples_produce_valid_verified_examples():
    # The two ladder-context modelled examples deliberately have NO diagram
    # (text only, per direct user request).
    ladder_topic_ids = {"pythagoras_ladder_context_H", "pythagoras_ladder_context_F"}
    for generate, tier, topic_id in MODELLED_EXAMPLE_GENERATORS:
        rng = random.Random(63)
        for _ in range(TRIALS):
            example = generate(tier, rng)
            assert example.topic_id == topic_id
            assert example.tier == tier
            assert example.prompt
            assert len(example.worked_calculation) >= 2
            assert len(example.teaching_steps) >= 3
            assert example.final_answer
            if topic_id in ladder_topic_ids:
                assert example.diagram is None
                continue
            assert example.diagram is not None
            assert example.diagram.kind == "right_triangle"
            labels = [
                example.diagram.params["leg1_label"],
                example.diagram.params["leg2_label"],
                example.diagram.params["hyp_label"],
            ]
            assert labels.count("x") == 1
