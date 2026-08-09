import os

from PIL import Image
from reportlab.lib.colors import HexColor

from app.pdf.fraction_images import get_fraction_image

INK = HexColor("#1a1a1a")
ACCENT = HexColor("#2f6f4f")


def test_returns_a_real_png_file_with_positive_dimensions():
    img = get_fraction_image("3", "4", 11.5, False, INK)
    assert os.path.isfile(img.path)
    assert img.width_pt > 0
    assert img.height_pt > 0
    with Image.open(img.path) as pil_img:
        assert pil_img.mode == "RGBA"
        assert pil_img.width > 0
        assert pil_img.height > 0


def test_repeated_calls_with_identical_params_reuse_the_cached_file():
    first = get_fraction_image("1", "2", 11.5, False, INK)
    second = get_fraction_image("1", "2", 11.5, False, INK)
    assert first.path == second.path


def test_different_numerator_or_denominator_produces_different_files():
    a = get_fraction_image("1", "2", 11.5, False, INK)
    b = get_fraction_image("1", "3", 11.5, False, INK)
    c = get_fraction_image("2", "2", 11.5, False, INK)
    assert len({a.path, b.path, c.path}) == 3


def test_wider_denominator_produces_a_wider_image_than_a_narrower_one():
    narrow = get_fraction_image("1", "2", 11.5, False, INK)
    wide = get_fraction_image("123", "456", 11.5, False, INK)
    assert wide.width_pt > narrow.width_pt


def test_larger_font_size_produces_a_larger_image():
    small = get_fraction_image("1", "2", 9, False, INK)
    large = get_fraction_image("1", "2", 18, False, INK)
    assert large.width_pt > small.width_pt
    assert large.height_pt > small.height_pt


def test_image_pixel_colour_matches_the_requested_colour():
    img = get_fraction_image("1", "2", 20, False, ACCENT)
    with Image.open(img.path) as pil_img:
        pixels = pil_img.getdata()
        opaque = [p for p in pixels if p[3] > 0]
        assert opaque, "expected at least one non-transparent pixel"
        expected_rgb = (round(ACCENT.red * 255), round(ACCENT.green * 255), round(ACCENT.blue * 255))
        assert all(p[:3] == expected_rgb for p in opaque)


# --- "x_n" run support (iteration.py's recurrence-formula fractions) -------
#
# get_fraction_image draws its num/den as raw PIL text with no markup
# interpretation at all (see the module docstring) - a literal "x_n" inside
# that text is a special-cased exception, drawn as a real subscript (and, if
# followed by "^digits", superscript too) instead of literal underscore/caret
# characters. These tests only check the image is produced without error and
# is sized sensibly - the actual glyph placement was verified visually (see
# CLAUDE.md's chronology for this fix).


def test_xn_token_does_not_crash_and_produces_a_real_image():
    img = get_fraction_image("20 - x_n^2", "9", 11.5, False, INK)
    assert os.path.isfile(img.path)
    assert img.width_pt > 0
    assert img.height_pt > 0


def test_xn_without_exponent_also_renders():
    img = get_fraction_image("11", "x_n + 7", 11.5, False, INK)
    assert os.path.isfile(img.path)
    assert img.width_pt > 0


def test_xn_token_is_narrower_than_the_equivalent_literal_text_would_be():
    # A real subscript "n" is drawn smaller than a full-size "n" - the "x_n"
    # token should measure narrower than "x" + "_" + "n" all at full size
    # would (an indirect check that the token is actually being special-
    # cased, not just drawn as literal text with the underscore stripped).
    xn = get_fraction_image("x_n", "1", 11.5, False, INK)
    literal = get_fraction_image("xXn", "1", 11.5, False, INK)  # 3 full-size glyphs, same char count
    assert xn.width_pt < literal.width_pt


def test_only_the_exact_literal_x_n_substring_is_special_cased():
    # A different variable with the same underscore shape (e.g. "y_n") is
    # NOT the literal "x_n" token, so it must render as plain literal text,
    # completely unaffected - _XN_RE is deliberately narrow so no other
    # topic's existing fraction content (which may contain an unrelated "_"
    # or "^") is ever touched by this special-casing.
    x_n = get_fraction_image("x_n", "1", 11.5, False, INK)
    y_n = get_fraction_image("y_n", "1", 11.5, False, INK)
    assert os.path.isfile(y_n.path)
    # "x_n" is drawn as x + a real (narrower) subscript n; "y_n" has no
    # special case and is drawn as three full-size literal glyphs "y", "_",
    # "n" - so it should measure noticeably wider.
    assert y_n.width_pt > x_n.width_pt


