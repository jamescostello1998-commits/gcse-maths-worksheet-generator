from app.core.models import Tier
from app.practice_tests.build import build_papers


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
