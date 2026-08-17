import random
from dataclasses import replace
from datetime import datetime, timezone

from app.core.errors import WorksheetGenerationError
from app.core.models import Question, Tier, Worksheet
from app.core.registry import get_topic
from app.topics.phrasing import AMOUNT_VERBS, CONVERT_PHRASINGS, EVALUATE_VERBS, SIMPLIFY_VERBS

DEFAULT_COUNT = 20
DEFAULT_MAX_ATTEMPTS = 400
MIN_COUNT = 5
MAX_COUNT = 40

# Topics where every question repeats the SAME leading instruction, mapped to
# that exact instruction string. On a single-topic worksheet the builder hoists
# it to one page-level header and shows each question's bare remainder
# (item_text) instead of repeating it - see app/pdf/renderer.py and
# app/docx/render.py. Fail-safe: a topic is only hoisted if EVERY question's
# prompt genuinely begins with this string and leaves a non-empty remainder
# (see _apply_shared_instruction); if a generator's wording ever drifts, the
# match fails and the full prompt is shown as before. Practice Tests (frozen,
# mixed papers) and modelled examples never pass through here, so they always
# keep the full self-contained prompt.
HOISTED_INSTRUCTIONS: dict[str, str] = {
    "classify_expressions_F": "Is the following an expression, equation, formula, or identity?",
    "prime_numbers_F": "From this list, write down all the prime numbers:",
    "lcm_by_listing_F": "Find the lowest common multiple (LCM) of",
    "hcf_by_listing_F": "Find the highest common factor (HCF) of",
    "hcf_lcm_by_prime_factors_H": "Using prime factorisation, find the",
    "expand_double_brackets_F": "Expand and simplify:",
    "expand_double_brackets_no_coefficient_F": "Expand and simplify:",
    "expand_double_brackets_H": "Expand and simplify:",
    "expand_triple_brackets_H": "Expand and simplify:",
    "expand_triple_brackets_no_coefficient_H": "Expand and simplify:",
    "change_subject_factorise_H": "Make x the subject of the formula",
    "simultaneous_common_coefficient_F": "Solve the simultaneous equations:",
    "simultaneous_different_coefficient_H": "Solve the simultaneous equations:",
    "simultaneous_quadratic_H": "Solve the simultaneous equations:",
    "solving_inequalities_F": "Solve the inequality:",
    "solving_inequalities_H": "Solve the inequality:",
    "quadratic_inequalities_H": "Solve the inequality:",
    "sequences_next_term_F": "Find the next term in the sequence:",
    "exact_trig_values_H": "Write down the exact value of",
    "stats_mean_F": "Find the mean of this data set:",
    "stats_mode_F": "Find the mode of this data set:",
    "stats_median_F": "Find the median of this data set:",
    "stats_range_F": "Find the range of this data set:",
    "fractional_equations_F": "Solve the following equation.",
    "fractional_equations_H": "Solve the following equation.",
    "cross_multiplication_F": "Solve the following equation.",
    "cross_multiplication_H": "Solve the following equation.",
    "fractional_equations_advanced_H": "Solve the following equation, giving your answers to 2 decimal places where necessary.",
    "linear_one_step_F": "Solve:",
    "linear_two_step_F": "Solve:",
    "linear_multi_step_F": "Solve:",
    "linear_both_sides_F": "Solve:",
    "linear_both_sides_H": "Solve:",
    "linear_brackets_F": "Solve:",
    "linear_brackets_H": "Solve:",
    "expand_single_bracket_F": "Expand:",
    "factorise_common_factor_F": "Factorise:",
    "factorise_quadratics_F": "Factorise:",
    "factorise_quadratics_H": "Factorise:",
    "algebraic_indices_F": "Simplify",
    "algebraic_indices_H": "Simplify",
    "turning_point_of_graph_H": "Find the coordinates of the turning point of the curve",
}


