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
    (solids_3d_trig.generate_modelled_example_3d_pythagoras, Tier.HIGHER, "pythagoras_3d_H"),
    (solids_3d_trig.generate_modelled_example_3d_trigonometry, Tier.HIGHER, "trig_3d_H"),
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
            # The space diagonal is shown as a dashed line with no "?"/"theta"
            # label (the dash indicates it); vertices are labelled a-h.
            assert q.diagram.params.get("show_diagonal") is True
            assert q.diagram.params["vertex_labels"] == ["a", "b", "c", "d", "e", "f", "g", "h"]


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


def test_decimal_topics_reach_all_three_rounding_phrasings():
    # pythagoras_3d's answer (a length) was converted from a hardcoded
    # "3 significant figures" to a random choice among the 3 real GCSE
    # rounding instructions (see app/topics/rounding.py) - confirm all three
    # genuinely appear over enough trials. trig_3d's answer is an angle,
    # which by real GCSE convention always stays fixed at "1 decimal place"
    # and is deliberately excluded here (never touched by the rollout).
    generators = [solids_3d_trig.generate_3d_pythagoras]
    phrasings = {"1 decimal place", "2 decimal places", "3 significant figures"}
    for generate in generators:
        rng = random.Random(506)
        seen = set()
        for _ in range(200):
            q = generate(Tier.HIGHER, rng)
            seen |= {p for p in phrasings if p in q.prompt}
        assert seen == phrasings
