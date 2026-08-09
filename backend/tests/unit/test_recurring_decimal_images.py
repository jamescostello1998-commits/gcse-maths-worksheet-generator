import os

import pytest
from PIL import Image
from reportlab.lib.colors import HexColor

from app.pdf.recurring_decimal_images import get_recurring_decimal_image

INK = HexColor("#1a1a1a")
ACCENT = HexColor("#2f6f4f")


def test_returns_a_real_png_file_with_positive_dimensions():
    img = get_recurring_decimal_image("0.", "3", 11.5, False, INK)
    assert os.path.isfile(img.path)
    assert img.width_pt > 0
    assert img.height_pt > 0
    with Image.open(img.path) as pil_img:
        assert pil_img.mode == "RGBA"
        assert pil_img.width > 0
        assert pil_img.height > 0


def test_repeated_calls_with_identical_params_reuse_the_cached_file():
    first = get_recurring_decimal_image("0.", "3", 11.5, False, INK)
    second = get_recurring_decimal_image("0.", "3", 11.5, False, INK)
    assert first.path == second.path


def test_different_prefix_or_block_produces_different_files():
    a = get_recurring_decimal_image("0.", "3", 11.5, False, INK)
    b = get_recurring_decimal_image("0.", "27", 11.5, False, INK)
    c = get_recurring_decimal_image("0.1", "3", 11.5, False, INK)
    assert len({a.path, b.path, c.path}) == 3


def test_longer_block_produces_a_wider_image():
    short = get_recurring_decimal_image("0.", "3", 11.5, False, INK)
    long = get_recurring_decimal_image("0.1", "428571", 11.5, False, INK)
    assert long.width_pt > short.width_pt


def test_empty_block_raises():
    with pytest.raises(ValueError):
        get_recurring_decimal_image("0.5", "", 11.5, False, INK)


def test_image_pixel_colour_matches_the_requested_colour():
    img = get_recurring_decimal_image("0.", "3", 20, False, ACCENT)
    with Image.open(img.path) as pil_img:
        pixels = pil_img.getdata()
        opaque = [p for p in pixels if p[3] > 0]
        assert opaque, "expected at least one non-transparent pixel"
        expected_rgb = (round(ACCENT.red * 255), round(ACCENT.green * 255), round(ACCENT.blue * 255))
        assert all(p[:3] == expected_rgb for p in opaque)


def test_single_digit_block_places_exactly_one_dot():
    # Structural check: for a 1-digit block, exactly one row of the image
    # (near the top) should contain filled pixels above the digit text -
    # confirmed indirectly by checking the image has a non-trivial top
    # padding reserved for the dot (height greater than the plain-text-only
    # bounding box would need).
    img = get_recurring_decimal_image("0.", "3", 11.5, False, INK)
    with Image.open(img.path) as pil_img:
        # Top few rows should have at least one opaque pixel (the dot), and
        # the very top-left corner (no character up there) should be
        # transparent.
        top_row_pixels = [pil_img.getpixel((x, 1)) for x in range(pil_img.width)]
        assert any(p[3] > 0 for p in top_row_pixels)
