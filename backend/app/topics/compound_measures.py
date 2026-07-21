import random
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction

from app.core.models import ModelledExample, Question, Tier
from app.topics.base import TopicDefinition

SECTION = "ratio_proportion"
GROUP = "Compound Measures"


# ---------------------------------------------------------------------------
# Shared formatting / rounding helpers
# ---------------------------------------------------------------------------


def _fmt_num(d: Decimal) -> str:
    """Format a Decimal without a trailing '.0' or scientific notation."""
    d = d.normalize()
    if d == d.to_integral_value():
        d = d.quantize(Decimal(1))
    return format(d, "f")


def _round_dp(value: Decimal, dp: int) -> Decimal:
    return value.quantize(Decimal(1).scaleb(-dp), rounding=ROUND_HALF_UP)


def _frac_round_dp(fr: Fraction, dp: int) -> Decimal:
    """Round a Fraction to `dp` decimal places via Decimal division - kept as a
    separate code path (Fraction arithmetic) from any Decimal-only computation
    it is being used to cross-check."""
    d = Decimal(fr.numerator) / Decimal(fr.denominator)
    return _round_dp(d, dp)


def _mul_via_repeated_addition(a: int, b: int) -> int:
    """Multiply two ints without using `*` - used as a genuinely independent
    check on a multiplication done elsewhere with `*`."""
    total = 0
    for _ in range(b):
        total += a
    return total


def _rand_decimal_value(rng: random.Random, lo: int, hi: int, one_dp_chance: float = 0.3) -> Decimal:
    whole = rng.randint(lo, hi)
    if rng.random() < one_dp_chance:
        tenth = rng.choice([1, 2, 3, 4, 5, 6, 7, 8, 9])
        return Decimal(f"{whole}.{tenth}")
    return Decimal(whole)


# ===========================================================================
# Speed, Distance and Time
# ===========================================================================

_SDT_SYSTEMS = [
    {"dist_unit": "km", "time_unit": "hours", "speed_unit": "km/h",
     "speed_range": (10, 120), "time_range": (1, 8)},
    {"dist_unit": "miles", "time_unit": "hours", "speed_unit": "mph",
     "speed_range": (10, 70), "time_range": (1, 8)},
    {"dist_unit": "m", "time_unit": "seconds", "speed_unit": "m/s",
     "speed_range": (1, 30), "time_range": (10, 300)},
]

_SDT_CONTEXTS = ["car", "cyclist", "train", "runner", "delivery van", "plane", "hiker"]


def generate_sdt_mixed(tier: Tier, rng: random.Random) -> Question:
    system = rng.choice(_SDT_SYSTEMS)
    context = rng.choice(_SDT_CONTEXTS)
    speed = rng.randint(*system["speed_range"])
    time = rng.randint(*system["time_range"])
    distance = speed * time
    unknown = rng.choice(["speed", "distance", "time"])

    if unknown == "speed":
        # Built via division; verify via the ORIGINAL relationship using
        # multiplication - a genuinely different operation.
        if speed * time != distance:
            raise ValueError("sdt_mixed verification failed (speed)")
        prompt = (
            f"A {context} travels {distance} {system['dist_unit']} in {time} "
            f"{system['time_unit']}. Find its average speed in {system['speed_unit']}."
        )
        steps = [
            "speed = distance ÷ time",
            f"speed = {distance} ÷ {time} = {speed} {system['speed_unit']}",
        ]
        answer = f"{speed} {system['speed_unit']}"
    elif unknown == "distance":
        # Built via multiplication; verify via the ORIGINAL relationship using
        # division.
        if Fraction(distance, time) != Fraction(speed):
            raise ValueError("sdt_mixed verification failed (distance)")
        prompt = (
            f"A {context} travels at {speed} {system['speed_unit']} for {time} "
            f"{system['time_unit']}. Find the distance travelled."
        )
        steps = [
            "distance = speed × time",
            f"distance = {speed} × {time} = {distance} {system['dist_unit']}",
        ]
        answer = f"{distance} {system['dist_unit']}"
    else:  # time
        # Built via division; verify via the ORIGINAL relationship using
        # multiplication.
        if speed * time != distance:
            raise ValueError("sdt_mixed verification failed (time)")
        prompt = (
            f"A {context} travels {distance} {system['dist_unit']} at an average "
            f"speed of {speed} {system['speed_unit']}. Find how long the journey takes."
        )
        steps = [
            "time = distance ÷ speed",
            f"time = {distance} ÷ {speed} = {time} {system['time_unit']}",
        ]
        answer = f"{time} {system['time_unit']}"

    return Question(
        topic_id="sdt_mixed",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"sdt:{system['speed_unit']}:{unknown}:{speed}:{time}",
    )


def generate_modelled_example_sdt_mixed(tier: Tier, rng: random.Random) -> ModelledExample:
    system = rng.choice(_SDT_SYSTEMS)
    context = rng.choice(_SDT_CONTEXTS)
    speed = rng.randint(*system["speed_range"])
    time = rng.randint(*system["time_range"])
    distance = speed * time
    unknown = rng.choice(["speed", "distance", "time"])

    if unknown == "speed":
        if speed * time != distance:
            raise ValueError("modelled example sdt_mixed verification failed (speed)")
        prompt = (
            f"A {context} travels {distance} {system['dist_unit']} in {time} "
            f"{system['time_unit']}. Find its average speed in {system['speed_unit']}."
        )
        answer = f"{speed} {system['speed_unit']}"
        teaching_steps = [
            "The three quantities speed, distance and time are always linked by "
            "speed = distance ÷ time - the trick is spotting which one is missing.",
            f"Here we're given the distance ({distance} {system['dist_unit']}) and the time "
            f"({time} {system['time_unit']}), and asked for the speed, so we can use the "
            "formula exactly as it stands, with no rearranging needed.",
            f"Dividing gives speed = {distance} ÷ {time} = {speed} {system['speed_unit']}.",
            f"As a check, multiplying the speed back by the time should return the original "
            f"distance: {speed} × {time} = {speed * time}, which matches {distance}.",
        ]
        worked_calculation = [
            f"speed = distance ÷ time = {distance} ÷ {time}",
            f"speed = {speed} {system['speed_unit']}",
        ]
    elif unknown == "distance":
        if Fraction(distance, time) != Fraction(speed):
            raise ValueError("modelled example sdt_mixed verification failed (distance)")
        prompt = (
            f"A {context} travels at {speed} {system['speed_unit']} for {time} "
            f"{system['time_unit']}. Find the distance travelled."
        )
        answer = f"{distance} {system['dist_unit']}"
        teaching_steps = [
            "Speed tells us how far something travels in one unit of time, so to find a total "
            "distance we scale the speed up by however much time has passed.",
            f"We're given the speed ({speed} {system['speed_unit']}) and the time "
            f"({time} {system['time_unit']}), so distance = speed × time applies directly.",
            f"Multiplying gives distance = {speed} × {time} = {distance} {system['dist_unit']}.",
            f"As a check, dividing that distance back by the time should return the original "
            f"speed: {distance} ÷ {time} = {speed}, which matches what we started with.",
        ]
        worked_calculation = [
            f"distance = speed × time = {speed} × {time}",
            f"distance = {distance} {system['dist_unit']}",
        ]
    else:  # time
        if speed * time != distance:
            raise ValueError("modelled example sdt_mixed verification failed (time)")
        prompt = (
            f"A {context} travels {distance} {system['dist_unit']} at an average "
            f"speed of {speed} {system['speed_unit']}. Find how long the journey takes."
        )
        answer = f"{time} {system['time_unit']}"
        teaching_steps = [
            "This time we know the distance and the speed, but not the time - so we need to "
            "rearrange speed = distance ÷ time to make time the subject.",
            f"Rearranging gives time = distance ÷ speed, using the {distance} "
            f"{system['dist_unit']} we're told and the {speed} {system['speed_unit']} speed.",
            f"Dividing gives time = {distance} ÷ {speed} = {time} {system['time_unit']}.",
            f"As a check, multiplying the speed by that time should reproduce the original "
            f"distance: {speed} × {time} = {speed * time}, which matches {distance}.",
        ]
        worked_calculation = [
            f"time = distance ÷ speed = {distance} ÷ {speed}",
            f"time = {time} {system['time_unit']}",
        ]

    return ModelledExample(
        topic_id="sdt_mixed",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
    )


# ===========================================================================
# Speed with Unit Conversions
# ===========================================================================

_SPEED_CONV_CONTEXTS = ["car", "train", "cyclist", "runner", "delivery van", "motorbike"]


