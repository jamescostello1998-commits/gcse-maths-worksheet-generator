import random
from fractions import Fraction

from app.core.models import Tier
from app.topics import map_scales

TRIALS = 300

GENERATORS = [
    (map_scales.generate_map_scale_drawings, Tier.FOUNDATION),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(900)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_final_answer_unit_matches_question_direction():
    rng = random.Random(901)
    for _ in range(TRIALS):
        q = map_scales.generate_map_scale_drawings(Tier.FOUNDATION, rng)
        if "Find the real-life distance" in q.prompt:
            assert q.final_answer.endswith(" m") or q.final_answer.endswith(" km")
        else:
            assert q.final_answer.endswith(" cm")
        # The numeric part must be a positive whole number in every case.
        number_part = q.final_answer.rsplit(" ", 1)[0]
        assert number_part.lstrip("-").isdigit()
        assert int(number_part) > 0


def test_dedup_keys_vary_widely():
    rng = random.Random(902)
    keys = {map_scales.generate_map_scale_drawings(Tier.FOUNDATION, rng).dedup_key for _ in range(TRIALS)}
    assert len(keys) > 20


def test_both_scale_kinds_and_both_directions_appear():
    rng = random.Random(903)
    seen_ratio = seen_verbal = seen_map_to_real = seen_real_to_map = False
    for _ in range(TRIALS):
        q = map_scales.generate_map_scale_drawings(Tier.FOUNDATION, rng)
        if "1 :" in q.prompt:
            seen_ratio = True
        if "represents" in q.prompt:
            seen_verbal = True
        if "Find the real-life distance" in q.prompt:
            seen_map_to_real = True
        if "Find the distance between the towns on the map" in q.prompt:
            seen_real_to_map = True
    assert seen_ratio and seen_verbal and seen_map_to_real and seen_real_to_map


def test_topic_definition_metadata():
    t = map_scales.TOPIC_MAP_SCALE_DRAWINGS
    assert t.id == "map_scale_drawings_F"
    assert t.section == "geometry"
    assert t.group == "Map Scales and Scale Drawings"
    assert t.fixed_tier == Tier.FOUNDATION
    assert t.generate_modelled_example is not None


def test_modelled_examples_are_valid():
    rng = random.Random(904)
    for _ in range(TRIALS):
        ex = map_scales.generate_modelled_example_map_scale_drawings(Tier.FOUNDATION, rng)
        assert ex.topic_id == "map_scale_drawings_F"
        assert ex.tier == Tier.FOUNDATION
        assert ex.prompt
        assert len(ex.worked_calculation) >= 2
        assert len(ex.teaching_steps) >= 3
        assert ex.final_answer


def test_build_case_inverse_recovers_original_value():
    # Direct re-check of the cross-multiplication invariant the generator
    # itself already asserts internally: dividing the computed real-world
    # distance by the scale factor must recover the original map distance
    # exactly (and vice versa), via plain Fraction arithmetic.
    rng = random.Random(905)
    for _ in range(TRIALS):
        v = map_scales._build_case(rng)
        scale = v["scale"]
        real_per_cm = scale["real_per_cm"]
        if v["direction"] == "map_to_real":
            recomputed_real = Fraction(v["map_cm"]) * real_per_cm
            assert recomputed_real == Fraction(v["real_value"])
            assert recomputed_real / real_per_cm == Fraction(v["map_cm"])
        else:
            recomputed_map_cm = Fraction(v["real_value"]) / real_per_cm
            assert recomputed_map_cm == Fraction(v["map_cm"])
            assert recomputed_map_cm * real_per_cm == Fraction(v["real_value"])
