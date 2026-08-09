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
P_SYM = sp.symbols("P")
E_SYM = sp.symbols("E")


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
        topic_id="substitution_F",
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
        topic_id="substitution_F",
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
        topic_id="substitution_F",
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
        topic_id="substitution_F",
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
    return dataclasses.replace(q, topic_id="substitution_F", tier=Tier.FOUNDATION)


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
        topic_id="substitution_H",
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
        topic_id="substitution_H",
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
        topic_id="substitution_H",
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
    return dataclasses.replace(q, topic_id="substitution_H", tier=Tier.HIGHER)


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
        topic_id="substitution_F",
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
        topic_id="substitution_F",
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
        topic_id="substitution_F",
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
        topic_id="substitution_F",
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
    return dataclasses.replace(example, topic_id="substitution_F", tier=Tier.FOUNDATION)


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
        topic_id="substitution_H",
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
        topic_id="substitution_H",
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
        topic_id="substitution_H",
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
    return dataclasses.replace(example, topic_id="substitution_H", tier=Tier.HIGHER)


# ---------------------------------------------------------------------------
# Rearrange the formula for a DIFFERENT (non-subject) letter first, then
# substitute given numbers to find its value - combines changing-the-subject
# and substitution as one question, per the confirmed clarifying-question
# design. Reuses the same already-verified formula shapes as
# substitution_foundation/_higher above, just solving for a different letter
# each time.
# ---------------------------------------------------------------------------


def _shape_kinematics_rearrange_foundation(rng: random.Random) -> Question:
    u = rng.randint(1, 20)
    a = rng.randint(1, 10)
    t = rng.randint(1, 10)
    v = u + a * t

    # Independent verification: sp.solve the original equation for a (a
    # genuinely different path than the manual (v-u)/t rearrangement used to
    # build the displayed steps), then confirm the concrete numbers still
    # satisfy the ORIGINAL equation with the derived a substituted back in.
    solved = sp.solve(sp.Eq(V_SYM, U_SYM + A_SYM * T_SYM), A_SYM)
    if not solved or solved[0].subs({V_SYM: v, U_SYM: u, T_SYM: t}) != a:
        raise ValueError("substitution_rearrange kinematics (foundation) verification failed")
    check = sp.Eq(V_SYM, U_SYM + A_SYM * T_SYM).subs({V_SYM: v, U_SYM: u, T_SYM: t, A_SYM: a})
    if bool(check) is not True:
        raise ValueError("substitution_rearrange kinematics (foundation) verification failed (substitution)")

    steps = [
        "v = u + at",
        "Rearrange to make a the subject: a = \\frac{v - u}{t}",
        f"Substitute v = {v}, u = {u} and t = {t}: a = \\frac{{{v} - {u}}}{{{t}}}",
        f"a = {v - u}/{t} = {a}",
    ]
    return Question(
        topic_id="substitution_rearrange_F",
        tier=Tier.FOUNDATION,
        prompt=(
            f"v = u + at. Make a the subject of the formula, then find the value of a when "
            f"v = {v}, u = {u} and t = {t}."
        ),
        solution_steps=tuple(steps),
        final_answer=f"a = {a}",
        dedup_key=f"subrearr_kinematics:{v}:{u}:{t}",
    )


def _shape_perimeter_rearrange_foundation(rng: random.Random) -> Question:
    l = rng.randint(2, 30)
    w = rng.randint(2, 30)
    p = 2 * l + 2 * w

    solved = sp.solve(sp.Eq(P_SYM, 2 * L_SYM + 2 * W_SYM), W_SYM)
    if not solved or solved[0].subs({P_SYM: p, L_SYM: l}) != w:
        raise ValueError("substitution_rearrange perimeter (foundation) verification failed")
    check = sp.Eq(P_SYM, 2 * L_SYM + 2 * W_SYM).subs({P_SYM: p, L_SYM: l, W_SYM: w})
    if bool(check) is not True:
        raise ValueError("substitution_rearrange perimeter (foundation) verification failed (substitution)")

    steps = [
        "P = 2L + 2w",
        "Rearrange to make w the subject: w = \\frac{P - 2L}{2}",
        f"Substitute P = {p} and L = {l}: w = \\frac{{{p} - 2×{l}}}{{2}}",
        f"w = {p - 2 * l}/2 = {w}",
    ]
    return Question(
        topic_id="substitution_rearrange_F",
        tier=Tier.FOUNDATION,
        prompt=(
            f"P = 2L + 2w. Make w the subject of the formula, then find the value of w when "
            f"P = {p} and L = {l}."
        ),
        solution_steps=tuple(steps),
        final_answer=f"w = {w}",
        dedup_key=f"subrearr_perimeter:{p}:{l}",
    )


