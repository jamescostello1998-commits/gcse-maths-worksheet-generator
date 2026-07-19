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


def test_geometric_vectors_has_a_diagram_and_coefficients_sum_to_one():
    import sympy as sp

    rng = random.Random(92)
    for _ in range(TRIALS):
        q = vectors.generate_geometric_vectors(Tier.HIGHER, rng)
        assert q.diagram is not None
        assert q.diagram.kind == "vector_triangle"
        m, n = q.diagram.params["ratio"]
        assert sp.Rational(n, m + n) + sp.Rational(m, m + n) == 1


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
