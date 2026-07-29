from app.practice_tests.mark_scheme import build_mark_scheme


def test_single_step_question_gets_two_marks():
    marks, points = build_mark_scheme(("Area = 6 x 5 = 30",), "30")
    assert marks == 2
    assert [p.code for p in points] == ["M1", "A1"]
    assert points[-1].description == "30 oe"


def test_multi_step_question_gets_one_method_mark_per_step_plus_accuracy():
    steps = ("Step 1", "Step 2", "Step 3")
    marks, points = build_mark_scheme(steps, "42")
    assert marks == 4
    assert [p.code for p in points] == ["M1", "M1", "M1", "A1"]
    assert [p.description for p in points[:3]] == list(steps)


def test_method_marks_are_capped_and_overflow_folds_into_the_last_one():
    steps = ("Step 1", "Step 2", "Step 3", "Step 4", "Step 5")
    marks, points = build_mark_scheme(steps, "1")
    assert marks == 5  # 4 method marks max + 1 accuracy mark
    assert [p.code for p in points] == ["M1", "M1", "M1", "M1", "A1"]
    assert [p.description for p in points[:3]] == ["Step 1", "Step 2", "Step 3"]
    assert points[3].description == "Step 4 Step 5"


def test_multiple_choice_style_answer_gets_a_single_b1_mark():
    marks, points = build_mark_scheme(("some working",), "B) 3/4")
    assert marks == 1
    assert len(points) == 1
    assert points[0].code == "B1"
    assert "B) 3/4" in points[0].description


def test_no_solution_steps_still_produces_a_valid_scheme():
    marks, points = build_mark_scheme((), "7")
    assert marks == 2
    assert [p.code for p in points] == ["M1", "A1"]


def test_every_mark_points_marks_sum_to_the_total():
    for steps, answer in [
        (("a",), "1"),
        (("a", "b"), "2"),
        (("a", "b", "c", "d", "e", "f"), "3"),
        (("a",), "C) 1/2"),
    ]:
        marks, points = build_mark_scheme(steps, answer)
        assert sum(p.marks for p in points) == marks