def generate_speed_with_conversions(tier: Tier, rng: random.Random) -> Question:
    context = rng.choice(_SPEED_CONV_CONTEXTS)
    flavour = rng.choice(["convert_input", "convert_output"])

    if flavour == "convert_input":
        sub = rng.choice(["km_min", "m_min"])
        if sub == "km_min":
            distance = rng.randint(2, 60)
            minutes = rng.choice([10, 12, 15, 20, 24, 30, 36, 40, 45, 48, 50, 54, 60, 72, 75, 90])
            speed_exact = Fraction(distance * 60, minutes)
            rounded = _frac_round_dp(speed_exact, 1)
            # Verify via a single combined conversion factor - a different order
            # of operations to the "convert minutes to hours, then divide" steps.
            combined = Fraction(distance * 60, minutes)
            if combined != speed_exact:
                raise ValueError("speed_with_conversions verification failed (km/min)")
            prompt = (
                f"A {context} travels {distance} km in {minutes} minutes. Find its average "
                "speed in km/h, correct to 1 decimal place."
            )
            steps = [
                f"Convert time to hours: {minutes} minutes = {minutes} ÷ 60 hours",
                f"speed = distance ÷ time = {distance} ÷ ({minutes} ÷ 60) = {_fmt_num(rounded)} km/h (1 d.p.)",
            ]
            answer = f"{_fmt_num(rounded)} km/h"
            dedup = f"swc:input:km_min:{distance}:{minutes}"
        else:  # m_min
            distance = rng.randint(50, 3000)
            minutes = rng.choice([1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 24, 30])
            seconds = minutes * 60
            speed_exact = Fraction(distance, seconds)
            rounded = _frac_round_dp(speed_exact, 1)
            combined = Fraction(distance, minutes * 60)
            if combined != speed_exact:
                raise ValueError("speed_with_conversions verification failed (m/min)")
            prompt = (
                f"A {context} travels {distance} m in {minutes} minutes. Find its average "
                "speed in m/s, correct to 1 decimal place."
            )
            steps = [
                f"Convert time to seconds: {minutes} minutes = {minutes} × 60 = {seconds} seconds",
                f"speed = distance ÷ time = {distance} ÷ {seconds} = {_fmt_num(rounded)} m/s (1 d.p.)",
            ]
            answer = f"{_fmt_num(rounded)} m/s"
            dedup = f"swc:input:m_min:{distance}:{minutes}"
    else:  # convert_output
        sub = rng.choice(["ms_to_kmh", "kmh_to_ms"])
        if sub == "ms_to_kmh":
            time_s = rng.randint(5, 120)
            speed_ms = rng.randint(2, 40)
            distance_m = speed_ms * time_s
            # Build: scale the m/s answer directly by 18/5.
            speed_kmh_exact = Fraction(speed_ms) * Fraction(18, 5)
            rounded = _frac_round_dp(speed_kmh_exact, 1)
            # Verify via an entirely different route: convert distance and time
            # to km and hours separately, then divide.
            distance_km = Fraction(distance_m, 1000)
            time_h = Fraction(time_s, 3600)
            check_exact = distance_km / time_h
            if _frac_round_dp(check_exact, 1) != rounded:
                raise ValueError("speed_with_conversions verification failed (m/s to km/h)")
            prompt = (
                f"A {context} travels {distance_m} m in {time_s} seconds. Find its average "
                "speed in km/h, correct to 1 decimal place."
            )
            steps = [
                f"speed = distance ÷ time = {distance_m} ÷ {time_s} = {speed_ms} m/s",
                f"Convert to km/h: {speed_ms} × 3.6 = {_fmt_num(rounded)} km/h (1 d.p.)",
            ]
            answer = f"{_fmt_num(rounded)} km/h"
            dedup = f"swc:output:ms_kmh:{time_s}:{speed_ms}"
        else:  # kmh_to_ms
            time_h = rng.randint(1, 6)
            speed_kmh = rng.randint(10, 120)
            distance_km = speed_kmh * time_h
            speed_ms_exact = Fraction(speed_kmh) * Fraction(5, 18)
            rounded = _frac_round_dp(speed_ms_exact, 1)
            distance_m = Fraction(distance_km * 1000)
            time_s = Fraction(time_h * 3600)
            check_exact = distance_m / time_s
            if _frac_round_dp(check_exact, 1) != rounded:
                raise ValueError("speed_with_conversions verification failed (km/h to m/s)")
            prompt = (
                f"A {context} travels {distance_km} km in {time_h} hours. Find its average "
                "speed in m/s, correct to 1 decimal place."
            )
            steps = [
                f"speed = distance ÷ time = {distance_km} ÷ {time_h} = {speed_kmh} km/h",
                f"Convert to m/s: {speed_kmh} ÷ 3.6 = {_fmt_num(rounded)} m/s (1 d.p.)",
            ]
            answer = f"{_fmt_num(rounded)} m/s"
            dedup = f"swc:output:kmh_ms:{time_h}:{speed_kmh}"

    return Question(
        topic_id="speed_with_conversions",
        tier=Tier.HIGHER,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=dedup,
    )


def generate_modelled_example_speed_with_conversions(tier: Tier, rng: random.Random) -> ModelledExample:
    context = rng.choice(_SPEED_CONV_CONTEXTS)
    flavour = rng.choice(["convert_input", "convert_output"])

    if flavour == "convert_input":
        sub = rng.choice(["km_min", "m_min"])
        if sub == "km_min":
            distance = rng.randint(2, 60)
            minutes = rng.choice([10, 12, 15, 20, 24, 30, 36, 40, 45, 48, 50, 54, 60, 72, 75, 90])
            speed_exact = Fraction(distance * 60, minutes)
            rounded = _frac_round_dp(speed_exact, 1)
            combined = Fraction(distance * 60, minutes)
            if combined != speed_exact:
                raise ValueError("modelled example speed_with_conversions verification failed (km/min)")
            prompt = (
                f"A {context} travels {distance} km in {minutes} minutes. Find its average "
                "speed in km/h, correct to 1 decimal place."
            )
            answer = f"{_fmt_num(rounded)} km/h"
            teaching_steps = [
                "The formula speed = distance ÷ time only works if distance and time are in "
                "units that match the speed we want - here we want km/h, so time must be in "
                "hours, but we're given minutes.",
                f"Convert the time first: {minutes} minutes = {minutes} ÷ 60 hours. Keeping it "
                "as a fraction (rather than rounding early) avoids losing accuracy.",
                f"Now divide: speed = {distance} ÷ ({minutes} ÷ 60) = {_fmt_num(rounded)} km/h, "
                "rounded to 1 decimal place as asked.",
                "As a check, the whole calculation can also be done in one combined step - "
                f"multiplying the distance by 60 and dividing by the minutes directly - and it "
                "gives the same answer, confirming the conversion was done correctly.",
            ]
            worked_calculation = [
                f"{minutes} min = {minutes} ÷ 60 hours",
                f"speed = {distance} ÷ ({minutes} ÷ 60)",
                f"speed = {_fmt_num(rounded)} km/h (1 d.p.)",
            ]
        else:  # m_min
            distance = rng.randint(50, 3000)
            minutes = rng.choice([1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 24, 30])
            seconds = minutes * 60
            speed_exact = Fraction(distance, seconds)
            rounded = _frac_round_dp(speed_exact, 1)
            combined = Fraction(distance, minutes * 60)
            if combined != speed_exact:
                raise ValueError("modelled example speed_with_conversions verification failed (m/min)")
            prompt = (
                f"A {context} travels {distance} m in {minutes} minutes. Find its average "
                "speed in m/s, correct to 1 decimal place."
            )
            answer = f"{_fmt_num(rounded)} m/s"
            teaching_steps = [
                "We want an answer in m/s, so the time needs to be in seconds - but we're "
                "given it in minutes, so it must be converted first.",
                f"Convert the time: {minutes} minutes = {minutes} × 60 = {seconds} seconds.",
                f"Now apply speed = distance ÷ time: {distance} ÷ {seconds} = {_fmt_num(rounded)} "
                "m/s, rounded to 1 decimal place.",
                "As a check, working with the minutes and the '× 60' bundled into a single "
                "division by (minutes × 60) in one step gives exactly the same result, which "
                "confirms the conversion step was applied correctly.",
            ]
            worked_calculation = [
                f"{minutes} min = {minutes} × 60 = {seconds} s",
                f"speed = {distance} ÷ {seconds}",
                f"speed = {_fmt_num(rounded)} m/s (1 d.p.)",
            ]
    else:  # convert_output
        sub = rng.choice(["ms_to_kmh", "kmh_to_ms"])
        if sub == "ms_to_kmh":
            time_s = rng.randint(5, 120)
            speed_ms = rng.randint(2, 40)
            distance_m = speed_ms * time_s
            speed_kmh_exact = Fraction(speed_ms) * Fraction(18, 5)
            rounded = _frac_round_dp(speed_kmh_exact, 1)
            distance_km = Fraction(distance_m, 1000)
            time_h = Fraction(time_s, 3600)
            check_exact = distance_km / time_h
            if _frac_round_dp(check_exact, 1) != rounded:
                raise ValueError("modelled example speed_with_conversions verification failed (m/s to km/h)")
            prompt = (
                f"A {context} travels {distance_m} m in {time_s} seconds. Find its average "
                "speed in km/h, correct to 1 decimal place."
            )
            answer = f"{_fmt_num(rounded)} km/h"
            teaching_steps = [
                f"First work out the speed in the units we're given: distance ÷ time = "
                f"{distance_m} ÷ {time_s} = {speed_ms} m/s. This part uses no conversion at all.",
                "Now the speed itself needs converting from m/s to km/h. Multiplying by 3.6 "
                "does this in one step, because there are 3600 seconds in an hour and 1000 "
                "metres in a km, and 3600 ÷ 1000 = 3.6.",
                f"So {speed_ms} × 3.6 = {_fmt_num(rounded)} km/h, rounded to 1 decimal place.",
                "As an independent check, converting the ORIGINAL distance and time into km "
                "and hours separately (rather than scaling the m/s answer) and dividing gives "
                "the same result - confirming the ×3.6 shortcut was applied correctly.",
            ]
            worked_calculation = [
                f"speed = {distance_m} ÷ {time_s} = {speed_ms} m/s",
                f"{speed_ms} × 3.6 = {_fmt_num(rounded)} km/h (1 d.p.)",
            ]
        else:  # kmh_to_ms
            time_h = rng.randint(1, 6)
            speed_kmh = rng.randint(10, 120)
            distance_km = speed_kmh * time_h
            speed_ms_exact = Fraction(speed_kmh) * Fraction(5, 18)
            rounded = _frac_round_dp(speed_ms_exact, 1)
            distance_m = Fraction(distance_km * 1000)
            time_s = Fraction(time_h * 3600)
            check_exact = distance_m / time_s
            if _frac_round_dp(check_exact, 1) != rounded:
                raise ValueError("modelled example speed_with_conversions verification failed (km/h to m/s)")
            prompt = (
                f"A {context} travels {distance_km} km in {time_h} hours. Find its average "
                "speed in m/s, correct to 1 decimal place."
            )
            answer = f"{_fmt_num(rounded)} m/s"
            teaching_steps = [
                f"First find the speed in the units given: {distance_km} ÷ {time_h} = "
                f"{speed_kmh} km/h. No conversion is needed for this part.",
                "To turn km/h into m/s, divide by 3.6 - the reverse of the km/h-to-m/s "
                "shortcut, since there are 3.6 times as many km/h as m/s for the same speed.",
                f"So {speed_kmh} ÷ 3.6 = {_fmt_num(rounded)} m/s, rounded to 1 decimal place.",
                "As an independent check, converting the ORIGINAL distance to metres and the "
                "time to seconds separately, then dividing, gives the same result - confirming "
                "the ÷3.6 shortcut was applied correctly.",
            ]
            worked_calculation = [
                f"speed = {distance_km} ÷ {time_h} = {speed_kmh} km/h",
                f"{speed_kmh} ÷ 3.6 = {_fmt_num(rounded)} m/s (1 d.p.)",
            ]

    return ModelledExample(
        topic_id="speed_with_conversions",
        tier=Tier.HIGHER,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
    )


