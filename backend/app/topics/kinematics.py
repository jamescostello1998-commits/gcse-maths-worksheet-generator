"""Kinematics (SUVAT) - the three standard constant-acceleration equations.

    v = u + at
    s = ut + (1/2)at^2
    v^2 = u^2 + 2as

One Higher-only topic, kinematics_suvat: each question picks one of the
three equations, then picks which variable is unknown (subject to the scope
constraints documented on generate_kinematics_suvat - notably, s = ut +
(1/2)at^2 never asks for t, since that would need the quadratic formula).

For every branch, all of that equation's variables are built as a
consistent, realistic set of values first (mirroring pythagoras.py's
convention of building a whole valid triple before hiding one member of it),
then the hidden value is independently re-derived via sp.solve on the
*original*, un-rearranged equation - a genuinely different code path than
the manual rearrangement shown in the displayed steps.
"""

import math
import random
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction

import sympy as sp

from app.core.models import ModelledExample, Question, Tier
from app.topics.base import TopicDefinition

SECTION = "algebra"
GROUP = "Kinematics (SUVAT)"

U, V, A, S, T = sp.symbols("u v a s t")

_MAX_ATTEMPTS = 300


def _nonzero_randint(rng: random.Random, lo: int, hi: int) -> int:
    while True:
        n = rng.randint(lo, hi)
        if n != 0:
            return n


def _fmt_exact_or_rounded(value) -> tuple[str, bool]:
    """Format an exact numeric value (int or sympy Rational) for display.

    Returns (display_string, needed_rounding). If the value terminates
    exactly within 1 decimal place it is shown exactly (a bare integer when
    whole, e.g. "20", otherwise e.g. "13.5"); otherwise it is rounded to
    1 d.p. (ROUND_HALF_UP) and displayed via fixed-point formatting - never
    scientific notation, see CLAUDE.md's Decimal/power-of-ten gotcha - and
    needed_rounding is True.
    """
    r = sp.Rational(value)
    frac = Fraction(int(r.p), int(r.q))
    scaled = frac * 10
    if scaled.denominator == 1:
        dec = Decimal(scaled.numerator) / Decimal(10)
        if dec == dec.to_integral_value():
            return str(int(dec)), False
        return format(dec, "f"), False
    dec = (Decimal(frac.numerator) / Decimal(frac.denominator)).quantize(
        Decimal("0.1"), rounding=ROUND_HALF_UP
    )
    return format(dec, "f"), True


