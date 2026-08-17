import random
import re

from app.core.models import Tier
from app.topics import expand_factorise

TRIALS = 200

GENERATORS = [
    (expand_factorise.generate_expand_single, Tier.FOUNDATION),
    (expand_factorise.generate_factorise_common, Tier.FOUNDATION),
    (expand_factorise.generate_expand_double_foundation, Tier.FOUNDATION),
    (expand_factorise.generate_expand_double_no_coefficient_foundation, Tier.FOUNDATION),
    (expand_factorise.generate_factorise_quadratic_foundation, Tier.FOUNDATION),
    (expand_factorise.generate_expand_double, Tier.HIGHER),
    (expand_factorise.generate_expand_triple, Tier.HIGHER),
    (expand_factorise.generate_expand_triple_no_coefficient, Tier.HIGHER),
    (expand_factorise.generate_factorise_quadratic, Tier.HIGHER),
    (expand_factorise.generate_solve_quadratic_factorising_foundation, Tier.FOUNDATION),
    (expand_factorise.generate_solve_quadratic_factorising, Tier.HIGHER),
]


def test_all_generators_produce_valid_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(10)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_foundation_double_bracket_constants_mix_signs():
    # Both Foundation double-bracket topics used to be all-positive
    # constants only (see the comments in expand_factorise.py) - confirm
    # negative constants now genuinely appear, roughly a third of the time
    # each, while the x-coefficients themselves stay positive.
    for generate, kind in [
        (expand_factorise.generate_expand_double_foundation, "coefficient"),
        (expand_factorise.generate_expand_double_no_coefficient_foundation, "no_coefficient"),
    ]:
        rng = random.Random(20)
        neg_seen = pos_seen = 0
        for _ in range(500):
            q = generate(Tier.FOUNDATION, rng)
            assert q.prompt.count("-x") == 0  # x-coefficient itself never negative here
            if "- " in q.prompt:
                neg_seen += 1
            else:
                pos_seen += 1
        assert neg_seen > 50, f"{kind}: expected genuine negative-constant variety, saw {neg_seen}/500"
        assert pos_seen > 50, f"{kind}: expected genuine positive-only questions too, saw {pos_seen}/500"


def test_factorise_common_never_starts_negative_and_is_constant_first_about_10_percent():
    rng = random.Random(21)
    constant_first = 0
    total = 3000
    for _ in range(total):
        q = expand_factorise.generate_factorise_common(Tier.FOUNDATION, rng)
        item = q.prompt.removeprefix("Factorise:").strip()
        assert not item.startswith("-")
        if re.match(r"^\d+ \+", item):
            constant_first += 1
    assert 0.06 < constant_first / total < 0.14


def test_factorise_quadratic_pair_search_matches_roots():
    assert expand_factorise._find_factor_pair(1, -12) in {(4, -3), (-3, 4)}
    assert expand_factorise._find_factor_pair(-7, 12) in {(-3, -4), (-4, -3)}
    assert expand_factorise._find_factor_pair(5, 0) == (0, 5)


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(12)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 50


def test_topic_definitions_have_expected_metadata():
    topics = [
        expand_factorise.TOPIC_EXPAND_SINGLE,
        expand_factorise.TOPIC_EXPAND_DOUBLE_FOUNDATION,
        expand_factorise.TOPIC_EXPAND_DOUBLE_NO_COEFFICIENT_FOUNDATION,
        expand_factorise.TOPIC_EXPAND_DOUBLE,
        expand_factorise.TOPIC_EXPAND_TRIPLE,
        expand_factorise.TOPIC_EXPAND_TRIPLE_NO_COEFFICIENT,
        expand_factorise.TOPIC_FACTORISE_COMMON,
        expand_factorise.TOPIC_FACTORISE_QUADRATIC_FOUNDATION,
        expand_factorise.TOPIC_FACTORISE_QUADRATIC,
        expand_factorise.TOPIC_SOLVE_QUADRATIC_FACTORISING_FOUNDATION,
        expand_factorise.TOPIC_SOLVE_QUADRATIC_FACTORISING,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 11
    for t in topics:
        assert t.section == "algebra"
        assert t.group in ("Expanding Brackets", "Factorising", "Solving Quadratic Equations")
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)


def test_all_topics_have_modelled_example_wired():
    topics = [
        expand_factorise.TOPIC_EXPAND_SINGLE,
        expand_factorise.TOPIC_EXPAND_DOUBLE_FOUNDATION,
        expand_factorise.TOPIC_EXPAND_DOUBLE_NO_COEFFICIENT_FOUNDATION,
        expand_factorise.TOPIC_EXPAND_DOUBLE,
        expand_factorise.TOPIC_EXPAND_TRIPLE,
        expand_factorise.TOPIC_EXPAND_TRIPLE_NO_COEFFICIENT,
        expand_factorise.TOPIC_FACTORISE_COMMON,
        expand_factorise.TOPIC_FACTORISE_QUADRATIC_FOUNDATION,
        expand_factorise.TOPIC_FACTORISE_QUADRATIC,
        expand_factorise.TOPIC_SOLVE_QUADRATIC_FACTORISING_FOUNDATION,
        expand_factorise.TOPIC_SOLVE_QUADRATIC_FACTORISING,
    ]
    for t in topics:
        assert t.generate_modelled_example is not None


MODELLED_EXAMPLE_GENERATORS = [
    (expand_factorise.generate_modelled_example_expand_single, Tier.FOUNDATION, "expand_single_bracket_F"),
    (
        expand_factorise.generate_modelled_example_expand_double_foundation,
        Tier.FOUNDATION,
        "expand_double_brackets_F",
    ),
    (
        expand_factorise.generate_modelled_example_expand_double_no_coefficient_foundation,
        Tier.FOUNDATION,
        "expand_double_brackets_no_coefficient_F",
    ),
    (expand_factorise.generate_modelled_example_expand_double, Tier.HIGHER, "expand_double_brackets_H"),
    (expand_factorise.generate_modelled_example_expand_triple, Tier.HIGHER, "expand_triple_brackets_H"),
    (expand_factorise.generate_modelled_example_expand_triple_no_coefficient, Tier.HIGHER, "expand_triple_brackets_no_coefficient_H"),
    (
        expand_factorise.generate_modelled_example_factorise_common,
        Tier.FOUNDATION,
        "factorise_common_factor_F",
    ),
    (
        expand_factorise.generate_modelled_example_factorise_quadratic_foundation,
        Tier.FOUNDATION,
        "factorise_quadratics_F",
    ),
    (
        expand_factorise.generate_modelled_example_factorise_quadratic,
        Tier.HIGHER,
        "factorise_quadratics_H",
    ),
    (
        expand_factorise.generate_modelled_example_solve_quadratic_factorising_foundation,
        Tier.FOUNDATION,
        "solve_quadratic_factorising_F",
    ),
    (
        expand_factorise.generate_modelled_example_solve_quadratic_factorising,
        Tier.HIGHER,
        "solve_quadratic_factorising_H",
    ),
]


def test_modelled_example_generators_produce_verified_examples():
    for generate_modelled_example, tier, topic_id in MODELLED_EXAMPLE_GENERATORS:
        rng = random.Random(101)
        for _ in range(TRIALS):
            example = generate_modelled_example(tier, rng)
            assert example.topic_id == topic_id
            assert example.prompt
            assert len(example.worked_calculation) >= 2
            assert len(example.teaching_steps) >= 3
            assert example.final_answer
