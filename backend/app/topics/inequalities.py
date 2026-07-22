import random

import sympy as sp

from app.core.models import ModelledExample, Question, Tier
from app.topics.algebra_utils import X, fmt_linear, fmt_num
from app.topics.base import TopicDefinition

SECTION = "algebra"
GROUP = "Inequalities"

SYM_DISPLAY = {"<": "<", ">": ">", "<=": "≤", ">=": "≥"}
FLIP = {"<": ">", ">": "<", "<=": ">=", ">=": "<="}
REL_FUNCS = {"<": sp.Lt, ">": sp.Gt, "<=": sp.Le, ">=": sp.Ge}


def _fmt_ineq_lhs(coeff, const) -> str:
    """Render coeff*x + const, using an 'x/k' style for unit-fraction
    coefficients (e.g. coeff = 1/2 -> 'x/2') rather than '1/2 x'."""
    coeff = sp.Rational(coeff)
    const = sp.Rational(const)
    parts: list[str] = []
    if coeff != 0:
        if coeff == 1:
            parts.append("x")
        elif coeff == -1:
            parts.append("-x")
        elif coeff.q == 1:
            parts.append(f"{fmt_num(coeff)}x")
        elif coeff.p == 1:
            parts.append(f"x/{coeff.q}")
        elif coeff.p == -1:
            parts.append(f"-x/{coeff.q}")
        else:
            parts.append(f"{coeff.p}x/{coeff.q}")
    if const != 0:
        sign = "+" if const > 0 else "-"
        term = fmt_num(sp.Abs(const))
        if parts:
            parts.append(f"{sign} {term}")
        else:
            parts.append(f"-{term}" if const < 0 else term)
    if not parts:
        return "0"
    return " ".join(parts)


def _interval_for(symbol: str, bound) -> sp.Set:
    b = sp.Rational(bound)
    if symbol == "<":
        return sp.Interval.open(-sp.oo, b)
    if symbol == "<=":
        return sp.Interval(-sp.oo, b)
    if symbol == ">":
        return sp.Interval.open(b, sp.oo)
    if symbol == ">=":
        return sp.Interval(b, sp.oo)
    raise ValueError(f"Unknown symbol {symbol}")


def _verify_relational(expr_lhs, expr_rhs, symbol, final_symbol, bound) -> None:
    """Independent check: ask sympy's own inequality solver to solve the exact
    relation as originally posed, and confirm it agrees with the (final_symbol,
    bound) pair derived by hand-rolled algebra - a genuinely different code path
    than the manual collect/flip logic used to build the displayed steps."""
    rel = REL_FUNCS[symbol](expr_lhs, expr_rhs)
    solved = sp.solve_univariate_inequality(rel, X, relational=False)
    expected = _interval_for(final_symbol, bound)
    if solved != expected:
        raise ValueError(
            f"Inequality verification failed: sympy gave {solved}, expected {expected}"
        )


def _solve_inequality_with_steps(lhs_coeff, lhs_const, rhs_coeff, rhs_const, symbol):
    """Solve lhs_coeff*x + lhs_const SYMBOL rhs_coeff*x + rhs_const, recording
    each manual algebra step (mirrors algebra_utils.solve_linear_with_steps but
    threads an inequality symbol through, flipping it whenever the working
    divides/multiplies by a negative number). Returns (steps, final_symbol, bound)."""
    lhs_coeff = sp.Rational(lhs_coeff)
    lhs_const = sp.Rational(lhs_const)
    rhs_coeff = sp.Rational(rhs_coeff)
    rhs_const = sp.Rational(rhs_const)
    sym = symbol

    steps = [f"{_fmt_ineq_lhs(lhs_coeff, lhs_const)} {SYM_DISPLAY[sym]} {_fmt_ineq_lhs(rhs_coeff, rhs_const)}"]

    if rhs_coeff != 0:
        new_lhs_coeff = lhs_coeff - rhs_coeff
        if rhs_coeff > 0:
            steps.append(f"Subtract {fmt_num(rhs_coeff)}x from both sides:")
        else:
            steps.append(f"Add {fmt_num(sp.Abs(rhs_coeff))}x to both sides:")
        steps.append(f"{_fmt_ineq_lhs(new_lhs_coeff, lhs_const)} {SYM_DISPLAY[sym]} {fmt_num(rhs_const)}")
        lhs_coeff, rhs_coeff = new_lhs_coeff, sp.Integer(0)

    if lhs_coeff == 0:
        raise ValueError("Inequality has no unique solution (coefficient of x is 0)")

    if lhs_const != 0:
        new_rhs_const = rhs_const - lhs_const
        if lhs_const > 0:
            steps.append(f"Subtract {fmt_num(lhs_const)} from both sides:")
        else:
            steps.append(f"Add {fmt_num(sp.Abs(lhs_const))} to both sides:")
        steps.append(f"{_fmt_ineq_lhs(lhs_coeff, 0)} {SYM_DISPLAY[sym]} {fmt_num(new_rhs_const)}")
        lhs_const, rhs_const = sp.Integer(0), new_rhs_const

    if lhs_coeff != 1:
        bound = rhs_const / lhs_coeff
        if lhs_coeff < 0:
            sym = FLIP[sym]
            steps.append(
                f"Divide both sides by {fmt_num(lhs_coeff)} (dividing by a negative number reverses "
                "the inequality sign):"
            )
        elif lhs_coeff.q != 1:
            multiplier = 1 / lhs_coeff
            steps.append(f"Multiply both sides by {fmt_num(multiplier)}:")
        else:
            steps.append(f"Divide both sides by {fmt_num(lhs_coeff)}:")
        steps.append(f"x {SYM_DISPLAY[sym]} {fmt_num(bound)}")
    else:
        bound = rhs_const
        steps.append(f"x {SYM_DISPLAY[sym]} {fmt_num(bound)}")

    return steps, sym, bound


