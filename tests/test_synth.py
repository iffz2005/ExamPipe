import re

import pytest

from exampipe.io import parse_pipe_text
from exampipe.synth import make_paper, paper_text
from exampipe.validate import validate_all


def test_same_seed_same_paper():
    assert paper_text(7) == paper_text(7)


def test_different_seeds_differ():
    assert paper_text(1) != paper_text(2)


@pytest.mark.parametrize("seed", range(60))
def test_every_seed_is_valid_with_no_warnings(course, seed):
    rows = make_paper(seed)
    assert len(rows) == 30
    assert validate_all(rows, course) == []


def test_text_round_trips_through_the_parser(course):
    parsed = parse_pipe_text(paper_text(5))
    assert parsed.issues == []
    assert [r.model_dump(exclude={"line"}) for r in parsed.rows] == \
           [r.model_dump(exclude={"line"}) for r in make_paper(5)]


def test_correct_option_text_matches_the_computed_answer():
    """Independent oracle: recompute simple-interest and percentage answers
    from the numbers in the question text and compare to the marked option."""
    checked = 0
    for seed in range(40):
        for r in make_paper(seed):
            marked = r.options[int(r.correct_answer) - 1]
            if r.sub_section == "Simple Interest" and r.question.startswith("What is the simple interest"):
                p, rate, years = (int(x) for x in re.findall(r"\$(?:\\text\{Rs\. \})?(\d+)(?:\\%)?\$", r.question))
                assert marked == r"$\text{Rs. }" + str(p * rate * years // 100) + "$"
                checked += 1
            if r.question.startswith("What is $") and r.sub_section == "Percentage":
                pct, n = (int(x) for x in re.findall(r"\$(\d+)(?:\\%)?\$", r.question))
                assert marked == "$" + str(pct * n // 100) + "$"
                checked += 1
    assert checked > 20


def test_work_together_answer_is_correct():
    for seed in range(40):
        for r in make_paper(seed):
            if r.question.startswith("A can finish a job"):
                x, y = (int(v) for v in re.findall(r"\$(\d+)\$", r.question))
                assert r.options[int(r.correct_answer) - 1] == f"${x * y // (x + y)}$"
                assert (x * y) % (x + y) == 0  # answer is a whole number of days


def test_options_are_distinct_in_every_question():
    for seed in range(60):
        for r in make_paper(seed):
            assert len(set(r.options)) == 4
