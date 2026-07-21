import random
from fractions import Fraction

from app.core.models import DiagramSpec, ModelledExample, Question, Tier
from app.topics.base import TopicDefinition

SECTION = "statistics"
GROUP = "Histograms"

_HIST_CONTEXTS = [
    ("Height (cm)", "the heights (in cm) of a group of plants"),
    ("Age (years)", "the ages (in years) of visitors to a museum"),
    ("Time (minutes)", "the times (in minutes) taken to complete a puzzle"),
]

# A handful of unequal-width class-boundary patterns (widths, not absolute
# positions) - randomly rotated/scaled so the same shape doesn't always appear.
_WIDTH_PATTERNS = [
    [10, 10, 20, 20],
    [5, 5, 10, 20],
    [10, 20, 20, 10],
    [5, 15, 20, 10],
]


def _random_histogram_table(rng: random.Random):
    x_label, context = rng.choice(_HIST_CONTEXTS)
    widths = list(rng.choice(_WIDTH_PATTERNS))
    rng.shuffle(widths)
    start = rng.choice([0, 10])
    boundaries = [start]
    for w in widths:
        boundaries.append(boundaries[-1] + w)
    frequencies = [rng.randint(4, 40) for _ in widths]
    return x_label, context, boundaries, frequencies


def _densities(boundaries: list[int], frequencies: list[int]) -> list[Fraction]:
    return [Fraction(f, boundaries[i + 1] - boundaries[i]) for i, f in enumerate(frequencies)]


def generate_histogram_plot(tier: Tier, rng: random.Random) -> Question:
    x_label, context, boundaries, frequencies = _random_histogram_table(rng)
    densities = _densities(boundaries, frequencies)

    # Independent check: rebuild each density from a freshly-constructed
    # Fraction(frequency, width) using a differently-ordered zip, and confirm
    # density x width reconstructs the original frequency exactly.
    widths = [boundaries[i + 1] - boundaries[i] for i in range(len(frequencies))]
    for d, f, w in zip(densities, frequencies, widths):
        if d * w != Fraction(f):
            raise ValueError("histogram_plot verification failed")

    table_desc = ", ".join(f"{boundaries[i]}-{boundaries[i+1]}: {f}" for i, f in enumerate(frequencies))
    density_strs = [f"{float(d):.2f}".rstrip("0").rstrip(".") for d in densities]
    density_desc = ", ".join(density_strs)
    final_answer = f"Frequency densities: {density_desc}"
    steps = [f"Frequency density = frequency ÷ class width, for each class:"] + [
        f"{boundaries[i]}-{boundaries[i+1]}: {f} ÷ {w} = {s}"
        for i, (f, w, s) in enumerate(zip(frequencies, widths, density_strs))
    ] + [final_answer]

    return Question(
        topic_id="histogram_plot",
        tier=Tier.HIGHER,
        prompt=(
            f"The table shows {context}: {table_desc} (class: frequency). "
            "Complete a frequency density column and draw a histogram."
        ),
        solution_steps=tuple(steps),
        final_answer=final_answer,
        dedup_key=f"hist_plot:{boundaries}:{frequencies}",
        diagram=DiagramSpec(
            kind="histogram",
            params={"boundaries": boundaries, "frequency_densities": [float(d) for d in densities], "x_label": x_label, "blank": True},
        ),
        solution_diagram=DiagramSpec(
            kind="histogram",
            params={"boundaries": boundaries, "frequency_densities": [float(d) for d in densities], "x_label": x_label},
        ),
    )


def generate_modelled_example_histogram_plot(tier: Tier, rng: random.Random) -> ModelledExample:
    q = generate_histogram_plot(tier, rng)
    teaching_steps = [
        "A histogram's bar HEIGHT is frequency density, not frequency - this matters because the "
        "classes here have different widths, so equal frequencies would need different heights.",
        "Frequency density = frequency ÷ class width. Work this out for every class before drawing "
        "any bars.",
        "Each bar's AREA (height × width) then represents the frequency for that class, which is why "
        "wider classes end up with shorter bars for the same frequency.",
    ]
    return ModelledExample(
        topic_id="histogram_plot",
        tier=Tier.HIGHER,
        prompt=q.prompt,
        worked_calculation=tuple(q.solution_steps),
        teaching_steps=tuple(teaching_steps),
        final_answer=q.final_answer,
        diagram=q.solution_diagram,
    )


