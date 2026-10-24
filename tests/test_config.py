import copy

import pytest
import yaml
from pydantic import ValidationError

from exampipe.config import Course, ConfigError, load_course

BASE = {
    "course_id": "t",
    "display_name": "t",
    "total_questions": 4,
    "answers_allowed": ["1", "2", "3", "4"],
    "difficulties": ["Easy"],
    "sections": [
        {"key": "A", "name": "Alpha", "start": 1, "end": 2,
         "subsections": [{"serial": 1, "code": "X", "name": "Xray", "aliases": ["ex"]}]},
        {"key": "B", "name": "Beta", "start": 3, "end": 4,
         "subsections": [{"serial": 1, "code": "Y", "name": "Yankee", "aliases": []}]},
    ],
}


def test_demo_config_loads(course):
    assert course.total_questions == 30
    assert [s.key for s in course.sections] == ["MATH", "REAS", "GK"]


@pytest.mark.parametrize("label", ["Percentage", "percent", "PERCENTAGES", " Percentage Problems "])
def test_resolve_accepts_canonical_name_and_aliases(course, label):
    section, sub = course.resolve(label)
    assert section.key == "MATH" and sub.code == "PCT"


def test_resolve_unknown_returns_none(course):
    assert course.resolve("Astrology") is None


def test_suggest_finds_the_closest_label(course):
    assert course.suggest("Percentge") == "Percentage"
    assert course.suggest("zzzzzz") is None


def test_section_for_number(course):
    assert course.section_for_number(1).key == "MATH"
    assert course.section_for_number(10).key == "MATH"
    assert course.section_for_number(11).key == "REAS"
    assert course.section_for_number(30).key == "GK"
    assert course.section_for_number(31) is None


def test_alias_collision_is_rejected():
    data = copy.deepcopy(BASE)
    data["sections"][1]["subsections"][0]["aliases"] = ["ex"]   # already used by Xray
    with pytest.raises(ValidationError, match="maps to both"):
        Course.model_validate(data)


def test_gap_between_sections_is_rejected():
    data = copy.deepcopy(BASE)
    data["sections"][1]["start"] = 4
    with pytest.raises(ValidationError, match="contiguous"):
        Course.model_validate(data)


def test_total_must_match_sections():
    data = copy.deepcopy(BASE)
    data["total_questions"] = 5
    with pytest.raises(ValidationError, match="total_questions"):
        Course.model_validate(data)


def test_load_course_wraps_errors(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text(yaml.safe_dump({"course_id": "x"}), encoding="utf-8")
    with pytest.raises(ConfigError):
        load_course(bad)
    with pytest.raises(ConfigError):
        load_course(tmp_path / "missing.yaml")
