import dataclasses
import math
import random
from fractions import Fraction

import sympy as sp

from app.core.models import ModelledExample, Question, Tier
from app.topics.base import TopicDefinition
from app.topics.rounding import pick_rounding

SECTION = "algebra"
GROUP = "Substitution into Formulae"

# Symbols used across the curated formula shapes below - each shape builds its
# own sympy expression and calls .subs(...) on it as a genuinely independent
# check of the manual arithmetic used to build the displayed steps.
U_SYM = sp.symbols("u")
A_SYM = sp.symbols("a")
S_SYM = sp.symbols("s")
V_SYM = sp.symbols("v")
T_SYM = sp.symbols("t")
L_SYM = sp.symbols("l")
W_SYM = sp.symbols("w")
M_SYM = sp.symbols("m")
B_SYM = sp.symbols("b")
H_SYM = sp.symbols("h")


def _fmt_frac(frac: Fraction) -> str:
    return str(frac.numerator) if frac.denominator == 1 else f"{frac.numerator}/{frac.denominator}"


def _fmt_signed_for_square(value: int) -> str:
    """Wraps a negative value in parentheses so a squaring step reads
    unambiguously, e.g. (-3)^2 rather than a bare -3^2 (which could be
    misread as -(3^2))."""
    return f"({value})" if value < 0 else str(value)


def _fmt_signed_term(value: int) -> str:
    """Formats a value as a trailing '+ n' or '- n' addition term."""
    return f"+ {value}" if value >= 0 else f"- {-value}"


# ---------------------------------------------------------------------------
# Foundation: substitute positive integers/simple fractions into a formula
# with the subject appearing exactly once - no rearranging required.
# ---------------------------------------------------------------------------


def _shape_kinematics_foundation(rng: random.Random) -> Question:
    u = rng.randint(1, 20)
    a = rng.randint(1, 10)
    t = rng.randint(1, 10)
    v = u + a * t

    # Independent verification: build v = u + at as a sympy expression and
    # substitute numerically, a genuinely different path than the plain
    # Python arithmetic used to build the displayed steps.
    check = sp.Eq(U_SYM + a * T_SYM, v).subs({U_SYM: u, T_SYM: t})
    if bool(check) is not True:
        raise ValueError("substitution kinematics (foundation) verification failed")

    steps = [
        "v = u + at",
        f"v = {u} + {a} × {t}",
        f"v = {u} + {a * t}",
        f"v = {v}",
    ]
    return Question(
        topic_id="substitution_foundation",
        tier=Tier.FOUNDATION,
        prompt=f"v = u + at. Find the value of v when u = {u}, a = {a} and t = {t}.",
        solution_steps=tuple(steps),
        final_answer=f"v = {v}",
        dedup_key=f"sub_kinematics:{u}:{a}:{t}",
    )


def _shape_perimeter_foundation(rng: random.Random) -> Question:
    l = rng.randint(2, 30)
    w = rng.randint(2, 30)
    p = 2 * l + 2 * w

    check = sp.Eq(2 * L_SYM + 2 * W_SYM, p).subs({L_SYM: l, W_SYM: w})
    if bool(check) is not True:
        raise ValueError("substitution perimeter (foundation) verification failed")

    steps = [
        "P = 2L + 2w",
        f"P = 2 × {l} + 2 × {w}",
        f"P = {2 * l} + {2 * w}",
        f"P = {p}",
    ]
    return Question(
        topic_id="substitution_foundation",
        tier=Tier.FOUNDATION,
        prompt=f"P = 2L + 2w. Find the value of P when L = {l} and w = {w}.",
        solution_steps=tuple(steps),
        final_answer=f"P = {p}",
        dedup_key=f"sub_perimeter:{l}:{w}",
    )