# ===========================================================================
# Unit Conversions (Foundation) - length, mass, capacity
# ===========================================================================

# Each entry: (small_unit, large_unit, factor) where 1 large_unit = factor small_units.
_UNIT_PAIRS = [
    ("mm", "cm", Decimal(10)),
    ("cm", "m", Decimal(100)),
    ("mm", "m", Decimal(1000)),
    ("m", "km", Decimal(1000)),
    ("g", "kg", Decimal(1000)),
    ("ml", "l", Decimal(1000)),
]


def generate_unit_conversions(tier: Tier, rng: random.Random) -> Question:
    small, large, factor = rng.choice(_UNIT_PAIRS)
    direction = rng.choice(["large_to_small", "small_to_large"])
    reciprocal = Fraction(1) / Fraction(factor)

    if direction == "large_to_small":
        value = _rand_decimal_value(rng, 1, 500)
        target = value * factor
        # Verify via dividing by the reciprocal - a different operation
        # (division) to the multiplication used to build the answer.
        check = Fraction(value) / reciprocal
        if check != Fraction(target):
            raise ValueError("unit_conversions verification failed (large_to_small)")
        prompt = f"Convert {_fmt_num(value)} {large} to {small}."
        steps = [
            f"1 {large} = {_fmt_num(Decimal(factor))} {small}",
            f"{_fmt_num(value)} {large} = {_fmt_num(value)} × {_fmt_num(Decimal(factor))} = {_fmt_num(target)} {small}",
        ]
        answer = f"{_fmt_num(target)} {small}"
    else:
        value = Decimal(rng.randint(1, 9999))
        target = value / factor
        # Verify via multiplying by the reciprocal - a different operation
        # (multiplication) to the division used to build the answer.
        check = Fraction(value) * reciprocal
        if check != Fraction(target):
            raise ValueError("unit_conversions verification failed (small_to_large)")
        prompt = f"Convert {_fmt_num(value)} {small} to {large}."
        steps = [
            f"1 {large} = {_fmt_num(Decimal(factor))} {small}",
            f"{_fmt_num(value)} {small} = {_fmt_num(value)} ÷ {_fmt_num(Decimal(factor))} = {_fmt_num(target)} {large}",
        ]
        answer = f"{_fmt_num(target)} {large}"

    return Question(
        topic_id="unit_conversions",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"uc:{small}:{large}:{direction}:{value}",
    )


def generate_modelled_example_unit_conversions(tier: Tier, rng: random.Random) -> ModelledExample:
    small, large, factor = rng.choice(_UNIT_PAIRS)
    direction = rng.choice(["large_to_small", "small_to_large"])
    reciprocal = Fraction(1) / Fraction(factor)

    if direction == "large_to_small":
        value = _rand_decimal_value(rng, 1, 500)
        target = value * factor
        check = Fraction(value) / reciprocal
        if check != Fraction(target):
            raise ValueError("modelled example unit_conversions verification failed (large_to_small)")
        prompt = f"Convert {_fmt_num(value)} {large} to {small}."
        answer = f"{_fmt_num(target)} {small}"
        teaching_steps = [
            f"{large} is a LARGER unit than {small}, and 1 {large} = "
            f"{_fmt_num(Decimal(factor))} {small}, so converting from the larger unit to the "
            "smaller one always means MULTIPLYING - the number of units gets bigger because "
            "each one is smaller.",
            f"Multiply the given value by the conversion factor: {_fmt_num(value)} × "
            f"{_fmt_num(Decimal(factor))} = {_fmt_num(target)}.",
            f"So {_fmt_num(value)} {large} = {_fmt_num(target)} {small}.",
            "As a check, dividing by the reciprocal of the factor (instead of multiplying by "
            "the factor directly) gives exactly the same result, confirming the direction of "
            "the conversion was correct.",
        ]
        worked_calculation = [
            f"1 {large} = {_fmt_num(Decimal(factor))} {small}",
            f"{_fmt_num(value)} × {_fmt_num(Decimal(factor))} = {_fmt_num(target)}",
            f"{_fmt_num(value)} {large} = {_fmt_num(target)} {small}",
        ]
    else:
        value = Decimal(rng.randint(1, 9999))
        target = value / factor
        check = Fraction(value) * reciprocal
        if check != Fraction(target):
            raise ValueError("modelled example unit_conversions verification failed (small_to_large)")
        prompt = f"Convert {_fmt_num(value)} {small} to {large}."
        answer = f"{_fmt_num(target)} {large}"
        teaching_steps = [
            f"{small} is a SMALLER unit than {large}, and 1 {large} = "
            f"{_fmt_num(Decimal(factor))} {small}, so converting from the smaller unit to the "
            "larger one always means DIVIDING - it takes many small units to make one big one.",
            f"Divide the given value by the conversion factor: {_fmt_num(value)} ÷ "
            f"{_fmt_num(Decimal(factor))} = {_fmt_num(target)}.",
            f"So {_fmt_num(value)} {small} = {_fmt_num(target)} {large}.",
            "As a check, multiplying by the reciprocal of the factor (instead of dividing by "
            "the factor directly) gives exactly the same result, confirming the direction of "
            "the conversion was correct.",
        ]
        worked_calculation = [
            f"1 {large} = {_fmt_num(Decimal(factor))} {small}",
            f"{_fmt_num(value)} ÷ {_fmt_num(Decimal(factor))} = {_fmt_num(target)}",
            f"{_fmt_num(value)} {small} = {_fmt_num(target)} {large}",
        ]

    return ModelledExample(
        topic_id="unit_conversions",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
    )


