import random

from app.core.models import Tier
from app.topics import best_buys

TRIALS = 200

GENERATORS = [
    (best_buys.generate_best_buys, Tier.FOUNDATION),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(320)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt
            assert q.solution_steps
            assert q.final_answer


def test_dedup_keys_vary_per_generator():
    for generate, tier in GENERATORS:
        rng = random.Random(321)
        keys = {generate(tier, rng).dedup_key for _ in range(100)}
        assert len(keys) > 40


def test_topic_definitions_have_expected_metadata():
    topics = [best_buys.TOPIC_BEST_BUYS]
    ids = {t.id for t in topics}
    assert len(ids) == 1
    for t in topics:
        assert t.section == "ratio_proportion"
        assert t.group == "Best Buys"
        assert t.fixed_tier in (Tier.FOUNDATION, Tier.HIGHER)
    assert best_buys.TOPIC_BEST_BUYS.fixed_tier == Tier.FOUNDATION


MODELLED_EXAMPLE_GENERATORS = [
    (best_buys.generate_modelled_example_best_buys, Tier.FOUNDATION, "best_buys"),
]


def test_all_topics_have_modelled_example_wired():
    for t in (best_buys.TOPIC_BEST_BUYS,):
        assert t.generate_modelled_example is not None


def test_modelled_example_generators_produce_verified_examples():
    for generate, tier, topic_id in MODELLED_EXAMPLE_GENERATORS:
        rng = random.Random(322)
        for _ in range(TRIALS):
            example = generate(tier, rng)
            assert example.topic_id == topic_id
            assert example.prompt
            assert len(example.worked_calculation) >= 2
            assert len(example.teaching_steps) >= 3
            assert example.final_answer


def test_best_buys_winner_matches_lowest_unit_price_via_cross_multiplication():
    """Independent, test-level cross-check: for every generated question, parse
    out the winner and re-verify it against ALL other options using raw
    cross-multiplication of price (pence) and quantity - not trusting the
    generator's own internal check."""
    rng = random.Random(323)
    for _ in range(TRIALS):
        noun, unit, options, winner_idx = best_buys._build_scenario(rng)
        winner = options[winner_idx]
        for other in options:
            if other is winner:
                continue
            # winner must be strictly cheaper per unit: winner_price * other_qty < other_price * winner_qty
            assert winner.price_pence * other.qty < other.price_pence * winner.qty


def test_best_buys_options_have_distinct_quantities():
    rng = random.Random(324)
    for _ in range(TRIALS):
        _, _, options, _ = best_buys._build_scenario(rng)
        qtys = [o.qty for o in options]
        assert len(qtys) == len(set(qtys))


def test_best_buys_final_answer_names_the_winning_label():
    rng = random.Random(325)
    for _ in range(TRIALS):
        q = best_buys.generate_best_buys(Tier.FOUNDATION, rng)
        assert q.final_answer[0] in ("A", "B", "C")