def _shape_area_foundation(rng: random.Random) -> Question:
    l = rng.randint(2, 20)
    w = rng.randint(2, 20)
    area = l * w

    check = sp.Eq(L_SYM * W_SYM, area).subs({L_SYM: l, W_SYM: w})
    if bool(check) is not True:
        raise ValueError("substitution area (foundation) verification failed")

    steps = [
        "A = LW",
        f"A = {l} × {w}",
        f"A = {area}",
    ]
    return Question(
        topic_id="substitution_foundation",
        tier=Tier.FOUNDATION,
        prompt=f"A = LW. Find the value of A when L = {l} and w = {w}.",
        solution_steps=tuple(steps),
        final_answer=f"A = {area}",
        dedup_key=f"sub_area:{l}:{w}",
    )


def _shape_triangle_area_foundation(rng: random.Random) -> Question:
    b = rng.randint(2, 20)
    h = rng.randint(2, 20)
    area = Fraction(b * h, 2)

    # Independent verification: build A = (1/2)bh as a sympy expression and
    # compare its substituted value to the Fraction computed manually above.
    expr_val = sp.Rational(1, 2) * B_SYM * H_SYM
    expr_val = expr_val.subs({B_SYM: b, H_SYM: h})
    if sp.simplify(expr_val - sp.Rational(area.numerator, area.denominator)) != 0:
        raise ValueError("substitution triangle area (foundation) verification failed")

    steps = [
        "A = (1/2)bh",
        f"A = (1/2) × {b} × {h}",
        f"A = {b * h}/2",
        f"A = {_fmt_frac(area)}",
    ]
    return Question(
        topic_id="substitution_foundation",
        tier=Tier.FOUNDATION,
        prompt=f"A = (1/2)bh. Find the value of A when b = {b} and h = {h}.",
        solution_steps=tuple(steps),
        final_answer=f"A = {_fmt_frac(area)}",
        dedup_key=f"sub_triangle_area:{b}:{h}",
    )


_FOUNDATION_SHAPES = [
    _shape_kinematics_foundation,
    _shape_perimeter_foundation,
    _shape_area_foundation,
    _shape_triangle_area_foundation,
]


def generate_substitution_foundation(tier: Tier, rng: random.Random) -> Question:
    shape = rng.choice(_FOUNDATION_SHAPES)
    q = shape(rng)
    return dataclasses.replace(q, topic_id="substitution_foundation", tier=Tier.FOUNDATION)


# ---------------------------------------------------------------------------
# Higher: substitute positive or negative values into a formula involving a
# power, a root, or an algebraic fraction.
# ---------------------------------------------------------------------------


def _build_speed_squared(rng: random.Random):
    """Picks u, a, s (a possibly negative, modelling deceleration) such that
    u^2 + 2as > 0, so v = sqrt(u^2 + 2as) is a genuine real value. Bounded
    retry loop, matching the established convention for generators with a
    real (if modest) rejection rate."""
    for _ in range(500):
        u = rng.randint(1, 15)
        a = rng.choice([rng.randint(-10, -1), rng.randint(1, 10)])
        s = rng.randint(1, 20)
        val = u * u + 2 * a * s
        if val > 0:
            return u, a, s, val
    raise ValueError("substitution speed-squared (higher): could not construct a valid question")