def _solve_single_relation(coeff, const, target, symbol, expr_on_left: bool):
    """Solve for x in coeff*x+const SYMBOL target (expr_on_left=True) or
    target SYMBOL coeff*x+const (expr_on_left=False). Returns (final_symbol,
    bound) meaning 'x final_symbol bound'. Independently verified via sympy's
    own inequality solver applied to the exact relation as originally posed."""
    c, k, t = sp.Rational(coeff), sp.Rational(const), sp.Rational(target)
    sym = symbol
    if not expr_on_left:
        sym = FLIP[sym]
    remaining = t - k
    if c < 0:
        sym = FLIP[sym]
    bound = remaining / c

    if expr_on_left:
        _verify_relational(c * X + k, t, symbol, sym, bound)
    else:
        _verify_relational(t, c * X + k, symbol, sym, bound)

    return sym, bound


def _split_bounds(sym1, bound1, sym2, bound2):
    """Given two atomic 'x SYM bound' relations, identify which is the lower
    bound (x >/>= bound) and which is the upper bound (x </<= bound) - needed
    because a negative coefficient can make either relation come out either
    way, regardless of how the original compound inequality was written."""
    pairs = [(sym1, bound1), (sym2, bound2)]
    lowers = [p for p in pairs if p[0] in (">", ">=")]
    uppers = [p for p in pairs if p[0] in ("<", "<=")]
    if len(lowers) != 1 or len(uppers) != 1:
        raise ValueError("Could not split compound inequality into one lower and one upper bound")
    return lowers[0], uppers[0]


def _direct_check(coeff, const, target, symbol, expr_on_left, xi) -> bool:
    """Plug the integer xi directly into the *original* (un-rearranged)
    relation and check it holds - a genuinely different check than solving
    algebraically for a bound and comparing xi against that bound."""
    val = coeff * xi + const
    lhs, rhs = (val, target) if expr_on_left else (target, val)
    if symbol == "<":
        return lhs < rhs
    if symbol == "<=":
        return lhs <= rhs
    if symbol == ">":
        return lhs > rhs
    if symbol == ">=":
        return lhs >= rhs
    raise ValueError(f"Unknown symbol {symbol}")


def _combine_and_list_integers(sym1, bound1, sym2, bound2, search_radius=40):
    def holds(xi, sym, bound):
        xi = sp.Integer(xi)
        if sym == "<":
            return xi < bound
        if sym == "<=":
            return xi <= bound
        if sym == ">":
            return xi > bound
        if sym == ">=":
            return xi >= bound
        raise ValueError(f"Unknown symbol {sym}")

    return [
        xi
        for xi in range(-search_radius, search_radius + 1)
        if holds(xi, sym1, bound1) and holds(xi, sym2, bound2)
    ]


def _fmt_quadratic(a, b, c) -> str:
    parts: list[str] = []
    if a != 0:
        if a == 1:
            parts.append("x^2")
        elif a == -1:
            parts.append("-x^2")
        else:
            parts.append(f"{a}x^2")
    if b != 0:
        term = "x" if abs(b) == 1 else f"{abs(b)}x"
        if parts:
            parts.append(f"{'+' if b > 0 else '-'} {term}")
        else:
            parts.append(f"-{term}" if b < 0 else term)
    if c != 0 or not parts:
        if parts:
            parts.append(f"{'+' if c > 0 else '-'} {abs(c)}")
        else:
            parts.append(str(c))
    return " ".join(parts)


def _fmt_root_factor(r) -> str:
    if r == 0:
        return "x"
    return f"x - {r}" if r > 0 else f"x + {abs(r)}"


def generate_solving_inequalities_foundation(tier: Tier, rng: random.Random) -> Question:
    symbol = rng.choice(["<", ">", "<=", ">="])
    if rng.random() < 0.3:
        lhs_coeff = sp.Rational(1, rng.choice([2, 3, 4]))
    else:
        lhs_coeff = sp.Integer(rng.randint(1, 6))
    lhs_const = rng.randint(-10, 10)
    rhs_const = rng.randint(-12, 12)

    steps, final_symbol, bound = _solve_inequality_with_steps(lhs_coeff, lhs_const, 0, rhs_const, symbol)
    if final_symbol != symbol:
        raise ValueError("solving_inequalities_foundation: coefficient should stay positive, no flip expected")
    _verify_relational(lhs_coeff * X + lhs_const, rhs_const, symbol, final_symbol, bound)

    prompt = f"Solve the inequality: {_fmt_ineq_lhs(lhs_coeff, lhs_const)} {SYM_DISPLAY[symbol]} {rhs_const}"
    final_answer = f"x {SYM_DISPLAY[final_symbol]} {fmt_num(bound)}"
    return Question(
        topic_id="solving_inequalities_foundation",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=final_answer,
        dedup_key=f"solve_ineq_f:{lhs_coeff}:{lhs_const}:{rhs_const}:{symbol}",
    )


def generate_solving_inequalities_higher(tier: Tier, rng: random.Random) -> Question:
    symbol = rng.choice(["<", ">", "<=", ">="])
    shape = rng.choice(["both_sides", "bracket"])

    if shape == "both_sides":
        a = rng.randint(2, 6)
        c = rng.randint(a + 1, a + 6)
        b = rng.randint(-10, 10)
        d = rng.randint(-10, 10)
        prompt = f"Solve the inequality: {_fmt_ineq_lhs(a, b)} {SYM_DISPLAY[symbol]} {_fmt_ineq_lhs(c, d)}"
        steps, final_symbol, bound = _solve_inequality_with_steps(a, b, c, d, symbol)
        _verify_relational(a * X + b, c * X + d, symbol, final_symbol, bound)
        dedup_key = f"solve_ineq_h_both:{a}:{b}:{c}:{d}:{symbol}"
    else:
        k = -rng.randint(2, 6)
        m = rng.randint(-9, 9)
        rhs_val = rng.randint(-15, 15)
        expanded_const = k * m
        bracket_inner = fmt_linear(1, m)

        residual = sp.expand(k * (X + m) - (k * X + expanded_const))
        if residual != 0:
            raise ValueError("solving_inequalities_higher: bracket expansion verification failed")

        expand_line = f"{k}({bracket_inner}) {SYM_DISPLAY[symbol]} {rhs_val}"
        expanded_line = f"{_fmt_ineq_lhs(k, expanded_const)} {SYM_DISPLAY[symbol]} {rhs_val}"
        rest_steps, final_symbol, bound = _solve_inequality_with_steps(k, expanded_const, 0, rhs_val, symbol)
        steps = [f"Expand the bracket: {expand_line}", expanded_line] + rest_steps[1:]
        _verify_relational(k * (X + m), rhs_val, symbol, final_symbol, bound)
        prompt = f"Solve the inequality: {k}({bracket_inner}) {SYM_DISPLAY[symbol]} {rhs_val}"
        dedup_key = f"solve_ineq_h_bracket:{k}:{m}:{rhs_val}:{symbol}"

    final_answer = f"x {SYM_DISPLAY[final_symbol]} {fmt_num(bound)}"
    return Question(
        topic_id="solving_inequalities_higher",
        tier=Tier.HIGHER,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=final_answer,
        dedup_key=dedup_key,
    )


