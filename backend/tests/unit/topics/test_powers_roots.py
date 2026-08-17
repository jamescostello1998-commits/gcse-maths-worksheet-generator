import random
import re
from fractions import Fraction

from app.core.models import Tier
from app.topics import powers_roots

TRIALS = 200

GENERATORS = [
    (powers_roots.generate_powers_foundation, Tier.FOUNDATION),
    (powers_roots.generate_indices_law_foundation, Tier.FOUNDATION),
    (powers_roots.generate_powers_higher, Tier.HIGHER),
    (powers_roots.generate_roots_foundation, Tier.FOUNDATION),
    (powers_roots.generate_roots_higher, Tier.HIGHER),
    (powers_roots.generate_rationalise_denominator, Tier.HIGHER),
    (powers_roots.generate_negative_indices, Tier.FOUNDATION),
    (powers_roots.generate_simplifying_indices_challenging, Tier.HIGHER),
    (powers_roots.generate_indices_common_base_equations, Tier.HIGHER),
    (powers_roots.generate_surds_multiply_divide, Tier.HIGHER),
    (powers_roots.generate_algebraic_surds, Tier.HIGHER),
    (powers_roots.generate_surds_add_subtract, Tier.HIGHER),
    (powers_roots.generate_surds_specified_form, Tier.HIGHER),
    (powers_roots.generate_surds_rectangle, Tier.HIGHER),
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


def test_powers_foundation_bases_and_exponents_match_the_four_ranges():
    rng = random.Random(704)
    for _ in range(500):
        q = powers_roots.generate_powers_foundation(Tier.FOUNDATION, rng)
        # The leading verb can be multi-word ("Work out ..."), so grab the
        # last whitespace-separated token rather than assuming position 1.
        base_str, exp_str = q.prompt.rsplit(None, 1)[-1].rstrip(".").split("^")
        base, exponent = int(base_str), int(exp_str)
        if exponent == 2:
            assert 2 <= base <= 15
        elif exponent == 3:
            assert 2 <= base <= 10
        elif exponent == 4:
            assert 2 <= base <= 5
        else:
            assert base == 2 and 2 <= exponent <= 8


def test_indices_law_foundation_never_produces_a_negative_exponent_and_mixes_bases():
    rng = random.Random(705)
    numeric_seen = False
    algebraic_seen = False
    for _ in range(300):
        q = powers_roots.generate_indices_law_foundation(Tier.FOUNDATION, rng)
        answer = q.final_answer
        assert "-" not in answer  # never a negative exponent
        base, _, exp_str = answer.partition("^")
        exponent = int(exp_str) if exp_str else 1  # bare base (e.g. "x") means exponent 1
        assert exponent > 0
        if base == "x":
            algebraic_seen = True
        else:
            numeric_seen = True
            assert 2 <= int(base) <= 9
    assert numeric_seen and algebraic_seen


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        if generate is powers_roots.generate_powers_foundation:
            continue  # deliberately bounded state space - see dedicated test below
        rng = random.Random(702)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 30


def test_powers_foundation_dedup_key_space_matches_the_31_allowed_combinations():
    # A deliberately small, user-specified range (base<=15 squared,
    # base<=10 cubed, base<=5 to the power 4, base 2 up to the power 8)
    # gives exactly 31 distinct (base, exponent) pairs in total - enough to
    # reliably build the default 20-question worksheet (confirmed via a
    # real build_worksheet trial), but not ">> 20" like most topics, so it's
    # excluded from the generic >30-in-100-draws check above.
    rng = random.Random(706)
    keys = {powers_roots.generate_powers_foundation(Tier.FOUNDATION, rng).dedup_key for _ in range(3000)}
    assert len(keys) == 31


def test_topic_definitions_have_expected_metadata():
    topics = [
        powers_roots.TOPIC_POWERS_FOUNDATION,
        powers_roots.TOPIC_INDICES_LAW_FOUNDATION,
        powers_roots.TOPIC_POWERS_HIGHER,
        powers_roots.TOPIC_ROOTS_FOUNDATION,
        powers_roots.TOPIC_ROOTS_HIGHER,
        powers_roots.TOPIC_RATIONALISE_DENOMINATOR,
        powers_roots.TOPIC_NEGATIVE_INDICES,
        powers_roots.TOPIC_SIMPLIFYING_INDICES_CHALLENGING,
        powers_roots.TOPIC_INDICES_COMMON_BASE_EQUATIONS,
        powers_roots.TOPIC_SURDS_MULTIPLY_DIVIDE,
        powers_roots.TOPIC_ALGEBRAIC_SURDS,
        powers_roots.TOPIC_SURDS_SPECIFIED_FORM,
        powers_roots.TOPIC_SURDS_RECTANGLE,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 13
    for t in topics:
        assert t.section == "number"
        assert t.group == "Powers, Roots & Indices"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)


def test_rationalise_denominator_never_leaves_a_root_on_the_bottom():
    # A genuine fraction answer is now built via the \frac{NUM}{DEN} marker
    # (see mathtext.py), not plain "NUM/DEN" text - extract DEN from
    # whichever form is present.
    frac_marker_re = re.compile(r"\\frac\{[^{}]*\}\{([^{}]*)\}")
    rng = random.Random(703)
    for _ in range(TRIALS):
        q = powers_roots.generate_rationalise_denominator(Tier.HIGHER, rng)
        m = frac_marker_re.search(q.final_answer)
        if m is not None:
            assert "√" not in m.group(1)
        elif "/" in q.final_answer:
            denom = q.final_answer.split("/")[-1]
            assert "√" not in denom


MODELLED_EXAMPLE_GENERATORS = [
    (powers_roots.generate_modelled_example_powers_foundation, Tier.FOUNDATION, "powers_F"),
    (powers_roots.generate_modelled_example_indices_law_foundation, Tier.FOUNDATION, "indices_law_F"),
    (powers_roots.generate_modelled_example_powers_higher, Tier.HIGHER, "powers_H"),
    (powers_roots.generate_modelled_example_roots_foundation, Tier.FOUNDATION, "roots_F"),
    (powers_roots.generate_modelled_example_roots_higher, Tier.HIGHER, "roots_H"),
    (powers_roots.generate_modelled_example_rationalise_denominator, Tier.HIGHER, "rationalise_denominator_H"),
    (powers_roots.generate_modelled_example_negative_indices, Tier.FOUNDATION, "negative_indices_F"),
    (
        powers_roots.generate_modelled_example_simplifying_indices_challenging,
        Tier.HIGHER,
        "simplifying_indices_challenging_H",
    ),
    (
        powers_roots.generate_modelled_example_indices_common_base_equations,
        Tier.HIGHER,
        "indices_common_base_equations_H",
    ),
    (powers_roots.generate_modelled_example_surds_multiply_divide, Tier.HIGHER, "surds_multiply_divide_H"),
    (powers_roots.generate_modelled_example_algebraic_surds, Tier.HIGHER, "algebraic_surds_H"),
    (powers_roots.generate_modelled_example_surds_add_subtract, Tier.HIGHER, "surds_add_subtract_H"),
    (powers_roots.generate_modelled_example_surds_specified_form, Tier.HIGHER, "surds_specified_form_H"),
    (powers_roots.generate_modelled_example_surds_rectangle, Tier.HIGHER, "surds_rectangle_H"),
]


def test_topic_definitions_have_modelled_example_generator():
    topics = [
        powers_roots.TOPIC_POWERS_FOUNDATION,
        powers_roots.TOPIC_INDICES_LAW_FOUNDATION,
        powers_roots.TOPIC_POWERS_HIGHER,
        powers_roots.TOPIC_ROOTS_FOUNDATION,
        powers_roots.TOPIC_ROOTS_HIGHER,
        powers_roots.TOPIC_RATIONALISE_DENOMINATOR,
        powers_roots.TOPIC_NEGATIVE_INDICES,
        powers_roots.TOPIC_SIMPLIFYING_INDICES_CHALLENGING,
        powers_roots.TOPIC_INDICES_COMMON_BASE_EQUATIONS,
        powers_roots.TOPIC_SURDS_MULTIPLY_DIVIDE,
        powers_roots.TOPIC_ALGEBRAIC_SURDS,
        powers_roots.TOPIC_SURDS_SPECIFIED_FORM,
        powers_roots.TOPIC_SURDS_RECTANGLE,
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


def test_powers_higher_shows_a_fractional_exponent_in_most_questions():
    # Reweighted towards the two fractional-exponent shapes (fractional_root/
    # fractional_full) since a genuine "^(num/den)" is this topic's own
    # distinguishing content - over enough trials it should be the common
    # case, not a rare one.
    rng = random.Random(713)
    fractional_count = 0
    for _ in range(TRIALS):
        q = powers_roots.generate_powers_higher(Tier.HIGHER, rng)
        if "^(" in q.prompt:
            fractional_count += 1
    assert fractional_count > TRIALS * 0.5


def test_simplifying_indices_challenging_shows_a_fractional_exponent_often():
    rng = random.Random(714)
    fractional_count = 0
    for _ in range(TRIALS):
        q = powers_roots.generate_simplifying_indices_challenging(Tier.HIGHER, rng)
        if "^(" in q.prompt:
            fractional_count += 1
    assert fractional_count > TRIALS * 0.35


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


def test_surds_add_subtract_answer_is_simplified_and_nonzero():
    import math as _math

    rng = random.Random(715)
    for _ in range(TRIALS):
        q = powers_roots.generate_surds_add_subtract(Tier.HIGHER, rng)
        answer = q.final_answer
        assert "√" in answer  # always a single like-surd result
        coeff_str, radicand = answer.split("√")
        coeff = -1 if coeff_str == "-" else (1 if coeff_str == "" else int(coeff_str))
        assert coeff != 0
        # Radicand must be square-free (fully simplified surd).
        r = int(radicand)
        assert r > 1
        for p in range(2, _math.isqrt(r) + 1):
            assert r % (p * p) != 0


def test_roots_and_surds_topics_no_longer_name_the_form_in_the_prompt():
    # Per direct request: only name the target form when it's genuinely
    # non-obvious (surds_specified_form_H) - a plain "simplify this surd"
    # instruction shouldn't redundantly spell out "in the form a√b".
    rng = random.Random(716)
    for _ in range(TRIALS):
        assert "in the form" not in powers_roots.generate_roots_higher(Tier.HIGHER, rng).prompt
        assert "in the form" not in powers_roots.generate_surds_multiply_divide(Tier.HIGHER, rng).prompt
        q = powers_roots.generate_surds_add_subtract(Tier.HIGHER, rng)
        assert "in the form" not in q.prompt
        assert q.prompt.startswith("Simplify fully ")


def test_surds_specified_form_answer_is_an_integer_matching_the_stated_root():
    rng = random.Random(717)
    for _ in range(TRIALS):
        q = powers_roots.generate_surds_specified_form(Tier.HIGHER, rng)
        assert "in the form k√" in q.prompt
        # The root stated in the prompt must be square-free (a genuine
        # simplest-form base, not e.g. k√12).
        root = int(q.prompt.split("k√")[1].split(",")[0])
        assert root > 1
        for p in range(2, int(root**0.5) + 1):
            assert root % (p * p) != 0
        int(q.final_answer)  # the answer is always a bare integer k, never a surd


def test_surds_rectangle_answer_and_diagram():
    rng = random.Random(718)
    perimeter_seen, area_seen = False, False
    for _ in range(TRIALS):
        q = powers_roots.generate_surds_rectangle(Tier.HIGHER, rng)
        assert q.diagram is not None
        assert q.diagram.kind == "rectangle"
        assert "√" in q.diagram.params["width_label"]
        assert "√" in q.diagram.params["height_label"]
        if "perimeter" in q.prompt:
            perimeter_seen = True
            assert "√" in q.final_answer  # a surd multiple, never a bare integer
        else:
            area_seen = True
            assert "√" not in q.final_answer  # always a clean integer number of cm²
    assert perimeter_seen and area_seen