def _shape_speed_squared_higher(rng: random.Random) -> Question:
    u, a, s, val = _build_speed_squared(rng)
    rounding = pick_rounding(rng)

    # Independent verification: build v^2 = u^2 + 2as as a sympy expression,
    # substitute numerically, then confirm sympy's own numeric sqrt (a
    # genuinely different code path than the plain math.isqrt/math.sqrt used
    # below to build the displayed answer) agrees to high precision.
    rhs = (U_SYM**2 + 2 * A_SYM * S_SYM).subs({U_SYM: u, A_SYM: a, S_SYM: s})
    if int(rhs) != val:
        raise ValueError("substitution speed-squared (higher) verification failed (rhs)")
    sympy_root = sp.sqrt(rhs)

    root_int = math.isqrt(val)
    is_exact = root_int * root_int == val
    if is_exact:
        if abs(sp.N(sympy_root) - root_int) > 1e-9:
            raise ValueError("substitution speed-squared (higher) verification failed (exact root)")
        v_final = str(root_int)
        note = f"v = √{val} = {root_int}"
    else:
        v_float = math.sqrt(val)
        if abs(float(sp.N(sympy_root)) - v_float) > 1e-9:
            raise ValueError("substitution speed-squared (higher) verification failed (approx root)")
        v_rounded = format(rounding.round_fn(v_float), "f")
        v_final = f"{v_rounded} ({rounding.short})"
        note = f"v = √{val} = {v_rounded} ({rounding.short})"

    a_disp = f"({a})" if a < 0 else str(a)
    term2 = 2 * a * s
    steps = [
        "v^2 = u^2 + 2as",
        f"v^2 = {u}^2 + 2 × {a_disp} × {s}",
        f"v^2 = {u * u} {_fmt_signed_term(term2)}",
        f"v^2 = {val}",
        note,
        "Take the positive square root only, since v represents a speed and must be positive.",
    ]
    return Question(
        topic_id="substitution_higher",
        tier=Tier.HIGHER,
        prompt=(
            f"v^2 = u^2 + 2as. Find the value of v when u = {u}, a = {a} and s = {s}. "
            f"Give your answer to {rounding.phrase} if it is not exact."
        ),
        solution_steps=tuple(steps),
        final_answer=f"v = {v_final}",
        dedup_key=f"sub_speed_sq:{u}:{a}:{s}",
    )


def _build_kinetic_energy(rng: random.Random):
    m = rng.randint(2, 20)
    v = rng.choice([rng.randint(-15, -1), rng.randint(1, 15)])
    return m, v


def _shape_kinetic_energy_higher(rng: random.Random) -> Question:
    m, v = _build_kinetic_energy(rng)
    energy = Fraction(m * v * v, 2)

    # Independent verification: build E = (1/2)mv^2 as a sympy expression and
    # compare its substituted value to the Fraction computed manually above.
    expr_val = (sp.Rational(1, 2) * M_SYM * V_SYM**2).subs({M_SYM: m, V_SYM: v})
    if sp.simplify(expr_val - sp.Rational(energy.numerator, energy.denominator)) != 0:
        raise ValueError("substitution kinetic energy (higher) verification failed")

    v_sq_disp = _fmt_signed_for_square(v)
    steps = [
        "E = (1/2)mv^2",
        f"E = (1/2) × {m} × {v_sq_disp}^2",
        f"E = (1/2) × {m} × {v * v}",
        f"E = {m * v * v}/2",
        f"E = {_fmt_frac(energy)}",
    ]
    return Question(
        topic_id="substitution_higher",
        tier=Tier.HIGHER,
        prompt=f"E = (1/2)mv^2. Find the value of E when m = {m} and v = {v}.",
        solution_steps=tuple(steps),
        final_answer=f"E = {_fmt_frac(energy)}",
        dedup_key=f"sub_kinetic:{m}:{v}",
    )


def _build_acceleration(rng: random.Random):
    """Picks t and a simple (possibly negative) fraction a = num/den first, then
    derives u and v so that a = (v - u)/t holds exactly with an integer v.
    Bounded retry loop, rejecting non-integer displacement or a negative
    final velocity."""
    for _ in range(500):
        t = rng.randint(2, 10)
        a_num = rng.randint(-15, 15)
        if a_num == 0:
            continue
        a_den = rng.choice([1, 2, 4, 5])
        a = Fraction(a_num, a_den)
        diff = a * t
        if diff.denominator != 1:
            continue
        u = rng.randint(5, 50)
        v = u + int(diff)
        if v < 0:
            continue
        return u, v, t, a
    raise ValueError("substitution acceleration (higher): could not construct a valid question")


