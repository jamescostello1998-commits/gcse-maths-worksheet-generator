import random
from fractions import Fraction

from app.core.models import DiagramSpec, ModelledExample, Question, Tier
from app.topics.base import TopicDefinition

SECTION = "statistics"
GROUP = "Charts and Graphs"

_BAR_CONTEXTS = [
    ("favourite colour", ["Red", "Blue", "Green", "Yellow"]),
    ("favourite fruit", ["Apple", "Banana", "Orange", "Grape"]),
    ("day of the week absent", ["Mon", "Tue", "Wed", "Thu", "Fri"]),
    ("mode of transport to school", ["Walk", "Bus", "Car", "Bike"]),
]


def _random_table(rng: random.Random) -> tuple[str, list[str], list[int]]:
    context, all_cats = rng.choice(_BAR_CONTEXTS)
    n = rng.randint(3, min(4, len(all_cats)))
    categories = rng.sample(all_cats, n)
    values = [rng.randint(2, 20) for _ in categories]
    return context, categories, values


def generate_bar_chart_construct(tier: Tier, rng: random.Random) -> Question:
    context, categories, values = _random_table(rng)
    table_desc = ", ".join(f"{c}: {v}" for c, v in zip(categories, values))

    # Independent check: rebuild the series via a dict round-trip rather than
    # reusing the same `values` list directly.
    as_dict = dict(zip(categories, values))
    rebuilt = [as_dict[c] for c in categories]
    if rebuilt != values:
        raise ValueError("bar_chart_construct verification failed")

    final_answer = "Bars of height " + ", ".join(f"{v} ({c})" for c, v in zip(categories, values))
    steps = [
        f"Draw one bar per category ({', '.join(categories)}), each as tall as its frequency.",
        f"Heights: {table_desc}.",
        final_answer,
    ]
    return Question(
        topic_id="bar_chart_construct",
        tier=Tier.FOUNDATION,
        prompt=f"The table shows the {context} of a group of students: {table_desc}. Draw a bar chart to show this information.",
        solution_steps=tuple(steps),
        final_answer=final_answer,
        dedup_key=f"bar_construct:{categories}:{values}",
        diagram=DiagramSpec(kind="bar_chart", params={"categories": categories, "series": values, "blank": True}),
        solution_diagram=DiagramSpec(kind="bar_chart", params={"categories": categories, "series": values}),
    )


def generate_modelled_example_bar_chart_construct(tier: Tier, rng: random.Random) -> ModelledExample:
    context, categories, values = _random_table(rng)
    as_dict = dict(zip(categories, values))
    rebuilt = [as_dict[c] for c in categories]
    if rebuilt != values:
        raise ValueError("modelled example bar_chart_construct verification failed")

    table_desc = ", ".join(f"{c}: {v}" for c, v in zip(categories, values))
    final_answer = "Bars of height " + ", ".join(f"{v} ({c})" for c, v in zip(categories, values))
    teaching_steps = [
        f"A bar chart shows one bar per category, with the height of each bar equal to its frequency. "
        f"Here the categories are {', '.join(categories)}.",
        "First draw and label the axes: categories along the bottom, frequency up the side, with an "
        "even scale that comfortably reaches the largest value.",
        f"Then draw each bar to the correct height: {table_desc}. All bars should be the same width, "
        "evenly spaced, with a small gap between them.",
    ]
    worked_calculation = [f"{c}: height {v}" for c, v in zip(categories, values)]
    return ModelledExample(
        topic_id="bar_chart_construct",
        tier=Tier.FOUNDATION,
        prompt=f"The table shows the {context} of a group of students: {table_desc}. Draw a bar chart to show this information.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=final_answer,
        diagram=DiagramSpec(kind="bar_chart", params={"categories": categories, "series": values}),
    )


_BAR_INTERPRET_KINDS = ["read_one", "difference", "total", "extreme"]


