"""Validation rules.

Two levels:
  * validate_row    : rules that look at ONE question in isolation
  * validate_paper  : rules that look at the WHOLE paper (numbering, ranges)

Every function returns a list of Issues and never raises on bad data, so a
single run reports everything that is wrong.
"""

from __future__ import annotations

import re

from .config import Course
from .issues import Issue
from .katex import check_katex, katex_spans
from .normalize import normalize_label
from .schema import Row

# "1. text", "A) text", "(b) text": an option label that should not be there.
_OPTION_PREFIX = re.compile(r"^\(?[1-4a-dA-D][\).]\s")
# "option 2", "Option (b)": explanations must describe the answer, not point at a slot.
_OPTION_REFERENCE = re.compile(r"\boption\s*\(?[1-4a-d]\)?(?![a-z])", re.IGNORECASE)
_HTML_TAG = re.compile(r"<[^>]+>")
_SENTENCE_END = re.compile(r"(?<=[.!?])\s+")


def _plain_text(text: str) -> str:
    """Strip HTML tags and replace each math span with a placeholder letter.

    Needed before counting sentences: "$5\\times5=25$." must not be split
    on any dot that lives inside the formula.
    """
    spans = katex_spans(text)
    if spans:
        for span in spans:
            text = text.replace(f"${span}$", "M", 1)
    return _HTML_TAG.sub(" ", text)


def count_sentences(text: str) -> int:
    plain = " ".join(_plain_text(text).split())
    return len([s for s in _SENTENCE_END.split(plain) if s.strip()])


def validate_row(row: Row, course: Course) -> list[Issue]:
    issues: list[Issue] = []

    def add(code: str, message: str, severity: str = "error") -> None:
        issues.append(Issue(code, message, severity, row_no=row.no, line=row.line))

    # -- required text ------------------------------------------------------
    if not row.question.strip():
        add("EMPTY_QUESTION", "question text is empty")
    if not row.explanation.strip():
        add("EMPTY_EXPLANATION", "explanation is empty")

    # -- section and sub-section -------------------------------------------
    section = course.section_by_name(row.section)
    if section is None:
        known = ", ".join(s.name for s in course.sections)
        add("SECTION_UNKNOWN", f"section {row.section!r} is not one of: {known}")

    hit = course.resolve(row.sub_section)
    if hit is None:
        hint = course.suggest(row.sub_section)
        tip = f" Did you mean {hint!r}?" if hint else ""
        add("SUBSECTION_UNKNOWN", f"sub-section {row.sub_section!r} is not in the config.{tip}")
    elif section is not None and hit[0].key != section.key:
        add(
            "SECTION_MISMATCH",
            f"sub-section {row.sub_section!r} belongs to {hit[0].name!r}, not {section.name!r}",
        )

    # -- options ---------------------------------------------------------------
    if len(row.options) != 4:
        add("OPTION_COUNT", f"expected 4 options, found {len(row.options)}")
    seen: set[str] = set()
    for idx, option in enumerate(row.options, start=1):
        if not option.strip():
            add("OPTION_EMPTY", f"option {idx} is empty")
            continue
        if _OPTION_PREFIX.match(option):
            add("OPTION_PREFIX", f"option {idx} starts with a label: '{option[:20]}'")
        key = normalize_label(option)
        if key in seen:
            add("OPTION_DUPLICATE", f"option {idx} repeats an earlier option: '{option[:30]}'")
        seen.add(key)

    # -- answer and difficulty --------------------------------------------------
    if row.correct_answer not in course.answers_allowed:
        allowed = "/".join(course.answers_allowed)
        add("ANSWER_INVALID", f"correct answer {row.correct_answer!r} must be one of {allowed}")
    allowed_difficulties = {normalize_label(d) for d in course.difficulties}
    if normalize_label(row.difficulty) not in allowed_difficulties:
        add("DIFFICULTY_INVALID", f"difficulty {row.difficulty!r} must be one of {course.difficulties}")

    # -- KaTeX in every text field ---------------------------------------------
    fields = {"question": row.question, "explanation": row.explanation}
    for idx, option in enumerate(row.options, start=1):
        fields[f"option {idx}"] = option
    for name, text in fields.items():
        for code, message in check_katex(text):
            add(code, f"in {name}: {message}")

    # -- explanation quality ----------------------------------------------------
    if _OPTION_REFERENCE.search(_plain_text(row.explanation)):
        add("EXPL_OPTION_REF", "explanation refers to an option number instead of the answer's content")
    n = count_sentences(row.explanation)
    rule = course.explanation
    if row.explanation.strip() and not (rule.min_sentences <= n <= rule.max_sentences):
        add(
            "EXPL_SENTENCES",
            f"explanation has {n} sentence(s); expected {rule.min_sentences} to {rule.max_sentences}",
            severity="warning",
        )

    # -- images need a human ----------------------------------------------------
    if "{{image" in (row.question + " ".join(row.options)).lower():
        add("IMAGE_PLACEHOLDER", "contains an {{Image}} placeholder; needs a manual image check", "warning")

    return issues


def validate_paper(rows: list[Row], course: Course) -> list[Issue]:
    """Numbering rules for the whole paper."""
    issues: list[Issue] = []
    total = course.total_questions

    numbers = [r.no for r in rows]
    seen: set[int] = set()
    for row in rows:
        if row.no in seen:
            issues.append(Issue("NUMBER_DUPLICATE", f"question number {row.no} appears more than once",
                                row_no=row.no, line=row.line))
        seen.add(row.no)
        if not 1 <= row.no <= total:
            issues.append(Issue("NUMBER_OUT_OF_RANGE", f"question number {row.no} is outside 1..{total}",
                                row_no=row.no, line=row.line))

    for prev, row in zip(rows, rows[1:]):
        if row.no < prev.no:
            issues.append(Issue("NUMBER_ORDER", f"question {row.no} comes after question {prev.no}",
                                row_no=row.no, line=row.line))

    missing = [n for n in range(1, total + 1) if n not in set(numbers)]
    if missing:
        shown = ", ".join(map(str, missing[:10])) + (" ..." if len(missing) > 10 else "")
        issues.append(Issue("NUMBER_MISSING", f"{len(missing)} question number(s) missing: {shown}"))

    # Each number belongs to exactly one section according to the config.
    for row in rows:
        expected = course.section_for_number(row.no)
        actual = course.section_by_name(row.section)
        if expected and actual and expected.key != actual.key:
            issues.append(
                Issue(
                    "NUMBER_SECTION_MISMATCH",
                    f"question {row.no} should be in {expected.name!r} but is labelled {row.section!r}",
                    row_no=row.no,
                    line=row.line,
                )
            )
    return issues


def validate_all(rows: list[Row], course: Course) -> list[Issue]:
    issues: list[Issue] = []
    for row in rows:
        issues.extend(validate_row(row, course))
    issues.extend(validate_paper(rows, course))
    return issues
