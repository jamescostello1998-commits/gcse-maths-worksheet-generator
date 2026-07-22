import dataclasses
import random

import sympy as sp

from app.core.models import ModelledExample, Question, Tier
from app.topics.algebra_utils import X, fmt_linear, fmt_num
from app.topics.base import TopicDefinition

SECTION = "algebra"
GROUP = "Changing the Subject of a Formula"

# Extra symbols used across the various curated formula shapes (X, for x, is
# already imported from algebra_utils - it's shared with every other topic
# that solves/rearranges linear equations).
Y = sp.symbols("y")
T = sp.symbols("t")
U = sp.symbols("u")
V = sp.symbols("v")
L = sp.symbols("l")
W = sp.symbols("w")
A_SYM = sp.symbols("A")
P_SYM = sp.symbols("P")
C_SYM = sp.symbols("C")
R_SYM = sp.symbols("r")


# ---------------------------------------------------------------------------
# Foundation: subject appears exactly once.
# ---------------------------------------------------------------------------


def _fmt_over(numerator: str, denom) -> str:
    return f"{numerator}/{denom}"


def _shape_axb_foundation(rng: random.Random) -> Question:
    a = rng.randint(2, 9)
    b = rng.randint(-20, 20)

    if b > 0:
        rhs = f"(y - {b})/{a}"
    elif b < 0:
        rhs = f"(y + {-b})/{a}"
    else:
        rhs = f"y/{a}"
    claimed = sp.Rational(1, a) * (Y - b)

    # Independent verification: use sympy's own equation solver on the
    # original equation, a genuinely different path than the manual
    # subtract-then-divide rearrangement used to build the displayed steps.
    solved = sp.solve(sp.Eq(Y, a * X + b), X)
    if not solved or sp.simplify(solved[0] - claimed) != 0:
        raise ValueError("change_subject axb (foundation) verification failed")

    steps = [f"y = {fmt_linear(a, b)}"]
    if b > 0:
        steps.append(f"Subtract {b} from both sides: y - {b} = {a}x")
    elif b < 0:
        steps.append(f"Add {-b} to both sides: y + {-b} = {a}x")
    steps.append(f"Divide both sides by {a}: x = {rhs}")

    return Question(
        topic_id="change_subject_foundation",
        tier=Tier.FOUNDATION,
        prompt=f"Make x the subject of the formula y = {fmt_linear(a, b)}.",
        solution_steps=tuple(steps),
        final_answer=f"x = {rhs}",
        dedup_key=f"subject_axb:{a}:{b}",
    )


def _shape_suvat_foundation(rng: random.Random) -> Question:
    a = rng.randint(2, 20)
    rhs = f"(v - u)/{a}"
    claimed = sp.Rational(1, a) * (V - U)

    solved = sp.solve(sp.Eq(V, U + a * T), T)
    if not solved or sp.simplify(solved[0] - claimed) != 0:
        raise ValueError("change_subject suvat (foundation) verification failed")

    steps = [
        f"v = u + {a}t",
        f"Subtract u from both sides: v - u = {a}t",
        f"Divide both sides by {a}: t = {rhs}",
    ]
    return Question(
        topic_id="change_subject_foundation",
        tier=Tier.FOUNDATION,
        prompt=f"Make t the subject of the formula v = u + {a}t.",
        solution_steps=tuple(steps),
        final_answer=f"t = {rhs}",
        dedup_key=f"subject_suvat:{a}",
    )


def _shape_area_foundation(rng: random.Random) -> Question:
    subject = rng.choice(["l", "w"])

    if subject == "w":
        rhs = "A/l"
        claimed = A_SYM / L
        solved = sp.solve(sp.Eq(A_SYM, L * W), W)
        if not solved or sp.simplify(solved[0] - claimed) != 0:
            raise ValueError("change_subject area (foundation) verification failed")
        steps = ["A = lw", "Divide both sides by l: w = A/l"]
        prompt = "Make w the subject of the formula A = lw."
        final_answer = "w = A/l"
    else:
        rhs = "A/w"
        claimed = A_SYM / W
        solved = sp.solve(sp.Eq(A_SYM, L * W), L)
        if not solved or sp.simplify(solved[0] - claimed) != 0:
            raise ValueError("change_subject area (foundation) verification failed")
        steps = ["A = lw", "Divide both sides by w: l = A/w"]
        prompt = "Make l the subject of the formula A = lw."
        final_answer = "l = A/w"

    return Question(
        topic_id="change_subject_foundation",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=final_answer,
        dedup_key=f"subject_arealw:{subject}",
    )


