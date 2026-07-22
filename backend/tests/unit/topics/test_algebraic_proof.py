import random

from app.core.models import Tier
from app.topics import algebraic_proof

TRIALS = 200

GENERATORS = [
    (algebraic_proof.generate_algebraic_proof, Tier.HIGHER),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(120)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.prompt.startswith("Prove algebraically that")
            assert len(q.solution_steps) >= 4
            assert q.final_answer


def test_dedup_keys_vary_per_generator():
    # Unlike almost every other topic, algebraic_proof questions are general
    # claims about ALL integers n - there's no per-instance random number to
    # vary, so the natural variety is exactly the size of the curated
    # template bank (see algebraic_proof.py's module docstring). With
    # len(TEMPLATES) templates picked via rng.choice, 300 trials should
    # comfortably surface every single one.
    for generate, tier in GENERATORS:
        rng = random.Random(121)
        keys = {generate(tier, rng).dedup_key for _ in range(300)}
        assert len(keys) == len(algebraic_proof.TEMPLATES)


def test_template_bank_has_at_least_twenty_entries():
    assert len(algebraic_proof.TEMPLATES) >= 20


def test_template_ids_are_unique():
    ids = [t.id for t in algebraic_proof.TEMPLATES]
    assert len(ids) == len(set(ids))


def test_every_template_verifies_without_raising():
    # Each template's verify() performs an independent sympy check (either
    # expansion against a claimed factorised form, or a residue-by-residue
    # congruence check) - calling every one directly, outside the random
    # generator, confirms the whole bank is internally consistent.
    for template in algebraic_proof.TEMPLATES:
        template.verify()


def test_topic_definitions_have_expected_metadata():
    topics = [algebraic_proof.TOPIC_ALGEBRAIC_PROOF]
    ids = {t.id for t in topics}
    assert len(ids) == 1
    for t in topics:
        assert t.section == "algebra"
        assert t.group == "Algebraic Proof"
        assert t.fixed_tier == Tier.HIGHER
        assert t.question_count == len(algebraic_proof.TEMPLATES)


MODELLED_EXAMPLE_GENERATORS = [
    (algebraic_proof.generate_modelled_example_algebraic_proof, Tier.HIGHER, "algebraic_proof"),
]


def test_all_topics_have_modelled_example_wired():
    for t in (algebraic_proof.TOPIC_ALGEBRAIC_PROOF,):
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
