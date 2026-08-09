"""Map scales and scale drawings: converting between a distance measured on a
map (in cm) and the real-life distance it represents, given a map scale in
either ratio form ("1 : 25000") or verbal form ("1 cm represents 5 km").
A standalone new file/group (not an addition to bearings.py), following that
file's SECTION/GROUP declaration convention.
"""

import random
from fractions import Fraction

from app.core.models import ModelledExample, Question, Tier
from app.topics.base import TopicDefinition

SECTION = "geometry"
GROUP_MAP_SCALES = "Map Scales and Scale Drawings"

# Ratio-form scales: "1 : n" means 1 cm on the map represents n cm in real
# life. All three are common real OS map scales, and each n is a multiple of
# 100 so the real-world distance per map cm, expressed in metres, is always
# a whole number (n / 100).
_RATIO_SCALES = [10000, 25000, 50000]

# Verbal-form scales: "1 cm represents k km" - expressed directly in km per
# map cm, so no unit conversion is needed to interpret them.
_VERBAL_SCALES = [1, 2, 5, 10]


def _scale_bank_entry(rng: random.Random) -> dict:
    """Pick one scale from the bank, either ratio or verbal form, and return
    it alongside the real-world distance (a Fraction) represented by a
    single map centimetre, in a fixed display unit."""
    kind = rng.choice(["ratio", "verbal"])
    if kind == "ratio":
        n = rng.choice(_RATIO_SCALES)
        real_per_cm = Fraction(n, 100)  # metres per map cm
        return {"kind": "ratio", "text": f"1 : {n}", "real_per_cm": real_per_cm, "unit": "m", "ratio_n": n}
    km = rng.choice(_VERBAL_SCALES)
    real_per_cm = Fraction(km)  # km per map cm
    return {"kind": "verbal", "text": f"1 cm represents {km} km", "real_per_cm": real_per_cm, "unit": "km"}


def _fmt_ratio(fr: Fraction) -> str:
    if fr.denominator == 1:
        return str(fr.numerator)
    return f"{fr.numerator}/{fr.denominator}"


def _scale_meaning_step(scale: dict) -> str:
    if scale["kind"] == "ratio":
        return (
            f"The scale {scale['text']} means 1 cm on the map represents {scale['ratio_n']} cm in real "
            f"life, which is {_fmt_ratio(scale['real_per_cm'])} {scale['unit']}."
        )
    return f"The scale means 1 cm on the map represents {_fmt_ratio(scale['real_per_cm'])} {scale['unit']} in real life."


def _build_case(rng: random.Random) -> dict:
    """Shared parameter generation + verification for both the real
    generator and the modelled example - the two differ only in how they
    present the same underlying calculation."""
    scale = _scale_bank_entry(rng)
    real_per_cm = scale["real_per_cm"]
    map_cm = rng.randint(2, 15)

    real_value_frac = Fraction(map_cm) * real_per_cm
    if real_value_frac.denominator != 1:
        raise ValueError("map_scale_drawings: non-integer real-world distance constructed")
    real_value = real_value_frac.numerator

    direction = rng.choice(["map_to_real", "real_to_map"])

    # Independent verification: compute the answer one way (multiply the map
    # distance by the scale factor, or divide the real distance by it), then
    # apply the INVERSE operation to that computed answer and confirm the
    # original given value is exactly recovered - a Fraction-based cross-
    # multiplication check, mirroring how ratio.py's
    # generate_ratio_shape_similar_foundation verifies a scale-factor
    # relationship (Fraction(len_b, len_a) == Fraction(answer, len_a2)).
    if direction == "map_to_real":
        computed_real = Fraction(map_cm) * real_per_cm
        if computed_real.denominator != 1:
            raise ValueError("map_scale_drawings: non-integer real-world distance constructed")
        recovered_map_cm = computed_real / real_per_cm
        if recovered_map_cm != Fraction(map_cm):
            raise ValueError("map_scale_drawings verification failed (map_to_real): inverse did not recover map_cm")
    else:
        computed_map_cm = Fraction(real_value) / real_per_cm
        if computed_map_cm.denominator != 1:
            raise ValueError("map_scale_drawings: non-integer map distance constructed")
        recovered_real = computed_map_cm * real_per_cm
        if recovered_real != Fraction(real_value):
            raise ValueError("map_scale_drawings verification failed (real_to_map): inverse did not recover real distance")
        if computed_map_cm.numerator != map_cm:
            raise ValueError("map_scale_drawings verification failed (real_to_map): recomputed map_cm mismatch")

    return {
        "scale": scale,
        "map_cm": map_cm,
        "real_value": real_value,
        "direction": direction,
    }


