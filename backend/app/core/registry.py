from dataclasses import dataclass

from app.core.errors import TopicNotFoundError
from app.topics import (
    angles,
    area_perimeter,
    circle_theorems,
    data_handling,
    decimals,
    estimation,
    expand_factorise,
    fractions,
    functions,
    graphs,
    linear_equations,
    negative_numbers,
    number_theory,
    percentages,
    powers_roots,
    probability,
    pythagoras,
    quadratic_graphs,
    ratio,
    sequences,
    simultaneous_equations,
    standard_form,
    tree_diagrams,
    triangle_rules,
    trigonometry,
    vectors,
)
from app.topics import statistics as statistics_topics
from app.topics.base import TopicDefinition

SECTIONS: list[tuple[str, str]] = [
    ("number", "Number"),
    ("algebra", "Algebra"),
    ("ratio_proportion", "Ratio & Proportion"),
    ("geometry", "Geometry"),
    ("probability", "Probability"),
    ("statistics", "Statistics"),
]

_TOPIC_LIST: list[TopicDefinition] = [
    # Number
    fractions.TOPIC_SIMPLIFY,
    fractions.TOPIC_ADD_SUBTRACT,
    fractions.TOPIC_MULTIPLY,
    fractions.TOPIC_DIVIDE,
    fractions.TOPIC_DIVIDE_FOUNDATION,
    fractions.TOPIC_MIXED_NUMBER_ARITHMETIC,
    fractions.TOPIC_OF_AMOUNT,
    decimals.TOPIC_ROUND_DP,
    decimals.TOPIC_ROUND_SF,
    decimals.TOPIC_ORDERING,
    decimals.TOPIC_RECURRING_TO_FRACTION,
    decimals.TOPIC_DIVIDE,
    standard_form.TOPIC_TO_STANDARD_FORM,
    standard_form.TOPIC_FROM_STANDARD_FORM,
    standard_form.TOPIC_MULTIPLY_DIVIDE,
    standard_form.TOPIC_MULTIPLY_DIVIDE_FOUNDATION,
    standard_form.TOPIC_ADD_SUBTRACT,
    estimation.TOPIC_ESTIMATION,
    estimation.TOPIC_ERROR_INTERVAL,
    estimation.TOPIC_BOUNDS,
    negative_numbers.TOPIC_NEGATIVE_NUMBERS,
    decimals.TOPIC_POWERS_OF_TEN,
    number_theory.TOPIC_PRIME_NUMBERS,
    number_theory.TOPIC_MULTIPLES,
    number_theory.TOPIC_FACTORS,
    number_theory.TOPIC_PRIME_FACTORS_FOUNDATION,
    number_theory.TOPIC_PRIME_FACTORS_HIGHER,
    number_theory.TOPIC_LCM_BY_LISTING,
    number_theory.TOPIC_HCF_BY_LISTING,
    number_theory.TOPIC_HCF_LCM_BY_PRIME_FACTORS,
    powers_roots.TOPIC_POWERS_FOUNDATION,
    powers_roots.TOPIC_POWERS_HIGHER,
    powers_roots.TOPIC_ROOTS_FOUNDATION,
    powers_roots.TOPIC_ROOTS_HIGHER,
    # Algebra
    linear_equations.TOPIC_ONE_STEP,
    linear_equations.TOPIC_TWO_STEP,
    linear_equations.TOPIC_MULTI_STEP,
    linear_equations.TOPIC_BOTH_SIDES_FOUNDATION,
    linear_equations.TOPIC_BOTH_SIDES,
    linear_equations.TOPIC_BRACKETS_FOUNDATION,
    linear_equations.TOPIC_BRACKETS,
    expand_factorise.TOPIC_EXPAND_SINGLE,
    expand_factorise.TOPIC_EXPAND_DOUBLE_FOUNDATION,
    expand_factorise.TOPIC_EXPAND_DOUBLE,
    expand_factorise.TOPIC_EXPAND_TRIPLE,
    expand_factorise.TOPIC_FACTORISE_COMMON,
    expand_factorise.TOPIC_FACTORISE_QUADRATIC_FOUNDATION,
    expand_factorise.TOPIC_FACTORISE_QUADRATIC,
    quadratic_graphs.TOPIC_COMPLETING_THE_SQUARE,
    quadratic_graphs.TOPIC_TURNING_POINT,
    functions.TOPIC_FUNCTIONS_EVALUATE,
    functions.TOPIC_FUNCTIONS_COMPOSITE_INVERSE,
    simultaneous_equations.TOPIC_COMMON_COEFFICIENT,
    simultaneous_equations.TOPIC_DIFFERENT_COEFFICIENT,
    simultaneous_equations.TOPIC_FORMING_AND_SOLVING,
    simultaneous_equations.TOPIC_QUADRATIC,
    simultaneous_equations.TOPIC_GRAPHICALLY,
    sequences.TOPIC_NEXT_TERM,
    sequences.TOPIC_TERM_TO_TERM_RULE,
    sequences.TOPIC_NTH_TERM,
    sequences.TOPIC_QUADRATIC_NTH_TERM,
    graphs.TOPIC_PLOT_STRAIGHT_LINE,
    graphs.TOPIC_PLOT_QUADRATIC,
    graphs.TOPIC_PLOT_CUBIC,
    graphs.TOPIC_PLOT_RECIPROCAL,
    graphs.TOPIC_PLOT_DISTANCE_TIME,
    graphs.TOPIC_LINE_EQUATION_FROM_GRAPH,
    graphs.TOPIC_PARALLEL_LINES_EQUATION,
    graphs.TOPIC_PERPENDICULAR_LINES_EQUATION,
    graphs.TOPIC_DISTANCE_TIME_INTERPRET,
    graphs.TOPIC_VELOCITY_TIME_INTERPRET,
    graphs.TOPIC_GRAPH_TRANSFORMATIONS,
    # Ratio & Proportion
    percentages.TOPIC_OF_AMOUNT,
    percentages.TOPIC_CHANGE,
    percentages.TOPIC_REVERSE_FOUNDATION,
    percentages.TOPIC_REVERSE,
    percentages.TOPIC_COMPOUND,
    percentages.TOPIC_COMPOUND_FOUNDATION,
    ratio.TOPIC_SHARE_TWO,
    ratio.TOPIC_FIND_SHARE,
    ratio.TOPIC_SHARE_THREE,
    ratio.TOPIC_SHARE_THREE_FOUNDATION,
    ratio.TOPIC_COMBINE,
    # Geometry
    area_perimeter.TOPIC_RECTANGLE,
    area_perimeter.TOPIC_TRIANGLE,
    area_perimeter.TOPIC_COMPOSITE_RECTANGLES,
    area_perimeter.TOPIC_CIRCLE_FOUNDATION,
    area_perimeter.TOPIC_CIRCLE,
    area_perimeter.TOPIC_SEMICIRCLE_COMPOUND,
    area_perimeter.TOPIC_SEMICIRCLE_COMPOUND_HIGHER,
    area_perimeter.TOPIC_SUBTRACT_COMPOUND,
    area_perimeter.TOPIC_SUBTRACT_COMPOUND_FOUNDATION,
    angles.TOPIC_STRAIGHT_LINE,
    angles.TOPIC_STRAIGHT_LINE_HIGHER,
    angles.TOPIC_AROUND_POINT,
    angles.TOPIC_AROUND_POINT_HIGHER,
    angles.TOPIC_TRIANGLE,
    angles.TOPIC_TRIANGLE_HIGHER,
    angles.TOPIC_PARALLEL_LINES_FOUNDATION,
    angles.TOPIC_PARALLEL_LINES,
    angles.TOPIC_EXTERIOR_FOUNDATION,
    angles.TOPIC_EXTERIOR,
    angles.TOPIC_POLYGON_INTERIOR_FOUNDATION,
    angles.TOPIC_POLYGON_INTERIOR,
    pythagoras.TOPIC_HYPOTENUSE_TRIPLE,
    pythagoras.TOPIC_HYPOTENUSE_DECIMAL,
    pythagoras.TOPIC_SHORTER_LEG,
    pythagoras.TOPIC_SURD_HYPOTENUSE,
    pythagoras.TOPIC_LADDER_CONTEXT,
    pythagoras.TOPIC_LADDER_CONTEXT_FOUNDATION,
    trigonometry.TOPIC_MISSING_SIDE_FOUNDATION,
    trigonometry.TOPIC_MISSING_SIDE_HIGHER,
    trigonometry.TOPIC_MISSING_ANGLE_FOUNDATION,
    trigonometry.TOPIC_MISSING_ANGLE_HIGHER,
    trigonometry.TOPIC_MIXED,
    triangle_rules.TOPIC_SINE_RULE,
    triangle_rules.TOPIC_COSINE_RULE,
    triangle_rules.TOPIC_TRIANGLE_AREA,
    vectors.TOPIC_VECTORS_ARITHMETIC_FOUNDATION,
    vectors.TOPIC_VECTORS_ARITHMETIC_HIGHER,
    vectors.TOPIC_GEOMETRIC_VECTORS,
    circle_theorems.TOPIC_CIRCLE_THEOREMS,
    # Probability
    probability.TOPIC_SINGLE_EVENT,
    probability.TOPIC_COMPLEMENT,
    probability.TOPIC_COMBINED_DICE,
    probability.TOPIC_CONDITIONAL,
    tree_diagrams.TOPIC_TREE_INDEPENDENT,
    tree_diagrams.TOPIC_TREE_DEPENDENT,
    tree_diagrams.TOPIC_TREE_DRAWING,
    data_handling.TOPIC_SET_NOTATION,
    data_handling.TOPIC_SET_NOTATION_FOUNDATION,
    data_handling.TOPIC_PRODUCT_RULE_COUNTING,
    data_handling.TOPIC_RELATIVE_FREQUENCY,
    data_handling.TOPIC_TWO_WAY_TABLES,
    data_handling.TOPIC_SAMPLE_SPACE_DIAGRAMS,
    # Statistics
    statistics_topics.TOPIC_MEAN_AND_RANGE,
    statistics_topics.TOPIC_MEDIAN_AND_MODE,
    statistics_topics.TOPIC_MEAN_FREQUENCY_TABLE,
    statistics_topics.TOPIC_MEAN_GROUPED_FREQUENCY_TABLE,
    statistics_topics.TOPIC_MEAN_GROUPED_FREQUENCY_TABLE_FOUNDATION,
    statistics_topics.TOPIC_REVERSE_MEAN,
    statistics_topics.TOPIC_REVERSE_MEAN_FOUNDATION,
]

