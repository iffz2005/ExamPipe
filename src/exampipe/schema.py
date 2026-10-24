"""The shape of one question row.

Design note: this model only describes the *shape* of the data (field names
and types). It deliberately has no domain rules. The rules live in
validate.py and return a list of Issues, so one run can report EVERY problem
in a paper instead of stopping at the first exception.
"""

from __future__ import annotations

from pydantic import BaseModel

# Column order of the pipe-separated text format (11 columns).
COLUMNS = [
    "No",
    "Section",
    "Sub-Section",
    "Question",
    "Answer 1",
    "Answer 2",
    "Answer 3",
    "Answer 4",
    "Correct Answer",
    "Explanation",
    "Difficulty",
]
SEPARATOR = " | "  # exactly: space, pipe, space


class Row(BaseModel):
    no: int
    section: str
    sub_section: str
    question: str
    options: list[str]
    correct_answer: str
    explanation: str
    difficulty: str
    line: int | None = None  # source line, for error messages only

    def to_pipe_line(self) -> str:
        """Serialize back to the 11-column pipe-separated format."""
        parts = [
            str(self.no),
            self.section,
            self.sub_section,
            self.question,
            *self.options,
            self.correct_answer,
            self.explanation,
            self.difficulty,
        ]
        return SEPARATOR.join(parts)