def _fmt_sqrt(n_squared: int) -> tuple[str, bool]:
    """Format sqrt(n_squared) (n_squared a non-negative int), taking the
    positive root. Returns (display_string, needed_rounding)."""
    root = math.isqrt(n_squared)
    if root * root == n_squared:
        return str(root), False
    raw = math.sqrt(n_squared)
    dec = Decimal(str(raw)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    return format(dec, "f"), True


def _rounding_clause(rounded: bool) -> str:
    return " Give your answer correct to 1 decimal place." if rounded else ""


# ---------------------------------------------------------------------------
# v = u + at  (any of the 4 variables may be the unknown - all rearrangements
# are linear).
# ---------------------------------------------------------------------------


def _build_eq1(rng: random.Random) -> dict:
    unknown = rng.choice(["u", "v", "a", "t"])
    for _ in range(_MAX_ATTEMPTS):
        u = rng.randint(0, 30)
        a = _nonzero_randint(rng, -5, 5)
        t = rng.randint(1, 10)
        v = u + a * t
        if 0 <= v <= 45:
            break
    else:
        raise ValueError("kinematics eq1 could not find valid parameters")

    values = {"u": u, "v": v, "a": a, "t": t}
    claimed = values[unknown]
    knowns = {k: val for k, val in values.items() if k != unknown}

    symbol_map = {"u": U, "v": V, "a": A, "t": T}
    eq = sp.Eq(V, U + A * T)
    subs = {symbol_map[k]: val for k, val in knowns.items()}
    solved = sp.solve(eq.subs(subs), symbol_map[unknown])
    if not solved or sp.simplify(solved[0] - claimed) != 0:
        raise ValueError("kinematics eq1 verification failed")

    display, rounded = _fmt_exact_or_rounded(claimed)
    return {
        "unknown": unknown,
        "u": u,
        "v": v,
        "a": a,
        "t": t,
        "claimed": claimed,
        "display": display,
        "rounded": rounded,
    }


def _prompt_and_steps_eq1(b: dict) -> tuple[str, list[str], str]:
    u, v, a, t = b["u"], b["v"], b["a"], b["t"]
    unknown = b["unknown"]
    display, rounded = b["display"], b["rounded"]
    reason = (
        "This question gives three of the four SUVAT quantities u, v, a and t (and asks "
        "for the fourth), so use v = u + at, the equation linking exactly those four."
    )

    if unknown == "v":
        prompt = (
            f"An object starts with a velocity of {u} m/s and has a constant acceleration "
            f"of {a} m/s^2 for {t} s. Find its final velocity (v).{_rounding_clause(rounded)}"
        )
        steps = [
            reason,
            "v = u + at",
            f"Substitute u = {u}, a = {a}, t = {t}: "
            f"v = {u} + {a} × {t} = {u} + {a * t} = {display}",
        ]
        final_answer = f"{display} m/s"
    elif unknown == "u":
        prompt = (
            f"An object has a final velocity of {v} m/s after a constant acceleration of "
            f"{a} m/s^2 for {t} s. Find its initial velocity (u).{_rounding_clause(rounded)}"
        )
        steps = [
            reason,
            "v = u + at",
            "Rearrange to make u the subject: u = v - at",
            f"Substitute v = {v}, a = {a}, t = {t}: "
            f"u = {v} - {a} × {t} = {v} - {a * t} = {display}",
        ]
        final_answer = f"{display} m/s"
    elif unknown == "a":
        prompt = (
            f"An object's velocity increases from {u} m/s to {v} m/s over {t} s at a "
            f"constant acceleration. Find this acceleration (a).{_rounding_clause(rounded)}"
        )
        steps = [
            reason,
            "v = u + at",
            "Rearrange to make a the subject: a = \\frac{v - u}{t}",
            f"Substitute u = {u}, v = {v}, t = {t}: "
            f"a = \\frac{{{v} - {u}}}{{{t}}} = {v - u}/{t} = {display}",
        ]
        final_answer = f"{display} m/s^2"
    else:  # unknown == "t"
        prompt = (
            f"An object's velocity increases from {u} m/s to {v} m/s at a constant "
            f"acceleration of {a} m/s^2. Find how long this takes (t).{_rounding_clause(rounded)}"
        )
        steps = [
            reason,
            "v = u + at",
            "Rearrange to make t the subject: t = \\frac{v - u}{a}",
            f"Substitute u = {u}, v = {v}, a = {a}: "
            f"t = \\frac{{{v} - {u}}}{{{a}}} = \\frac{{{v - u}}}{{{a}}} = {display}",
        ]
        final_answer = f"{display} s"

    return prompt, steps, final_answer


# ---------------------------------------------------------------------------
# s = ut + (1/2)at^2  (only s, u, or a may be the unknown - solving for t
# here would need the quadratic formula, out of scope for this topic).
# ---------------------------------------------------------------------------


def _build_eq2(rng: random.Random) -> dict:
    unknown = rng.choice(["s", "u", "a"])
    for _ in range(_MAX_ATTEMPTS):
        u = rng.randint(0, 20)
        a = _nonzero_randint(rng, -5, 5)
        t = rng.randint(1, 10)
        s_val = sp.Rational(u * t) + sp.Rational(a, 2) * t * t
        if 0 < s_val <= 400:
            break
    else:
        raise ValueError("kinematics eq2 could not find valid parameters")

    values = {"u": u, "a": a, "t": t, "s": s_val}
    claimed = values[unknown]
    knowns = {k: val for k, val in values.items() if k != unknown}

    symbol_map = {"u": U, "a": A, "t": T, "s": S}
    eq = sp.Eq(S, U * T + sp.Rational(1, 2) * A * T**2)
    subs = {symbol_map[k]: val for k, val in knowns.items()}
    solved = sp.solve(eq.subs(subs), symbol_map[unknown])
    if not solved or sp.simplify(solved[0] - claimed) != 0:
        raise ValueError("kinematics eq2 verification failed")

    display, rounded = _fmt_exact_or_rounded(claimed)
    s_display, _ = _fmt_exact_or_rounded(s_val)
    return {
        "unknown": unknown,
        "u": u,
        "a": a,
        "t": t,
        "s": s_val,
        "s_display": s_display,
        "claimed": claimed,
        "display": display,
        "rounded": rounded,
    }


def _prompt_and_steps_eq2(b: dict) -> tuple[str, list[str], str]:
    u, a, t = b["u"], b["a"], b["t"]
    unknown = b["unknown"]
    display, rounded = b["display"], b["rounded"]
    s_display = b["s_display"]
    reason = (
        "This question gives three of s, u, a and t and asks for another, so use "
        "s = ut + (1/2)at^2, the equation linking exactly those four (note: t is never the "
        "unknown here, since solving this equation for t needs the quadratic formula)."
    )

    if unknown == "s":
        prompt = (
            f"An object starts with a velocity of {u} m/s and has a constant acceleration "
            f"of {a} m/s^2 for {t} s. Find the total displacement (s).{_rounding_clause(rounded)}"
        )
        steps = [
            reason,
            "s = ut + (1/2)at^2",
            f"Substitute u = {u}, a = {a}, t = {t}: "
            f"s = {u} × {t} + (1/2) × {a} × {t}^2 = {u * t} + {sp.Rational(a, 2) * t * t} = {display}",
        ]
        final_answer = f"{display} m"
    elif unknown == "u":
        prompt = (
            f"An object has a constant acceleration of {a} m/s^2 for {t} s, and travels a "
            f"displacement of {s_display} m in that time. Find its initial velocity (u)."
            f"{_rounding_clause(rounded)}"
        )
        steps = [
            reason,
            "s = ut + (1/2)at^2",
            "Rearrange to make u the subject: u = \\frac{s - (1/2)at^2}{t}",
            f"Substitute s = {s_display}, a = {a}, t = {t}: "
            f"u = \\frac{{{s_display} - (1/2) × {a} × {t}^2}}{{{t}}} = {display}",
        ]
        final_answer = f"{display} m/s"
    else:  # unknown == "a"
        prompt = (
            f"An object starts with a velocity of {u} m/s and travels a displacement of "
            f"{s_display} m in {t} s. Find its acceleration (a).{_rounding_clause(rounded)}"
        )
        steps = [
            reason,
            "s = ut + (1/2)at^2",
            "Rearrange to make a the subject: a = \\frac{2(s - ut)}{t^2}",
            f"Substitute s = {s_display}, u = {u}, t = {t}: "
            f"a = \\frac{{2({s_display} - {u} × {t})}}{{{t}^2}} = {display}",
        ]
        final_answer = f"{display} m/s^2"

    return prompt, steps, final_answer


# ---------------------------------------------------------------------------
# v^2 = u^2 + 2as  (any of the 4 variables may be the unknown; solving for v
# or u involves a square root - the positive root is always taken, since
# these are speeds/magnitudes and never negative in this context).
# ---------------------------------------------------------------------------


def _build_eq3(rng: random.Random) -> dict:
    unknown = rng.choice(["v", "u", "a", "s"])

    if unknown == "v":
        for _ in range(_MAX_ATTEMPTS):
            u = rng.randint(0, 40)
            a = _nonzero_randint(rng, -10, 10)
            s = rng.randint(1, 300)
            v_sq = u * u + 2 * a * s
            if 0 <= v_sq <= 48 * 48:
                break
        else:
            raise ValueError("kinematics eq3 (v) could not find valid parameters")
        claimed = sp.sqrt(sp.Integer(v_sq))
        display, rounded = _fmt_sqrt(v_sq)
        extra = {"u": u, "a": a, "s": s, "v_sq": v_sq}
        knowns = {"u": u, "a": a, "s": s}
    elif unknown == "u":
        for _ in range(_MAX_ATTEMPTS):
            v = rng.randint(0, 40)
            a = _nonzero_randint(rng, -10, 10)
            s = rng.randint(1, 300)
            u_sq = v * v - 2 * a * s
            if 0 <= u_sq <= 48 * 48:
                break
        else:
            raise ValueError("kinematics eq3 (u) could not find valid parameters")
        claimed = sp.sqrt(sp.Integer(u_sq))
        display, rounded = _fmt_sqrt(u_sq)
        extra = {"v": v, "a": a, "s": s, "u_sq": u_sq}
        knowns = {"v": v, "a": a, "s": s}
    elif unknown == "a":
        for _ in range(_MAX_ATTEMPTS):
            u = rng.randint(0, 40)
            v = rng.randint(0, 40)
            s = _nonzero_randint(rng, 10, 150)
            a_val = sp.Rational(v * v - u * u, 2 * s)
            if a_val != 0 and abs(a_val) <= 10:
                break
        else:
            raise ValueError("kinematics eq3 (a) could not find valid parameters")
        claimed = a_val
        display, rounded = _fmt_exact_or_rounded(a_val)
        extra = {"u": u, "v": v, "s": s}
        knowns = {"u": u, "v": v, "s": s}
    else:  # unknown == "s"
        for _ in range(_MAX_ATTEMPTS):
            u = rng.randint(0, 40)
            v = rng.randint(0, 40)
            a = _nonzero_randint(rng, -10, 10)
            s_val = sp.Rational(v * v - u * u, 2 * a)
            if 0 < s_val <= 300:
                break
        else:
            raise ValueError("kinematics eq3 (s) could not find valid parameters")
        claimed = s_val
        display, rounded = _fmt_exact_or_rounded(s_val)
        extra = {"u": u, "v": v, "a": a}
        knowns = {"u": u, "v": v, "a": a}

    symbol_map = {"u": U, "v": V, "a": A, "s": S}
    eq = sp.Eq(V**2, U**2 + 2 * A * S)
    subs = {symbol_map[k]: val for k, val in knowns.items()}
    solved = sp.solve(eq.subs(subs), symbol_map[unknown])
    if not any(sp.simplify(sol - claimed) == 0 for sol in solved):
        raise ValueError("kinematics eq3 verification failed")

    result = {"unknown": unknown, "claimed": claimed, "display": display, "rounded": rounded}
    result.update(extra)
    return result


def _prompt_and_steps_eq3(b: dict) -> tuple[str, list[str], str]:
    unknown = b["unknown"]
    display, rounded = b["display"], b["rounded"]
    reason = (
        "This question gives three of v, u, a and s and asks for the fourth, so use "
        "v^2 = u^2 + 2as, the equation linking exactly those four (note: no t appears here)."
    )

    if unknown == "v":
        u, a, s, v_sq = b["u"], b["a"], b["s"], b["v_sq"]
        prompt = (
            f"An object starts with a velocity of {u} m/s and has a constant acceleration "
            f"of {a} m/s^2 over a displacement of {s} m. Find its final velocity (v)."
            f"{_rounding_clause(rounded)}"
        )
        steps = [
            reason,
            "v^2 = u^2 + 2as",
            f"Substitute u = {u}, a = {a}, s = {s}: "
            f"v^2 = {u}^2 + 2 × {a} × {s} = {u * u} + {2 * a * s} = {v_sq}",
            f"v = √{v_sq} = {display} m/s (taking the positive root, since speed cannot be "
            "negative)",
        ]
        final_answer = f"{display} m/s (taking the positive root)"
    elif unknown == "u":
        v, a, s, u_sq = b["v"], b["a"], b["s"], b["u_sq"]
        prompt = (
            f"An object has a final velocity of {v} m/s after a constant acceleration of "
            f"{a} m/s^2 over a displacement of {s} m. Find its initial velocity (u)."
            f"{_rounding_clause(rounded)}"
        )
        steps = [
            reason,
            "v^2 = u^2 + 2as",
            "Rearrange to make u^2 the subject: u^2 = v^2 - 2as",
            f"Substitute v = {v}, a = {a}, s = {s}: "
            f"u^2 = {v}^2 - 2 × {a} × {s} = {v * v} - {2 * a * s} = {u_sq}",
            f"u = √{u_sq} = {display} m/s (taking the positive root, since speed cannot be "
            "negative)",
        ]
        final_answer = f"{display} m/s (taking the positive root)"
    elif unknown == "a":
        u, v, s = b["u"], b["v"], b["s"]
        prompt = (
            f"An object's velocity changes from {u} m/s to {v} m/s over a displacement of "
            f"{s} m at a constant acceleration. Find this acceleration (a)."
            f"{_rounding_clause(rounded)}"
        )
        steps = [
            reason,
            "v^2 = u^2 + 2as",
            "Rearrange to make a the subject: a = \\frac{v^2 - u^2}{2s}",
            f"Substitute u = {u}, v = {v}, s = {s}: "
            f"a = \\frac{{{v}^2 - {u}^2}}{{2 × {s}}} = \\frac{{{v * v} - {u * u}}}{{{2 * s}}} = {display}",
        ]
        final_answer = f"{display} m/s^2"
    else:  # unknown == "s"
        u, v, a = b["u"], b["v"], b["a"]
        prompt = (
            f"An object's velocity changes from {u} m/s to {v} m/s at a constant "
            f"acceleration of {a} m/s^2. Find the displacement (s).{_rounding_clause(rounded)}"
        )
        steps = [
            reason,
            "v^2 = u^2 + 2as",
            "Rearrange to make s the subject: s = \\frac{v^2 - u^2}{2a}",
            f"Substitute u = {u}, v = {v}, a = {a}: "
            f"s = \\frac{{{v}^2 - {u}^2}}{{2 × {a}}} = \\frac{{{v * v} - {u * u}}}{{{2 * a}}} = {display}",
        ]
        final_answer = f"{display} m"

    return prompt, steps, final_answer


def generate_kinematics_suvat(tier: Tier, rng: random.Random) -> Question:
    equation = rng.choice(["eq1", "eq2", "eq3"])

    if equation == "eq1":
        b = _build_eq1(rng)
        prompt, steps, final_answer = _prompt_and_steps_eq1(b)
        dedup_key = f"eq1:{b['unknown']}:{b['u']}:{b['v']}:{b['a']}:{b['t']}"
    elif equation == "eq2":
        b = _build_eq2(rng)
        prompt, steps, final_answer = _prompt_and_steps_eq2(b)
        dedup_key = f"eq2:{b['unknown']}:{b['u']}:{b['a']}:{b['t']}:{b['s']}"
    else:
        b = _build_eq3(rng)
        prompt, steps, final_answer = _prompt_and_steps_eq3(b)
        unknown = b["unknown"]
        if unknown == "v":
            dedup_key = f"eq3:v:{b['u']}:{b['a']}:{b['s']}"
        elif unknown == "u":
            dedup_key = f"eq3:u:{b['v']}:{b['a']}:{b['s']}"
        elif unknown == "a":
            dedup_key = f"eq3:a:{b['u']}:{b['v']}:{b['s']}"
        else:
            dedup_key = f"eq3:s:{b['u']}:{b['v']}:{b['a']}"

    return Question(
        topic_id="kinematics_suvat",
        tier=Tier.HIGHER,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=final_answer,
        dedup_key=dedup_key,
    )


# ---------------------------------------------------------------------------
# Modelled examples
# ---------------------------------------------------------------------------


def _modelled_eq1(rng: random.Random) -> ModelledExample:
    b = _build_eq1(rng)
    prompt, _, final_answer = _prompt_and_steps_eq1(b)
    unknown = b["unknown"]
    u, v, a, t = b["u"], b["v"], b["a"], b["t"]
    display = b["display"]

    teaching_steps = [
        "SUVAT problems always start the same way: write down which of the five "
        "quantities (s, u, v, a, t) you're given and which one you need to find, then pick "
        "the one equation that connects exactly those variables.",
        "Here we're given three of u, v, a and t (and not asked about s at all), so the "
        "right equation is v = u + at - it's the only one of the three SUVAT equations "
        "that leaves s out entirely.",
    ]
    if unknown == "v":
        teaching_steps += [
            f"Every value we need (u = {u}, a = {a}, t = {t}) is already on the side we "
            "need it on, so no rearranging is required - just substitute and calculate.",
            f"v = {u} + {a} × {t} = {u} + {a * t} = {display} m/s.",
        ]
        worked_calculation = [f"v = {u} + {a} × {t}", f"v = {display} m/s"]
    elif unknown == "u":
        teaching_steps += [
            "This time v is given but u is wanted, so rearrange first: since at is added "
            "to u to get v, subtract at from both sides to undo it, giving u = v - at.",
            f"Substitute v = {v}, a = {a}, t = {t}: "
            f"u = {v} - {a} × {t} = {v} - {a * t} = {display} m/s.",
        ]
        worked_calculation = [f"u = {v} - {a} × {t}", f"u = {display} m/s"]
    elif unknown == "a":
        teaching_steps += [
            "This time a is wanted, so rearrange v = u + at: subtract u from both sides to "
            "get v - u = at, then divide both sides by t to isolate a.",
            f"Substitute u = {u}, v = {v}, t = {t}: "
            f"a = \\frac{{{v} - {u}}}{{{t}}} = {v - u}/{t} = {display} m/s^2.",
        ]
        worked_calculation = [f"a = \\frac{{{v} - {u}}}{{{t}}}", f"a = {display} m/s^2"]
    else:
        teaching_steps += [
            "This time t is wanted, so rearrange v = u + at the same way as for a, but "
            "divide by a instead of t: t = \\frac{v - u}{a}.",
            f"Substitute u = {u}, v = {v}, a = {a}: "
            f"t = \\frac{{{v} - {u}}}{{{a}}} = \\frac{{{v - u}}}{{{a}}} = {display} s.",
        ]
        worked_calculation = [f"t = \\frac{{{v} - {u}}}{{{a}}}", f"t = {display} s"]

    teaching_steps.append(
        "As a check, this is exactly the same relationship sympy's own equation solver "
        "confirms when you feed it the original, un-rearranged formula directly - a good "
        "habit whenever you're not sure a rearrangement is correct."
    )

    return ModelledExample(
        topic_id="kinematics_suvat",
        tier=Tier.HIGHER,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=final_answer,
    )


def _modelled_eq2(rng: random.Random) -> ModelledExample:
    b = _build_eq2(rng)
    prompt, _, final_answer = _prompt_and_steps_eq2(b)
    unknown = b["unknown"]
    u, a, t = b["u"], b["a"], b["t"]
    s_display = b["s_display"]
    display = b["display"]

    teaching_steps = [
        "SUVAT problems always start the same way: write down which of the five "
        "quantities (s, u, v, a, t) you're given and which one you need to find, then pick "
        "the one equation that connects exactly those variables.",
        "Here v doesn't appear anywhere in the question, so the right equation is "
        "s = ut + (1/2)at^2 - the only SUVAT equation that leaves v out.",
        "Note this equation is never rearranged to find t here, since t appears both on "
        "its own and squared - untangling that would need the quadratic formula, which is "
        "out of scope for this topic.",
    ]
    if unknown == "s":
        teaching_steps.append(
            f"Every value we need (u = {u}, a = {a}, t = {t}) is already given, so just "
            f"substitute directly: s = {u} × {t} + (1/2) × {a} × {t}^2 = {display} m."
        )
        worked_calculation = [
            f"s = {u} × {t} + (1/2) × {a} × {t}^2",
            f"s = {display} m",
        ]
    elif unknown == "u":
        teaching_steps.append(
            "This time u is wanted, so rearrange first: subtract the (1/2)at^2 term from "
            "both sides, then divide both sides by t to isolate u, giving "
            "u = \\frac{s - (1/2)at^2}{t}."
        )
        teaching_steps.append(
            f"Substitute s = {s_display}, a = {a}, t = {t}: "
            f"u = \\frac{{{s_display} - (1/2) × {a} × {t}^2}}{{{t}}} = {display} m/s."
        )
        worked_calculation = [
            f"u = \\frac{{{s_display} - (1/2) × {a} × {t}^2}}{{{t}}}",
            f"u = {display} m/s",
        ]
    else:
        teaching_steps.append(
            "This time a is wanted, so rearrange first: subtract ut from both sides, then "
            "divide both sides by (1/2)t^2 (equivalently, multiply by 2 and divide by t^2), "
            "giving a = \\frac{2(s - ut)}{t^2}."
        )
        teaching_steps.append(
            f"Substitute s = {s_display}, u = {u}, t = {t}: "
            f"a = \\frac{{2({s_display} - {u} × {t})}}{{{t}^2}} = {display} m/s^2."
        )
        worked_calculation = [
            f"a = \\frac{{2({s_display} - {u} × {t})}}{{{t}^2}}",
            f"a = {display} m/s^2",
        ]

    return ModelledExample(
        topic_id="kinematics_suvat",
        tier=Tier.HIGHER,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=final_answer,
    )


def _modelled_eq3(rng: random.Random) -> ModelledExample:
    b = _build_eq3(rng)
    prompt, _, final_answer = _prompt_and_steps_eq3(b)
    unknown = b["unknown"]
    display = b["display"]

    teaching_steps = [
        "SUVAT problems always start the same way: write down which of the five "
        "quantities (s, u, v, a, t) you're given and which one you need to find, then pick "
        "the one equation that connects exactly those variables.",
        "Here t doesn't appear anywhere in the question, so the right equation is "
        "v^2 = u^2 + 2as - the only SUVAT equation that leaves t out.",
    ]
    if unknown == "v":
        u, a, s, v_sq = b["u"], b["a"], b["s"], b["v_sq"]
        teaching_steps += [
            f"Substitute u = {u}, a = {a}, s = {s} directly: "
            f"v^2 = {u}^2 + 2 × {a} × {s} = {v_sq}.",
            f"Since the equation gives v^2, not v itself, take the square root of both "
            f"sides to finish: v = √{v_sq} = {display} m/s. We only take the positive "
            "root, since a speed can never be negative - the negative root is "
            "mathematically valid but has no physical meaning here.",
        ]
        worked_calculation = [
            f"v^2 = {u}^2 + 2 × {a} × {s} = {v_sq}",
            f"v = √{v_sq} = {display} m/s",
        ]
    elif unknown == "u":
        v, a, s, u_sq = b["v"], b["a"], b["s"], b["u_sq"]
        teaching_steps += [
            "This time u is wanted, so rearrange first: subtract 2as from both sides to "
            "get u^2 = v^2 - 2as.",
            f"Substitute v = {v}, a = {a}, s = {s}: u^2 = {v}^2 - 2 × {a} × {s} = {u_sq}, "
            f"then take the square root: u = √{u_sq} = {display} m/s (taking the positive "
            "root, since speed cannot be negative).",
        ]
        worked_calculation = [
            f"u^2 = {v}^2 - 2 × {a} × {s} = {u_sq}",
            f"u = √{u_sq} = {display} m/s",
        ]
    elif unknown == "a":
        u, v, s = b["u"], b["v"], b["s"]
        teaching_steps += [
            "This time a is wanted, and it only appears once here (not squared or "
            "square-rooted), so this rearrangement is purely linear: subtract u^2 from "
            "both sides, then divide by 2s, giving a = \\frac{v^2 - u^2}{2s}.",
            f"Substitute u = {u}, v = {v}, s = {s}: "
            f"a = \\frac{{{v}^2 - {u}^2}}{{2 × {s}}} = {display} m/s^2.",
        ]
        worked_calculation = [
            f"a = \\frac{{{v}^2 - {u}^2}}{{2 × {s}}}",
            f"a = {display} m/s^2",
        ]
    else:
        u, v, a = b["u"], b["v"], b["a"]
        teaching_steps += [
            "This time s is wanted, and like a, it only appears once, so this "
            "rearrangement is purely linear too: subtract u^2 from both sides, then "
            "divide by 2a, giving s = \\frac{v^2 - u^2}{2a}.",
            f"Substitute u = {u}, v = {v}, a = {a}: "
            f"s = \\frac{{{v}^2 - {u}^2}}{{2 × {a}}} = {display} m.",
        ]
        worked_calculation = [
            f"s = \\frac{{{v}^2 - {u}^2}}{{2 × {a}}}",
            f"s = {display} m",
        ]

    return ModelledExample(
        topic_id="kinematics_suvat",
        tier=Tier.HIGHER,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=final_answer,
    )


def generate_modelled_example_kinematics_suvat(tier: Tier, rng: random.Random) -> ModelledExample:
    equation = rng.choice(["eq1", "eq2", "eq3"])
    if equation == "eq1":
        return _modelled_eq1(rng)
    elif equation == "eq2":
        return _modelled_eq2(rng)
    else:
        return _modelled_eq3(rng)


TOPIC_KINEMATICS_SUVAT = TopicDefinition(
    id="kinematics_suvat",
    display_name="Kinematics (SUVAT)",
    description=(
        "Use the constant-acceleration (SUVAT) equations v = u + at, s = ut + (1/2)at^2 "
        "and v^2 = u^2 + 2as to find a missing quantity."
    ),
    generate=generate_kinematics_suvat,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_kinematics_suvat,
    preamble_lines=("v = u + at", "s = ut + (1/2)at^2", "v^2 = u^2 + 2as"),
)