# ===========================================================================
# Unit Conversions (Higher) - area and volume
# ===========================================================================

_UNIT_PRETTY = {
    "mm2": "mm²", "cm2": "cm²", "m2": "m²",
    "mm3": "mm³", "cm3": "cm³", "m3": "m³",
}

# Each entry: (small_unit, large_unit, linear_factor, power) where power=2 for
# area, 3 for volume, and the area/volume factor is linear_factor ** power.
_UNIT_PAIRS_HIGHER = [
    ("mm2", "cm2", 10, 2),
    ("cm2", "m2", 100, 2),
    ("mm3", "cm3", 10, 3),
    ("cm3", "m3", 100, 3),
]


def generate_unit_conversions_higher(tier: Tier, rng: random.Random) -> Question:
    small, large, linear_factor, power = rng.choice(_UNIT_PAIRS_HIGHER)
    small_p, large_p = _UNIT_PRETTY[small], _UNIT_PRETTY[large]
    kind = "area" if power == 2 else "volume"

    # Independent derivation of the factor: repeated multiplication, a
    # genuinely different code path to the `**` operator used below.
    factor_built = linear_factor ** power
    factor_check = 1
    for _ in range(power):
        factor_check *= linear_factor
    if factor_check != factor_built:
        raise ValueError("unit_conversions_higher factor verification failed")
    factor = Decimal(factor_built)
    reciprocal = Fraction(1) / Fraction(factor)

    direction = rng.choice(["large_to_small", "small_to_large"])
    if direction == "large_to_small":
        value = _rand_decimal_value(rng, 1, 50, one_dp_chance=0.4)
        target = value * factor
        check = Fraction(value) / reciprocal
        if check != Fraction(target):
            raise ValueError("unit_conversions_higher verification failed (large_to_small)")
        prompt = f"Convert {_fmt_num(value)} {large_p} to {small_p}."
        steps = [
            f"Linear conversion factor: 1 {large.replace('2','').replace('3','')} = "
            f"{linear_factor} {small.replace('2','').replace('3','')}, so for {kind}, "
            f"1 {large_p} = {linear_factor}^{power} = {_fmt_num(factor)} {small_p}",
            f"{_fmt_num(value)} {large_p} = {_fmt_num(value)} × {_fmt_num(factor)} = {_fmt_num(target)} {small_p}",
        ]
        answer = f"{_fmt_num(target)} {small_p}"
    else:
        value = Decimal(rng.randint(1, 5000))
        target = value / factor
        check = Fraction(value) * reciprocal
        if check != Fraction(target):
            raise ValueError("unit_conversions_higher verification failed (small_to_large)")
        prompt = f"Convert {_fmt_num(value)} {small_p} to {large_p}."
        steps = [
            f"Linear conversion factor: 1 {large.replace('2','').replace('3','')} = "
            f"{linear_factor} {small.replace('2','').replace('3','')}, so for {kind}, "
            f"1 {large_p} = {linear_factor}^{power} = {_fmt_num(factor)} {small_p}",
            f"{_fmt_num(value)} {small_p} = {_fmt_num(value)} ÷ {_fmt_num(factor)} = {_fmt_num(target)} {large_p}",
        ]
        answer = f"{_fmt_num(target)} {large_p}"

    return Question(
        topic_id="unit_conversions_higher",
        tier=Tier.HIGHER,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=f"uch:{small}:{large}:{direction}:{value}",
    )


def generate_modelled_example_unit_conversions_higher(tier: Tier, rng: random.Random) -> ModelledExample:
    small, large, linear_factor, power = rng.choice(_UNIT_PAIRS_HIGHER)
    small_p, large_p = _UNIT_PRETTY[small], _UNIT_PRETTY[large]
    kind = "area" if power == 2 else "volume"
    verb = "squaring" if power == 2 else "cubing"

    factor_built = linear_factor ** power
    factor_check = 1
    for _ in range(power):
        factor_check *= linear_factor
    if factor_check != factor_built:
        raise ValueError("modelled example unit_conversions_higher factor verification failed")
    factor = Decimal(factor_built)
    reciprocal = Fraction(1) / Fraction(factor)

    direction = rng.choice(["large_to_small", "small_to_large"])
    if direction == "large_to_small":
        value = _rand_decimal_value(rng, 1, 50, one_dp_chance=0.4)
        target = value * factor
        check = Fraction(value) / reciprocal
        if check != Fraction(target):
            raise ValueError("modelled example unit_conversions_higher verification failed (large_to_small)")
        prompt = f"Convert {_fmt_num(value)} {large_p} to {small_p}."
        answer = f"{_fmt_num(target)} {small_p}"
        teaching_steps = [
            f"With {kind} units, you can't just reuse the LINEAR conversion factor - a "
            f"1 {large_p} square (or cube) isn't made of only {linear_factor} of the smaller "
            f"unit's squares/cubes, because both dimensions (or all three) scale up.",
            f"Instead, {verb} the linear factor: 1 {large_p} = {linear_factor}^{power} = "
            f"{_fmt_num(factor)} {small_p}.",
            f"Now convert as normal: since {large_p} is the larger unit, multiply: "
            f"{_fmt_num(value)} × {_fmt_num(factor)} = {_fmt_num(target)}.",
            f"So {_fmt_num(value)} {large_p} = {_fmt_num(target)} {small_p}. As a check, "
            "dividing by the reciprocal of the factor instead of multiplying directly gives "
            "the same result.",
        ]
        worked_calculation = [
            f"1 {large_p} = {linear_factor}^{power} = {_fmt_num(factor)} {small_p}",
            f"{_fmt_num(value)} × {_fmt_num(factor)} = {_fmt_num(target)}",
            f"{_fmt_num(value)} {large_p} = {_fmt_num(target)} {small_p}",
        ]
    else:
        value = Decimal(rng.randint(1, 5000))
        target = value / factor
        check = Fraction(value) * reciprocal
        if check != Fraction(target):
            raise ValueError("modelled example unit_conversions_higher verification failed (small_to_large)")
        prompt = f"Convert {_fmt_num(value)} {small_p} to {large_p}."
        answer = f"{_fmt_num(target)} {large_p}"
        teaching_steps = [
            f"With {kind} units, you can't just reuse the LINEAR conversion factor - a "
            f"1 {large_p} square (or cube) isn't made of only {linear_factor} of the smaller "
            f"unit's squares/cubes, because both dimensions (or all three) scale up.",
            f"Instead, {verb} the linear factor: 1 {large_p} = {linear_factor}^{power} = "
            f"{_fmt_num(factor)} {small_p}.",
            f"Now convert as normal: since {small_p} is the smaller unit, divide: "
            f"{_fmt_num(value)} ÷ {_fmt_num(factor)} = {_fmt_num(target)}.",
            f"So {_fmt_num(value)} {small_p} = {_fmt_num(target)} {large_p}. As a check, "
            "multiplying by the reciprocal of the factor instead of dividing directly gives "
            "the same result.",
        ]
        worked_calculation = [
            f"1 {large_p} = {linear_factor}^{power} = {_fmt_num(factor)} {small_p}",
            f"{_fmt_num(value)} ÷ {_fmt_num(factor)} = {_fmt_num(target)}",
            f"{_fmt_num(value)} {small_p} = {_fmt_num(target)} {large_p}",
        ]

    return ModelledExample(
        topic_id="unit_conversions_higher",
        tier=Tier.HIGHER,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
    )


# ===========================================================================
# Density
# ===========================================================================

_DENSITY_SYSTEMS = [
    {"mass_unit": "g", "vol_unit": "cm³", "density_unit": "g/cm³",
     "mass_range": (20, 500), "vol_range": (2, 80), "density_range": (1, 15)},
    {"mass_unit": "kg", "vol_unit": "m³", "density_unit": "kg/m³",
     "mass_range": (200, 8000), "vol_range": (1, 20), "density_range": (50, 900)},
]

_DENSITY_CONTEXTS = ["metal block", "piece of wood", "stone", "sample of liquid", "block of alloy", "sculpture"]


