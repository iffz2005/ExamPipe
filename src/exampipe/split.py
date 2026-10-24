"""Group the rows of one paper by sub-section.

Routing rule: the sub-section LABEL decides where a row goes (looked up through
the config's aliases). A row whose label is unknown is kept in ``unmapped``
instead of being dropped, so nothing disappears silently.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .config import Course
from .schema import Row

# (section key, sub-section serial), e.g. ("MATH", 1)
Key = tuple[str, int]


@dataclass
class SplitResult:
    by_subsection: dict[Key, list[Row]] = field(default_factory=dict)
    unmapped: list[Row] = field(default_factory=list)


def split_rows(rows: list[Row], course: Course) -> SplitResult:
    result = SplitResult()
    for row in rows:
        hit = course.resolve(row.sub_section)
        if hit is None:
            result.unmapped.append(row)
            continue
        section, sub = hit
        result.by_subsection.setdefault((section.key, sub.serial), []).append(row)
    return result
