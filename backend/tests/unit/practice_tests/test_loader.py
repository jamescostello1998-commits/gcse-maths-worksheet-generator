import pytest

from app.practice_tests.loader import PracticeTestNotFoundError, get_practice_test, list_practice_tests


def test_list_practice_tests_returns_the_60_committed_papers():
    papers = list_practice_tests()
    assert len(papers) == 60
    ids = {p.id for p in papers}
    expected = {
        f"{tier}-{i:02d}-paper{n}"
        for tier in ("foundation", "higher")
        for i in range(1, 11)
        for n in (1, 2, 3)
    }
    assert ids == expected


def test_get_practice_test_returns_the_matching_paper():
    paper = get_practice_test("foundation-01-paper1")
    assert paper.id == "foundation-01-paper1"
    assert paper.sitting_id == "foundation-01"
    assert paper.paper_number == 1
    assert paper.total_marks == 100


def test_get_practice_test_raises_for_unknown_id():
    with pytest.raises(PracticeTestNotFoundError):
        get_practice_test("not-a-real-paper")
