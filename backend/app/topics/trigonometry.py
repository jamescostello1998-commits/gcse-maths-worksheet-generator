import math
import random
from decimal import ROUND_HALF_UP, Decimal

from app.core.models import DiagramSpec, ModelledExample, Question, Tier
from app.topics.base import TopicDefinition

SECTION = "geometry"
GROUP = "Trigonometry"

_ROLE_NAME = {"opp": "opposite", "adj": "adjacent", "hyp": "hypotenuse"}

# "Finding a side" shapes where the unknown is the numerator (unknown = known x ratio) -
# no rearranging required, so these are the Foundation-appropriate subset.
_SIDE_SHAPES_NO_REARRANGE = ["hyp_opp", "hyp_adj", "adj_opp"]
_SIDE_SHAPES_ALL = _SIDE_SHAPES_NO_REARRANGE + ["opp_adj", "adj_hyp", "opp_hyp"]


def _fmt_dec(d: Decimal) -> str:
    return format(d, "f")


def _round_sf(value: float, sig_figs: int) -> Decimal:
    d = Decimal(str(value))
    if d == 0:
        return d
    exp = d.adjusted()
    return d.quantize(Decimal(1).scaleb(exp - sig_figs + 1), rounding=ROUND_HALF_UP)


def _round_dp(value: float, dp: int) -> Decimal:
    return Decimal(str(value)).quantize(Decimal(1).scaleb(-dp), rounding=ROUND_HALF_UP)


def _trig_side_question(rng: random.Random, *, angle_lo, angle_hi, side_lo, side_hi, sig_figs, shapes, topic_id, tier) -> Question:
    angle_deg = rng.randint(angle_lo, angle_hi)
    rad = math.radians(angle_deg)
    known_val = rng.randint(side_lo, side_hi)
    shape = rng.choice(shapes)

    if shape == "hyp_opp":
        unknown_val = known_val * math.sin(rad)
        check_angle = math.degrees(math.asin(unknown_val / known_val))
        ratio, calc = "sin", f"x = {known_val} × sin({angle_deg}°)"
        known_role, unknown_role = "hyp", "opp"
    elif shape == "hyp_adj":
        unknown_val = known_val * math.cos(rad)
        check_angle = math.degrees(math.acos(unknown_val / known_val))
        ratio, calc = "cos", f"x = {known_val} × cos({angle_deg}°)"
        known_role, unknown_role = "hyp", "adj"
    elif shape == "adj_opp":
        unknown_val = known_val * math.tan(rad)
        check_angle = math.degrees(math.atan(unknown_val / known_val))
        ratio, calc = "tan", f"x = {known_val} × tan({angle_deg}°)"
        known_role, unknown_role = "adj", "opp"
    elif shape == "opp_adj":
        unknown_val = known_val / math.tan(rad)
        check_angle = math.degrees(math.atan(known_val / unknown_val))
        ratio, calc = "tan", f"x = {known_val} ÷ tan({angle_deg}°)"
        known_role, unknown_role = "opp", "adj"
    elif shape == "adj_hyp":
        unknown_val = known_val / math.cos(rad)
        check_angle = math.degrees(math.acos(known_val / unknown_val))
        ratio, calc = "cos", f"x = {known_val} ÷ cos({angle_deg}°)"
        known_role, unknown_role = "adj", "hyp"
    else:  # opp_hyp
        unknown_val = known_val / math.sin(rad)
        check_angle = math.degrees(math.asin(known_val / unknown_val))
        ratio, calc = "sin", f"x = {known_val} ÷ sin({angle_deg}°)"
        known_role, unknown_role = "opp", "hyp"

    # Independent verification: invert the computed side back to the original angle
    # using the inverse trig function - a different computation path than the one
    # used to derive the side - and check it reproduces angle_deg.
    if abs(check_angle - angle_deg) > 1e-6:
        raise ValueError("trig_side verification failed: angle does not invert cleanly")

    rounded = _round_sf(unknown_val, sig_figs)
    labels = {"adj": None, "opp": None, "hyp": None}
    labels[known_role] = f"{known_val} cm"
    labels[unknown_role] = "x cm"

    steps = [
        f"We know the {_ROLE_NAME[known_role]} and want the {_ROLE_NAME[unknown_role]}, so use {ratio}.",
        f"{calc} = {_fmt_dec(rounded)} (to {sig_figs} s.f.)",
    ]
    return Question(
        topic_id=topic_id,
        tier=tier,
        prompt=f"In the right-angled triangle shown, find the length of x, correct to {sig_figs} significant figures.",
        solution_steps=tuple(steps),
        final_answer=f"{_fmt_dec(rounded)} cm",
        dedup_key=f"trig_side:{shape}:{angle_deg}:{known_val}",
        diagram=DiagramSpec(
            kind="trig_triangle",
            params={
                "adjacent_label": labels["adj"],
                "opposite_label": labels["opp"],
                "hyp_label": labels["hyp"],
                "angle_label": f"{angle_deg}°",
            },
        ),
    )


