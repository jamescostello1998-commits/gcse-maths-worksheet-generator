"""Scatter graphs and correlation (AQA 3.6 S6): a genuinely new diagram kind
(draw_scatter_graph, app/pdf/diagrams.py) built on the existing
_draw_stats_axes engine but plotting unconnected point markers (no PolyLine,
unlike draw_time_series/draw_cumulative_frequency) with an optional line of
best fit. Two topics: constructing a scatter graph from a data table (the
student draws it - no diagram on the question page, same pattern as
tree_diagram_drawing), and interpreting one that's already drawn with its
line of best fit (reading a value off the line, or stating the correlation
type).

Data is generated around a known straight line with random noise, then the
Pearson correlation coefficient of the actual (noisy) data is computed and
checked to genuinely match the intended correlation direction - rerolling
the noise if an unlucky draw flipped it, rather than just trusting the
construction. The "line of best fit" here is the known generating line
itself (GCSE questions give or ask you to draw one by eye, not compute an
exact regression), not a fitted line - stated up front so the modelled
example doesn't overclaim.
"""

import random

from app.core.models import DiagramSpec, ModelledExample, Question, Tier
from app.topics.base import TopicDefinition

SECTION = "statistics"
GROUP = "Charts and Graphs"

_CONTEXTS = (
    {"positive": True, "x_label": "Hours revised", "y_label": "Test score (%)",
     "x_range": (1, 10), "m": 6.5, "c": 25, "noise": 8,
     "context": "the number of hours a group of students revised for a test and their test score"},
    {"positive": True, "x_label": "Temperature (°C)", "y_label": "Ice creams sold",
     "x_range": (10, 30), "m": 3.2, "c": 5, "noise": 10,
     "context": "the midday temperature on a number of days and the number of ice creams a shop sold"},
    {"positive": True, "x_label": "Advert spend (£100s)", "y_label": "Weekly sales (£1000s)",
     "x_range": (2, 20), "m": 1.8, "c": 4, "noise": 6,
     "context": "a company's weekly advertising spend and its weekly sales"},
    {"positive": False, "x_label": "Age of car (years)", "y_label": "Value (£1000s)",
     "x_range": (1, 12), "m": -1.4, "c": 22, "noise": 4,
     "context": "the age of a number of second-hand cars and their value"},
    {"positive": False, "x_label": "Journey speed (mph)", "y_label": "Journey time (minutes)",
     "x_range": (20, 60), "m": -0.9, "c": 70, "noise": 6,
     "context": "the average speed of a number of journeys of the same distance and how long they took"},
)


def _pearson_sign(xs: list, ys: list) -> int:
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    var_x = sum((x - mx) ** 2 for x in xs)
    var_y = sum((y - my) ** 2 for y in ys)
    if var_x == 0 or var_y == 0:
        return 0
    r = cov / (var_x * var_y) ** 0.5
    return 1 if r > 0 else (-1 if r < 0 else 0)


def _scatter_case(rng: random.Random) -> dict:
    ctx = rng.choice(_CONTEXTS)
    lo, hi = ctx["x_range"]
    n = 9
    intended_sign = 1 if ctx["positive"] else -1

    for _ in range(200):
        xs = sorted(rng.sample(range(lo, hi + 1), n))
        ys = [round(ctx["m"] * x + ctx["c"] + rng.uniform(-ctx["noise"], ctx["noise"]), 1) for x in xs]
        # Independent verification: recompute the Pearson correlation sign
        # of the actual (noisy) data via the covariance formula - a
        # different check than just trusting the generating line's own
        # sign, since random noise could occasionally flip the apparent
        # correlation of a small sample.
        if _pearson_sign(xs, ys) == intended_sign:
            break
    else:
        raise ValueError("scatter_graphs: could not construct data matching the intended correlation")

    points = list(zip(xs, ys))
    correlation = "positive" if ctx["positive"] else "negative"
    return {"ctx": ctx, "points": points, "correlation": correlation}


def _scatter_table(ctx: dict, points: list) -> DiagramSpec:
    """A two-row x/y data table, reusing the generic two_way_table renderer -
    replaces the old prose listing of (x, y) pairs."""
    n = len(points)
    return DiagramSpec(
        kind="two_way_table",
        params={
            "row_labels": [ctx["x_label"], ctx["y_label"]],
            "col_labels": [str(i + 1) for i in range(n)],
            "cells": [[str(x) for x, _y in points], [str(y) for _x, y in points]],
        },
    )