def _shape_acceleration_higher(rng: random.Random) -> Question:
    u, v, t, a = _build_acceleration(rng)

    # Independent verification: build a = (v - u)/t as a sympy expression and
    # compare its substituted value to the Fraction computed manually above.
    expr_val = ((V_SYM - U_SYM) / T_SYM).subs({V_SYM: v, U_SYM: u, T_SYM: t})
    if sp.simplify(expr_val - sp.Rational(a.numerator, a.denominator)) != 0:
        raise ValueError("substitution acceleration (higher) verification failed")

    diff = v - u
    steps = [
        "a = \\frac{v - u}{t}",
        f"a = \\frac{{{v} - {u}}}{{{t}}}",
        f"a = {diff}/{t}" if diff >= 0 else f"a = -{-diff}/{t}",
        f"a = {_fmt_frac(a)}",
    ]
    return Question(
        topic_id="substitution_higher",
        tier=Tier.HIGHER,
        prompt=f"a = \\frac{{v - u}}{{t}}. Find the value of a when u = {u}, v = {v} and t = {t}.",
        solution_steps=tuple(steps),
        final_answer=f"a = {_fmt_frac(a)}",
        dedup_key=f"sub_accel:{u}:{v}:{t}",
    )


_HIGHER_SHAPES = [
    _shape_speed_squared_higher,
    _shape_kinetic_energy_higher,
    _shape_acceleration_higher,
]


def generate_substitution_higher(tier: Tier, rng: random.Random) -> Question:
    shape = rng.choice(_HIGHER_SHAPES)
    q = shape(rng)
    return dataclasses.replace(q, topic_id="substitution_higher", tier=Tier.HIGHER)


# ---------------------------------------------------------------------------
# Modelled examples (foundation)
# ---------------------------------------------------------------------------


def _modelled_kinematics_foundation(rng: random.Random) -> ModelledExample:
    u = rng.randint(1, 20)
    a = rng.randint(1, 10)
    t = rng.randint(1, 10)
    v = u + a * t

    check = sp.Eq(U_SYM + a * T_SYM, v).subs({U_SYM: u, T_SYM: t})
    if bool(check) is not True:
        raise ValueError("modelled example substitution kinematics (foundation) verification failed")

    teaching_steps = [
        "Substituting into a formula means replacing each letter with the number you've been given, "
        "then working out the calculation that's left - the formula itself never changes, only the "
        "numbers standing in for its letters.",
        f"v = u + at has three letters. We're told u = {u}, a = {a} and t = {t}, so write those "
        f"numbers in exactly where the matching letters were: v = {u} + {a} × {t}.",
        "Remember that 'at' in the formula means a multiplied by t, even though there's no "
        "multiplication sign written - so once numbers replace the letters, that multiplication has "
        "to be done explicitly.",
        f"Work out the multiplication first (following the normal order of operations), then add: "
        f"{a} × {t} = {a * t}, so v = {u} + {a * t} = {v}.",
    ]
    worked_calculation = [
        "v = u + at",
        f"v = {u} + {a} × {t}",
        f"v = {v}",
    ]
    return ModelledExample(
        topic_id="substitution_foundation",
        tier=Tier.FOUNDATION,
        prompt=f"v = u + at. Find the value of v when u = {u}, a = {a} and t = {t}.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"v = {v}",
    )


def _modelled_perimeter_foundation(rng: random.Random) -> ModelledExample:
    l = rng.randint(2, 30)
    w = rng.randint(2, 30)
    p = 2 * l + 2 * w

    check = sp.Eq(2 * L_SYM + 2 * W_SYM, p).subs({L_SYM: l, W_SYM: w})
    if bool(check) is not True:
        raise ValueError("modelled example substitution perimeter (foundation) verification failed")

    teaching_steps = [
        "P = 2L + 2w has two separate terms added together: 2L (twice the length) and 2w (twice the "
        "width) - each term needs its own substitution and multiplication before they're added.",
        f"Replace L with {l} and w with {w}: P = 2 × {l} + 2 × {w}.",
        f"Work out each multiplication separately first: 2 × {l} = {2 * l} and 2 × {w} = {2 * w}.",
        f"Then add the two results together: P = {2 * l} + {2 * w} = {p}.",
    ]
    worked_calculation = [
        "P = 2L + 2w",
        f"P = 2 × {l} + 2 × {w}",
        f"P = {p}",
    ]
    return ModelledExample(
        topic_id="substitution_foundation",
        tier=Tier.FOUNDATION,
        prompt=f"P = 2L + 2w. Find the value of P when L = {l} and w = {w}.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"P = {p}",
    )