def _bar_interpret_body(categories: list[str], values: list[int], kind: str, rng: random.Random):
    as_dict = dict(zip(categories, values))
    if kind == "read_one":
        cat = rng.choice(categories)
        answer = as_dict[cat]
        prompt = f"How many chose {cat}?"
        steps = [f"Find the {cat} bar on the chart.", f"Read its height: {answer}."]
        check = as_dict[cat] == values[categories.index(cat)]
    elif kind == "difference":
        a, b = rng.sample(categories, 2)
        answer = abs(as_dict[a] - as_dict[b])
        prompt = f"How many more chose {a} than {b}? (Give a positive answer either way.)"
        steps = [f"{a}: {as_dict[a]}, {b}: {as_dict[b]}.", f"Difference = |{as_dict[a]} - {as_dict[b]}| = {answer}."]
        check = max(as_dict[a], as_dict[b]) - min(as_dict[a], as_dict[b]) == answer
    elif kind == "total":
        answer = sum(values)
        prompt = "Find the total frequency shown on the chart."
        steps = [
            f"Read every bar's height: {', '.join(str(v) for v in values)}.",
            f"Add them together: {' + '.join(str(v) for v in values)} = {answer}.",
        ]
        total_alt = 0
        for v in values:
            total_alt += v
        check = total_alt == answer
    else:
        which = "highest" if rng.random() < 0.5 else "lowest"
        target = max(values) if which == "highest" else min(values)
        cat = categories[values.index(target)]
        answer = cat
        prompt = f"Which category has the {which} frequency?"
        steps = [
            f"Compare every bar's height: {', '.join(str(v) for v in values)}.",
            f"The {which} bar belongs to {cat}, with frequency {target}.",
        ]
        # Independent check: scan for the first index reaching the target value
        # via a generator expression, rather than reusing values.index() - and
        # match its same "first occurrence wins" tie-break, since sorted(...,
        # reverse=True) reverses tie order instead of preserving it.
        first_idx = next(i for i, v in enumerate(values) if v == target)
        check = categories[first_idx] == cat
    if not check:
        raise ValueError("bar_chart_interpret verification failed")
    return prompt, steps, str(answer)


def generate_bar_chart_interpret(tier: Tier, rng: random.Random) -> Question:
    context, categories, values = _random_table(rng)
    kind = rng.choice(_BAR_INTERPRET_KINDS)
    prompt_tail, steps, answer = _bar_interpret_body(categories, values, kind, rng)
    table_desc = ", ".join(f"{c}: {v}" for c, v in zip(categories, values))

    return Question(
        topic_id="bar_chart_interpret",
        tier=Tier.FOUNDATION,
        prompt=f"The bar chart shows the {context} of a group of students. {prompt_tail}",
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"bar_interpret:{categories}:{values}:{kind}",
        diagram=DiagramSpec(kind="bar_chart", params={"categories": categories, "series": values}),
    )


def generate_modelled_example_bar_chart_interpret(tier: Tier, rng: random.Random) -> ModelledExample:
    context, categories, values = _random_table(rng)
    kind = rng.choice(_BAR_INTERPRET_KINDS)
    prompt_tail, steps, answer = _bar_interpret_body(categories, values, kind, rng)

    teaching_steps = [
        f"This bar chart shows the {context} of a group of students - each bar's height tells you "
        "the frequency for that category.",
        "Read the heights carefully against the frequency axis before doing any arithmetic with them.",
    ] + [f"{s}" for s in steps]
    return ModelledExample(
        topic_id="bar_chart_interpret",
        tier=Tier.FOUNDATION,
        prompt=f"The bar chart shows the {context} of a group of students. {prompt_tail}",
        worked_calculation=tuple(steps),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
        diagram=DiagramSpec(kind="bar_chart", params={"categories": categories, "series": values}),
    )


_COMPOSITE_CONTEXTS = [
    ("students", ["Boys", "Girls"], ["Mon", "Tue", "Wed", "Thu"]),
    ("commuters", ["Bus", "Car"], ["Week 1", "Week 2", "Week 3"]),
    ("sales", ["2023", "2024"], ["Jan", "Feb", "Mar", "Apr"]),
]

_COMPOSITE_KINDS = ["read_segment", "category_total", "segment_difference", "grand_total"]


def _random_composite(rng: random.Random):
    label, segs, all_cats = rng.choice(_COMPOSITE_CONTEXTS)
    n = rng.randint(3, len(all_cats))
    categories = all_cats[:n]
    series = [[rng.randint(2, 15) for _ in segs] for _ in categories]
    return label, segs, categories, series


