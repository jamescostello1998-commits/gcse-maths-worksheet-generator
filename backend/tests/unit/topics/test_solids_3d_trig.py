import math
import random

from app.core.models import Tier
from app.topics import solids_3d_trig

TRIALS = 200

GENERATORS = [
    (solids_3d_trig.generate_3d_pythagoras, Tier.HIGHER),
    (solids_3d_trig.generate_3d_trigonometry, Tier.HIGHER),
]

MODELLED_EXAMPLE_GENERATORS = [
    (solids_3d_trig.generate_modelled_example_3d_pythagoras, Tier.HIGHER, "pythagoras_3d"),
    (solids_3d_trig.generate_modelled_example_3d_trigonometry, Tier.HIGHER, "trig_3d"),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(410)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer
            assert q.diagram is not None
            assert q.diagram.kind == "cuboid"
            assert "diagonal_label" in q.diagram.params


def test_3d_pythagoras_answer_format():
    rng = random.Random(411)
    for _ in range(TRIALS):
        q = solids_3d_trig.generate_3d_pythagoras(Tier.HIGHER, rng)
        assert q.final_answer.endswith(" cm")


def test_3d_trigonometry_answer_format():
    rng = random.Random(412)
    for _ in range(TRIALS):
        q = solids_3d_trig.generate_3d_trigonometry(Tier.HIGHER, rng)
        assert q.final_answer.endswith("°")


def test_cuboid_dims_never_have_a_perfect_square_diagonal():
    # Confirms the reroll invariant actually holds across many generations,
    # not just "usually" - re-derives l, w, h from each question's dedup_key.
    rng = random.Random(413)
    for _ in range(300):
        q = solids_3d_trig.generate_3d_pythagoras(Tier.HIGHER, rng)
        _, l, w, h = q.dedup_key.split(":")
        l, w, h = int(l), int(w), int(h)
        sum_sq = l * l + w * w + h * h
        assert math.isqrt(sum_sq) ** 2 != sum_sq

    rng2 = random.Random(414)
    for _ in range(300):
        q = solids_3d_trig.generate_3d_trigonometry(Tier.HIGHER, rng2)
        _, l, w, h = q.dedup_key.split(":")
        l, w, h = int(l), int(w), int(h)
        sum_sq = l * l + w * w + h * h
        assert math.isqrt(sum_sq) ** 2 != sum_sq


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(415)
        keys = {generate(tier, rng).dedup_key for _ in range(300)}
        assert len(keys) > 100


def test_topic_definitions_have_expected_metadata():
    topics = [
        solids_3d_trig.TOPIC_3D_PYTHAGORAS,
        solids_3d_trig.TOPIC_3D_TRIGONOMETRY,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 2
    for t in topics:
        assert t.section == "geometry"
        assert t.fixed_tier == Tier.HIGHER
        assert t.generate_modelled_example is not None
    assert solids_3d_trig.TOPIC_3D_PYTHAGORAS.group == "Pythagoras' Theorem"
    assert solids_3d_trig.TOPIC_3D_TRIGONOMETRY.group == "Trigonometry"


def test_modelled_example_generators_produce_verified_examples():
    for generate, tier, topic_id in MODELLED_EXAMPLE_GENERATORS:
        rng = random.Random(420)
        for _ in range(TRIALS):
            example = generate(tier, rng)
            assert example.topic_id == topic_id
            assert example.prompt
            assert len(example.worked_calculation) >= 2
            assert len(example.teaching_steps) >= 3
            assert example.final_answer
