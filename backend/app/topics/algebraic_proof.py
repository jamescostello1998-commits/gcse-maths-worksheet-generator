"""Algebraic proof: classic GCSE "prove algebraically that..." number-property
questions (Higher only).

Unlike almost every other topic in this app, these proofs are general claims
about ALL integers n - the proof itself doesn't depend on drawing a random
number each time, only on which curated template is picked. So the natural
question variety here is the size of the template bank, not a combinatorial
space of random integers (see the "Show that root n lies between two
consecutive integers" precedent in powers_roots.py for the same non-numeric
final_answer style, though even that topic still varies its numbers - this
one genuinely can't, since a proof "for a specific n" wouldn't be a proof at
all). `TopicDefinition.question_count` is therefore set to the template bank
size rather than the usual default of 20.
"""

import random
from typing import Callable, NamedTuple, Optional

import sympy as sp

from app.core.models import ModelledExample, Question, Tier
from app.topics.base import TopicDefinition

SECTION = "algebra"
GROUP = "Algebraic Proof"

N = sp.symbols("n")
M = sp.symbols("m")


def _verify_identity(raw: sp.Expr, coeff: int, inner: sp.Expr, remainder: int) -> None:
    """Verify raw ≡ coeff*inner + remainder for every value of n, via sympy
    expansion - independent of however the displayed steps were written."""
    residual = sp.expand(raw - (coeff * inner + remainder))
    if residual != 0:
        raise ValueError("algebraic_proof: identity verification failed")


def _verify_congruent(raw: sp.Expr, divisor: int, remainder: int = 0, modulus: Optional[int] = None) -> None:
    """Verify raw ≡ remainder (mod divisor) for every integer n, by
    substituting n = modulus*m + r for every residue r and checking the
    quotient (raw - remainder) / divisor is an integer-coefficient polynomial
    in m. This is a genuinely different verification method than the
    'factor out a constant' identity check above - it's needed for claims
    like "the product of two consecutive integers is even", where the factor
    of 2 comes from parity casework, not from a fixed polynomial factor."""
    modulus = modulus or divisor
    for r in range(modulus):
        case_expr = sp.expand(raw.subs(N, modulus * M + r))
        quotient = sp.expand((case_expr - remainder) / divisor)
        poly = quotient.as_poly(M)
        coeffs = poly.all_coeffs() if poly is not None else [quotient]
        if not all(sp.Rational(c).is_Integer for c in coeffs):
            raise ValueError(f"algebraic_proof: congruence verification failed for residue {r} mod {modulus}")


class _Template(NamedTuple):
    id: str
    claim: str  # e.g. "the sum of two consecutive integers is always odd"
    definitions: tuple[str, ...]
    expression_line: str
    expanded_line: str
    factored_line: str  # the line that exposes the multiple/parity structure
    conclusion: str
    final_answer: str
    verify: Callable[[], None]


def _t(id, claim, definitions, expression_line, expanded_line, factored_line, conclusion, final_answer, verify):
    return _Template(id, claim, tuple(definitions), expression_line, expanded_line, factored_line, conclusion, final_answer, verify)


