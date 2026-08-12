import math
import random

from app.core.models import Tier
from app.topics import coordinate_geometry

TRIALS = 300

GENERATORS = [
    (coordinate_geometry.generate_midpoint_of_segment, Tier.FOUNDATION),
    (coordinate_geometry.generate_distance_between_points, Tier.HIGHER),
]


def test_all_generators_produce_valid_verified_questions():
    for generate, tier in GENERATORS:
        rng = random.Random(520)
        for _ in range(TRIALS):
            q = generate(tier, rng)
            assert q.tier == tier
            assert q.prompt and q.solution_steps and q.final_answer


def test_dedup_keys_vary():
    for generate, tier in GENERATORS:
        rng = random.Random(521)
        keys = {generate(tier, rng).dedup_key for _ in range(150)}
        assert len(keys) > 80


def test_midpoint_answer_is_the_average_of_coordinates():
    """Re-parse the two given points from the prompt and confirm the stated
    midpoint really is their average - independent of the generator's build."""
    rng = random.Random(522)
    for _ in range(TRIALS):
        q = coordinate_geometry.generate_midpoint_of_segment(Tier.FOUNDATION, rng)
        # prompt: "...joining A(x1, y1) and B(x2, y2)."
        nums = q.prompt.replace("(", " ").replace(")", " ").replace(",", " ").split()
        coords = [int(t) for t in nums if t.lstrip("-").isdigit()]
        x1, y1, x2, y2 = coords
        mx, my = q.final_answer.strip("()").split(", ")
        assert float(mx) == (x1 + x2) / 2
        assert float(my) == (y1 + y2) / 2


def test_distance_answer_is_a_simplified_surd_matching_the_true_length():
    rng = random.Random(523)
    for _ in range(TRIALS):
        q = coordinate_geometry.generate_distance_between_points(Tier.HIGHER, rng)
        nums = q.prompt.replace("(", " ").replace(")", " ").replace(",", " ").split()
        coords = [int(t) for t in nums if t.lstrip("-").isdigit()]
        x1, y1, x2, y2 = coords
        answer = q.final_answer
        assert "√" in answer  # always a genuine surd (perfect squares are rejected)
        coeff_str, radicand = answer.split("√")
        coeff = 1 if coeff_str == "" else int(coeff_str)
        r = int(radicand)
        # value matches the true distance, and radicand is square-free
        assert abs(coeff * math.sqrt(r) - math.hypot(x2 - x1, y2 - y1)) < 1e-9
        for p in range(2, math.isqrt(r) + 1):
            assert r % (p * p) != 0


def test_modelled_examples_are_verified():
    modelled = [
        (coordinate_geometry.generate_modelled_example_midpoint_of_segment, Tier.FOUNDATION, "midpoint_of_segment_F"),
        (coordinate_geometry.generate_modelled_example_distance_between_points, Tier.HIGHER, "distance_between_points_H"),
    ]
    for generate, tier, topic_id in modelled:
        rng = random.Random(524)
        for _ in range(TRIALS):
            ex = generate(tier, rng)
            assert ex.topic_id == topic_id
            assert len(ex.worked_calculation) >= 2
            assert len(ex.teaching_steps) >= 3


def test_topic_metadata():
    for t in (coordinate_geometry.TOPIC_MIDPOINT_OF_SEGMENT, coordinate_geometry.TOPIC_DISTANCE_BETWEEN_POINTS):
        assert t.section == "algebra"
        assert t.group == "Coordinate Geometry"
        assert t.generate_modelled_example is not None