def generate_satisfying_inequalities_foundation(tier: Tier, rng: random.Random) -> Question:
    for _ in range(50):
        a = rng.randint(1, 4)
        b = rng.randint(-8, 8)
        lo = rng.randint(-15, 5)
        hi = lo + rng.randint(6, 24)
        lo_sym = rng.choice(["<", "<="])
        hi_sym = rng.choice(["<", "<="])

        sym1, bound1 = _solve_single_relation(a, b, lo, lo_sym, expr_on_left=False)
        sym2, bound2 = _solve_single_relation(a, b, hi, hi_sym, expr_on_left=True)
        (lower_sym, lower_bound), (upper_sym, upper_bound) = _split_bounds(sym1, bound1, sym2, bound2)

        candidates = [
            xi
            for xi in range(-40, 41)
            if _direct_check(a, b, lo, lo_sym, False, xi) and _direct_check(a, b, hi, hi_sym, True, xi)
        ]
        via_bounds = _combine_and_list_integers(sym1, bound1, sym2, bound2)
        if candidates != via_bounds:
            raise ValueError("satisfying_inequalities_foundation: algebraic and brute-force lists disagree")
        if 2 <= len(candidates) <= 15:
            break
    else:
        raise ValueError("Could not generate a valid satisfying_inequalities_foundation question")

    left_display_sym = FLIP[lower_sym]
    range_str = f"{fmt_num(lower_bound)} {SYM_DISPLAY[left_display_sym]} x {SYM_DISPLAY[upper_sym]} {fmt_num(upper_bound)}"

    prompt = (
        f"Solve the inequality {lo} {SYM_DISPLAY[lo_sym]} {_fmt_ineq_lhs(a, b)} {SYM_DISPLAY[hi_sym]} {hi}, "
        "then list the integer values of x that satisfy it."
    )
    steps = [f"{lo} {SYM_DISPLAY[lo_sym]} {_fmt_ineq_lhs(a, b)} {SYM_DISPLAY[hi_sym]} {hi}"]
    if b != 0:
        if b > 0:
            steps.append(f"Subtract {fmt_num(b)} from all three parts:")
        else:
            steps.append(f"Add {fmt_num(sp.Abs(b))} to all three parts:")
        steps.append(
            f"{fmt_num(lo - b)} {SYM_DISPLAY[lo_sym]} {_fmt_ineq_lhs(a, 0)} {SYM_DISPLAY[hi_sym]} {fmt_num(hi - b)}"
        )
    if a != 1:
        steps.append(f"Divide all three parts by {a}:")
    if b != 0 or a != 1:
        steps.append(range_str)
    candidates_str = ", ".join(str(v) for v in candidates)
    steps.append(f"The integers satisfying this are: {candidates_str}")

    return Question(
        topic_id="satisfying_inequalities_foundation",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=candidates_str,
        dedup_key=f"satisfy_ineq_f:{a}:{b}:{lo}:{lo_sym}:{hi}:{hi_sym}",
    )


