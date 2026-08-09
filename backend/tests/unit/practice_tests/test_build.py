from app.core.models import Tier
from app.practice_tests.build import build_papers
from app.practice_tests.topic_selection import CALCULATOR_ONLY_TOPIC_IDS


def test_build_papers_produces_60_papers_30_per_tier_10_sittings_of_3_papers_each():
    papers = build_papers()
    assert len(papers) == 60
    foundation = [p for p in papers if p.tier == Tier.FOUNDATION]
    higher = [p for p in papers if p.tier == Tier.HIGHER]
    assert len(foundation) == 30
    assert len(higher) == 30
    for tier_papers in (foundation, higher):
        sittings: dict[str, list[int]] = {}
        for paper in tier_papers:
            sittings.setdefault(paper.sitting_id, []).append(paper.paper_number)
        assert len(sittings) == 10
        for paper_numbers in sittings.values():
            assert sorted(paper_numbers) == [1, 2, 3]
    for paper in papers:
        assert paper.total_marks == 100
        assert sum(q.marks for q in paper.questions) == 100
        for question in paper.questions:
            assert sum(p.marks for p in question.mark_scheme) == question.marks
        topic_ids = [q.topic_id for q in paper.questions]
        assert len(topic_ids) == len(set(topic_ids))
        # Paper 2 of every sitting is real OCR's non-calculator paper
        # (Foundation Paper 2 / Higher Paper 5); Papers 1 and 3 stay
        # calculator-allowed.
        assert paper.calculator_allowed == (paper.paper_number != 2)
        if not paper.calculator_allowed:
            assert not any(tid in CALCULATOR_ONLY_TOPIC_IDS for tid in topic_ids)


def test_paper_2_never_contains_a_calculator_only_topic():
    papers = build_papers(
        [f"{tier}-{i:02d}-paper2" for tier in ("foundation", "higher") for i in range(1, 11)]
    )
    assert len(papers) == 20
    for paper in papers:
        assert paper.paper_number == 2
        assert paper.calculator_allowed is False
        topic_ids = {q.topic_id for q in paper.questions}
        assert not (topic_ids & CALCULATOR_ONLY_TOPIC_IDS)


def test_papers_1_and_3_are_calculator_allowed():
    papers = build_papers(["foundation-01-paper1", "foundation-01-paper3", "higher-02-paper1"])
    for paper in papers:
        assert paper.calculator_allowed is True


def test_build_papers_is_deterministic():
    from app.practice_tests.models import paper_to_dict
    import json

    first = build_papers(["foundation-01-paper1", "higher-01-paper1"])
    second = build_papers(["foundation-01-paper1", "higher-01-paper1"])
    for a, b in zip(first, second):
        assert json.dumps(paper_to_dict(a), sort_keys=True) == json.dumps(paper_to_dict(b), sort_keys=True)


def test_build_papers_can_build_a_subset():
    papers = build_papers(["foundation-03-paper2"])
    assert len(papers) == 1
    assert papers[0].id == "foundation-03-paper2"
    assert papers[0].sitting_id == "foundation-03"
    assert papers[0].paper_number == 2
