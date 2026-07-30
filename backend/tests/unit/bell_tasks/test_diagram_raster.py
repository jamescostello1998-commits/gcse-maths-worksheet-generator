import io
import random

from PIL import Image

from app.bell_tasks.diagram_raster import rasterize_drawing
from app.core.registry import get_topic
from app.pdf.diagrams import render_diagram

# A spread of genuinely different diagram kinds/shapes, all confirmed to exist
# in the registry - triangle, rectangle, circle-theorem, and a stats chart.
DIAGRAM_TOPIC_IDS = [
    "angles_triangle",
    "area_rectangle",
    "circle_theorems",
    "bar_chart_construct",
]


def _first_diagram_spec(topic_id: str):
    topic = get_topic(topic_id)
    for seed in range(50):
        question = topic.generate(topic.fixed_tier, random.Random(seed))
        if question.diagram is not None:
            return question.diagram
    raise AssertionError(f"{topic_id} never produced a diagram across 50 seeds")


def test_rasterize_drawing_produces_nonblank_png():
    for topic_id in DIAGRAM_TOPIC_IDS:
        spec = _first_diagram_spec(topic_id)
        drawing = render_diagram(spec)
        png_bytes = rasterize_drawing(drawing, dpi=150)

        assert png_bytes[:8] == b"\x89PNG\r\n\x1a\n", topic_id

        img = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
        assert img.width > 0 and img.height > 0, topic_id

        # Confirm it isn't blank: some pixel must have non-zero alpha (something drawn).
        alpha_channel = img.getchannel("A")
        assert alpha_channel.getextrema()[1] > 0, f"{topic_id} rasterized as fully transparent/blank"


def test_rasterize_drawing_scales_with_dpi():
    spec = _first_diagram_spec("angles_triangle")
    drawing = render_diagram(spec)

    png_150 = rasterize_drawing(drawing, dpi=150)
    png_300 = rasterize_drawing(drawing, dpi=300)

    def _dimensions(png_bytes: bytes) -> tuple[int, int]:
        img = Image.open(io.BytesIO(png_bytes))
        return img.width, img.height

    w150, h150 = _dimensions(png_150)
    w300, h300 = _dimensions(png_300)

    # Doubling DPI should roughly double pixel dimensions.
    assert abs(w300 / w150 - 2.0) < 0.05
    assert abs(h300 / h150 - 2.0) < 0.05
