from app.topics.units import display_qty, needs_larger_unit


def test_below_threshold_is_unchanged():
    assert display_qty(750, "g") == "750g"
    assert display_qty(900, "ml") == "900ml"
    assert not needs_larger_unit(750, "g")


def test_at_or_above_threshold_converts_to_the_larger_unit():
    assert display_qty(1000, "g") == "1kg"
    assert display_qty(1200, "g") == "1.2kg"
    assert display_qty(1250, "g") == "1.25kg"
    assert display_qty(1500, "ml") == "1.5L"
    assert needs_larger_unit(1000, "g")


def test_result_never_uses_scientific_notation():
    # A qty that normalizes to a round number (e.g. 10000 -> 10) must still
    # print as fixed-point, not "1E+1" - see units.py's docstring and the
    # documented estimation_rounding gotcha this mirrors.
    assert display_qty(10000, "g") == "10kg"


def test_units_other_than_g_or_ml_are_left_untouched():
    assert display_qty(1500, "cm") == "1500cm"
    assert not needs_larger_unit(1500, "cm")
