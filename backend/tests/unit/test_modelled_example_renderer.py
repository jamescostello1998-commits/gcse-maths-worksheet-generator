import random

from app.core.registry import list_topics
from app.pdf.modelled_example_renderer import _steps_shown_count, render_modelled_example
from app.worksheet.builder import build_worksheet


def test_every_topic_is_flagged_with_a_modelled_example():
    # The pilot (6 topics) has been rolled out to the full curriculum.
    topics = list_topics()
    assert len(topics) == 160
    for t in topics:
        assert t.generate_modelled_example is not None


def test_render_modelled_example_produces_a_valid_pdf_for_every_topic():
    for topic in list_topics():
        rng = random.Random(42)
        example = topic.generate_modelled_example(topic.fixed_tier, rng)
        practice = build_worksheet(topic.id, topic.fixed_tier, count=5, rng=rng)
        pdf_bytes = render_modelled_example(topic.display_name, topic.fixed_tier, example, practice.questions)
        assert pdf_bytes.startswith(b"%PDF-")
        assert len(pdf_bytes) > 1000


def test_steps_shown_count_fades_backward_and_ends_independent():
    for n in (2, 3, 4, 5):
        counts = [_steps_shown_count(i, n) for i in range(5)]
        # Q1 shows everything, Q5 shows nothing, and it never increases along the way.
        assert counts[0] == n
        assert counts[-1] == 0
        assert counts == sorted(counts, reverse=True)


def test_steps_shown_count_never_exceeds_available_steps():
    for n in range(0, 8):
        for i in range(5):
            shown = _steps_shown_count(i, n)
            assert 0 <= shown <= n
