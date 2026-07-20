import random

from app.core.models import Tier
from app.core.registry import get_topic, list_topics
from app.pdf.modelled_example_renderer import _steps_shown_count, render_modelled_example
from app.worksheet.builder import build_worksheet

PILOT_TOPIC_IDS = [
    "fractions_add_subtract",
    "linear_two_step",
    "percentage_of_amount",
    "angles_triangle",
    "probability_single_event",
    "stats_mean_and_range",
]


def test_pilot_topics_are_flagged_with_a_modelled_example():
    topics = {t.id: t for t in list_topics()}
    for tid in PILOT_TOPIC_IDS:
        assert topics[tid].generate_modelled_example is not None


def test_non_pilot_topics_have_no_modelled_example():
    topics = list_topics()
    flagged = {t.id for t in topics if t.generate_modelled_example is not None}
    assert flagged == set(PILOT_TOPIC_IDS)


def test_render_modelled_example_produces_a_valid_pdf_for_every_pilot_topic():
    for tid in PILOT_TOPIC_IDS:
        topic = get_topic(tid)
        rng = random.Random(42)
        example = topic.generate_modelled_example(topic.fixed_tier, rng)
        practice = build_worksheet(tid, topic.fixed_tier, count=5, rng=rng)
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