# --- General "base^exp" exponent support (e.g. algebraic_fractions_multiply_
# divide's "x^2", kinematics.py's "t^2" denominator) ------------------------
#
# Previously a bare "^" inside a \frac{}{} marker printed as a literal caret
# character (this module never learned the "^" convention mathtext.py uses
# for ordinary prose). Fixed by drawing the base at normal size followed by a
# real raised, shrunk exponent - see the module docstring.


def test_exponent_token_does_not_crash_and_produces_a_real_image():
    img = get_fraction_image("x^2 - 9", "x + 3", 11.5, False, INK)
    assert os.path.isfile(img.path)
    assert img.width_pt > 0
    assert img.height_pt > 0


def test_multi_digit_numeric_base_exponent_also_renders():
    # A regression test: the base pattern originally only captured a single
    # character, so a multi-digit base like "10^2" (e.g. substitution_
    # rearrange_higher's "8^2 - 10^2" numerator) silently fell through to
    # plain literal text instead of being superscripted - found via a real
    # rendered-PDF check, not a unit test written in advance.
    single = get_fraction_image("8^2 - 10^2", "2 × (-2)", 11.5, False, INK)
    literal = get_fraction_image("8^2 - 10^^2", "2 × (-2)", 11.5, False, INK)  # "^^" never a valid token
    assert single.width_pt < literal.width_pt


def test_numeric_base_exponent_also_renders():
    img = get_fraction_image("1", "t^2", 11.5, False, INK)
    assert os.path.isfile(img.path)
    assert img.width_pt > 0


def test_exponent_token_is_narrower_than_the_equivalent_literal_text_would_be():
    # A raised, shrunk exponent digit should measure narrower than the same
    # digit drawn at full size with a literal caret in front of it.
    exp = get_fraction_image("t^2", "1", 11.5, False, INK)
    literal = get_fraction_image("t^^2", "1", 11.5, False, INK)  # not a valid token, stays literal
    assert exp.width_pt < literal.width_pt


def test_exponent_and_xn_tokens_compose_without_double_matching():
    # "x_n^2" must be claimed entirely by the xn token (with its own trailing
    # "^digits" superscript group), never partially re-matched by the general
    # exponent token - a regression test for the token-priority ordering.
    img = get_fraction_image("a - x_n^2", "x_n + b", 11.5, False, INK)
    assert os.path.isfile(img.path)


# --- Radical "√digits" support (e.g. rationalise_denominator's "\frac{a}{√b}")
# -----------------------------------------------------------------------------
#
# Previously a bare "√" inside a \frac{}{} marker rendered as a flat Arial
# glyph with no bar - fixed by drawing a real hook + bar spanning the digits,
# mirroring radical_images.py's geometry directly in this module's own
# coordinate space. See the module docstring.


def test_radical_token_does_not_crash_and_produces_a_real_image():
    img = get_fraction_image("3", "√7", 11.5, False, INK)
    assert os.path.isfile(img.path)
    assert img.width_pt > 0
    assert img.height_pt > 0


def test_radical_with_coefficient_in_the_same_run_also_renders():
    img = get_fraction_image("3√5", "√5", 11.5, False, INK)
    assert os.path.isfile(img.path)
    assert img.width_pt > 0


def test_decimal_radicand_also_renders():
    img = get_fraction_image("1", "√205.1", 11.5, False, INK)
    assert os.path.isfile(img.path)


def test_radical_token_is_taller_than_a_plain_denominator_of_the_same_digit():
    # The hook+bar geometry adds real height above the digit - a fraction
    # with a radical denominator should measure taller than the same digit
    # with no radical at all (an indirect check the hook/bar is actually
    # being drawn, not just the bare digit).
    with_radical = get_fraction_image("3", "√7", 11.5, False, INK)
    plain = get_fraction_image("3", "7", 11.5, False, INK)
    assert with_radical.height_pt > plain.height_pt
