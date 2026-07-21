from datetime import datetime, timezone

import pytest
from pypdf import PdfReader
import io

from app.core.errors import PdfRenderError
from app.core.models import DiagramSpec, Question, Tier, Worksheet
from app.pdf.renderer import render_worksheet


def _make_worksheet(n=20) -> Worksheet:
    questions = tuple(
        Question(
            topic_id="linear_equations",
            tier=Tier.FOUNDATION,
            prompt=f"Solve: {i}x + 1 = {i + 1}",
            solution_steps=(f"Subtract 1: {i}x = {i}", f"Divide by {i}: x = 1"),
            final_answer="1",
            dedup_key=str(i),
        )
        for i in range(1, n + 1)
    )
    return Worksheet(
        topic_id="linear_equations",
        topic_name="Solving Linear Equations",
        tier=Tier.FOUNDATION,
        questions=questions,
        generated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


def test_renders_non_empty_pdf_bytes():
    worksheet = _make_worksheet()
    pdf_bytes = render_worksheet(worksheet)
    assert len(pdf_bytes) > 0
    assert pdf_bytes.startswith(b"%PDF-")


def test_contains_worked_solutions_heading_and_all_question_numbers():
    worksheet = _make_worksheet()
    pdf_bytes = render_worksheet(worksheet)
    reader = PdfReader(io.BytesIO(pdf_bytes))
    full_text = "\n".join(page.extract_text() for page in reader.pages)

    assert "Worked Solutions" in full_text
    assert "Q1." in full_text
    assert "Q20" in full_text
    assert worksheet.topic_name in full_text


def test_renders_worksheet_with_a_diagram_bearing_question():
    diagram_question = Question(
        topic_id="area_rectangle",
        tier=Tier.FOUNDATION,
        prompt="A rectangle has length 10 cm and width 6 cm. Find its area.",
        solution_steps=("Area = length × width = 10 × 6 = 60 cm²",),
        final_answer="60 cm²",
        dedup_key="diagram-test",
        diagram=DiagramSpec(
            kind="rectangle",
            params={"width": 10, "height": 6, "width_label": "10 cm", "height_label": "6 cm"},
        ),
    )
    worksheet = Worksheet(
        topic_id="area_rectangle",
        topic_name="Rectangles",
        tier=Tier.FOUNDATION,
        questions=(diagram_question,) + tuple(_make_worksheet(19).questions),
    )
    pdf_bytes = render_worksheet(worksheet)
    assert len(pdf_bytes) > 0
    assert pdf_bytes.startswith(b"%PDF-")


def test_answers_only_renders_compact_answer_key_not_worked_solutions():
    worksheet = _make_worksheet()
    pdf_bytes = render_worksheet(worksheet, answers_only=True)
    reader = PdfReader(io.BytesIO(pdf_bytes))
    full_text = "\n".join(page.extract_text() for page in reader.pages)

    assert "Answers" in full_text
    assert "Worked Solutions" not in full_text
    assert "Q1." in full_text
    assert "Q20" in full_text
    # The worked-solution steps text must not leak into the answers-only page.
    assert "Subtract 1:" not in full_text


def test_pdf_render_error_wraps_unexpected_failures(monkeypatch):
    import app.pdf.renderer as renderer_module

    def broken(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(renderer_module, "_question_block", broken)

    with pytest.raises(PdfRenderError):
        render_worksheet(_make_worksheet())