def _shape_perimeter_foundation(rng: random.Random) -> Question:
    subject = rng.choice(["l", "w"])

    if subject == "l":
        claimed = (P_SYM - 2 * W) / 2
        solved = sp.solve(sp.Eq(P_SYM, 2 * L + 2 * W), L)
        if not solved or sp.simplify(solved[0] - claimed) != 0:
            raise ValueError("change_subject perimeter (foundation) verification failed")
        steps = [
            "P = 2l + 2w",
            "Subtract 2w from both sides: P - 2w = 2l",
            "Divide both sides by 2: l = (P - 2w)/2",
        ]
        prompt = "Make l the subject of the formula P = 2l + 2w."
        final_answer = "l = (P - 2w)/2"
    else:
        claimed = (P_SYM - 2 * L) / 2
        solved = sp.solve(sp.Eq(P_SYM, 2 * L + 2 * W), W)
        if not solved or sp.simplify(solved[0] - claimed) != 0:
            raise ValueError("change_subject perimeter (foundation) verification failed")
        steps = [
            "P = 2l + 2w",
            "Subtract 2l from both sides: P - 2l = 2w",
            "Divide both sides by 2: w = (P - 2l)/2",
        ]
        prompt = "Make w the subject of the formula P = 2l + 2w."
        final_answer = "w = (P - 2l)/2"

    return Question(
        topic_id="change_subject_foundation",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=final_answer,
        dedup_key=f"subject_perimeter:{subject}",
    )


def _shape_circumference_foundation(rng: random.Random) -> Question:
    claimed = C_SYM / (2 * sp.pi)
    solved = sp.solve(sp.Eq(C_SYM, 2 * sp.pi * R_SYM), R_SYM)
    if not solved or sp.simplify(solved[0] - claimed) != 0:
        raise ValueError("change_subject circumference (foundation) verification failed")

    steps = ["C = 2πr", "Divide both sides by 2π: r = C/(2π)"]
    return Question(
        topic_id="change_subject_foundation",
        tier=Tier.FOUNDATION,
        prompt="Make r the subject of the formula C = 2πr.",
        solution_steps=tuple(steps),
        final_answer="r = C/(2π)",
        dedup_key="subject_circ",
    )


_FOUNDATION_SHAPES = [
    _shape_axb_foundation,
    _shape_suvat_foundation,
    _shape_area_foundation,
    _shape_perimeter_foundation,
    _shape_circumference_foundation,
]

# Weighted towards the two shapes with many possible integer coefficients
# (axb, suvat) - the other three are fixed real-world formulas with only 1-2
# possible "which letter is the subject" variants, so drawing them as often
# as the others would starve the topic's overall dedup-key variety.
_FOUNDATION_WEIGHTS = [4, 3, 1, 1, 1]


def generate_change_subject_foundation(tier: Tier, rng: random.Random) -> Question:
    shape = rng.choices(_FOUNDATION_SHAPES, weights=_FOUNDATION_WEIGHTS, k=1)[0]
    q = shape(rng)
    return dataclasses.replace(q, topic_id="change_subject_foundation", tier=Tier.FOUNDATION)


# ---------------------------------------------------------------------------
# Higher: subject appears twice, or is squared/rooted, or inside a fraction.
# ---------------------------------------------------------------------------


