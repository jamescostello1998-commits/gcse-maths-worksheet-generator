import random

from app.core.models import Tier
from app.topics import number_theory

TRIALS = 200

GENERATORS = [
    (number_theory.generate_prime_numbers, Tier.FOUNDATION),
    (number_theory.generate_multiples, Tier.FOUNDATION),
    (number_theory.generate_factors, Tier.FOUNDATION),
    (number_theory.generate_prime_factors_foundation, Tier.FOUNDATION),
    (number_theory.generate_prime_factors_higher, Tier.HIGHER),
    (number_theory.generate_lcm_by_listing, Tier.FOUNDATION),
    (number_theory.generate_hcf_by_listing, Tier.FOUNDATION),
    (number_theory.generate_hcf_lcm_by_prime_factors, Tier.HIGHER),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(600)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_prime_factors_foundation_is_never_in_index_form():
    rng = random.Random(601)
    for _ in range(TRIALS):
        q = number_theory.generate_prime_factors_foundation(Tier.FOUNDATION, rng)
        assert "^" not in q.final_answer


def test_prime_factors_higher_uses_index_form_when_repeated():
    rng = random.Random(602)
    found_index_form = False
    for _ in range(TRIALS):
        q = number_theory.generate_prime_factors_higher(Tier.HIGHER, rng)
        if "^" in q.final_answer:
            found_index_form = True
    assert found_index_form


def test_hcf_lcm_by_prime_factors_covers_both_kinds():
    rng = random.Random(603)
    kinds = {number_theory.generate_hcf_lcm_by_prime_factors(Tier.HIGHER, rng).dedup_key.split(":")[-1] for _ in range(100)}
    assert kinds == {"hcf", "lcm"}


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(604)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 40


def test_topic_definitions_have_expected_metadata():
    topics = [
        number_theory.TOPIC_PRIME_NUMBERS,
        number_theory.TOPIC_MULTIPLES,
        number_theory.TOPIC_FACTORS,
        number_theory.TOPIC_PRIME_FACTORS_FOUNDATION,
        number_theory.TOPIC_PRIME_FACTORS_HIGHER,
        number_theory.TOPIC_LCM_BY_LISTING,
        number_theory.TOPIC_HCF_BY_LISTING,
        number_theory.TOPIC_HCF_LCM_BY_PRIME_FACTORS,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 8
    for t in topics:
        assert t.section == "number"
        assert t.group == "Factors, Multiples & Primes"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)