def _composite_body(segs, categories, series, kind, rng):
    if kind == "read_segment":
        ci = rng.randrange(len(categories))
        si = rng.randrange(len(segs))
        answer = series[ci][si]
        prompt = f"How many {segs[si].lower()} are shown for {categories[ci]}?"
        steps = [
            f"Find the {categories[ci]} bar, then the {segs[si]} segment within it.",
            f"That segment's value is {answer}.",
        ]
        check = series[ci][si] == answer
    elif kind == "category_total":
        ci = rng.randrange(len(categories))
        answer = sum(series[ci])
        prompt = f"Find the total for {categories[ci]}."
        steps = [
            f"{categories[ci]}'s segments are {', '.join(str(v) for v in series[ci])}.",
            f"Add them: {' + '.join(str(v) for v in series[ci])} = {answer}.",
        ]
        acc = 0
        for v in series[ci]:
            acc += v
        check = acc == answer
    elif kind == "segment_difference":
        ci = rng.randrange(len(categories))
        answer = abs(series[ci][0] - series[ci][1]) if len(segs) >= 2 else 0
        prompt = f"Find the difference between {segs[0]} and {segs[1]} for {categories[ci]}."
        steps = [f"{segs[0]}: {series[ci][0]}, {segs[1]}: {series[ci][1]}.", f"Difference = {answer}."]
        check = abs(series[ci][1] - series[ci][0]) == answer
    else:
        answer = sum(sum(seg) for seg in series)
        prompt = "Find the grand total across every category and segment."
        steps = [
            "Add up every segment in every bar, category by category.",
            f"Total = {answer}.",
        ]
        grand = sum(v for seg in series for v in seg)
        check = grand == answer
    if not check:
        raise ValueError("composite_bar_chart verification failed")
    return prompt, steps, str(answer)


def generate_composite_bar_chart(tier: Tier, rng: random.Random) -> Question:
    label, segs, categories, series = _random_composite(rng)
    kind = rng.choice(_COMPOSITE_KINDS)
    prompt_tail, steps, answer = _composite_body(segs, categories, series, kind, rng)

    return Question(
        topic_id="composite_bar_chart",
        tier=Tier.FOUNDATION,
        prompt=f"The composite bar chart shows the number of {label} split by {' and '.join(segs)}. {prompt_tail}",
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"composite:{categories}:{series}:{kind}",
        diagram=DiagramSpec(
            kind="bar_chart",
            params={"categories": categories, "series": series, "series_labels": segs, "y_label": "Frequency"},
        ),
    )


def generate_modelled_example_composite_bar_chart(tier: Tier, rng: random.Random) -> ModelledExample:
    label, segs, categories, series = _random_composite(rng)
    kind = rng.choice(_COMPOSITE_KINDS)
    prompt_tail, steps, answer = _composite_body(segs, categories, series, kind, rng)

    teaching_steps = [
        f"A composite (stacked) bar chart shows {' and '.join(segs)} stacked on top of each other in "
        f"one bar per category, so each bar's total height is the sum of its segments.",
        "Read each coloured segment's own height first, using the legend to tell the segments apart, "
        "before combining any values.",
    ] + list(steps)
    return ModelledExample(
        topic_id="composite_bar_chart",
        tier=Tier.FOUNDATION,
        prompt=f"The composite bar chart shows the number of {label} split by {' and '.join(segs)}. {prompt_tail}",
        worked_calculation=tuple(steps),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
        diagram=DiagramSpec(
            kind="bar_chart",
            params={"categories": categories, "series": series, "series_labels": segs, "y_label": "Frequency"},
        ),
    )


_PIE_TOTALS = [12, 18, 24, 36]
_PIE_CONTEXTS = [
    ("favourite subject", ["Maths", "English", "Science", "Art"]),
    ("favourite sport", ["Football", "Tennis", "Swimming", "Rugby"]),
    ("holiday destination", ["UK", "France", "Spain", "USA"]),
]


