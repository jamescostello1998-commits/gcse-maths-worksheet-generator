"""Which topics go on which practice paper, and how many marks each one is
worth. Two curated inputs drive selection - a per-section mark-share target
(a judgment-call approximation of real GCSE paper weighting) and a per-topic
"priority" tag (core/common/niche) so frequently-examined skills recur across
several papers while advanced/rare topics appear less often. Neither list
needs to be exhaustive - anything not explicitly tagged defaults to "common".
"""

import random

from app.core.models import Tier
from app.core.registry import list_topics
from app.practice_tests.mark_scheme import build_mark_scheme
from app.topics.base import TopicDefinition

SECTION_TARGET_MARKS: dict[str, int] = {
    "number": 25,
    "algebra": 30,
    "ratio_proportion": 15,
    "geometry": 15,
    "probability": 8,
    "statistics": 7,
}

CORE_TOPIC_IDS: frozenset[str] = frozenset(
    {
        # Number
        "fractions_add_subtract_F", "fractions_of_amount_F", "decimals_round_dp_F",
        "standard_form_to_F", "negative_add_subtract_F", "bidmas_F",
        # Algebra
        "linear_two_step_F", "linear_multi_step_F", "expand_single_bracket_F",
        "factorise_common_factor_F", "sequences_nth_term_F",
        "forming_equations_F", "forming_equations_H",
        # Ratio & Proportion
        "percentage_of_amount_F", "percentage_change_F", "ratio_share_two_part_F",
        "direct_proportion_F",
        # Geometry
        "area_rectangle_F", "area_triangle_F", "angles_triangle_F",
        "angles_straight_line_F", "pythagoras_hypotenuse_triple_F",
        "trig_missing_side_F",
        # Probability
        "probability_single_event_F", "probability_and_or_rule_F",
        "tree_diagram_independent_F", "two_way_tables_F",
        # Statistics
        "stats_mean_F", "stats_mode_F", "stats_median_F", "stats_range_F",
        "bar_chart_interpret_F",
    }
)

NICHE_TOPIC_IDS: frozenset[str] = frozenset(
    {
        # Algebra
        "iteration_H", "algebraic_proof_H", "quadratic_inequalities_H",
        "functions_composite_inverse_H", "graph_transformations_H",
        "algebraic_fractions_add_subtract_H", "algebraic_fractions_multiply_divide_H",
        # Geometry
        "circle_theorems_H", "geometric_vectors_H", "sine_rule_H", "cosine_rule_H",
        "triangle_area_sine_rule_H", "vectors_arithmetic_H",
        # Number
        "algebraic_surds_H", "rationalise_denominator_H",
        "indices_common_base_equations_H", "surds_multiply_divide_H",
        # Probability
        "tree_diagram_algebraic_H", "venn_diagram_algebra_H", "product_rule_counting_H",
        # Statistics
        "histogram_interpret_H", "cumulative_frequency_interpret_H",
        "box_plot_interpret_H", "stats_interquartile_range_H",
    }
)

_PRIORITY_WEIGHT = {"core": 3, "common": 2, "niche": 1}

# Topics confirmed to require a calculator - a messy/irrational decimal result
# (rounded trig ratios, sqrt-derived lengths, calculator-value-of-pi areas/
# volumes), or explicitly labelled "(Calculator)" in their own display_name.
# Real OCR GCSE Maths reserves Paper 2 (Foundation) / Paper 5 (Higher) - the
# middle paper of every 3-paper sitting - as non-calculator, so build.py
# excludes every topic in this set from that paper's eligible pool. A topic
# whose generator randomly branches between an exact and a decimal/irrational
# result (e.g. quadratic_formula's decimal-vs-surd branches) is included here
# wholesale, since selection can't pick only the exact branch - conservative,
# but this only affects 1 of every 3 papers, so the cost of erring toward
# inclusion is low (see CLAUDE.md-style rationale in the PR that added this).
CALCULATOR_ONLY_TOPIC_IDS: frozenset[str] = frozenset(
    {
        # Number
        "standard_form_calculator_F",
        # Ratio & Proportion - now that a genuinely non-calculator-friendly
        # sibling exists for each of these (best_buys_noncalculator,
        # direct_proportion_noncalculator, inverse_proportion_noncalculator),
        # the original topics move here so a non-calculator paper picks the
        # friendly sibling instead - their own numbers were never guaranteed
        # to avoid a calculator (best_buys' sticker-price division especially).
        "percentage_increase_decrease_calculator_H",
        "best_buys_F", "direct_proportion_F", "inverse_proportion_F",
        # Geometry - decimal/calculator-pi area & perimeter
        "area_circle_F", "area_semicircle_compound_F",
        "arc_length_F", "area_sector_F",
        # Geometry - decimal/calculator-pi volume & surface area
        "volume_surface_area_cylinder_F", "volume_surface_area_cone_H",
        "volume_surface_area_sphere_H", "volume_surface_area_pyramid_H",
        "frustum_volume_surface_area_H", "compound_3d_volume_H", "compound_3d_surface_area_H",
        # Geometry - Pythagoras/trig giving a rounded decimal answer
        "pythagoras_hypotenuse_decimal_F", "pythagoras_3d_H", "trig_3d_H",
        "trig_missing_side_F", "trig_missing_side_H",
        "trig_missing_angle_F", "trig_missing_angle_H", "trig_mixed_H",
        "sine_rule_H", "cosine_rule_H", "triangle_area_sine_rule_H", "bearings_cosine_rule_H",
        # Algebra - branches between an exact surd and a rounded decimal root
        "quadratic_formula_H",
        # Algebra - the process itself requires repeated calculator evaluation
        "iteration_H",
    }
)