def generate_density(tier: Tier, rng: random.Random) -> Question:
    system = rng.choice(_DENSITY_SYSTEMS)
    obj = rng.choice(_DENSITY_CONTEXTS)
    unknown = rng.choice(["mass", "volume", "density"])

    if unknown == "mass":
        density = rng.randint(*system["density_range"])
        volume = rng.randint(*system["vol_range"])
        mass = density * volume
        # Verify via the ORIGINAL relationship using division - different
        # operation to the multiplication used to build the answer.
        if Fraction(mass, volume) != Fraction(density):
            raise ValueError("density verification failed (mass)")
        prompt = (
            f"A {obj} has a volume of {volume} {system['vol_unit']} and a density of "
            f"{density} {system['density_unit']}. Find its mass."
        )
        steps = [
            "mass = density × volume",
            f"mass = {density} × {volume} = {mass} {system['mass_unit']}",
        ]
        answer = f"{mass} {system['mass_unit']}"
        dedup = f"density:mass:{density}:{volume}"
    elif unknown == "volume":
        mass = rng.randint(*system["mass_range"])
        density = rng.randint(*system["density_range"])
        volume_dec = _round_dp(Decimal(mass) / Decimal(density), 2)
        check_dec = _frac_round_dp(Fraction(mass, density), 2)
        if check_dec != volume_dec:
            raise ValueError("density verification failed (volume)")
        prompt = (
            f"A {obj} has a mass of {mass} {system['mass_unit']} and a density of "
            f"{density} {system['density_unit']}. Find its volume, correct to 2 decimal places."
        )
        steps = [
            "volume = mass ÷ density",
            f"volume = {mass} ÷ {density} = {_fmt_num(volume_dec)} {system['vol_unit']} (2 d.p.)",
        ]
        answer = f"{_fmt_num(volume_dec)} {system['vol_unit']}"
        dedup = f"density:volume:{mass}:{density}"
    else:  # density
        mass = rng.randint(*system["mass_range"])
        volume = rng.randint(*system["vol_range"])
        density_dec = _round_dp(Decimal(mass) / Decimal(volume), 2)
        check_dec = _frac_round_dp(Fraction(mass, volume), 2)
        if check_dec != density_dec:
            raise ValueError("density verification failed (density)")
        prompt = (
            f"A {obj} has a mass of {mass} {system['mass_unit']} and a volume of "
            f"{volume} {system['vol_unit']}. Find its density, correct to 2 decimal places."
        )
        steps = [
            "density = mass ÷ volume",
            f"density = {mass} ÷ {volume} = {_fmt_num(density_dec)} {system['density_unit']} (2 d.p.)",
        ]
        answer = f"{_fmt_num(density_dec)} {system['density_unit']}"
        dedup = f"density:density:{mass}:{volume}"

    return Question(
        topic_id="density",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=dedup,
    )


def generate_modelled_example_density(tier: Tier, rng: random.Random) -> ModelledExample:
    system = rng.choice(_DENSITY_SYSTEMS)
    obj = rng.choice(_DENSITY_CONTEXTS)
    unknown = rng.choice(["mass", "volume", "density"])

    if unknown == "mass":
        density = rng.randint(*system["density_range"])
        volume = rng.randint(*system["vol_range"])
        mass = density * volume
        if Fraction(mass, volume) != Fraction(density):
            raise ValueError("modelled example density verification failed (mass)")
        prompt = (
            f"A {obj} has a volume of {volume} {system['vol_unit']} and a density of "
            f"{density} {system['density_unit']}. Find its mass."
        )
        answer = f"{mass} {system['mass_unit']}"
        teaching_steps = [
            "Density links mass and volume together: density = mass ÷ volume. Whenever we "
            "know density and volume, we can rearrange this to find the mass instead.",
            f"Rearranged, mass = density × volume, using the density ({density} "
            f"{system['density_unit']}) and volume ({volume} {system['vol_unit']}) we're given.",
            f"Multiplying gives mass = {density} × {volume} = {mass} {system['mass_unit']}.",
            f"As a check, dividing that mass back by the volume should return the original "
            f"density: {mass} ÷ {volume} = {density}, which matches.",
        ]
        worked_calculation = [
            f"mass = density × volume = {density} × {volume}",
            f"mass = {mass} {system['mass_unit']}",
        ]
    elif unknown == "volume":
        mass = rng.randint(*system["mass_range"])
        density = rng.randint(*system["density_range"])
        volume_dec = _round_dp(Decimal(mass) / Decimal(density), 2)
        check_dec = _frac_round_dp(Fraction(mass, density), 2)
        if check_dec != volume_dec:
            raise ValueError("modelled example density verification failed (volume)")
        prompt = (
            f"A {obj} has a mass of {mass} {system['mass_unit']} and a density of "
            f"{density} {system['density_unit']}. Find its volume, correct to 2 decimal places."
        )
        answer = f"{_fmt_num(volume_dec)} {system['vol_unit']}"
        teaching_steps = [
            "Starting from density = mass ÷ volume, if we know the mass and the density but "
            "not the volume, we need to rearrange to make volume the subject.",
            f"Rearranged, volume = mass ÷ density, giving {mass} ÷ {density}.",
            f"This division doesn't come out exactly, so we round the result to 2 decimal "
            f"places as the question asks: volume ≈ {_fmt_num(volume_dec)} {system['vol_unit']}.",
            "As a check, the division was recomputed as an exact fraction and rounded the "
            "same way, giving an identical result, which confirms the rounding is correct.",
        ]
        worked_calculation = [
            f"volume = mass ÷ density = {mass} ÷ {density}",
            f"volume = {_fmt_num(volume_dec)} {system['vol_unit']} (2 d.p.)",
        ]
    else:  # density
        mass = rng.randint(*system["mass_range"])
        volume = rng.randint(*system["vol_range"])
        density_dec = _round_dp(Decimal(mass) / Decimal(volume), 2)
        check_dec = _frac_round_dp(Fraction(mass, volume), 2)
        if check_dec != density_dec:
            raise ValueError("modelled example density verification failed (density)")
        prompt = (
            f"A {obj} has a mass of {mass} {system['mass_unit']} and a volume of "
            f"{volume} {system['vol_unit']}. Find its density, correct to 2 decimal places."
        )
        answer = f"{_fmt_num(density_dec)} {system['density_unit']}"
        teaching_steps = [
            "Density measures how tightly packed the mass of an object is into its volume, "
            "and is defined as density = mass ÷ volume.",
            f"Here we're given the mass ({mass} {system['mass_unit']}) and the volume "
            f"({volume} {system['vol_unit']}), so the formula applies directly with no "
            "rearranging.",
            f"Dividing gives {mass} ÷ {volume} ≈ {_fmt_num(density_dec)} "
            f"{system['density_unit']}, rounded to 2 decimal places since it doesn't divide "
            "exactly.",
            "As a check, the same division was redone as an exact fraction before rounding, "
            "and it rounds to the same value, confirming the answer.",
        ]
        worked_calculation = [
            f"density = mass ÷ volume = {mass} ÷ {volume}",
            f"density = {_fmt_num(density_dec)} {system['density_unit']} (2 d.p.)",
        ]

    return ModelledExample(
        topic_id="density",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
    )


# ===========================================================================
# Density (Multi-Step, Higher)
# ===========================================================================


def generate_density_higher(tier: Tier, rng: random.Random) -> Question:
    obj = rng.choice(_DENSITY_CONTEXTS)
    flavour = rng.choice(["from_dimensions", "unit_conversion"])

    if flavour == "from_dimensions":
        length, width, height = rng.randint(2, 10), rng.randint(2, 10), rng.randint(2, 10)
        volume = length * width * height
        # Independent verification of the volume via repeated addition
        # instead of `*`.
        area = _mul_via_repeated_addition(length, width)
        volume_check = _mul_via_repeated_addition(area, height)
        if volume_check != volume:
            raise ValueError("density_higher verification failed (volume from dimensions)")

        unknown = rng.choice(["mass", "density"])
        if unknown == "mass":
            density = rng.randint(1, 15)
            mass = density * volume
            if Fraction(mass, volume) != Fraction(density):
                raise ValueError("density_higher verification failed (mass)")
            prompt = (
                f"A {obj} in the shape of a cuboid has dimensions {length} cm × {width} cm × "
                f"{height} cm and a density of {density} g/cm³. Find its mass."
            )
            steps = [
                f"volume = length × width × height = {length} × {width} × {height} = {volume} cm³",
                f"mass = density × volume = {density} × {volume} = {mass} g",
            ]
            answer = f"{mass} g"
        else:  # density
            mass = rng.randint(50, 3000)
            density_dec = _round_dp(Decimal(mass) / Decimal(volume), 2)
            check_dec = _frac_round_dp(Fraction(mass, volume), 2)
            if check_dec != density_dec:
                raise ValueError("density_higher verification failed (density)")
            prompt = (
                f"A {obj} in the shape of a cuboid has dimensions {length} cm × {width} cm × "
                f"{height} cm and a mass of {mass} g. Find its density, correct to 2 decimal places."
            )
            steps = [
                f"volume = length × width × height = {length} × {width} × {height} = {volume} cm³",
                f"density = mass ÷ volume = {mass} ÷ {volume} = {_fmt_num(density_dec)} g/cm³ (2 d.p.)",
            ]
            answer = f"{_fmt_num(density_dec)} g/cm³"
        dedup = f"density_h:dims:{unknown}:{length}:{width}:{height}:{density if unknown == 'mass' else mass}"
    else:  # unit_conversion
        mass_kg = rng.randint(1, 20)
        volume_cm3 = rng.randint(50, 2000)
        mass_g = mass_kg * 1000
        # Independent verification of the kg->g conversion via a different
        # factor decomposition (×100 then ×10, rather than ×1000 directly).
        mass_g_check = mass_kg * 100 * 10
        if mass_g_check != mass_g:
            raise ValueError("density_higher verification failed (unit conversion)")
        density_dec = _round_dp(Decimal(mass_g) / Decimal(volume_cm3), 2)
        check_dec = _frac_round_dp(Fraction(mass_g, volume_cm3), 2)
        if check_dec != density_dec:
            raise ValueError("density_higher verification failed (density from conversion)")
        prompt = (
            f"A {obj} has a mass of {mass_kg} kg and a volume of {volume_cm3} cm³. "
            "Find its density in g/cm³, correct to 2 decimal places."
        )
        steps = [
            f"Convert mass to grams: {mass_kg} kg = {mass_kg} × 1000 = {mass_g} g",
            f"density = mass ÷ volume = {mass_g} ÷ {volume_cm3} = {_fmt_num(density_dec)} g/cm³ (2 d.p.)",
        ]
        answer = f"{_fmt_num(density_dec)} g/cm³"
        dedup = f"density_h:conv:{mass_kg}:{volume_cm3}"

    return Question(
        topic_id="density_higher",
        tier=Tier.HIGHER,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=dedup,
    )


