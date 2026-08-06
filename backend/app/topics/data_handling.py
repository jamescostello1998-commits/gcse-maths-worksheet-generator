import itertools
import random
from decimal import Decimal
from fractions import Fraction

from app.core.models import DiagramSpec, ModelledExample, Question, Tier
from app.topics.base import TopicDefinition

SECTION = "probability"
GROUP_COUNTING = "Sets and Counting"
GROUP_DATA = "Tables and Diagrams"


def _venn_region_text(universal: list, a_set: set, b_set: set) -> dict:
    """The four atomic Venn regions (a_only/b_only/both/neither) for
    draw_venn_diagram's region_text param - always the full partition of the
    universal set, independent of which specific notation a question asks
    about, so the solution diagram shows exactly where every element went."""
    regions = {
        "a_only": sorted(a_set - b_set),
        "b_only": sorted(b_set - a_set),
        "both": sorted(a_set & b_set),
        "neither": sorted(set(universal) - (a_set | b_set)),
    }
    return {key: (", ".join(str(x) for x in elems) if elems else "-") for key, elems in regions.items()}


def generate_set_notation(tier: Tier, rng: random.Random) -> Question:
    universal = list(range(1, rng.choice([10, 11, 12]) + 1))
    a_set = set(rng.sample(universal, rng.randint(3, 6)))
    b_set = set(rng.sample(universal, rng.randint(3, 6)))

    operation = rng.choice(
        ["union", "intersection", "complement_a", "complement_union", "complement_intersection", "a_and_not_b"]
    )

    if operation == "union":
        result = a_set | b_set
        notation, description = "A ∪ B", "A union B (elements in A, B, or both)"
    elif operation == "intersection":
        result = a_set & b_set
        notation, description = "A ∩ B", "A intersect B (elements in both A and B)"
    elif operation == "complement_a":
        result = set(universal) - a_set
        notation, description = "A'", "the complement of A (elements not in A)"
    elif operation == "complement_union":
        result = set(universal) - (a_set | b_set)
        notation, description = "(A ∪ B)'", "the complement of A union B"
    elif operation == "complement_intersection":
        result = set(universal) - (a_set & b_set)
        notation, description = "(A ∩ B)'", "the complement of A intersect B"
    else:
        result = a_set - b_set
        notation, description = "A ∩ B'", "elements in A but not in B"

    def manual_member(x: int) -> bool:
        in_a, in_b = x in a_set, x in b_set
        if operation == "union":
            return in_a or in_b
        if operation == "intersection":
            return in_a and in_b
        if operation == "complement_a":
            return not in_a
        if operation == "complement_union":
            return not (in_a or in_b)
        if operation == "complement_intersection":
            return not (in_a and in_b)
        return in_a and not in_b

    # Independent check: rebuild the result by scanning every element of the
    # universal set and testing membership manually, a different method than
    # the set-operator expressions used above.
    manual_result = {x for x in universal if manual_member(x)}
    if manual_result != result:
        raise ValueError("set_notation verification failed")

    ordered = sorted(result)
    answer = "{" + ", ".join(str(x) for x in ordered) + "}" if ordered else "{ } (the empty set)"

    steps = [
        f"ξ = {{{', '.join(str(x) for x in universal)}}}",
        f"A = {{{', '.join(str(x) for x in sorted(a_set))}}}",
        f"B = {{{', '.join(str(x) for x in sorted(b_set))}}}",
        f"{notation} means {description}.",
        f"{notation} = {answer}",
    ]
    return Question(
        topic_id="set_notation",
        tier=Tier.HIGHER,
        prompt=(
            f"ξ = {{{', '.join(str(x) for x in universal)}}}, A = {{{', '.join(str(x) for x in sorted(a_set))}}}, "
            f"B = {{{', '.join(str(x) for x in sorted(b_set))}}}. List the elements of {notation}."
        ),
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"set_notation:{universal[-1]}:{sorted(a_set)}:{sorted(b_set)}:{operation}",
        diagram=DiagramSpec(kind="venn_diagram", params={"labels": ["A", "B"], "universal_label": "ξ"}),
        solution_diagram=DiagramSpec(
            kind="venn_diagram",
            params={
                "labels": ["A", "B"], "universal_label": "ξ",
                "region_text": _venn_region_text(universal, a_set, b_set),
            },
        ),
    )


