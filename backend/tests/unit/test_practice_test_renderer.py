import fitz

from app.pdf.practice_test_renderer import render_mark_scheme, render_practice_test_paper
from app.practice_tests.loader import get_practice_test, list_practice_tests


def test_render_practice_test_paper_produces_a_valid_pdf_for_every_paper():
    for paper in list_practice_tests():
        pdf_bytes = render_practice_test_paper(paper)
        assert pdf_bytes.startswith(b"%PDF-")
        assert len(pdf_bytes) > 1000


def test_render_mark_scheme_produces_a_valid_pdf_for_every_paper():
    for paper in list_practice_tests():
        pdf_bytes = render_mark_scheme(paper)
        assert pdf_bytes.startswith(b"%PDF-")
        assert len(pdf_bytes) > 1000


def _text_of(pdf_bytes: bytes) -> str:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    return "\n".join(page.get_text() for page in doc)


def test_paper_includes_a_tier_appropriate_formulae_sheet():
    foundation_text = _text_of(render_practice_test_paper(get_practice_test("foundation-01-paper1")))
    higher_text = _text_of(render_practice_test_paper(get_practice_test("higher-01-paper1")))

    assert "Formulae Sheet" in foundation_text
    assert "Formulae Sheet" in higher_text
    assert "Quadratic Formula" not in foundation_text
    assert "Quadratic Formula" in higher_text
    assert "Sine Rule" in higher_text


def test_mark_scheme_uses_current_ocr_conventions_not_the_retired_cao_tag():
    for paper_id in ("foundation-01-paper1", "higher-01-paper1"):
        text = _text_of(render_mark_scheme(get_practice_test(paper_id)))
        assert "M marks are for using a correct method" in text
        assert "oe = or equivalent" in text
        assert "(cao)" not in text
        assert "cao" not in text
