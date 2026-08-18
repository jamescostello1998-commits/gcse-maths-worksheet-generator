import random

from app.core.models import Tier
from app.topics import sequences

TRIALS = 200

GENERATORS = [
    (sequences.generate_next_term, Tier.FOUNDATION),
    (sequences.generate_term_to_term_rule, Tier.FOUNDATION),
    (sequences.generate_nth_term, Tier.FOUNDATION),
    (sequences.generate_quadratic_nth_term, Tier.HIGHER),
    (sequences.generate_special_sequences_foundation, Tier.FOUNDATION),
    (sequences.generate_special_sequences_higher, Tier.HIGHER),
    (sequences.generate_missing_term, Tier.FOUNDATION),
    (sequences.generate_is_a_term, Tier.FOUNDATION),
    (sequences.generate_first_term_exceeding, Tier.FOUNDATION),
    (sequences.generate_terms_from_nth_term, Tier.FOUNDATION),
    (sequences.generate_terms_from_quadratic_nth_term, Tier.HIGHER),
    (sequences.generate_term_difference, Tier.FOUNDATION),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(150)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(151)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 30


def test_every_displayed_sequence_ends_with_an_ellipsis():
    # Every shown sequence should end "..." to signal it continues, per
    # direct user request. The two "terms from the nth term" generators are
    # the one exception that checks final_answer instead of prompt - their
    # prompt states a FORMULA, not a sequence (the sequence only appears
    # once it's derived, as the answer).
    answer_only = {sequences.generate_terms_from_nth_term, sequences.generate_terms_from_quadratic_nth_term}
    for generate, tier in GENERATORS:
        rng = random.Random(152)
        for _ in range(50):
            q = generate(tier, rng)
            target = q.final_answer if generate in answer_only else q.prompt
            assert ", ..." in target, (generate.__name__, target)


ALL_TOPICS = [
    sequences.TOPIC_NEXT_TERM,
    sequences.TOPIC_TERM_TO_TERM_RULE,
    sequences.TOPIC_NTH_TERM,
    sequences.TOPIC_QUADRATIC_NTH_TERM,
    sequences.TOPIC_SPECIAL_SEQUENCES_FOUNDATION,
    sequences.TOPIC_SPECIAL_SEQUENCES_HIGHER,
    sequences.TOPIC_MISSING_TERM,
    sequences.TOPIC_IS_A_TERM,
    sequences.TOPIC_FIRST_TERM_EXCEEDING,
    sequences.TOPIC_TERMS_FROM_NTH_TERM_FOUNDATION,
    sequences.TOPIC_TERMS_FROM_NTH_TERM_HIGHER,
    sequences.TOPIC_TERM_DIFFERENCE,
]


def test_topic_definitions_have_expected_metadata():
    ids = {t.id for t in ALL_TOPICS}
    assert len(ids) == 12
    for t in ALL_TOPICS:
        assert t.section == "algebra"
        assert t.group == "Sequences"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)


MODELLED_EXAMPLE_GENERATORS = [
    (sequences.generate_modelled_example_next_term, Tier.FOUNDATION, "sequences_next_term_F"),
    (sequences.generate_modelled_example_term_to_term_rule, Tier.FOUNDATION, "sequences_term_to_term_rule_F"),
    (sequences.generate_modelled_example_nth_term, Tier.FOUNDATION, "sequences_nth_term_F"),
    (sequences.generate_modelled_example_quadratic_nth_term, Tier.HIGHER, "sequences_quadratic_nth_term_H"),
    (
        sequences.generate_modelled_example_special_sequences_foundation,
        Tier.FOUNDATION,
        "special_sequences_F",
    ),
    (sequences.generate_modelled_example_special_sequences_higher, Tier.HIGHER, "special_sequences_H"),
    (sequences.generate_modelled_example_missing_term, Tier.FOUNDATION, "sequences_missing_term_F"),
    (sequences.generate_modelled_example_is_a_term, Tier.FOUNDATION, "sequences_is_a_term_F"),
    (
        sequences.generate_modelled_example_first_term_exceeding,
        Tier.FOUNDATION,
        "sequences_first_term_exceeding_F",
    ),
    (
        sequences.generate_modelled_example_terms_from_nth_term,
        Tier.FOUNDATION,
        "sequences_terms_from_nth_term_F",
    ),
    (
        sequences.generate_modelled_example_terms_from_quadratic_nth_term,
        Tier.HIGHER,
        "sequences_terms_from_nth_term_H",
    ),
    (sequences.generate_modelled_example_term_difference, Tier.FOUNDATION, "sequences_term_difference_F"),
]


def test_all_topics_have_modelled_example_wired():
    for t in ALL_TOPICS:
        assert t.generate_modelled_example is not None


def test_modelled_example_generators_produce_verified_examples():
    for generate, tier, topic_id in MODELLED_EXAMPLE_GENERATORS:
        rng = random.Random(250)
        for _ in range(TRIALS):
            example = generate(tier, rng)
            assert example.topic_id == topic_id
            assert example.prompt
            assert len(example.worked_calculation) >= 2
            assert len(example.teaching_steps) >= 3
            assert example.final_answer


def test_missing_term_uses_a_safe_ascii_placeholder():
    # A literal "□" (U+25A1) has no glyph in this app's PDF font and
    # silently renders as a missing-glyph box - "?" is used instead.
    rng = random.Random(160)
    for _ in range(TRIALS):
        q = sequences.generate_missing_term(Tier.FOUNDATION, rng)
        assert "□" not in q.prompt
        assert "?" in q.prompt


def test_is_a_term_answers_are_yes_or_no_and_both_occur():
    rng = random.Random(161)
    yes_count = no_count = 0
    for _ in range(TRIALS):
        q = sequences.generate_is_a_term(Tier.FOUNDATION, rng)
        if q.final_answer == "No":
            no_count += 1
        else:
            assert q.final_answer.startswith("Yes, the")
            yes_count += 1
    assert yes_count > 20
    assert no_count > 20


def test_first_term_exceeding_sequence_is_always_increasing():
    # "Which term is the first to be greater than N" only makes sense for
    # an increasing sequence.
    rng = random.Random(162)
    for _ in range(TRIALS):
        q = sequences.generate_first_term_exceeding(Tier.FOUNDATION, rng)
        first, second = (int(v) for v in q.prompt.split(": ")[1].split(",")[:2])
        assert second > first
