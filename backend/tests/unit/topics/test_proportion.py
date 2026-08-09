import random
import re

from app.core.models import Tier
from app.topics import proportion

TRIALS = 200

GENERATORS = [
    (proportion.generate_direct_proportion, Tier.FOUNDATION),
    (proportion.generate_inverse_proportion, Tier.FOUNDATION),
    (proportion.generate_algebraic_direct_proportion, Tier.HIGHER),
    (proportion.generate_algebraic_inverse_proportion, Tier.HIGHER),
]


def test_all_generators_produce_valid_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(30)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(32)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 50


def test_topic_definitions_have_expected_metadata():
    topics = [
        proportion.TOPIC_DIRECT_PROPORTION,
        proportion.TOPIC_INVERSE_PROPORTION,
        proportion.TOPIC_ALGEBRAIC_DIRECT_PROPORTION,
        proportion.TOPIC_ALGEBRAIC_INVERSE_PROPORTION,
    ]
    ids = {t.id for t in topics}
    assert len(ids) == 4
    for t in topics:
        assert t.section == "ratio_proportion"
        assert t.group == "Proportion"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)
    assert proportion.TOPIC_DIRECT_PROPORTION.fixed_tier == Tier.FOUNDATION
    assert proportion.TOPIC_INVERSE_PROPORTION.fixed_tier == Tier.FOUNDATION
    assert proportion.TOPIC_ALGEBRAIC_DIRECT_PROPORTION.fixed_tier == Tier.HIGHER
    assert proportion.TOPIC_ALGEBRAIC_INVERSE_PROPORTION.fixed_tier == Tier.HIGHER


def test_modelled_example_topics_have_generator_wired():
    for t in (
        proportion.TOPIC_DIRECT_PROPORTION,
        proportion.TOPIC_INVERSE_PROPORTION,
        proportion.TOPIC_ALGEBRAIC_DIRECT_PROPORTION,
        proportion.TOPIC_ALGEBRAIC_INVERSE_PROPORTION,
    ):
        assert t.generate_modelled_example is not None


def test_modelled_example_direct_proportion_produces_verified_examples():
    rng = random.Random(402)
    for _ in range(TRIALS):
        example = proportion.generate_modelled_example_direct_proportion(Tier.FOUNDATION, rng)
        assert example.topic_id == "direct_proportion_F"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_inverse_proportion_produces_verified_examples():
    rng = random.Random(403)
    for _ in range(TRIALS):
        example = proportion.generate_modelled_example_inverse_proportion(Tier.FOUNDATION, rng)
        assert example.topic_id == "inverse_proportion_F"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_algebraic_direct_proportion_produces_verified_examples():
    rng = random.Random(404)
    for _ in range(TRIALS):
        example = proportion.generate_modelled_example_algebraic_direct_proportion(
            Tier.HIGHER, rng
        )
        assert example.topic_id == "algebraic_direct_proportion_H"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_modelled_example_algebraic_inverse_proportion_produces_verified_examples():
    rng = random.Random(405)
    for _ in range(TRIALS):
        example = proportion.generate_modelled_example_algebraic_inverse_proportion(
            Tier.HIGHER, rng
        )
        assert example.topic_id == "algebraic_inverse_proportion_H"
        assert example.prompt
        assert len(example.worked_calculation) >= 2
        assert len(example.teaching_steps) >= 3
        assert example.final_answer


def test_direct_proportion_prompt_starts_with_if():
    rng = random.Random(406)
    for _ in range(TRIALS):
        q = proportion.generate_direct_proportion(Tier.FOUNDATION, rng)
        assert q.prompt.startswith("If ")


def test_direct_proportion_currency_names_the_symbol_after_the_bare_word():
    rng = random.Random(407)
    found_currency = False
    for _ in range(TRIALS):
        q = proportion.generate_direct_proportion(Tier.FOUNDATION, rng)
        if q.dedup_key.startswith("direct:currency"):
            found_currency = True
            assert "dollars ($)" in q.prompt
    assert found_currency


_BARE_GRAMS_RE = re.compile(r"(\d+)g\b")
_KG_CONVERSION_CLAUSE_RE = re.compile(r"\d+(\.\d+)?kg = \d+g|\d+g = \d+(\.\d+)?kg")


def test_direct_proportion_recipe_quantities_at_or_above_1000_display_in_kg():
    rng = random.Random(408)
    found_a_conversion = False
    for _ in range(500):
        q = proportion.generate_direct_proportion(Tier.FOUNDATION, rng)
        if not q.dedup_key.startswith("direct:recipe"):
            continue
        for line in (q.prompt, q.final_answer):
            for m in _BARE_GRAMS_RE.finditer(line):
                assert int(m.group(1)) < 1000
        if any(_KG_CONVERSION_CLAUSE_RE.search(step) for step in q.solution_steps):
            found_a_conversion = True
    assert found_a_conversion
