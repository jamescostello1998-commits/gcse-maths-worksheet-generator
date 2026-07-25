"""Loads the 20 frozen practice-test JSON files into PracticeTestPaper
objects, once at import time - a small, fixed dataset, no lazy loading
needed. Mirrors app/core/registry.py's get_topic()/list_topics() shape."""

import json
from pathlib import Path

from app.practice_tests.models import PracticeTestPaper, paper_from_dict

DATA_DIR = Path(__file__).parent / "data"


class PracticeTestNotFoundError(Exception):
    def __init__(self, paper_id: str):
        self.paper_id = paper_id
        super().__init__(f"Unknown practice test '{paper_id}'")


def _load_all() -> dict[str, PracticeTestPaper]:
    papers: dict[str, PracticeTestPaper] = {}
    if not DATA_DIR.exists():
        return papers
    for path in sorted(DATA_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        paper = paper_from_dict(data)
        papers[paper.id] = paper
    return papers


_PAPERS: dict[str, PracticeTestPaper] = _load_all()


def list_practice_tests() -> list[PracticeTestPaper]:
    return list(_PAPERS.values())


def get_practice_test(paper_id: str) -> PracticeTestPaper:
    try:
        return _PAPERS[paper_id]
    except KeyError:
        raise PracticeTestNotFoundError(paper_id) from None


def reload() -> None:
    """Used by tests / after running build.py in the same process."""
    global _PAPERS
    _PAPERS = _load_all()