def _shape_double_occurrence_higher(rng: random.Random) -> Question:
    a = rng.randint(2, 8)
    b = rng.randint(2, 8)
    while b == a:
        b = rng.randint(2, 8)
    c = rng.randint(-20, 20)

    rhs = f"(y - {c})/{a + b}" if c > 0 else (f"(y + {-c})/{a + b}" if c < 0 else f"y/{a + b}")
    claimed = (Y - c) / (a + b)

    # Independent verification: sp.solve the original equation directly, a
    # genuinely different path than the collect-and-divide steps shown.
    solved = sp.solve(sp.Eq(Y, a * X + b * X + c), X)
    if not solved or sp.simplify(solved[0] - claimed) != 0:
        raise ValueError("change_subject double-occurrence (higher) verification failed")

    steps = [f"y = {a}x + {b}x + {fmt_num(c)}" if c != 0 else f"y = {a}x + {b}x"]
    if c > 0:
        steps.append(f"Subtract {c} from both sides: y - {c} = {a}x + {b}x")
    elif c < 0:
        steps.append(f"Add {-c} to both sides: y + {-c} = {a}x + {b}x")
    steps.append(f"Factorise the right-hand side: {'y - ' + str(c) if c > 0 else ('y + ' + str(-c) if c < 0 else 'y')} = ({a + b})x")
    steps.append(f"Divide both sides by {a + b}: x = {rhs}")

    return Question(
        topic_id="change_subject_higher",
        tier=Tier.HIGHER,
        prompt=f"Make x the subject of the formula y = {a}x + {b}x + {c}." if c != 0 else f"Make x the subject of the formula y = {a}x + {b}x.",
        solution_steps=tuple(steps),
        final_answer=f"x = {rhs}",
        dedup_key=f"subject_h_double:{a}:{b}:{c}",
    )


def _shape_squared_higher(rng: random.Random) -> Question:
    k = rng.randint(1, 6)
    coeff_text = "" if k == 1 else str(k)
    rhs = f"√(A/({coeff_text}π))" if k != 1 else "√(A/π)"
    claimed = sp.sqrt(A_SYM / (k * sp.pi))

    # Independent verification: use sympy's solver on the original equation
    # A = kπr^2, then confirm the claimed (positive) root matches one of its
    # returned solutions - a different path than manually dividing then
    # square-rooting.
    solved = sp.solve(sp.Eq(A_SYM, k * sp.pi * R_SYM**2), R_SYM)
    if not any(sp.simplify(sol - claimed) == 0 for sol in solved):
        raise ValueError("change_subject squared (higher) verification failed")

    formula_text = f"A = {coeff_text}πr^2" if k != 1 else "A = πr^2"
    steps = [
        formula_text,
        f"Divide both sides by {coeff_text}π: A/({coeff_text}π) = r^2" if k != 1 else "Divide both sides by π: A/π = r^2",
        f"Take the square root of both sides: r = {rhs}",
    ]
    return Question(
        topic_id="change_subject_higher",
        tier=Tier.HIGHER,
        prompt=f"Make r the subject of the formula {formula_text}.",
        solution_steps=tuple(steps),
        final_answer=f"r = {rhs}",
        dedup_key=f"subject_h_sqrt:{k}",
    )


def _shape_fraction_higher(rng: random.Random) -> Question:
    a = rng.randint(1, 15)
    b = rng.randint(1, 15)

    rhs = f"({a} + {b}y)/(y - 1)"
    claimed = (a + b * Y) / (Y - 1)

    # Independent verification: sp.solve the original fractional equation
    # directly, a genuinely different path than the manual cross-multiply /
    # collect / factorise steps used to build the displayed solution.
    solved = sp.solve(sp.Eq(Y, (X + a) / (X - b)), X)
    if not solved or sp.simplify(solved[0] - claimed) != 0:
        raise ValueError("change_subject fraction (higher) verification failed")

    steps = [
        f"y = (x + {a})/(x - {b})",
        f"Multiply both sides by (x - {b}): y(x - {b}) = x + {a}",
        f"Expand the bracket: yx - {b}y = x + {a}",
        f"Collect the x-terms on one side: yx - x = {a} + {b}y",
        f"Factorise: x(y - 1) = {a} + {b}y",
        f"Divide both sides by (y - 1): x = {rhs}",
    ]
    return Question(
        topic_id="change_subject_higher",
        tier=Tier.HIGHER,
        prompt=f"Make x the subject of the formula y = (x + {a})/(x - {b}).",
        solution_steps=tuple(steps),
        final_answer=f"x = {rhs}",
        dedup_key=f"subject_h_fraction:{a}:{b}",
    )


