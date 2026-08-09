import random
from decimal import Decimal

from app.topics import rounding


def test_pick_rounding_returns_only_the_three_gcse_options():
    rng = random.Random(1)
    seen = {rounding.pick_rounding(rng).phrase for _ in range(200)}
    assert seen == {"1 decimal place", "2 decimal places", "3 significant figures"}


def test_pick_rounding_gives_real_variety_across_many_draws():
    rng = random.Random(2)
    seen = {rounding.pick_rounding(rng).phrase for _ in range(30)}
    assert len(seen) == 3


def test_dp_round_fn_rounds_to_the_right_number_of_decimal_places():
    rng = random.Random(3)
    spec_1dp = next(s for s in [rounding.pick_rounding(rng) for _ in range(50)] if s.phrase == "1 decimal place")
    assert spec_1dp.round_fn(3.14159) == Decimal("3.1")
    assert spec_1dp.short == "1 d.p."

    rng = random.Random(4)
    spec_2dp = next(s for s in [rounding.pick_rounding(rng) for _ in range(50)] if s.phrase == "2 decimal places")
    assert spec_2dp.round_fn(3.14159) == Decimal("3.14")
    assert spec_2dp.short == "2 d.p."


def test_sf_round_fn_rounds_to_3_significant_figures():
    rng = random.Random(5)
    spec_3sf = next(s for s in [rounding.pick_rounding(rng) for _ in range(50)] if s.phrase == "3 significant figures")
    assert spec_3sf.round_fn(3.14159) == Decimal("3.14")
    assert spec_3sf.round_fn(0.0031415) == Decimal("0.00314")
    assert spec_3sf.short == "3 s.f."


def test_sf_round_fn_never_prints_scientific_notation_for_a_power_of_ten():
    # 9995 rounded to 3 s.f. crosses up to exactly 10000 - Decimal.quantize alone
    # keeps the scientific exponent internally here, which str()/format() would
    # otherwise print as "1E+4" instead of "10000" (the same bug class documented
    # for estimation_rounding elsewhere in this codebase).
    result = rounding._round_to_sf(9995, 3)
    assert format(result, "f") == "10000"
    assert "E" not in format(result, "f")


def test_sf_round_fn_handles_zero():
    assert rounding._round_to_sf(0.0, 3) == Decimal("0")