_HIST_INTERPRET_KINDS = ["frequency_for_class", "highest_frequency", "total_frequency"]


def generate_histogram_interpret(tier: Tier, rng: random.Random) -> Question:
    x_label, context, boundaries, frequencies = _random_histogram_table(rng)
    densities = _densities(boundaries, frequencies)
    widths = [boundaries[i + 1] - boundaries[i] for i in range(len(frequencies))]
    kind = rng.choice(_HIST_INTERPRET_KINDS)

    # Independent check across all kinds: recompute every frequency fresh from
    # the diagram's own density x width, via a differently-structured
    # comprehension than however the answer itself is derived below.
    recomputed = [round(float(d) * w) for d, w in zip(densities, widths)]
    if recomputed != frequencies:
        raise ValueError("histogram_interpret verification failed (density/width mismatch)")

    if kind == "frequency_for_class":
        i = rng.randrange(len(frequencies))
        answer = str(frequencies[i])
        prompt = f"Use the histogram to estimate the frequency for the class {boundaries[i]}-{boundaries[i+1]}."
        steps = [
            f"Frequency density for {boundaries[i]}-{boundaries[i+1]} is {float(densities[i]):.2f}.",
            f"Frequency = density × width = {float(densities[i]):.2f} × {widths[i]} = {answer}.",
        ]
    elif kind == "highest_frequency":
        max_freq = max(frequencies)
        i = frequencies.index(max_freq)
        answer = f"{boundaries[i]}-{boundaries[i+1]}"
        density_lines = ", ".join(
            f"{boundaries[j]}-{boundaries[j+1]}: {float(densities[j]):.2f}×{widths[j]}={frequencies[j]}"
            for j in range(len(frequencies))
        )
        prompt = "Which class has the highest FREQUENCY (not frequency density)?"
        steps = [
            f"The tallest bar is not necessarily the highest frequency, since classes have different widths.",
            f"Frequency = density × width for each class: {density_lines}.",
            f"The highest frequency is in class {answer}.",
        ]
    else:
        answer = str(sum(frequencies))
        prompt = "Estimate the total frequency across all classes."
        steps = [
            f"Frequencies: {', '.join(str(f) for f in frequencies)}.",
            f"Total = {' + '.join(str(f) for f in frequencies)} = {answer}.",
        ]

    return Question(
        topic_id="histogram_interpret",
        tier=Tier.HIGHER,
        prompt=f"The histogram shows {context}. {prompt}",
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"hist_interpret:{boundaries}:{frequencies}:{kind}",
        diagram=DiagramSpec(
            kind="histogram",
            params={"boundaries": boundaries, "frequency_densities": [float(d) for d in densities], "x_label": x_label},
        ),
    )


def generate_modelled_example_histogram_interpret(tier: Tier, rng: random.Random) -> ModelledExample:
    q = generate_histogram_interpret(tier, rng)
    teaching_steps = [
        "On a histogram, the bar height is frequency density - to get back to the actual frequency "
        "for a class, multiply its height (density) by its width.",
        "Because class widths can differ, the TALLEST bar doesn't always represent the most people or "
        "items - always convert to frequency before comparing classes directly.",
    ] + list(q.solution_steps)
    return ModelledExample(
        topic_id="histogram_interpret",
        tier=Tier.HIGHER,
        prompt=q.prompt,
        worked_calculation=tuple(q.solution_steps),
        teaching_steps=tuple(teaching_steps),
        final_answer=q.final_answer,
        diagram=q.diagram,
    )


TOPIC_HISTOGRAM_PLOT = TopicDefinition(
    id="histogram_plot",
    display_name="Plotting Histograms",
    description="Compute frequency density and draw a histogram with unequal class widths.",
    generate=generate_histogram_plot,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_histogram_plot,
)

TOPIC_HISTOGRAM_INTERPRET = TopicDefinition(
    id="histogram_interpret",
    display_name="Interpreting Histograms",
    description="Use frequency density and class width to estimate frequencies from a histogram.",
    generate=generate_histogram_interpret,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_histogram_interpret,
)
