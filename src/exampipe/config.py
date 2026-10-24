"""Course configuration: loads a YAML file and builds the label lookup.

The key idea: *data* (which labels exist, which aliases map to them, which
question numbers belong to which section) lives in YAML; *code* stays the same
for every course. Supporting a new exam means writing a new YAML file.
"""

from __future__ import annotations

from difflib import get_close_matches
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, PrivateAttr, ValidationError, model_validator

from .normalize import normalize_label


class ConfigError(ValueError):
    """The config file is invalid (bad ranges, colliding aliases, ...)."""


class SubSection(BaseModel):
    serial: int
    code: str
    name: str
    aliases: list[str] = Field(default_factory=list)


class Section(BaseModel):
    key: str
    name: str
    start: int
    end: int
    subsections: list[SubSection]


class ExplanationRule(BaseModel):
    min_sentences: int = 3
    max_sentences: int = 5


class Course(BaseModel):
    course_id: str
    display_name: str
    total_questions: int
    answers_allowed: list[str]
    difficulties: list[str]
    explanation: ExplanationRule = Field(default_factory=ExplanationRule)
    sections: list[Section]

    # Built once after validation; maps normalized label -> (section, subsection).
    _lookup: dict[str, tuple[Section, SubSection]] = PrivateAttr(default_factory=dict)

    @model_validator(mode="after")
    def _check_and_build(self) -> "Course":
        self._check_ranges()
        self._lookup = self._build_lookup()
        return self

    # ---- validation of the config itself -------------------------------

    def _check_ranges(self) -> None:
        """Sections must tile 1..total_questions with no gap and no overlap."""
        expected_start = 1
        for sec in self.sections:
            if sec.start != expected_start:
                raise ConfigError(
                    f"section {sec.key!r} starts at {sec.start}, expected {expected_start} "
                    "(sections must be contiguous and start at 1)"
                )
            if sec.end < sec.start:
                raise ConfigError(f"section {sec.key!r} has end < start")
            expected_start = sec.end + 1
        if expected_start - 1 != self.total_questions:
            raise ConfigError(
                f"sections cover 1..{expected_start - 1} but total_questions is {self.total_questions}"
            )

    def _build_lookup(self) -> dict[str, tuple[Section, SubSection]]:
        """Map every canonical name and alias to its sub-section.

        If two different sub-sections claim the same normalized alias, that is
        a config bug we want to catch at load time, not in the middle of a run.
        """
        lookup: dict[str, tuple[Section, SubSection]] = {}
        for sec in self.sections:
            for sub in sec.subsections:
                for label in [sub.name, *sub.aliases]:
                    key = normalize_label(label)
                    existing = lookup.get(key)
                    if existing is not None and existing[1] is not sub:
                        raise ConfigError(
                            f"alias {label!r} maps to both {existing[1].name!r} "
                            f"and {sub.name!r}"
                        )
                    lookup[key] = (sec, sub)
        return lookup

    # ---- queries used by the validators --------------------------------

    def resolve(self, label: str) -> tuple[Section, SubSection] | None:
        """Look up a sub-section label (any alias). None if unknown."""
        return self._lookup.get(normalize_label(label))

    def suggest(self, label: str) -> str | None:
        """Closest known label, for "did you mean ...?" hints."""
        hits = get_close_matches(normalize_label(label), list(self._lookup), n=1, cutoff=0.75)
        if not hits:
            return None
        return self._lookup[hits[0]][1].name

    def section_by_name(self, name: str) -> Section | None:
        target = normalize_label(name)
        for sec in self.sections:
            if normalize_label(sec.name) == target:
                return sec
        return None

    def section_for_number(self, no: int) -> Section | None:
        for sec in self.sections:
            if sec.start <= no <= sec.end:
                return sec
        return None


def load_course(path: str | Path) -> Course:
    """Read a YAML file and return a validated Course."""
    path = Path(path)
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ConfigError(f"cannot read config {path}: {exc}") from exc
    try:
        return Course.model_validate(data)
    except ValidationError as exc:
        raise ConfigError(f"invalid config {path}:\n{exc}") from exc
