import random

from app.core.models import Tier
from app.topics import congruent_triangle_proof

TRIALS = 200

GENERATORS = [
    (congruent_triangle_proof.generate_congruent_triangle_proof_higher, Tier.HIGHER),
    (congruent_triangle_proof.generate_congruent_triangle_proof_foundation, Tier.FOUNDATION),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(510)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer
            assert q.diagram is not None
            assert q.diagram.kind == "two_triangle_congruence"
            # Both triangles carry matching congruence info: the Higher topic
            # marks equal parts (vertex labels + ticks/arcs); the Foundation
            # topic shows real numeric side/angle measurements instead.
            p = q.diagram.params
            assert p.get("labels_1") or p.get("side_labels_1")
            assert p.get("labels_2") or p.get("side_labels_2")


def test_higher_answer_names_the_criterion():
    rng = random.Random(511)
    for _ in range(TRIALS):
        q = congruent_triangle_proof.generate_congruent_triangle_proof_higher(Tier.HIGHER, rng)
        assert any(c in q.final_answer for c in ("SSS", "SAS", "ASA", "RHS"))


def test_foundation_answer_is_a_lettered_multiple_choice_option():
    import re

    rng = random.Random(512)
    for _ in range(TRIALS):
        q = congruent_triangle_proof.generate_congruent_triangle_proof_foundation(Tier.FOUNDATION, rng)
        assert re.fullmatch(r"[A-D]\) (SSS|SAS|ASA|RHS)", q.final_answer)


def test_foundation_prompt_lists_all_four_options_shuffled():
    rng = random.Random(514)
    letters_used = set()
    for _ in range(TRIALS):
        q = congruent_triangle_proof.generate_congruent_triangle_proof_foundation(Tier.FOUNDATION, rng)
        for criterion in ("SSS", "SAS", "ASA", "RHS"):
            assert criterion in q.prompt
        answer_letter = q.final_answer[0]
        letters_used.add(answer_letter)
        # The answer's own criterion must appear next to its stated letter
        # in the prompt's option list, not just anywhere in the criteria set.
        assert f"{answer_letter}) {q.final_answer.split(') ', 1)[1]}" in q.prompt
    # Confirms the correct answer isn't pinned to always the same letter.
    assert letters_used == {"A", "B", "C", "D"}


def test_dedup_keys_vary_per_generator():
    # Higher is a fixed narrative-proof template bank (no per-instance random
    # numbers), so its ceiling is exactly the bank size. Foundation is now
    # procedural (real random numeric measurements per question), so it has a
    # much larger variety ceiling.
    rng = random.Random(513)
    higher_keys = {
        congruent_triangle_proof.generate_congruent_triangle_proof_higher(Tier.HIGHER, rng).dedup_key
        for _ in range(300)
    }
    assert len(higher_keys) == len(congruent_triangle_proof.TEMPLATES)

    rng = random.Random(513)
    foundation_keys = {
        congruent_triangle_proof.generate_congruent_triangle_proof_foundation(Tier.FOUNDATION, rng).dedup_key
        for _ in range(300)
    }
    assert len(foundation_keys) >= 40


def test_template_bank_has_at_least_fifteen_entries():
    assert len(congruent_triangle_proof.TEMPLATES) >= 15


def test_template_ids_are_unique():
    ids = [t.id for t in congruent_triangle_proof.TEMPLATES]
    assert len(ids) == len(set(ids))


def test_every_template_verifies_without_raising():
    # Each template's verify() builds one concrete coordinate instance
    # satisfying its stated givens and confirms all 3 corresponding side
    # lengths match between the two triangles - an authoring-error trap,
    # called directly here outside the random generator.
    for template in congruent_triangle_proof.TEMPLATES:
        template.verify()


def test_every_template_has_a_valid_criterion():
    for template in congruent_triangle_proof.TEMPLATES:
        assert template.criterion in {"SSS", "SAS", "ASA", "RHS"}


def test_topic_definitions_have_expected_metadata():
    topics = [
        congruent_triangle_proof.TOPIC_CONGRUENT_TRIANGLE_PROOF,
        congruent_triangle_proof.TOPIC_CONGRUENT_TRIANGLE_PROOF_FOUNDATION,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 2
    for t in topics:
        assert t.section == "geometry"
        assert t.group == "Congruence Proof"
        assert t.generate_modelled_example is not None
    # Higher is a curated template bank (question_count == bank size);
    # Foundation is procedural (default worksheet size).
    assert congruent_triangle_proof.TOPIC_CONGRUENT_TRIANGLE_PROOF.question_count == len(
        congruent_triangle_proof.TEMPLATES
    )
    assert congruent_triangle_proof.TOPIC_CONGRUENT_TRIANGLE_PROOF_FOUNDATION.question_count is None
    assert congruent_triangle_proof.TOPIC_CONGRUENT_TRIANGLE_PROOF.fixed_tier == Tier.HIGHER
    assert congruent_triangle_proof.TOPIC_CONGRUENT_TRIANGLE_PROOF_FOUNDATION.fixed_tier == Tier.FOUNDATION


MODELLED_EXAMPLE_GENERATORS = [
    (congruent_triangle_proof.generate_modelled_example_congruent_triangle_proof_higher, Tier.HIGHER, "congruent_triangle_proof"),
    (congruent_triangle_proof.generate_modelled_example_congruent_triangle_proof_foundation, Tier.FOUNDATION, "congruent_triangle_proof_foundation"),
]


def test_modelled_example_generators_produce_verified_examples():
    for generate, tier, topic_id in MODELLED_EXAMPLE_GENERATORS:
        rng = random.Random(520)
        for _ in range(TRIALS):
            example = generate(tier, rng)
            assert example.topic_id == topic_id
            assert example.prompt
            assert len(example.worked_calculation) >= 2
            assert len(example.teaching_steps) >= 3
            assert example.final_answer