TOPICS: dict[str, TopicDefinition] = {t.id: t for t in _TOPIC_LIST}


def get_topic(topic_id: str) -> TopicDefinition:
    try:
        return TOPICS[topic_id]
    except KeyError:
        raise TopicNotFoundError(topic_id) from None


def list_topics() -> list[TopicDefinition]:
    return list(_TOPIC_LIST)


@dataclass(frozen=True)
class GroupNode:
    name: str
    topics: tuple[TopicDefinition, ...]


@dataclass(frozen=True)
class SectionNode:
    id: str
    name: str
    groups: tuple[GroupNode, ...]


def sections_tree() -> list[SectionNode]:
    """Group all topics by section then by group, preserving the declared
    order in SECTIONS and _TOPIC_LIST (not alphabetical). Sections with no
    topics yet (e.g. Number) are still included, with an empty groups tuple.
    """
    nodes: list[SectionNode] = []
    for section_id, section_name in SECTIONS:
        section_topics = [t for t in _TOPIC_LIST if t.section == section_id]

        group_order: list[str] = []
        group_topics: dict[str, list[TopicDefinition]] = {}
        for t in section_topics:
            if t.group not in group_topics:
                group_topics[t.group] = []
                group_order.append(t.group)
            group_topics[t.group].append(t)

        groups = tuple(GroupNode(name=g, topics=tuple(group_topics[g])) for g in group_order)
        nodes.append(SectionNode(id=section_id, name=section_name, groups=groups))
    return nodes
