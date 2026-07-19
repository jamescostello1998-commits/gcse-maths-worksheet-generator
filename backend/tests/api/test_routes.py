import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_topics_returns_all_59_topics():
    response = client.get("/api/topics")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 59
    for topic in data:
        assert set(topic.keys()) == {"id", "name", "description", "fixed_tier"}


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
    assert len(number_section["groups"]) == 4

    total_topics = sum(len(g["topics"]) for s in data for g in s["groups"])
    assert total_topics == 59


def test_valid_worksheet_request_returns_pdf():
    response = client.post(
        "/api/worksheets", json={"topic_id": "reverse_percentage", "tier": "higher"}
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF-")
    assert "reverse_percentage-higher-worksheet.pdf" in response.headers["content-disposition"]


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
