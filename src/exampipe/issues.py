"""The one data type every validator returns."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Issue:
    """A single problem found in the input.

    ``code`` is a stable machine-readable name (tests and dashboards key on it).
    ``severity`` is "error" (must fix) or "warning" (a human should look).
    ``row_no`` is the question number inside the paper; ``line`` is the line
    number in the source text file.
    """

    code: str
    message: str
    severity: str = "error"
    row_no: int | None = None
    line: int | None = None

    def format(self) -> str:
        where = []
        if self.row_no is not None:
            where.append(f"Q{self.row_no}")
        if self.line is not None:
            where.append(f"line {self.line}")
        loc = f" ({', '.join(where)})" if where else ""
        return f"[{self.severity.upper():7}]{loc} {self.code}: {self.message}"