def generate_modelled_example_set_notation(tier: Tier, rng: random.Random) -> ModelledExample:
    universal = list(range(1, rng.choice([10, 11, 12]) + 1))
    a_set = set(rng.sample(universal, rng.randint(3, 6)))
    b_set = set(rng.sample(universal, rng.randint(3, 6)))

    operation = rng.choice(
        ["union", "intersection", "complement_a", "complement_union", "complement_intersection", "a_and_not_b"]
    )

    if operation == "union":
        result = a_set | b_set
        notation, description = "A ∪ B", "everything in A, in B, or in both"
    elif operation == "intersection":
        result = a_set & b_set
        notation, description = "A ∩ B", "only the elements that are in both A and B"
    elif operation == "complement_a":
        result = set(universal) - a_set
        notation, description = "A'", "everything in the universal set that is NOT in A"
    elif operation == "complement_union":
        result = set(universal) - (a_set | b_set)
        notation, description = "(A ∪ B)'", "everything that is in neither A nor B"
    elif operation == "complement_intersection":
        result = set(universal) - (a_set & b_set)
        notation, description = "(A ∩ B)'", "everything that is not in both A and B at once"
    else:
        result = a_set - b_set
        notation, description = "A ∩ B'", "elements in A that are NOT also in B"

    def manual_member(x: int) -> bool:
        in_a, in_b = x in a_set, x in b_set
        if operation == "union":
            return in_a or in_b
        if operation == "intersection":
            return in_a and in_b
        if operation == "complement_a":
            return not in_a
        if operation == "complement_union":
            return not (in_a or in_b)
        if operation == "complement_intersection":
            return not (in_a and in_b)
        return in_a and not in_b

    # Independent check: rebuild the result by scanning every element of the
    # universal set and testing membership manually, a different method than
    # the set-operator expressions used above.
    manual_result = {x for x in universal if manual_member(x)}
    if manual_result != result:
        raise ValueError("modelled example set_notation verification failed")

    ordered = sorted(result)
    answer = "{" + ", ".join(str(x) for x in ordered) + "}" if ordered else "{ } (the empty set)"

    teaching_steps = [
        "The universal set ξ contains every element we're considering; A and B are subsets of it, and set "
        "notation gives us a shorthand for describing combinations of them without listing elements out "
        "each time.",
        f"Here, {notation} means {description}.",
        "Go through the universal set one element at a time and test the condition for each - this is "
        "slower than spotting a pattern, but it never misses an element.",
        f"Collecting every element that passes the test gives {notation} = {answer}.",
    ]
    worked_calculation = [
        f"ξ = {{{', '.join(str(x) for x in universal)}}}",
        f"A = {{{', '.join(str(x) for x in sorted(a_set))}}}, B = {{{', '.join(str(x) for x in sorted(b_set))}}}",
        f"{notation} = {answer}",
    ]

    return ModelledExample(
        topic_id="set_notation",
        tier=Tier.HIGHER,
        prompt=(
            f"ξ = {{{', '.join(str(x) for x in universal)}}}, A = {{{', '.join(str(x) for x in sorted(a_set))}}}, "
            f"B = {{{', '.join(str(x) for x in sorted(b_set))}}}. List the elements of {notation}."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
        diagram=DiagramSpec(
            kind="venn_diagram",
            params={
                "labels": ["A", "B"], "universal_label": "ξ",
                "region_text": _venn_region_text(universal, a_set, b_set),
            },
        ),
    )


def generate_set_notation_foundation(tier: Tier, rng: random.Random) -> Question:
    universal = list(range(1, rng.choice([8, 9, 10]) + 1))
    a_set = set(rng.sample(universal, rng.randint(3, 5)))
    b_set = set(rng.sample(universal, rng.randint(3, 5)))

    operation = rng.choice(["union", "intersection", "not_a", "in_a_not_b"])

    if operation == "union":
        result = a_set | b_set
        question_text = "are in A, in B, or in both"
    elif operation == "intersection":
        result = a_set & b_set
        question_text = "are in both A and B"
    elif operation == "not_a":
        result = set(universal) - a_set
        question_text = "are not in A"
    else:
        result = a_set - b_set
        question_text = "are in A but not in B"

    def manual_member(x: int) -> bool:
        in_a, in_b = x in a_set, x in b_set
        if operation == "union":
            return in_a or in_b
        if operation == "intersection":
            return in_a and in_b
        if operation == "not_a":
            return not in_a
        return in_a and not in_b

    # Independent check: rebuild the result by scanning every element of the
    # universal set and testing membership manually, a different method than
    # the set-operator expressions used above.
    manual_result = {x for x in universal if manual_member(x)}
    if manual_result != result:
        raise ValueError("set_notation_foundation verification failed")

    ordered = sorted(result)
    answer = "{" + ", ".join(str(x) for x in ordered) + "}" if ordered else "{ } (none)"

    steps = [
        f"ξ = {{{', '.join(str(x) for x in universal)}}}",
        f"A = {{{', '.join(str(x) for x in sorted(a_set))}}}",
        f"B = {{{', '.join(str(x) for x in sorted(b_set))}}}",
        f"Check each element of ξ in turn to see whether it {question_text}.",
        f"Elements that {question_text}: {answer}",
    ]
    return Question(
        topic_id="set_notation_foundation",
        tier=Tier.FOUNDATION,
        prompt=(
            f"ξ = {{{', '.join(str(x) for x in universal)}}}, A = {{{', '.join(str(x) for x in sorted(a_set))}}}, "
            f"B = {{{', '.join(str(x) for x in sorted(b_set))}}}. List the elements that {question_text}."
        ),
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"set_notation_f:{universal[-1]}:{sorted(a_set)}:{sorted(b_set)}:{operation}",
        diagram=DiagramSpec(kind="venn_diagram", params={"labels": ["A", "B"], "universal_label": "ξ"}),
        solution_diagram=DiagramSpec(
            kind="venn_diagram",
            params={
                "labels": ["A", "B"], "universal_label": "ξ",
                "region_text": _venn_region_text(universal, a_set, b_set),
            },
        ),
    )


def generate_modelled_example_set_notation_foundation(tier: Tier, rng: random.Random) -> ModelledExample:
    universal = list(range(1, rng.choice([8, 9, 10]) + 1))
    a_set = set(rng.sample(universal, rng.randint(3, 5)))
    b_set = set(rng.sample(universal, rng.randint(3, 5)))

    operation = rng.choice(["union", "intersection", "not_a", "in_a_not_b"])

    if operation == "union":
        result = a_set | b_set
        question_text = "are in A, in B, or in both"
        why = "an element counts as long as it turns up in at least one of the two sets"
    elif operation == "intersection":
        result = a_set & b_set
        question_text = "are in both A and B"
        why = "an element only counts if it appears in A AND in B at the same time"
    elif operation == "not_a":
        result = set(universal) - a_set
        question_text = "are not in A"
        why = "an element counts if it's part of the universal set ξ but wasn't listed inside A"
    else:
        result = a_set - b_set
        question_text = "are in A but not in B"
        why = "an element has to be in A, but gets excluded if it's also in B"

    def manual_member(x: int) -> bool:
        in_a, in_b = x in a_set, x in b_set
        if operation == "union":
            return in_a or in_b
        if operation == "intersection":
            return in_a and in_b
        if operation == "not_a":
            return not in_a
        return in_a and not in_b

    manual_result = {x for x in universal if manual_member(x)}
    if manual_result != result:
        raise ValueError("modelled example set_notation_foundation verification failed")

    ordered = sorted(result)
    answer = "{" + ", ".join(str(x) for x in ordered) + "}" if ordered else "{ } (none)"

    teaching_steps = [
        "The universal set ξ contains every element being considered, and A and B are just smaller "
        "collections picked out from it - the question is really asking you to sort every element of "
        "ξ into 'counts' or 'doesn't count' based on a rule.",
        f"Here, the rule for which elements count is: they {question_text}. In other words, {why}.",
        f"Go through ξ = {{{', '.join(str(x) for x in universal)}}} one element at a time, checking "
        f"whether each one is in A = {{{', '.join(str(x) for x in sorted(a_set))}}} and/or "
        f"B = {{{', '.join(str(x) for x in sorted(b_set))}}}, and apply the rule.",
        f"Collecting every element that passes the test gives the answer: {answer}.",
    ]
    worked_calculation = [
        f"ξ = {{{', '.join(str(x) for x in universal)}}}",
        f"A = {{{', '.join(str(x) for x in sorted(a_set))}}}, B = {{{', '.join(str(x) for x in sorted(b_set))}}}",
        f"Elements that {question_text}: {answer}",
    ]
    return ModelledExample(
        topic_id="set_notation_foundation",
        tier=Tier.FOUNDATION,
        prompt=(
            f"ξ = {{{', '.join(str(x) for x in universal)}}}, A = {{{', '.join(str(x) for x in sorted(a_set))}}}, "
            f"B = {{{', '.join(str(x) for x in sorted(b_set))}}}. List the elements that {question_text}."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
        diagram=DiagramSpec(
            kind="venn_diagram",
            params={
                "labels": ["A", "B"], "universal_label": "ξ",
                "region_text": _venn_region_text(universal, a_set, b_set),
            },
        ),
    )


_CATEGORY_CONTEXTS = [
    ("shirts", "pairs of trousers", "pairs of shoes"),
    ("starters", "main courses", "desserts"),
    ("phone cases", "screen protectors", "chargers"),
    ("fonts", "colours", "paper sizes"),
]


def generate_product_rule_counting(tier: Tier, rng: random.Random) -> Question:
    labels = rng.choice(_CATEGORY_CONTEXTS)
    n_categories = rng.choice([2, 3])
    used_labels = labels[:n_categories]
    counts = [rng.randint(2, 6) for _ in used_labels]

    formula_total = 1
    for count in counts:
        formula_total *= count

    # Independent check: brute-force enumeration of the full Cartesian
    # product of choices - a different method than multiplying the counts.
    brute_total = len(list(itertools.product(*[range(count) for count in counts])))
    if brute_total != formula_total:
        raise ValueError("product_rule_counting verification failed")

    parts = [f"{count} different {label}" for count, label in zip(counts, used_labels)]
    prompt = (
        f"A shop sells {', '.join(parts[:-1])} and {parts[-1]}. Use the product rule for counting to find how "
        "many different combinations are possible, choosing exactly one of each."
    )
    steps = ["Total combinations = " + " × ".join(str(count) for count in counts) + f" = {formula_total}"]
    return Question(
        topic_id="product_rule_counting",
        tier=Tier.HIGHER,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=str(formula_total),
        dedup_key=f"product_rule:{used_labels}:{counts}",
    )


def generate_modelled_example_product_rule_counting(tier: Tier, rng: random.Random) -> ModelledExample:
    labels = rng.choice(_CATEGORY_CONTEXTS)
    n_categories = rng.choice([2, 3])
    used_labels = labels[:n_categories]
    counts = [rng.randint(2, 6) for _ in used_labels]

    formula_total = 1
    for count in counts:
        formula_total *= count

    # Independent check: brute-force enumeration of the full Cartesian
    # product of choices - a different method than multiplying the counts.
    brute_total = len(list(itertools.product(*[range(count) for count in counts])))
    if brute_total != formula_total:
        raise ValueError("modelled example product_rule_counting verification failed")

    parts = [f"{count} different {label}" for count, label in zip(counts, used_labels)]
    prompt = (
        f"A shop sells {', '.join(parts[:-1])} and {parts[-1]}. Use the product rule for counting to find how "
        "many different combinations are possible, choosing exactly one of each."
    )

    teaching_steps = [
        "When you're making a sequence of independent choices - one from each category - and you want to "
        "count every possible combination, the product rule says: multiply the number of options in each "
        "category together.",
        f"Here there are {n_categories} categories to choose from: " + ", ".join(used_labels) + ".",
        "For every single choice made in the first category, ALL of the choices in the second category are "
        "still available, and so on for a third category if there is one - which is exactly why "
        "multiplying (rather than adding) counts every combination.",
        "Total combinations = " + " × ".join(str(count) for count in counts) + f" = {formula_total}.",
    ]
    worked_calculation = [
        " × ".join(str(count) for count in counts),
        f"= {formula_total}",
    ]

    return ModelledExample(
        topic_id="product_rule_counting",
        tier=Tier.HIGHER,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=str(formula_total),
    )


_RELATIVE_FREQUENCY_CONTEXTS = [
    ("drawing pin", "lands point up"),
    ("spinner", "lands on red"),
    ("biased dice", "shows a six"),
    ("coin", "lands on heads"),
]


def _relative_frequency_diagram(item: str) -> DiagramSpec | None:
    """Purely illustrative - like the existing 'biased dice' diagram (always
    shows face 6 regardless of the real frequency numbers), this never
    determines the answer. The 'spinner' item's event text is always fixed
    ("lands on red"), so a fixed 4-sector layout with one highlighted sector
    is enough - no side-count needs deriving from anything."""
    if item == "biased dice":
        return DiagramSpec(kind="dice", params={"values": [6], "highlight": [0]})
    if item == "spinner":
        return DiagramSpec(kind="spinner", params={"sectors": ["", "", "R", ""], "highlight": [2]})
    return None


def generate_relative_frequency(tier: Tier, rng: random.Random) -> Question:
    item, event = rng.choice(_RELATIVE_FREQUENCY_CONTEXTS)
    trials = rng.choice([20, 40, 50, 80, 100, 200])
    frequency = rng.randint(1, trials - 1)
    relative_freq = Fraction(frequency, trials)
    future_trials = relative_freq.denominator * rng.randint(3, 15)
    expected = relative_freq * future_trials

    # Independent check: recompute the expected count via a Decimal division
    # instead of exact-Fraction multiplication - a different numeric
    # representation that must agree exactly.
    decimal_expected = (Decimal(frequency) / Decimal(trials)) * Decimal(future_trials)
    if Decimal(expected.numerator) != decimal_expected:
        raise ValueError("relative_frequency verification failed")

    steps = [
        f"Relative frequency = frequency ÷ number of trials = {frequency}/{trials} = "
        f"{relative_freq.numerator}/{relative_freq.denominator}",
        f"Estimated number of times in {future_trials} trials = {relative_freq.numerator}/{relative_freq.denominator} "
        f"× {future_trials} = {expected}",
    ]
    return Question(
        topic_id="relative_frequency",
        tier=Tier.FOUNDATION,
        prompt=(
            f"A {item} is tested {trials} times, and it {event} {frequency} times. Use this relative frequency "
            f"to estimate how many times this would happen in {future_trials} trials."
        ),
        solution_steps=tuple(steps),
        final_answer=str(int(expected)),
        dedup_key=f"relfreq:{item}:{event}:{trials}:{frequency}:{future_trials}",
        diagram=_relative_frequency_diagram(item),
    )


def generate_modelled_example_relative_frequency(tier: Tier, rng: random.Random) -> ModelledExample:
    item, event = rng.choice(_RELATIVE_FREQUENCY_CONTEXTS)
    trials = rng.choice([20, 40, 50, 80, 100, 200])
    frequency = rng.randint(1, trials - 1)
    relative_freq = Fraction(frequency, trials)
    future_trials = relative_freq.denominator * rng.randint(3, 15)
    expected = relative_freq * future_trials

    # Independent check: recompute the expected count via a Decimal division
    # instead of exact-Fraction multiplication - a different numeric
    # representation that must agree exactly.
    decimal_expected = (Decimal(frequency) / Decimal(trials)) * Decimal(future_trials)
    if Decimal(expected.numerator) != decimal_expected:
        raise ValueError("modelled example relative_frequency verification failed")

    teaching_steps = [
        "Relative frequency is an ESTIMATE of probability based on real experimental results, rather than "
        "a theoretical calculation - it's what actually happened when the trial was repeated.",
        f"Here the {item} {event} on {frequency} out of {trials} trials, so the relative frequency is "
        f"{frequency}/{trials} = {relative_freq.numerator}/{relative_freq.denominator}.",
        "Assuming the same relative frequency will continue to apply, we can use it to predict how many "
        f"times the event should happen in a different, larger number of trials ({future_trials}).",
        f"Multiply the relative frequency by the new number of trials: {relative_freq.numerator}/"
        f"{relative_freq.denominator} × {future_trials} = {expected}.",
    ]
    worked_calculation = [
        f"Relative frequency = {frequency}/{trials} = {relative_freq.numerator}/{relative_freq.denominator}",
        f"Estimate = {relative_freq.numerator}/{relative_freq.denominator} × {future_trials}",
        f"= {int(expected)}",
    ]

    return ModelledExample(
        topic_id="relative_frequency",
        tier=Tier.FOUNDATION,
        prompt=(
            f"A {item} is tested {trials} times, and it {event} {frequency} times. Use this relative "
            f"frequency to estimate how many times this would happen in {future_trials} trials."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=str(int(expected)),
        diagram=_relative_frequency_diagram(item),
    )


_TWO_WAY_ROW_LABELS = [("Boys", "Girls"), ("Year 10", "Year 11")]
_TWO_WAY_COL_LABELS = [("Football", "Tennis"), ("Cats", "Dogs"), ("Bus", "Walk")]


def generate_two_way_tables(tier: Tier, rng: random.Random) -> Question:
    row_labels = rng.choice(_TWO_WAY_ROW_LABELS)
    col_labels = rng.choice(_TWO_WAY_COL_LABELS)

    a, b, c, d = (rng.randint(4, 20) for _ in range(4))
    grid = [[a, b], [c, d]]
    row_totals = [a + b, c + d]
    col_totals = [a + c, b + d]
    grand_total = a + b + c + d

    # Independent check: the grand total from summing row totals must equal
    # the grand total from summing column totals - a different summation
    # order than the direct a + b + c + d used above.
    if sum(row_totals) != sum(col_totals) or sum(row_totals) != grand_total:
        raise ValueError("two_way_tables verification failed: totals do not reconcile")

    blanks = rng.sample([(0, 0), (0, 1), (1, 0), (1, 1)], 2)

    def _derive(r: int, cidx: int) -> tuple:
        # Recover the missing cell from whichever margin - its row total, or
        # its column total - has exactly one unknown cell in it. For any 2
        # distinct cells chosen from a 2x2 grid, at least one direction
        # always qualifies (both do for a diagonal pair).
        if sum(1 for (rr, _cc) in blanks if rr == r) == 1:
            other_c = 1 - cidx
            value = row_totals[r] - grid[r][other_c]
            desc = f"the '{row_labels[r]}' row total: {row_totals[r]} - {grid[r][other_c]} = {value}"
        else:
            other_r = 1 - r
            value = col_totals[cidx] - grid[other_r][cidx]
            desc = f"the '{col_labels[cidx]}' column total: {col_totals[cidx]} - {grid[other_r][cidx]} = {value}"
        return value, desc

    steps = []
    for r, cidx in blanks:
        value, desc = _derive(r, cidx)
        # Independent check: the value recovered from the margin totals
        # must match the true (known) grid value it was generated from.
        if value != grid[r][cidx]:
            raise ValueError("two_way_tables verification failed: blank cell not consistently recoverable")
        steps.append(f"'{row_labels[r]}' / '{col_labels[cidx]}': using {desc}")

    final_answer = "; ".join(f"'{row_labels[r]}' / '{col_labels[cidx]}' = {grid[r][cidx]}" for r, cidx in blanks)

    def cell_text(r: int, cidx: int) -> str:
        return "" if (r, cidx) in blanks else str(grid[r][cidx])

    display_cells = [
        [cell_text(0, 0), cell_text(0, 1), str(row_totals[0])],
        [cell_text(1, 0), cell_text(1, 1), str(row_totals[1])],
        [str(col_totals[0]), str(col_totals[1]), str(grand_total)],
    ]
    solved_cells = [
        [str(grid[0][0]), str(grid[0][1]), str(row_totals[0])],
        [str(grid[1][0]), str(grid[1][1]), str(row_totals[1])],
        [str(col_totals[0]), str(col_totals[1]), str(grand_total)],
    ]
    table_row_labels = [row_labels[0], row_labels[1], "Total"]
    table_col_labels = [col_labels[0], col_labels[1], "Total"]

    return Question(
        topic_id="two_way_tables",
        tier=Tier.FOUNDATION,
        prompt=(
            f"The two-way table shows the number of {row_labels[0].lower()} and {row_labels[1].lower()} who "
            f"prefer {col_labels[0].lower()} or {col_labels[1].lower()}. Find the missing values."
        ),
        solution_steps=tuple(steps),
        final_answer=final_answer,
        dedup_key=f"twoway:{row_labels}:{col_labels}:{a}:{b}:{c}:{d}:{sorted(blanks)}",
        diagram=DiagramSpec(
            kind="two_way_table",
            params={"row_labels": table_row_labels, "col_labels": table_col_labels, "cells": display_cells},
        ),
        solution_diagram=DiagramSpec(
            kind="two_way_table",
            params={"row_labels": table_row_labels, "col_labels": table_col_labels, "cells": solved_cells},
        ),
    )


def generate_modelled_example_two_way_tables(tier: Tier, rng: random.Random) -> ModelledExample:
    row_labels = rng.choice(_TWO_WAY_ROW_LABELS)
    col_labels = rng.choice(_TWO_WAY_COL_LABELS)

    a, b, c, d = (rng.randint(4, 20) for _ in range(4))
    grid = [[a, b], [c, d]]
    row_totals = [a + b, c + d]
    col_totals = [a + c, b + d]
    grand_total = a + b + c + d

    # Independent check: the grand total from summing row totals must equal
    # the grand total from summing column totals - a different summation
    # order than the direct a + b + c + d used above.
    if sum(row_totals) != sum(col_totals) or sum(row_totals) != grand_total:
        raise ValueError("modelled example two_way_tables verification failed: totals do not reconcile")

    blanks = rng.sample([(0, 0), (0, 1), (1, 0), (1, 1)], 2)

    def _derive(r: int, cidx: int) -> tuple:
        if sum(1 for (rr, _cc) in blanks if rr == r) == 1:
            other_c = 1 - cidx
            value = row_totals[r] - grid[r][other_c]
            desc = (
                f"the '{row_labels[r]}' row totals {row_totals[r]}, and the other entry in that row is "
                f"{grid[r][other_c]}, so {row_totals[r]} - {grid[r][other_c]} = {value}"
            )
        else:
            other_r = 1 - r
            value = col_totals[cidx] - grid[other_r][cidx]
            desc = (
                f"the '{col_labels[cidx]}' column totals {col_totals[cidx]}, and the other entry in that "
                f"column is {grid[other_r][cidx]}, so {col_totals[cidx]} - {grid[other_r][cidx]} = {value}"
            )
        return value, desc

    worked_calculation = []
    teaching_steps = [
        "A two-way table organises data by two categories at once - here, by "
        f"{row_labels[0].lower()}/{row_labels[1].lower()} and by {col_labels[0].lower()}/{col_labels[1].lower()} "
        "- with row and column totals along the edges as a built-in check.",
        "Every row must add up to its row total, and every column must add up to its column total - work out "
        "each missing value from whichever total (row or column) has only that one unknown in it.",
    ]
    for r, cidx in blanks:
        value, desc = _derive(r, cidx)
        # Independent check: the value recovered from the margin totals
        # must match the true (known) grid value it was generated from.
        if value != grid[r][cidx]:
            raise ValueError(
                "modelled example two_way_tables verification failed: blank cell not consistently recoverable"
            )
        teaching_steps.append(f"For '{row_labels[r]}' / '{col_labels[cidx]}': {desc}.")
        worked_calculation.append(f"'{row_labels[r]}' / '{col_labels[cidx]}' = {value}")

    solved_cells = [
        [str(grid[0][0]), str(grid[0][1]), str(row_totals[0])],
        [str(grid[1][0]), str(grid[1][1]), str(row_totals[1])],
        [str(col_totals[0]), str(col_totals[1]), str(grand_total)],
    ]
    table_row_labels = [row_labels[0], row_labels[1], "Total"]
    table_col_labels = [col_labels[0], col_labels[1], "Total"]
    final_answer = "; ".join(f"'{row_labels[r]}' / '{col_labels[cidx]}' = {grid[r][cidx]}" for r, cidx in blanks)

    return ModelledExample(
        topic_id="two_way_tables",
        tier=Tier.FOUNDATION,
        prompt=(
            f"The two-way table shows the number of {row_labels[0].lower()} and {row_labels[1].lower()} who "
            f"prefer {col_labels[0].lower()} or {col_labels[1].lower()}. Find the missing values."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=final_answer,
        diagram=DiagramSpec(
            kind="two_way_table",
            params={"row_labels": table_row_labels, "col_labels": table_col_labels, "cells": solved_cells},
        ),
    )


def generate_sample_space_diagrams(tier: Tier, rng: random.Random) -> Question:
    faces1 = rng.choice([4, 6])
    faces2 = rng.choice([4, 6])
    op = rng.choice(["sum", "product"])
    rows = list(range(1, faces1 + 1))
    cols = list(range(1, faces2 + 1))

    if op == "sum":
        grid = [[r + c for c in cols] for r in rows]
    else:
        grid = [[r * c for c in cols] for r in rows]

    all_indices = [(r, c) for r in range(faces1) for c in range(faces2)]
    values = sorted({grid[r][c] for r, c in all_indices})
    event_kind = rng.choice(["equals", "greater_than", "even"])
    target = None

    if event_kind == "equals":
        target = rng.choice(values)
        matches = [(r, c) for r, c in all_indices if grid[r][c] == target]
        event_desc = f"the {op} is {target}"
    elif event_kind == "greater_than":
        target = rng.choice(values[:-1]) if len(values) > 1 else values[0]
        matches = [(r, c) for r, c in all_indices if grid[r][c] > target]
        event_desc = f"the {op} is greater than {target}"
    else:
        matches = [(r, c) for r, c in all_indices if grid[r][c] % 2 == 0]
        event_desc = f"the {op} is even"

    formula_prob = Fraction(len(matches), len(all_indices))

    # Independent check: recount favourable outcomes by scanning the
    # flattened grid values directly - a different traversal than the
    # (row, col) index-based enumeration used to build `matches` above.
    flat_values = [v for row in grid for v in row]
    if event_kind == "equals":
        brute_count = sum(1 for v in flat_values if v == target)
    elif event_kind == "greater_than":
        brute_count = sum(1 for v in flat_values if v > target)
    else:
        brute_count = sum(1 for v in flat_values if v % 2 == 0)
    brute_prob = Fraction(brute_count, len(flat_values))
    if brute_prob != formula_prob:
        raise ValueError("sample_space_diagrams verification failed")

    highlight = [[r, c] for r, c in matches]
    steps = [
        f"The sample space diagram shows every possible {op} of the two spinners.",
        f"Number of favourable outcomes ({event_desc}) = {len(matches)}",
        f"Total number of equally likely outcomes = {len(all_indices)}",
        f"P({event_desc}) = {formula_prob.numerator}/{formula_prob.denominator}",
    ]
    return Question(
        topic_id="sample_space_diagrams",
        tier=Tier.FOUNDATION,
        prompt=(
            f"Two fair spinners, one numbered 1 to {faces1} and the other numbered 1 to {faces2}, are spun "
            f"together. Complete the sample space diagram showing the {op} of the two spinners, and use it to "
            f"find the probability that {event_desc}."
        ),
        solution_steps=tuple(steps),
        final_answer=f"{formula_prob.numerator}/{formula_prob.denominator}",
        dedup_key=f"samplespace:{faces1}:{faces2}:{op}:{event_kind}:{target}",
        diagram=DiagramSpec(
            kind="sample_space_diagram",
            params={
                "row_values": rows, "col_values": cols,
                "cells": [["" for _ in row] for row in grid],
            },
        ),
        solution_diagram=DiagramSpec(
            kind="sample_space_diagram",
            params={
                "row_values": rows, "col_values": cols,
                "cells": [[str(v) for v in row] for row in grid],
                "highlight": highlight,
            },
        ),
    )


def generate_modelled_example_sample_space_diagrams(tier: Tier, rng: random.Random) -> ModelledExample:
    faces1 = rng.choice([4, 6])
    faces2 = rng.choice([4, 6])
    op = rng.choice(["sum", "product"])
    rows = list(range(1, faces1 + 1))
    cols = list(range(1, faces2 + 1))

    if op == "sum":
        grid = [[r + c for c in cols] for r in rows]
    else:
        grid = [[r * c for c in cols] for r in rows]

    all_indices = [(r, c) for r in range(faces1) for c in range(faces2)]
    values = sorted({grid[r][c] for r, c in all_indices})
    event_kind = rng.choice(["equals", "greater_than", "even"])
    target = None

    if event_kind == "equals":
        target = rng.choice(values)
        matches = [(r, c) for r, c in all_indices if grid[r][c] == target]
        event_desc = f"the {op} is {target}"
    elif event_kind == "greater_than":
        target = rng.choice(values[:-1]) if len(values) > 1 else values[0]
        matches = [(r, c) for r, c in all_indices if grid[r][c] > target]
        event_desc = f"the {op} is greater than {target}"
    else:
        matches = [(r, c) for r, c in all_indices if grid[r][c] % 2 == 0]
        event_desc = f"the {op} is even"

    formula_prob = Fraction(len(matches), len(all_indices))

    # Independent check: recount favourable outcomes by scanning the
    # flattened grid values directly - a different traversal than the
    # (row, col) index-based enumeration used to build `matches` above.
    flat_values = [v for row in grid for v in row]
    if event_kind == "equals":
        brute_count = sum(1 for v in flat_values if v == target)
    elif event_kind == "greater_than":
        brute_count = sum(1 for v in flat_values if v > target)
    else:
        brute_count = sum(1 for v in flat_values if v % 2 == 0)
    brute_prob = Fraction(brute_count, len(flat_values))
    if brute_prob != formula_prob:
        raise ValueError("modelled example sample_space_diagrams verification failed")

    highlight = [[r, c] for r, c in matches]
    teaching_steps = [
        f"A sample space diagram lists every possible {op} of the two spinners in a grid, so you can see "
        "the whole set of equally likely outcomes at once instead of trying to list them in your head.",
        f"There are {faces1} × {faces2} = {len(all_indices)} cells in the grid altogether, and each one is "
        "equally likely because both spinners are fair.",
        f"Shade or circle every cell where {event_desc} - counting {len(matches)} such cells here - these "
        "are the favourable outcomes.",
        f"P({event_desc}) = favourable ÷ total = {len(matches)}/{len(all_indices)} = "
        f"{formula_prob.numerator}/{formula_prob.denominator}.",
    ]
    worked_calculation = [
        f"Favourable outcomes ({event_desc}) = {len(matches)}",
        f"Total outcomes = {len(all_indices)}",
        f"P = {len(matches)}/{len(all_indices)} = {formula_prob.numerator}/{formula_prob.denominator}",
    ]

    return ModelledExample(
        topic_id="sample_space_diagrams",
        tier=Tier.FOUNDATION,
        prompt=(
            f"Two fair spinners, one numbered 1 to {faces1} and the other numbered 1 to {faces2}, are spun "
            f"together. Complete the sample space diagram showing the {op} of the two spinners, and use it "
            f"to find the probability that {event_desc}."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{formula_prob.numerator}/{formula_prob.denominator}",
        diagram=DiagramSpec(
            kind="sample_space_diagram",
            params={
                "row_values": rows, "col_values": cols,
                "cells": [[str(v) for v in row] for row in grid],
                "highlight": highlight,
            },
        ),
    )


TOPIC_SET_NOTATION = TopicDefinition(
    id="set_notation",
    display_name="Set Notation",
    description="Use set notation (union, intersection, complement) to list elements of a set.",
    generate=generate_set_notation,
    section=SECTION,
    group=GROUP_COUNTING,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_set_notation,
)

TOPIC_SET_NOTATION_FOUNDATION = TopicDefinition(
    id="set_notation_foundation",
    display_name="Sets (Foundation)",
    description="List the elements of a set described in plain English, using a Venn-diagram style rule.",
    generate=generate_set_notation_foundation,
    section=SECTION,
    group=GROUP_COUNTING,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_set_notation_foundation,
)

TOPIC_PRODUCT_RULE_COUNTING = TopicDefinition(
    id="product_rule_counting",
    display_name="Product Rule for Counting",
    description="Use the product rule for counting to find the number of possible combinations.",
    generate=generate_product_rule_counting,
    section=SECTION,
    group=GROUP_COUNTING,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_product_rule_counting,
)

TOPIC_RELATIVE_FREQUENCY = TopicDefinition(
    id="relative_frequency",
    display_name="Relative Frequency",
    description="Use relative frequency from a set of trials to estimate the probability of an event.",
    generate=generate_relative_frequency,
    section=SECTION,
    group=GROUP_DATA,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_relative_frequency,
)

TOPIC_TWO_WAY_TABLES = TopicDefinition(
    id="two_way_tables",
    display_name="Two-Way Tables",
    description="Interpret and complete a two-way table using row and column totals.",
    generate=generate_two_way_tables,
    section=SECTION,
    group=GROUP_DATA,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_two_way_tables,
)

TOPIC_SAMPLE_SPACE_DIAGRAMS = TopicDefinition(
    id="sample_space_diagrams",
    display_name="Sample Space Diagrams",
    description="Use a sample space diagram to find the probability of a combined event.",
    generate=generate_sample_space_diagrams,
    section=SECTION,
    group=GROUP_DATA,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_sample_space_diagrams,
)
