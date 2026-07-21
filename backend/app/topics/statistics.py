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


def _random_stat_list(rng: random.Random) -> list[int]:
    """A small random integer data set, used by the single-statistic topics
    (mean/mode/median/range) and their combined variant."""
    n = rng.randint(5, 8)
    return [rng.randint(1, 30) for _ in range(n)]


def _random_mode_list(rng: random.Random) -> tuple[list[int], int]:
    """A small random integer data set with a well-defined single mode: one
    value forced to appear exactly `mode_count` times, with every other value
    appearing fewer times, then shuffled. Returns the shuffled data alongside
    the known mode value so callers can cross-check against
    `statistics.mode` without recomputing it themselves."""
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
    return data, mode_value


def generate_mean(tier: Tier, rng: random.Random) -> Question:
    data = _random_stat_list(rng)
    n = len(data)
    total = sum(data)
    mean = Fraction(total, n)

    # Independent verification via Python's stdlib statistics module.
    if abs(float(mean) - statistics.mean(data)) > 1e-9:
        raise ValueError("mean verification failed")

    data_str = ", ".join(str(v) for v in data)
    steps = [
        f"Mean = sum ÷ count = ({' + '.join(str(v) for v in data)}) ÷ {n} = {total} ÷ {n} = {fmt_money(mean)}",
    ]
    return Question(
        topic_id="stats_mean",
        tier=Tier.FOUNDATION,
        prompt=f"Find the mean of this data set: {data_str}.",
        solution_steps=tuple(steps),
        final_answer=fmt_money(mean),
        dedup_key=f"mean:{data}",
    )


def generate_modelled_example_mean(tier: Tier, rng: random.Random) -> ModelledExample:
    data = _random_stat_list(rng)
    n = len(data)
    total = sum(data)
    mean = Fraction(total, n)

    if abs(float(mean) - statistics.mean(data)) > 1e-9:
        raise ValueError("modelled example mean verification failed")

    data_str = ", ".join(str(v) for v in data)
    teaching_steps = [
        "The mean is the everyday 'average': add up every value, then share that total equally "
        "across however many values there are.",
        f"Add up all {n} numbers: {' + '.join(str(v) for v in data)} = {total}.",
        f"Divide that total by how many numbers there are: {total} ÷ {n} = {fmt_money(mean)}. That's the mean.",
    ]
    worked_calculation = [
        f"Mean = ({' + '.join(str(v) for v in data)}) ÷ {n}",
        f"= {total} ÷ {n} = {fmt_money(mean)}",
    ]
    return ModelledExample(
        topic_id="stats_mean",
        tier=Tier.FOUNDATION,
        prompt=f"Find the mean of this data set: {data_str}.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=fmt_money(mean),
    )


def generate_mode(tier: Tier, rng: random.Random) -> Question:
    data, mode_value = _random_mode_list(rng)

    # Independent verification via Python's stdlib statistics module.
    if statistics.mode(data) != mode_value:
        raise ValueError("mode verification failed")

    data_str = ", ".join(str(v) for v in data)
    steps = [
        f"Count how often each value appears. {mode_value} appears 3 times, more than any other value.",
        f"Mode = the most frequent value = {mode_value}",
    ]
    return Question(
        topic_id="stats_mode",
        tier=Tier.FOUNDATION,
        prompt=f"Find the mode of this data set: {data_str}.",
        solution_steps=tuple(steps),
        final_answer=str(mode_value),
        dedup_key=f"mode:{data}",
    )


def generate_modelled_example_mode(tier: Tier, rng: random.Random) -> ModelledExample:
    data, mode_value = _random_mode_list(rng)

    if statistics.mode(data) != mode_value:
        raise ValueError("modelled example mode verification failed")

    data_str = ", ".join(str(v) for v in data)
    teaching_steps = [
        "The mode is simply the value that appears most often in the data set - unlike the mean or "
        "median, it doesn't involve any adding, dividing, or sorting by size.",
        "Go through the list and count how many times each different value occurs.",
        f"Here {mode_value} appears 3 times, which is more than any other value appears, so {mode_value} "
        "is the mode.",
    ]
    worked_calculation = [
        f"{mode_value} appears 3 times (most of any value)",
        f"Mode = {mode_value}",
    ]
    return ModelledExample(
        topic_id="stats_mode",
        tier=Tier.FOUNDATION,
        prompt=f"Find the mode of this data set: {data_str}.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=str(mode_value),
    )


