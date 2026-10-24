"""One test per rule: start from a valid row, break exactly one thing."""

import pytest

from exampipe.validate import count_sentences, validate_all, validate_paper, validate_row
from exampipe.sample import clean_rows


def codes(issues):
    return {i.code for i in issues}


def test_valid_row_has_no_issues(course, row):
    assert validate_row(row, course) == []


def test_whole_clean_paper_has_no_issues(course):
    assert validate_all(clean_rows(), course) == []


# ---- sections and sub-sections ---------------------------------------------------


def test_unknown_section(course, row):
    row.section = "Astrology"
    assert "SECTION_UNKNOWN" in codes(validate_row(row, course))


def test_unknown_subsection_suggests_a_fix(course, row):
    row.sub_section = "Percentge"
    issue = next(i for i in validate_row(row, course) if i.code == "SUBSECTION_UNKNOWN")
    assert "Percentage" in issue.message


def test_subsection_from_another_section(course, row):
    row.sub_section = "Geography"
    assert "SECTION_MISMATCH" in codes(validate_row(row, course))


def test_alias_with_odd_dash_and_case_still_resolves(course, row):
    row.sub_section = "CODING–DECODING"     # alias of a different section; only mismatch expected
    found = codes(validate_row(row, course))
    assert "SUBSECTION_UNKNOWN" not in found and "SECTION_MISMATCH" in found


# ---- options -----------------------------------------------------------------------


def test_wrong_option_count(course, row):
    row.options = row.options[:3]
    assert "OPTION_COUNT" in codes(validate_row(row, course))


def test_duplicate_options(course, row):
    row.options[2] = row.options[0]
    assert "OPTION_DUPLICATE" in codes(validate_row(row, course))


@pytest.mark.parametrize("prefix", ["1. ", "A) ", "(b) ", "c. "])
def test_option_prefix(course, row, prefix):
    row.options[0] = prefix + row.options[0]
    assert "OPTION_PREFIX" in codes(validate_row(row, course))


def test_empty_option(course, row):
    row.options[1] = "  "
    assert "OPTION_EMPTY" in codes(validate_row(row, course))


# ---- answer and difficulty -------------------------------------------------------------


@pytest.mark.parametrize("answer", ["1", "2", "3", "4", "UNCERTAIN"])
def test_allowed_answers(course, row, answer):
    row.correct_answer = answer
    assert "ANSWER_INVALID" not in codes(validate_row(row, course))


@pytest.mark.parametrize("answer", ["0", "5", "uncertain", "A", ""])
def test_invalid_answers(course, row, answer):
    row.correct_answer = answer
    assert "ANSWER_INVALID" in codes(validate_row(row, course))


def test_difficulty(course, row):
    row.difficulty = "easy"          # case-insensitive match is fine
    assert "DIFFICULTY_INVALID" not in codes(validate_row(row, course))
    row.difficulty = "Impossible"
    assert "DIFFICULTY_INVALID" in codes(validate_row(row, course))


# ---- katex is checked in every field ------------------------------------------------------


@pytest.mark.parametrize("field", ["question", "explanation"])
def test_katex_checked_in_text_fields(course, row, field):
    setattr(row, field, "broken $ math")
    assert "KATEX_UNBALANCED" in codes(validate_row(row, course))


def test_katex_checked_in_options(course, row):
    row.options[0] = "$ 20$"
    assert "KATEX_SPACE" in codes(validate_row(row, course))


# ---- explanation ----------------------------------------------------------------------------


@pytest.mark.parametrize("text", ["Option 2 is correct.", "The answer is option (b).", "Because OPTION 4 fits."])
def test_explanation_must_not_reference_option_numbers(course, row, text):
    row.explanation = text + " More. Even more."
    assert "EXPL_OPTION_REF" in codes(validate_row(row, course))


def test_the_word_options_is_not_a_reference(course, row):
    row.explanation = "Look at all the options carefully. Only one is valid. This is it."
    assert "EXPL_OPTION_REF" not in codes(validate_row(row, course))


def test_sentence_count_is_a_warning(course, row):
    row.explanation = "Only one sentence."
    issue = next(i for i in validate_row(row, course) if i.code == "EXPL_SENTENCES")
    assert issue.severity == "warning"


def test_count_sentences_ignores_math_and_html():
    text = r"We compute $3.5\times2=7.0$. Then add one.<br><br>So <b>$8$</b> is the result."
    assert count_sentences(text) == 3


def test_image_placeholder_is_a_warning(course, row):
    row.question = "{{Image}} " + row.question
    issue = next(i for i in validate_row(row, course) if i.code == "IMAGE_PLACEHOLDER")
    assert issue.severity == "warning"


# ---- whole-paper numbering ----------------------------------------------------------------------


def test_missing_number(course):
    rows = [r for r in clean_rows() if r.no != 7]
    found = validate_paper(rows, course)
    assert "NUMBER_MISSING" in codes(found)
    assert "7" in next(i for i in found if i.code == "NUMBER_MISSING").message


def test_duplicate_number(course):
    rows = clean_rows()
    rows[5].no = 5
    assert "NUMBER_DUPLICATE" in codes(validate_paper(rows, course))


def test_number_out_of_range(course):
    rows = clean_rows()
    rows[-1].no = 31
    assert "NUMBER_OUT_OF_RANGE" in codes(validate_paper(rows, course))


def test_rows_out_of_order(course):
    rows = clean_rows()
    rows[3], rows[4] = rows[4], rows[3]
    assert "NUMBER_ORDER" in codes(validate_paper(rows, course))


def test_question_in_wrong_section_for_its_number(course):
    rows = clean_rows()
    rows[10].section = "Mathematics"     # Q11 belongs to Reasoning
    assert "NUMBER_SECTION_MISMATCH" in codes(validate_paper(rows, course))
