"""Cheap structural checks for inline KaTeX ($...$).

We are NOT rendering math here (that would need a real KaTeX engine). We catch
the mistakes that most often break rendering and are easy to detect with plain
string logic:

  * an odd number of "$" (a span is opened but never closed)
  * a space just inside the delimiters:   "$ x+1 $"
  * a line break inside a span:           "$x<br>y$"
  * unbalanced curly braces inside a span: "$\\frac{1}{2$"
  * an empty span:                         "$$"

A backslash escapes the next character, so "\\$" is a literal dollar sign.
"""

from __future__ import annotations


def _dollar_positions(text: str) -> list[int]:
    positions: list[int] = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == "\\":  # skip the escaped character
            i += 2
            continue
        if ch == "$":
            positions.append(i)
        i += 1
    return positions


def _braces_balanced(span: str) -> bool:
    depth = 0
    i = 0
    while i < len(span):
        ch = span[i]
        if ch == "\\":  # "\{" and "\}" are literal braces, not grouping
            i += 2
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth < 0:
                return False
        i += 1
    return depth == 0


def katex_spans(text: str) -> list[str] | None:
    """Return the contents of each $...$ span, or None if delimiters are unbalanced."""
    positions = _dollar_positions(text)
    if len(positions) % 2:
        return None
    return [text[a + 1 : b] for a, b in zip(positions[0::2], positions[1::2])]


def check_katex(text: str) -> list[tuple[str, str]]:
    """Return a list of (code, message) problems found in ``text``."""
    spans = katex_spans(text)
    if spans is None:
        return [("KATEX_UNBALANCED", "odd number of '$' delimiters (a math span is not closed)")]

    problems: list[tuple[str, str]] = []
    for span in spans:
        if span == "":
            problems.append(("KATEX_EMPTY", "empty math span '$$'"))
            continue
        if span.strip() == "":
            problems.append(("KATEX_EMPTY", "math span contains only whitespace"))
            continue
        if span != span.strip():
            problems.append(("KATEX_SPACE", f"space just inside the delimiters: ${span}$"))
        if "<br" in span.lower():
            problems.append(("KATEX_BR", f"line break inside a math span: ${span}$"))
        if not _braces_balanced(span):
            problems.append(("KATEX_BRACES", f"unbalanced curly braces: ${span}$"))
    return problems
