import pytest

from exampipe.io import parse_pipe_text
from exampipe.katex import check_katex
from exampipe.sample import clean_rows, clean_text

# ---- parser -----------------------------------------------------------------


def test_clean_sample_round_trips():
    parsed = parse_pipe_text(clean_text())
    assert parsed.issues == []
    assert [r.model_dump(exclude={"line"}) for r in parsed.rows] == [
        r.model_dump(exclude={"line"}) for r in clean_rows()
    ]


def test_parser_skips_fences_blank_lines_and_header():
    text = "```\n\nNo | Section | Sub-Section | Question | Answer 1 | Answer 2 | Answer 3 | Answer 4 | Correct Answer | Explanation | Difficulty\n" \
           + clean_rows()[0].to_pipe_line() + "\n```\n"
    parsed = parse_pipe_text(text)
    assert len(parsed.rows) == 1 and parsed.issues == []


def test_wrong_column_count_becomes_an_issue_not_an_exception():
    parsed = parse_pipe_text("1 | Mathematics | Percentage | only four columns")
    assert parsed.rows == []
    assert [i.code for i in parsed.issues] == ["PARSE_COLUMNS"]
    assert parsed.issues[0].line == 1


def test_non_numeric_question_number():
    line = clean_rows()[0].to_pipe_line().replace("1 | ", "one | ", 1)
    assert [i.code for i in parse_pipe_text(line).issues] == ["PARSE_NUMBER"]


# ---- katex ------------------------------------------------------------------


@pytest.mark.parametrize(
    "text",
    [
        "plain text, no math",
        r"What is $20\%$ of $150$?",
        r"$\frac{1}{2}$ and $x^{2}$",
        r"Price is \$5 (escaped dollar, not math)",
        r"$A \rightarrow D(+3)$",                   # inner spaces are fine
        r"$\text{Rs. }500$",
    ],
)
def test_valid_katex_has_no_problems(text):
    assert check_katex(text) == []


@pytest.mark.parametrize(
    "text, code",
    [
        ("an odd $ delimiter", "KATEX_UNBALANCED"),
        ("$ x+1$", "KATEX_SPACE"),
        ("$x+1 $", "KATEX_SPACE"),
        ("$x<br>y$", "KATEX_BR"),
        (r"$\frac{1}{2$", "KATEX_BRACES"),
        (r"$x}$", "KATEX_BRACES"),
        ("$$", "KATEX_EMPTY"),
    ],
)
def test_katex_problems_are_detected(text, code):
    assert code in {c for c, _ in check_katex(text)}
