import random

from app.core.models import Tier
from app.topics import statistics as stats_topic

TRIALS = 200

GENERATORS = [
    (stats_topic.generate_mean, Tier.FOUNDATION),
    (stats_topic.generate_mode, Tier.FOUNDATION),
    (stats_topic.generate_median, Tier.FOUNDATION),
    (stats_topic.generate_range, Tier.FOUNDATION),
    (stats_topic.generate_averages_combined, Tier.FOUNDATION),
    (stats_topic.generate_interquartile_range, Tier.HIGHER),
    (stats_topic.generate_mean_frequency_table, Tier.FOUNDATION),
    (stats_topic.generate_mode_frequency_table, Tier.FOUNDATION),
    (stats_topic.generate_median_frequency_table, Tier.FOUNDATION),
    (stats_topic.generate_range_frequency_table, Tier.FOUNDATION),
    (stats_topic.generate_mean_grouped_frequency_table, Tier.HIGHER),
    (stats_topic.generate_mean_grouped_frequency_table_foundation, Tier.FOUNDATION),
    (stats_topic.generate_reverse_mean, Tier.HIGHER),
    (stats_topic.generate_reverse_mean_foundation, Tier.FOUNDATION),
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


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(82)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 50


def test_topic_definitions_have_expected_metadata():
    topics = [
        stats_topic.TOPIC_MEAN,
        stats_topic.TOPIC_MODE,
        stats_topic.TOPIC_MEDIAN,
        stats_topic.TOPIC_RANGE,
        stats_topic.TOPIC_AVERAGES_COMBINED,
        stats_topic.TOPIC_INTERQUARTILE_RANGE,
        stats_topic.TOPIC_MEAN_FREQUENCY_TABLE,
        stats_topic.TOPIC_MODE_FREQUENCY_TABLE,
        stats_topic.TOPIC_MEDIAN_FREQUENCY_TABLE,
        stats_topic.TOPIC_RANGE_FREQUENCY_TABLE,
        stats_topic.TOPIC_MEAN_GROUPED_FREQUENCY_TABLE,
        stats_topic.TOPIC_MEAN_GROUPED_FREQUENCY_TABLE_FOUNDATION,
        stats_topic.TOPIC_REVERSE_MEAN,
        stats_topic.TOPIC_REVERSE_MEAN_FOUNDATION,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 14
    for t in topics:
        assert t.section == "statistics"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)
    assert stats_topic.TOPIC_INTERQUARTILE_RANGE.fixed_tier == Tier.HIGHER
    assert stats_topic.TOPIC_MEAN_GROUPED_FREQUENCY_TABLE_FOUNDATION.fixed_tier == Tier.FOUNDATION
    assert stats_topic.TOPIC_REVERSE_MEAN_FOUNDATION.fixed_tier == Tier.FOUNDATION


def test_modelled_example_definitions_are_wired():
    topics = [
        stats_topic.TOPIC_MEAN,
        stats_topic.TOPIC_MODE,
        stats_topic.TOPIC_MEDIAN,
        stats_topic.TOPIC_RANGE,
        stats_topic.TOPIC_AVERAGES_COMBINED,
        stats_topic.TOPIC_INTERQUARTILE_RANGE,
        stats_topic.TOPIC_MEAN_FREQUENCY_TABLE,
        stats_topic.TOPIC_MODE_FREQUENCY_TABLE,
        stats_topic.TOPIC_MEDIAN_FREQUENCY_TABLE,
        stats_topic.TOPIC_RANGE_FREQUENCY_TABLE,
        stats_topic.TOPIC_MEAN_GROUPED_FREQUENCY_TABLE,
        stats_topic.TOPIC_MEAN_GROUPED_FREQUENCY_TABLE_FOUNDATION,
        stats_topic.TOPIC_REVERSE_MEAN,
        stats_topic.TOPIC_REVERSE_MEAN_FOUNDATION,
    ]
    for t in topics:
        assert t.generate_modelled_example is not None


def test_modelled_example_mean_produces_verified_examples():
    rng = random.Random(220)
    for _ in range(TRIALS):
        example = stats_topic.generate_modelled_example_mean(Tier.FOUNDATION, rng)
        assert example.topic_id == "stats_mean_F"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_mode_produces_verified_examples():
    rng = random.Random(221)
    for _ in range(TRIALS):
        example = stats_topic.generate_modelled_example_mode(Tier.FOUNDATION, rng)
        assert example.topic_id == "stats_mode_F"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_median_produces_verified_examples():
    rng = random.Random(222)
    for _ in range(TRIALS):
        example = stats_topic.generate_modelled_example_median(Tier.FOUNDATION, rng)
        assert example.topic_id == "stats_median_F"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_range_produces_verified_examples():
    rng = random.Random(223)
    for _ in range(TRIALS):
        example = stats_topic.generate_modelled_example_range(Tier.FOUNDATION, rng)
        assert example.topic_id == "stats_range_F"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_averages_combined_produces_verified_examples():
    rng = random.Random(224)
    for _ in range(TRIALS):
        example = stats_topic.generate_modelled_example_averages_combined(Tier.FOUNDATION, rng)
        assert example.topic_id == "stats_averages_combined_F"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_interquartile_range_produces_verified_examples():
    rng = random.Random(225)
    for _ in range(TRIALS):
        example = stats_topic.generate_modelled_example_interquartile_range(Tier.HIGHER, rng)
        assert example.topic_id == "stats_interquartile_range_H"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_mean_frequency_table_produces_verified_examples():
    rng = random.Random(207)
    for _ in range(TRIALS):
        example = stats_topic.generate_modelled_example_mean_frequency_table(Tier.FOUNDATION, rng)
        assert example.topic_id == "stats_mean_frequency_table_F"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_mode_frequency_table_produces_verified_examples():
    rng = random.Random(226)
    for _ in range(TRIALS):
        example = stats_topic.generate_modelled_example_mode_frequency_table(Tier.FOUNDATION, rng)
        assert example.topic_id == "stats_mode_frequency_table_F"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_median_frequency_table_produces_verified_examples():
    rng = random.Random(227)
    for _ in range(TRIALS):
        example = stats_topic.generate_modelled_example_median_frequency_table(Tier.FOUNDATION, rng)
        assert example.topic_id == "stats_median_frequency_table_F"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_range_frequency_table_produces_verified_examples():
    rng = random.Random(228)
    for _ in range(TRIALS):
        example = stats_topic.generate_modelled_example_range_frequency_table(Tier.FOUNDATION, rng)
        assert example.topic_id == "stats_range_frequency_table_F"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_mean_grouped_frequency_table_produces_verified_examples():
    rng = random.Random(208)
    for _ in range(TRIALS):
        example = stats_topic.generate_modelled_example_mean_grouped_frequency_table(Tier.HIGHER, rng)
        assert example.topic_id == "stats_mean_grouped_frequency_table_H"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_reverse_mean_produces_verified_examples():
    rng = random.Random(209)
    for _ in range(TRIALS):
        example = stats_topic.generate_modelled_example_reverse_mean(Tier.HIGHER, rng)
        assert example.topic_id == "stats_reverse_mean_H"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_mean_grouped_frequency_table_foundation_produces_verified_examples():
    rng = random.Random(210)
    for _ in range(TRIALS):
        example = stats_topic.generate_modelled_example_mean_grouped_frequency_table_foundation(
            Tier.FOUNDATION, rng
        )
        assert example.topic_id == "stats_mean_grouped_frequency_table_F"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_reverse_mean_foundation_produces_verified_examples():
    rng = random.Random(211)
    for _ in range(TRIALS):
        example = stats_topic.generate_modelled_example_reverse_mean_foundation(Tier.FOUNDATION, rng)
        assert example.topic_id == "stats_reverse_mean_F"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_frequency_table_topics_vary_their_context_not_just_pets():
    # Real user report: these 6 topics were always "pets"/"runners" - no
    # context pool at all. Confirm genuine variety now exists.
    generators = [
        stats_topic.generate_mean_frequency_table,
        stats_topic.generate_mode_frequency_table,
        stats_topic.generate_median_frequency_table,
        stats_topic.generate_range_frequency_table,
    ]
    rng = random.Random(3001)
    prompts = {gen.__name__: {gen(Tier.FOUNDATION, rng).prompt for _ in range(40)} for gen in generators}
    for name, seen in prompts.items():
        assert len(seen) > 1, f"{name} produced only one distinct prompt across 40 trials"

    rng2 = random.Random(3002)
    grouped_prompts = {stats_topic.generate_mean_grouped_frequency_table(Tier.HIGHER, rng2).prompt for _ in range(40)}
    assert len(grouped_prompts) > 1


def test_frequency_table_diagrams_have_a_titled_value_column():
    rng = random.Random(3003)
    q = stats_topic.generate_mean_frequency_table(Tier.FOUNDATION, rng)
    assert q.diagram.params["corner_label"].startswith("Number of ")
    rng2 = random.Random(3004)
    q2 = stats_topic.generate_mean_grouped_frequency_table(Tier.HIGHER, rng2)
    assert q2.diagram.params["corner_label"]