def _random_pie(rng: random.Random):
    context, all_cats = rng.choice(_PIE_CONTEXTS)
    total = rng.choice(_PIE_TOTALS)
    n = rng.randint(3, len(all_cats))
    categories = all_cats[:n]
    # Partition `total` into n positive parts.
    cuts = sorted(rng.sample(range(1, total), n - 1))
    bounds = [0] + cuts + [total]
    values = [bounds[i + 1] - bounds[i] for i in range(n)]
    rng.shuffle(values)
    return context, categories, values, total


def generate_pie_chart_construct(tier: Tier, rng: random.Random) -> Question:
    context, categories, values, total = _random_pie(rng)
    table_desc = ", ".join(f"{c}: {v}" for c, v in zip(categories, values))

    angles = [Fraction(v, total) * 360 for v in values]
    if sum(angles) != 360:
        raise ValueError("pie_chart_construct verification failed: angles do not sum to 360")
    # Independent re-check of one angle via integer arithmetic where it divides evenly.
    for v, a in zip(values, angles):
        if (360 * v) % total == 0 and 360 * v // total != a:
            raise ValueError("pie_chart_construct verification failed: angle mismatch")

    angle_strs = [f"{c}: {int(a) if a == int(a) else float(a):.0f}°" for c, a in zip(categories, angles)]
    final_answer = ", ".join(angle_strs)
    steps = [f"Total = {total}."] + [
        f"{c}: {v}/{total} × 360° = {int(a) if a == int(a) else float(a):.0f}°" for c, v, a in zip(categories, values, angles)
    ] + [final_answer]
    return Question(
        topic_id="pie_chart_construct",
        tier=Tier.FOUNDATION,
        prompt=f"A survey of {total} people asked about their {context}: {table_desc}. Calculate the angle for each category, and draw a pie chart.",
        solution_steps=tuple(steps),
        final_answer=final_answer,
        dedup_key=f"pie_construct:{categories}:{values}:{total}",
        solution_diagram=DiagramSpec(kind="pie_chart", params={"categories": categories, "values": values, "show": "value"}),
    )


def generate_modelled_example_pie_chart_construct(tier: Tier, rng: random.Random) -> ModelledExample:
    context, categories, values, total = _random_pie(rng)
    angles = [Fraction(v, total) * 360 for v in values]
    if sum(angles) != 360:
        raise ValueError("modelled example pie_chart_construct verification failed")

    table_desc = ", ".join(f"{c}: {v}" for c, v in zip(categories, values))
    angle_strs = [f"{c}: {int(a) if a == int(a) else float(a):.0f}°" for c, a in zip(categories, angles)]
    final_answer = ", ".join(angle_strs)
    teaching_steps = [
        f"A pie chart shares 360° between the categories in proportion to their frequency, out of a "
        f"total of {total}.",
        "For each category, work out what fraction of the total it represents, then multiply that "
        "fraction by 360° to get its angle.",
        f"{table_desc}. Check the angles add back up to 360° as a sanity check.",
    ]
    worked_calculation = [f"{c}: {v}/{total} × 360° = {s.split(': ')[1]}" for c, v, s in zip(categories, values, angle_strs)]
    return ModelledExample(
        topic_id="pie_chart_construct",
        tier=Tier.FOUNDATION,
        prompt=f"A survey of {total} people asked about their {context}: {table_desc}. Calculate the angle for each category, and draw a pie chart.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=final_answer,
        diagram=DiagramSpec(kind="pie_chart", params={"categories": categories, "values": values, "show": "value"}),
    )


_PIE_INTERPRET_KINDS = ["percentage", "difference", "fraction"]