_HIGHER_SHAPES = [
    _shape_double_occurrence_higher,
    _shape_squared_higher,
    _shape_fraction_higher,
]


def generate_change_subject_higher(tier: Tier, rng: random.Random) -> Question:
    shape = rng.choice(_HIGHER_SHAPES)
    q = shape(rng)
    return dataclasses.replace(q, topic_id="change_subject_higher", tier=Tier.HIGHER)


# ---------------------------------------------------------------------------
# Modelled examples (foundation)
# ---------------------------------------------------------------------------


def _modelled_axb_foundation(rng: random.Random) -> ModelledExample:
    a = rng.randint(2, 9)
    b = rng.randint(-20, 20)

    if b > 0:
        rhs = f"(y - {b})/{a}"
    elif b < 0:
        rhs = f"(y + {-b})/{a}"
    else:
        rhs = f"y/{a}"
    claimed = sp.Rational(1, a) * (Y - b)

    solved = sp.solve(sp.Eq(Y, a * X + b), X)
    if not solved or sp.simplify(solved[0] - claimed) != 0:
        raise ValueError("modelled example change_subject axb (foundation) verification failed")

    teaching_steps = [
        "'Making x the subject' means rearranging the formula so it reads 'x = ...' instead of "
        "'y = ...' - x needs to end up on its own on one side, with everything else on the other.",
        f"Start with y = {fmt_linear(a, b)}. Undo the operations applied to x, working in reverse "
        "order to how they were applied (last operation undone first).",
        (
            f"The constant {b} was added last, so undo that first by "
            f"{'subtracting ' + str(b) if b > 0 else 'adding ' + str(-b)} from both sides."
            if b != 0
            else "There's no constant term here, so the only step is undoing the multiplication."
        ),
        f"Finally undo the multiplication by {a} by dividing both sides by {a}, giving x = {rhs}.",
        f"Check this is right by substituting the rearranged formula back into the original and "
        "confirming both sides genuinely match - this is exactly what a computer algebra check does.",
    ]
    worked_calculation = [f"y = {fmt_linear(a, b)}", f"x = {rhs}"]
    return ModelledExample(
        topic_id="change_subject_foundation",
        tier=Tier.FOUNDATION,
        prompt=f"Make x the subject of the formula y = {fmt_linear(a, b)}.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"x = {rhs}",
    )


def _modelled_suvat_foundation(rng: random.Random) -> ModelledExample:
    a = rng.randint(2, 20)
    rhs = f"(v - u)/{a}"
    claimed = sp.Rational(1, a) * (V - U)

    solved = sp.solve(sp.Eq(V, U + a * T), T)
    if not solved or sp.simplify(solved[0] - claimed) != 0:
        raise ValueError("modelled example change_subject suvat (foundation) verification failed")

    teaching_steps = [
        "This formula has three letters, but we only care about isolating t - u and v can simply "
        "be treated as 'just numbers' for the purposes of the rearranging, even though we never "
        "know their actual values.",
        f"v = u + {a}t has u added on last, so undo that first: subtract u from both sides, "
        f"giving v - u = {a}t.",
        f"Now t is only being multiplied by {a}, so divide both sides by {a} to finish: "
        f"t = {rhs}.",
        "The order matters here - always undo the 'outermost' operation first, working inwards "
        "towards the letter you want, just like solving a normal equation for x.",
    ]
    worked_calculation = [f"v = u + {a}t", f"t = {rhs}"]
    return ModelledExample(
        topic_id="change_subject_foundation",
        tier=Tier.FOUNDATION,
        prompt=f"Make t the subject of the formula v = u + {a}t.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"t = {rhs}",
    )


