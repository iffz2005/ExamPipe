"""Parsing the pipe-separated text that comes out of the extraction step."""

from __future__ import annotations

from dataclasses import dataclass, field

from .issues import Issue
from .schema import COLUMNS, SEPARATOR, Row


@dataclass
class ParseResult:
    rows: list[Row] = field(default_factory=list)
    issues: list[Issue] = field(default_factory=list)


def parse_pipe_text(text: str) -> ParseResult:
    """Parse text with one question per line and exactly 11 " | " separated columns.

    Tolerated: blank lines, a Markdown code fence (```), and a header row.
    A malformed line does not stop the run; it becomes an Issue and we move on.
    """
    result = ParseResult()
    expected = len(COLUMNS)

    for line_no, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("```"):
            continue

        parts = line.split(SEPARATOR)
        if len(parts) != expected:
            result.issues.append(
                Issue(
                    "PARSE_COLUMNS",
                    f"expected {expected} columns separated by ' | ', found {len(parts)}",
                    line=line_no,
                )
            )
            continue

        number = parts[0].strip()
        if number.lower() in {"no", "no."}:  # header row
            continue
        if not number.isdigit():
            result.issues.append(
                Issue("PARSE_NUMBER", f"question number {number!r} is not an integer", line=line_no)
            )
            continue

        result.rows.append(
            Row(
                no=int(number),
                section=parts[1].strip(),
                sub_section=parts[2].strip(),
                question=parts[3].strip(),
                options=[p.strip() for p in parts[4:8]],
                correct_answer=parts[8].strip(),
                explanation=parts[9].strip(),
                difficulty=parts[10].strip(),
                line=line_no,
            )
        )
    return result