def _apply_shared_instruction(topic_id: str, questions: list[Question]) -> tuple[list[Question], str | None]:
    """If this topic is in HOISTED_INSTRUCTIONS and every question's prompt
    starts with that instruction (leaving a non-empty remainder), return the
    questions rewritten with shared_instruction/item_text set, plus the shared
    instruction. Otherwise return them unchanged with None."""
    instr = HOISTED_INSTRUCTIONS.get(topic_id)
    if not instr:
        return questions, None
    items = [q.prompt[len(instr):].strip() if q.prompt.startswith(instr) else None for q in questions]
    if not all(items):
        return questions, None  # wording drifted - fall back to full prompts
    rewritten = [replace(q, shared_instruction=instr, item_text=item) for q, item in zip(questions, items)]
    return rewritten, instr


_FRACTION_SIMPLEST_FORM_SUFFIX = ". Give your answer as a fraction in its simplest form."
_FRACTION_SIMPLEST_FORM_TITLE = "{v} the following, giving your answer as a fraction in its simplest form."
_MIXED_NUMBER_SUFFIX = ". Give your answer as a mixed number."
_MIXED_NUMBER_TITLE = "{v} the following, giving your answer as a mixed number."
_BARE_PERIOD_SUFFIX = "."
_BARE_PERIOD_TITLE = "{v} the following."
_STANDARD_FORM_ANSWER_SUFFIX = ". Give your answer in standard form."
_STANDARD_FORM_ANSWER_TITLE = "{v} the following, giving your answer in standard form."
_EVALUATE_OR_SIMPLIFY_VERBS = EVALUATE_VERBS + SIMPLIFY_VERBS
_CONVERT_VERBS = [v for v, _ in CONVERT_PHRASINGS]


def _titles(template: str, verbs: list[str]) -> list[str]:
    """Expand a "{v} ..." title template across a verb pool into the list of
    complete title strings _apply_shared_verb_instruction picks from."""
    return [template.format(v=v) for v in verbs]


def _colon_titles(verbs: list[str]) -> list[str]:
    """Sibling to _titles for "verb_only"-style entries, whose title is
    always just "{verb}:" with nothing else appended."""
    return [f"{v}:" for v in verbs]


