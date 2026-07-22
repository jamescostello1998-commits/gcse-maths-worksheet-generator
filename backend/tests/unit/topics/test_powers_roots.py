import random
from fractions import Fraction

from app.core.models import Tier
from app.topics import powers_roots

TRIALS = 200

GENERATORS = [
    (powers_roots.generate_powers_foundation, Tier.FOUNDATION),
    (powers_roots.generate_powers_higher, Tier.HIGHER),
    (powers_roots.generate_roots_foundation, Tier.FOUNDATION),
    (powers_roots.generate_roots_higher, Tier.HIGHER),
    (powers_roots.generate_rationalise_denominator, Tier.HIGHER),
    (powers_roots.generate_negative_indices, Tier.FOUNDATION),
    (powers_roots.generate_simplifying_indices_challenging, Tier.HIGHER),
    (powers_roots.generate_indices_common_base_equations, Tier.HIGHER),
    (powers_roots.generate_surds_multiply_divide, Tier.HIGHER),
    (powers_roots.generate_algebraic_surds, Tier.HIGHER),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(700)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_roots_higher_answer_is_in_a_root_b_form():
    rng = random.Random(701)
    for _ in range(TRIALS):
        q = powers_roots.generate_roots_higher(Tier.HIGHER, rng)
        assert "√" in q.final_answer
        coeff, radicand = q.final_answer.split("√")
        assert int(coeff) > 1
        assert int(radicand) > 1


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(702)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 30


def test_topic_definitions_have_expected_metadata():
    topics = [
        powers_roots.TOPIC_POWERS_FOUNDATION,
        powers_roots.TOPIC_POWERS_HIGHER,
        powers_roots.TOPIC_ROOTS_FOUNDATION,
        powers_roots.TOPIC_ROOTS_HIGHER,
        powers_roots.TOPIC_RATIONALISE_DENOMINATOR,
        powers_roots.TOPIC_NEGATIVE_INDICES,
        powers_roots.TOPIC_SIMPLIFYING_INDICES_CHALLENGING,
        powers_roots.TOPIC_INDICES_COMMON_BASE_EQUATIONS,
        powers_roots.TOPIC_SURDS_MULTIPLY_DIVIDE,
        powers_roots.TOPIC_ALGEBRAIC_SURDS,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 10
    for t in topics:
        assert t.section == "number"
        assert t.group == "Powers, Roots & Indices"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)


def test_rationalise_denominator_never_leaves_a_root_on_the_bottom():
    rng = random.Random(703)
    for _ in range(TRIALS):
        q = powers_roots.generate_rationalise_denominator(Tier.HIGHER, rng)
        if "/" in q.final_answer:
            denom = q.final_answer.split("/")[-1]
            assert "√" not in denom


MODELLED_EXAMPLE_GENERATORS = [
    (powers_roots.generate_modelled_example_powers_foundation, Tier.FOUNDATION, "powers_foundation"),
    (powers_roots.generate_modelled_example_powers_higher, Tier.HIGHER, "powers_higher"),
    (powers_roots.generate_modelled_example_roots_foundation, Tier.FOUNDATION, "roots_foundation"),
    (powers_roots.generate_modelled_example_roots_higher, Tier.HIGHER, "roots_higher"),
    (powers_roots.generate_modelled_example_rationalise_denominator, Tier.HIGHER, "rationalise_denominator"),
    (powers_roots.generate_modelled_example_negative_indices, Tier.FOUNDATION, "negative_indices"),
    (
        powers_roots.generate_modelled_example_simplifying_indices_challenging,
        Tier.HIGHER,
        "simplifying_indices_challenging",
    ),
    (
        powers_roots.generate_modelled_example_indices_common_base_equations,
        Tier.HIGHER,
        "indices_common_base_equations",
    ),
    (powers_roots.generate_modelled_example_surds_multiply_divide, Tier.HIGHER, "surds_multiply_divide"),
    (powers_roots.generate_modelled_example_algebraic_surds, Tier.HIGHER, "algebraic_surds"),
]


def test_topic_definitions_have_modelled_example_generator():
    topics = [
        powers_roots.TOPIC_POWERS_FOUNDATION,
        powers_roots.TOPIC_POWERS_HIGHER,
        powers_roots.TOPIC_ROOTS_FOUNDATION,
        powers_roots.TOPIC_ROOTS_HIGHER,
        powers_roots.TOPIC_RATIONALISE_DENOMINATOR,
        powers_roots.TOPIC_NEGATIVE_INDICES,
        powers_roots.TOPIC_SIMPLIFYING_INDICES_CHALLENGING,
        powers_roots.TOPIC_INDICES_COMMON_BASE_EQUATIONS,
        powers_roots.TOPIC_SURDS_MULTIPLY_DIVIDE,
        powers_roots.TOPIC_ALGEBRAIC_SURDS,
    ]
    for t in topics:
        assert t.generate_modelled_example is not None


def test_modelled_examples_produce_valid_content():
    for generate, tier, topic_id in MODELLED_EXAMPLE_GENERATORS:
        rng = random.Random(940)
        for _ in range(200):
            example = generate(tier, rng)
            assert example.topic_id == topic_id
            assert example.prompt
            assert len(example.worked_calculation) >= 2
            assert len(example.teaching_steps) >= 3
            assert example.final_answer


def test_negative_indices_answer_is_int_or_valid_fraction_less_than_one_in_size():
    rng = random.Random(710)
    for _ in range(TRIALS):
        q = powers_roots.generate_negative_indices(Tier.FOUNDATION, rng)
        answer = q.final_answer
        if answer.startswith("1/"):
            # The plain-evaluation shape: always a unit fraction 1/base^n.
            assert int(answer.split("/")[1]) > 1
        else:
            # The index-law shapes: a single power of the base, e.g. "3^-2".
            assert "^" in answer


def test_simplifying_indices_challenging_answer_is_int_or_valid_fraction():
    rng = random.Random(711)
    for _ in range(TRIALS):
        q = powers_roots.generate_simplifying_indices_challenging(Tier.HIGHER, rng)
        answer = q.final_answer
        if "/" in answer:
            num, den = answer.split("/")
            frac = Fraction(int(num), int(den))
            assert frac.numerator == int(num) and frac.denominator == int(den)
        else:
            int(answer)  # must parse as a plain integer


def test_indices_common_base_equations_answer_is_int_or_valid_fraction():
    rng = random.Random(712)
    for _ in range(TRIALS):
        q = powers_roots.generate_indices_common_base_equations(Tier.HIGHER, rng)
        answer = q.final_answer
        if "/" in answer:
            num, den = answer.split("/")
            frac = Fraction(int(num), int(den))
            assert frac.numerator == int(num) and frac.denominator == int(den)
        else:
            int(answer)  # must parse as a plain integer


def test_surds_multiply_divide_answer_is_integer_or_a_root_b_form():
    rng = random.Random(713)
    for _ in range(TRIALS):
        q = powers_roots.generate_surds_multiply_divide(Tier.HIGHER, rng)
        answer = q.final_answer
        if "√" in answer:
            coeff, radicand = answer.split("√")
            assert int(coeff) > 1
            assert int(radicand) > 1
        else:
            int(answer)  # the "clean" multiply/divide shapes give a plain integer


def test_algebraic_surds_answer_always_contains_a_surd_term():
    rng = random.Random(714)
    for _ in range(TRIALS):
        q = powers_roots.generate_algebraic_surds(Tier.HIGHER, rng)
        # Both shapes are constructed so the surd coefficient is never zero.
        assert "√" in q.final_answer