def generate_scatter_graph_construct(tier: Tier, rng: random.Random) -> Question:
    c = _scatter_case(rng)
    ctx, points = c["ctx"], c["points"]
    steps = [
        f"Plot each ({ctx['x_label']}, {ctx['y_label']}) pair as a single point - do not join the points "
        "up with a line or curve.",
        f"As {ctx['x_label'].lower()} increases, {ctx['y_label'].lower()} tends to "
        f"{'increase' if ctx['positive'] else 'decrease'} too, so the points show "
        f"{c['correlation']} correlation.",
    ]
    return Question(
        topic_id="scatter_graph_construct_F",
        tier=Tier.FOUNDATION,
        prompt=f"The table shows {ctx['context']}. Draw a scatter graph of this data, and "
        "describe the correlation.",
        solution_steps=tuple(steps),
        final_answer=f"{c['correlation'].capitalize()} correlation",
        dedup_key=f"scatter_construct:{ctx['x_label']}:{tuple(points)}",
        diagram=_scatter_table(ctx, points),
        solution_diagram=DiagramSpec(
            kind="scatter_graph",
            params={"points": points, "x_label": ctx["x_label"], "y_label": ctx["y_label"]},
        ),
    )


def generate_modelled_example_scatter_graph_construct(tier: Tier, rng: random.Random) -> ModelledExample:
    c = _scatter_case(rng)
    ctx, points = c["ctx"], c["points"]
    table = ", ".join(f"({x}, {y})" for x, y in points)
    teaching_steps = [
        "A scatter graph shows whether there's a relationship between two variables - each data pair "
        "becomes a single point, plotted but never joined up, since there's no meaningful 'path' between "
        "one data pair and the next.",
        f"Plot every ({ctx['x_label']}, {ctx['y_label']}) pair from the table as its own point.",
        f"Look at the overall pattern the points make: here, as {ctx['x_label'].lower()} increases, "
        f"{ctx['y_label'].lower()} tends to {'increase' if ctx['positive'] else 'decrease'} too - the "
        f"points broadly trend {'upward' if ctx['positive'] else 'downward'} from left to right, which is "
        f"called {c['correlation']} correlation.",
        "Real data is never perfectly tidy, so the points won't lie exactly on a line - correlation is "
        "about the overall trend, not every individual point matching it.",
    ]
    worked_calculation = [table, f"Trend: {c['correlation']} correlation"]
    return ModelledExample(
        topic_id="scatter_graph_construct_F",
        tier=Tier.FOUNDATION,
        prompt=f"The table shows {ctx['context']}. Draw a scatter graph of this data, and "
        "describe the correlation.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{c['correlation'].capitalize()} correlation",
        diagram=DiagramSpec(
            kind="scatter_graph",
            params={"points": points, "x_label": ctx["x_label"], "y_label": ctx["y_label"]},
        ),
    )


