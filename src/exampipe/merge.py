"""Merge several papers into one question bank, keeping track of where each
question came from."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .config import Course
from .schema import Row
from .split import Key, split_rows


def natural_key(text: str) -> list:
    """Sort key where numbers inside text compare as numbers.

    Plain string sorting puts "P10" before "P2" (because "1" < "2"). Splitting
    the text into text / number / text / number ... pieces fixes that:
    "p2" -> ["p", 2, ""] sorts before "p10" -> ["p", 10, ""].
    """
    parts = re.split(r"(\d+)", text.casefold())
    return [int(p) if p.isdigit() else p for p in parts]


@dataclass(frozen=True)
class BankEntry:
    paper: str   # which paper the question came from
    row: Row


@dataclass
class Bank:
    entries: dict[Key, list[BankEntry]] = field(default_factory=dict)
    unmapped: list[BankEntry] = field(default_factory=list)
    papers: list[str] = field(default_factory=list)

    def total(self) -> int:
        return sum(len(v) for v in self.entries.values()) + len(self.unmapped)

    def summary(self, course: Course) -> list[tuple[str, str, int]]:
        """(section name, sub-section name, question count) for every sub-section."""
        out = []
        for section in course.sections:
            for sub in section.subsections:
                out.append((section.name, sub.name, len(self.entries.get((section.key, sub.serial), []))))
        return out


def build_bank(papers: dict[str, list[Row]], course: Course) -> Bank:
    """``papers`` maps a paper id (usually the file name) to its rows."""
    bank = Bank()
    for paper_id in sorted(papers, key=natural_key):
        bank.papers.append(paper_id)
        rows = sorted(papers[paper_id], key=lambda r: r.no)
        split = split_rows(rows, course)
        for key, group in split.by_subsection.items():
            bank.entries.setdefault(key, []).extend(BankEntry(paper_id, r) for r in group)
        bank.unmapped.extend(BankEntry(paper_id, r) for r in split.unmapped)
    return bank