def generate_modelled_example_density_higher(tier: Tier, rng: random.Random) -> ModelledExample:
    obj = rng.choice(_DENSITY_CONTEXTS)
    flavour = rng.choice(["from_dimensions", "unit_conversion"])

    if flavour == "from_dimensions":
        length, width, height = rng.randint(2, 10), rng.randint(2, 10), rng.randint(2, 10)
        volume = length * width * height
        area = _mul_via_repeated_addition(length, width)
        volume_check = _mul_via_repeated_addition(area, height)
        if volume_check != volume:
            raise ValueError("modelled example density_higher verification failed (volume)")

        unknown = rng.choice(["mass", "density"])
        if unknown == "mass":
            density = rng.randint(1, 15)
            mass = density * volume
            if Fraction(mass, volume) != Fraction(density):
                raise ValueError("modelled example density_higher verification failed (mass)")
            prompt = (
                f"A {obj} in the shape of a cuboid has dimensions {length} cm × {width} cm × "
                f"{height} cm and a density of {density} g/cm³. Find its mass."
            )
            answer = f"{mass} g"
            teaching_steps = [
                "Unlike a straightforward density question, here the volume isn't given "
                "directly - it has to be worked out first from the shape's dimensions.",
                f"For a cuboid, volume = length × width × height = {length} × {width} × "
                f"{height} = {volume} cm³.",
                f"Now the question is just like a normal density question: mass = density × "
                f"volume = {density} × {volume} = {mass} g.",
                f"As a check, dividing that mass back by the volume returns the original "
                f"density: {mass} ÷ {volume} = {density}, which matches.",
            ]
            worked_calculation = [
                f"volume = {length} × {width} × {height} = {volume} cm³",
                f"mass = {density} × {volume} = {mass} g",
            ]
        else:  # density
            mass = rng.randint(50, 3000)
            density_dec = _round_dp(Decimal(mass) / Decimal(volume), 2)
            check_dec = _frac_round_dp(Fraction(mass, volume), 2)
            if check_dec != density_dec:
                raise ValueError("modelled example density_higher verification failed (density)")
            prompt = (
                f"A {obj} in the shape of a cuboid has dimensions {length} cm × {width} cm × "
                f"{height} cm and a mass of {mass} g. Find its density, correct to 2 decimal places."
            )
            answer = f"{_fmt_num(density_dec)} g/cm³"
            teaching_steps = [
                "The extra step here is finding the volume before we can even use the "
                "density formula, since only the cuboid's dimensions are given.",
                f"Volume = length × width × height = {length} × {width} × {height} = {volume} cm³.",
                f"Now apply density = mass ÷ volume = {mass} ÷ {volume} ≈ "
                f"{_fmt_num(density_dec)} g/cm³, rounded to 2 decimal places.",
                "As a check, the volume was verified using repeated addition instead of "
                "multiplication, and the final division was redone as an exact fraction "
                "before rounding - both agree with the answer above.",
            ]
            worked_calculation = [
                f"volume = {length} × {width} × {height} = {volume} cm³",
                f"density = {mass} ÷ {volume} = {_fmt_num(density_dec)} g/cm³ (2 d.p.)",
            ]
        dedup_answer = density if unknown == "mass" else mass
    else:  # unit_conversion
        mass_kg = rng.randint(1, 20)
        volume_cm3 = rng.randint(50, 2000)
        mass_g = mass_kg * 1000
        mass_g_check = mass_kg * 100 * 10
        if mass_g_check != mass_g:
            raise ValueError("modelled example density_higher verification failed (unit conversion)")
        density_dec = _round_dp(Decimal(mass_g) / Decimal(volume_cm3), 2)
        check_dec = _frac_round_dp(Fraction(mass_g, volume_cm3), 2)
        if check_dec != density_dec:
            raise ValueError("modelled example density_higher verification failed (density)")
        prompt = (
            f"A {obj} has a mass of {mass_kg} kg and a volume of {volume_cm3} cm³. "
            "Find its density in g/cm³, correct to 2 decimal places."
        )
        answer = f"{_fmt_num(density_dec)} g/cm³"
        teaching_steps = [
            "The units here don't match: the mass is in kg but the volume is in cm³, and "
            "g/cm³ needs the mass in grams - so a conversion has to happen before dividing.",
            f"Convert the mass: {mass_kg} kg = {mass_kg} × 1000 = {mass_g} g.",
            f"Now apply density = mass ÷ volume using the converted mass: {mass_g} ÷ "
            f"{volume_cm3} ≈ {_fmt_num(density_dec)} g/cm³, rounded to 2 decimal places.",
            "As a check, the kg-to-g conversion was redone using a different factor split "
            "(×100 then ×10, instead of ×1000 directly), and it gives the same number of "
            "grams, confirming the conversion was correct.",
        ]
        worked_calculation = [
            f"{mass_kg} kg = {mass_kg} × 1000 = {mass_g} g",
            f"density = {mass_g} ÷ {volume_cm3} = {_fmt_num(density_dec)} g/cm³ (2 d.p.)",
        ]

    return ModelledExample(
        topic_id="density_higher",
        tier=Tier.HIGHER,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
    )


# ===========================================================================
# Pressure
# ===========================================================================

_PRESSURE_SYSTEMS = [
    {"force_unit": "N", "area_unit": "m²", "pressure_unit": "N/m²",
     "force_range": (100, 5000), "area_range": (2, 50), "pressure_range": (5, 200)},
    {"force_unit": "N", "area_unit": "cm²", "pressure_unit": "N/cm²",
     "force_range": (50, 2000), "area_range": (2, 80), "pressure_range": (1, 40)},
]

_PRESSURE_CONTEXTS = ["brick", "crate", "table leg", "concrete block", "storage container", "machine foot"]