def _modelled_area_foundation(rng: random.Random) -> ModelledExample:
    subject = rng.choice(["l", "w"])

    if subject == "w":
        claimed = A_SYM / L
        solved = sp.solve(sp.Eq(A_SYM, L * W), W)
        if not solved or sp.simplify(solved[0] - claimed) != 0:
            raise ValueError("modelled example change_subject area (foundation) verification failed")
        prompt = "Make w the subject of the formula A = lw."
        final_answer = "w = A/l"
        teaching_steps = [
            "A = lw says area equals length times width - both l and w are multiplied together "
            "to give A.",
            "To undo a multiplication, divide. Since we want w on its own, divide both sides by l "
            "(the thing currently multiplying it).",
            f"That leaves w = A/l, with l and A left exactly as they were - we never actually "
            "need to know their numeric values to rearrange the formula.",
        ]
        worked_calculation = ["A = lw", "w = A/l"]
    else:
        claimed = A_SYM / W
        solved = sp.solve(sp.Eq(A_SYM, L * W), L)
        if not solved or sp.simplify(solved[0] - claimed) != 0:
            raise ValueError("modelled example change_subject area (foundation) verification failed")
        prompt = "Make l the subject of the formula A = lw."
        final_answer = "l = A/w"
        teaching_steps = [
            "A = lw says area equals length times width - both l and w are multiplied together "
            "to give A.",
            "To undo a multiplication, divide. Since we want l on its own, divide both sides by w "
            "(the thing currently multiplying it).",
            "That leaves l = A/w, with w and A left exactly as they were - we never actually "
            "need to know their numeric values to rearrange the formula.",
        ]
        worked_calculation = ["A = lw", "l = A/w"]

    return ModelledExample(
        topic_id="change_subject_foundation",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=final_answer,
    )


def _modelled_perimeter_foundation(rng: random.Random) -> ModelledExample:
    subject = rng.choice(["l", "w"])

    if subject == "l":
        claimed = (P_SYM - 2 * W) / 2
        solved = sp.solve(sp.Eq(P_SYM, 2 * L + 2 * W), L)
        if not solved or sp.simplify(solved[0] - claimed) != 0:
            raise ValueError("modelled example change_subject perimeter (foundation) verification failed")
        prompt = "Make l the subject of the formula P = 2l + 2w."
        final_answer = "l = (P - 2w)/2"
        teaching_steps = [
            "P = 2l + 2w adds two terms together: 2l (twice the length) and 2w (twice the width).",
            "Since we want l, first get rid of the 2w term by subtracting it from both sides: "
            "P - 2w = 2l.",
            "Now l is only being multiplied by 2, so divide both sides by 2 to finish: "
            "l = (P - 2w)/2.",
        ]
        worked_calculation = ["P = 2l + 2w", "P - 2w = 2l", "l = (P - 2w)/2"]
    else:
        claimed = (P_SYM - 2 * L) / 2
        solved = sp.solve(sp.Eq(P_SYM, 2 * L + 2 * W), W)
        if not solved or sp.simplify(solved[0] - claimed) != 0:
            raise ValueError("modelled example change_subject perimeter (foundation) verification failed")
        prompt = "Make w the subject of the formula P = 2l + 2w."
        final_answer = "w = (P - 2l)/2"
        teaching_steps = [
            "P = 2l + 2w adds two terms together: 2l (twice the length) and 2w (twice the width).",
            "Since we want w, first get rid of the 2l term by subtracting it from both sides: "
            "P - 2l = 2w.",
            "Now w is only being multiplied by 2, so divide both sides by 2 to finish: "
            "w = (P - 2l)/2.",
        ]
        worked_calculation = ["P = 2l + 2w", "P - 2l = 2w", "w = (P - 2l)/2"]

    return ModelledExample(
        topic_id="change_subject_foundation",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=final_answer,
    )