def _trig_side_modelled_example(rng: random.Random, *, angle_lo, angle_hi, side_lo, side_hi, sig_figs, shapes, topic_id, tier) -> ModelledExample:
    angle_deg = rng.randint(angle_lo, angle_hi)
    rad = math.radians(angle_deg)
    known_val = rng.randint(side_lo, side_hi)
    shape = rng.choice(shapes)

    if shape == "hyp_opp":
        unknown_val = known_val * math.sin(rad)
        check_angle = math.degrees(math.asin(unknown_val / known_val))
        ratio, calc = "sin", f"x = {known_val} × sin({angle_deg}°)"
        known_role, unknown_role = "hyp", "opp"
    elif shape == "hyp_adj":
        unknown_val = known_val * math.cos(rad)
        check_angle = math.degrees(math.acos(unknown_val / known_val))
        ratio, calc = "cos", f"x = {known_val} × cos({angle_deg}°)"
        known_role, unknown_role = "hyp", "adj"
    elif shape == "adj_opp":
        unknown_val = known_val * math.tan(rad)
        check_angle = math.degrees(math.atan(unknown_val / known_val))
        ratio, calc = "tan", f"x = {known_val} × tan({angle_deg}°)"
        known_role, unknown_role = "adj", "opp"
    elif shape == "opp_adj":
        unknown_val = known_val / math.tan(rad)
        check_angle = math.degrees(math.atan(known_val / unknown_val))
        ratio, calc = "tan", f"x = {known_val} ÷ tan({angle_deg}°)"
        known_role, unknown_role = "opp", "adj"
    elif shape == "adj_hyp":
        unknown_val = known_val / math.cos(rad)
        check_angle = math.degrees(math.acos(known_val / unknown_val))
        ratio, calc = "cos", f"x = {known_val} ÷ cos({angle_deg}°)"
        known_role, unknown_role = "adj", "hyp"
    else:  # opp_hyp
        unknown_val = known_val / math.sin(rad)
        check_angle = math.degrees(math.asin(known_val / unknown_val))
        ratio, calc = "sin", f"x = {known_val} ÷ sin({angle_deg}°)"
        known_role, unknown_role = "opp", "hyp"

    # Independent verification: invert the computed side back to the original angle
    # using the inverse trig function - a different computation path than the one
    # used to derive the side - and check it reproduces angle_deg.
    if abs(check_angle - angle_deg) > 1e-6:
        raise ValueError("modelled example trig_side verification failed: angle does not invert cleanly")

    rounded = _round_sf(unknown_val, sig_figs)
    labels = {"adj": None, "opp": None, "hyp": None}
    labels[known_role] = f"{known_val} cm"
    labels[unknown_role] = "x cm"

    # Whether this shape is "unknown = known x ratio" (no rearranging) or
    # "unknown = known / ratio" (division, i.e. rearranging the ratio first).
    is_multiplication = shape in ("hyp_opp", "hyp_adj", "adj_opp")

    teaching_steps = [
        f"Label the triangle's sides relative to the angle {angle_deg}°: the "
        f"{_ROLE_NAME[known_role]} is given as {known_val} cm, and we want the "
        f"{_ROLE_NAME[unknown_role]}, labelled x.",
        f"SOH CAH TOA tells us which ratio links the {_ROLE_NAME[known_role]} and the "
        f"{_ROLE_NAME[unknown_role]}: here that's {ratio} "
        f"({'sin = opp/hyp' if ratio == 'sin' else 'cos = adj/hyp' if ratio == 'cos' else 'tan = opp/adj'}).",
        (
            f"Since the {_ROLE_NAME[known_role]} is the one being multiplied in that ratio, "
            f"we can go straight to x = {known_val} × {ratio}({angle_deg}°) without any rearranging."
            if is_multiplication else
            f"The {_ROLE_NAME[known_role]} isn't in the position the ratio naturally gives us, "
            f"so we rearrange first, giving x = {known_val} ÷ {ratio}({angle_deg}°)."
        ),
        f"Evaluating gives x ≈ {_fmt_dec(rounded)}, which we round to {sig_figs} significant "
        "figures as the question asks - always check whether the question wants significant "
        "figures or decimal places, since they aren't always the same thing.",
    ]
    worked_calculation = [
        calc,
        f"x = {_fmt_dec(rounded)} cm (to {sig_figs} s.f.)",
    ]
    return ModelledExample(
        topic_id=topic_id,
        tier=tier,
        prompt=f"In the right-angled triangle shown, find the length of x, correct to {sig_figs} significant figures.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{_fmt_dec(rounded)} cm",
        diagram=DiagramSpec(
            kind="trig_triangle",
            params={
                "adjacent_label": labels["adj"],
                "opposite_label": labels["opp"],
                "hyp_label": labels["hyp"],
                "angle_label": f"{angle_deg}°",
            },
        ),
    )


