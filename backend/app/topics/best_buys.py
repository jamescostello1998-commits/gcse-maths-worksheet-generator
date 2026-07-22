import random
from decimal import ROUND_HALF_UP, Decimal
from typing import NamedTuple

from app.core.models import ModelledExample, Question, Tier
from app.topics.base import TopicDefinition

SECTION = "ratio_proportion"
GROUP = "Best Buys"

# Each entry: (product noun, unit of measure, qty lower bound, qty upper bound, qty step).
_PRODUCTS = [
    ("shampoo", "ml", 100, 500, 50),
    ("orange juice", "ml", 250, 1500, 250),
    ("washing-up liquid", "ml", 200, 900, 50),
    ("breakfast cereal", "g", 200, 750, 50),
    ("ground coffee", "g", 100, 400, 25),
    ("washing powder", "g", 500, 2000, 100),
    ("pasta", "g", 250, 1000, 50),
    ("rice", "g", 250, 1000, 50),
]

_OPTION_LABELS = ["A", "B", "C"]

# A pool of "pence per 100 units" rates, spaced 4 pence apart, sampled without
# replacement so every option in a single question has a clearly distinct
# underlying rate - this keeps the winner unambiguous even after the sticker
# price is rounded to the nearest whole penny (see below).
_PER_100_POOL = list(range(40, 320, 4))


class _Option(NamedTuple):
    label: str
    qty: int
    price_pence: int
    unit_price: Decimal  # pence per 100 units, rounded to 2 d.p. - for display only


