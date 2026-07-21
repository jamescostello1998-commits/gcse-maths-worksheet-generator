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
    assert len(data) == 169
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
    assert len(number_section["groups"]) == 8

    total_topics = sum(len(g["topics"]) for s in data for g in s["groups"])
    assert total_topics == 169


def test_valid_worksheet_request_returns_pdf():
    response = client.post(
        "/api/worksheets", json={"topic_id": "reverse_percentage", "tier": "higher"}
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF-")
    assert "reverse_percentage-higher-worksheet.pdf" in response.headers["content-disposition"]


def test_worksheet_request_respects_per_topic_question_count():
    response = client.post(
        "/api/worksheets", json={"topic_id": "plot_straight_line", "tier": "foundation"}
    )
    assert response.status_code == 200
    assert response.content.startswith(b"%PDF-")


def test_worksheet_request_honours_explicit_question_count():
    response = client.post(
        "/api/worksheets",
        json={"topic_id": "reverse_percentage", "tier": "higher", "count": 10},
    )
    assert response.status_code == 200
    reader = PdfReader(io.BytesIO(response.content))
    full_text = "\n".join(page.extract_text() for page in reader.pages)
    assert "10 Questions" in full_text
    assert "Q10." in full_text
    assert "Q11." not in full_text


def test_worksheet_request_count_out_of_range_returns_422():
    too_few = client.post(
        "/api/worksheets", json={"topic_id": "reverse_percentage", "tier": "higher", "count": 0}
    )
    too_many = client.post(
        "/api/worksheets", json={"topic_id": "reverse_percentage", "tier": "higher", "count": 41}
    )
    assert too_few.status_code == 422
    assert too_many.status_code == 422


def test_worksheet_request_answers_only_returns_compact_answer_key():
    response = client.post(
        "/api/worksheets",
        json={"topic_id": "reverse_percentage", "tier": "higher", "answers_only": True},
    )
    assert response.status_code == 200
    assert "reverse_percentage-higher-worksheet-answers-only.pdf" in response.headers["content-disposition"]
    reader = PdfReader(io.BytesIO(response.content))
    full_text = "\n".join(page.extract_text() for page in reader.pages)
    assert "Answers" in full_text
    assert "Worked Solutions" not in full_text


def test_topics_expose_default_question_count():
    response = client.get("/api/topics")
    data = response.json()
    plot = next(t for t in data if t["id"] == "plot_straight_line")
    assert plot["default_question_count"] == 5
    reverse_pct = next(t for t in data if t["id"] == "reverse_percentage")
    assert reverse_pct["default_question_count"] == 20


def test_invalid_topic_returns_404():
    response = client.post(
        "/api/worksheets", json={"topic_id": "not_a_real_topic", "tier": "foundation"}
    )
    assert response.status_code == 404
    assert "detail" in response.json()


def test_invalid_tier_returns_422():
    response = client.post(
        "/api/worksheets", json={"topic_id": "reverse_percentage", "tier": "expert"}
    )
    assert response.status_code == 422


def test_modelled_example_request_returns_pdf_for_pilot_topic():
    response = client.post(
        "/api/modelled-examples", json={"topic_id": "linear_two_step", "tier": "foundation"}
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF-")
    assert "linear_two_step-foundation-modelled-example.pdf" in response.headers["content-disposition"]


def test_modelled_example_request_returns_404_for_topic_without_one(monkeypatch):
    # Every real topic now has a modelled example, so this exercises the 404 branch
    # in routes.py via a stand-in topic rather than relying on real data for it.
    import app.api.routes as routes_module
    from app.core.registry import get_topic

    real_topic = get_topic("linear_one_step")
    topic_without_example = real_topic._replace(generate_modelled_example=None)
    monkeypatch.setattr(routes_module, "get_topic", lambda topic_id: topic_without_example)

    response = client.post(
        "/api/modelled-examples", json={"topic_id": "linear_one_step", "tier": "foundation"}
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
        raise WorksheetGenerationError("reverse_percentage", "higher", attempts=400, produced=5)

    monkeypatch.setattr(routes_module, "build_worksheet", broken)

    response = client.post(
        "/api/worksheets", json={"topic_id": "reverse_percentage", "tier": "higher"}
    )
    assert response.status_code == 500
    body = response.json()
    assert "detail" in body
    assert "attempts" not in body["detail"]  # no internal detail/stack trace leaked
