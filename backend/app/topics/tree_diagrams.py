import itertools
import random
from fractions import Fraction

from app.core.models import DiagramSpec, Question, Tier
from app.topics.base import TopicDefinition

SECTION = "probability"
GROUP = "Tree Diagrams"

COLOURS = ["red", "blue", "green", "yellow"]
TREE_DRAWING_QUESTION_COUNT = 5


def _frac_str(f: Fraction) -> str:
    return f"{f.numerator}/{f.denominator}"


def generate_tree_diagram_independent(tier: Tier, rng: random.Random) -> Question:
    c1, c2 = rng.sample(COLOURS, 2)
    n1 = rng.randint(2, 8)
    n2 = rng.randint(2, 8)
    total = n1 + n2
    p1, p2 = Fraction(n1, total), Fraction(n2, total)

    event = rng.choice(["same", "sequence"])
    items = [c1] * n1 + [c2] * n2
    sample = list(itertools.product(items, items))

    if event == "same":
        formula_prob = p1 * p1 + p2 * p2
        matches = [o for o in sample if o[0] == o[1]]
        prompt_event = "both counters are the same colour"
        steps_extra = [
            f"P(both {c1}) = {_frac_str(p1)} × {_frac_str(p1)} = {_frac_str(p1 * p1)}",
            f"P(both {c2}) = {_frac_str(p2)} × {_frac_str(p2)} = {_frac_str(p2 * p2)}",
            f"P(same colour) = {_frac_str(p1 * p1)} + {_frac_str(p2 * p2)} = {_frac_str(formula_prob)}",
        ]
    else:
        first, second = rng.choice([(c1, c2), (c2, c1), (c1, c1), (c2, c2)])
        p_first = p1 if first == c1 else p2
        p_second = p1 if second == c1 else p2
        formula_prob = p_first * p_second
        matches = [o for o in sample if o[0] == first and o[1] == second]
        prompt_event = f"the first counter is {first} and the second counter is {second}"
        steps_extra = [
            f"P({first} then {second}) = {_frac_str(p_first)} × {_frac_str(p_second)} = {_frac_str(formula_prob)}",
        ]

    # Independent check: brute-force count over every physically-labelled
    # pair of picks (with replacement) - a different method than the
    # branch-probability multiplication used to build the tree above.
    brute_prob = Fraction(len(matches), len(sample))
    if brute_prob != formula_prob:
        raise ValueError("tree_diagram_independent verification failed")

    stage1 = [(c1.title(), _frac_str(p1)), (c2.title(), _frac_str(p2))]
    stage2 = [
        [(c1.title(), _frac_str(p1)), (c2.title(), _frac_str(p2))],
        [(c1.title(), _frac_str(p1)), (c2.title(), _frac_str(p2))],
    ]

    steps = [
        f"A counter is picked, replaced, then a second counter is picked. The probabilities stay the same "
        f"each time: P({c1}) = {_frac_str(p1)}, P({c2}) = {_frac_str(p2)}.",
        *steps_extra,
    ]
    return Question(
        topic_id="tree_diagram_independent",
        tier=Tier.FOUNDATION,
        prompt=(
            f"A bag contains {n1} {c1} and {n2} {c2} counters. A counter is picked at random, replaced, and "
            f"then a second counter is picked at random. The tree diagram shows this information. "
            f"Find the probability that {prompt_event}."
        ),
        solution_steps=tuple(steps),
        final_answer=_frac_str(formula_prob),
        dedup_key=f"tree_indep:{c1}:{c2}:{n1}:{n2}:{event}:{prompt_event}",
        diagram=DiagramSpec(kind="tree_diagram", params={"stage1": stage1, "stage2": stage2}),
    )