def _modelled_circumference_foundation(rng: random.Random) -> ModelledExample:
    claimed = C_SYM / (2 * sp.pi)
    solved = sp.solve(sp.Eq(C_SYM, 2 * sp.pi * R_SYM), R_SYM)
    if not solved or sp.simplify(solved[0] - claimed) != 0:
        raise ValueError("modelled example change_subject circumference (foundation) verification failed")

    teaching_steps = [
        "C = 2πr is the circumference formula - r is currently being multiplied by both 2 and π "
        "together.",
        "Treat '2π' as a single combined multiplier (it's just a number, roughly 6.28, even "
        "though we write it symbolically). Divide both sides by 2π to undo that multiplication.",
        "That leaves r = C/(2π) - the radius written in terms of the circumference.",
    ]
    worked_calculation = ["C = 2πr", "r = C/(2π)"]
    return ModelledExample(
        topic_id="change_subject_foundation",
        tier=Tier.FOUNDATION,
        prompt="Make r the subject of the formula C = 2πr.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer="r = C/(2π)",
    )


_FOUNDATION_MODELLED_SHAPES = [
    _modelled_axb_foundation,
    _modelled_suvat_foundation,
    _modelled_area_foundation,
    _modelled_perimeter_foundation,
    _modelled_circumference_foundation,
]


def generate_modelled_example_change_subject_foundation(tier: Tier, rng: random.Random) -> ModelledExample:
    shape = rng.choices(_FOUNDATION_MODELLED_SHAPES, weights=_FOUNDATION_WEIGHTS, k=1)[0]
    example = shape(rng)
    return dataclasses.replace(example, topic_id="change_subject_foundation", tier=Tier.FOUNDATION)


# ---------------------------------------------------------------------------
# Modelled examples (higher)
# ---------------------------------------------------------------------------


def _modelled_double_occurrence_higher(rng: random.Random) -> ModelledExample:
    a = rng.randint(2, 8)
    b = rng.randint(2, 8)
    while b == a:
        b = rng.randint(2, 8)
    c = rng.randint(-20, 20)

    rhs = f"(y - {c})/{a + b}" if c > 0 else (f"(y + {-c})/{a + b}" if c < 0 else f"y/{a + b}")
    claimed = (Y - c) / (a + b)

    solved = sp.solve(sp.Eq(Y, a * X + b * X + c), X)
    if not solved or sp.simplify(solved[0] - claimed) != 0:
        raise ValueError("modelled example change_subject double-occurrence (higher) verification failed")

    formula_text = f"y = {a}x + {b}x + {c}" if c != 0 else f"y = {a}x + {b}x"
    teaching_steps = [
        f"The tricky part here is that x appears twice, in two separate terms ({a}x and {b}x) - "
        "you can't isolate x until those two terms are combined into one.",
        (
            f"First deal with any plain number: {'subtract ' + str(c) if c > 0 else 'add ' + str(-c)} "
            "on both sides to leave only x-terms on the right."
            if c != 0
            else "There's no separate constant term here, so we can collect the x-terms straight away."
        ),
        f"Now factorise the right-hand side: {a}x + {b}x = ({a} + {b})x = {a + b}x, since both "
        "terms share x as a common factor.",
        f"With a single combined x-term, divide both sides by {a + b} to finish: x = {rhs}.",
        "The key habit for 'subject appears twice' questions is always: collect constants first, "
        "then factorise out x, then divide.",
    ]
    worked_calculation = [formula_text, f"{a + b}x = {'y - ' + str(c) if c > 0 else ('y + ' + str(-c) if c < 0 else 'y')}", f"x = {rhs}"]
    return ModelledExample(
        topic_id="change_subject_higher",
        tier=Tier.HIGHER,
        prompt=f"Make x the subject of the formula {formula_text}.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"x = {rhs}",
    )