def topic_priority(topic_id: str) -> str:
    if topic_id in CORE_TOPIC_IDS:
        return "core"
    if topic_id in NICHE_TOPIC_IDS:
        return "niche"
    return "common"


def eligible_topics_by_section(tier: Tier, calculator_allowed: bool = True) -> dict[str, list[TopicDefinition]]:
    """The pool of topics available for a paper of this tier. When
    calculator_allowed is False (the middle paper of a 3-paper sitting - real
    OCR's non-calculator paper), every topic in CALCULATOR_ONLY_TOPIC_IDS is
    excluded from the pool entirely."""
    by_section: dict[str, list[TopicDefinition]] = {s: [] for s in SECTION_TARGET_MARKS}
    for topic in list_topics():
        if topic.fixed_tier != tier or topic.section not in by_section:
            continue
        if not calculator_allowed and topic.id in CALCULATOR_ONLY_TOPIC_IDS:
            continue
        by_section[topic.section].append(topic)
    return by_section


def typical_marks_for(topic: TopicDefinition, sample_rng: random.Random) -> int:
    """A throwaway generation used only to measure how many marks this
    topic's question shape is typically worth (via the same rule used for
    real frozen questions) - not the question that ends up on any paper."""
    question = topic.generate(topic.fixed_tier, sample_rng)
    marks, _ = build_mark_scheme(question.solution_steps, question.final_answer)
    return marks


def _weighted_choice(topics: list[TopicDefinition], rng: random.Random) -> TopicDefinition:
    weights = [_PRIORITY_WEIGHT[topic_priority(t.id)] for t in topics]
    return rng.choices(topics, weights=weights, k=1)[0]


def select_paper_topics(
    tier: Tier,
    rng: random.Random,
    typical_marks: dict[str, int],
    by_section: dict[str, list[TopicDefinition]],
    target_total: int = 100,
    max_attempts: int = 500,
    max_restarts: int = 50,
) -> list[TopicDefinition]:
    """Pick an ordered list of distinct topics (no repeats within one paper)
    whose *typical* mark values sum to exactly target_total, roughly matching
    each section's target share. The real per-paper mark total is only known
    once build.py generates the actual frozen questions (a handful of topics
    have branch-dependent solution_steps length) - build.py re-checks and
    repairs if the real total drifts from this plan.

    The single-pass fill-then-close algorithm occasionally paints itself into
    a corner (a tight pool with an unlucky draw sequence) - rather than a
    hand-tuned perfect solver, this just retries the whole attempt with a
    freshly perturbed sub-seed, which resolves it in practice within a few
    restarts."""
    for _ in range(max_restarts):
        try:
            return _attempt_select_paper_topics(tier, rng, typical_marks, by_section, target_total, max_attempts)
        except ValueError:
            continue
    raise ValueError(f"Could not assemble a {tier.value} paper summing to exactly {target_total} marks")


def _attempt_select_paper_topics(
    tier: Tier,
    rng: random.Random,
    typical_marks: dict[str, int],
    by_section: dict[str, list[TopicDefinition]],
    target_total: int,
    max_attempts: int,
) -> list[TopicDefinition]:
    chosen: list[TopicDefinition] = []
    used_ids: set[str] = set()
    section_totals = {s: 0 for s in SECTION_TARGET_MARKS}
    total = 0

    def all_unused() -> list[TopicDefinition]:
        return [t for topics in by_section.values() for t in topics if t.id not in used_ids]

    # Phase 1: fill each section toward its own target share (best-effort -
    # may undershoot if a section's pool runs out or nothing fits).
    for section, target in SECTION_TARGET_MARKS.items():
        attempts = 0
        while section_totals[section] < target and total < target_total and attempts < max_attempts:
            attempts += 1
            pool = [t for t in by_section[section] if t.id not in used_ids]
            if not pool:
                break
            candidate = _weighted_choice(pool, rng)
            m = typical_marks[candidate.id]
            if total + m > target_total:
                continue
            chosen.append(candidate)
            used_ids.add(candidate.id)
            total += m
            section_totals[section] += m

    # Phase 2: top up from any section (ignoring section targets) until
    # within reach of an exact close - no single question is worth more than
    # 5 marks, so the gap-closing pass below can only ever close a gap <= 5.
    max_single_marks = max(typical_marks.values(), default=0)
    attempts = 0
    while total < target_total - max_single_marks and attempts < max_attempts:
        attempts += 1
        pool = all_unused()
        if not pool:
            break
        candidate = _weighted_choice(pool, rng)
        m = typical_marks[candidate.id]
        if total + m > target_total:
            continue
        chosen.append(candidate)
        used_ids.add(candidate.id)
        total += m

    # Phase 3: exact gap-closing with backtracking. If no unused topic's
    # marks exactly match the remaining gap, remove a RANDOM already-chosen
    # question (not always the last one) and retry - removing a random item
    # reshuffles the gap value instead of cycling on the same dead end.
    attempts = 0
    while total != target_total and attempts < max_attempts:
        attempts += 1
        gap = target_total - total
        candidates = [t for t in all_unused() if 0 < typical_marks[t.id] == gap]
        if candidates:
            pick = _weighted_choice(candidates, rng)
            chosen.append(pick)
            used_ids.add(pick.id)
            total = target_total
            break
        if chosen:
            idx = rng.randrange(len(chosen))
            removed = chosen.pop(idx)
            used_ids.discard(removed.id)
            total -= typical_marks[removed.id]
        else:
            break

    if total != target_total:
        raise ValueError(f"Could not assemble a {tier.value} paper summing to exactly {target_total} marks")

    return chosen
