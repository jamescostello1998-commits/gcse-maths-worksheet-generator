import random

from app.core.models import Tier
from app.topics import vectors

TRIALS = 200

GENERATORS = [
    (vectors.generate_vectors_arithmetic_foundation, Tier.FOUNDATION),
    (vectors.generate_vectors_arithmetic_higher, Tier.HIGHER),
    (vectors.generate_geometric_vectors, Tier.HIGHER),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(90)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_foundation_vector_arithmetic_never_uses_negative_scalars():
    import re

    rng = random.Random(91)
    for _ in range(TRIALS):
        q = vectors.generate_vectors_arithmetic_foundation(Tier.FOUNDATION, rng)
        # Scalars are always positive for Foundation (only vector subtraction, via
        # the "-" *between* terms, may appear) - so neither term itself starts with "-".
        find_clause = q.prompt.split("Find ", 1)[1].rstrip(".")
        terms = re.split(r" [+-] ", find_clause)
        assert all(not t.startswith("-") for t in terms)


def test_higher_vector_arithmetic_never_shows_a_double_minus_sign():
    # Higher's scalars can be negative, so "k*a - m*b" with m itself negative
    # used to render as e.g. "2a - -4b" - must now be parenthesised instead
    # ("2a - (-4b)"), never a literal "- -".
    rng = random.Random(96)
    for _ in range(TRIALS):
        q = vectors.generate_vectors_arithmetic_higher(Tier.HIGHER, rng)
        find_clause = q.prompt.split("Find ", 1)[1].rstrip(".")
        assert " - -" not in find_clause


def test_vector_answers_use_the_colvec_marker():
    rng = random.Random(97)
    q = vectors.generate_vectors_arithmetic_foundation(Tier.FOUNDATION, rng)
    assert q.final_answer.startswith("\\colvec{")


def test_geometric_vectors_has_a_diagram_and_coefficients_sum_to_one():
    import sympy as sp

    rng = random.Random(92)
    for _ in range(TRIALS):
        q = vectors.generate_geometric_vectors(Tier.HIGHER, rng)
        assert q.diagram is not None
        assert q.diagram.kind == "vector_triangle"
        m, n = q.diagram.params["ratio"]
        assert sp.Rational(n, m + n) + sp.Rational(m, m + n) == 1


def test_generators_use_the_vec_sentinel_for_genuine_vector_mentions():
    # \vec{a}/\vec{b} is bolded at render time (see mathtext.py's _VECTOR_RE) -
    # confirms vectors.py itself writes the raw sentinel, not just that it
    # renders correctly (that's mathtext.py's own test suite's job).
    rng = random.Random(94)
    for _ in range(TRIALS):
        q = vectors.generate_vectors_arithmetic_foundation(Tier.FOUNDATION, rng)
        assert "\\vec{a}" in q.prompt
        assert "\\vec{b}" in q.prompt


def test_geometric_vectors_prompt_leaves_the_english_article_untouched():
    # The one genuinely ambiguous sentence in this app ("OAB is a triangle
    # with OA = a and OB = b") - "is a triangle" must stay a plain,
    # unmarked "a" while the two genuine vector mentions get the sentinel.
    rng = random.Random(95)
    for _ in range(TRIALS):
        q = vectors.generate_geometric_vectors(Tier.HIGHER, rng)
        assert "is a triangle" in q.prompt
        assert "OA = \\vec{a}" in q.prompt
        assert "OB = \\vec{b}" in q.prompt
        assert q.diagram.params["a_label"] == "\\vec{a}"
        assert q.diagram.params["b_label"] == "\\vec{b}"


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(93)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 30


def test_topic_definitions_have_expected_metadata():
    topics = [
        vectors.TOPIC_VECTORS_ARITHMETIC_FOUNDATION,
        vectors.TOPIC_VECTORS_ARITHMETIC_HIGHER,
        vectors.TOPIC_GEOMETRIC_VECTORS,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 3
    for t in topics:
        assert t.section == "geometry"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)
    assert vectors.TOPIC_VECTORS_ARITHMETIC_FOUNDATION.group == "Vectors"
    assert vectors.TOPIC_VECTORS_ARITHMETIC_HIGHER.group == "Vectors"
    assert vectors.TOPIC_GEOMETRIC_VECTORS.group == "Geometric Vectors"


MODELLED_TOPICS = [
    vectors.TOPIC_VECTORS_ARITHMETIC_FOUNDATION,
    vectors.TOPIC_VECTORS_ARITHMETIC_HIGHER,
    vectors.TOPIC_GEOMETRIC_VECTORS,
]


def test_topics_have_a_modelled_example_generator_wired_up():
    for t in MODELLED_TOPICS:
        assert t.generate_modelled_example is not None


def test_modelled_example_vectors_arithmetic_is_valid():
    generators = [
        (vectors.generate_modelled_example_vectors_arithmetic_foundation, Tier.FOUNDATION, "vectors_arithmetic_F"),
        (vectors.generate_modelled_example_vectors_arithmetic_higher, Tier.HIGHER, "vectors_arithmetic_H"),
    ]
    for generate, tier, topic_id in generators:
        rng = random.Random(201)
        for _ in range(TRIALS):
            ex = generate(tier, rng)
            assert ex.topic_id == topic_id
            assert ex.tier == tier
            assert ex.prompt
            assert len(ex.worked_calculation) >= 2
            assert len(ex.teaching_steps) >= 3
            assert ex.final_answer
            assert ex.diagram is None


def test_modelled_example_geometric_vectors_is_valid():
    rng = random.Random(202)
    for _ in range(TRIALS):
        ex = vectors.generate_modelled_example_geometric_vectors(Tier.HIGHER, rng)
        assert ex.topic_id == "geometric_vectors_H"
        assert ex.tier == Tier.HIGHER
        assert ex.prompt
        assert len(ex.worked_calculation) >= 2
        assert len(ex.teaching_steps) >= 3
        assert ex.final_answer
        assert ex.diagram is not None
        assert ex.diagram.kind == "vector_triangle"
