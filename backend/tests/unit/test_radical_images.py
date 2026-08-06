import os

from PIL import Image
from reportlab.lib.colors import HexColor

from app.pdf.radical_images import get_radical_image

INK = HexColor("#1a1a1a")
ACCENT = HexColor("#2f6f4f")


def test_returns_a_real_png_file_with_positive_dimensions():
    img = get_radical_image("72", 11.5, False, INK)
    assert os.path.isfile(img.path)
    assert img.width_pt > 0
    assert img.height_pt > 0
    with Image.open(img.path) as pil_img:
        assert pil_img.mode == "RGBA"
        assert pil_img.width > 0
        assert pil_img.height > 0


def test_repeated_calls_with_identical_params_reuse_the_cached_file():
    first = get_radical_image("5", 11.5, False, INK)
    second = get_radical_image("5", 11.5, False, INK)
    assert first.path == second.path


def test_different_radicand_produces_different_files():
    a = get_radical_image("5", 11.5, False, INK)
    b = get_radical_image("72", 11.5, False, INK)
    assert a.path != b.path


def test_wider_radicand_produces_a_wider_image_than_a_narrower_one():
    narrow = get_radical_image("5", 11.5, False, INK)
    wide = get_radical_image("14400", 11.5, False, INK)
    assert wide.width_pt > narrow.width_pt


def test_larger_font_size_produces_a_larger_image():
    small = get_radical_image("72", 9, False, INK)
    large = get_radical_image("72", 18, False, INK)
    assert large.width_pt > small.width_pt
    assert large.height_pt > small.height_pt


def test_image_pixel_colour_matches_the_requested_colour():
    img = get_radical_image("5", 20, False, ACCENT)
    with Image.open(img.path) as pil_img:
        pixels = pil_img.getdata()
        opaque = [p for p in pixels if p[3] > 0]
        assert opaque, "expected at least one non-transparent pixel"
        expected_rgb = (round(ACCENT.red * 255), round(ACCENT.green * 255), round(ACCENT.blue * 255))
        assert all(p[:3] == expected_rgb for p in opaque)


def test_bold_uses_a_different_font_and_produces_a_different_file():
    regular = get_radical_image("5", 11.5, False, INK)
    bold = get_radical_image("5", 11.5, True, INK)
    assert regular.path != bold.path