TEMPLATES: list[_Template] = [
    _t(
        "sum_two_consecutive_odd",
        "the sum of two consecutive integers is always odd",
        ["Let two consecutive integers be n and n + 1."],
        "n + (n + 1)",
        "2n + 1",
        "2n + 1",
        "2n is always a multiple of 2 (even), so 2n + 1 is always exactly 1 more than an even "
        "number - that makes it always odd.",
        "Proven: n + (n + 1) = 2n + 1, which is always odd since 2n is always even.",
        lambda: _verify_identity(N + (N + 1), 2, N, 1),
    ),
    _t(
        "sum_three_consecutive_mult3",
        "the sum of three consecutive integers is always a multiple of 3",
        ["Let three consecutive integers be n, n + 1 and n + 2."],
        "n + (n + 1) + (n + 2)",
        "3n + 3",
        "3(n + 1)",
        "Since 3n + 3 factorises exactly to 3(n + 1), the sum is always 3 times a whole number, "
        "so it is always a multiple of 3.",
        "Proven: the sum is 3(n + 1), always a multiple of 3.",
        lambda: _verify_identity(N + (N + 1) + (N + 2), 3, N + 1, 0),
    ),
    _t(
        "sum_five_consecutive_mult5",
        "the sum of five consecutive integers is always a multiple of 5",
        ["Let five consecutive integers be n, n + 1, n + 2, n + 3 and n + 4."],
        "n + (n + 1) + (n + 2) + (n + 3) + (n + 4)",
        "5n + 10",
        "5(n + 2)",
        "Since 5n + 10 factorises exactly to 5(n + 2), the sum is always 5 times a whole number, "
        "so it is always a multiple of 5.",
        "Proven: the sum is 5(n + 2), always a multiple of 5.",
        lambda: _verify_identity(N + (N + 1) + (N + 2) + (N + 3) + (N + 4), 5, N + 2, 0),
    ),
    _t(
        "sum_four_consecutive_even",
        "the sum of four consecutive integers is always even",
        ["Let four consecutive integers be n, n + 1, n + 2 and n + 3."],
        "n + (n + 1) + (n + 2) + (n + 3)",
        "4n + 6",
        "2(2n + 3)",
        "Since 4n + 6 factorises exactly to 2(2n + 3), the sum is always 2 times a whole number, "
        "so it is always even - though because 2n + 3 is itself always odd, the sum is NOT "
        "always a multiple of 4.",
        "Proven: the sum is 2(2n + 3), always even (but not always a multiple of 4).",
        lambda: _verify_identity(N + (N + 1) + (N + 2) + (N + 3), 2, 2 * N + 3, 0),
    ),
    _t(
        "product_two_consecutive_even",
        "the product of two consecutive integers is always even",
        ["Let two consecutive integers be n and n + 1."],
        "n(n + 1)",
        "n^2 + n",
        "if n is even, n(n + 1) is even × anything = even; if n is odd, then n + 1 is even, so "
        "n(n + 1) is anything × even = even",
        "Either n or n + 1 must be even (they can't both be odd), so their product always has an "
        "even factor - the product is always even, whichever case n falls into.",
        "Proven: n(n + 1) is always even, since one of n, n + 1 is always even.",
        lambda: _verify_congruent(N * (N + 1), divisor=2, remainder=0, modulus=2),
    ),
    _t(
        "sum_two_consecutive_odd_numbers_mult4",
        "the sum of two consecutive odd numbers is always a multiple of 4",
        ["Let two consecutive odd numbers be 2n + 1 and 2n + 3 (for integer n)."],
        "(2n + 1) + (2n + 3)",
        "4n + 4",
        "4(n + 1)",
        "Since 4n + 4 factorises exactly to 4(n + 1), the sum is always 4 times a whole number, "
        "so it is always a multiple of 4.",
        "Proven: the sum is 4(n + 1), always a multiple of 4.",
        lambda: _verify_identity((2 * N + 1) + (2 * N + 3), 4, N + 1, 0),
    ),
    _t(
        "product_two_consecutive_odds_odd",
        "the product of two consecutive odd numbers is always odd",
        ["Let two consecutive odd numbers be 2n + 1 and 2n + 3 (for integer n)."],
        "(2n + 1)(2n + 3)",
        "4n^2 + 8n + 3",
        "2(2n^2 + 4n + 1) + 1",
        "Since 4n^2 + 8n + 3 is exactly 1 more than the even number 2(2n^2 + 4n + 1), the product "
        "is always odd.",
        "Proven: the product is 2(2n^2 + 4n + 1) + 1, always odd.",
        lambda: _verify_identity((2 * N + 1) * (2 * N + 3), 2, 2 * N**2 + 4 * N + 1, 1),
    ),
    _t(
        "diff_squares_consecutive_equals_sum",
        "the difference between the squares of two consecutive integers equals their sum",
        ["Let two consecutive integers be n and n + 1."],
        "(n + 1)^2 - n^2",
        "2n + 1",
        "n + (n + 1)",
        "2n + 1 is exactly n + (n + 1), the sum of the two original integers - so the difference "
        "of their squares always equals their sum.",
        "Proven: (n + 1)^2 - n^2 = 2n + 1 = n + (n + 1), their sum.",
        lambda: _verify_identity((N + 1) ** 2 - N**2, 1, N + (N + 1), 0),
    ),
    _t(
        "diff_squares_consecutive_even_mult4",
        "the difference between the squares of two consecutive even numbers is always a multiple of 4",
        ["Let two consecutive even numbers be 2n and 2n + 2 (for integer n)."],
        "(2n + 2)^2 - (2n)^2",
        "8n + 4",
        "4(2n + 1)",
        "Since 8n + 4 factorises exactly to 4(2n + 1), the difference is always 4 times a whole "
        "number, so it is always a multiple of 4.",
        "Proven: the difference is 4(2n + 1), always a multiple of 4.",
        lambda: _verify_identity((2 * N + 2) ** 2 - (2 * N) ** 2, 4, 2 * N + 1, 0),
    ),
    _t(
        "diff_squares_consecutive_odd_mult8",
        "the difference between the squares of two consecutive odd numbers is always a multiple of 8",
        ["Let two consecutive odd numbers be 2n + 1 and 2n + 3 (for integer n)."],
        "(2n + 3)^2 - (2n + 1)^2",
        "8n + 8",
        "8(n + 1)",
        "Since 8n + 8 factorises exactly to 8(n + 1), the difference is always 8 times a whole "
        "number, so it is always a multiple of 8.",
        "Proven: the difference is 8(n + 1), always a multiple of 8.",
        lambda: _verify_identity((2 * N + 3) ** 2 - (2 * N + 1) ** 2, 8, N + 1, 0),
    ),
    _t(
        "n_squared_minus_n_even",
        "n^2 - n is always even",
        ["n^2 - n factorises as n(n - 1), the product of two consecutive integers n - 1 and n."],
        "n^2 - n",
        "n(n - 1)",
        "if n is even, n(n - 1) is even × anything = even; if n is odd, then n - 1 is even, so "
        "n(n - 1) is anything × even = even",
        "Either n or n - 1 must be even (they are consecutive integers, so they can't both be "
        "odd), so the product always has an even factor - n^2 - n is always even.",
        "Proven: n^2 - n = n(n - 1) is always even, since one of n, n - 1 is always even.",
        lambda: _verify_congruent(N**2 - N, divisor=2, remainder=0, modulus=2),
    ),
    _t(
        "n_squared_plus_n_even",
        "n^2 + n is always even",
        ["n^2 + n factorises as n(n + 1), the product of two consecutive integers n and n + 1."],
        "n^2 + n",
        "n(n + 1)",
        "if n is even, n(n + 1) is even × anything = even; if n is odd, then n + 1 is even, so "
        "n(n + 1) is anything × even = even",
        "Either n or n + 1 must be even (they are consecutive integers, so they can't both be "
        "odd), so the product always has an even factor - n^2 + n is always even.",
        "Proven: n^2 + n = n(n + 1) is always even, since one of n, n + 1 is always even.",
        lambda: _verify_congruent(N**2 + N, divisor=2, remainder=0, modulus=2),
    ),
    _t(
        "diff_squares_gap4_mult8",
        "(n + 2)^2 - (n - 2)^2 is always a multiple of 8",
        ["Let n be any integer, with n + 2 and n - 2 the integers 2 either side of it."],
        "(n + 2)^2 - (n - 2)^2",
        "8n",
        "8n",
        "8n is exactly 8 times the whole number n, so the expression is always a multiple of 8.",
        "Proven: (n + 2)^2 - (n - 2)^2 = 8n, always a multiple of 8.",
        lambda: _verify_identity((N + 2) ** 2 - (N - 2) ** 2, 8, N, 0),
    ),
    _t(
        "diff_squares_gap2_mult4",
        "(n + 1)^2 - (n - 1)^2 is always a multiple of 4",
        ["Let n be any integer, with n + 1 and n - 1 the integers either side of it."],
        "(n + 1)^2 - (n - 1)^2",
        "4n",
        "4n",
        "4n is exactly 4 times the whole number n, so the expression is always a multiple of 4.",
        "Proven: (n + 1)^2 - (n - 1)^2 = 4n, always a multiple of 4.",
        lambda: _verify_identity((N + 1) ** 2 - (N - 1) ** 2, 4, N, 0),
    ),
    _t(
        "linear_combination_mult6",
        "2n(n + 3) - 2n^2 is always a multiple of 6",
        ["Let n be any integer."],
        "2n(n + 3) - 2n^2",
        "6n",
        "6n",
        "6n is exactly 6 times the whole number n, so the expression is always a multiple of 6.",
        "Proven: 2n(n + 3) - 2n^2 = 6n, always a multiple of 6.",
        lambda: _verify_identity(2 * N * (N + 3) - 2 * N**2, 6, N, 0),
    ),
    _t(
        "sum_squares_consecutive_odd",
        "the sum of the squares of two consecutive integers is always odd",
        ["Let two consecutive integers be n and n + 1."],
        "n^2 + (n + 1)^2",
        "2n^2 + 2n + 1",
        "2(n^2 + n) + 1",
        "n^2 + n is always a whole number, so 2(n^2 + n) is always even - and the sum of squares "
        "is exactly 1 more than that even number, so it is always odd.",
        "Proven: n^2 + (n + 1)^2 = 2(n^2 + n) + 1, always odd.",
        lambda: _verify_identity(N**2 + (N + 1) ** 2, 2, N**2 + N, 1),
    ),
    _t(
        "diff_squares_gap3_mult4",
        "(n + 3)^2 - (n + 1)^2 is always a multiple of 4",
        ["Let n be any integer, with n + 1 and n + 3 two integers 2 apart from each other."],
        "(n + 3)^2 - (n + 1)^2",
        "4n + 8",
        "4(n + 2)",
        "Since 4n + 8 factorises exactly to 4(n + 2), the difference is always 4 times a whole "
        "number, so it is always a multiple of 4.",
        "Proven: (n + 3)^2 - (n + 1)^2 = 4(n + 2), always a multiple of 4.",
        lambda: _verify_identity((N + 3) ** 2 - (N + 1) ** 2, 4, N + 2, 0),
    ),
    _t(
        "sum_integer_and_square_even",
        "the sum of an integer and its square is always even",
        ["n + n^2 factorises as n(n + 1), the product of two consecutive integers n and n + 1."],
        "n + n^2",
        "n(n + 1)",
        "if n is even, n(n + 1) is even × anything = even; if n is odd, then n + 1 is even, so "
        "n(n + 1) is anything × even = even",
        "Either n or n + 1 must be even (they are consecutive integers), so the product always "
        "has an even factor - n + n^2 is always even.",
        "Proven: n + n^2 = n(n + 1) is always even, since one of n, n + 1 is always even.",
        lambda: _verify_congruent(N + N**2, divisor=2, remainder=0, modulus=2),
    ),
    _t(
        "square_odd_minus_one_mult4",
        "(2n + 1)^2 - 1 is always a multiple of 4 (and, in fact, of 8)",
        ["Let 2n + 1 be any odd number (for integer n)."],
        "(2n + 1)^2 - 1",
        "4n^2 + 4n",
        "4n(n + 1)",
        "4n(n + 1) is always a multiple of 4. But n(n + 1) is itself always even (one of n, n + 1 "
        "is always even), so 4n(n + 1) is actually always a multiple of 4 × 2 = 8 as well.",
        "Proven: (2n + 1)^2 - 1 = 4n(n + 1), a multiple of 4 (and of 8, since n(n + 1) is even).",
        lambda: (
            _verify_identity((2 * N + 1) ** 2 - 1, 4, N * (N + 1), 0),
            _verify_congruent((2 * N + 1) ** 2 - 1, divisor=8, remainder=0, modulus=2),
        ),
    ),
    _t(
        "product_three_consecutive_mult6",
        "the product of three consecutive integers is always a multiple of 6",
        ["Let three consecutive integers be n, n + 1 and n + 2."],
        "n(n + 1)(n + 2)",
        "n^3 + 3n^2 + 2n",
        "among any 3 consecutive integers, one is a multiple of 3, and at least one is even, so "
        "their product always carries both a factor of 3 and a factor of 2",
        "Since one of any three consecutive integers is always a multiple of 3, and at least one "
        "is always even, the product always has both 2 and 3 as factors - so it is always a "
        "multiple of 2 × 3 = 6.",
        "Proven: n(n + 1)(n + 2) is always a multiple of 6.",
        lambda: _verify_congruent(N * (N + 1) * (N + 2), divisor=6, remainder=0, modulus=6),
    ),
    _t(
        "n_squared_plus_n_plus_one_odd",
        "n^2 + n + 1 is always odd",
        ["n^2 + n factorises as n(n + 1), the product of two consecutive integers n and n + 1."],
        "n^2 + n + 1",
        "n(n + 1) + 1",
        "n(n + 1) is always even (one of n, n + 1 is always even), so n(n + 1) + 1 is always 1 "
        "more than an even number",
        "Since n(n + 1) is always even, adding 1 to it always gives an odd number - so n^2 + n + 1 "
        "is always odd.",
        "Proven: n^2 + n + 1 = n(n + 1) + 1, always odd since n(n + 1) is always even.",
        lambda: _verify_congruent(N**2 + N + 1, divisor=2, remainder=1, modulus=2),
    ),
    _t(
        "diff_squares_gap4_mult8_v2",
        "the difference between the squares of two integers that differ by 4 is always a multiple of 8",
        ["Let two integers that differ by 4 be n and n + 4."],
        "(n + 4)^2 - n^2",
        "8n + 16",
        "8(n + 2)",
        "Since 8n + 16 factorises exactly to 8(n + 2), the difference is always 8 times a whole "
        "number, so it is always a multiple of 8.",
        "Proven: (n + 4)^2 - n^2 = 8(n + 2), always a multiple of 8.",
        lambda: _verify_identity((N + 4) ** 2 - N**2, 8, N + 2, 0),
    ),
    _t(
        "cube_minus_n_mult6",
        "n^3 - n is always a multiple of 6",
        ["n^3 - n factorises as (n - 1)n(n + 1), the product of three consecutive integers."],
        "n^3 - n",
        "(n - 1)n(n + 1)",
        "among any 3 consecutive integers, one is a multiple of 3, and at least one is even, so "
        "their product always carries both a factor of 3 and a factor of 2",
        "Since (n - 1), n and (n + 1) are three consecutive integers, one of them is always a "
        "multiple of 3 and at least one is always even - so their product always has both 2 and "
        "3 as factors, making it always a multiple of 6.",
        "Proven: n^3 - n = (n - 1)n(n + 1) is always a multiple of 6.",
        lambda: _verify_congruent(N**3 - N, divisor=6, remainder=0, modulus=6),
    ),
    _t(
        "cube_expansion_mult6",
        "(n + 1)^3 - n^3 - 1 is always a multiple of 6",
        ["Let n be any integer."],
        "(n + 1)^3 - n^3 - 1",
        "3n^2 + 3n",
        "3n(n + 1), and n(n + 1) is always even, so 3n(n + 1) always carries a factor of 2 as "
        "well as its factor of 3",
        "3n(n + 1) is clearly a multiple of 3. But n(n + 1) is also always even (one of n, n + 1 "
        "is always even), so 3n(n + 1) is a multiple of 3 × 2 = 6 as well.",
        "Proven: (n + 1)^3 - n^3 - 1 = 3n(n + 1), always a multiple of 6.",
        lambda: _verify_congruent((N + 1) ** 3 - N**3 - 1, divisor=6, remainder=0, modulus=6),
    ),
]

