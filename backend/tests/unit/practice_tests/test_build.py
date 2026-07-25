from app.core.models import Tier
from app.practice_tests.build import build_papers


def test_build_papers_produces_20_papers_summing_to_exactly_100_marks():
    papers = build_papers()
    assert len(papers) == 20
    foundation = [p for p in papers if p.tier == Tier.FOUNDATION]
    higher = [p for p in papers if p.tier == Tier.HIGHER]
    assert len(foundation) == 10
    assert len(higher) == 10
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

    first = build_papers(["foundation-01", "higher-01"])
    second = build_papers(["foundation-01", "higher-01"])
    for a, b in zip(first, second):
        assert json.dumps(paper_to_dict(a), sort_keys=True) == json.dumps(paper_to_dict(b), sort_keys=True)


def test_build_papers_can_build_a_subset():
    papers = build_papers(["foundation-03"])
    assert len(papers) == 1
    assert papers[0].id == "foundation-03"
