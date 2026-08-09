import random

from app.core.models import Tier
from app.topics import exact_trig_values

TRIALS = 200

GENERATORS = [
    (exact_trig_values.generate_exact_trig_values, Tier.HIGHER),
    (exact_trig_values.generate_exact_trig_values_triangles, Tier.HIGHER),
]

MODELLED_EXAMPLE_GENERATORS = [
    (exact_trig_values.generate_modelled_example_exact_trig_values, Tier.HIGHER, "exact_trig_values_H"),
    (exact_trig_values.generate_modelled_example_exact_trig_values_triangles, Tier.HIGHER, "exact_trig_values_triangles_H"),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(310)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_exact_trig_values_has_no_diagram():
    rng = random.Random(311)
    for _ in range(TRIALS):
        q = exact_trig_values.generate_exact_trig_values(Tier.HIGHER, rng)
        assert q.diagram is None
        assert q.final_answer in {
            exact_trig_values._fmt_exact(*v) for v in exact_trig_values.EXACT_VALUES.values()
        }


def test_exact_trig_values_triangles_has_trig_triangle_diagram():
    rng = random.Random(312)
    for _ in range(TRIALS):
        q = exact_trig_values.generate_exact_trig_values_triangles(Tier.HIGHER, rng)
        assert q.diagram is not None
        assert q.diagram.kind == "trig_triangle"
        assert q.diagram.params["angle_label"] in {"30°", "45°", "60°"}


def test_dedup_keys_vary_per_generator():
    # Topic 1's variety is exactly the size of the exact-value lookup table
    # (14 (ratio, angle) combinations) - the natural ceiling for a small
    # enumerable space, not a combinatorial random range.
    rng = random.Random(313)
    keys = {exact_trig_values.generate_exact_trig_values(Tier.HIGHER, rng).dedup_key for _ in range(300)}
    assert len(keys) == len(exact_trig_values.EXACT_VALUES)

    rng2 = random.Random(314)
    keys2 = {exact_trig_values.generate_exact_trig_values_triangles(Tier.HIGHER, rng2).dedup_key for _ in range(300)}
    assert len(keys2) > 50


def test_topic_definitions_have_expected_metadata():
    topics = [
        exact_trig_values.TOPIC_EXACT_TRIG_VALUES,
        exact_trig_values.TOPIC_EXACT_TRIG_VALUES_TRIANGLES,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 2
    for t in topics:
        assert t.section == "geometry"
        assert t.group == "Trigonometry"
        assert t.fixed_tier == Tier.HIGHER
        assert t.generate_modelled_example is not None
    assert exact_trig_values.TOPIC_EXACT_TRIG_VALUES.question_count == len(exact_trig_values.EXACT_VALUES)


def test_modelled_example_generators_produce_verified_examples():
    for generate, tier, topic_id in MODELLED_EXAMPLE_GENERATORS:
        rng = random.Random(320)
        for _ in range(TRIALS):
            example = generate(tier, rng)
            assert example.topic_id == topic_id
            assert example.prompt
            assert len(example.worked_calculation) >= 2
            assert len(example.teaching_steps) >= 3
            assert example.final_answer
