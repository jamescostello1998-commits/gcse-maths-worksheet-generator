from app.pdf.practice_test_renderer import render_mark_scheme, render_practice_test_paper
from app.practice_tests.loader import list_practice_tests


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