_ids = [t.id for t in TEMPLATES]
if len(_ids) != len(set(_ids)):
    raise ValueError("algebraic_proof: duplicate template id found in TEMPLATES")


def generate_algebraic_proof(tier: Tier, rng: random.Random) -> Question:
    template = rng.choice(TEMPLATES)
    template.verify()

    definitions_line = " ".join(template.definitions)
    steps = [
        definitions_line,
        f"Write the given expression algebraically: {template.expression_line}.",
        f"Expand and simplify: {template.expression_line} = {template.expanded_line}.",
        f"Factorise/rearrange to expose the structure: {template.expanded_line} = {template.factored_line}.",
        template.conclusion,
    ]
    return Question(
        topic_id="algebraic_proof",
        tier=Tier.HIGHER,
        prompt=f"Prove algebraically that {template.claim}.",
        solution_steps=tuple(steps),
        final_answer=template.final_answer,
        dedup_key=f"proof:{template.id}",
    )


def generate_modelled_example_algebraic_proof(tier: Tier, rng: random.Random) -> ModelledExample:
    template = rng.choice(TEMPLATES)
    template.verify()

    definitions_line = " ".join(template.definitions)
    teaching_steps = [
        f"An algebraic proof question like this asks you to show that a claim is true for EVERY "
        f"integer n, not just check it for a couple of examples - trying n = 1, 2, 3 might make "
        "the claim look true, but it never proves it for all the infinitely many integers there "
        "are. The whole point of writing it algebraically is that the argument then works for "
        "every value of n at once.",
        f"The first job is always to define the numbers involved using n: {definitions_line} "
        "Using a single letter n to represent 'any integer' is what makes the argument general - "
        "everything that follows has to work no matter what whole number n turns out to be.",
        f"Now write down the exact expression the question is about: {template.expression_line}. "
        f"Expanding every bracket and collecting like terms simplifies this to "
        f"{template.expanded_line}.",
        f"The final step is to rearrange that simplified expression into a form that plainly "
        f"reveals the property being claimed: {template.expanded_line} = {template.factored_line}. "
        f"{template.conclusion}",
        "Notice that nowhere in this argument was a specific number substituted for n - every line "
        "holds for whichever integer n happens to be, which is exactly what makes it a complete "
        "proof rather than just a worked example.",
    ]
    worked_calculation = [
        template.expression_line,
        f"= {template.expanded_line}",
        f"= {template.factored_line}",
    ]
    return ModelledExample(
        topic_id="algebraic_proof",
        tier=Tier.HIGHER,
        prompt=f"Prove algebraically that {template.claim}.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=template.final_answer,
    )


TOPIC_ALGEBRAIC_PROOF = TopicDefinition(
    id="algebraic_proof",
    display_name="Algebraic Proof",
    description="Prove a general algebraic claim about integers (parity, multiples, consecutive-number properties).",
    generate=generate_algebraic_proof,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    question_count=len(TEMPLATES),
    generate_modelled_example=generate_modelled_example_algebraic_proof,
)