def _modelled_area_foundation(rng: random.Random) -> ModelledExample:
    l = rng.randint(2, 20)
    w = rng.randint(2, 20)
    area = l * w

    check = sp.Eq(L_SYM * W_SYM, area).subs({L_SYM: l, W_SYM: w})
    if bool(check) is not True:
        raise ValueError("modelled example substitution area (foundation) verification failed")

    teaching_steps = [
        "A = LW means area equals length multiplied by width - substituting just means replacing L "
        "and w with the numbers given, then doing that one multiplication.",
        f"Replace L with {l} and w with {w}: A = {l} × {w}.",
        f"Multiply the two numbers together: A = {area}.",
    ]
    worked_calculation = [
        "A = LW",
        f"A = {l} × {w}",
        f"A = {area}",
    ]
    return ModelledExample(
        topic_id="substitution_foundation",
        tier=Tier.FOUNDATION,
        prompt=f"A = LW. Find the value of A when L = {l} and w = {w}.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"A = {area}",
    )


def _modelled_triangle_area_foundation(rng: random.Random) -> ModelledExample:
    b = rng.randint(2, 20)
    h = rng.randint(2, 20)
    area = Fraction(b * h, 2)

    expr_val = sp.Rational(1, 2) * B_SYM * H_SYM
    expr_val = expr_val.subs({B_SYM: b, H_SYM: h})
    if sp.simplify(expr_val - sp.Rational(area.numerator, area.denominator)) != 0:
        raise ValueError("modelled example substitution triangle area (foundation) verification failed")

    teaching_steps = [
        "A = (1/2)bh has a fraction as part of the formula itself, not just in the answer - the (1/2) "
        "is a multiplier just like any number, so it gets multiplied in exactly the same way as b "
        "and h.",
        f"Replace b with {b} and h with {h}: A = (1/2) × {b} × {h}.",
        f"Multiply b and h together first: {b} × {h} = {b * h}, then multiply by (1/2), which is the "
        f"same as dividing by 2: A = {b * h}/2.",
        (
            f"{b * h} divides by 2 exactly, giving a whole-number area: A = {area.numerator}."
            if area.denominator == 1
            else f"{b * h} doesn't divide by 2 exactly, so the answer stays as a fraction: "
            f"A = {_fmt_frac(area)}."
        ),
    ]
    worked_calculation = [
        "A = (1/2)bh",
        f"A = (1/2) × {b} × {h}",
        f"A = {_fmt_frac(area)}",
    ]
    return ModelledExample(
        topic_id="substitution_foundation",
        tier=Tier.FOUNDATION,
        prompt=f"A = (1/2)bh. Find the value of A when b = {b} and h = {h}.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"A = {_fmt_frac(area)}",
    )


_FOUNDATION_MODELLED_SHAPES = [
    _modelled_kinematics_foundation,
    _modelled_perimeter_foundation,
    _modelled_area_foundation,
    _modelled_triangle_area_foundation,
]


def generate_modelled_example_substitution_foundation(tier: Tier, rng: random.Random) -> ModelledExample:
    shape = rng.choice(_FOUNDATION_MODELLED_SHAPES)
    example = shape(rng)
    return dataclasses.replace(example, topic_id="substitution_foundation", tier=Tier.FOUNDATION)


# ---------------------------------------------------------------------------
# Modelled examples (higher)
# ---------------------------------------------------------------------------