def generate_tree_diagram_dependent(tier: Tier, rng: random.Random) -> Question:
    c1, c2 = rng.sample(COLOURS, 2)
    n1 = rng.randint(3, 8)
    n2 = rng.randint(3, 8)
    total = n1 + n2

    p1, p2 = Fraction(n1, total), Fraction(n2, total)
    p1_given1 = Fraction(n1 - 1, total - 1)
    p2_given1 = Fraction(n2, total - 1)
    p1_given2 = Fraction(n1, total - 1)
    p2_given2 = Fraction(n2 - 1, total - 1)

    event = rng.choice(["same", "different", "sequence"])
    labels = [c1] * n1 + [c2] * n2
    ordered_pairs = list(itertools.permutations(range(total), 2))

    def outcome(i: int, j: int) -> tuple[str, str]:
        return (labels[i], labels[j])

    if event == "same":
        formula_prob = p1 * p1_given1 + p2 * p2_given2
        matches = [1 for i, j in ordered_pairs if outcome(i, j)[0] == outcome(i, j)[1]]
        prompt_event = "both counters are the same colour"
    elif event == "different":
        formula_prob = p1 * p2_given1 + p2 * p1_given2
        matches = [1 for i, j in ordered_pairs if outcome(i, j)[0] != outcome(i, j)[1]]
        prompt_event = "the two counters are different colours"
    else:
        first, second = rng.choice([(c1, c2), (c2, c1), (c1, c1), (c2, c2)])
        if (first, second) == (c1, c2):
            formula_prob = p1 * p2_given1
        elif (first, second) == (c2, c1):
            formula_prob = p2 * p1_given2
        elif (first, second) == (c1, c1):
            formula_prob = p1 * p1_given1
        else:
            formula_prob = p2 * p2_given2
        matches = [1 for i, j in ordered_pairs if outcome(i, j) == (first, second)]
        prompt_event = f"the first counter is {first} and the second counter is {second}"

    # Independent check: brute-force count over every ordered pair of
    # distinct physical counters (without replacement) - a different method
    # than the branch-probability multiplication used to build the tree.
    brute_prob = Fraction(len(matches), len(ordered_pairs))
    if brute_prob != formula_prob:
        raise ValueError("tree_diagram_dependent verification failed")

    stage1 = [(c1.title(), _frac_str(p1)), (c2.title(), _frac_str(p2))]
    stage2 = [
        [(c1.title(), _frac_str(p1_given1)), (c2.title(), _frac_str(p2_given1))],
        [(c1.title(), _frac_str(p1_given2)), (c2.title(), _frac_str(p2_given2))],
    ]
    leaf_probs = [
        [_frac_str(p1 * p1_given1), _frac_str(p1 * p2_given1)],
        [_frac_str(p2 * p1_given2), _frac_str(p2 * p2_given2)],
    ]

    steps = [
        f"After the first counter is picked (without replacement), there are {total - 1} counters left.",
        f"P({c1} then {c1}) = {_frac_str(p1)} × {_frac_str(p1_given1)} = {_frac_str(p1 * p1_given1)}",
        f"P({c1} then {c2}) = {_frac_str(p1)} × {_frac_str(p2_given1)} = {_frac_str(p1 * p2_given1)}",
        f"P({c2} then {c1}) = {_frac_str(p2)} × {_frac_str(p1_given2)} = {_frac_str(p2 * p1_given2)}",
        f"P({c2} then {c2}) = {_frac_str(p2)} × {_frac_str(p2_given2)} = {_frac_str(p2 * p2_given2)}",
        f"P({prompt_event}) = {_frac_str(formula_prob)}",
    ]
    return Question(
        topic_id="tree_diagram_dependent",
        tier=Tier.HIGHER,
        prompt=(
            f"A bag contains {n1} {c1} and {n2} {c2} counters. Two counters are picked at random, one after "
            f"the other, without replacement. The tree diagram shows this information. "
            f"Find the probability that {prompt_event}."
        ),
        solution_steps=tuple(steps),
        final_answer=_frac_str(formula_prob),
        dedup_key=f"tree_dep:{c1}:{c2}:{n1}:{n2}:{event}:{prompt_event}",
        diagram=DiagramSpec(
            kind="tree_diagram", params={"stage1": stage1, "stage2": stage2, "leaf_probs": leaf_probs}
        ),
    )


def generate_tree_diagram_drawing(tier: Tier, rng: random.Random) -> Question:
    c1, c2 = rng.sample(COLOURS, 2)
    n1 = rng.randint(2, 8)
    n2 = rng.randint(2, 8)
    total = n1 + n2
    p1, p2 = Fraction(n1, total), Fraction(n2, total)

    target_first, target_second = rng.choice([(c1, c1), (c1, c2), (c2, c1), (c2, c2)])
    p_first = p1 if target_first == c1 else p2
    p_second = p1 if target_second == c1 else p2
    formula_prob = p_first * p_second

    # Independent check: brute-force count over every physically-labelled
    # pair of picks (with replacement) - a different method than the
    # branch-probability multiplication used above.
    items = [c1] * n1 + [c2] * n2
    sample = list(itertools.product(items, items))
    matches = [o for o in sample if o == (target_first, target_second)]
    brute_prob = Fraction(len(matches), len(sample))
    if brute_prob != formula_prob:
        raise ValueError("tree_diagram_drawing verification failed")

    stage1 = [(c1.title(), _frac_str(p1)), (c2.title(), _frac_str(p2))]
    stage2 = [
        [(c1.title(), _frac_str(p1)), (c2.title(), _frac_str(p2))],
        [(c1.title(), _frac_str(p1)), (c2.title(), _frac_str(p2))],
    ]

    steps = [
        f"Draw two branches from the start: P({c1}) = {_frac_str(p1)}, P({c2}) = {_frac_str(p2)}.",
        "From each of those branches, draw two more with the same probabilities (the counter is replaced).",
        f"P({target_first} then {target_second}) = {_frac_str(p_first)} × {_frac_str(p_second)} = "
        f"{_frac_str(formula_prob)}",
    ]
    return Question(
        topic_id="tree_diagram_drawing",
        tier=Tier.FOUNDATION,
        prompt=(
            f"A bag contains {n1} {c1} and {n2} {c2} counters. A counter is picked at random, replaced, and "
            f"then a second counter is picked at random. Draw a fully-labelled tree diagram to show this "
            f"information, and use it to find the probability that the first counter is {target_first} and "
            f"the second counter is {target_second}."
        ),
        solution_steps=tuple(steps),
        final_answer=_frac_str(formula_prob),
        dedup_key=f"tree_draw:{c1}:{c2}:{n1}:{n2}:{target_first}:{target_second}",
        solution_diagram=DiagramSpec(kind="tree_diagram", params={"stage1": stage1, "stage2": stage2}),
    )


TOPIC_TREE_INDEPENDENT = TopicDefinition(
    id="tree_diagram_independent",
    display_name="Interpreting Tree Diagrams (Independent Events)",
    description="Use a tree diagram to find probabilities when events are independent (with replacement).",
    generate=generate_tree_diagram_independent,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
)

TOPIC_TREE_DEPENDENT = TopicDefinition(
    id="tree_diagram_dependent",
    display_name="Interpreting Tree Diagrams (Dependent Events)",
    description="Use a tree diagram to find probabilities when events are dependent (without replacement).",
    generate=generate_tree_diagram_dependent,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
)

TOPIC_TREE_DRAWING = TopicDefinition(
    id="tree_diagram_drawing",
    display_name="Drawing Tree Diagrams",
    description="Draw a fully-labelled tree diagram from a description, then use it to find a probability. (5 questions)",
    generate=generate_tree_diagram_drawing,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    question_count=TREE_DRAWING_QUESTION_COUNT,
)