def generate_scatter_graph_interpret(tier: Tier, rng: random.Random) -> Question:
    c = _scatter_case(rng)
    ctx, points = c["ctx"], c["points"]
    xs = [p[0] for p in points]
    base_params = {"points": points, "x_label": ctx["x_label"], "y_label": ctx["y_label"]}
    best_fit = {"m": ctx["m"], "c": ctx["c"]}

    shape = rng.choice(["read_value", "correlation_type"])
    if shape == "read_value":
        query_x = round((min(xs) + max(xs)) / 2)
        query_y = round(ctx["m"] * query_x + ctx["c"])
        # Independent check: rearranging the line equation to solve for x
        # given the predicted y must reproduce query_x - a different
        # direction through the same relationship than the substitution
        # used to compute query_y. Tolerance allows for query_y itself
        # having been rounded to the nearest whole number (up to 0.5 of
        # rounding error, scaled by how shallow the line's slope is).
        recovered_x = (query_y - ctx["c"]) / ctx["m"]
        tolerance = 0.5 / abs(ctx["m"]) + 0.05
        if abs(recovered_x - query_x) > tolerance:
            raise ValueError("scatter_graph_interpret verification failed: read_value round-trip mismatch")
        steps = [
            f"Find {query_x} on the {ctx['x_label'].lower()} axis and read up to your line of best fit.",
            f"Read across to the {ctx['y_label'].lower()} axis: approximately {query_y}.",
        ]
        return Question(
            topic_id="scatter_graph_interpret_F",
            tier=Tier.FOUNDATION,
            prompt=f"The scatter graph shows {ctx['context']}. Draw a line of best fit, and use it to "
            f"estimate {ctx['y_label'].lower()} when {ctx['x_label'].lower()} is {query_x}.",
            solution_steps=tuple(steps),
            final_answer=f"Approximately {query_y}",
            dedup_key=f"scatter_interpret_read:{ctx['x_label']}:{tuple(points)}:{query_x}",
            diagram=DiagramSpec(kind="scatter_graph", params=base_params),
            solution_diagram=DiagramSpec(
                kind="scatter_graph", params={**base_params, "best_fit": best_fit}
            ),
        )

    steps = [
        f"As {ctx['x_label'].lower()} increases, {ctx['y_label'].lower()} tends to "
        f"{'increase' if ctx['positive'] else 'decrease'}.",
        f"This means the scatter graph shows {c['correlation']} correlation.",
    ]
    return Question(
        topic_id="scatter_graph_interpret_F",
        tier=Tier.FOUNDATION,
        prompt=f"The scatter graph shows {ctx['context']}. Describe the correlation shown.",
        solution_steps=tuple(steps),
        final_answer=f"{c['correlation'].capitalize()} correlation",
        dedup_key=f"scatter_interpret_corr:{ctx['x_label']}:{tuple(points)}",
        diagram=DiagramSpec(kind="scatter_graph", params=base_params),
    )


def generate_modelled_example_scatter_graph_interpret(tier: Tier, rng: random.Random) -> ModelledExample:
    c = _scatter_case(rng)
    ctx, points = c["ctx"], c["points"]
    xs = [p[0] for p in points]
    best_fit = {"m": ctx["m"], "c": ctx["c"]}
    diagram = DiagramSpec(
        kind="scatter_graph",
        params={"points": points, "x_label": ctx["x_label"], "y_label": ctx["y_label"], "best_fit": best_fit},
    )
    query_x = round((min(xs) + max(xs)) / 2)
    query_y = round(ctx["m"] * query_x + ctx["c"])

    teaching_steps = [
        "A line of best fit is a single straight line drawn through the middle of a scatter graph's "
        "points, following the overall trend - it lets you estimate values you don't have exact data for.",
        f"To estimate {ctx['y_label'].lower()} when {ctx['x_label'].lower()} is {query_x}: find {query_x} "
        f"on the {ctx['x_label'].lower()} axis, go straight up to the line of best fit, then read across "
        f"to the {ctx['y_label'].lower()} axis - giving approximately {query_y}.",
        "This kind of estimate is only reliable within the range of the original data - using the same "
        "line to predict a value far outside that range (extrapolation) is much less trustworthy, since "
        "there's no evidence the trend continues that far.",
        "It's also worth remembering that correlation on its own doesn't prove one variable *causes* the "
        f"other to change - {ctx['context']} might be linked through some other factor entirely.",
    ]
    worked_calculation = [
        f"Line of best fit read at {ctx['x_label'].lower()} = {query_x}",
        f"Estimated {ctx['y_label'].lower()} ≈ {query_y}",
    ]
    return ModelledExample(
        topic_id="scatter_graph_interpret_F",
        tier=Tier.FOUNDATION,
        prompt=f"The scatter graph shows {ctx['context']}. Draw a line of best fit, and use it to "
        f"estimate {ctx['y_label'].lower()} when {ctx['x_label'].lower()} is {query_x}.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"Approximately {query_y}",
        diagram=diagram,
    )


TOPIC_SCATTER_GRAPH_CONSTRUCT = TopicDefinition(
    id="scatter_graph_construct_F",
    display_name="Constructing Scatter Graphs",
    description="Plot a scatter graph from a data table and describe the correlation shown.",
    generate=generate_scatter_graph_construct,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_scatter_graph_construct,
)

TOPIC_SCATTER_GRAPH_INTERPRET = TopicDefinition(
    id="scatter_graph_interpret_F",
    display_name="Interpreting Scatter Graphs",
    description="Use a line of best fit to estimate a value, or describe the correlation shown.",
    generate=generate_scatter_graph_interpret,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_scatter_graph_interpret,
)