def _modelled_squared_higher(rng: random.Random) -> ModelledExample:
    k = rng.randint(1, 6)
    coeff_text = "" if k == 1 else str(k)
    rhs = f"√(A/({coeff_text}π))" if k != 1 else "√(A/π)"
    claimed = sp.sqrt(A_SYM / (k * sp.pi))

    solved = sp.solve(sp.Eq(A_SYM, k * sp.pi * R_SYM**2), R_SYM)
    if not any(sp.simplify(sol - claimed) == 0 for sol in solved):
        raise ValueError("modelled example change_subject squared (higher) verification failed")

    formula_text = f"A = {coeff_text}πr^2" if k != 1 else "A = πr^2"
    teaching_steps = [
        f"Here r is squared, not just multiplied by a number - so dividing alone won't fully "
        "isolate r, we'll need a square root at the end too.",
        f"First undo the multiplication by dividing both sides by {coeff_text}π: "
        f"A/({coeff_text}π) = r^2." if k != 1 else "First undo the multiplication by dividing both sides by π: A/π = r^2.",
        f"Now undo the squaring by taking the square root of both sides: r = {rhs}. We only take "
        "the positive root, since r represents a physical radius and must be positive.",
        "A useful check: square the claimed answer back up and confirm it reproduces the "
        "original area formula exactly.",
    ]
    worked_calculation = [formula_text, f"r^2 = A/({coeff_text}π)" if k != 1 else "r^2 = A/π", f"r = {rhs}"]
    return ModelledExample(
        topic_id="change_subject_higher",
        tier=Tier.HIGHER,
        prompt=f"Make r the subject of the formula {formula_text}.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"r = {rhs}",
    )


def _modelled_fraction_higher(rng: random.Random) -> ModelledExample:
    a = rng.randint(1, 15)
    b = rng.randint(1, 15)

    rhs = f"({a} + {b}y)/(y - 1)"
    claimed = (a + b * Y) / (Y - 1)

    solved = sp.solve(sp.Eq(Y, (X + a) / (X - b)), X)
    if not solved or sp.simplify(solved[0] - claimed) != 0:
        raise ValueError("modelled example change_subject fraction (higher) verification failed")

    teaching_steps = [
        f"With x trapped inside a fraction, the first job is always to clear the fraction by "
        f"multiplying both sides by whatever is in the denominator, here (x - {b}): "
        f"y(x - {b}) = x + {a}.",
        f"Expand the bracket on the left: yx - {b}y = x + {a}.",
        f"Now x appears in two places (yx and x) - move every x-term to one side and everything "
        f"else to the other: yx - x = {a} + {b}y.",
        "Factorise out x on the left, since it's the common factor of both remaining terms: "
        f"x(y - 1) = {a} + {b}y.",
        f"Finally divide both sides by (y - 1) to isolate x: x = {rhs}.",
    ]
    worked_calculation = [
        f"y(x - {b}) = x + {a}",
        f"x(y - 1) = {a} + {b}y",
        f"x = {rhs}",
    ]
    return ModelledExample(
        topic_id="change_subject_higher",
        tier=Tier.HIGHER,
        prompt=f"Make x the subject of the formula y = (x + {a})/(x - {b}).",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"x = {rhs}",
    )


_HIGHER_MODELLED_SHAPES = [
    _modelled_double_occurrence_higher,
    _modelled_squared_higher,
    _modelled_fraction_higher,
]


def generate_modelled_example_change_subject_higher(tier: Tier, rng: random.Random) -> ModelledExample:
    shape = rng.choice(_HIGHER_MODELLED_SHAPES)
    example = shape(rng)
    return dataclasses.replace(example, topic_id="change_subject_higher", tier=Tier.HIGHER)


TOPIC_CHANGE_SUBJECT_FOUNDATION = TopicDefinition(
    id="change_subject_foundation",
    display_name="Changing the Subject of a Formula",
    description="Rearrange a formula to make a different letter the subject (appears exactly once).",
    generate=generate_change_subject_foundation,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_change_subject_foundation,
)

TOPIC_CHANGE_SUBJECT_HIGHER = TopicDefinition(
    id="change_subject_higher",
    display_name="Changing the Subject of a Formula (Higher)",
    description=(
        "Rearrange a formula to make a letter the subject when it appears twice, is squared or "
        "rooted, or sits inside a fraction."
    ),
    generate=generate_change_subject_higher,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_change_subject_higher,
)