def generate_missing_side_foundation(tier: Tier, rng: random.Random) -> Question:
    return _trig_side_question(
        rng,
        angle_lo=20, angle_hi=70, side_lo=5, side_hi=20, sig_figs=3,
        shapes=_SIDE_SHAPES_NO_REARRANGE,
        topic_id="trig_missing_side_foundation",
        tier=Tier.FOUNDATION,
    )


def generate_missing_side_higher(tier: Tier, rng: random.Random) -> Question:
    return _trig_side_question(
        rng,
        angle_lo=5, angle_hi=85, side_lo=4, side_hi=40, sig_figs=3,
        shapes=_SIDE_SHAPES_ALL,
        topic_id="trig_missing_side_higher",
        tier=Tier.HIGHER,
    )


def generate_modelled_example_missing_side_foundation(tier: Tier, rng: random.Random) -> ModelledExample:
    return _trig_side_modelled_example(
        rng,
        angle_lo=20, angle_hi=70, side_lo=5, side_hi=20, sig_figs=3,
        shapes=_SIDE_SHAPES_NO_REARRANGE,
        topic_id="trig_missing_side_foundation",
        tier=Tier.FOUNDATION,
    )


def generate_modelled_example_missing_side_higher(tier: Tier, rng: random.Random) -> ModelledExample:
    return _trig_side_modelled_example(
        rng,
        angle_lo=5, angle_hi=85, side_lo=4, side_hi=40, sig_figs=3,
        shapes=_SIDE_SHAPES_ALL,
        topic_id="trig_missing_side_higher",
        tier=Tier.HIGHER,
    )


def _trig_angle_question(rng: random.Random, *, side_lo, side_hi, topic_id, tier) -> Question:
    shape = rng.choice(["opp_adj", "opp_hyp", "adj_hyp"])

    if shape == "opp_adj":
        opp, adj = rng.randint(side_lo, side_hi), rng.randint(side_lo, side_hi)
        angle = math.degrees(math.atan(opp / adj))
        check = adj * math.tan(math.radians(angle))
        if abs(check - opp) > 1e-6:
            raise ValueError("trig_angle verification failed: opp_adj")
        ratio, ratio_arg = "tan", f"{opp} ÷ {adj}"
        labels = {"opp": f"{opp} cm", "adj": f"{adj} cm", "hyp": None}
    elif shape == "opp_hyp":
        opp = rng.randint(side_lo, side_hi - 1)
        hyp = rng.randint(opp + 1, side_hi)
        angle = math.degrees(math.asin(opp / hyp))
        check = hyp * math.sin(math.radians(angle))
        if abs(check - opp) > 1e-6:
            raise ValueError("trig_angle verification failed: opp_hyp")
        ratio, ratio_arg = "sin", f"{opp} ÷ {hyp}"
        labels = {"opp": f"{opp} cm", "adj": None, "hyp": f"{hyp} cm"}
    else:  # adj_hyp
        adj = rng.randint(side_lo, side_hi - 1)
        hyp = rng.randint(adj + 1, side_hi)
        angle = math.degrees(math.acos(adj / hyp))
        check = hyp * math.cos(math.radians(angle))
        if abs(check - adj) > 1e-6:
            raise ValueError("trig_angle verification failed: adj_hyp")
        ratio, ratio_arg = "cos", f"{adj} ÷ {hyp}"
        labels = {"opp": None, "adj": f"{adj} cm", "hyp": f"{hyp} cm"}

    rounded = _round_dp(angle, 1)
    steps = [
        f"Use {ratio}, since we know two of the three sides.",
        f"{ratio}(x) = {ratio_arg}",
        f"x = {ratio}^-1({ratio_arg}) = {_fmt_dec(rounded)}° (1 d.p.)",
    ]
    return Question(
        topic_id=topic_id,
        tier=tier,
        prompt="In the right-angled triangle shown, find the angle x, correct to 1 decimal place.",
        solution_steps=tuple(steps),
        final_answer=f"{_fmt_dec(rounded)}°",
        dedup_key=f"trig_angle:{shape}:{ratio_arg}",
        diagram=DiagramSpec(
            kind="trig_triangle",
            params={
                "adjacent_label": labels["adj"],
                "opposite_label": labels["opp"],
                "hyp_label": labels["hyp"],
                "angle_label": "x°",
            },
        ),
    )


