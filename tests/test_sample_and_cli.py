from pathlib import Path

from exampipe.cli import main
from exampipe.io import parse_pipe_text
from exampipe.sample import broken_text, clean_text
from exampipe.validate import validate_all

ROOT = Path(__file__).resolve().parent.parent
CONFIG = str(ROOT / "configs" / "demo_exam.yaml")

# Every rule we planted in sample.broken_text(), and nothing else.
EXPECTED_BROKEN = {
    "KATEX_BR", "SUBSECTION_UNKNOWN", "SECTION_MISMATCH", "OPTION_PREFIX", "OPTION_DUPLICATE",
    "ANSWER_INVALID", "KATEX_SPACE", "EXPL_OPTION_REF", "KATEX_UNBALANCED", "NUMBER_DUPLICATE",
    "NUMBER_MISSING", "PARSE_COLUMNS", "EXPL_SENTENCES", "IMAGE_PLACEHOLDER",
}


def all_codes(text, course):
    parsed = parse_pipe_text(text)
    return {i.code for i in [*parsed.issues, *validate_all(parsed.rows, course)]}


def test_clean_paper_is_fully_clean(course):
    assert all_codes(clean_text(), course) == set()


def test_broken_paper_triggers_exactly_the_planted_rules(course):
    assert all_codes(broken_text(), course) == EXPECTED_BROKEN


def test_cli_exit_codes(tmp_path, capsys):
    clean = tmp_path / "clean.txt"
    broken = tmp_path / "broken.txt"
    clean.write_text(clean_text(), encoding="utf-8")
    broken.write_text(broken_text(), encoding="utf-8")

    assert main(["validate", str(clean), "--course", CONFIG]) == 0
    assert main(["validate", str(broken), "--course", CONFIG]) == 1
    out = capsys.readouterr().out
    assert "SUBSECTION_UNKNOWN" in out and "Did you mean 'Percentage'" in out
    assert main(["validate", str(tmp_path / "nope.txt"), "--course", CONFIG]) == 2
    assert main(["validate", str(clean), "--course", str(tmp_path / "nope.yaml")]) == 2


def test_strict_mode_fails_on_warnings(tmp_path):
    only_warning = tmp_path / "w.txt"
    lines = clean_text().splitlines()
    lines[29] = lines[29].replace("Which of the following", "{{Image}} Which of the following", 1)
    only_warning.write_text("\n".join(lines) + "\n", encoding="utf-8")
    assert main(["validate", str(only_warning), "--course", CONFIG]) == 0
    assert main(["validate", str(only_warning), "--course", CONFIG, "--strict"]) == 1


def test_sample_command_writes_files(tmp_path):
    assert main(["sample", "--out", str(tmp_path)]) == 0
    assert (tmp_path / "demo_paper_clean.txt").read_text(encoding="utf-8") == clean_text()
    assert (tmp_path / "demo_paper_broken.txt").read_text(encoding="utf-8") == broken_text()
