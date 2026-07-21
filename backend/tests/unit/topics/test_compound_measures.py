import random

from app.core.models import Tier
from app.topics import compound_measures

TRIALS = 200

GENERATORS = [
    (compound_measures.generate_sdt_mixed, Tier.FOUNDATION),
    (compound_measures.generate_speed_with_conversions, Tier.HIGHER),
    (compound_measures.generate_unit_conversions, Tier.FOUNDATION),
    (compound_measures.generate_unit_conversions_higher, Tier.HIGHER),
    (compound_measures.generate_density, Tier.FOUNDATION),
    (compound_measures.generate_density_higher, Tier.HIGHER),
    (compound_measures.generate_pressure, Tier.FOUNDATION),
    (compound_measures.generate_pressure_higher, Tier.HIGHER),
]


def test_all_generators_produce_valid_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(30)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(32)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 50


def test_topic_definitions_have_expected_metadata():
    topics = [
        compound_measures.TOPIC_SDT_MIXED,
        compound_measures.TOPIC_SPEED_WITH_CONVERSIONS,
        compound_measures.TOPIC_UNIT_CONVERSIONS,
        compound_measures.TOPIC_UNIT_CONVERSIONS_HIGHER,
        compound_measures.TOPIC_DENSITY,
        compound_measures.TOPIC_DENSITY_HIGHER,
        compound_measures.TOPIC_PRESSURE,
        compound_measures.TOPIC_PRESSURE_HIGHER,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 8
    for t in topics:
        assert t.section == "ratio_proportion"
        assert t.group == "Compound Measures"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)
    assert compound_measures.TOPIC_SDT_MIXED.fixed_tier == Tier.FOUNDATION
    assert compound_measures.TOPIC_SPEED_WITH_CONVERSIONS.fixed_tier == Tier.HIGHER
    assert compound_measures.TOPIC_UNIT_CONVERSIONS.fixed_tier == Tier.FOUNDATION
    assert compound_measures.TOPIC_UNIT_CONVERSIONS_HIGHER.fixed_tier == Tier.HIGHER
    assert compound_measures.TOPIC_DENSITY.fixed_tier == Tier.FOUNDATION
    assert compound_measures.TOPIC_DENSITY_HIGHER.fixed_tier == Tier.HIGHER
    assert compound_measures.TOPIC_PRESSURE.fixed_tier == Tier.FOUNDATION
    assert compound_measures.TOPIC_PRESSURE_HIGHER.fixed_tier == Tier.HIGHER


def test_modelled_example_topics_have_generator_wired():
    for t in (
        compound_measures.TOPIC_SDT_MIXED,
        compound_measures.TOPIC_SPEED_WITH_CONVERSIONS,
        compound_measures.TOPIC_UNIT_CONVERSIONS,
        compound_measures.TOPIC_UNIT_CONVERSIONS_HIGHER,
        compound_measures.TOPIC_DENSITY,
        compound_measures.TOPIC_DENSITY_HIGHER,
        compound_measures.TOPIC_PRESSURE,
        compound_measures.TOPIC_PRESSURE_HIGHER,
    ):
        assert t.generate_modelled_example is not None


def test_modelled_example_sdt_mixed_produces_verified_examples():
    rng = random.Random(401)
    for _ in range(TRIALS):
        example = compound_measures.generate_modelled_example_sdt_mixed(Tier.FOUNDATION, rng)
        assert example.topic_id == "sdt_mixed"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_speed_with_conversions_produces_verified_examples():
    rng = random.Random(402)
    for _ in range(TRIALS):
        example = compound_measures.generate_modelled_example_speed_with_conversions(Tier.HIGHER, rng)
        assert example.topic_id == "speed_with_conversions"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_unit_conversions_produces_verified_examples():
    rng = random.Random(403)
    for _ in range(TRIALS):
        example = compound_measures.generate_modelled_example_unit_conversions(Tier.FOUNDATION, rng)
        assert example.topic_id == "unit_conversions"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_unit_conversions_higher_produces_verified_examples():
    rng = random.Random(404)
    for _ in range(TRIALS):
        example = compound_measures.generate_modelled_example_unit_conversions_higher(Tier.HIGHER, rng)
        assert example.topic_id == "unit_conversions_higher"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_density_produces_verified_examples():
    rng = random.Random(405)
    for _ in range(TRIALS):
        example = compound_measures.generate_modelled_example_density(Tier.FOUNDATION, rng)
        assert example.topic_id == "density"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_density_higher_produces_verified_examples():
    rng = random.Random(406)
    for _ in range(TRIALS):
        example = compound_measures.generate_modelled_example_density_higher(Tier.HIGHER, rng)
        assert example.topic_id == "density_higher"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_pressure_produces_verified_examples():
    rng = random.Random(407)
    for _ in range(TRIALS):
        example = compound_measures.generate_modelled_example_pressure(Tier.FOUNDATION, rng)
        assert example.topic_id == "pressure"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_pressure_higher_produces_verified_examples():
    rng = random.Random(408)
    for _ in range(TRIALS):
        example = compound_measures.generate_modelled_example_pressure_higher(Tier.HIGHER, rng)
        assert example.topic_id == "pressure_higher"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer
