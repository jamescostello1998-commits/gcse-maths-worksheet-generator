import random
from fractions import Fraction
from itertools import accumulate

from app.core.models import DiagramSpec, ModelledExample, Question, Tier
from app.topics.base import TopicDefinition

SECTION = "statistics"
GROUP = "Cumulative Frequency & Box Plots"

_CF_CONTEXTS = [
    ("Weight (kg)", "the weights (in kg) of a group of parcels"),
    ("Time (minutes)", "the times (in minutes) taken to run a race"),
    ("Height (cm)", "the heights (in cm) of a group of plants"),
]


def _random_grouped_table(rng: random.Random):
    x_label, context = rng.choice(_CF_CONTEXTS)
    n_classes = rng.randint(5, 6)
    width = 10
    start = rng.choice([0, 10, 20])
    boundaries = [start + i * width for i in range(n_classes + 1)]
    frequencies = [rng.randint(2, 15) for _ in range(n_classes)]
    return x_label, context, boundaries, frequencies


def _cumulative_points(boundaries: list[int], frequencies: list[int]) -> list[tuple[int, int]]:
    cumulative = list(accumulate(frequencies))
    return [(boundaries[0], 0)] + [(boundaries[i + 1], cumulative[i]) for i in range(len(frequencies))]


def generate_cumulative_frequency_plot(tier: Tier, rng: random.Random) -> Question:
    x_label, context, boundaries, frequencies = _random_grouped_table(rng)
    points = _cumulative_points(boundaries, frequencies)

    # Independent check: recompute the running total via a manual accumulator
    # loop, a genuinely different code path from itertools.accumulate.
    running = 0
    manual_cumulative = []
    for f in frequencies:
        running += f
        manual_cumulative.append(running)
    if manual_cumulative != [cf for _, cf in points[1:]]:
        raise ValueError("cumulative_frequency_plot verification failed")

    table_desc = ", ".join(f"{boundaries[i]}-{boundaries[i+1]}: {f}" for i, f in enumerate(frequencies))
    cf_desc = ", ".join(str(cf) for cf in manual_cumulative)
    final_answer = f"Cumulative frequencies: {cf_desc}"
    steps = [
        f"Running total of the frequencies, class by class: {table_desc}.",
        final_answer,
        "Plot each (upper class boundary, cumulative frequency) point and join with a smooth curve.",
    ]
    return Question(
        topic_id="cumulative_frequency_plot",
        tier=Tier.HIGHER,
        prompt=(
            f"The table shows {context}: {table_desc} (class: frequency). "
            "Draw a cumulative frequency graph to show this information."
        ),
        solution_steps=tuple(steps),
        final_answer=final_answer,
        dedup_key=f"cf_plot:{boundaries}:{frequencies}",
        diagram=DiagramSpec(kind="cumulative_frequency", params={"points": points, "x_label": x_label, "blank": True}),
        solution_diagram=DiagramSpec(kind="cumulative_frequency", params={"points": points, "x_label": x_label}),
    )


