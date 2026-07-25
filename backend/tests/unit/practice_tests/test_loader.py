import pytest

from app.practice_tests.loader import PracticeTestNotFoundError, get_practice_test, list_practice_tests


def test_list_practice_tests_returns_the_20_committed_papers():
    papers = list_practice_tests()
    assert len(papers) == 20
    ids = {p.id for p in papers}
    assert ids == {f"foundation-{i:02d}" for i in range(1, 11)} | {f"higher-{i:02d}" for i in range(1, 11)}


def test_get_practice_test_returns_the_matching_paper():
    paper = get_practice_test("foundation-01")
    assert paper.id == "foundation-01"
    assert paper.total_marks == 100


def test_get_practice_test_raises_for_unknown_id():
    with pytest.raises(PracticeTestNotFoundError):
        get_practice_test("not-a-real-paper")