def generate_median(tier: Tier, rng: random.Random) -> Question:
    data = _random_stat_list(rng)
    n = len(data)
    sorted_data = sorted(data)

    if n % 2 == 1:
        median = Fraction(sorted_data[n // 2])
    else:
        median = Fraction(sorted_data[n // 2 - 1] + sorted_data[n // 2], 2)

    # Independent verification via Python's stdlib statistics module.
    if abs(float(median) - statistics.median(data)) > 1e-9:
        raise ValueError("median verification failed")

    data_str = ", ".join(str(v) for v in data)
    if n % 2 == 1:
        median_step = f"Sort the data: {', '.join(str(v) for v in sorted_data)}. The middle value is {sorted_data[n // 2]}."
    else:
        median_step = (
            f"Sort the data: {', '.join(str(v) for v in sorted_data)}. "
            f"The middle two values are {sorted_data[n // 2 - 1]} and {sorted_data[n // 2]}, "
            f"so the median = ({sorted_data[n // 2 - 1]} + {sorted_data[n // 2]}) ÷ 2 = {fmt_money(median)}."
        )
    steps = [median_step]
    return Question(
        topic_id="stats_median",
        tier=Tier.FOUNDATION,
        prompt=f"Find the median of this data set: {data_str}.",
        solution_steps=tuple(steps),
        final_answer=fmt_money(median),
        dedup_key=f"median:{data}",
    )


def generate_modelled_example_median(tier: Tier, rng: random.Random) -> ModelledExample:
    data = _random_stat_list(rng)
    n = len(data)
    sorted_data = sorted(data)

    if n % 2 == 1:
        median = Fraction(sorted_data[n // 2])
    else:
        median = Fraction(sorted_data[n // 2 - 1] + sorted_data[n // 2], 2)

    if abs(float(median) - statistics.median(data)) > 1e-9:
        raise ValueError("modelled example median verification failed")

    data_str = ", ".join(str(v) for v in data)
    sorted_str = ", ".join(str(v) for v in sorted_data)
    if n % 2 == 1:
        median_teaching = (
            f"Since there are {n} values (an odd number), there's a single middle value once the "
            f"list is sorted: {sorted_data[n // 2]}. That's the median - no averaging needed."
        )
        median_calc = f"Sorted: {sorted_str}. Middle value = {sorted_data[n // 2]}"
    else:
        median_teaching = (
            f"Since there are {n} values (an even number), there's no single middle value - the two "
            f"values either side of the middle are {sorted_data[n // 2 - 1]} and {sorted_data[n // 2]}, "
            f"so the median is their average: ({sorted_data[n // 2 - 1]} + {sorted_data[n // 2]}) ÷ 2 = {fmt_money(median)}."
        )
        median_calc = (
            f"Sorted: {sorted_str}. Median = ({sorted_data[n // 2 - 1]} + {sorted_data[n // 2]}) ÷ 2 = {fmt_money(median)}"
        )

    teaching_steps = [
        "The median is the middle value once the data is written in order, so the very first job is "
        "to sort the list from smallest to largest - never read the median off an unsorted list.",
        median_teaching,
        "If there's an odd number of values there's a single middle one; if there's an even number, "
        "the median is the average of the two values either side of the middle.",
    ]
    worked_calculation = [
        f"Sorted: {sorted_str}",
        median_calc,
    ]
    return ModelledExample(
        topic_id="stats_median",
        tier=Tier.FOUNDATION,
        prompt=f"Find the median of this data set: {data_str}.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=fmt_money(median),
    )


def generate_range(tier: Tier, rng: random.Random) -> Question:
    data = _random_stat_list(rng)
    data_range = max(data) - min(data)

    # Independent verification: sort ascending and take last-minus-first,
    # a genuinely separate route from calling max()/min() on the raw list.
    s = sorted(data)
    check_range = s[-1] - s[0]
    if data_range != check_range:
        raise ValueError("range verification failed")

    data_str = ", ".join(str(v) for v in data)
    steps = [
        f"Range = largest - smallest = {max(data)} - {min(data)} = {data_range}",
    ]
    return Question(
        topic_id="stats_range",
        tier=Tier.FOUNDATION,
        prompt=f"Find the range of this data set: {data_str}.",
        solution_steps=tuple(steps),
        final_answer=str(data_range),
        dedup_key=f"range:{data}",
    )


def generate_modelled_example_range(tier: Tier, rng: random.Random) -> ModelledExample:
    data = _random_stat_list(rng)
    data_range = max(data) - min(data)

    s = sorted(data)
    check_range = s[-1] - s[0]
    if data_range != check_range:
        raise ValueError("modelled example range verification failed")

    data_str = ", ".join(str(v) for v in data)
    teaching_steps = [
        "The range measures how spread out a data set is - it doesn't involve adding or averaging, "
        "just the two most extreme values.",
        f"Find the largest value ({max(data)}) and the smallest value ({min(data)}) in the list.",
        f"Range = largest - smallest = {max(data)} - {min(data)} = {data_range}.",
    ]
    worked_calculation = [
        f"Largest = {max(data)}, smallest = {min(data)}",
        f"Range = {max(data)} - {min(data)} = {data_range}",
    ]
    return ModelledExample(
        topic_id="stats_range",
        tier=Tier.FOUNDATION,
        prompt=f"Find the range of this data set: {data_str}.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=str(data_range),
    )


def generate_averages_combined(tier: Tier, rng: random.Random) -> Question:
    data, mode_value = _random_mode_list(rng)
    n = len(data)
    total = sum(data)
    mean = Fraction(total, n)
    sorted_data = sorted(data)
    if n % 2 == 1:
        median = Fraction(sorted_data[n // 2])
    else:
        median = Fraction(sorted_data[n // 2 - 1] + sorted_data[n // 2], 2)
    data_range = max(data) - min(data)

    # Independent verification, each stat cross-checked its own way.
    if abs(float(mean) - statistics.mean(data)) > 1e-9:
        raise ValueError("averages_combined verification failed (mean)")
    if statistics.mode(data) != mode_value:
        raise ValueError("averages_combined verification failed (mode)")
    if abs(float(median) - statistics.median(data)) > 1e-9:
        raise ValueError("averages_combined verification failed (median)")
    check_range = sorted_data[-1] - sorted_data[0]
    if data_range != check_range:
        raise ValueError("averages_combined verification failed (range)")

    data_str = ", ".join(str(v) for v in data)
    if n % 2 == 1:
        median_step = f"Sorted: {', '.join(str(v) for v in sorted_data)}. Middle value = {sorted_data[n // 2]}."
    else:
        median_step = (
            f"Sorted: {', '.join(str(v) for v in sorted_data)}. "
            f"Middle two values are {sorted_data[n // 2 - 1]} and {sorted_data[n // 2]}, "
            f"so median = ({sorted_data[n // 2 - 1]} + {sorted_data[n // 2]}) ÷ 2 = {fmt_money(median)}."
        )
    steps = [
        f"(a) Mean = ({' + '.join(str(v) for v in data)}) ÷ {n} = {total} ÷ {n} = {fmt_money(mean)}",
        f"(b) Mode = the most frequent value = {mode_value} (appears 3 times)",
        f"(c) Median: {median_step}",
        f"(d) Range = {max(data)} - {min(data)} = {data_range}",
    ]
    return Question(
        topic_id="stats_averages_combined",
        tier=Tier.FOUNDATION,
        prompt=(
            "For this data set, find (a) the mean (b) the mode (c) the median (d) the range: "
            f"{data_str}."
        ),
        solution_steps=tuple(steps),
        final_answer=f"Mean = {fmt_money(mean)}, Mode = {mode_value}, Median = {fmt_money(median)}, Range = {data_range}",
        dedup_key=f"averages_combined:{data}",
    )


def generate_modelled_example_averages_combined(tier: Tier, rng: random.Random) -> ModelledExample:
    data, mode_value = _random_mode_list(rng)
    n = len(data)
    total = sum(data)
    mean = Fraction(total, n)
    sorted_data = sorted(data)
    if n % 2 == 1:
        median = Fraction(sorted_data[n // 2])
    else:
        median = Fraction(sorted_data[n // 2 - 1] + sorted_data[n // 2], 2)
    data_range = max(data) - min(data)

    if abs(float(mean) - statistics.mean(data)) > 1e-9:
        raise ValueError("modelled example averages_combined verification failed (mean)")
    if statistics.mode(data) != mode_value:
        raise ValueError("modelled example averages_combined verification failed (mode)")
    if abs(float(median) - statistics.median(data)) > 1e-9:
        raise ValueError("modelled example averages_combined verification failed (median)")
    check_range = sorted_data[-1] - sorted_data[0]
    if data_range != check_range:
        raise ValueError("modelled example averages_combined verification failed (range)")

    data_str = ", ".join(str(v) for v in data)
    sorted_str = ", ".join(str(v) for v in sorted_data)
    if n % 2 == 1:
        median_calc = f"Sorted: {sorted_str}. Middle value = {sorted_data[n // 2]}"
    else:
        median_calc = (
            f"Sorted: {sorted_str}. Median = ({sorted_data[n // 2 - 1]} + {sorted_data[n // 2]}) ÷ 2 = {fmt_money(median)}"
        )

    teaching_steps = [
        "This question asks for four different summary statistics from the same data set - it's worth "
        "keeping them straight, since each measures something different and a mix-up is a common exam slip.",
        f"Mean: add every value and divide by how many there are - ({' + '.join(str(v) for v in data)}) "
        f"÷ {n} = {total} ÷ {n} = {fmt_money(mean)}.",
        f"Mode: the most frequently occurring value - here {mode_value} appears 3 times, more than any "
        "other value.",
        "Median: sort the data first, then take the middle value (or the average of the middle two if "
        f"there's an even count) - {median_calc}.",
        f"Range: the largest value minus the smallest - {max(data)} - {min(data)} = {data_range}. It "
        "measures spread, not a 'typical' value like the other three.",
    ]
    worked_calculation = [
        f"Mean = {total} ÷ {n} = {fmt_money(mean)}",
        f"Mode = {mode_value}",
        median_calc,
        f"Range = {max(data)} - {min(data)} = {data_range}",
    ]
    return ModelledExample(
        topic_id="stats_averages_combined",
        tier=Tier.FOUNDATION,
        prompt=(
            "For this data set, find (a) the mean (b) the mode (c) the median (d) the range: "
            f"{data_str}."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"Mean = {fmt_money(mean)}, Mode = {mode_value}, Median = {fmt_money(median)}, Range = {data_range}",
    )


def generate_interquartile_range(tier: Tier, rng: random.Random) -> Question:
    n = rng.randint(7, 11)
    data = [rng.randint(1, 40) for _ in range(n)]
    sorted_data = sorted(data)
    mid = n // 2
    lower_half = sorted_data[:mid]
    upper_half = sorted_data[mid:] if n % 2 == 0 else sorted_data[mid + 1 :]

    def _median_frac(vals: list[int]) -> Fraction:
        m = len(vals)
        if m % 2 == 1:
            return Fraction(vals[m // 2])
        return Fraction(vals[m // 2 - 1] + vals[m // 2], 2)

    q1 = _median_frac(lower_half)
    q3 = _median_frac(upper_half)
    iqr = q3 - q1

    # Independent verification: recompute the lower/upper halves via a
    # differently-structured enumerate-based filter (not slicing), then
    # cross-check the medians via stdlib statistics.median rather than the
    # hand-rolled _median_frac helper above.
    upper_start = mid + 1 if n % 2 == 1 else mid
    lower_check = [v for i, v in enumerate(sorted_data) if i < mid]
    upper_check = [v for i, v in enumerate(sorted_data) if i >= upper_start]
    if lower_check != lower_half or upper_check != upper_half:
        raise ValueError("interquartile_range half-split mismatch")
    if abs(float(q1) - statistics.median(lower_check)) > 1e-9:
        raise ValueError("interquartile_range verification failed (q1)")
    if abs(float(q3) - statistics.median(upper_check)) > 1e-9:
        raise ValueError("interquartile_range verification failed (q3)")

    data_str = ", ".join(str(v) for v in data)
    sorted_str = ", ".join(str(v) for v in sorted_data)
    steps = [
        f"Sort the data: {sorted_str}.",
        f"Split into a lower half {lower_half} and an upper half {upper_half} "
        f"(excluding the overall middle value when {n} is odd).",
        f"Q1 = median of the lower half = {fmt_money(q1)}",
        f"Q3 = median of the upper half = {fmt_money(q3)}",
        f"Interquartile range = Q3 - Q1 = {fmt_money(q3)} - {fmt_money(q1)} = {fmt_money(iqr)}",
    ]
    return Question(
        topic_id="stats_interquartile_range",
        tier=Tier.HIGHER,
        prompt=f"Find the interquartile range (IQR) of this data set: {data_str}.",
        solution_steps=tuple(steps),
        final_answer=fmt_money(iqr),
        dedup_key=f"iqr:{data}",
    )


def generate_modelled_example_interquartile_range(tier: Tier, rng: random.Random) -> ModelledExample:
    n = rng.randint(7, 11)
    data = [rng.randint(1, 40) for _ in range(n)]
    sorted_data = sorted(data)
    mid = n // 2
    lower_half = sorted_data[:mid]
    upper_half = sorted_data[mid:] if n % 2 == 0 else sorted_data[mid + 1 :]

    def _median_frac(vals: list[int]) -> Fraction:
        m = len(vals)
        if m % 2 == 1:
            return Fraction(vals[m // 2])
        return Fraction(vals[m // 2 - 1] + vals[m // 2], 2)

    q1 = _median_frac(lower_half)
    q3 = _median_frac(upper_half)
    iqr = q3 - q1

    upper_start = mid + 1 if n % 2 == 1 else mid
    lower_check = [v for i, v in enumerate(sorted_data) if i < mid]
    upper_check = [v for i, v in enumerate(sorted_data) if i >= upper_start]
    if lower_check != lower_half or upper_check != upper_half:
        raise ValueError("modelled example interquartile_range half-split mismatch")
    if abs(float(q1) - statistics.median(lower_check)) > 1e-9:
        raise ValueError("modelled example interquartile_range verification failed (q1)")
    if abs(float(q3) - statistics.median(upper_check)) > 1e-9:
        raise ValueError("modelled example interquartile_range verification failed (q3)")

    data_str = ", ".join(str(v) for v in data)
    sorted_str = ", ".join(str(v) for v in sorted_data)
    teaching_steps = [
        "The interquartile range (IQR) measures the spread of the MIDDLE 50% of the data, which makes "
        "it more resistant to a single extreme outlier than the ordinary range.",
        f"Start by sorting the data: {sorted_str}. Quartiles only make sense once the data is in order.",
        f"The median splits the data into a lower half and an upper half - here that's {lower_half} "
        f"and {upper_half} (the overall middle value is left out of both halves, since {n} is odd)"
        if n % 2 == 1
        else f"The median splits the data exactly in half - here that's {lower_half} and {upper_half}.",
        f"Q1 (the lower quartile) is the median of the lower half = {fmt_money(q1)}. Q3 (the upper "
        f"quartile) is the median of the upper half = {fmt_money(q3)}.",
        f"IQR = Q3 - Q1 = {fmt_money(q3)} - {fmt_money(q1)} = {fmt_money(iqr)}.",
    ]
    worked_calculation = [
        f"Sorted: {sorted_str}",
        f"Q1 = median of {lower_half} = {fmt_money(q1)}",
        f"Q3 = median of {upper_half} = {fmt_money(q3)}",
        f"IQR = {fmt_money(q3)} - {fmt_money(q1)} = {fmt_money(iqr)}",
    ]
    return ModelledExample(
        topic_id="stats_interquartile_range",
        tier=Tier.HIGHER,
        prompt=f"Find the interquartile range (IQR) of this data set: {data_str}.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=fmt_money(iqr),
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


def generate_modelled_example_mean_frequency_table(tier: Tier, rng: random.Random) -> ModelledExample:
    n_values = rng.randint(4, 6)
    values = list(range(n_values))
    frequencies = [rng.randint(2, 10) for _ in values]
    total_freq = sum(frequencies)
    weighted_sum = sum(v * f for v, f in zip(values, frequencies))
    mean = Fraction(weighted_sum, total_freq)

    # Independent verification: expand to a flat list and recompute via stdlib.
    flat = [v for v, f in zip(values, frequencies) for _ in range(f)]
    if abs(float(mean) - statistics.mean(flat)) > 1e-9:
        raise ValueError("modelled example mean_frequency_table verification failed")

    table_desc = ", ".join(f"{v} ({f} times)" for v, f in zip(values, frequencies))
    product_terms = " + ".join(f"{v}×{f}" for v, f in zip(values, frequencies))

    teaching_steps = [
        "A frequency table is just a shorthand for a long list of data - 'value 0, 3 times' means the "
        "value 0 appears three separate times in the underlying list, and so on for every row.",
        "To find the mean, you can't just average the values shown in the table - you have to account "
        "for how often each one occurs, otherwise a rare value counts the same as a common one.",
        f"So multiply each value by its frequency (this gives the total contributed by that row), then "
        f"add all those products together: {product_terms} = {weighted_sum}. This is the same as adding "
        f"up every single number in the full, expanded list.",
        f"Then divide by the total number of data items - not the number of rows in the table, but the "
        f"sum of the frequencies: {' + '.join(str(f) for f in frequencies)} = {total_freq}. "
        f"Mean = {weighted_sum} ÷ {total_freq} = {fmt_money(mean)}.",
    ]
    worked_calculation = [
        f"Σ(value × frequency) = {product_terms} = {weighted_sum}",
        f"Σ(frequency) = {' + '.join(str(f) for f in frequencies)} = {total_freq}",
        f"Mean = {weighted_sum} ÷ {total_freq} = {fmt_money(mean)}",
    ]
    return ModelledExample(
        topic_id="stats_mean_frequency_table",
        tier=Tier.FOUNDATION,
        prompt=(
            "A survey recorded the number of pets owned by each household: "
            f"{table_desc}. Find the mean number of pets."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=fmt_money(mean),
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


def generate_modelled_example_mean_grouped_frequency_table(tier: Tier, rng: random.Random) -> ModelledExample:
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
        raise ValueError("modelled example mean_grouped_frequency_table verification failed")
    if not (float(midpoints[0]) <= float(mean) <= float(midpoints[-1])):
        raise ValueError("modelled example mean_grouped_frequency_table produced an out-of-range estimate")

    table_desc = ", ".join(f"{lo}-{hi} ({f})" for (lo, hi), f in zip(classes, frequencies))
    midpoint_terms = " + ".join(f"{fmt_money(m)}×{f}" for m, f in zip(midpoints, frequencies))

    teaching_steps = [
        "With grouped data you don't know the exact value of each item any more - you only know which "
        "class it falls into - so you can't find the exact mean. Instead you find an ESTIMATE of the mean.",
        f"To estimate, assume every value in a class sits at that class's midpoint. For example the "
        f"class {classes[0][0]}-{classes[0][1]} gets treated as if all {frequencies[0]} of its values "
        f"were exactly {fmt_money(midpoints[0])}, the halfway point of that class.",
        f"From there it's the same method as an ordinary frequency table: multiply each midpoint by its "
        f"frequency, sum the results ({midpoint_terms} = {fmt_money(weighted_sum)}), then divide by the "
        f"total frequency ({' + '.join(str(f) for f in frequencies)} = {total_freq}).",
        f"Estimated mean = {fmt_money(weighted_sum)} ÷ {total_freq} = {fmt_money(mean)}. Because it's built "
        "from midpoints rather than real values, this is always called an ESTIMATE of the mean, not the exact mean.",
    ]
    worked_calculation = [
        f"Midpoints: {', '.join(fmt_money(m) for m in midpoints)}",
        f"Σ(midpoint × frequency) = {midpoint_terms} = {fmt_money(weighted_sum)}",
        f"Σ(frequency) = {' + '.join(str(f) for f in frequencies)} = {total_freq}",
        f"Estimated mean = {fmt_money(weighted_sum)} ÷ {total_freq} = {fmt_money(mean)}",
    ]
    return ModelledExample(
        topic_id="stats_mean_grouped_frequency_table",
        tier=Tier.HIGHER,
        prompt=(
            "The table shows the times (in minutes) taken by a group of runners: "
            f"{table_desc} (class: frequency). Find an estimate of the mean time."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"≈ {fmt_money(mean)}",
    )


def generate_mean_grouped_frequency_table_foundation(tier: Tier, rng: random.Random) -> Question:
    n_classes = 3
    class_width = 10
    start = 0
    classes = [(start + i * class_width, start + (i + 1) * class_width - 1) for i in range(n_classes)]
    midpoints = [Fraction(lo + hi, 2) for lo, hi in classes]
    frequencies = [rng.randint(2, 8) for _ in range(n_classes)]
    total_freq = sum(frequencies)
    weighted_sum = sum(m * f for m, f in zip(midpoints, frequencies))
    mean = weighted_sum / total_freq

    flat = [float(m) for m, f in zip(midpoints, frequencies) for _ in range(f)]
    if abs(float(mean) - statistics.mean(flat)) > 1e-9:
        raise ValueError("mean_grouped_frequency_table_foundation verification failed")
    if not (float(midpoints[0]) <= float(mean) <= float(midpoints[-1])):
        raise ValueError("mean_grouped_frequency_table_foundation produced an out-of-range estimate")

    table_desc = ", ".join(f"{lo}-{hi} ({f})" for (lo, hi), f in zip(classes, frequencies))
    midpoint_terms = " + ".join(f"{fmt_money(m)}×{f}" for m, f in zip(midpoints, frequencies))
    steps = [
        f"Midpoints of each class: {', '.join(fmt_money(m) for m in midpoints)}",
        f"Sum of (midpoint × frequency): {midpoint_terms} = {fmt_money(weighted_sum)}",
        f"Total frequency = {' + '.join(str(f) for f in frequencies)} = {total_freq}",
        f"Estimated mean = {fmt_money(weighted_sum)} ÷ {total_freq} = {fmt_money(mean)}",
    ]
    return Question(
        topic_id="stats_mean_grouped_frequency_table_foundation",
        tier=Tier.FOUNDATION,
        prompt=(
            "The table shows the times (in minutes) taken by a group of runners: "
            f"{table_desc} (class: frequency). Find an estimate of the mean time."
        ),
        solution_steps=tuple(steps),
        final_answer=f"≈ {fmt_money(mean)}",
        dedup_key=f"grouped_freq_f:{frequencies}",
    )


def generate_modelled_example_mean_grouped_frequency_table_foundation(
    tier: Tier, rng: random.Random
) -> ModelledExample:
    n_classes = 3
    class_width = 10
    start = 0
    classes = [(start + i * class_width, start + (i + 1) * class_width - 1) for i in range(n_classes)]
    midpoints = [Fraction(lo + hi, 2) for lo, hi in classes]
    frequencies = [rng.randint(2, 8) for _ in range(n_classes)]
    total_freq = sum(frequencies)
    weighted_sum = sum(m * f for m, f in zip(midpoints, frequencies))
    mean = weighted_sum / total_freq

    flat = [float(m) for m, f in zip(midpoints, frequencies) for _ in range(f)]
    if abs(float(mean) - statistics.mean(flat)) > 1e-9:
        raise ValueError("modelled example mean_grouped_frequency_table_foundation verification failed")
    if not (float(midpoints[0]) <= float(mean) <= float(midpoints[-1])):
        raise ValueError(
            "modelled example mean_grouped_frequency_table_foundation produced an out-of-range estimate"
        )

    table_desc = ", ".join(f"{lo}-{hi} ({f})" for (lo, hi), f in zip(classes, frequencies))
    midpoint_terms = " + ".join(f"{fmt_money(m)}×{f}" for m, f in zip(midpoints, frequencies))

    teaching_steps = [
        "With grouped data you don't know the exact value of each item any more - you only know which "
        "class it falls into - so you can't find the exact mean. Instead you find an ESTIMATE of the mean.",
        f"To estimate, assume every value in a class sits at that class's midpoint. For example the "
        f"class {classes[0][0]}-{classes[0][1]} gets treated as if all {frequencies[0]} of its values "
        f"were exactly {fmt_money(midpoints[0])}, the halfway point of that class.",
        f"From there it's the same method as an ordinary frequency table: multiply each midpoint by its "
        f"frequency, sum the results ({midpoint_terms} = {fmt_money(weighted_sum)}), then divide by the "
        f"total frequency ({' + '.join(str(f) for f in frequencies)} = {total_freq}).",
        f"Estimated mean = {fmt_money(weighted_sum)} ÷ {total_freq} = {fmt_money(mean)}. Because it's built "
        "from midpoints rather than real values, this is always called an ESTIMATE of the mean, not the exact mean.",
    ]
    worked_calculation = [
        f"Midpoints: {', '.join(fmt_money(m) for m in midpoints)}",
        f"Σ(midpoint × frequency) = {midpoint_terms} = {fmt_money(weighted_sum)}",
        f"Σ(frequency) = {' + '.join(str(f) for f in frequencies)} = {total_freq}",
        f"Estimated mean = {fmt_money(weighted_sum)} ÷ {total_freq} = {fmt_money(mean)}",
    ]
    return ModelledExample(
        topic_id="stats_mean_grouped_frequency_table_foundation",
        tier=Tier.FOUNDATION,
        prompt=(
            "The table shows the times (in minutes) taken by a group of runners: "
            f"{table_desc} (class: frequency). Find an estimate of the mean time."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"≈ {fmt_money(mean)}",
    )


def _random_frequency_table(rng: random.Random) -> tuple[list[int], list[int]]:
    """A small values/frequencies parallel-list frequency table, following the
    same convention as generate_mean_frequency_table but with a randomised
    starting value (not always 0) to widen the dedup-key space."""
    n_values = rng.randint(4, 6)
    start = rng.randint(0, 5)
    values = list(range(start, start + n_values))
    frequencies = [rng.randint(2, 10) for _ in values]
    return values, frequencies


def generate_mode_frequency_table(tier: Tier, rng: random.Random) -> Question:
    for _ in range(200):
        values, frequencies = _random_frequency_table(rng)
        max_freq = max(frequencies)
        if frequencies.count(max_freq) == 1:
            break
    else:
        raise ValueError("mode_frequency_table could not find a unique modal frequency")
    modal_index = frequencies.index(max_freq)
    modal_value = values[modal_index]

    # Independent verification: expand to a flat list and recompute via stdlib.
    flat = [v for v, f in zip(values, frequencies) for _ in range(f)]
    if statistics.mode(flat) != modal_value:
        raise ValueError("mode_frequency_table verification failed")

    table_desc = ", ".join(f"{v} ({f} times)" for v, f in zip(values, frequencies))
    steps = [
        f"The frequency shows how often each value occurs: {table_desc}.",
        f"The highest frequency is {max_freq}, for the value {modal_value}.",
        f"Mode = {modal_value}",
    ]
    return Question(
        topic_id="stats_mode_frequency_table",
        tier=Tier.FOUNDATION,
        prompt=(
            "A survey recorded the number of pets owned by each household: "
            f"{table_desc}. Find the modal number of pets."
        ),
        solution_steps=tuple(steps),
        final_answer=str(modal_value),
        dedup_key=f"mode_freq:{values}:{frequencies}",
    )


def generate_modelled_example_mode_frequency_table(tier: Tier, rng: random.Random) -> ModelledExample:
    for _ in range(200):
        values, frequencies = _random_frequency_table(rng)
        max_freq = max(frequencies)
        if frequencies.count(max_freq) == 1:
            break
    else:
        raise ValueError("modelled example mode_frequency_table could not find a unique modal frequency")
    modal_index = frequencies.index(max_freq)
    modal_value = values[modal_index]

    flat = [v for v, f in zip(values, frequencies) for _ in range(f)]
    if statistics.mode(flat) != modal_value:
        raise ValueError("modelled example mode_frequency_table verification failed")

    table_desc = ", ".join(f"{v} ({f} times)" for v, f in zip(values, frequencies))
    teaching_steps = [
        "The mode of a frequency table is just the value with the highest frequency - you're reading "
        "the table, not calculating anything from it.",
        f"Compare every frequency in the table: {', '.join(str(f) for f in frequencies)}. The largest "
        f"one is {max_freq}.",
        f"That largest frequency, {max_freq}, belongs to the value {modal_value}, so {modal_value} is "
        "the modal value - it's the value that occurred most often.",
    ]
    worked_calculation = [
        f"Highest frequency = {max_freq}",
        f"Value with that frequency = {modal_value}",
        f"Mode = {modal_value}",
    ]
    return ModelledExample(
        topic_id="stats_mode_frequency_table",
        tier=Tier.FOUNDATION,
        prompt=(
            "A survey recorded the number of pets owned by each household: "
            f"{table_desc}. Find the modal number of pets."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=str(modal_value),
    )


def generate_median_frequency_table(tier: Tier, rng: random.Random) -> Question:
    values, frequencies = _random_frequency_table(rng)
    flat = [v for v, f in zip(values, frequencies) for _ in range(f)]
    flat_sorted = sorted(flat)
    total = len(flat_sorted)
    if total % 2 == 1:
        median = Fraction(flat_sorted[total // 2])
    else:
        median = Fraction(flat_sorted[total // 2 - 1] + flat_sorted[total // 2], 2)

    # Independent verification via Python's stdlib statistics module.
    if abs(float(median) - statistics.median(flat)) > 1e-9:
        raise ValueError("median_frequency_table verification failed")

    table_desc = ", ".join(f"{v} ({f} times)" for v, f in zip(values, frequencies))
    steps = [
        f"Total frequency = {' + '.join(str(f) for f in frequencies)} = {total} data items.",
        "Imagine the data written out in full, in order (each value repeated as many times as its "
        "frequency), then find the middle of that list.",
        f"Median = {fmt_money(median)}",
    ]
    return Question(
        topic_id="stats_median_frequency_table",
        tier=Tier.FOUNDATION,
        prompt=(
            "A survey recorded the number of pets owned by each household: "
            f"{table_desc}. Find the median number of pets."
        ),
        solution_steps=tuple(steps),
        final_answer=fmt_money(median),
        dedup_key=f"median_freq:{values}:{frequencies}",
    )


def generate_modelled_example_median_frequency_table(tier: Tier, rng: random.Random) -> ModelledExample:
    values, frequencies = _random_frequency_table(rng)
    flat = [v for v, f in zip(values, frequencies) for _ in range(f)]
    flat_sorted = sorted(flat)
    total = len(flat_sorted)
    if total % 2 == 1:
        median = Fraction(flat_sorted[total // 2])
    else:
        median = Fraction(flat_sorted[total // 2 - 1] + flat_sorted[total // 2], 2)

    if abs(float(median) - statistics.median(flat)) > 1e-9:
        raise ValueError("modelled example median_frequency_table verification failed")

    table_desc = ", ".join(f"{v} ({f} times)" for v, f in zip(values, frequencies))
    teaching_steps = [
        "A frequency table is shorthand for a long list of data - to find the median, it helps to "
        "picture that full list written out in order, even though you never actually write it all down.",
        f"There are {total} data items in total (the sum of all the frequencies), so the median sits at "
        f"the middle position of that imagined list of {total} values.",
        f"Because the values in the table are already in ascending order, you can find the middle "
        "position directly without expanding the whole list: work along the frequencies, counting how "
        "many items have been passed, until you reach the middle.",
        f"Median = {fmt_money(median)}.",
    ]
    worked_calculation = [
        f"Total frequency = {total}",
        f"Median = {fmt_money(median)}",
    ]
    return ModelledExample(
        topic_id="stats_median_frequency_table",
        tier=Tier.FOUNDATION,
        prompt=(
            "A survey recorded the number of pets owned by each household: "
            f"{table_desc}. Find the median number of pets."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=fmt_money(median),
    )


def generate_range_frequency_table(tier: Tier, rng: random.Random) -> Question:
    values, frequencies = _random_frequency_table(rng)
    data_range = values[-1] - values[0]

    # Independent verification: expand to a flat list and recompute via
    # genuine max()/min() over the expanded data, a separate route from
    # reading the extreme values directly off the values list.
    flat = [v for v, f in zip(values, frequencies) for _ in range(f)]
    check_range = max(flat) - min(flat)
    if data_range != check_range:
        raise ValueError("range_frequency_table verification failed")

    table_desc = ", ".join(f"{v} ({f} times)" for v, f in zip(values, frequencies))
    steps = [
        f"The listed values run from {values[0]} to {values[-1]} (every value in between has a "
        "frequency of at least 1, so these are the true extremes).",
        f"Range = largest - smallest = {values[-1]} - {values[0]} = {data_range}",
    ]
    return Question(
        topic_id="stats_range_frequency_table",
        tier=Tier.FOUNDATION,
        prompt=(
            "A survey recorded the number of pets owned by each household: "
            f"{table_desc}. Find the range of the number of pets."
        ),
        solution_steps=tuple(steps),
        final_answer=str(data_range),
        dedup_key=f"range_freq:{values}:{frequencies}",
    )


def generate_modelled_example_range_frequency_table(tier: Tier, rng: random.Random) -> ModelledExample:
    values, frequencies = _random_frequency_table(rng)
    data_range = values[-1] - values[0]

    flat = [v for v, f in zip(values, frequencies) for _ in range(f)]
    check_range = max(flat) - min(flat)
    if data_range != check_range:
        raise ValueError("modelled example range_frequency_table verification failed")

    table_desc = ", ".join(f"{v} ({f} times)" for v, f in zip(values, frequencies))
    teaching_steps = [
        "The range only cares about the smallest and largest values that actually occur - the "
        "frequencies (how OFTEN each value occurs) don't matter for this one, as long as the frequency "
        "is at least 1.",
        f"Reading the table, the smallest value listed is {values[0]} and the largest is {values[-1]}. "
        "Every value in the table has a frequency of at least 1, so these really are the smallest and "
        "largest values that occur, not just the smallest and largest rows.",
        f"Range = largest - smallest = {values[-1]} - {values[0]} = {data_range}.",
    ]
    worked_calculation = [
        f"Largest = {values[-1]}, smallest = {values[0]}",
        f"Range = {values[-1]} - {values[0]} = {data_range}",
    ]
    return ModelledExample(
        topic_id="stats_range_frequency_table",
        tier=Tier.FOUNDATION,
        prompt=(
            "A survey recorded the number of pets owned by each household: "
            f"{table_desc}. Find the range of the number of pets."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=str(data_range),
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


def generate_modelled_example_reverse_mean(tier: Tier, rng: random.Random) -> ModelledExample:
    for _ in range(200):
        n = rng.randint(4, 6)
        mean_value = rng.randint(5, 20)
        known = [rng.randint(1, 30) for _ in range(n - 1)]
        total_required = mean_value * n
        missing = total_required - sum(known)
        if 1 <= missing <= 50:
            break
    else:
        raise ValueError("modelled example reverse_mean could not find valid parameters")

    full = known + [missing]
    if Fraction(sum(full), n) != mean_value:
        raise ValueError("modelled example reverse_mean verification failed (exact)")
    # Independent verification via Python's stdlib statistics module.
    if abs(statistics.mean(full) - mean_value) > 1e-9:
        raise ValueError("modelled example reverse_mean verification failed (stdlib)")

    known_str = ", ".join(str(v) for v in known)
    teaching_steps = [
        "This is a 'working backwards' problem - we're told the mean, not the raw data, so we have to "
        "undo the usual mean calculation to recover the missing piece.",
        f"Start from what the mean formula tells us: mean = total ÷ count. Rearranged, that means "
        f"total = mean × count, so the {n} numbers must add up to {mean_value} × {n} = {total_required}.",
        f"We already know {n - 1} of the numbers, so add those up: {' + '.join(str(v) for v in known)} = {sum(known)}.",
        f"Whatever is left of the required total must be the missing number: {total_required} - {sum(known)} = {missing}. "
        f"As a check, the full list {', '.join(str(v) for v in full)} really does average to {mean_value}.",
    ]
    worked_calculation = [
        f"Total needed = mean × count = {mean_value} × {n} = {total_required}",
        f"Known sum = {' + '.join(str(v) for v in known)} = {sum(known)}",
        f"Missing number = {total_required} - {sum(known)} = {missing}",
    ]
    return ModelledExample(
        topic_id="stats_reverse_mean",
        tier=Tier.HIGHER,
        prompt=(
            f"The mean of {n} numbers is {mean_value}. {n - 1} of the numbers are {known_str}. "
            "Find the missing number."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=str(missing),
    )


def generate_reverse_mean_foundation(tier: Tier, rng: random.Random) -> Question:
    for _ in range(200):
        n = rng.randint(3, 4)
        mean_value = rng.randint(3, 12)
        known = [rng.randint(1, 15) for _ in range(n - 1)]
        total_required = mean_value * n
        missing = total_required - sum(known)
        if 1 <= missing <= 25:
            break
    else:
        raise ValueError("reverse_mean_foundation could not find valid parameters")

    full = known + [missing]
    if Fraction(sum(full), n) != mean_value:
        raise ValueError("reverse_mean_foundation verification failed (exact)")
    if abs(statistics.mean(full) - mean_value) > 1e-9:
        raise ValueError("reverse_mean_foundation verification failed (stdlib)")

    known_str = ", ".join(str(v) for v in known)
    steps = [
        f"Total of all {n} numbers = mean × count = {mean_value} × {n} = {total_required}",
        f"Sum of the known numbers = {' + '.join(str(v) for v in known)} = {sum(known)}",
        f"Missing number = {total_required} - {sum(known)} = {missing}",
    ]
    return Question(
        topic_id="stats_reverse_mean_foundation",
        tier=Tier.FOUNDATION,
        prompt=(
            f"The mean of {n} numbers is {mean_value}. {n - 1} of the numbers are {known_str}. "
            "Find the missing number."
        ),
        solution_steps=tuple(steps),
        final_answer=str(missing),
        dedup_key=f"reverse_mean_f:{known}:{mean_value}",
    )


def generate_modelled_example_reverse_mean_foundation(tier: Tier, rng: random.Random) -> ModelledExample:
    for _ in range(200):
        n = rng.randint(3, 4)
        mean_value = rng.randint(3, 12)
        known = [rng.randint(1, 15) for _ in range(n - 1)]
        total_required = mean_value * n
        missing = total_required - sum(known)
        if 1 <= missing <= 25:
            break
    else:
        raise ValueError("modelled example reverse_mean_foundation could not find valid parameters")

    full = known + [missing]
    if Fraction(sum(full), n) != mean_value:
        raise ValueError("modelled example reverse_mean_foundation verification failed (exact)")
    if abs(statistics.mean(full) - mean_value) > 1e-9:
        raise ValueError("modelled example reverse_mean_foundation verification failed (stdlib)")

    known_str = ", ".join(str(v) for v in known)
    teaching_steps = [
        "This is a 'working backwards' problem - we're told the mean, not the raw data, so we have to "
        "undo the usual mean calculation to recover the missing piece.",
        f"Start from what the mean formula tells us: mean = total ÷ count. Rearranged, that means "
        f"total = mean × count, so the {n} numbers must add up to {mean_value} × {n} = {total_required}.",
        f"We already know {n - 1} of the numbers, so add those up: {' + '.join(str(v) for v in known)} = {sum(known)}.",
        f"Whatever is left of the required total must be the missing number: {total_required} - {sum(known)} = {missing}. "
        f"As a check, the full list {', '.join(str(v) for v in full)} really does average to {mean_value}.",
    ]
    worked_calculation = [
        f"Total needed = mean × count = {mean_value} × {n} = {total_required}",
        f"Known sum = {' + '.join(str(v) for v in known)} = {sum(known)}",
        f"Missing number = {total_required} - {sum(known)} = {missing}",
    ]
    return ModelledExample(
        topic_id="stats_reverse_mean_foundation",
        tier=Tier.FOUNDATION,
        prompt=(
            f"The mean of {n} numbers is {mean_value}. {n - 1} of the numbers are {known_str}. "
            "Find the missing number."
        ),
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=str(missing),
    )


TOPIC_MEAN = TopicDefinition(
    id="stats_mean",
    display_name="Mean",
    description="Find the mean of a list of numbers.",
    generate=generate_mean,
    section=SECTION,
    group=GROUP_AVERAGES,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_mean,
)

TOPIC_MODE = TopicDefinition(
    id="stats_mode",
    display_name="Mode",
    description="Find the mode of a list of numbers.",
    generate=generate_mode,
    section=SECTION,
    group=GROUP_AVERAGES,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_mode,
)

TOPIC_MEDIAN = TopicDefinition(
    id="stats_median",
    display_name="Median",
    description="Find the median of a list of numbers.",
    generate=generate_median,
    section=SECTION,
    group=GROUP_AVERAGES,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_median,
)

TOPIC_RANGE = TopicDefinition(
    id="stats_range",
    display_name="Range",
    description="Find the range of a list of numbers.",
    generate=generate_range,
    section=SECTION,
    group=GROUP_AVERAGES,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_range,
)

TOPIC_AVERAGES_COMBINED = TopicDefinition(
    id="stats_averages_combined",
    display_name="Mean, Mode, Median & Range",
    description="Find the mean, mode, median and range of the same list of numbers.",
    generate=generate_averages_combined,
    section=SECTION,
    group=GROUP_AVERAGES,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_averages_combined,
)

TOPIC_INTERQUARTILE_RANGE = TopicDefinition(
    id="stats_interquartile_range",
    display_name="Interquartile Range",
    description="Find the interquartile range (IQR) of a small raw data set.",
    generate=generate_interquartile_range,
    section=SECTION,
    group=GROUP_AVERAGES,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_interquartile_range,
)

TOPIC_MEAN_FREQUENCY_TABLE = TopicDefinition(
    id="stats_mean_frequency_table",
    display_name="Mean from a Frequency Table",
    description="Find the mean of discrete data presented in a frequency table.",
    generate=generate_mean_frequency_table,
    section=SECTION,
    group=GROUP_FREQUENCY,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_mean_frequency_table,
)

TOPIC_MEAN_GROUPED_FREQUENCY_TABLE = TopicDefinition(
    id="stats_mean_grouped_frequency_table",
    display_name="Mean from a Grouped Frequency Table",
    description="Estimate the mean of grouped/continuous data using class midpoints.",
    generate=generate_mean_grouped_frequency_table,
    section=SECTION,
    group=GROUP_FREQUENCY,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_mean_grouped_frequency_table,
)

TOPIC_MEAN_GROUPED_FREQUENCY_TABLE_FOUNDATION = TopicDefinition(
    id="stats_mean_grouped_frequency_table_foundation",
    display_name="Mean from a Grouped Frequency Table (Foundation)",
    description="Estimate the mean of grouped/continuous data using class midpoints.",
    generate=generate_mean_grouped_frequency_table_foundation,
    section=SECTION,
    group=GROUP_FREQUENCY,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_mean_grouped_frequency_table_foundation,
)

TOPIC_MODE_FREQUENCY_TABLE = TopicDefinition(
    id="stats_mode_frequency_table",
    display_name="Mode from a Frequency Table",
    description="Find the modal value of discrete data presented in a frequency table.",
    generate=generate_mode_frequency_table,
    section=SECTION,
    group=GROUP_FREQUENCY,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_mode_frequency_table,
)

TOPIC_MEDIAN_FREQUENCY_TABLE = TopicDefinition(
    id="stats_median_frequency_table",
    display_name="Median from a Frequency Table",
    description="Find the median of discrete data presented in a frequency table.",
    generate=generate_median_frequency_table,
    section=SECTION,
    group=GROUP_FREQUENCY,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_median_frequency_table,
)

TOPIC_RANGE_FREQUENCY_TABLE = TopicDefinition(
    id="stats_range_frequency_table",
    display_name="Range from a Frequency Table",
    description="Find the range of discrete data presented in a frequency table.",
    generate=generate_range_frequency_table,
    section=SECTION,
    group=GROUP_FREQUENCY,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_range_frequency_table,
)

TOPIC_REVERSE_MEAN = TopicDefinition(
    id="stats_reverse_mean",
    display_name="Reverse Mean",
    description="Find a missing value given the mean of a set of numbers.",
    generate=generate_reverse_mean,
    section=SECTION,
    group=GROUP_REVERSE,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_reverse_mean,
)

TOPIC_REVERSE_MEAN_FOUNDATION = TopicDefinition(
    id="stats_reverse_mean_foundation",
    display_name="Reverse Mean (Foundation)",
    description="Find a missing value given the mean of a set of numbers.",
    generate=generate_reverse_mean_foundation,
    section=SECTION,
    group=GROUP_REVERSE,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_reverse_mean_foundation,
)
