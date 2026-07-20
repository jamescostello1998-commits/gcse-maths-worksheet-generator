import random
import statistics
from fractions import Fraction

from app.core.models import ModelledExample, Question, Tier
from app.topics.base import TopicDefinition
from app.topics.number_format import fmt_money

SECTION = "statistics"
GROUP_AVERAGES = "Averages from a List"
GROUP_FREQUENCY = "Frequency Tables"
GROUP_REVERSE = "Working Backwards"


def generate_mean_and_range(tier: Tier, rng: random.Random) -> Question:
    n = rng.randint(5, 8)
    data = [rng.randint(1, 30) for _ in range(n)]
    total = sum(data)
    mean = Fraction(total, n)
    data_range = max(data) - min(data)

    # Independent verification via Python's stdlib statistics module.
    if abs(float(mean) - statistics.mean(data)) > 1e-9:
        raise ValueError("mean_and_range verification failed")

    data_str = ", ".join(str(v) for v in data)
    steps = [
        f"Mean = sum ÷ count = ({' + '.join(str(v) for v in data)}) ÷ {n} = {total} ÷ {n} = {fmt_money(mean)}",
        f"Range = largest - smallest = {max(data)} - {min(data)} = {data_range}",
    ]
    return Question(
        topic_id="stats_mean_and_range",
        tier=Tier.FOUNDATION,
        prompt=f"Find the mean and range of this list of numbers: {data_str}.",
        solution_steps=tuple(steps),
        final_answer=f"Mean = {fmt_money(mean)}, Range = {data_range}",
        dedup_key=f"mean_range:{data}",
    )


def generate_modelled_example_mean_and_range(tier: Tier, rng: random.Random) -> ModelledExample:
    n = rng.randint(5, 8)
    data = [rng.randint(1, 30) for _ in range(n)]
    total = sum(data)
    mean = Fraction(total, n)
    data_range = max(data) - min(data)

    if abs(float(mean) - statistics.mean(data)) > 1e-9:
        raise ValueError("modelled example mean_and_range verification failed")

    data_str = ", ".join(str(v) for v in data)
    teaching_steps = [
        "The mean is the everyday 'average': add up every value, then share that total equally "
        "across however many values there are.",
        f"Add up all {n} numbers: {' + '.join(str(v) for v in data)} = {total}.",
        f"Divide that total by how many numbers there are: {total} ÷ {n} = {fmt_money(mean)}. That's the mean.",
        f"The range measures how spread out the data is: it's the largest value minus the smallest "
        f"value. Largest = {max(data)}, smallest = {min(data)}, so range = {max(data)} - {min(data)} = {data_range}.",
    ]
    worked_calculation = [
        f"Mean = ({' + '.join(str(v) for v in data)}) ÷ {n}",
        f"= {total} ÷ {n} = {fmt_money(mean)}",
        f"Range = {max(data)} - {min(data)} = {data_range}",
    ]
    return ModelledExample(
        topic_id="stats_mean_and_range",
        tier=Tier.FOUNDATION,
        prompt=f"Find the mean and range of this list of numbers: {data_str}.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"Mean = {fmt_money(mean)}, Range = {data_range}",
    )