def _build_scenario(rng: random.Random) -> tuple:
    """Pick a product and a set of 2-3 differently-sized/priced options for it.

    Returns (noun, unit, options, winner_idx). The `unit_price` field on each
    option is a ROUNDED display value (what a student would actually compute
    and write down); the winner is determined and independently verified
    using the raw, un-rounded integers below - see generate_best_buys.
    """
    noun, unit, qty_lo, qty_hi, qty_step = rng.choice(_PRODUCTS)
    num_options = rng.choices([2, 3], weights=[70, 30])[0]
    per_100_rates = rng.sample(_PER_100_POOL, num_options)

    # Sample distinct quantities without replacement so a "different sizes"
    # scenario never degenerates into two options of the identical size.
    qty_choices = list(range(qty_lo, qty_hi + 1, qty_step))
    qtys = rng.sample(qty_choices, num_options)

    options = []
    for label, per_100, qty in zip(_OPTION_LABELS, per_100_rates, qtys):
        # Realistic sticker prices are always a whole number of pence, so the
        # "ideal" rate-based price is rounded to the nearest penny.
        exact_pence = Decimal(per_100) * Decimal(qty) / Decimal(100)
        price_pence = int(exact_pence.quantize(Decimal(1), rounding=ROUND_HALF_UP))
        unit_price = (Decimal(price_pence) * 100 / Decimal(qty)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        options.append(_Option(label, qty, price_pence, unit_price))

    # Determine the best value via the ROUNDED per-unit prices - this is the
    # method a student actually uses (compute a unit price for each option,
    # then compare them).
    winner_idx_by_unit_price = min(range(num_options), key=lambda i: options[i].unit_price)

    # Independent verification: cross-multiply the RAW integer price and
    # quantity for every pair directly (price_i x qty_j vs price_j x qty_i) -
    # a genuinely different method that never goes through any rounded
    # per-unit price at all.
    def _cheaper(i: int, j: int) -> bool:
        return options[i].price_pence * options[j].qty < options[j].price_pence * options[i].qty

    winner_idx_cross_mult = 0
    for i in range(1, num_options):
        if _cheaper(i, winner_idx_cross_mult):
            winner_idx_cross_mult = i

    if winner_idx_cross_mult != winner_idx_by_unit_price:
        raise ValueError("best_buys: unit-price and cross-multiplication methods disagree")

    return noun, unit, options, winner_idx_by_unit_price


def _fmt_price(pence: int) -> str:
    pounds, rem = divmod(pence, 100)
    return f"£{pounds}.{rem:02d}"


def _fmt_unit_price(unit_price: Decimal, unit: str) -> str:
    return f"{unit_price}p per 100{unit}"


def generate_best_buys(tier: Tier, rng: random.Random) -> Question:
    noun, unit, options, winner_idx = _build_scenario(rng)
    winner = options[winner_idx]

    option_lines = "; ".join(
        f"{o.label}: {_fmt_price(o.price_pence)} for {o.qty}{unit}" for o in options
    )
    steps = [f"Work out the price per 100{unit} for each option:"]
    for o in options:
        steps.append(f"{o.label}: {_fmt_price(o.price_pence)} ÷ {o.qty} × 100 = {_fmt_unit_price(o.unit_price, unit)}")
    steps.append(
        f"The lowest price per 100{unit} is {winner.label} at "
        f"{_fmt_unit_price(winner.unit_price, unit)}, so {winner.label} is the best value."
    )

    return Question(
        topic_id="best_buys",
        tier=Tier.FOUNDATION,
        prompt=(
            f"A shop sells {noun} in different sizes: {option_lines}. "
            "Which option is the better value for money? Show your working."
        ),
        solution_steps=tuple(steps),
        final_answer=f"{winner.label} ({_fmt_price(winner.price_pence)} for {winner.qty}{unit})",
        dedup_key=(
            f"bb:{noun}:{'|'.join(f'{o.label}:{o.qty}:{o.price_pence}' for o in options)}"
        ),
    )


def generate_modelled_example_best_buys(tier: Tier, rng: random.Random) -> ModelledExample:
    noun, unit, options, winner_idx = _build_scenario(rng)
    winner = options[winner_idx]

    option_lines = "; ".join(
        f"{o.label}: {_fmt_price(o.price_pence)} for {o.qty}{unit}" for o in options
    )
    prompt = (
        f"A shop sells {noun} in different sizes: {option_lines}. "
        "Which option is the better value for money? Show your working."
    )

    teaching_steps = [
        "Two options can't be compared directly just by looking at their prices, because they're "
        "different SIZES too - a bigger pack costing more isn't automatically worse value. Instead, "
        f"we need to work out a fair 'per-unit' price for each one, such as the price per 100{unit}.",
    ]
    for o in options:
        teaching_steps.append(
            f"For {o.label}: divide the price by the quantity, then scale up to 100{unit}: "
            f"{_fmt_price(o.price_pence)} ÷ {o.qty} × 100 = {_fmt_unit_price(o.unit_price, unit)}."
        )
    teaching_steps.append(
        f"Now the options are on a level playing field - whichever has the LOWEST price per "
        f"100{unit} is the better value. Here, {winner.label} has the lowest at "
        f"{_fmt_unit_price(winner.unit_price, unit)}, so {winner.label} is the best value."
    )
    teaching_steps.append(
        "As an independent check, comparing the options by cross-multiplying the raw price and "
        "quantity directly (rather than trusting the rounded per-unit prices above) confirms the "
        f"same option, {winner.label}, comes out cheapest."
    )

    worked_calculation = [f"Price per 100{unit}:"]
    for o in options:
        worked_calculation.append(f"{o.label}: {_fmt_price(o.price_pence)} ÷ {o.qty} × 100 = {_fmt_unit_price(o.unit_price, unit)}")
    worked_calculation.append(f"Best value: {winner.label}")

    return ModelledExample(
        topic_id="best_buys",
        tier=Tier.FOUNDATION,
        prompt=prompt,
        worked_calculation=tuple(worked_calculation),
        teaching_steps=tuple(teaching_steps),
        final_answer=f"{winner.label} ({_fmt_price(winner.price_pence)} for {winner.qty}{unit})",
    )


TOPIC_BEST_BUYS = TopicDefinition(
    id="best_buys",
    display_name="Best Buys",
    description="Compare differently-sized/priced options of the same product to find the best value for money.",
    generate=generate_best_buys,
    section=SECTION,
    group=GROUP,
    fixed_tier=Tier.FOUNDATION,
    generate_modelled_example=generate_modelled_example_best_buys,
)