def generate_missing_angle_foundation(tier: Tier, rng: random.Random) -> Question:
    return _trig_angle_question(
        rng, side_lo=5, side_hi=20,
        topic_id="trig_missing_angle_foundation", tier=Tier.FOUNDATION,
    )


def generate_missing_angle_higher(tier: Tier, rng: random.Random) -> Question:
    return _trig_angle_question(
        rng, side_lo=4, side_hi=40,
        topic_id="trig_missing_angle_higher", tier=Tier.HIGHER,
    )


def _trig_angle_modelled_example(rng: random.Random, *, side_lo, side_hi, topic_id, tier) -> ModelledExample:
    shape = rng.choice(["opp_adj", "opp_hyp", "adj_hyp"])

    if shape == "opp_adj":
        opp, adj = rng.randint(side_lo, side_hi), rng.randint(side_lo, side_hi)
        angle = math.degrees(math.atan(opp / adj))
        check = adj * math.tan(math.radians(angle))
        if abs(check - opp) > 1e-6:
            raise ValueError("modelled example trig_angle verification failed: opp_adj")
        ratio, ratio_arg = "tan", f"{opp} ÷ {adj}"
        known_pair = "opposite and adjacent"
        labels = {"opp": f"{opp} cm", "adj": f"{adj} cm", "hyp": None}
    elif shape == "opp_hyp":
        opp = rng.randint(side_lo, side_hi - 1)
        hyp = rng.randint(opp + 1, side_hi)
        angle = math.degrees(math.asin(opp / hyp))
        check = hyp * math.sin(math.radians(angle))
        if abs(check - opp) > 1e-6:
            raise ValueError("modelled example trig_angle verification failed: opp_hyp")
        ratio, ratio_arg = "sin", f"{opp} ÷ {hyp}"
        known_pair = "opposite and hypotenuse"
        labels = {"opp": f"{opp} cm", "adj": None, "hyp": f"{hyp} cm"}
    else:  # adj_hyp
        adj = rng.randint(side_lo, side_hi - 1)
        hyp = rng.randint(adj + 1, side_hi)
        angle = math.degrees(math.acos(adj / hyp))
        check = hyp * math.cos(math.radians(angle))
        if abs(check - adj) > 1e-6:
            raise ValueError("modelled example trig_angle verification failed: adj_hyp")
        ratio, ratio_arg = "cos", f"{adj} ÷ {hyp}"
        known_pair = "adjacent and hypotenuse"
        labels = {"opp": None, "adj": f"{adj} cm", "hyp": f"{hyp} cm"}

    rounded = _round_dp(angle, 1)
    # Independent verification already happened above: for each shape, the forward
    # ratio (a different direction of computation than the inverse-trig step used to
    # find the angle) was substituted back in using the unrounded angle and checked
    # to reproduce the known side - mirroring the real generator's converse check.

    teaching_steps = [
        f"This time we're given two sides instead of an angle, so we work backwards: we know "
        f"the {known_pair}, and we want the angle x itself.",
        f"SOH CAH TOA tells us which ratio uses those two sides - here that's {ratio}, since "
        f"{ratio}(x) = {ratio_arg}.",
        f"To undo {ratio} and get x on its own, apply the inverse function {ratio}^-1 to both "
        f"sides: x = {ratio}^-1({ratio_arg}).",
        f"Evaluating gives x ≈ {_fmt_dec(rounded)}° (1 d.p.). As a check, substituting this "
        f"angle back into {ratio}(x) should reproduce {ratio_arg} - and it does, confirming "
        "the answer.",
    ]
    worked_calculation = [
        f"{ratio}(x) = {ratio_arg}",
        f"x = {ratio}^-1({ratio_arg})",
        f"x = {_fmt_dec(rounded)}° (1 d.p.)",
    ]
    return ModelledExample(
        topic_id=topic_id,
        tier=tier,
        prompt="In the right-angled triangle shown, find the angle x, correct to 1 decimal place.",
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{_fmt_dec(rounded)}°",
        diagram=DiagramSpec(
            kind="trig_triangle",
            params={
                "adjacent_label": labels["adj"],
                "opposite_label": labels["opp"],
                "hyp_label": labels["hyp"],
                "angle_label": "x°",
            },
        ),
    )