def generate_median_and_mode(tier: Tier, rng: random.Random) -> Question:
    n = rng.choice([5, 6, 7, 8])
    mode_value = rng.randint(1, 20)
    mode_count = 3
    others: list[int] = []
    while len(others) < n - mode_count:
        v = rng.randint(1, 20)
        if v != mode_value and others.count(v) < mode_count - 1:
            others.append(v)
    data = [mode_value] * mode_count + others
    rng.shuffle(data)
    sorted_data = sorted(data)

    if n % 2 == 1:
        median = Fraction(sorted_data[n // 2])
    else:
        median = Fraction(sorted_data[n // 2 - 1] + sorted_data[n // 2], 2)

    # Independent verification via Python's stdlib statistics module.
    if statistics.mode(data) != mode_value:
        raise ValueError("median_and_mode verification failed (mode)")
    if abs(float(median) - statistics.median(data)) > 1e-9:
        raise ValueError("median_and_mode verification failed (median)")

    data_str = ", ".join(str(v) for v in data)
    if n % 2 == 1:
        median_step = f"Sort the data: {', '.join(str(v) for v in sorted_data)}. The middle value is {sorted_data[n // 2]}."
    else:
        median_step = (
            f"Sort the data: {', '.join(str(v) for v in sorted_data)}. "
            f"The middle two values are {sorted_data[n // 2 - 1]} and {sorted_data[n // 2]}, "
            f"so the median = ({sorted_data[n // 2 - 1]} + {sorted_data[n // 2]}) ÷ 2 = {fmt_money(median)}."
        )
    steps = [
        median_step,
        f"Mode = the most frequent value = {mode_value} (appears {mode_count} times)",
    ]
    return Question(
        topic_id="stats_median_and_mode",
        tier=Tier.FOUNDATION,
        prompt=f"Find the median and mode of this list of numbers: {data_str}.",
        solution_steps=tuple(steps),
        final_answer=f"Median = {fmt_money(median)}, Mode = {mode_value}",
        dedup_key=f"median_mode:{data}",
    )


def generate_mean_frequency_table(tier: Tier, rng: random.Random) -> Question:
    n_values = rng.randint(4, 6)
    values = list(range(n_values))
    frequencies = [rng.randint(2, 10) for _ in values]
    total_freq = sum(frequencies)
    weighted_sum = sum(v * f for v, f in zip(values, frequencies))
    mean = Fraction(weighted_sum, total_freq)

    # Independent verification: expand to a flat list and recompute via stdlib.
    flat = [v for v, f in zip(values, frequencies) for _ in range(f)]
    if abs(float(mean) - statistics.mean(flat)) > 1e-9:
        raise ValueError("mean_frequency_table verification failed")

    table_desc = ", ".join(f"{v} ({f} times)" for v, f in zip(values, frequencies))
    product_terms = " + ".join(f"{v}×{f}" for v, f in zip(values, frequencies))
    steps = [
        f"Multiply each value by its frequency and sum: {product_terms} = {weighted_sum}",
        f"Total frequency = {' + '.join(str(f) for f in frequencies)} = {total_freq}",
        f"Mean = {weighted_sum} ÷ {total_freq} = {fmt_money(mean)}",
    ]
    return Question(
        topic_id="stats_mean_frequency_table",
        tier=Tier.FOUNDATION,
        prompt=(
            "A survey recorded the number of pets owned by each household: "
            f"{table_desc}. Find the mean number of pets."
        ),
        solution_steps=tuple(steps),
        final_answer=fmt_money(mean),
        dedup_key=f"freq_table:{values}:{frequencies}",
    )


def generate_mean_grouped_frequency_table(tier: Tier, rng: random.Random) -> Question:
    n_classes = rng.randint(4, 5)
    class_width = rng.choice([10, 20])
    start = rng.choice([0, 10, 20])
    classes = [(start + i * class_width, start + (i + 1) * class_width - 1) for i in range(n_classes)]
    midpoints = [Fraction(lo + hi, 2) for lo, hi in classes]
    frequencies = [rng.randint(2, 10) for _ in range(n_classes)]
    total_freq = sum(frequencies)
    weighted_sum = sum(m * f for m, f in zip(midpoints, frequencies))
    mean = weighted_sum / total_freq

    # Independent verification: expand midpoints to a flat list and recompute via stdlib,
    # plus a sanity check that the estimate lies within the overall data range.
    flat = [float(m) for m, f in zip(midpoints, frequencies) for _ in range(f)]
    if abs(float(mean) - statistics.mean(flat)) > 1e-9:
        raise ValueError("mean_grouped_frequency_table verification failed")
    if not (float(midpoints[0]) <= float(mean) <= float(midpoints[-1])):
        raise ValueError("mean_grouped_frequency_table produced an out-of-range estimate")

    table_desc = ", ".join(f"{lo}-{hi} ({f})" for (lo, hi), f in zip(classes, frequencies))
    midpoint_terms = " + ".join(f"{fmt_money(m)}×{f}" for m, f in zip(midpoints, frequencies))
    steps = [
        f"Midpoints of each class: {', '.join(fmt_money(m) for m in midpoints)}",
        f"Sum of (midpoint × frequency): {midpoint_terms} = {fmt_money(weighted_sum)}",
        f"Total frequency = {' + '.join(str(f) for f in frequencies)} = {total_freq}",
        f"Estimated mean = {fmt_money(weighted_sum)} ÷ {total_freq} = {fmt_money(mean)}",
    ]
    return Question(
        topic_id="stats_mean_grouped_frequency_table",
        tier=Tier.HIGHER,
        prompt=(
            "The table shows the times (in minutes) taken by a group of runners: "
            f"{table_desc} (class: frequency). Find an estimate of the mean time."
        ),
        solution_steps=tuple(steps),
        final_answer=f"≈ {fmt_money(mean)}",
        dedup_key=f"grouped_freq:{classes}:{frequencies}",
    )


def generate_reverse_mean(tier: Tier, rng: random.Random) -> Question:
    for _ in range(200):
        n = rng.randint(4, 6)
        mean_value = rng.randint(5, 20)
        known = [rng.randint(1, 30) for _ in range(n - 1)]
        total_required = mean_value * n
        missing = total_required - sum(known)
        if 1 <= missing <= 50:
            break
    else:
        raise ValueError("reverse_mean could not find valid parameters")

    full = known + [missing]
    if Fraction(sum(full), n) != mean_value:
        raise ValueError("reverse_mean verification failed (exact)")
    # Independent verification via Python's stdlib statistics module.
    if abs(statistics.mean(full) - mean_value) > 1e-9:
        raise ValueError("reverse_mean verification failed (stdlib)")

    known_str = ", ".join(str(v) for v in known)
    steps = [
        f"Total of all {n} numbers = mean × count = {mean_value} × {n} = {total_required}",
        f"Sum of the known numbers = {' + '.join(str(v) for v in known)} = {sum(known)}",
        f"Missing number = {total_required} - {sum(known)} = {missing}",
    ]
    return Question(
        topic_id="stats_reverse_mean",
        tier=Tier.HIGHER,
        prompt=(
            f"The mean of {n} numbers is {mean_value}. {n - 1} of the numbers are {known_str}. "
            "Find the missing number."
        ),
        solution_steps=tuple(steps),
        final_answer=str(missing),
        dedup_key=f"reverse_mean:{known}:{mean_value}",
    )


TOPIC_MEAN_AND_RANGE = TopicDefinition(
    id="stats_mean_and_range",
    display_name="Mean & Range",
    description="Find the mean and range of a list of numbers.",
    generate=generate_mean_and_range,
    section=SECTION,
    group=GROUP_AVERAGES,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_mean_and_range,
)

TOPIC_MEDIAN_AND_MODE = TopicDefinition(
    id="stats_median_and_mode",
    display_name="Median & Mode",
    description="Find the median and mode of a list of numbers.",
    generate=generate_median_and_mode,
    section=SECTION,
    group=GROUP_AVERAGES,
    fixed_tier=Tier.FOUNDATION,
)

TOPIC_MEAN_FREQUENCY_TABLE = TopicDefinition(
    id="stats_mean_frequency_table",
    display_name="Mean from a Frequency Table",
    description="Find the mean of discrete data presented in a frequency table.",
    generate=generate_mean_frequency_table,
    section=SECTION,
    group=GROUP_FREQUENCY,
    fixed_tier=Tier.FOUNDATION,
)

TOPIC_MEAN_GROUPED_FREQUENCY_TABLE = TopicDefinition(
    id="stats_mean_grouped_frequency_table",
    display_name="Mean from a Grouped Frequency Table",
    description="Estimate the mean of grouped/continuous data using class midpoints.",
    generate=generate_mean_grouped_frequency_table,
    section=SECTION,
    group=GROUP_FREQUENCY,
    fixed_tier=Tier.HIGHER,
)

TOPIC_REVERSE_MEAN = TopicDefinition(
    id="stats_reverse_mean",
    display_name="Reverse Mean",
    description="Find a missing value given the mean of a set of numbers.",
    generate=generate_reverse_mean,
    section=SECTION,
    group=GROUP_REVERSE,
    fixed_tier=Tier.HIGHER,
)