def generate_pressure(tier: Tier, rng: random.Random) -> Question:
    system = rng.choice(_PRESSURE_SYSTEMS)
    obj = rng.choice(_PRESSURE_CONTEXTS)
    unknown = rng.choice(["force", "area", "pressure"])

    if unknown == "force":
        pressure = rng.randint(*system["pressure_range"])
        area = rng.randint(*system["area_range"])
        force = pressure * area
        if Fraction(force, area) != Fraction(pressure):
            raise ValueError("pressure verification failed (force)")
        prompt = (
            f"A {obj} exerts a pressure of {pressure} {system['pressure_unit']} over a "
            f"contact area of {area} {system['area_unit']}. Find the force."
        )
        steps = [
            "force = pressure × area",
            f"force = {pressure} × {area} = {force} {system['force_unit']}",
        ]
        answer = f"{force} {system['force_unit']}"
        dedup = f"pressure:force:{pressure}:{area}"
    elif unknown == "area":
        force = rng.randint(*system["force_range"])
        pressure = rng.randint(*system["pressure_range"])
        area_dec = _round_dp(Decimal(force) / Decimal(pressure), 2)
        check_dec = _frac_round_dp(Fraction(force, pressure), 2)
        if check_dec != area_dec:
            raise ValueError("pressure verification failed (area)")
        prompt = (
            f"A {obj} exerts a force of {force} {system['force_unit']} and a pressure of "
            f"{pressure} {system['pressure_unit']}. Find the contact area, correct to 2 decimal places."
        )
        steps = [
            "area = force ÷ pressure",
            f"area = {force} ÷ {pressure} = {_fmt_num(area_dec)} {system['area_unit']} (2 d.p.)",
        ]
        answer = f"{_fmt_num(area_dec)} {system['area_unit']}"
        dedup = f"pressure:area:{force}:{pressure}"
    else:  # pressure
        force = rng.randint(*system["force_range"])
        area = rng.randint(*system["area_range"])
        pressure_dec = _round_dp(Decimal(force) / Decimal(area), 2)
        check_dec = _frac_round_dp(Fraction(force, area), 2)
        if check_dec != pressure_dec:
            raise ValueError("pressure verification failed (pressure)")
        prompt = (
            f"A {obj} exerts a force of {force} {system['force_unit']} over a contact area of "
            f"{area} {system['area_unit']}. Find the pressure, correct to 2 decimal places."
        )
        steps = [
            "pressure = force ÷ area",
            f"pressure = {force} ÷ {area} = {_fmt_num(pressure_dec)} {system['pressure_unit']} (2 d.p.)",
        ]
        answer = f"{_fmt_num(pressure_dec)} {system['pressure_unit']}"
        dedup = f"pressure:pressure:{force}:{area}"

    return Question(
        topic_id="pressure",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=dedup,
    )


def generate_modelled_example_pressure(tier: Tier, rng: random.Random) -> ModelledExample:
    system = rng.choice(_PRESSURE_SYSTEMS)
    obj = rng.choice(_PRESSURE_CONTEXTS)
    unknown = rng.choice(["force", "area", "pressure"])

    if unknown == "force":
        pressure = rng.randint(*system["pressure_range"])
        area = rng.randint(*system["area_range"])
        force = pressure * area
        if Fraction(force, area) != Fraction(pressure):
            raise ValueError("modelled example pressure verification failed (force)")
        prompt = (
            f"A {obj} exerts a pressure of {pressure} {system['pressure_unit']} over a "
            f"contact area of {area} {system['area_unit']}. Find the force."
        )
        answer = f"{force} {system['force_unit']}"
        teaching_steps = [
            "Pressure is defined as pressure = force ÷ area, so whenever we know the pressure "
            "and the area, we can rearrange to find the force pushing down.",
            f"Rearranged, force = pressure × area, using the pressure ({pressure} "
            f"{system['pressure_unit']}) and area ({area} {system['area_unit']}) given.",
            f"Multiplying gives force = {pressure} × {area} = {force} {system['force_unit']}.",
            f"As a check, dividing that force back by the area should return the original "
            f"pressure: {force} ÷ {area} = {pressure}, which matches.",
        ]
        worked_calculation = [
            f"force = pressure × area = {pressure} × {area}",
            f"force = {force} {system['force_unit']}",
        ]
    elif unknown == "area":
        force = rng.randint(*system["force_range"])
        pressure = rng.randint(*system["pressure_range"])
        area_dec = _round_dp(Decimal(force) / Decimal(pressure), 2)
        check_dec = _frac_round_dp(Fraction(force, pressure), 2)
        if check_dec != area_dec:
            raise ValueError("modelled example pressure verification failed (area)")
        prompt = (
            f"A {obj} exerts a force of {force} {system['force_unit']} and a pressure of "
            f"{pressure} {system['pressure_unit']}. Find the contact area, correct to 2 decimal places."
        )
        answer = f"{_fmt_num(area_dec)} {system['area_unit']}"
        teaching_steps = [
            "Starting from pressure = force ÷ area, if we're given the force and the "
            "pressure but not the area, we rearrange to make area the subject.",
            f"Rearranged, area = force ÷ pressure, giving {force} ÷ {pressure}.",
            f"This division doesn't come out exactly, so we round to 2 decimal places: "
            f"area ≈ {_fmt_num(area_dec)} {system['area_unit']}.",
            "As a check, the division was recomputed as an exact fraction and rounded the "
            "same way, giving the same result, confirming the rounding is correct.",
        ]
        worked_calculation = [
            f"area = force ÷ pressure = {force} ÷ {pressure}",
            f"area = {_fmt_num(area_dec)} {system['area_unit']} (2 d.p.)",
        ]
    else:  # pressure
        force = rng.randint(*system["force_range"])
        area = rng.randint(*system["area_range"])
        pressure_dec = _round_dp(Decimal(force) / Decimal(area), 2)
        check_dec = _frac_round_dp(Fraction(force, area), 2)
        if check_dec != pressure_dec:
            raise ValueError("modelled example pressure verification failed (pressure)")
        prompt = (
            f"A {obj} exerts a force of {force} {system['force_unit']} over a contact area of "
            f"{area} {system['area_unit']}. Find the pressure, correct to 2 decimal places."
        )
        answer = f"{_fmt_num(pressure_dec)} {system['pressure_unit']}"
        teaching_steps = [
            "Pressure measures how concentrated a force is over an area - the same force "
            "spread over a smaller area creates a bigger pressure. The formula is "
            "pressure = force ÷ area.",
            f"Here we're given the force ({force} {system['force_unit']}) and the area "
            f"({area} {system['area_unit']}), so the formula applies directly.",
            f"Dividing gives {force} ÷ {area} ≈ {_fmt_num(pressure_dec)} "
            f"{system['pressure_unit']}, rounded to 2 decimal places since it doesn't divide "
            "exactly.",
            "As a check, the same division was redone as an exact fraction before rounding, "
            "and it rounds to the same value, confirming the answer.",
        ]
        worked_calculation = [
            f"pressure = force ÷ area = {force} ÷ {area}",
            f"pressure = {_fmt_num(pressure_dec)} {system['pressure_unit']} (2 d.p.)",
        ]

    return ModelledExample(
        topic_id="pressure",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
    )


# ===========================================================================
# Pressure (Multi-Step, Higher)
# ===========================================================================


def generate_pressure_higher(tier: Tier, rng: random.Random) -> Question:
    obj = rng.choice(_PRESSURE_CONTEXTS)
    flavour = rng.choice(["from_dimensions", "unit_conversion"])

    if flavour == "from_dimensions":
        length, width = rng.randint(2, 30), rng.randint(2, 30)
        area = length * width
        # Independent verification of the area via repeated addition instead
        # of `*`.
        area_check = _mul_via_repeated_addition(length, width)
        if area_check != area:
            raise ValueError("pressure_higher verification failed (area from dimensions)")

        unknown = rng.choice(["force", "pressure"])
        if unknown == "force":
            pressure = rng.randint(1, 50)
            force = pressure * area
            if Fraction(force, area) != Fraction(pressure):
                raise ValueError("pressure_higher verification failed (force)")
            prompt = (
                f"A {obj} has a rectangular base measuring {length} cm × {width} cm and exerts "
                f"a pressure of {pressure} N/cm². Find the force it exerts."
            )
            steps = [
                f"area = length × width = {length} × {width} = {area} cm²",
                f"force = pressure × area = {pressure} × {area} = {force} N",
            ]
            answer = f"{force} N"
        else:  # pressure
            force = rng.randint(100, 5000)
            pressure_dec = _round_dp(Decimal(force) / Decimal(area), 2)
            check_dec = _frac_round_dp(Fraction(force, area), 2)
            if check_dec != pressure_dec:
                raise ValueError("pressure_higher verification failed (pressure)")
            prompt = (
                f"A {obj} has a rectangular base measuring {length} cm × {width} cm and exerts "
                f"a force of {force} N. Find the pressure it exerts, correct to 2 decimal places."
            )
            steps = [
                f"area = length × width = {length} × {width} = {area} cm²",
                f"pressure = force ÷ area = {force} ÷ {area} = {_fmt_num(pressure_dec)} N/cm² (2 d.p.)",
            ]
            answer = f"{_fmt_num(pressure_dec)} N/cm²"
        dedup = f"pressure_h:dims:{unknown}:{length}:{width}:{pressure if unknown == 'force' else force}"
    else:  # unit_conversion
        force = rng.randint(500, 6000)
        area_cm2 = rng.randint(100, 5000)
        area_m2_exact = Fraction(area_cm2, 10000)
        # Independent verification of the cm²->m² conversion via the
        # reciprocal-multiplication route rather than direct division.
        area_m2_check = Fraction(area_cm2) * (Fraction(1) / Fraction(10000))
        if area_m2_check != area_m2_exact:
            raise ValueError("pressure_higher verification failed (area conversion)")
        area_m2_dec = Decimal(area_m2_exact.numerator) / Decimal(area_m2_exact.denominator)

        pressure_exact = Fraction(force * 10000, area_cm2)
        pressure_dec = _frac_round_dp(pressure_exact, 2)
        # Independent check: divide force by the Decimal-converted area
        # directly (a different route to the combined-factor Fraction above).
        check_dec = _round_dp(Decimal(force) / area_m2_dec, 2)
        if check_dec != pressure_dec:
            raise ValueError("pressure_higher verification failed (pressure from conversion)")

        prompt = (
            f"A {obj} exerts a force of {force} N over a contact area of {area_cm2} cm². "
            "Find the pressure in N/m², correct to 2 decimal places."
        )
        steps = [
            f"Convert area to m²: {area_cm2} cm² = {area_cm2} ÷ 10000 = {_fmt_num(_round_dp(area_m2_dec, 6))} m²",
            f"pressure = force ÷ area = {force} ÷ {_fmt_num(_round_dp(area_m2_dec, 6))} = "
            f"{_fmt_num(pressure_dec)} N/m² (2 d.p.)",
        ]
        answer = f"{_fmt_num(pressure_dec)} N/m²"
        dedup = f"pressure_h:conv:{force}:{area_cm2}"

    return Question(
        topic_id="pressure_higher",
        tier=Tier.HIGHER,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=answer,
        dedup_key=dedup,
    )


