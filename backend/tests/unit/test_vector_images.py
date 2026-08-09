import os

from PIL import Image
from reportlab.lib.colors import HexColor

from app.pdf.vector_images import get_column_vector_image

INK = HexColor("#1a1a1a")
ACCENT = HexColor("#2f6f4f")


def test_returns_a_real_png_file_with_positive_dimensions():
    img = get_column_vector_image("2", "3", 11.5, False, INK)
    assert os.path.isfile(img.path)
    assert img.width_pt > 0
    assert img.height_pt > 0
    with Image.open(img.path) as pil_img:
        assert pil_img.mode == "RGBA"
        assert pil_img.width > 0
        assert pil_img.height > 0


def test_repeated_calls_with_identical_params_reuse_the_cached_file():
    first = get_column_vector_image("2", "3", 11.5, False, INK)
    second = get_column_vector_image("2", "3", 11.5, False, INK)
    assert first.path == second.path


def test_different_top_or_bottom_produces_different_files():
    a = get_column_vector_image("2", "3", 11.5, False, INK)
    b = get_column_vector_image("2", "4", 11.5, False, INK)
    c = get_column_vector_image("5", "3", 11.5, False, INK)
    assert len({a.path, b.path, c.path}) == 3


def test_wider_row_produces_a_wider_image_than_a_narrower_one():
    narrow = get_column_vector_image("2", "3", 11.5, False, INK)
    wide = get_column_vector_image("-128", "-256", 11.5, False, INK)
    assert wide.width_pt > narrow.width_pt


def test_larger_font_size_produces_a_larger_image():
    small = get_column_vector_image("2", "3", 9, False, INK)
    large = get_column_vector_image("2", "3", 18, False, INK)
    assert large.width_pt > small.width_pt
    assert large.height_pt > small.height_pt


def test_image_height_stays_close_to_a_single_line_of_leading():
    # This image is inherently taller than one text line (two stacked rows
    # plus overhanging brackets) - but it must stay close enough to a normal
    # line's own leading that no paragraph-style spacing changes are needed
    # wherever it's used inline (confirmed via a real rendered-PDF spike -
    # see mathtext.py's docstring). A generous multiple, not an exact bound.
    img = get_column_vector_image("-12", "34", 11.5, False, INK)
    assert img.height_pt < 11.5 * 1.8


def test_image_pixel_colour_matches_the_requested_colour():
    img = get_column_vector_image("2", "3", 20, False, ACCENT)
    with Image.open(img.path) as pil_img:
        pixels = pil_img.getdata()
        opaque = [p for p in pixels if p[3] > 0]
        assert opaque, "expected at least one non-transparent pixel"
        expected_rgb = (round(ACCENT.red * 255), round(ACCENT.green * 255), round(ACCENT.blue * 255))
        assert all(p[:3] == expected_rgb for p in opaque)


def test_negative_numbers_render_without_error():
    img = get_column_vector_image("-2", "5", 11.5, False, INK)
    assert os.path.isfile(img.path)
    assert img.width_pt > 0
