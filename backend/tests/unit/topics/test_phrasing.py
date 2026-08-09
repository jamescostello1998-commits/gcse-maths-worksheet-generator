import random

from app.topics import phrasing


def test_evaluate_verb_returns_only_pool_members():
    rng = random.Random(1)
    seen = {phrasing.evaluate_verb(rng) for _ in range(200)}
    assert seen <= set(phrasing.EVALUATE_VERBS)
    assert len(seen) > 1  # confirms real variety across many draws


def test_amount_verb_returns_only_pool_members():
    rng = random.Random(2)
    seen = {phrasing.amount_verb(rng) for _ in range(200)}
    assert seen <= set(phrasing.AMOUNT_VERBS)
    assert len(seen) > 1


def test_simplify_verb_returns_only_pool_members():
    rng = random.Random(3)
    seen = {phrasing.simplify_verb(rng) for _ in range(200)}
    assert seen <= set(phrasing.SIMPLIFY_VERBS)
    assert len(seen) > 1


def test_convert_phrasing_pairs_are_never_mismatched():
    rng = random.Random(4)
    for _ in range(200):
        verb, prep = phrasing.convert_phrasing(rng)
        assert (verb, prep) in phrasing.CONVERT_PHRASINGS