def generate_satisfying_inequalities_higher(tier: Tier, rng: random.Random) -> Question:
    shape = rng.choice(["negative_compound", "separate"])

    if shape == "negative_compound":
        for _ in range(50):
            a = -rng.randint(1, 4)
            b = rng.randint(-8, 8)
            lo = rng.randint(-15, 5)
            hi = lo + rng.randint(6, 24)
            lo_sym = rng.choice(["<", "<="])
            hi_sym = rng.choice(["<", "<="])

            sym1, bound1 = _solve_single_relation(a, b, lo, lo_sym, expr_on_left=False)
            sym2, bound2 = _solve_single_relation(a, b, hi, hi_sym, expr_on_left=True)
            (lower_sym, lower_bound), (upper_sym, upper_bound) = _split_bounds(sym1, bound1, sym2, bound2)

            candidates = [
                xi
                for xi in range(-40, 41)
                if _direct_check(a, b, lo, lo_sym, False, xi) and _direct_check(a, b, hi, hi_sym, True, xi)
            ]
            via_bounds = _combine_and_list_integers(sym1, bound1, sym2, bound2)
            if candidates != via_bounds:
                raise ValueError("satisfying_inequalities_higher (negative compound): lists disagree")
            if 2 <= len(candidates) <= 15:
                break
        else:
            raise ValueError("Could not generate a valid negative-compound satisfying_inequalities_higher question")

        left_display_sym = FLIP[lower_sym]
        range_str = (
            f"{fmt_num(lower_bound)} {SYM_DISPLAY[left_display_sym]} x {SYM_DISPLAY[upper_sym]} {fmt_num(upper_bound)}"
        )

        prompt = (
            f"Solve the inequality {lo} {SYM_DISPLAY[lo_sym]} {_fmt_ineq_lhs(a, b)} {SYM_DISPLAY[hi_sym]} {hi}, "
            "then list the integer values of x that satisfy it."
        )
        steps = [f"{lo} {SYM_DISPLAY[lo_sym]} {_fmt_ineq_lhs(a, b)} {SYM_DISPLAY[hi_sym]} {hi}"]
        if b != 0:
            if b > 0:
                steps.append(f"Subtract {fmt_num(b)} from all three parts:")
            else:
                steps.append(f"Add {fmt_num(sp.Abs(b))} to all three parts:")
            steps.append(
                f"{fmt_num(lo - b)} {SYM_DISPLAY[lo_sym]} {_fmt_ineq_lhs(a, 0)} {SYM_DISPLAY[hi_sym]} {fmt_num(hi - b)}"
            )
        steps.append(
            f"Divide all three parts by {a} - since this is negative, every inequality sign reverses, "
            "and the low/high sides swap around:"
        )
        steps.append(range_str)
        candidates_str = ", ".join(str(v) for v in candidates)
        steps.append(f"The integers satisfying this are: {candidates_str}")

        return Question(
            topic_id="satisfying_inequalities_higher",
            tier=Tier.HIGHER,
            prompt=prompt,
            solution_steps=tuple(steps),
            final_answer=candidates_str,
            dedup_key=f"satisfy_ineq_h_neg:{a}:{b}:{lo}:{lo_sym}:{hi}:{hi_sym}",
        )
    else:
        for _ in range(50):
            sym_1 = rng.choice([">", ">="])
            sym_2 = rng.choice(["<", "<="])
            p = rng.randint(1, 5)
            q = rng.randint(-10, 10)
            t1 = rng.randint(-15, 15)
            r = rng.randint(1, 5)
            s = rng.randint(-10, 10)
            t2 = rng.randint(-15, 15)

            sym1, bound1 = _solve_single_relation(p, q, t1, sym_1, expr_on_left=True)
            sym2, bound2 = _solve_single_relation(r, s, t2, sym_2, expr_on_left=True)

            candidates = [
                xi
                for xi in range(-40, 41)
                if _direct_check(p, q, t1, sym_1, True, xi) and _direct_check(r, s, t2, sym_2, True, xi)
            ]
            via_bounds = _combine_and_list_integers(sym1, bound1, sym2, bound2)
            if candidates != via_bounds:
                raise ValueError("satisfying_inequalities_higher (separate): lists disagree")
            if 2 <= len(candidates) <= 15:
                break
        else:
            raise ValueError("Could not generate a valid separate-inequalities satisfying_inequalities_higher question")

        first_steps, sym1b, bound1b = _solve_inequality_with_steps(p, q, 0, t1, sym_1)
        if sym1b != sym1 or bound1b != bound1:
            raise ValueError("satisfying_inequalities_higher: step-derivation disagrees with verified solve (1st)")
        second_steps, sym2b, bound2b = _solve_inequality_with_steps(r, s, 0, t2, sym_2)
        if sym2b != sym2 or bound2b != bound2:
            raise ValueError("satisfying_inequalities_higher: step-derivation disagrees with verified solve (2nd)")

        combined_str = f"{fmt_num(bound1)} {SYM_DISPLAY[FLIP[sym1]]} x {SYM_DISPLAY[sym2]} {fmt_num(bound2)}"
        candidates_str = ", ".join(str(v) for v in candidates)

        prompt = (
            f"x satisfies both {_fmt_ineq_lhs(p, q)} {SYM_DISPLAY[sym_1]} {t1} and "
            f"{_fmt_ineq_lhs(r, s)} {SYM_DISPLAY[sym_2]} {t2}. List the integer values of x that satisfy both."
        )
        steps = ["Solve the first inequality:"]
        steps.extend(first_steps)
        steps.append("Solve the second inequality:")
        steps.extend(second_steps)
        steps.append(f"Combine both results into a single range: {combined_str}")
        steps.append(f"The integers satisfying both inequalities are: {candidates_str}")

        return Question(
            topic_id="satisfying_inequalities_higher",
            tier=Tier.HIGHER,
            prompt=prompt,
            solution_steps=tuple(steps),
            final_answer=candidates_str,
            dedup_key=f"satisfy_ineq_h_sep:{p}:{q}:{sym_1}:{t1}:{r}:{s}:{sym_2}:{t2}",
        )


