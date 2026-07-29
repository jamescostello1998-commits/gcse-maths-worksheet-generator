"""Derives an OCR-style mark breakdown (M1/A1/B1 marking points) from a
frozen question's own solution_steps/final_answer. Deliberately generic and
data-driven rather than hand-authored per topic - see CLAUDE.md's Practice
Tests entry for why. Calibrated against the real "Subject-Specific Marking
Instructions" read directly from actual OCR mark schemes spanning June 2017
to June 2024 (Foundation and Higher): M marks reward a correct method and
aren't lost for purely numerical errors; A marks require a preceding M mark;
B marks are independent of method marks. The `oe` (or equivalent) abbreviation
is still current throughout 2017-2024; `cao` ("correct answer only") was an
explicitly-defined abbreviation in the 2017/2019 schemes but is dropped from
the 2022/2024 ones in favour of plain accepted-answer wording - this module
follows the current (2022+) convention, not the retired one. Every M1's
description is the actual generated working line; the A1/B1's description is
the actual generated final_answer - nothing here is invented text unrelated
to the real question content.
"""

import re

from app.practice_tests.models import MarkPoint

# A final_answer like "B) 3/4" (this app's convention for multiple-choice
# "identify the correct one" questions - see e.g. fractions_equivalent's
# identify_equivalent branch) has no method to mark, so it gets a single
# independent B1 instead of the usual method-then-accuracy pattern.
_MC_ANSWER_RE = re.compile(r"^[A-D]\)")

_MAX_METHOD_MARKS = 4


def build_mark_scheme(solution_steps: tuple[str, ...], final_answer: str) -> tuple[int, tuple[MarkPoint, ...]]:
    if _MC_ANSWER_RE.match(final_answer):
        point = MarkPoint(code="B1", description=f"{final_answer} (selecting the correct option)", marks=1)
        return 1, (point,)

    steps = list(solution_steps) if solution_steps else ["correct method shown"]
    n_method = min(len(steps), _MAX_METHOD_MARKS)
    if len(steps) > n_method:
        # More steps than we're willing to award separate method marks for -
        # fold the overflow into the last method point's description rather
        # than silently dropping it.
        method_texts = steps[: n_method - 1] + [" ".join(steps[n_method - 1 :])]
    else:
        method_texts = steps[:n_method]

    method_points = tuple(MarkPoint(code="M1", description=text, marks=1) for text in method_texts)
    accuracy_point = MarkPoint(code="A1", description=f"{final_answer} oe", marks=1)

    marks = n_method + 1
    return marks, method_points + (accuracy_point,)