def _modelled_speed_squared_higher(rng: random.Random) -> ModelledExample:
    u, a, s, val = _build_speed_squared(rng)
    rounding = pick_rounding(rng)

    rhs = (U_SYM**2 + 2 * A_SYM * S_SYM).subs({U_SYM: u, A_SYM: a, S_SYM: s})
    if int(rhs) != val:
        raise ValueError("modelled example substitution speed-squared (higher) verification failed (rhs)")
    sympy_root = sp.sqrt(rhs)

    root_int = math.isqrt(val)
    is_exact = root_int * root_int == val
    if is_exact:
        if abs(sp.N(sympy_root) - root_int) > 1e-9:
            raise ValueError(
                "modelled example substitution speed-squared (higher) verification failed (exact root)"
            )
        v_final = str(root_int)
        final_line = f"v = √{val} = {root_int}"
    else:
        v_float = math.sqrt(val)
        if abs(float(sp.N(sympy_root)) - v_float) > 1e-9:
            raise ValueError(
                "modelled example substitution speed-squared (higher) verification failed (approx root)"
            )
        v_rounded = format(rounding.round_fn(v_float), "f")
        v_final = f"{v_rounded} ({rounding.short})"
        final_line = f"v = √{val} ≈ {v_rounded} ({rounding.short})"

    a_disp = f"({a})" if a < 0 else str(a)
    term2 = 2 * a * s
    prompt = (
        f"v^2 = u^2 + 2as. Find the value of v when u = {u}, a = {a} and s = {s}. "
        f"Give your answer to {rounding.phrase} if it is not exact."
    )
    teaching_steps = [
        "This formula gives v squared, not v itself - so after substituting, there's one extra step "
        "at the end that a simple linear formula wouldn't need: taking a square root.",
        f"Substitute u = {u}, a = {a} and s = {s} into the right-hand side: "
        f"v^2 = {u}^2 + 2 × {a_disp} × {s}.",
        (
            f"Work out each part separately: {u}^2 = {u * u}, and 2 × {a_disp} × {s} = {term2}. "
            f"Since a is negative here, that second term is subtracted rather than added, giving "
            f"v^2 = {u * u} {_fmt_signed_term(term2)} = {val}."
            if a < 0
            else f"Work out each part separately: {u}^2 = {u * u}, and 2 × {a} × {s} = {term2}. "
            f"Adding them gives v^2 = {u * u} + {term2} = {val}."
        ),
        (
            f"{val} is a perfect square, so the square root is exact: v = √{val} = {root_int}."
            if is_exact
            else f"{val} isn't a perfect square, so the square root is irrational - use a calculator "
            f"and round to {rounding.phrase}: v = √{val} ≈ {v_rounded}."
        ),
        "Only the positive square root is taken as the final answer, since v represents a speed and "
        "a physical speed can't be negative (even though a decelerating object might have a negative "
        "acceleration).",
    ]
    worked_calculation = [
        "v^2 = u^2 + 2as",
        f"v^2 = {u}^2 {_fmt_signed_term(term2)}",
        f"v^2 = {val}",
        final_line,
    ]
    return ModelledExample(
        topic_id="substitution_higher",
        tier=Tier.HIGHER,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"v = {v_final}",
    )