def generate_quadratic_inequalities(tier: Tier, rng: random.Random) -> Question:
    r1 = rng.randint(-9, 9)
    r2 = rng.randint(-9, 9)
    while r2 == r1:
        r2 = rng.randint(-9, 9)
    lo, hi = sorted((r1, r2))
    leading = rng.choice([1, -1])
    symbol = rng.choice(["<", ">", "<=", ">="])

    expanded = sp.expand(leading * (X - r1) * (X - r2))
    poly = sp.Poly(expanded, X)
    coeffs = poly.all_coeffs()
    coeffs = [0] * (3 - len(coeffs)) + coeffs
    qa, qb, qc = (int(v) for v in coeffs)

    residual = sp.expand(leading * (X - r1) * (X - r2) - (qa * X**2 + qb * X + qc))
    if residual != 0:
        raise ValueError("quadratic_inequalities verification failed (symbolic expansion)")

    strict = symbol in ("<", ">")
    between = (leading == 1 and symbol in ("<", "<=")) or (leading == -1 and symbol in (">", ">="))

    if between:
        claimed = sp.Interval(lo, hi, left_open=strict, right_open=strict)
    else:
        claimed = sp.Union(
            sp.Interval(-sp.oo, lo, left_open=True, right_open=strict),
            sp.Interval(hi, sp.oo, left_open=strict, right_open=True),
        )

    quad_expr = qa * X**2 + qb * X + qc
    rel = REL_FUNCS[symbol](quad_expr, 0)
    solved = sp.solve_univariate_inequality(rel, X, relational=False)
    if not (solved - claimed).is_empty or not (claimed - solved).is_empty:
        raise ValueError("quadratic_inequalities verification failed: sympy solution disagrees with claimed answer")

    sample_points = {lo - 2, lo, hi, hi + 2}
    if hi - lo >= 2:
        sample_points.add((lo + hi) // 2)
    for p in sample_points:
        val = qa * p**2 + qb * p + qc
        direct_holds = {"<": val < 0, ">": val > 0, "<=": val <= 0, ">=": val >= 0}[symbol]
        claimed_holds = bool(claimed.contains(p))
        if direct_holds != claimed_holds:
            raise ValueError("quadratic_inequalities verification failed: point-sample mismatch")

    if between:
        bound_sym = "<=" if not strict else "<"
        final_answer = f"{lo} {SYM_DISPLAY[bound_sym]} x {SYM_DISPLAY[bound_sym]} {hi}"
    else:
        left_sym = "<=" if not strict else "<"
        right_sym = ">=" if not strict else ">"
        final_answer = f"x {SYM_DISPLAY[left_sym]} {lo} or x {SYM_DISPLAY[right_sym]} {hi}"

    factor_str = (
        f"-({_fmt_root_factor(r1)})({_fmt_root_factor(r2)})"
        if leading == -1
        else f"({_fmt_root_factor(r1)})({_fmt_root_factor(r2)})"
    )
    parabola_desc = "U-shaped" if leading == 1 else "upside-down U-shaped"
    steps = [
        f"Factorise: {_fmt_quadratic(qa, qb, qc)} = {factor_str}",
        f"The critical values are x = {lo} and x = {hi}.",
        (
            f"The coefficient of x^2 is {'positive' if leading == 1 else 'negative'}, so the graph is a "
            f"{parabola_desc} parabola, and {SYM_DISPLAY[symbol]} 0 is satisfied "
            f"{'between' if between else 'outside'} the two roots."
        ),
        f"Answer: {final_answer}",
    ]

    return Question(
        topic_id="quadratic_inequalities",
        tier=Tier.HIGHER,
        prompt=f"Solve the inequality: {_fmt_quadratic(qa, qb, qc)} {SYM_DISPLAY[symbol]} 0",
        solution_steps=tuple(steps),
        final_answer=final_answer,
        dedup_key=f"quad_ineq:{qa}:{qb}:{qc}:{symbol}",
    )


def generate_modelled_example_solving_inequalities_foundation(
    tier: Tier, rng: random.Random
) -> ModelledExample:
    symbol = rng.choice(["<", ">", "<=", ">="])
    if rng.random() < 0.3:
        lhs_coeff = sp.Rational(1, rng.choice([2, 3, 4]))
    else:
        lhs_coeff = sp.Integer(rng.randint(1, 6))
    lhs_const = rng.randint(-10, 10)
    rhs_const = rng.randint(-12, 12)

    steps, final_symbol, bound = _solve_inequality_with_steps(lhs_coeff, lhs_const, 0, rhs_const, symbol)
    if final_symbol != symbol:
        raise ValueError(
            "modelled example solving_inequalities_foundation: coefficient should stay positive"
        )
    _verify_relational(lhs_coeff * X + lhs_const, rhs_const, symbol, final_symbol, bound)

    prompt = f"Solve the inequality: {_fmt_ineq_lhs(lhs_coeff, lhs_const)} {SYM_DISPLAY[symbol]} {rhs_const}"
    final_answer = f"x {SYM_DISPLAY[final_symbol]} {fmt_num(bound)}"

    teaching_steps = [
        "An inequality like this is solved with exactly the same moves as an ordinary equation - undo "
        "whatever has been done to x, one step at a time, doing the same thing to both sides. The only "
        "difference is that the answer is a whole range of values, not a single number.",
        f"Here x has been multiplied by {fmt_num(lhs_coeff)}"
        + (f" and then {'added to' if lhs_const > 0 else 'had subtracted'} {fmt_num(sp.Abs(lhs_const))}"
           if lhs_const != 0 else "")
        + f". Undo these in reverse order: first deal with the {fmt_num(lhs_const)} term, then the "
        f"{fmt_num(lhs_coeff)} coefficient.",
        "Because the coefficient of x stays positive the whole way through, the inequality symbol never "
        "needs to change direction here - that's what makes this a Foundation-level question rather than "
        "a Higher one.",
        f"Working through those two steps gives the final answer, {final_answer}.",
    ]
    worked_calculation = list(steps)

    return ModelledExample(
        topic_id="solving_inequalities_foundation",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=final_answer,
    )


def generate_modelled_example_solving_inequalities_higher(
    tier: Tier, rng: random.Random
) -> ModelledExample:
    symbol = rng.choice(["<", ">", "<=", ">="])
    shape = rng.choice(["both_sides", "bracket"])

    if shape == "both_sides":
        a = rng.randint(2, 6)
        c = rng.randint(a + 1, a + 6)
        b = rng.randint(-10, 10)
        d = rng.randint(-10, 10)
        prompt = f"Solve the inequality: {_fmt_ineq_lhs(a, b)} {SYM_DISPLAY[symbol]} {_fmt_ineq_lhs(c, d)}"
        steps, final_symbol, bound = _solve_inequality_with_steps(a, b, c, d, symbol)
        _verify_relational(a * X + b, c * X + d, symbol, final_symbol, bound)

        teaching_steps = [
            f"With x-terms on both sides ({_fmt_ineq_lhs(a, b)} and {_fmt_ineq_lhs(c, d)}), the first job "
            f"is to collect all the x-terms onto one side. Since {c} is bigger than {a}, moving the "
            f"{a}x term across (subtracting it from both sides) leaves a negative coefficient of x behind "
            f"- this is exactly the situation where a sign flip becomes necessary.",
            "Collect the x-terms on one side and the numbers on the other, exactly as you would for an "
            "equation.",
            "Now the coefficient of x is negative. To isolate x, both sides must be divided by that "
            "negative number - and dividing (or multiplying) an inequality by a negative number always "
            "reverses the direction of the inequality sign. Forgetting this is the single most common "
            "mistake with inequalities.",
            f"Dividing through and flipping the sign gives the final answer, x {SYM_DISPLAY[final_symbol]} "
            f"{fmt_num(bound)}.",
        ]
        worked_calculation = list(steps)
    else:
        k = -rng.randint(2, 6)
        m = rng.randint(-9, 9)
        rhs_val = rng.randint(-15, 15)
        expanded_const = k * m
        bracket_inner = fmt_linear(1, m)

        residual = sp.expand(k * (X + m) - (k * X + expanded_const))
        if residual != 0:
            raise ValueError("modelled example solving_inequalities_higher: bracket expansion failed")

        expand_line = f"{k}({bracket_inner}) {SYM_DISPLAY[symbol]} {rhs_val}"
        expanded_line = f"{_fmt_ineq_lhs(k, expanded_const)} {SYM_DISPLAY[symbol]} {rhs_val}"
        rest_steps, final_symbol, bound = _solve_inequality_with_steps(k, expanded_const, 0, rhs_val, symbol)
        steps = [f"Expand the bracket: {expand_line}", expanded_line] + rest_steps[1:]
        _verify_relational(k * (X + m), rhs_val, symbol, final_symbol, bound)
        prompt = f"Solve the inequality: {k}({bracket_inner}) {SYM_DISPLAY[symbol]} {rhs_val}"

        teaching_steps = [
            f"A negative number multiplied onto a bracket, like {k}({bracket_inner}), needs expanding "
            "first, exactly as with an equation - multiply every term inside by the number outside, "
            "keeping careful track of the signs.",
            f"Expanding gives {_fmt_ineq_lhs(k, expanded_const)}, which already has a negative coefficient "
            f"of x ({k}) - no need to collect terms from another side here, since the negative coefficient "
            "was there from the start.",
            "To finish, divide both sides by that negative coefficient. Dividing an inequality by a "
            "negative number always reverses its direction - so whatever symbol we started with must be "
            "flipped at this step.",
            f"That gives the final answer, x {SYM_DISPLAY[final_symbol]} {fmt_num(bound)}.",
        ]
        worked_calculation = list(steps)

    final_answer = f"x {SYM_DISPLAY[final_symbol]} {fmt_num(bound)}"
    return ModelledExample(
        topic_id="solving_inequalities_higher",
        tier=Tier.HIGHER,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=final_answer,
    )


def generate_modelled_example_satisfying_inequalities_foundation(
    tier: Tier, rng: random.Random
) -> ModelledExample:
    for _ in range(50):
        a = rng.randint(1, 4)
        b = rng.randint(-8, 8)
        lo = rng.randint(-15, 5)
        hi = lo + rng.randint(6, 24)
        lo_sym = rng.choice(["<", "<="])
        hi_sym = rng.choice(["<", "<="])

        sym1, bound1 = _solve_single_relation(a, b, lo, lo_sym, expr_on_left=False)
        sym2, bound2 = _solve_single_relation(a, b, hi, hi_sym, expr_on_left=True)
        (lower_sym, lower_bound), (upper_sym, upper_bound) = _split_bounds(sym1, bound1, sym2, bound2)

        candidates = [
            xi
            for xi in range(-40, 41)
            if _direct_check(a, b, lo, lo_sym, False, xi) and _direct_check(a, b, hi, hi_sym, True, xi)
        ]
        via_bounds = _combine_and_list_integers(sym1, bound1, sym2, bound2)
        if candidates != via_bounds:
            raise ValueError("modelled example satisfying_inequalities_foundation: lists disagree")
        if 2 <= len(candidates) <= 15:
            break
    else:
        raise ValueError("Could not generate a valid modelled example for satisfying_inequalities_foundation")

    left_display_sym = FLIP[lower_sym]
    range_str = f"{fmt_num(lower_bound)} {SYM_DISPLAY[left_display_sym]} x {SYM_DISPLAY[upper_sym]} {fmt_num(upper_bound)}"
    candidates_str = ", ".join(str(v) for v in candidates)

    prompt = (
        f"Solve the inequality {lo} {SYM_DISPLAY[lo_sym]} {_fmt_ineq_lhs(a, b)} {SYM_DISPLAY[hi_sym]} {hi}, "
        "then list the integer values of x that satisfy it."
    )
    worked_calculation = [f"{lo} {SYM_DISPLAY[lo_sym]} {_fmt_ineq_lhs(a, b)} {SYM_DISPLAY[hi_sym]} {hi}"]
    if b != 0:
        worked_calculation.append(
            f"{fmt_num(lo - b)} {SYM_DISPLAY[lo_sym]} {_fmt_ineq_lhs(a, 0)} {SYM_DISPLAY[hi_sym]} {fmt_num(hi - b)}"
        )
    worked_calculation.append(range_str)
    worked_calculation.append(candidates_str)

    teaching_steps = [
        f"This is a compound inequality: {lo} {SYM_DISPLAY[lo_sym]} {_fmt_ineq_lhs(a, b)} "
        f"{SYM_DISPLAY[hi_sym]} {hi} means the middle expression is trapped between two bounds at once. "
        "The trick is to do the same operation to all three parts together, not just two of them.",
        (f"Since {fmt_num(b)} is being added to (or subtracted from) x in the middle, undo that first by "
         f"subtracting/adding it to all three parts." if b != 0 else
         "There's no constant term to undo here, so we move straight to isolating x."),
        (f"Then divide all three parts by {a} to leave x on its own in the middle - since {a} is "
         "positive, none of the inequality signs need to change direction." if a != 1 else
         "Since x already has a coefficient of 1, that's already the range for x."),
        f"This gives the range {range_str}, and listing every whole number inside that range gives the "
        f"final answer: {candidates_str}.",
    ]

    return ModelledExample(
        topic_id="satisfying_inequalities_foundation",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=candidates_str,
    )


def generate_modelled_example_satisfying_inequalities_higher(
    tier: Tier, rng: random.Random
) -> ModelledExample:
    shape = rng.choice(["negative_compound", "separate"])

    if shape == "negative_compound":
        for _ in range(50):
            a = -rng.randint(1, 4)
            b = rng.randint(-8, 8)
            lo = rng.randint(-15, 5)
            hi = lo + rng.randint(6, 24)
            lo_sym = rng.choice(["<", "<="])
            hi_sym = rng.choice(["<", "<="])

            sym1, bound1 = _solve_single_relation(a, b, lo, lo_sym, expr_on_left=False)
            sym2, bound2 = _solve_single_relation(a, b, hi, hi_sym, expr_on_left=True)
            (lower_sym, lower_bound), (upper_sym, upper_bound) = _split_bounds(sym1, bound1, sym2, bound2)

            candidates = [
                xi
                for xi in range(-40, 41)
                if _direct_check(a, b, lo, lo_sym, False, xi) and _direct_check(a, b, hi, hi_sym, True, xi)
            ]
            via_bounds = _combine_and_list_integers(sym1, bound1, sym2, bound2)
            if candidates != via_bounds:
                raise ValueError("modelled example satisfying_inequalities_higher (negative compound): lists disagree")
            if 2 <= len(candidates) <= 15:
                break
        else:
            raise ValueError(
                "Could not generate a valid modelled example (negative compound) for satisfying_inequalities_higher"
            )

        left_display_sym = FLIP[lower_sym]
        range_str = (
            f"{fmt_num(lower_bound)} {SYM_DISPLAY[left_display_sym]} x {SYM_DISPLAY[upper_sym]} {fmt_num(upper_bound)}"
        )
        candidates_str = ", ".join(str(v) for v in candidates)

        prompt = (
            f"Solve the inequality {lo} {SYM_DISPLAY[lo_sym]} {_fmt_ineq_lhs(a, b)} {SYM_DISPLAY[hi_sym]} {hi}, "
            "then list the integer values of x that satisfy it."
        )
        worked_calculation = [f"{lo} {SYM_DISPLAY[lo_sym]} {_fmt_ineq_lhs(a, b)} {SYM_DISPLAY[hi_sym]} {hi}"]
        if b != 0:
            worked_calculation.append(
                f"{fmt_num(lo - b)} {SYM_DISPLAY[lo_sym]} {_fmt_ineq_lhs(a, 0)} {SYM_DISPLAY[hi_sym]} {fmt_num(hi - b)}"
            )
        worked_calculation.append(range_str)
        worked_calculation.append(candidates_str)

        teaching_steps = [
            f"This compound inequality has a negative coefficient of x ({a}), which makes the final "
            "division step trickier than usual - watch closely.",
            "First undo the constant term attached to x, dividing/subtracting it from all three parts of "
            "the inequality together.",
            f"Now divide all three parts by {a}. Because this is negative, every inequality sign in the "
            "statement reverses direction, and (just as importantly) the lower and upper bounds swap "
            "places - what was the smaller number becomes the larger one, and vice versa.",
            f"Once the signs are flipped and the bounds reordered correctly, this settles down to "
            f"{range_str}, and the integers inside that range are: {candidates_str}.",
        ]

        return ModelledExample(
            topic_id="satisfying_inequalities_higher",
            tier=Tier.HIGHER,
            prompt=prompt,
            worked_calculation=tuple(worked_calculation),
            teaching_steps=tuple(teaching_steps),
            final_answer=candidates_str,
        )
    else:
        for _ in range(50):
            sym_1 = rng.choice([">", ">="])
            sym_2 = rng.choice(["<", "<="])
            p = rng.randint(1, 5)
            q = rng.randint(-10, 10)
            t1 = rng.randint(-15, 15)
            r = rng.randint(1, 5)
            s = rng.randint(-10, 10)
            t2 = rng.randint(-15, 15)

            sym1, bound1 = _solve_single_relation(p, q, t1, sym_1, expr_on_left=True)
            sym2, bound2 = _solve_single_relation(r, s, t2, sym_2, expr_on_left=True)

            candidates = [
                xi
                for xi in range(-40, 41)
                if _direct_check(p, q, t1, sym_1, True, xi) and _direct_check(r, s, t2, sym_2, True, xi)
            ]
            via_bounds = _combine_and_list_integers(sym1, bound1, sym2, bound2)
            if candidates != via_bounds:
                raise ValueError("modelled example satisfying_inequalities_higher (separate): lists disagree")
            if 2 <= len(candidates) <= 15:
                break
        else:
            raise ValueError(
                "Could not generate a valid modelled example (separate) for satisfying_inequalities_higher"
            )

        first_steps, sym1b, bound1b = _solve_inequality_with_steps(p, q, 0, t1, sym_1)
        if sym1b != sym1 or bound1b != bound1:
            raise ValueError("modelled example satisfying_inequalities_higher: derivation mismatch (1st)")
        second_steps, sym2b, bound2b = _solve_inequality_with_steps(r, s, 0, t2, sym_2)
        if sym2b != sym2 or bound2b != bound2:
            raise ValueError("modelled example satisfying_inequalities_higher: derivation mismatch (2nd)")

        combined_str = f"{fmt_num(bound1)} {SYM_DISPLAY[FLIP[sym1]]} x {SYM_DISPLAY[sym2]} {fmt_num(bound2)}"
        candidates_str = ", ".join(str(v) for v in candidates)

        prompt = (
            f"x satisfies both {_fmt_ineq_lhs(p, q)} {SYM_DISPLAY[sym_1]} {t1} and "
            f"{_fmt_ineq_lhs(r, s)} {SYM_DISPLAY[sym_2]} {t2}. List the integer values of x that satisfy both."
        )
        worked_calculation = list(first_steps) + list(second_steps) + [combined_str, candidates_str]

        teaching_steps = [
            "When a problem gives two separate inequalities that x must satisfy at the same time, solve "
            "each one on its own first, exactly like the single-inequality questions seen earlier.",
            f"Solving the first inequality gives x {SYM_DISPLAY[sym1]} {fmt_num(bound1)}, and solving the "
            f"second gives x {SYM_DISPLAY[sym2]} {fmt_num(bound2)}.",
            "Now combine the two results into a single range - x must be above the first bound AND below "
            "the second, so write them either side of x in one statement.",
            f"That combined range is {combined_str}, and the whole numbers inside it are: {candidates_str}.",
        ]

        return ModelledExample(
            topic_id="satisfying_inequalities_higher",
            tier=Tier.HIGHER,
            prompt=prompt,
            worked_calculation=tuple(worked_calculation),
            teaching_steps=tuple(teaching_steps),
            final_answer=candidates_str,
        )


def generate_modelled_example_quadratic_inequalities(tier: Tier, rng: random.Random) -> ModelledExample:
    r1 = rng.randint(-9, 9)
    r2 = rng.randint(-9, 9)
    while r2 == r1:
        r2 = rng.randint(-9, 9)
    lo, hi = sorted((r1, r2))
    leading = rng.choice([1, -1])
    symbol = rng.choice(["<", ">", "<=", ">="])

    expanded = sp.expand(leading * (X - r1) * (X - r2))
    poly = sp.Poly(expanded, X)
    coeffs = poly.all_coeffs()
    coeffs = [0] * (3 - len(coeffs)) + coeffs
    qa, qb, qc = (int(v) for v in coeffs)

    residual = sp.expand(leading * (X - r1) * (X - r2) - (qa * X**2 + qb * X + qc))
    if residual != 0:
        raise ValueError("modelled example quadratic_inequalities verification failed (symbolic expansion)")

    strict = symbol in ("<", ">")
    between = (leading == 1 and symbol in ("<", "<=")) or (leading == -1 and symbol in (">", ">="))

    if between:
        claimed = sp.Interval(lo, hi, left_open=strict, right_open=strict)
    else:
        claimed = sp.Union(
            sp.Interval(-sp.oo, lo, left_open=True, right_open=strict),
            sp.Interval(hi, sp.oo, left_open=strict, right_open=True),
        )

    quad_expr = qa * X**2 + qb * X + qc
    rel = REL_FUNCS[symbol](quad_expr, 0)
    solved = sp.solve_univariate_inequality(rel, X, relational=False)
    if not (solved - claimed).is_empty or not (claimed - solved).is_empty:
        raise ValueError(
            "modelled example quadratic_inequalities verification failed: sympy disagrees with claimed answer"
        )

    sample_points = {lo - 2, lo, hi, hi + 2}
    if hi - lo >= 2:
        sample_points.add((lo + hi) // 2)
    for p in sample_points:
        val = qa * p**2 + qb * p + qc
        direct_holds = {"<": val < 0, ">": val > 0, "<=": val <= 0, ">=": val >= 0}[symbol]
        claimed_holds = bool(claimed.contains(p))
        if direct_holds != claimed_holds:
            raise ValueError("modelled example quadratic_inequalities verification failed: point-sample mismatch")

    if between:
        bound_sym = "<=" if not strict else "<"
        final_answer = f"{lo} {SYM_DISPLAY[bound_sym]} x {SYM_DISPLAY[bound_sym]} {hi}"
    else:
        left_sym = "<=" if not strict else "<"
        right_sym = ">=" if not strict else ">"
        final_answer = f"x {SYM_DISPLAY[left_sym]} {lo} or x {SYM_DISPLAY[right_sym]} {hi}"

    factor_str = (
        f"-({_fmt_root_factor(r1)})({_fmt_root_factor(r2)})"
        if leading == -1
        else f"({_fmt_root_factor(r1)})({_fmt_root_factor(r2)})"
    )
    prompt = f"Solve the inequality: {_fmt_quadratic(qa, qb, qc)} {SYM_DISPLAY[symbol]} 0"
    worked_calculation = [
        f"{_fmt_quadratic(qa, qb, qc)} {SYM_DISPLAY[symbol]} 0",
        f"{factor_str} {SYM_DISPLAY[symbol]} 0",
        f"Roots (critical values): x = {lo}, x = {hi}",
        final_answer,
    ]

    parabola_desc = "U-shaped" if leading == 1 else "upside-down U-shaped"
    teaching_steps = [
        "A quadratic inequality is solved by first factorising the quadratic to find its roots (the "
        "'critical values' where the expression equals zero) - these are the two points where the graph "
        "crosses the x-axis.",
        f"Factorising gives roots at x = {lo} and x = {hi}. Sketching (even just mentally) the graph of "
        f"y = {_fmt_quadratic(qa, qb, qc)}, which is a {parabola_desc} parabola since the coefficient of "
        f"x^2 is {'positive' if leading == 1 else 'negative'}, shows exactly where the graph is above or "
        "below the x-axis.",
        (
            "Since the inequality asks where the expression is negative (or zero), and this parabola opens "
            "upwards, that happens only in the dip between the two roots - so the solution is the range "
            "between them."
            if between and leading == 1
            else
            "Since the inequality asks where the expression is positive (or zero), and this parabola opens "
            "downwards, that happens only in the hump between the two roots - so the solution is the range "
            "between them."
            if between
            else
            "Since the inequality asks for the opposite sign to what happens between the roots, the "
            "solution must lie outside them instead - either below the smaller root or above the larger one."
        ),
        f"Putting that together gives the final answer: {final_answer}.",
    ]

    return ModelledExample(
        topic_id="quadratic_inequalities",
        tier=Tier.HIGHER,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=final_answer,
    )


TOPIC_SOLVING_INEQUALITIES_FOUNDATION = TopicDefinition(
    id="solving_inequalities_foundation",
    display_name="Solving Linear Inequalities",
    description="Solve a one- or two-step linear inequality, keeping the coefficient of x positive.",
    generate=generate_solving_inequalities_foundation,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_solving_inequalities_foundation,
)

TOPIC_SOLVING_INEQUALITIES_HIGHER = TopicDefinition(
    id="solving_inequalities_higher",
    display_name="Solving Linear Inequalities",
    description=(
        "Solve a linear inequality that requires collecting x-terms from both sides or expanding a "
        "bracket, reversing the inequality sign when dividing by a negative number."
    ),
    generate=generate_solving_inequalities_higher,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_solving_inequalities_higher,
)

TOPIC_SATISFYING_INEQUALITIES_FOUNDATION = TopicDefinition(
    id="satisfying_inequalities_foundation",
    display_name="Satisfying an Inequality",
    description="Solve a compound inequality and list every integer value of x that satisfies it.",
    generate=generate_satisfying_inequalities_foundation,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_satisfying_inequalities_foundation,
)

TOPIC_SATISFYING_INEQUALITIES_HIGHER = TopicDefinition(
    id="satisfying_inequalities_higher",
    display_name="Satisfying an Inequality",
    description=(
        "Solve a compound inequality with a negative coefficient, or combine two separate inequalities "
        "into one range, then list every integer value of x that satisfies it."
    ),
    generate=generate_satisfying_inequalities_higher,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_satisfying_inequalities_higher,
)

TOPIC_QUADRATIC_INEQUALITIES = TopicDefinition(
    id="quadratic_inequalities",
    display_name="Solving Quadratic Inequalities",
    description="Solve a quadratic inequality by factorising and reasoning about the shape of the parabola.",
    generate=generate_quadratic_inequalities,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_quadratic_inequalities,
)
