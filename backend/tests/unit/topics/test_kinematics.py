import random

from app.core.models import Tier
from app.topics import kinematics

TRIALS = 300

GENERATORS = [
    (kinematics.generate_kinematics_suvat, Tier.HIGHER),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(120)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(121)
        keys = {generate(tier, rng).dedup_key for _ in range(300)}
        assert len(keys) > 40


def test_topic_definitions_have_expected_metadata():
    topics = [kinematics.TOPIC_KINEMATICS_SUVAT]
    ids = {t.id for t in topics}
    assert len(ids) == 1
    for t in topics:
        assert t.section == "algebra"
        assert t.group == "Kinematics (SUVAT)"
        assert t.fixed_tier == Tier.HIGHER


MODELLED_EXAMPLE_GENERATORS = [
    (kinematics.generate_modelled_example_kinematics_suvat, Tier.HIGHER, "kinematics_suvat"),
]


def test_all_topics_have_modelled_example_wired():
    for t in (kinematics.TOPIC_KINEMATICS_SUVAT,):
        assert t.generate_modelled_example is not None


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


def test_final_answer_never_negative_root_language_missing_when_sqrt_used():
    """Whenever a square root was genuinely needed to isolate a speed (v or u
    in v^2 = u^2 + 2as), the final answer should note the positive root was
    taken - the negative root is mathematically valid but unphysical here."""
    rng = random.Random(555)
    seen_v_or_u_branch = False
    for _ in range(400):
        q = kinematics.generate_kinematics_suvat(Tier.HIGHER, rng)
        if q.dedup_key.startswith("eq3:v:") or q.dedup_key.startswith("eq3:u:"):
            seen_v_or_u_branch = True
            assert "positive root" in q.final_answer
    assert seen_v_or_u_branch
