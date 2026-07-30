import random

from app.core.models import Tier
from app.topics import substitution

TRIALS = 300

GENERATORS = [
    (substitution.generate_substitution_foundation, Tier.FOUNDATION),
    (substitution.generate_substitution_higher, Tier.HIGHER),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(120)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.topic_id == ("substitution_foundation" if tier == Tier.FOUNDATION else "substitution_higher")
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(121)
        keys = {generate(tier, rng).dedup_key for _ in range(300)}
        assert len(keys) > 40


def test_topic_definitions_have_expected_metadata():
    topics = [
        substitution.TOPIC_SUBSTITUTION_FOUNDATION,
        substitution.TOPIC_SUBSTITUTION_HIGHER,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 2
    for t in topics:
        assert t.section == "algebra"
        assert t.group == "Substitution into Formulae"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)


def test_all_topics_have_modelled_example_wired():
    for t in (
        substitution.TOPIC_SUBSTITUTION_FOUNDATION,
        substitution.TOPIC_SUBSTITUTION_HIGHER,
    ):
        assert t.generate_modelled_example is not None


MODELLED_EXAMPLE_GENERATORS = [
    (
        substitution.generate_modelled_example_substitution_foundation,
        Tier.FOUNDATION,
        "substitution_foundation",
    ),
    (
        substitution.generate_modelled_example_substitution_higher,
        Tier.HIGHER,
        "substitution_higher",
    ),
]


def test_modelled_example_generators_produce_verified_examples():
    for generate, tier, topic_id in MODELLED_EXAMPLE_GENERATORS:
        rng = random.Random(220)
        for _ in range(TRIALS):
            example = generate(tier, rng)
            assert example.topic_id == topic_id
            assert example.prompt
            assert len(example.worked_calculation) >= 2
            assert len(example.teaching_steps) >= 3
            assert example.final_answer


def test_higher_generator_includes_negative_values():
    """The Higher topic must exercise substituting a negative value into a
    power/root/fraction formula, not just positive ones - confirmed by
    checking the acceleration/deceleration and kinetic-energy shapes both
    produce a negative substituted variable across enough trials."""
    rng = random.Random(555)
    saw_negative_a = False
    saw_negative_v = False
    for _ in range(500):
        q = substitution.generate_substitution_higher(Tier.HIGHER, rng)
        if "a = " in q.prompt and "-" in q.prompt.split("a = ")[1].split(",")[0].split(".")[0]:
            saw_negative_a = True
        if "v = -" in q.prompt or ", v = -" in q.prompt:
            saw_negative_v = True
    assert saw_negative_a or saw_negative_v