def _shape_area_rearrange_foundation(rng: random.Random) -> Question:
    l = rng.randint(2, 20)
    w = rng.randint(2, 20)
    area = l * w

    solved = sp.solve(sp.Eq(A_SYM, L_SYM * W_SYM), L_SYM)
    if not solved or solved[0].subs({A_SYM: area, W_SYM: w}) != l:
        raise ValueError("substitution_rearrange area (foundation) verification failed")
    check = sp.Eq(A_SYM, L_SYM * W_SYM).subs({A_SYM: area, L_SYM: l, W_SYM: w})
    if bool(check) is not True:
        raise ValueError("substitution_rearrange area (foundation) verification failed (substitution)")

    steps = [
        "A = LW",
        "Rearrange to make L the subject: L = \\frac{A}{w}",
        f"Substitute A = {area} and w = {w}: L = \\frac{{{area}}}{{{w}}}",
        f"L = {l}",
    ]
    return Question(
        topic_id="substitution_rearrange_F",
        tier=Tier.FOUNDATION,
        prompt=(
            f"A = LW. Make L the subject of the formula, then find the value of L when "
            f"A = {area} and w = {w}."
        ),
        solution_steps=tuple(steps),
        final_answer=f"L = {l}",
        dedup_key=f"subrearr_area:{area}:{w}",
    )


def _shape_triangle_area_rearrange_foundation(rng: random.Random) -> Question:
    b = rng.randint(2, 20)
    h = rng.randint(2, 20)
    area = Fraction(b * h, 2)

    solved = sp.solve(sp.Eq(A_SYM, sp.Rational(1, 2) * B_SYM * H_SYM), H_SYM)
    area_rat = sp.Rational(area.numerator, area.denominator)
    if not solved or sp.simplify(solved[0].subs({A_SYM: area_rat, B_SYM: b}) - h) != 0:
        raise ValueError("substitution_rearrange triangle area (foundation) verification failed")
    check = sp.Eq(A_SYM, sp.Rational(1, 2) * B_SYM * H_SYM).subs({A_SYM: area_rat, B_SYM: b, H_SYM: h})
    if bool(check) is not True:
        raise ValueError("substitution_rearrange triangle area (foundation) verification failed (substitution)")

    steps = [
        "A = (1/2)bh",
        "Rearrange to make h the subject: h = \\frac{2A}{b}",
        f"Substitute A = {_fmt_frac(area)} and b = {b}: h = \\frac{{2 × {_fmt_frac(area)}}}{{{b}}}",
        f"h = {h}",
    ]
    return Question(
        topic_id="substitution_rearrange_F",
        tier=Tier.FOUNDATION,
        prompt=(
            f"A = (1/2)bh. Make h the subject of the formula, then find the value of h when "
            f"A = {_fmt_frac(area)} and b = {b}."
        ),
        solution_steps=tuple(steps),
        final_answer=f"h = {h}",
        dedup_key=f"subrearr_triangle_area:{area.numerator}:{area.denominator}:{b}",
    )


_REARRANGE_FOUNDATION_SHAPES = [
    _shape_kinematics_rearrange_foundation,
    _shape_perimeter_rearrange_foundation,
    _shape_area_rearrange_foundation,
    _shape_triangle_area_rearrange_foundation,
]