# Topics whose questions each independently vary their OWN leading verb (see
# app/topics/phrasing.py's verb pools), rather than repeating one fixed
# instruction string throughout the worksheet (that simpler case is
# HOISTED_INSTRUCTIONS above). On a single-topic worksheet, ONE title is
# chosen ONCE from title_choices (equal chance per choice, not per question)
# for a shared bold header, rather than repeating a randomly-varying verb on
# every question - see _apply_shared_verb_instruction. title_choices is
# usually just a verb pool expanded across one template (via _titles/
# _colon_titles above), but is a plain list so a topic whose verb and
# preposition are paired (e.g. "Write ... in" vs "Convert ... to") can supply
# genuinely different full titles rather than one template shared by every
# verb.
#
# style="full": every question's own trailing text (after its own verb) is
# identical boilerplate (e.g. always "Give your answer as a fraction in its
# simplest form.") - both the verb AND that boilerplate collapse into one
# combined title, leaving a bare expression per question.
# style="verb_only": the trailing text genuinely varies per question (e.g.
# "giving your answer as a single power of {base}", where {base} differs by
# question) - only the leading verb hoists; each question keeps its own full
# remainder, including its own trailing clause, unchanged.
#
# Each entry: (candidate verb pool [used to recognise/strip each question's
# own leading verb - not necessarily the same wording as title_choices],
# style, suffix to also strip [only used for "full"], title_choices to pick
# the shared header from).
HOISTED_VERB_INSTRUCTIONS: dict[str, tuple[list[str], str, str, list[str]]] = {
    "fractions_add_subtract_F": (
        EVALUATE_VERBS, "full", _FRACTION_SIMPLEST_FORM_SUFFIX, _titles(_FRACTION_SIMPLEST_FORM_TITLE, EVALUATE_VERBS)
    ),
    "fractions_multiply_F": (
        EVALUATE_VERBS, "full", _FRACTION_SIMPLEST_FORM_SUFFIX, _titles(_FRACTION_SIMPLEST_FORM_TITLE, EVALUATE_VERBS)
    ),
    "fractions_divide_F": (
        EVALUATE_VERBS, "full", _FRACTION_SIMPLEST_FORM_SUFFIX, _titles(_FRACTION_SIMPLEST_FORM_TITLE, EVALUATE_VERBS)
    ),
    "fractions_divide_H": (
        EVALUATE_VERBS, "full", _FRACTION_SIMPLEST_FORM_SUFFIX, _titles(_FRACTION_SIMPLEST_FORM_TITLE, EVALUATE_VERBS)
    ),
    "fractions_mixed_number_arithmetic_H": (
        EVALUATE_VERBS, "full", _MIXED_NUMBER_SUFFIX, _titles(_MIXED_NUMBER_TITLE, EVALUATE_VERBS)
    ),
    "decimals_add_subtract_F": (EVALUATE_VERBS, "full", _BARE_PERIOD_SUFFIX, _titles(_BARE_PERIOD_TITLE, EVALUATE_VERBS)),
    "decimals_multiply_F": (EVALUATE_VERBS, "full", _BARE_PERIOD_SUFFIX, _titles(_BARE_PERIOD_TITLE, EVALUATE_VERBS)),
    "decimals_divide_F": (EVALUATE_VERBS, "full", _BARE_PERIOD_SUFFIX, _titles(_BARE_PERIOD_TITLE, EVALUATE_VERBS)),
    "number_powers_of_ten_F": (EVALUATE_VERBS, "full", _BARE_PERIOD_SUFFIX, _titles(_BARE_PERIOD_TITLE, EVALUATE_VERBS)),
    "fractions_of_amount_F": (AMOUNT_VERBS, "full", _BARE_PERIOD_SUFFIX, _titles(_BARE_PERIOD_TITLE, AMOUNT_VERBS)),
    "bidmas_F": (EVALUATE_VERBS, "full", _BARE_PERIOD_SUFFIX, _titles(_BARE_PERIOD_TITLE, EVALUATE_VERBS)),
    "bidmas_two_three_F": (EVALUATE_VERBS, "full", _BARE_PERIOD_SUFFIX, _titles(_BARE_PERIOD_TITLE, EVALUATE_VERBS)),
    "negative_add_subtract_F": (EVALUATE_VERBS, "full", _BARE_PERIOD_SUFFIX, _titles(_BARE_PERIOD_TITLE, EVALUATE_VERBS)),
    "negative_multiply_divide_F": (
        EVALUATE_VERBS, "full", _BARE_PERIOD_SUFFIX, _titles(_BARE_PERIOD_TITLE, EVALUATE_VERBS)
    ),
    "fractions_improper_mixed_F": (_CONVERT_VERBS, "verb_only", "", _colon_titles(_CONVERT_VERBS)),
    # powers_F is now evaluate-only (split from the old combined topic, see
    # indices_law_F below) - every question is "{verb} {base}^{exponent}."
    # with nothing after the bare period, so this collapses fully.
    "powers_F": (EVALUATE_VERBS, "full", _BARE_PERIOD_SUFFIX, _titles(_BARE_PERIOD_TITLE, EVALUATE_VERBS)),
    # indices_law_F's own trailing clause names the base ("...as a single
    # power of {base}"), which varies per question (numeric or "x") - only
    # the leading verb is safe to hoist.
    "indices_law_F": (SIMPLIFY_VERBS, "verb_only", "", _colon_titles(SIMPLIFY_VERBS)),
    "powers_H": (EVALUATE_VERBS, "verb_only", "", _colon_titles(EVALUATE_VERBS)),
    "roots_H": (SIMPLIFY_VERBS, "verb_only", "", _colon_titles(SIMPLIFY_VERBS)),
    "negative_indices_F": (_EVALUATE_OR_SIMPLIFY_VERBS, "verb_only", "", _colon_titles(_EVALUATE_OR_SIMPLIFY_VERBS)),
    "simplifying_indices_challenging_H": (
        SIMPLIFY_VERBS, "full", ", giving your answer as a fraction where necessary.",
        ["Fully simplify (giving your answer as a fraction if necessary)"],
    ),
    "indices_common_base_equations_H": (["Solve"], "full", ".", ["Solve:"]),
    "surds_multiply_divide_H": (_EVALUATE_OR_SIMPLIFY_VERBS, "verb_only", "", _colon_titles(_EVALUATE_OR_SIMPLIFY_VERBS)),
    # "Write {n} in standard form." - the generator always says "Write", but
    # the displayed title varies across a small Write/Convert/Express pool
    # (each paired with its own natural preposition, since "Convert in" and
    # "Write to" don't read naturally - see CONVERT_PHRASINGS' precedent).
    "standard_form_to_F": (
        ["Write"], "full", " in standard form.",
        ["Write in standard form:", "Convert to standard form:", "Express in standard form:"],
    ),
    "standard_form_to_small_F": (
        ["Write"], "full", " in standard form.",
        ["Write in standard form:", "Convert to standard form:", "Express in standard form:"],
    ),
    # "Write {a} × 10^{n} as an ordinary number." - the reverse direction;
    # kept to one fixed title rather than a pool, per direct confirmation.
    "standard_form_from_large_F": (["Write"], "full", " as an ordinary number.", ["Write as an ordinary number:"]),
    "standard_form_from_small_F": (["Write"], "full", " as an ordinary number.", ["Write as an ordinary number:"]),
    # "Work out (...) op (...). Give your answer in standard form." - an
    # arithmetic topic, not a conversion, so it reuses the EVALUATE_VERBS
    # pool/template pattern rather than the Write/Convert/Express one above.
    "standard_form_multiply_divide_F": (
        EVALUATE_VERBS, "full", _STANDARD_FORM_ANSWER_SUFFIX, _titles(_STANDARD_FORM_ANSWER_TITLE, EVALUATE_VERBS)
    ),
    "standard_form_multiply_divide_H": (
        EVALUATE_VERBS, "full", _STANDARD_FORM_ANSWER_SUFFIX, _titles(_STANDARD_FORM_ANSWER_TITLE, EVALUATE_VERBS)
    ),
    "standard_form_add_subtract_H": (
        EVALUATE_VERBS, "full", _STANDARD_FORM_ANSWER_SUFFIX, _titles(_STANDARD_FORM_ANSWER_TITLE, EVALUATE_VERBS)
    ),
    # "Work out an estimate for (...) by rounding each number to 1
    # significant figure." - always the same fixed wording (no verb pool),
    # reordered into one title with the "by rounding..." clause moved first.
    "estimation_rounding_F": (
        ["Work out an estimate for"], "full", " by rounding each number to 1 significant figure.",
        ["By rounding each number to 1 significant figure, estimate:"],
    ),
    "fractions_simplify_F": (SIMPLIFY_VERBS, "full", _BARE_PERIOD_SUFFIX, _titles(_BARE_PERIOD_TITLE, SIMPLIFY_VERBS)),
    # Both factorising branches always end in the identical fixed clause
    # "= 0 by factorising." - splitting the suffix just before " by" (not
    # before "= 0") keeps the "= 0" attached to each item, since that's part
    # of the actual equation, not decoration, while "by factorising" moves
    # into the title.
    "solve_quadratic_factorising_F": (["Solve"], "full", " by factorising.", ["Solve by factorising:"]),
    "solve_quadratic_factorising_H": (["Solve"], "full", " by factorising.", ["Solve by factorising:"]),
    "solve_quadratic_completing_square_H": (
        ["Solve"], "full", " by completing the square, giving your answers in exact surd form.",
        ["Solve the following by completing the square, giving your answers in exact surd form:"],
    ),
    # "Write {n} as a product of its prime factors[, giving your answer in
    # index form]." - always the same fixed wording (no verb pool), the
    # number is the only thing that varies.
    "prime_factors_F": (
        ["Write"], "full", " as a product of its prime factors.",
        ["Write the following as a product of its prime factors:"],
    ),
    "prime_factors_H": (
        ["Write"], "full", " as a product of its prime factors, giving your answer in index form.",
        ["Write the following as a product of its prime factors, giving your answer in index form:"],
    ),
    # "Rationalise the denominator of {fraction}, giving your answer in its
    # simplest form." - always the same fixed wording (no verb pool); the
    # "verb" here is the whole multi-word lead-in, exactly like
    # estimation_rounding_F's "Work out an estimate for" below.
    "rationalise_denominator_H": (
        ["Rationalise the denominator of"], "full", ", giving your answer in its simplest form.",
        ["Rationalise the denominator of the following, giving your answer in its simplest form."],
    ),
    # "Write {expr} in the form (x + p)^2 + q." - always the same fixed wording.
    "completing_the_square_H": (
        ["Write"], "full", " in the form (x + p)^2 + q.",
        ["Write the following in the form (x + p)^2 + q."],
    ),
    # "Solve {equation}" - the displayed title is a completely different phrase
    # ("By using the quadratic formula, solve:") from the matched leading verb
    # ("Solve"), which HOISTED_VERB_INSTRUCTIONS supports directly (the verb
    # pool is only used to find/strip the prompt's own leading word - the
    # title_choices list is independent display text).
    "quadratic_formula_H": (["Solve"], "full", "", ["By using the quadratic formula, solve:"]),
    # "Simplify {fraction expr}, giving your answer as a single fraction." /
    # "...in its simplest form." - always the same fixed wording per topic.
    "algebraic_fractions_add_subtract_H": (["Simplify"], "full", ", giving your answer as a single fraction.", ["Simplify"]),
    "algebraic_fractions_multiply_divide_H": (
        ["Simplify"], "full", ", giving your answer in its simplest form.", ["Simplify"]
    ),
    # "Solve the inequality {...}, then list the integer values of x that
    # satisfy it." - satisfying_inequalities_H's "separate" shape (two
    # independent inequalities joined by "and") was reworded to share this
    # exact prefix/suffix with its other shape so hoisting works reliably
    # regardless of which shape a worksheet's questions land on.
    "satisfying_inequalities_F": (
        ["Solve the inequality"], "full", ", then list the integer values of x that satisfy it.",
        ["Solve the inequality, then list the integer values of x that satisfy it."],
    ),
    "satisfying_inequalities_H": (
        ["Solve the inequality"], "full", ", then list the integer values of x that satisfy it.",
        ["Solve the inequality, then list the integer values of x that satisfy it."],
    ),
}


