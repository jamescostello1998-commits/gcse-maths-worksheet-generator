import io

import pytest
from fastapi.testclient import TestClient
from pypdf import PdfReader

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_topics_returns_all_topics():
    response = client.get("/api/topics")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 313
    for topic in data:
        assert set(topic.keys()) == {
            "id", "name", "description", "fixed_tier", "has_modelled_example", "default_question_count",
        }


def test_sections_returns_six_sections_in_declared_order():
    response = client.get("/api/sections")
    assert response.status_code == 200
    data = response.json()
    assert [s["id"] for s in data] == [
        "number",
        "algebra",
        "ratio_proportion",
        "geometry",
        "probability",
        "statistics",
    ]

    number_section = next(s for s in data if s["id"] == "number")
    assert len(number_section["groups"]) == 9

    total_topics = sum(len(g["topics"]) for s in data for g in s["groups"])
    assert total_topics == 313


def test_valid_worksheet_request_returns_pdf():
    response = client.post(
        "/api/worksheets", json={"topic_id": "reverse_percentage_H", "tier": "higher"}
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF-")
    assert "reverse_percentage_H-higher-worksheet.pdf" in response.headers["content-disposition"]


def test_worksheet_request_respects_per_topic_question_count():
    response = client.post(
        "/api/worksheets", json={"topic_id": "plot_straight_line_F", "tier": "foundation"}
    )
    assert response.status_code == 200
    assert response.content.startswith(b"%PDF-")


def test_worksheet_request_honours_explicit_question_count():
    response = client.post(
        "/api/worksheets",
        json={"topic_id": "reverse_percentage_H", "tier": "higher", "count": 10},
    )
    assert response.status_code == 200
    reader = PdfReader(io.BytesIO(response.content))
    full_text = "\n".join(page.extract_text() for page in reader.pages)
    assert "10 Questions" in full_text
    assert "Q10." in full_text
    assert "Q11." not in full_text


def test_worksheet_request_count_out_of_range_returns_422():
    too_few = client.post(
        "/api/worksheets", json={"topic_id": "reverse_percentage_H", "tier": "higher", "count": 0}
    )
    too_many = client.post(
        "/api/worksheets", json={"topic_id": "reverse_percentage_H", "tier": "higher", "count": 41}
    )
    assert too_few.status_code == 422
    assert too_many.status_code == 422


def test_worksheet_request_answers_only_returns_compact_answer_key():
    response = client.post(
        "/api/worksheets",
        json={"topic_id": "reverse_percentage_H", "tier": "higher", "answers_only": True},
    )
    assert response.status_code == 200
    assert "reverse_percentage_H-higher-worksheet-answers-only.pdf" in response.headers["content-disposition"]
    reader = PdfReader(io.BytesIO(response.content))
    full_text = "\n".join(page.extract_text() for page in reader.pages)
    assert "Answers" in full_text
    assert "Worked Solutions" not in full_text


def test_topics_expose_default_question_count():
    response = client.get("/api/topics")
    data = response.json()
    plot = next(t for t in data if t["id"] == "plot_straight_line_F")
    assert plot["default_question_count"] == 5
    reverse_pct = next(t for t in data if t["id"] == "reverse_percentage_H")
    assert reverse_pct["default_question_count"] == 20


def test_invalid_topic_returns_404():
    response = client.post(
        "/api/worksheets", json={"topic_id": "not_a_real_topic", "tier": "foundation"}
    )
    assert response.status_code == 404
    assert "detail" in response.json()


def test_invalid_tier_returns_422():
    response = client.post(
        "/api/worksheets", json={"topic_id": "reverse_percentage_H", "tier": "expert"}
    )
    assert response.status_code == 422


def test_modelled_example_request_returns_pdf_for_pilot_topic():
    response = client.post(
        "/api/modelled-examples", json={"topic_id": "linear_two_step_F", "tier": "foundation"}
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF-")
    assert "linear_two_step_F-foundation-modelled-example.pdf" in response.headers["content-disposition"]


def test_modelled_example_request_returns_404_for_topic_without_one(monkeypatch):
    # Every real topic now has a modelled example, so this exercises the 404 branch
    # in routes.py via a stand-in topic rather than relying on real data for it.
    import app.api.routes as routes_module
    from app.core.registry import get_topic

    real_topic = get_topic("linear_one_step_F")
    topic_without_example = real_topic._replace(generate_modelled_example=None)
    monkeypatch.setattr(routes_module, "get_topic", lambda topic_id: topic_without_example)

    response = client.post(
        "/api/modelled-examples", json={"topic_id": "linear_one_step_F", "tier": "foundation"}
    )
    assert response.status_code == 404
    assert "detail" in response.json()


def test_modelled_example_request_returns_404_for_unknown_topic():
    response = client.post(
        "/api/modelled-examples", json={"topic_id": "not_a_real_topic", "tier": "foundation"}
    )
    assert response.status_code == 404


def test_worksheet_generation_error_returns_500(monkeypatch):
    import app.api.routes as routes_module
    from app.core.errors import WorksheetGenerationError

    def broken(*args, **kwargs):
        raise WorksheetGenerationError("reverse_percentage_H", "higher", attempts=400, produced=5)

    monkeypatch.setattr(routes_module, "build_worksheet", broken)

    response = client.post(
        "/api/worksheets", json={"topic_id": "reverse_percentage_H", "tier": "higher"}
    )
    assert response.status_code == 500
    body = response.json()
    assert "detail" in body
    assert "attempts" not in body["detail"]  # no internal detail/stack trace leaked


def test_practice_tests_returns_all_60_papers():
    response = client.get("/api/practice-tests")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 60
    for paper in data:
        assert set(paper.keys()) == {
            "id", "name", "tier", "sitting_id", "paper_number", "calculator_allowed",
            "total_marks", "question_count",
        }
        assert paper["total_marks"] == 100


def test_practice_tests_filters_by_tier():
    response = client.get("/api/practice-tests", params={"tier": "higher"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 30
    assert all(p["tier"] == "higher" for p in data)


def test_practice_test_paper_returns_pdf():
    response = client.get("/api/practice-tests/foundation-01-paper1/paper")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF-")
    assert "foundation-01-paper1-test-paper.pdf" in response.headers["content-disposition"]


def test_practice_test_mark_scheme_returns_pdf():
    response = client.get("/api/practice-tests/higher-05-paper2/mark-scheme")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF-")
    assert "higher-05-paper2-mark-scheme.pdf" in response.headers["content-disposition"]


def test_unknown_practice_test_returns_404():
    paper_response = client.get("/api/practice-tests/not-a-real-paper/paper")
    mark_scheme_response = client.get("/api/practice-tests/not-a-real-paper/mark-scheme")
    assert paper_response.status_code == 404
    assert mark_scheme_response.status_code == 404
    assert "detail" in paper_response.json()


BELL_TASKS_TOPIC_IDS = [
    "angles_triangle_F",
    "area_rectangle_F",
    "fractions_add_subtract_F",
    "linear_two_step_F",
    "probability_single_event_F",
    "bar_chart_construct_F",
]


def test_bell_tasks_valid_request_returns_pptx():
    response = client.post("/api/bell-tasks", json={"topic_ids": BELL_TASKS_TOPIC_IDS})
    assert response.status_code == 200
    assert response.headers["content-type"] == (
        "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )
    assert response.content[:2] == b"PK"  # a .pptx is a zip archive
    assert "bell-tasks-" in response.headers["content-disposition"]
    assert ".pptx" in response.headers["content-disposition"]


def test_bell_tasks_wrong_topic_count_returns_422():
    too_few = client.post("/api/bell-tasks", json={"topic_ids": BELL_TASKS_TOPIC_IDS[:5]})
    too_many = client.post("/api/bell-tasks", json={"topic_ids": BELL_TASKS_TOPIC_IDS + ["fractions_simplify_F"]})
    assert too_few.status_code == 422
    assert too_many.status_code == 422


def test_bell_tasks_duplicate_topic_returns_422():
    duplicated = BELL_TASKS_TOPIC_IDS[:5] + [BELL_TASKS_TOPIC_IDS[0]]
    response = client.post("/api/bell-tasks", json={"topic_ids": duplicated})
    assert response.status_code == 422


def test_bell_tasks_unknown_topic_returns_404():
    bad = BELL_TASKS_TOPIC_IDS[:5] + ["not_a_real_topic"]
    response = client.post("/api/bell-tasks", json={"topic_ids": bad})
    assert response.status_code == 404
    assert "detail" in response.json()