def generate_substitution_rearrange_foundation(tier: Tier, rng: random.Random) -> Question:
    shape = rng.choice(_REARRANGE_FOUNDATION_SHAPES)
    q = shape(rng)
    return dataclasses.replace(q, topic_id="substitution_rearrange_F", tier=Tier.FOUNDATION)


def _build_speed_squared_exact(rng: random.Random):
    """Like _build_speed_squared, but rejects unless u^2 + 2as is a perfect
    square - this rearrange-then-substitute variant states v directly as a
    clean given number, so an irrational v (needing rounding) would make
    "substitute v = ..." awkward to state as a clean input."""
    for _ in range(500):
        s = rng.randint(1, 20)
        a = rng.choice([rng.randint(-10, -1), rng.randint(1, 10)])
        u = rng.randint(1, 15)
        val = u * u + 2 * a * s
        if val > 0:
            root = math.isqrt(val)
            if root * root == val:
                return u, a, s, root
    raise ValueError("substitution_rearrange speed-squared (higher): could not construct a valid question")


def _shape_speed_squared_rearrange_higher(rng: random.Random) -> Question:
    u, a, s, v = _build_speed_squared_exact(rng)

    solved = sp.solve(sp.Eq(V_SYM**2, U_SYM**2 + 2 * A_SYM * S_SYM), S_SYM)
    if not solved or sp.simplify(solved[0].subs({V_SYM: v, U_SYM: u, A_SYM: a}) - s) != 0:
        raise ValueError("substitution_rearrange speed-squared (higher) verification failed")
    check = sp.Eq(V_SYM**2, U_SYM**2 + 2 * A_SYM * S_SYM).subs({V_SYM: v, U_SYM: u, A_SYM: a, S_SYM: s})
    if bool(check) is not True:
        raise ValueError("substitution_rearrange speed-squared (higher) verification failed (substitution)")

    a_disp = f"({a})" if a < 0 else str(a)
    steps = [
        "v^2 = u^2 + 2as",
        "Rearrange to make s the subject: s = \\frac{v^2 - u^2}{2a}",
        f"Substitute v = {v}, u = {u} and a = {a}: s = \\frac{{{v}^2 - {u}^2}}{{2 × {a_disp}}}",
        f"s = {v * v - u * u}/{2 * a} = {s}",
    ]
    return Question(
        topic_id="substitution_rearrange_H",
        tier=Tier.HIGHER,
        prompt=(
            f"v^2 = u^2 + 2as. Make s the subject of the formula, then find the value of s when "
            f"v = {v}, u = {u} and a = {a}."
        ),
        solution_steps=tuple(steps),
        final_answer=f"s = {s}",
        dedup_key=f"subrearr_speed_sq:{v}:{u}:{a}",
    )


def _shape_kinetic_energy_rearrange_higher(rng: random.Random) -> Question:
    v = rng.choice([rng.randint(-10, -1), rng.randint(1, 10)])
    m = rng.randint(2, 20)
    energy = Fraction(m * v * v, 2)

    solved = sp.solve(sp.Eq(E_SYM, sp.Rational(1, 2) * M_SYM * V_SYM**2), M_SYM)
    energy_rat = sp.Rational(energy.numerator, energy.denominator)
    if not solved or sp.simplify(solved[0].subs({E_SYM: energy_rat, V_SYM: v}) - m) != 0:
        raise ValueError("substitution_rearrange kinetic energy (higher) verification failed")
    check = sp.Eq(E_SYM, sp.Rational(1, 2) * M_SYM * V_SYM**2).subs({E_SYM: energy_rat, M_SYM: m, V_SYM: v})
    if bool(check) is not True:
        raise ValueError("substitution_rearrange kinetic energy (higher) verification failed (substitution)")

    v_sq_disp = _fmt_signed_for_square(v)
    steps = [
        "E = (1/2)mv^2",
        "Rearrange to make m the subject: m = \\frac{2E}{v^2}",
        f"Substitute E = {_fmt_frac(energy)} and v = {v}: m = \\frac{{2 × {_fmt_frac(energy)}}}{{{v_sq_disp}^2}}",
        f"m = {m}",
    ]
    return Question(
        topic_id="substitution_rearrange_H",
        tier=Tier.HIGHER,
        prompt=(
            f"E = (1/2)mv^2. Make m the subject of the formula, then find the value of m when "
            f"E = {_fmt_frac(energy)} and v = {v}."
        ),
        solution_steps=tuple(steps),
        final_answer=f"m = {m}",
        dedup_key=f"subrearr_kinetic:{energy.numerator}:{energy.denominator}:{v}",
    )