def _apply_shared_verb_instruction(
    topic_id: str, questions: list[Question], rng: random.Random
) -> tuple[list[Question], str | None]:
    """Sibling to _apply_shared_instruction, for topics in
    HOISTED_VERB_INSTRUCTIONS whose questions vary their own leading verb
    per-question rather than sharing one fixed instruction string. Fail-safe
    exactly like _apply_shared_instruction: if any question's prompt doesn't
    start with a pool verb (or, for "full" style, end with the expected
    suffix), the match fails and the full prompts are shown as before."""
    entry = HOISTED_VERB_INSTRUCTIONS.get(topic_id)
    if not entry:
        return questions, None
    verbs, style, suffix, title_choices = entry

    items: list[str] = []
    for q in questions:
        verb = next((v for v in verbs if q.prompt.startswith(v + " ")), None)
        if verb is None:
            return questions, None
        rest = q.prompt[len(verb) + 1 :]
        if style == "full":
            if not rest.endswith(suffix) or len(rest) <= len(suffix):
                return questions, None
            item = rest[: len(rest) - len(suffix)].strip()
        else:
            item = rest.strip()
        if not item:
            return questions, None
        items.append(item)

    instr = rng.choice(title_choices)
    rewritten = [replace(q, shared_instruction=instr, item_text=item) for q, item in zip(questions, items)]
    return rewritten, instr


def build_worksheet(
    topic_id: str,
    tier: Tier,
    count: int = DEFAULT_COUNT,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    rng: random.Random | None = None,
) -> Worksheet:
    topic = get_topic(topic_id)
    rng = rng or random.Random()

    seen_keys: set[str] = set()
    questions: list[Question] = []
    attempts = 0

    while len(questions) < count and attempts < max_attempts:
        attempts += 1
        question = topic.generate(tier, rng)
        if question.dedup_key in seen_keys:
            continue
        seen_keys.add(question.dedup_key)
        questions.append(question)

    if len(questions) < count:
        raise WorksheetGenerationError(
            topic_id=topic_id,
            tier=tier.value,
            attempts=attempts,
            produced=len(questions),
        )

    questions, shared_instruction = _apply_shared_instruction(topic.id, questions)
    if shared_instruction is None:
        questions, shared_instruction = _apply_shared_verb_instruction(topic.id, questions, rng)

    return Worksheet(
        topic_id=topic.id,
        topic_name=topic.display_name,
        tier=tier,
        questions=tuple(questions),
        generated_at=datetime.now(timezone.utc),
        preamble_lines=topic.preamble_lines or (),
        shared_instruction=shared_instruction,
    )
