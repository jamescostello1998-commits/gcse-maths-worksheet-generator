"""Shared pools of opening-verb phrasing for question prompts, so a
worksheet doesn't repeat the exact same fixed word (e.g. always "Work out")
on every question. Each pool is a small set of GCSE-natural synonyms
appropriate to one sentence shape - not a single universal list, since not
every verb fits every grammatical pattern (e.g. "Evaluate" reads fine before
a bare expression, but "Convert" only makes sense before a conversion). A
topic generator calls the pool matching its own prompt's sentence shape and
picks one via `rng.choice`, exactly like any other randomised content in
these generators.

Piloted on the Number-section topics touched during a review-feedback pass
(fractions.py, decimals.py, powers_roots.py) - a full rollout across the
other ~250 topics is deliberately out of scope for now and flagged as a
follow-up (see CLAUDE.md's "Ideas for a future session").
"""

import random

# "{VERB} <expression>." - a direct instruction to compute a given expression.
EVALUATE_VERBS = ["Work out", "Calculate", "Evaluate"]

# "{VERB} <expression>." for a bare fraction-of-an-amount question - "Evaluate"
# reads awkwardly here ("Evaluate 3/4 of 60"), so this is its own smaller pool
# rather than reusing EVALUATE_VERBS.
AMOUNT_VERBS = ["Work out", "Calculate", "Find"]

# "{VERB} <expression>." - simplifying/reducing to lowest terms.
SIMPLIFY_VERBS = ["Simplify", "Fully simplify"]

# "{VERB} <this> {PREP} <that>." - converting between representations. Kept
# as (verb, preposition) pairs since "Write X AS Y" and "Convert X TO Y" take
# different prepositions - picking the verb and preposition independently
# could produce an ungrammatical combination.
CONVERT_PHRASINGS = [("Write", "as"), ("Convert", "to"), ("Express", "as")]


def evaluate_verb(rng: random.Random) -> str:
    return rng.choice(EVALUATE_VERBS)


def amount_verb(rng: random.Random) -> str:
    return rng.choice(AMOUNT_VERBS)


def simplify_verb(rng: random.Random) -> str:
    return rng.choice(SIMPLIFY_VERBS)


def convert_phrasing(rng: random.Random) -> tuple[str, str]:
    """Returns a (verb, preposition) pair, e.g. ("Convert", "to") - use as
    f"{verb} {x} {prep} {y}." Kept paired so the two can never mismatch."""
    return rng.choice(CONVERT_PHRASINGS)