def _shape_acceleration_rearrange_higher(rng: random.Random) -> Question:
    u, v, t, a = _build_acceleration(rng)

    solved = sp.solve(sp.Eq(A_SYM, (V_SYM - U_SYM) / T_SYM), U_SYM)
    a_rat = sp.Rational(a.numerator, a.denominator)
    if not solved or sp.simplify(solved[0].subs({A_SYM: a_rat, V_SYM: v, T_SYM: t}) - u) != 0:
        raise ValueError("substitution_rearrange acceleration (higher) verification failed")
    check = sp.Eq(A_SYM, (V_SYM - U_SYM) / T_SYM).subs({A_SYM: a_rat, U_SYM: u, V_SYM: v, T_SYM: t})
    if bool(check) is not True:
        raise ValueError("substitution_rearrange acceleration (higher) verification failed (substitution)")

    steps = [
        "a = \\frac{v - u}{t}",
        "Rearrange to make u the subject: u = v - at",
        f"Substitute v = {v}, a = {_fmt_frac(a)} and t = {t}: u = {v} - {_fmt_frac(a)} × {t}",
        f"u = {u}",
    ]
    return Question(
        topic_id="substitution_rearrange_H",
        tier=Tier.HIGHER,
        prompt=(
            f"a = \\frac{{v - u}}{{t}}. Make u the subject of the formula, then find the value of u when "
            f"v = {v}, a = {_fmt_frac(a)} and t = {t}."
        ),
        solution_steps=tuple(steps),
        final_answer=f"u = {u}",
        dedup_key=f"subrearr_accel:{v}:{a.numerator}:{a.denominator}:{t}",
    )


_REARRANGE_HIGHER_SHAPES = [
    _shape_speed_squared_rearrange_higher,
    _shape_kinetic_energy_rearrange_higher,
    _shape_acceleration_rearrange_higher,
]


def generate_substitution_rearrange_higher(tier: Tier, rng: random.Random) -> Question:
    shape = rng.choice(_REARRANGE_HIGHER_SHAPES)
    q = shape(rng)
    return dataclasses.replace(q, topic_id="substitution_rearrange_H", tier=Tier.HIGHER)


# ---------------------------------------------------------------------------
# Modelled examples (rearrange, foundation)
# ---------------------------------------------------------------------------


