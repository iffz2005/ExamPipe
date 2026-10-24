"""Command line interface.

    exampipe validate PAPER.txt --course configs/demo_exam.yaml
    exampipe sample --out sample_data/

Exit code: 0 = no errors, 1 = errors found, 2 = bad usage/config.
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

from .config import ConfigError, load_course
from .io import parse_pipe_text
from .sample import broken_text, clean_text
from .validate import validate_all


def _cmd_validate(args: argparse.Namespace) -> int:
    try:
        course = load_course(args.course)
    except ConfigError as exc:
        print(f"config error: {exc}", file=sys.stderr)
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


def _cmd_sample(args: argparse.Namespace) -> int:
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "demo_paper_clean.txt").write_text(clean_text(), encoding="utf-8")
    (out / "demo_paper_broken.txt").write_text(broken_text(), encoding="utf-8")
    print(f"wrote {out / 'demo_paper_clean.txt'} and {out / 'demo_paper_broken.txt'}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="exampipe", description="Exam question bank toolkit")
    sub = parser.add_subparsers(dest="command", required=True)

    p_val = sub.add_parser("validate", help="check a pipe-separated paper against a course config")
    p_val.add_argument("paper", help="text file: one question per line, 11 columns separated by ' | '")
    p_val.add_argument("--course", required=True, help="course config (YAML)")
    p_val.add_argument("--strict", action="store_true", help="treat warnings as failures too")
    p_val.set_defaults(func=_cmd_validate)

    p_sample = sub.add_parser("sample", help="write the synthetic demo papers")
    p_sample.add_argument("--out", default="sample_data", help="output folder")
    p_sample.set_defaults(func=_cmd_sample)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