def generate_modelled_example_cumulative_frequency_plot(tier: Tier, rng: random.Random) -> ModelledExample:
    x_label, context, boundaries, frequencies = _random_grouped_table(rng)
    points = _cumulative_points(boundaries, frequencies)
    running = 0
    manual_cumulative = []
    for f in frequencies:
        running += f
        manual_cumulative.append(running)
    if manual_cumulative != [cf for _, cf in points[1:]]:
        raise ValueError("modelled example cumulative_frequency_plot verification failed")

    table_desc = ", ".join(f"{boundaries[i]}-{boundaries[i+1]}: {f}" for i, f in enumerate(frequencies))
    cf_desc = ", ".join(str(cf) for cf in manual_cumulative)
    final_answer = f"Cumulative frequencies: {cf_desc}"
    teaching_steps = [
        "A cumulative frequency graph plots the running total of the frequencies up to the END of "
        "each class, against that class's upper boundary.",
        f"Working through the classes ({table_desc}), keep a running total: it only ever goes up, "
        "never down, since you're always adding another class's frequency on top.",
        f"So the cumulative frequencies are {cf_desc}. Plot each one against its class's upper "
        f"boundary ({', '.join(str(b) for b in boundaries[1:])}), starting from ({boundaries[0]}, 0), "
        "and join the points with straight lines (or a smooth curve).",
    ]
    worked_calculation = [f"Up to {boundaries[i+1]}: {cf}" for i, cf in enumerate(manual_cumulative)]
    return ModelledExample(
        topic_id="cumulative_frequency_plot",
        tier=Tier.HIGHER,
        prompt=(
            f"The table shows {context}: {table_desc} (class: frequency). "
            "Draw a cumulative frequency graph to show this information."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=final_answer,
        diagram=DiagramSpec(kind="cumulative_frequency", params={"points": points, "x_label": x_label}),
    )


_CF_INTERPRET_KINDS = ["median", "lower_quartile", "upper_quartile", "iqr", "threshold"]


def _interpolate(points: list[tuple[int, int]], target_cf: Fraction) -> Fraction:
    for i in range(len(points) - 1):
        (x1, y1), (x2, y2) = points[i], points[i + 1]
        if y1 <= target_cf <= y2:
            if y2 == y1:
                return Fraction(x1)
            proportion = Fraction(target_cf - y1, y2 - y1)
            return x1 + proportion * (x2 - x1)
    raise ValueError("target cumulative frequency out of range")


def _estimate_at(points: list[tuple[int, int]], target_cf: Fraction) -> Fraction:
    # Independent re-derivation via explicit "fraction of the way between the
    # two bracketing points" reasoning, structured differently from _interpolate.
    for i in range(len(points) - 1):
        (x1, y1), (x2, y2) = points[i], points[i + 1]
        if y1 <= target_cf <= y2:
            if y2 == y1:
                return Fraction(x1)
            span_y = y2 - y1
            span_x = x2 - x1
            offset = target_cf - y1
            return Fraction(x1 * span_y + offset * span_x, span_y)
    raise ValueError("target cumulative frequency out of range")


def generate_cumulative_frequency_interpret(tier: Tier, rng: random.Random) -> Question:
    x_label, context, boundaries, frequencies = _random_grouped_table(rng)
    points = _cumulative_points(boundaries, frequencies)
    total = points[-1][1]
    kind = rng.choice(_CF_INTERPRET_KINDS)

    if kind == "median":
        target = Fraction(total, 2)
        label = "median"
    elif kind == "lower_quartile":
        target = Fraction(total, 4)
        label = "lower quartile"
    elif kind == "upper_quartile":
        target = Fraction(total * 3, 4)
        label = "upper quartile"
    elif kind == "iqr":
        q1 = _interpolate(points, Fraction(total, 4))
        q3 = _interpolate(points, Fraction(total * 3, 4))
        q1_check = _estimate_at(points, Fraction(total, 4))
        q3_check = _estimate_at(points, Fraction(total * 3, 4))
        if q1 != q1_check or q3 != q3_check:
            raise ValueError("cumulative_frequency_interpret verification failed (iqr)")
        answer_val = q3 - q1
        answer = f"{float(answer_val):.1f}"
        prompt = "Use the graph to estimate the interquartile range."
        steps = [
            f"Lower quartile (at cumulative frequency {float(Fraction(total,4)):.1f}) ≈ {float(q1):.1f}.",
            f"Upper quartile (at cumulative frequency {float(Fraction(total*3,4)):.1f}) ≈ {float(q3):.1f}.",
            f"IQR = {float(q3):.1f} - {float(q1):.1f} = {answer}.",
        ]
        return Question(
            topic_id="cumulative_frequency_interpret",
            tier=Tier.HIGHER,
            prompt=f"The cumulative frequency graph shows {context}. {prompt}",
            solution_steps=tuple(steps),
            final_answer=answer,
            dedup_key=f"cf_interpret:{boundaries}:{frequencies}:{kind}",
            diagram=DiagramSpec(kind="cumulative_frequency", params={"points": points, "x_label": x_label}),
        )
    else:
        # threshold: pick one of the exact plotted upper boundaries.
        idx = rng.randrange(1, len(points))
        x_val, cf_val = points[idx]
        above = rng.random() < 0.5
        answer = str(total - cf_val if above else cf_val)
        direction = "above" if above else "below or equal to"
        prompt = f"Estimate how many values are {direction} {x_val} {x_label.split(' ')[0].lower()}."
        steps = [
            f"At {x_val}, the cumulative frequency is {cf_val} (out of {total} total).",
            f"{'Above' if above else 'Below or equal to'} that point: {answer}.",
        ]
        check = (total - cf_val if above else cf_val)
        if str(check) != answer:
            raise ValueError("cumulative_frequency_interpret verification failed (threshold)")
        return Question(
            topic_id="cumulative_frequency_interpret",
            tier=Tier.HIGHER,
            prompt=f"The cumulative frequency graph shows {context}. {prompt}",
            solution_steps=tuple(steps),
            final_answer=answer,
            dedup_key=f"cf_interpret:{boundaries}:{frequencies}:{kind}:{x_val}:{above}",
            diagram=DiagramSpec(kind="cumulative_frequency", params={"points": points, "x_label": x_label}),
        )

    estimate = _interpolate(points, target)
    estimate_check = _estimate_at(points, target)
    if estimate != estimate_check:
        raise ValueError("cumulative_frequency_interpret verification failed")
    answer = f"{float(estimate):.1f}"
    prompt = f"Use the graph to estimate the {label}."
    steps = [
        f"The {label} is at cumulative frequency {float(target):.1f} (out of {total} total).",
        f"Reading across from {float(target):.1f} to the curve, then down to the axis, gives ≈ {answer}.",
    ]
    return Question(
        topic_id="cumulative_frequency_interpret",
        tier=Tier.HIGHER,
        prompt=f"The cumulative frequency graph shows {context}. {prompt}",
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"cf_interpret:{boundaries}:{frequencies}:{kind}",
        diagram=DiagramSpec(kind="cumulative_frequency", params={"points": points, "x_label": x_label}),
    )


def generate_modelled_example_cumulative_frequency_interpret(tier: Tier, rng: random.Random) -> ModelledExample:
    q = generate_cumulative_frequency_interpret(tier, rng)
    teaching_steps = [
        "A cumulative frequency graph lets you estimate statistics like the median and quartiles "
        "without going back to the raw data - the curve already has the running totals built in.",
        "To estimate a value, find the target cumulative frequency on the vertical axis, trace "
        "across to the curve, then straight down to the horizontal axis to read the estimate.",
    ] + list(q.solution_steps)
    return ModelledExample(
        topic_id="cumulative_frequency_interpret",
        tier=Tier.HIGHER,
        prompt=q.prompt,
        worked_calculation=tuple(q.solution_steps),
        teaching_steps=tuple(teaching_steps),
        final_answer=q.final_answer,
        diagram=q.diagram,
    )


def _quartiles(data: list[int]) -> tuple[float, float, float]:
    data = sorted(data)
    n = len(data)
    median = data[n // 2] if n % 2 else Fraction(data[n // 2 - 1] + data[n // 2], 2)
    lower = data[: n // 2]
    upper = data[(n + 1) // 2 :]
    q1 = lower[len(lower) // 2] if len(lower) % 2 else Fraction(lower[len(lower) // 2 - 1] + lower[len(lower) // 2], 2)
    q3 = upper[len(upper) // 2] if len(upper) % 2 else Fraction(upper[len(upper) // 2 - 1] + upper[len(upper) // 2], 2)
    return q1, median, q3


_BOX_PLOT_CONTEXTS = ["test scores", "journey times (minutes)", "weekly pocket money (£)"]


def generate_box_plot_construct(tier: Tier, rng: random.Random) -> Question:
    context = rng.choice(_BOX_PLOT_CONTEXTS)
    n = rng.choice([7, 9, 11])
    data = sorted(rng.sample(range(1, 50), n))
    q1, median, q3 = _quartiles(data)

    # Independent check: recompute min/max via a fresh sort + indexing, and
    # q1/q3 via differently-structured slicing than `_quartiles`.
    resorted = sorted(data)
    if resorted[0] != data[0] or resorted[-1] != data[-1]:
        raise ValueError("box_plot_construct verification failed (min/max)")
    half = len(resorted) // 2
    lower_alt, upper_alt = resorted[:half], resorted[-half:]
    q1_alt = lower_alt[len(lower_alt) // 2] if len(lower_alt) % 2 else Fraction(lower_alt[len(lower_alt) // 2 - 1] + lower_alt[len(lower_alt) // 2], 2)
    q3_alt = upper_alt[len(upper_alt) // 2] if len(upper_alt) % 2 else Fraction(upper_alt[len(upper_alt) // 2 - 1] + upper_alt[len(upper_alt) // 2], 2)
    if q1_alt != q1 or q3_alt != q3:
        raise ValueError("box_plot_construct verification failed (quartiles)")

    final_answer = f"Min = {data[0]}, Q1 = {q1}, Median = {median}, Q3 = {q3}, Max = {data[-1]}"
    steps = [
        f"Sorted data: {data}.",
        f"Min = {data[0]}, Max = {data[-1]}.",
        f"Median splits the data in half; Q1 is the median of the lower half, Q3 the median of the upper half.",
        final_answer,
    ]
    return Question(
        topic_id="box_plot_construct",
        tier=Tier.HIGHER,
        prompt=f"Here are {n} {context}: {data}. Find the five-number summary (min, Q1, median, Q3, max) and draw a box plot.",
        solution_steps=tuple(steps),
        final_answer=final_answer,
        dedup_key=f"boxplot_construct:{data}",
        solution_diagram=DiagramSpec(
            kind="box_plot",
            params={"box_plots": [{"min": data[0], "q1": float(q1), "median": float(median), "q3": float(q3), "max": data[-1]}], "x_label": context.title()},
        ),
    )


def generate_modelled_example_box_plot_construct(tier: Tier, rng: random.Random) -> ModelledExample:
    q = generate_box_plot_construct(tier, rng)
    teaching_steps = [
        "A box plot is built from five key values: the minimum, the lower quartile (Q1), the median, "
        "the upper quartile (Q3), and the maximum.",
        "First sort the data, then find the median (the middle value). Q1 is the median of everything "
        "below the overall median; Q3 is the median of everything above it.",
        "Draw a box from Q1 to Q3 with a line at the median, then whiskers stretching out to the "
        "minimum and maximum values.",
    ]
    return ModelledExample(
        topic_id="box_plot_construct",
        tier=Tier.HIGHER,
        prompt=q.prompt,
        worked_calculation=tuple(q.solution_steps),
        teaching_steps=tuple(teaching_steps),
        final_answer=q.final_answer,
        diagram=q.solution_diagram,
    )


_BOX_INTERPRET_KINDS = ["median", "iqr", "range", "compare_median", "compare_iqr", "compare_range"]


def _random_box(rng: random.Random) -> dict:
    n = rng.choice([7, 9, 11])
    data = sorted(rng.sample(range(1, 50), n))
    q1, median, q3 = _quartiles(data)
    return {"min": data[0], "q1": float(q1), "median": float(median), "q3": float(q3), "max": data[-1]}


def generate_box_plot_interpret(tier: Tier, rng: random.Random) -> Question:
    context = rng.choice(_BOX_PLOT_CONTEXTS)
    compare = rng.random() < 0.5
    box_a = _random_box(rng)

    if not compare:
        kind = rng.choice(["median", "iqr", "range"])
        if kind == "median":
            answer = str(box_a["median"])
            prompt = "Find the median."
            steps = [
                "The median is marked by the line drawn inside the box.",
                f"Median = {answer}.",
            ]
            check = box_a["median"] == float(answer)
        elif kind == "iqr":
            answer = str(round(box_a["q3"] - box_a["q1"], 2))
            prompt = "Find the interquartile range."
            steps = [f"Q1 = {box_a['q1']}, Q3 = {box_a['q3']}.", f"IQR = {box_a['q3']} - {box_a['q1']} = {answer}."]
            check = round(box_a["q3"] - box_a["q1"], 2) == float(answer)
        else:
            answer = str(box_a["max"] - box_a["min"])
            prompt = "Find the range."
            steps = [f"Min = {box_a['min']}, Max = {box_a['max']}.", f"Range = {answer}."]
            check = (box_a["max"] - box_a["min"]) == int(answer)
        if not check:
            raise ValueError("box_plot_interpret verification failed")
        return Question(
            topic_id="box_plot_interpret",
            tier=Tier.HIGHER,
            prompt=f"The box plot shows {context}. {prompt}",
            solution_steps=tuple(steps),
            final_answer=answer,
            dedup_key=f"boxplot_interpret:{box_a}:{kind}",
            diagram=DiagramSpec(kind="box_plot", params={"box_plots": [box_a], "x_label": context.title()}),
        )

    box_b = _random_box(rng)
    while box_b == box_a:
        box_b = _random_box(rng)
    kind = rng.choice(["compare_median", "compare_iqr", "compare_range"])
    label_a, label_b = "Class A", "Class B"
    iqr_a, iqr_b = box_a["q3"] - box_a["q1"], box_b["q3"] - box_b["q1"]
    range_a, range_b = box_a["max"] - box_a["min"], box_b["max"] - box_b["min"]

    if kind == "compare_median":
        winner = label_a if box_a["median"] > box_b["median"] else label_b
        prompt = "Which class had the higher median?"
        steps = [f"{label_a} median = {box_a['median']}, {label_b} median = {box_b['median']}.", f"{winner} is higher."]
        check = (label_a if box_a["median"] > box_b["median"] else label_b) == winner
    elif kind == "compare_iqr":
        winner = label_a if iqr_a < iqr_b else label_b
        prompt = "Which class had the smaller interquartile range (more consistent results)?"
        steps = [f"{label_a} IQR = {iqr_a}, {label_b} IQR = {iqr_b}.", f"{winner} is smaller/more consistent."]
        check = (label_a if iqr_a < iqr_b else label_b) == winner
    else:
        winner = label_a if range_a < range_b else label_b
        prompt = "Which class had the smaller range?"
        steps = [f"{label_a} range = {range_a}, {label_b} range = {range_b}.", f"{winner} is smaller."]
        check = (label_a if range_a < range_b else label_b) == winner
    if not check:
        raise ValueError("box_plot_interpret verification failed (compare)")
    return Question(
        topic_id="box_plot_interpret",
        tier=Tier.HIGHER,
        prompt=f"The box plots compare {context} for two classes. {prompt}",
        solution_steps=tuple(steps),
        final_answer=winner,
        dedup_key=f"boxplot_compare:{box_a}:{box_b}:{kind}",
        diagram=DiagramSpec(
            kind="box_plot",
            params={
                "box_plots": [
                    {**box_a, "label": label_a},
                    {**box_b, "label": label_b},
                ],
                "x_label": context.title(),
            },
        ),
    )


def generate_modelled_example_box_plot_interpret(tier: Tier, rng: random.Random) -> ModelledExample:
    q = generate_box_plot_interpret(tier, rng)
    teaching_steps = [
        "A box plot's five key positions - the two whisker ends, the two box edges, and the median "
        "line - can be read directly off the diagram using the labelled axis.",
        "When comparing two box plots, compare the same feature (median, IQR, or range) on both "
        "before deciding which is bigger or more consistent.",
    ] + list(q.solution_steps)
    return ModelledExample(
        topic_id="box_plot_interpret",
        tier=Tier.HIGHER,
        prompt=q.prompt,
        worked_calculation=tuple(q.solution_steps),
        teaching_steps=tuple(teaching_steps),
        final_answer=q.final_answer,
        diagram=q.diagram,
    )


TOPIC_CUMULATIVE_FREQUENCY_PLOT = TopicDefinition(
    id="cumulative_frequency_plot",
    display_name="Plotting Cumulative Frequency Graphs",
    description="Build a cumulative frequency table and draw the graph.",
    generate=generate_cumulative_frequency_plot,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_cumulative_frequency_plot,
)

TOPIC_CUMULATIVE_FREQUENCY_INTERPRET = TopicDefinition(
    id="cumulative_frequency_interpret",
    display_name="Interpreting Cumulative Frequency Graphs",
    description="Estimate the median, quartiles, and IQR from a cumulative frequency graph.",
    generate=generate_cumulative_frequency_interpret,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_cumulative_frequency_interpret,
)

TOPIC_BOX_PLOT_CONSTRUCT = TopicDefinition(
    id="box_plot_construct",
    display_name="Constructing Box Plots",
    description="Find the five-number summary from raw data and draw a box plot.",
    generate=generate_box_plot_construct,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_box_plot_construct,
)

TOPIC_BOX_PLOT_INTERPRET = TopicDefinition(
    id="box_plot_interpret",
    display_name="Interpreting Box Plots",
    description="Read and compare medians, ranges, and interquartile ranges from box plots.",
    generate=generate_box_plot_interpret,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_box_plot_interpret,
)
