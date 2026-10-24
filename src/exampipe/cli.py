"""Command line interface.

    exampipe validate PAPER.txt --course configs/demo_exam.yaml
    exampipe build "papers/*.txt" --course configs/demo_exam.yaml --out out/
    exampipe sample --out sample_data/

Exit code: 0 = no errors, 1 = errors found, 2 = bad usage/config.
"""

from __future__ import annotations

import argparse
import glob
import sys
from collections import Counter
from pathlib import Path

from .config import ConfigError, load_course
from .export import write_bank
from .io import parse_pipe_text
from .merge import build_bank
from .sample import broken_text, clean_text
from .synth import paper_text
from .validate import validate_all

SAMPLE_PAPER_SEEDS = (1, 2, 3)


def _expand(patterns: list[str]) -> list[Path]:
    """Expand wildcards ourselves.

    Linux/macOS shells expand ``papers/*.txt`` before the program starts, but
    PowerShell and cmd do not, so the program has to do it. A pattern with no
    wildcard is taken as a plain path. Duplicates are removed, order is kept.
    """
    seen: set[Path] = set()
    out: list[Path] = []
    for pattern in patterns:
        matches = sorted(glob.glob(pattern)) if glob.has_magic(pattern) else [pattern]
        for match in matches:
            path = Path(match)
            if path not in seen:
                seen.add(path)
                out.append(path)
    return out


def _load(course_path: str):
    try:
        return load_course(course_path)
    except ConfigError as exc:
        print(f"config error: {exc}", file=sys.stderr)
        return None


def _cmd_validate(args: argparse.Namespace) -> int:
    course = _load(args.course)
    if course is None:
        return 2

    path = Path(args.paper)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"cannot read {path}: {exc}", file=sys.stderr)
        return 2

    parsed = parse_pipe_text(text)
    issues = [*parsed.issues, *validate_all(parsed.rows, course)]

    for issue in issues:
        print(issue.format())

    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]
    print(f"\n{course.display_name}: parsed {len(parsed.rows)} row(s), "
          f"{len(errors)} error(s), {len(warnings)} warning(s)")
    if issues:
        by_code = Counter(i.code for i in issues)
        print("by rule: " + ", ".join(f"{code} x{n}" for code, n in sorted(by_code.items())))

    if errors or (args.strict and warnings):
        return 1
    return 0


def _cmd_build(args: argparse.Namespace) -> int:
    course = _load(args.course)
    if course is None:
        return 2

    paths = _expand(args.papers)
    if not paths:
        print("no paper files matched", file=sys.stderr)
        return 2

    # Paper id = file name without extension. Two papers with the same id would
    # silently overwrite each other in the bank, so refuse up front.
    ids: dict[str, Path] = {}
    for path in paths:
        if path.stem in ids:
            print(f"two papers share the id '{path.stem}': {ids[path.stem]} and {path}", file=sys.stderr)
            return 2
        ids[path.stem] = path

    papers = {}
    total_errors = 0
    total_warnings = 0
    for paper_id, path in ids.items():
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"cannot read {path}: {exc}", file=sys.stderr)
            return 2
        parsed = parse_pipe_text(text)
        issues = [*parsed.issues, *validate_all(parsed.rows, course)]
        for issue in issues:
            print(f"{paper_id}: {issue.format()}")
        total_errors += sum(1 for i in issues if i.severity == "error")
        total_warnings += sum(1 for i in issues if i.severity == "warning")
        papers[paper_id] = parsed.rows

    print(f"\nchecked {len(papers)} paper(s): {total_errors} error(s), {total_warnings} warning(s)")

    # Fail closed: a bank built from broken papers looks fine and is not.
    if total_errors and not args.allow_errors:
        print("no files written. Fix the errors above, or pass --allow-errors to build anyway.",
              file=sys.stderr)
        return 1

    bank = build_bank(papers, course)
    written = write_bank(bank, course, args.out)

    print(f"\n{bank.total()} question(s) from {len(bank.papers)} paper(s) -> {len(written)} file(s) in {args.out}")
    for section, sub, count in bank.summary(course):
        print(f"  {section:<20} {sub:<24} {count:>4}")
    if bank.unmapped:
        print(f"  {len(bank.unmapped)} question(s) had an unknown sub-section -> _unmapped.xlsx")
    return 1 if total_errors else 0


def _cmd_sample(args: argparse.Namespace) -> int:
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "demo_paper_clean.txt").write_text(clean_text(), encoding="utf-8")
    (out / "demo_paper_broken.txt").write_text(broken_text(), encoding="utf-8")

    papers = out / "papers"
    papers.mkdir(exist_ok=True)
    for seed in SAMPLE_PAPER_SEEDS:
        (papers / f"demo_paper_{seed:02d}.txt").write_text(paper_text(seed), encoding="utf-8")

    print(f"wrote demo_paper_clean.txt, demo_paper_broken.txt and "
          f"{len(SAMPLE_PAPER_SEEDS)} generated papers in {out}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="exampipe", description="Exam question bank toolkit")
    sub = parser.add_subparsers(dest="command", required=True)

    p_val = sub.add_parser("validate", help="check a pipe-separated paper against a course config")
    p_val.add_argument("paper", help="text file: one question per line, 11 columns separated by ' | '")
    p_val.add_argument("--course", required=True, help="course config (YAML)")
    p_val.add_argument("--strict", action="store_true", help="treat warnings as failures too")
    p_val.set_defaults(func=_cmd_validate)

    p_build = sub.add_parser("build", help="validate papers, merge them and write one Excel file per sub-section")
    p_build.add_argument("papers", nargs="+", help="paper files or wildcards, e.g. \"papers/*.txt\" (quote them)")
    p_build.add_argument("--course", required=True, help="course config (YAML)")
    p_build.add_argument("--out", default="out", help="output folder (default: out)")
    p_build.add_argument("--allow-errors", action="store_true",
                         help="write the bank even if validation found errors")
    p_build.set_defaults(func=_cmd_build)

    p_sample = sub.add_parser("sample", help="write the synthetic demo papers")
    p_sample.add_argument("--out", default="sample_data", help="output folder")
    p_sample.set_defaults(func=_cmd_sample)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