def _prompt_and_steps(v: dict) -> tuple:
    scale = v["scale"]
    unit = scale["unit"]
    meaning_step = _scale_meaning_step(scale)

    if v["direction"] == "map_to_real":
        prompt = (
            f"A map has a scale of {scale['text']}. The distance between two towns on the map is "
            f"{v['map_cm']} cm. Find the real-life distance between the towns, in {unit}."
        )
        steps = [
            meaning_step,
            f"Real-life distance = {v['map_cm']} × {_fmt_ratio(scale['real_per_cm'])} = {v['real_value']} {unit}",
        ]
        final_answer = f"{v['real_value']} {unit}"
    else:
        prompt = (
            f"A map has a scale of {scale['text']}. Two towns are {v['real_value']} {unit} apart in real "
            "life. Find the distance between the towns on the map, in cm."
        )
        steps = [
            meaning_step,
            f"Map distance = {v['real_value']} ÷ {_fmt_ratio(scale['real_per_cm'])} = {v['map_cm']} cm",
        ]
        final_answer = f"{v['map_cm']} cm"

    return prompt, steps, final_answer


def generate_map_scale_drawings(tier: Tier, rng: random.Random) -> Question:
    v = _build_case(rng)
    prompt, steps, final_answer = _prompt_and_steps(v)
    scale = v["scale"]
    dedup_key = f"map_scale:{scale['kind']}:{scale['text']}:{v['map_cm']}:{v['direction']}"
    return Question(
        topic_id="map_scale_drawings_F",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        solution_steps=tuple(steps),
        final_answer=final_answer,
        dedup_key=dedup_key,
    )


def generate_modelled_example_map_scale_drawings(tier: Tier, rng: random.Random) -> ModelledExample:
    v = _build_case(rng)
    prompt, steps, final_answer = _prompt_and_steps(v)
    scale = v["scale"]
    unit = scale["unit"]

    if v["direction"] == "map_to_real":
        teaching_steps = [
            "A map scale tells you how a distance measured on the map relates to the real, physical "
            "distance it stands for - the first job is always to work out exactly how much real-world "
            "distance a single map centimetre represents.",
            steps[0],
            f"To convert a measured map distance into a real-life one, multiply it by that amount: "
            f"{v['map_cm']} cm on the map × {_fmt_ratio(scale['real_per_cm'])} {unit} per cm = "
            f"{v['real_value']} {unit}.",
            f"So the real-life distance between the two towns is {final_answer}.",
        ]
    else:
        teaching_steps = [
            "This time the real-life distance is given, and the map distance is unknown - since map "
            "distance × (real distance per map cm) = real-life distance, finding the map distance means "
            "doing the inverse: dividing instead of multiplying.",
            steps[0],
            f"Divide the real-life distance by the real distance represented by 1 cm: "
            f"{v['real_value']} {unit} ÷ {_fmt_ratio(scale['real_per_cm'])} {unit} per cm = {v['map_cm']} cm.",
            f"So the two towns are {final_answer} apart on the map.",
        ]

    return ModelledExample(
        topic_id="map_scale_drawings_F",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        worked_calculation=tuple(steps),
        teaching_steps=tuple(teaching_steps),
        final_answer=final_answer,
    )


TOPIC_MAP_SCALE_DRAWINGS = TopicDefinition(
    id="map_scale_drawings_F",
    display_name="Map Scales and Scale Drawings",
    description=(
        "Convert between a distance measured on a map and the real-life distance it represents, given "
        "a map scale in ratio form (1 : n) or in words (1 cm represents n km)."
    ),
    generate=generate_map_scale_drawings,
    section=SECTION,
    group=GROUP_MAP_SCALES,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_map_scale_drawings,
)