def _modelled_kinetic_energy_higher(rng: random.Random) -> ModelledExample:
    m, v = _build_kinetic_energy(rng)
    energy = Fraction(m * v * v, 2)

    expr_val = (sp.Rational(1, 2) * M_SYM * V_SYM**2).subs({M_SYM: m, V_SYM: v})
    if sp.simplify(expr_val - sp.Rational(energy.numerator, energy.denominator)) != 0:
        raise ValueError("modelled example substitution kinetic energy (higher) verification failed")

    v_sq_disp = _fmt_signed_for_square(v)
    teaching_steps = [
        "E = (1/2)mv^2 combines two things this topic likes to test together: a fraction coefficient "
        "(1/2) and a squared variable (v^2) - both have to be handled carefully.",
        f"Substitute m = {m} and v = {v}: E = (1/2) × {m} × {v_sq_disp}^2.",
        (
            f"Square v first, remembering that squaring a negative number gives a POSITIVE result: "
            f"({v})^2 = {v * v}, not -{v * v}. This is the single most common mistake with this "
            "formula."
            if v < 0
            else f"Square v first: {v}^2 = {v * v}."
        ),
        f"Now multiply everything together: (1/2) × {m} × {v * v} is the same as {m} × {v * v} ÷ 2, "
        f"which is {m * v * v} ÷ 2 = {_fmt_frac(energy)}.",
    ]
    worked_calculation = [
        "E = (1/2)mv^2",
        f"E = (1/2) × {m} × {v_sq_disp}^2",
        f"E = (1/2) × {m} × {v * v}",
        f"E = {_fmt_frac(energy)}",
    ]
    return ModelledExample(
        topic_id="substitution_higher",
        tier=Tier.HIGHER,
        prompt=f"E = (1/2)mv^2. Find the value of E when m = {m} and v = {v}.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"E = {_fmt_frac(energy)}",
    )


def _modelled_acceleration_higher(rng: random.Random) -> ModelledExample:
    u, v, t, a = _build_acceleration(rng)

    expr_val = ((V_SYM - U_SYM) / T_SYM).subs({V_SYM: v, U_SYM: u, T_SYM: t})
    if sp.simplify(expr_val - sp.Rational(a.numerator, a.denominator)) != 0:
        raise ValueError("modelled example substitution acceleration (higher) verification failed")

    diff = v - u
    teaching_steps = [
        "a = \\frac{v - u}{t} is an algebraic fraction: the whole numerator (v - u) has to be "
        "worked out first, before dividing by t - you can't divide u by t and v by t separately, "
        "since it's the DIFFERENCE that's being divided.",
        f"Substitute u = {u}, v = {v} and t = {t}: a = \\frac{{{v} - {u}}}{{{t}}}.",
        (
            f"Work out the numerator: {v} - {u} = {diff}, which is negative here - that makes sense "
            "physically, since the object is slowing down (its final velocity is lower than its "
            f"starting velocity), so a = {diff}/{t}."
            if diff < 0
            else f"Work out the numerator first: {v} - {u} = {diff}, giving a = {diff}/{t}."
        ),
        f"Finally, express that division as a simplified fraction: a = {_fmt_frac(a)}.",
    ]
    worked_calculation = [
        "a = \\frac{v - u}{t}",
        f"a = \\frac{{{v} - {u}}}{{{t}}}",
        f"a = {diff}/{t}" if diff >= 0 else f"a = -{-diff}/{t}",
        f"a = {_fmt_frac(a)}",
    ]
    return ModelledExample(
        topic_id="substitution_higher",
        tier=Tier.HIGHER,
        prompt=f"a = \\frac{{v - u}}{{t}}. Find the value of a when u = {u}, v = {v} and t = {t}.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"a = {_fmt_frac(a)}",
    )


_HIGHER_MODELLED_SHAPES = [
    _modelled_speed_squared_higher,
    _modelled_kinetic_energy_higher,
    _modelled_acceleration_higher,
]


def generate_modelled_example_substitution_higher(tier: Tier, rng: random.Random) -> ModelledExample:
    shape = rng.choice(_HIGHER_MODELLED_SHAPES)
    example = shape(rng)
    return dataclasses.replace(example, topic_id="substitution_higher", tier=Tier.HIGHER)


TOPIC_SUBSTITUTION_FOUNDATION = TopicDefinition(
    id="substitution_foundation",
    display_name="Substituting into Formulae",
    description="Substitute positive values into a simple formula to find the value of its subject.",
    generate=generate_substitution_foundation,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_substitution_foundation,
)

TOPIC_SUBSTITUTION_HIGHER = TopicDefinition(
    id="substitution_higher",
    display_name="Substituting into Formulae (Higher)",
    description=(
        "Substitute positive or negative values into a formula involving a power, a root, or an "
        "algebraic fraction."
    ),
    generate=generate_substitution_higher,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_substitution_higher,
)