def generate_modelled_example_missing_angle_foundation(tier: Tier, rng: random.Random) -> ModelledExample:
    return _trig_angle_modelled_example(
        rng, side_lo=5, side_hi=20,
        topic_id="trig_missing_angle_foundation", tier=Tier.FOUNDATION,
    )


def generate_modelled_example_missing_angle_higher(tier: Tier, rng: random.Random) -> ModelledExample:
    return _trig_angle_modelled_example(
        rng, side_lo=4, side_hi=40,
        topic_id="trig_missing_angle_higher", tier=Tier.HIGHER,
    )


def generate_mixed(tier: Tier, rng: random.Random) -> Question:
    if rng.random() < 0.5:
        q = _trig_side_question(
            rng, angle_lo=5, angle_hi=85, side_lo=4, side_hi=40, sig_figs=3,
            shapes=_SIDE_SHAPES_ALL, topic_id="trig_mixed", tier=Tier.HIGHER,
        )
    else:
        q = _trig_angle_question(rng, side_lo=4, side_hi=40, topic_id="trig_mixed", tier=Tier.HIGHER)
    return q


def generate_modelled_example_mixed(tier: Tier, rng: random.Random) -> ModelledExample:
    if rng.random() < 0.5:
        example = _trig_side_modelled_example(
            rng, angle_lo=5, angle_hi=85, side_lo=4, side_hi=40, sig_figs=3,
            shapes=_SIDE_SHAPES_ALL, topic_id="trig_mixed", tier=Tier.HIGHER,
        )
    else:
        example = _trig_angle_modelled_example(rng, side_lo=4, side_hi=40, topic_id="trig_mixed", tier=Tier.HIGHER)
    return example


TOPIC_MISSING_SIDE_FOUNDATION = TopicDefinition(
    id="trig_missing_side_foundation",
    display_name="Missing Sides",
    description="Use SOH CAH TOA to find a missing side of a right-angled triangle.",
    generate=generate_missing_side_foundation,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_missing_side_foundation,
)

TOPIC_MISSING_SIDE_HIGHER = TopicDefinition(
    id="trig_missing_side_higher",
    display_name="Missing Sides",
    description="Use SOH CAH TOA to find a missing side of a right-angled triangle, including rearranging.",
    generate=generate_missing_side_higher,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_missing_side_higher,
)

TOPIC_MISSING_ANGLE_FOUNDATION = TopicDefinition(
    id="trig_missing_angle_foundation",
    display_name="Missing Angles",
    description="Use inverse trigonometric ratios to find a missing angle of a right-angled triangle.",
    generate=generate_missing_angle_foundation,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_missing_angle_foundation,
)

TOPIC_MISSING_ANGLE_HIGHER = TopicDefinition(
    id="trig_missing_angle_higher",
    display_name="Missing Angles",
    description="Use inverse trigonometric ratios to find a missing angle of a right-angled triangle.",
    generate=generate_missing_angle_higher,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_missing_angle_higher,
)

TOPIC_MIXED = TopicDefinition(
    id="trig_mixed",
    display_name="Mixed Sides and Angles",
    description="A mix of missing-side and missing-angle right-angled triangle trigonometry questions.",
    generate=generate_mixed,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.HIGHER,
    generate_modelled_example=generate_modelled_example_mixed,
)
