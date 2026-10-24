from exampipe.merge import build_bank, natural_key
from exampipe.sample import clean_rows
from exampipe.split import split_rows
from exampipe.synth import make_paper


def test_split_routes_every_row_by_subsection(course):
    result = split_rows(clean_rows(), course)
    assert result.unmapped == []
    assert sum(len(v) for v in result.by_subsection.values()) == 30
    assert len(result.by_subsection) == 12  # 4 + 4 + 4 sub-sections


def test_split_routes_through_aliases(course, row):
    row.sub_section = "  Percentages "  # alias of Percentage, with stray spaces and different case
    result = split_rows([row], course)
    assert list(result.by_subsection) == [("MATH", 1)]


def test_unknown_subsection_is_kept_not_dropped(course, row):
    row.sub_section = "Astrology"
    result = split_rows([row], course)
    assert result.by_subsection == {}
    assert result.unmapped == [row]


def test_natural_key_sorts_numbers_as_numbers():
    names = ["P10", "P2", "P1", "p3"]
    assert sorted(names, key=natural_key) == ["P1", "P2", "p3", "P10"]
    # plain string sort is the bug this avoids
    assert sorted(names)[1] == "P10"


def test_bank_orders_papers_naturally_and_keeps_provenance(course):
    papers = {f"P{n}": make_paper(n) for n in (10, 2, 1)}
    bank = build_bank(papers, course)
    assert bank.papers == ["P1", "P2", "P10"]
    entries = bank.entries[("MATH", 1)]
    assert [e.paper for e in entries] == sorted((e.paper for e in entries), key=natural_key)
    assert all(e.row.sub_section == "Percentage" for e in entries)
    assert bank.total() == 90


def test_bank_sorts_rows_by_number_within_a_paper(course):
    rows = list(reversed(clean_rows()))
    bank = build_bank({"A": rows}, course)
    for entries in bank.entries.values():
        numbers = [e.row.no for e in entries]
        assert numbers == sorted(numbers)


def test_bank_summary_lists_every_subsection_even_if_empty(course):
    bank = build_bank({"A": clean_rows()[:3]}, course)  # only Percentage questions
    summary = bank.summary(course)
    assert len(summary) == 12
    assert summary[0] == ("Mathematics", "Percentage", 3)
    assert sum(count for _, _, count in summary) == 3