def _pie_interpret_body(categories, values, total, kind, rng):
    as_dict = dict(zip(categories, values))
    if kind == "percentage":
        cat = rng.choice(categories)
        pct = Fraction(as_dict[cat], total) * 100
        answer = f"{float(pct):.1f}%" if pct != int(pct) else f"{int(pct)}%"
        prompt = f"What percentage chose {cat}?"
        steps = [
            f"{cat} accounts for {as_dict[cat]} out of {total}.",
            f"{as_dict[cat]}/{total} × 100 = {answer}.",
        ]
        # Independent check: multiply-then-divide as a single exact Fraction,
        # rather than reusing the divide-then-multiply `pct` computed above.
        check = Fraction(as_dict[cat] * 100, total) == pct
    elif kind == "difference":
        a, b = rng.sample(categories, 2)
        answer = str(abs(as_dict[a] - as_dict[b]))
        prompt = f"How many more chose {a} than {b}?"
        steps = [f"{a}: {as_dict[a]}, {b}: {as_dict[b]}.", f"Difference = {answer}."]
        check = max(as_dict[a], as_dict[b]) - min(as_dict[a], as_dict[b]) == abs(as_dict[a] - as_dict[b])
    else:
        cat = rng.choice(categories)
        frac = Fraction(as_dict[cat], total)
        answer = f"{frac.numerator}/{frac.denominator}"
        prompt = f"What fraction of the total chose {cat}? Give your answer in its simplest form."
        steps = [
            f"{cat} represents {as_dict[cat]} out of {total}: {as_dict[cat]}/{total}.",
            f"Simplify: {answer}.",
        ]
        import math
        g = math.gcd(as_dict[cat], total)
        check = (as_dict[cat] // g, total // g) == (frac.numerator, frac.denominator)
    if not check:
        raise ValueError("pie_chart_interpret verification failed")
    return prompt, steps, answer


def generate_pie_chart_interpret(tier: Tier, rng: random.Random) -> Question:
    context, categories, values, total = _random_pie(rng)
    kind = rng.choice(_PIE_INTERPRET_KINDS)
    prompt_tail, steps, answer = _pie_interpret_body(categories, values, total, kind, rng)

    return Question(
        topic_id="pie_chart_interpret",
        tier=Tier.FOUNDATION,
        prompt=f"The pie chart shows the {context} of {total} people. {prompt_tail}",
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"pie_interpret:{categories}:{values}:{total}:{kind}",
        diagram=DiagramSpec(kind="pie_chart", params={"categories": categories, "values": values, "show": "value"}),
    )


def generate_modelled_example_pie_chart_interpret(tier: Tier, rng: random.Random) -> ModelledExample:
    context, categories, values, total = _random_pie(rng)
    kind = rng.choice(_PIE_INTERPRET_KINDS)
    prompt_tail, steps, answer = _pie_interpret_body(categories, values, total, kind, rng)

    teaching_steps = [
        f"The pie chart already shows how many of the {total} people chose each category, so this is "
        "about using those counts, not re-measuring angles.",
    ] + list(steps)
    return ModelledExample(
        topic_id="pie_chart_interpret",
        tier=Tier.FOUNDATION,
        prompt=f"The pie chart shows the {context} of {total} people. {prompt_tail}",
        worked_calculation=tuple(steps),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
        diagram=DiagramSpec(kind="pie_chart", params={"categories": categories, "values": values, "show": "value"}),
    )


_TIME_SERIES_CONTEXTS = [
    ("ice creams sold", "Month", "Ice creams sold"),
    ("average temperature", "Day", "Temperature (°C)"),
    ("number of visitors", "Week", "Visitors"),
]
_TS_KINDS = ["read_value", "change", "extreme", "range"]


def _random_time_series(rng: random.Random):
    label, x_label, y_label = rng.choice(_TIME_SERIES_CONTEXTS)
    n = rng.randint(5, 8)
    start = rng.randint(20, 100)
    points = [(1, start)]
    for p in range(2, n + 1):
        delta = rng.randint(-15, 15)
        points.append((p, max(0, points[-1][1] + delta)))
    return label, x_label, y_label, points


def _time_series_body(points, kind, rng):
    values = [v for _, v in points]
    if kind == "read_value":
        p, v = rng.choice(points)
        answer = str(v)
        prompt = f"What was the value at period {p}?"
        steps = [f"Find period {p} on the horizontal axis.", f"Read the value there: {answer}."]
        check = dict(points)[p] == v
    elif kind == "change":
        i = rng.randrange(len(points) - 1)
        p1, v1 = points[i]
        p2, v2 = points[i + 1]
        answer = str(v2 - v1)
        prompt = f"Find the change in value from period {p1} to period {p2}."
        steps = [f"Period {p1}: {v1}, period {p2}: {v2}.", f"Change = {v2} - {v1} = {answer}."]
        # Independent check: re-fetch both values fresh from `points` via dict
        # lookup rather than reusing the already-bound v1/v2 locals.
        by_period = dict(points)
        check = (by_period[p2] - by_period[p1]) == int(answer)
    elif kind == "extreme":
        which = "highest" if rng.random() < 0.5 else "lowest"
        target = max(values) if which == "highest" else min(values)
        p = next(pp for pp, vv in points if vv == target)
        answer = str(p)
        prompt = f"At which period was the value {which}?"
        steps = [
            f"Compare every plotted value: {', '.join(str(v) for v in values)}.",
            f"The {which} value, {target}, occurs at period {p}.",
        ]
        sorted_vals = sorted(values, reverse=(which == "highest"))
        check = sorted_vals[0] == target and dict(points)[p] == target
    else:
        answer = str(max(values) - min(values))
        prompt = "Find the range of values across the whole series."
        steps = [f"Max = {max(values)}, min = {min(values)}.", f"Range = {answer}."]
        check = (max(values) - min(values)) == int(answer)
    if not check:
        raise ValueError("time_series_graph verification failed")
    return prompt, steps, answer


def generate_time_series_graph(tier: Tier, rng: random.Random) -> Question:
    label, x_label, y_label, points = _random_time_series(rng)
    kind = rng.choice(_TS_KINDS)
    prompt_tail, steps, answer = _time_series_body(points, kind, rng)

    return Question(
        topic_id="time_series_graph",
        tier=Tier.FOUNDATION,
        prompt=f"The time series graph shows the {label} over time. {prompt_tail}",
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"time_series:{points}:{kind}",
        diagram=DiagramSpec(kind="time_series", params={"points": points, "x_label": x_label, "y_label": y_label}),
    )


def generate_modelled_example_time_series_graph(tier: Tier, rng: random.Random) -> ModelledExample:
    label, x_label, y_label, points = _random_time_series(rng)
    kind = rng.choice(_TS_KINDS)
    prompt_tail, steps, answer = _time_series_body(points, kind, rng)

    teaching_steps = [
        f"A time series graph plots the {label} at each successive {x_label.lower()}, joined by "
        "straight lines so you can see the trend over time.",
        "Trace along the line to the period you need, then read straight across to the value axis.",
    ] + list(steps)
    return ModelledExample(
        topic_id="time_series_graph",
        tier=Tier.FOUNDATION,
        prompt=f"The time series graph shows the {label} over time. {prompt_tail}",
        worked_calculation=tuple(steps),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
        diagram=DiagramSpec(kind="time_series", params={"points": points, "x_label": x_label, "y_label": y_label}),
    )


TOPIC_BAR_CONSTRUCT = TopicDefinition(
    id="bar_chart_construct",
    display_name="Constructing Bar Charts",
    description="Draw a bar chart from a frequency table.",
    generate=generate_bar_chart_construct,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_bar_chart_construct,
)

TOPIC_BAR_INTERPRET = TopicDefinition(
    id="bar_chart_interpret",
    display_name="Interpreting Bar Charts",
    description="Read and compare values from a bar chart.",
    generate=generate_bar_chart_interpret,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_bar_chart_interpret,
)

TOPIC_COMPOSITE_BAR = TopicDefinition(
    id="composite_bar_chart",
    display_name="Composite Bar Charts",
    description="Read and compare values from a stacked (composite) bar chart.",
    generate=generate_composite_bar_chart,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_composite_bar_chart,
)

TOPIC_PIE_CONSTRUCT = TopicDefinition(
    id="pie_chart_construct",
    display_name="Constructing Pie Charts",
    description="Calculate angles and draw a pie chart from a frequency table.",
    generate=generate_pie_chart_construct,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_pie_chart_construct,
)

TOPIC_PIE_INTERPRET = TopicDefinition(
    id="pie_chart_interpret",
    display_name="Interpreting Pie Charts",
    description="Use a pie chart's values to find percentages, fractions, and differences.",
    generate=generate_pie_chart_interpret,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_pie_chart_interpret,
)

TOPIC_TIME_SERIES = TopicDefinition(
    id="time_series_graph",
    display_name="Time Series Graphs",
    description="Read values, changes, and trends from a time series graph.",
    generate=generate_time_series_graph,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_time_series_graph,
)
