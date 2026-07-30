import random

from app.core.models import Tier
from app.practice_tests.topic_selection import (
    CALCULATOR_ONLY_TOPIC_IDS,
    CORE_TOPIC_IDS,
    NICHE_TOPIC_IDS,
    SECTION_TARGET_MARKS,
    eligible_topics_by_section,
    select_paper_topics,
    topic_priority,
    typical_marks_for,
)


def test_core_and_niche_topic_ids_are_real_and_do_not_overlap():
    from app.core.registry import list_topics

    all_ids = {t.id for t in list_topics()}
    assert CORE_TOPIC_IDS <= all_ids
    assert NICHE_TOPIC_IDS <= all_ids
    assert not (CORE_TOPIC_IDS & NICHE_TOPIC_IDS)


def test_calculator_only_topic_ids_are_real():
    from app.core.registry import list_topics

    all_ids = {t.id for t in list_topics()}
    assert CALCULATOR_ONLY_TOPIC_IDS <= all_ids


def test_eligible_topics_by_section_excludes_calculator_only_topics_when_disallowed():
    for tier in (Tier.FOUNDATION, Tier.HIGHER):
        calc_by_section = eligible_topics_by_section(tier)
        noncalc_by_section = eligible_topics_by_section(tier, calculator_allowed=False)

        calc_ids = {t.id for topics in calc_by_section.values() for t in topics}
        noncalc_ids = {t.id for topics in noncalc_by_section.values() for t in topics}

        # The non-calculator pool is a strict subset with every
        # calculator-only topic (for this tier) removed, and nothing else
        # changed.
        assert noncalc_ids <= calc_ids
        assert not (noncalc_ids & CALCULATOR_ONLY_TOPIC_IDS)
        assert calc_ids - noncalc_ids == calc_ids & CALCULATOR_ONLY_TOPIC_IDS


def test_select_paper_topics_never_picks_a_calculator_only_topic_from_a_filtered_pool():
    for tier in (Tier.FOUNDATION, Tier.HIGHER):
        by_section = eligible_topics_by_section(tier, calculator_allowed=False)
        typical_marks = {
            t.id: typical_marks_for(t, random.Random(f"typical-{t.id}"))
            for topics in by_section.values()
            for t in topics
        }
        for seed in range(5):
            rng = random.Random(f"noncalc-paper-{tier.value}-{seed}")
            chosen = select_paper_topics(tier, rng, typical_marks, by_section)
            assert not any(t.id in CALCULATOR_ONLY_TOPIC_IDS for t in chosen)


def test_topic_priority_defaults_to_common():
    assert topic_priority("fractions_add_subtract") == "core"
    assert topic_priority("circle_theorems") == "niche"
    assert topic_priority("some_topic_never_tagged") == "common"


def test_eligible_topics_by_section_only_includes_the_requested_tier():
    for tier in (Tier.FOUNDATION, Tier.HIGHER):
        by_section = eligible_topics_by_section(tier)
        assert set(by_section.keys()) == set(SECTION_TARGET_MARKS.keys())
        for topics in by_section.values():
            assert all(t.fixed_tier == tier for t in topics)


def test_select_paper_topics_sums_to_exactly_100_marks_with_no_repeats():
    for tier in (Tier.FOUNDATION, Tier.HIGHER):
        by_section = eligible_topics_by_section(tier)
        typical_marks = {
            t.id: typical_marks_for(t, random.Random(f"typical-{t.id}"))
            for topics in by_section.values()
            for t in topics
        }
        for seed in range(10):
            rng = random.Random(f"paper-{tier.value}-{seed}")
            chosen = select_paper_topics(tier, rng, typical_marks, by_section)
            assert sum(typical_marks[t.id] for t in chosen) == 100
            ids = [t.id for t in chosen]
            assert len(ids) == len(set(ids))