def _modelled_kinematics_rearrange_foundation(rng: random.Random) -> ModelledExample:
    u = rng.randint(1, 20)
    a = rng.randint(1, 10)
    t = rng.randint(1, 10)
    v = u + a * t

    solved = sp.solve(sp.Eq(V_SYM, U_SYM + A_SYM * T_SYM), A_SYM)
    if not solved or solved[0].subs({V_SYM: v, U_SYM: u, T_SYM: t}) != a:
        raise ValueError("modelled example substitution_rearrange kinematics (foundation) verification failed")

    teaching_steps = [
        "This question has two parts: first rearrange the formula so a different letter (a) is the "
        "subject, then substitute the given numbers into that rearranged formula - not the original.",
        "v = u + at has a being multiplied by t, then u added on. To isolate a: subtract u from both "
        "sides, then divide by t, giving a = \\frac{v - u}{t}.",
        f"Now substitute v = {v}, u = {u} and t = {t} into this rearranged formula: "
        f"a = \\frac{{{v} - {u}}}{{{t}}}.",
        f"Work out the numerator first: {v} - {u} = {v - u}, then divide by {t}: a = {a}.",
    ]
    worked_calculation = [
        "a = \\frac{v - u}{t}",
        f"a = \\frac{{{v} - {u}}}{{{t}}}",
        f"a = {a}",
    ]
    return ModelledExample(
        topic_id="substitution_rearrange_F",
        tier=Tier.FOUNDATION,
        prompt=(
            f"v = u + at. Make a the subject of the formula, then find the value of a when "
            f"v = {v}, u = {u} and t = {t}."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"a = {a}",
    )


def _modelled_perimeter_rearrange_foundation(rng: random.Random) -> ModelledExample:
    l = rng.randint(2, 30)
    w = rng.randint(2, 30)
    p = 2 * l + 2 * w

    solved = sp.solve(sp.Eq(P_SYM, 2 * L_SYM + 2 * W_SYM), W_SYM)
    if not solved or solved[0].subs({P_SYM: p, L_SYM: l}) != w:
        raise ValueError("modelled example substitution_rearrange perimeter (foundation) verification failed")

    teaching_steps = [
        "First rearrange P = 2L + 2w to make w the subject: subtract 2L from both sides, then divide "
        "by 2, giving w = \\frac{P - 2L}{2}.",
        f"Now substitute the given values P = {p} and L = {l} into that rearranged formula: "
        f"w = \\frac{{{p} - 2×{l}}}{{2}}.",
        f"Work out 2 × {l} = {2 * l} first, then {p} - {2 * l} = {p - 2 * l}, then divide by 2: w = {w}.",
    ]
    worked_calculation = [
        "w = \\frac{P - 2L}{2}",
        f"w = \\frac{{{p} - 2×{l}}}{{2}}",
        f"w = {w}",
    ]
    return ModelledExample(
        topic_id="substitution_rearrange_F",
        tier=Tier.FOUNDATION,
        prompt=(
            f"P = 2L + 2w. Make w the subject of the formula, then find the value of w when "
            f"P = {p} and L = {l}."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"w = {w}",
    )


def _modelled_area_rearrange_foundation(rng: random.Random) -> ModelledExample:
    l = rng.randint(2, 20)
    w = rng.randint(2, 20)
    area = l * w

    solved = sp.solve(sp.Eq(A_SYM, L_SYM * W_SYM), L_SYM)
    if not solved or solved[0].subs({A_SYM: area, W_SYM: w}) != l:
        raise ValueError("modelled example substitution_rearrange area (foundation) verification failed")

    teaching_steps = [
        "A = LW says area equals length times width. To make L the subject, divide both sides by w, "
        "giving L = \\frac{A}{w}.",
        f"Substitute A = {area} and w = {w} into that rearranged formula: L = \\frac{{{area}}}{{{w}}}.",
        f"{area} ÷ {w} = {l}.",
    ]
    worked_calculation = [
        "L = \\frac{A}{w}",
        f"L = \\frac{{{area}}}{{{w}}}",
        f"L = {l}",
    ]
    return ModelledExample(
        topic_id="substitution_rearrange_F",
        tier=Tier.FOUNDATION,
        prompt=(
            f"A = LW. Make L the subject of the formula, then find the value of L when "
            f"A = {area} and w = {w}."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"L = {l}",
    )


def _modelled_triangle_area_rearrange_foundation(rng: random.Random) -> ModelledExample:
    b = rng.randint(2, 20)
    h = rng.randint(2, 20)
    area = Fraction(b * h, 2)

    solved = sp.solve(sp.Eq(A_SYM, sp.Rational(1, 2) * B_SYM * H_SYM), H_SYM)
    area_rat = sp.Rational(area.numerator, area.denominator)
    if not solved or sp.simplify(solved[0].subs({A_SYM: area_rat, B_SYM: b}) - h) != 0:
        raise ValueError(
            "modelled example substitution_rearrange triangle area (foundation) verification failed"
        )

    teaching_steps = [
        "A = (1/2)bh has a fraction built into the formula. To make h the subject: multiply both "
        "sides by 2 to clear the fraction, then divide by b, giving h = \\frac{2A}{b}.",
        f"Substitute A = {_fmt_frac(area)} and b = {b} into that rearranged formula: "
        f"h = \\frac{{2 × {_fmt_frac(area)}}}{{{b}}}.",
        f"2 × {_fmt_frac(area)} = {b * h}, then divide by {b}: h = {h}.",
    ]
    worked_calculation = [
        "h = \\frac{2A}{b}",
        f"h = \\frac{{2 × {_fmt_frac(area)}}}{{{b}}}",
        f"h = {h}",
    ]
    return ModelledExample(
        topic_id="substitution_rearrange_F",
        tier=Tier.FOUNDATION,
        prompt=(
            f"A = (1/2)bh. Make h the subject of the formula, then find the value of h when "
            f"A = {_fmt_frac(area)} and b = {b}."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"h = {h}",
    )


_REARRANGE_FOUNDATION_MODELLED_SHAPES = [
    _modelled_kinematics_rearrange_foundation,
    _modelled_perimeter_rearrange_foundation,
    _modelled_area_rearrange_foundation,
    _modelled_triangle_area_rearrange_foundation,
]


def generate_modelled_example_substitution_rearrange_foundation(
    tier: Tier, rng: random.Random
) -> ModelledExample:
    shape = rng.choice(_REARRANGE_FOUNDATION_MODELLED_SHAPES)
    example = shape(rng)
    return dataclasses.replace(example, topic_id="substitution_rearrange_F", tier=Tier.FOUNDATION)


# ---------------------------------------------------------------------------
# Modelled examples (rearrange, higher)
# ---------------------------------------------------------------------------


def _modelled_speed_squared_rearrange_higher(rng: random.Random) -> ModelledExample:
    u, a, s, v = _build_speed_squared_exact(rng)

    solved = sp.solve(sp.Eq(V_SYM**2, U_SYM**2 + 2 * A_SYM * S_SYM), S_SYM)
    if not solved or sp.simplify(solved[0].subs({V_SYM: v, U_SYM: u, A_SYM: a}) - s) != 0:
        raise ValueError("modelled example substitution_rearrange speed-squared (higher) verification failed")

    a_disp = f"({a})" if a < 0 else str(a)
    teaching_steps = [
        "First rearrange v^2 = u^2 + 2as to make s the subject: subtract u^2 from both sides, then "
        "divide by 2a, giving s = \\frac{v^2 - u^2}{2a}.",
        f"Substitute v = {v}, u = {u} and a = {a} into that rearranged formula: "
        f"s = \\frac{{{v}^2 - {u}^2}}{{2 × {a_disp}}}.",
        f"Work out the numerator first: {v}^2 - {u}^2 = {v * v - u * u}, then divide by "
        f"2 × {a_disp} = {2 * a}: s = {s}.",
    ]
    worked_calculation = [
        "s = \\frac{v^2 - u^2}{2a}",
        f"s = \\frac{{{v}^2 - {u}^2}}{{2 × {a_disp}}}",
        f"s = {s}",
    ]
    return ModelledExample(
        topic_id="substitution_rearrange_H",
        tier=Tier.HIGHER,
        prompt=(
            f"v^2 = u^2 + 2as. Make s the subject of the formula, then find the value of s when "
            f"v = {v}, u = {u} and a = {a}."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"s = {s}",
    )


def _modelled_kinetic_energy_rearrange_higher(rng: random.Random) -> ModelledExample:
    v = rng.choice([rng.randint(-10, -1), rng.randint(1, 10)])
    m = rng.randint(2, 20)
    energy = Fraction(m * v * v, 2)

    solved = sp.solve(sp.Eq(E_SYM, sp.Rational(1, 2) * M_SYM * V_SYM**2), M_SYM)
    energy_rat = sp.Rational(energy.numerator, energy.denominator)
    if not solved or sp.simplify(solved[0].subs({E_SYM: energy_rat, V_SYM: v}) - m) != 0:
        raise ValueError("modelled example substitution_rearrange kinetic energy (higher) verification failed")

    v_sq_disp = _fmt_signed_for_square(v)
    teaching_steps = [
        "First rearrange E = (1/2)mv^2 to make m the subject: multiply both sides by 2, then divide "
        "by v^2, giving m = \\frac{2E}{v^2}.",
        f"Substitute E = {_fmt_frac(energy)} and v = {v} into that rearranged formula: "
        f"m = \\frac{{2 × {_fmt_frac(energy)}}}{{{v_sq_disp}^2}}.",
        f"Square v first (a negative squares to a positive): {v_sq_disp}^2 = {v * v}, then work out "
        f"m = {m}.",
    ]
    worked_calculation = [
        "m = \\frac{2E}{v^2}",
        f"m = \\frac{{2 × {_fmt_frac(energy)}}}{{{v_sq_disp}^2}}",
        f"m = {m}",
    ]
    return ModelledExample(
        topic_id="substitution_rearrange_H",
        tier=Tier.HIGHER,
        prompt=(
            f"E = (1/2)mv^2. Make m the subject of the formula, then find the value of m when "
            f"E = {_fmt_frac(energy)} and v = {v}."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"m = {m}",
    )


def _modelled_acceleration_rearrange_higher(rng: random.Random) -> ModelledExample:
    u, v, t, a = _build_acceleration(rng)

    solved = sp.solve(sp.Eq(A_SYM, (V_SYM - U_SYM) / T_SYM), U_SYM)
    a_rat = sp.Rational(a.numerator, a.denominator)
    if not solved or sp.simplify(solved[0].subs({A_SYM: a_rat, V_SYM: v, T_SYM: t}) - u) != 0:
        raise ValueError("modelled example substitution_rearrange acceleration (higher) verification failed")

    teaching_steps = [
        "First rearrange a = \\frac{v - u}{t} to make u the subject: multiply both sides by t, then "
        "rearrange for u, giving u = v - at.",
        f"Substitute v = {v}, a = {_fmt_frac(a)} and t = {t} into that rearranged formula: "
        f"u = {v} - {_fmt_frac(a)} × {t}.",
        f"Work out {_fmt_frac(a)} × {t} first, then subtract from {v}: u = {u}.",
    ]
    worked_calculation = [
        "u = v - at",
        f"u = {v} - {_fmt_frac(a)} × {t}",
        f"u = {u}",
    ]
    return ModelledExample(
        topic_id="substitution_rearrange_H",
        tier=Tier.HIGHER,
        prompt=(
            f"a = \\frac{{v - u}}{{t}}. Make u the subject of the formula, then find the value of u when "
            f"v = {v}, a = {_fmt_frac(a)} and t = {t}."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"u = {u}",
    )


_REARRANGE_HIGHER_MODELLED_SHAPES = [
    _modelled_speed_squared_rearrange_higher,
    _modelled_kinetic_energy_rearrange_higher,
    _modelled_acceleration_rearrange_higher,
]


def generate_modelled_example_substitution_rearrange_higher(tier: Tier, rng: random.Random) -> ModelledExample:
    shape = rng.choice(_REARRANGE_HIGHER_MODELLED_SHAPES)
    example = shape(rng)
    return dataclasses.replace(example, topic_id="substitution_rearrange_H", tier=Tier.HIGHER)


TOPIC_SUBSTITUTION_FOUNDATION = TopicDefinition(
    id="substitution_F",
    display_name="Substituting into Formulae",
    description="Substitute positive values into a simple formula to find the value of its subject.",
    generate=generate_substitution_foundation,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_substitution_foundation,
)

TOPIC_SUBSTITUTION_HIGHER = TopicDefinition(
    id="substitution_H",
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

TOPIC_SUBSTITUTION_REARRANGE_FOUNDATION = TopicDefinition(
    id="substitution_rearrange_F",
    display_name="Rearranging and Substituting into Formulae",
    description="Rearrange a formula for a different letter, then substitute given values to find it.",
    generate=generate_substitution_rearrange_foundation,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_substitution_rearrange_foundation,
)

TOPIC_SUBSTITUTION_REARRANGE_HIGHER = TopicDefinition(
    id="substitution_rearrange_H",
    display_name="Rearranging and Substituting into Formulae (Higher)",
    description=(
        "Rearrange a formula involving a power or an algebraic fraction for a different letter, "
        "then substitute given values to find it."
    ),
    generate=generate_substitution_rearrange_higher,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_substitution_rearrange_higher,
)