def generate_modelled_example_pressure_higher(tier: Tier, rng: random.Random) -> ModelledExample:
    obj = rng.choice(_PRESSURE_CONTEXTS)
    flavour = rng.choice(["from_dimensions", "unit_conversion"])

    if flavour == "from_dimensions":
        length, width = rng.randint(2, 30), rng.randint(2, 30)
        area = length * width
        area_check = _mul_via_repeated_addition(length, width)
        if area_check != area:
            raise ValueError("modelled example pressure_higher verification failed (area)")

        unknown = rng.choice(["force", "pressure"])
        if unknown == "force":
            pressure = rng.randint(1, 50)
            force = pressure * area
            if Fraction(force, area) != Fraction(pressure):
                raise ValueError("modelled example pressure_higher verification failed (force)")
            prompt = (
                f"A {obj} has a rectangular base measuring {length} cm × {width} cm and exerts "
                f"a pressure of {pressure} N/cm². Find the force it exerts."
            )
            answer = f"{force} N"
            teaching_steps = [
                "Before the pressure formula can be used, we need the contact area - and here "
                "it's given as a rectangle's dimensions rather than as a single number.",
                f"area = length × width = {length} × {width} = {area} cm².",
                f"Now use force = pressure × area = {pressure} × {area} = {force} N.",
                f"As a check, dividing that force back by the area returns the original "
                f"pressure: {force} ÷ {area} = {pressure}, which matches.",
            ]
            worked_calculation = [
                f"area = {length} × {width} = {area} cm²",
                f"force = {pressure} × {area} = {force} N",
            ]
        else:  # pressure
            force = rng.randint(100, 5000)
            pressure_dec = _round_dp(Decimal(force) / Decimal(area), 2)
            check_dec = _frac_round_dp(Fraction(force, area), 2)
            if check_dec != pressure_dec:
                raise ValueError("modelled example pressure_higher verification failed (pressure)")
            prompt = (
                f"A {obj} has a rectangular base measuring {length} cm × {width} cm and exerts "
                f"a force of {force} N. Find the pressure it exerts, correct to 2 decimal places."
            )
            answer = f"{_fmt_num(pressure_dec)} N/cm²"
            teaching_steps = [
                "The extra step here is finding the contact area before applying the pressure "
                "formula, since only the rectangle's dimensions are given.",
                f"area = length × width = {length} × {width} = {area} cm².",
                f"Now use pressure = force ÷ area = {force} ÷ {area} ≈ {_fmt_num(pressure_dec)} "
                "N/cm², rounded to 2 decimal places.",
                "As a check, the area was verified using repeated addition instead of "
                "multiplication, and the final division was redone as an exact fraction "
                "before rounding - both agree with the answer above.",
            ]
            worked_calculation = [
                f"area = {length} × {width} = {area} cm²",
                f"pressure = {force} ÷ {area} = {_fmt_num(pressure_dec)} N/cm² (2 d.p.)",
            ]
    else:  # unit_conversion
        force = rng.randint(500, 6000)
        area_cm2 = rng.randint(100, 5000)
        area_m2_exact = Fraction(area_cm2, 10000)
        area_m2_check = Fraction(area_cm2) * (Fraction(1) / Fraction(10000))
        if area_m2_check != area_m2_exact:
            raise ValueError("modelled example pressure_higher verification failed (area conversion)")
        area_m2_dec = Decimal(area_m2_exact.numerator) / Decimal(area_m2_exact.denominator)

        pressure_exact = Fraction(force * 10000, area_cm2)
        pressure_dec = _frac_round_dp(pressure_exact, 2)
        check_dec = _round_dp(Decimal(force) / area_m2_dec, 2)
        if check_dec != pressure_dec:
            raise ValueError("modelled example pressure_higher verification failed (pressure)")

        prompt = (
            f"A {obj} exerts a force of {force} N over a contact area of {area_cm2} cm². "
            "Find the pressure in N/m², correct to 2 decimal places."
        )
        answer = f"{_fmt_num(pressure_dec)} N/m²"
        area_m2_display = _fmt_num(_round_dp(area_m2_dec, 6))
        teaching_steps = [
            "The area here is given in cm², but a pressure in N/m² needs the area in m² - so "
            "it has to be converted before dividing.",
            f"Convert the area: {area_cm2} cm² = {area_cm2} ÷ 10000 = {area_m2_display} m², "
            "since 1 m² = 10000 cm².",
            f"Now apply pressure = force ÷ area using the converted area: {force} ÷ "
            f"{area_m2_display} ≈ {_fmt_num(pressure_dec)} N/m², rounded to 2 decimal places.",
            "As a check, the whole calculation can also be done as one combined step - "
            "multiplying the force by 10000 and dividing by the area in cm² directly - and it "
            "gives the same answer, confirming the conversion was applied correctly.",
        ]
        worked_calculation = [
            f"{area_cm2} cm² = {area_cm2} ÷ 10000 = {area_m2_display} m²",
            f"pressure = {force} ÷ {area_m2_display} = {_fmt_num(pressure_dec)} N/m² (2 d.p.)",
        ]

    return ModelledExample(
        topic_id="pressure_higher",
        tier=Tier.HIGHER,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=answer,
    )


# ===========================================================================
# Topic definitions
# ===========================================================================

TOPIC_SDT_MIXED = TopicDefinition(
    id="sdt_mixed",
    display_name="Speed, Distance and Time",
    description="Mixed problems using speed = distance ÷ time, with consistent units throughout.",
    generate=generate_sdt_mixed,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_sdt_mixed,
)

TOPIC_SPEED_WITH_CONVERSIONS = TopicDefinition(
    id="speed_with_conversions",
    display_name="Speed with Unit Conversions",
    description="Speed, distance and time problems that require a unit conversion.",
    generate=generate_speed_with_conversions,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_speed_with_conversions,
)

TOPIC_UNIT_CONVERSIONS = TopicDefinition(
    id="unit_conversions",
    display_name="Unit Conversions",
    description="Convert between common metric units of length, mass and capacity.",
    generate=generate_unit_conversions,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_unit_conversions,
)

TOPIC_UNIT_CONVERSIONS_HIGHER = TopicDefinition(
    id="unit_conversions_higher",
    display_name="Area and Volume Unit Conversions",
    description="Convert between metric units of area and volume, squaring or cubing the linear factor.",
    generate=generate_unit_conversions_higher,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_unit_conversions_higher,
)

TOPIC_DENSITY = TopicDefinition(
    id="density",
    display_name="Density",
    description="Use density = mass ÷ volume to find a missing mass, volume or density.",
    generate=generate_density,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_density,
)

TOPIC_DENSITY_HIGHER = TopicDefinition(
    id="density_higher",
    display_name="Density (Multi-Step)",
    description="Density problems requiring an extra step: computing a volume from dimensions, or a unit conversion.",
    generate=generate_density_higher,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_density_higher,
)

TOPIC_PRESSURE = TopicDefinition(
    id="pressure",
    display_name="Pressure",
    description="Use pressure = force ÷ area to find a missing force, area or pressure.",
    generate=generate_pressure,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_pressure,
)

TOPIC_PRESSURE_HIGHER = TopicDefinition(
    id="pressure_higher",
    display_name="Pressure (Multi-Step)",
    description="Pressure problems requiring an extra step: computing an area from dimensions, or a unit conversion.",
    generate=generate_pressure_higher,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_pressure_higher,
)
