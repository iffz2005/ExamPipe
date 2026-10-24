"""Seeded generator of synthetic demo papers for configs/demo_exam.yaml.

Everything is invented: arithmetic is generated from random numbers with the
answer COMPUTED (so it is right by construction), reasoning items come from
small templates, and general-knowledge items come from a pool of widely known
facts. ``make_paper(seed)`` always returns the same 30 questions for the same
seed, so tests and demos are reproducible.

Why it exists: later stages (search, duplicate detection, evaluation) need
more data than one hand-written paper, and real exam content can never be
published.
"""

from __future__ import annotations

import random
from math import gcd

from .schema import Row

M, R, G = "Mathematics", "Reasoning", "General Knowledge"

# (sub_section, question, options, correct_answer, explanation, difficulty)
Item = tuple[str, str, list[str], str, str, str]


# ---- small helpers -----------------------------------------------------------


def _t(value) -> str:
    """Wrap a value in an inline math span."""
    return "$" + str(value) + "$"


def _frac(a, b) -> str:
    return r"\frac{" + str(a) + "}{" + str(b) + "}"


def _pct(n) -> str:
    return str(n) + r"\%"


def _rs(n) -> str:
    return r"\text{Rs. }" + str(n)


def _reduce(a: int, b: int) -> tuple[int, int]:
    g = gcd(a, b)
    return a // g, b // g


def _near(correct: int, step: int, rng: random.Random) -> list[int]:
    """Plausible wrong numbers around ``correct`` (positive, shuffled)."""
    candidates = [correct + k * step for k in (-3, -2, -1, 1, 2, 3)]
    candidates = [c for c in candidates if c > 0]
    rng.shuffle(candidates)
    return candidates


def _pack(correct: str, wrong: list[str], rng: random.Random) -> tuple[list[str], str]:
    """Build 4 distinct options with the correct one at a random position."""
    distinct: list[str] = []
    for w in wrong:
        if w != correct and w not in distinct:
            distinct.append(w)
    if len(distinct) < 3:
        raise ValueError("not enough distinct distractors")
    options = [correct, *distinct[:3]]
    rng.shuffle(options)
    return options, str(options.index(correct) + 1)


# ---- mathematics -------------------------------------------------------------


def _pct_of(rng) -> Item:
    p = rng.choice([10, 15, 20, 25, 30, 40, 50, 60, 75])
    n = rng.randrange(40, 401, 20)
    c = p * n // 100
    options, ans = _pack(_t(c), [_t(x) for x in _near(c, max(1, c // 5), rng)], rng)
    question = "What is " + _t(_pct(p)) + " of " + _t(n) + "?"
    expl = (
        "The percentage " + _t(_pct(p)) + " means " + _t(_frac(p, 100)) + ". "
        "Multiplying this by the number gives " + _t(_frac(p, 100) + r"\times" + str(n) + "=" + str(c)) + ".<br><br>"
        "Hence <b>" + _t(c) + "</b> is the required value."
    )
    return "Percentage", question, options, ans, expl, "Easy"


def _pct_increase(rng) -> Item:
    a = rng.randrange(100, 501, 20)
    pct = rng.choice([10, 20, 25, 40, 50])
    b = a * (100 + pct) // 100
    d = b - a
    options, ans = _pack(_t(_pct(pct)), [_t(_pct(x)) for x in _near(pct, 5, rng)], rng)
    question = "A price rises from " + _t(a) + " to " + _t(b) + ". What is the percentage increase?"
    expl = (
        "The increase is " + _t(str(b) + "-" + str(a) + "=" + str(d)) + ". "
        "The percentage increase is " + _t(_frac(d, a) + r"\times100=" + _pct(pct)) + ".<br><br>"
        "Therefore the price rose by <b>" + _t(_pct(pct)) + "</b>."
    )
    return "Percentage", question, options, ans, expl, "Medium"


def _pct_reverse(rng) -> Item:
    p = rng.choice([20, 25, 40, 50, 60, 75])
    x = rng.randrange(40, 401, 20)
    v = p * x // 100
    options, ans = _pack(_t(x), [_t(c) for c in _near(x, 20, rng)], rng)
    question = "If " + _t(_pct(p)) + " of a number is " + _t(v) + ", what is the number?"
    expl = (
        "Let the number be " + _t("x") + ". "
        "Then " + _t(_frac(p, 100) + "x=" + str(v)) + ", so " + _t("x=" + _frac(str(v) + r"\times100", p) + "=" + str(x)) + ".<br><br>"
        "The number is therefore <b>" + _t(x) + "</b>."
    )
    return "Percentage", question, options, ans, expl, "Medium"


def _ratio_divide(rng) -> Item:
    a, b = rng.choice([(1, 2), (2, 3), (3, 4), (3, 5), (2, 5), (4, 5), (1, 3), (1, 4)])
    unit = rng.randrange(4, 21)
    total, larger, smaller = (a + b) * unit, b * unit, a * unit
    wrong = [smaller, larger + unit, larger - unit, total // 2, larger + 2 * unit]
    options, ans = _pack(_t(larger), [_t(w) for w in wrong if w > 0], rng)
    question = "Divide " + _t(total) + " in the ratio " + _t(str(a) + ":" + str(b)) + ". What is the larger part?"
    expl = (
        "The total number of parts is " + _t(str(a) + "+" + str(b) + "=" + str(a + b)) + ". "
        "One part equals " + _t(_frac(total, a + b) + "=" + str(unit)) + ".<br><br>"
        "The larger part has " + _t(b) + " parts, so it is <b>" + _t(larger) + "</b>."
    )
    return "Ratio and Proportion", question, options, ans, expl, "Easy"


def _ratio_given(rng) -> Item:
    first, second = rng.choice([("boys", "girls"), ("apples", "oranges"), ("pens", "pencils")])
    a, b = rng.choice([(3, 2), (2, 3), (4, 3), (5, 2), (3, 5), (5, 4)])
    unit = rng.randrange(3, 13)
    x, y = a * unit, b * unit
    options, ans = _pack(_t(y), [_t(c) for c in _near(y, max(1, unit), rng)], rng)
    question = (
        "The ratio of " + first + " to " + second + " in a group is " + _t(str(a) + ":" + str(b)) + ". "
        "If there are " + _t(x) + " " + first + ", how many " + second + " are there?"
    )
    expl = (
        "Each part of the ratio equals " + _t(_frac(x, a) + "=" + str(unit)) + ". "
        "The " + second + " make up " + _t(b) + " parts, so there are " + _t(str(b) + r"\times" + str(unit) + "=" + str(y)) + " " + second + ".<br><br>"
        "The answer is therefore <b>" + _t(y) + "</b>."
    )
    return "Ratio and Proportion", question, options, ans, expl, "Easy"


def _ratio_chain(rng) -> Item:
    a = rng.randrange(1, 6)
    b1, b2 = rng.sample([2, 3, 4, 5, 6], 2)
    c = rng.randrange(1, 8)
    lcm = b1 * b2 // gcd(b1, b2)
    big_a, big_c = a * (lcm // b1), c * (lcm // b2)
    ra, rc = _reduce(big_a, big_c)
    ans_text = str(ra) + ":" + str(rc)
    wrong = [str(rc) + ":" + str(ra), str(a) + ":" + str(c), str(ra + 1) + ":" + str(rc), str(ra) + ":" + str(rc + 1),
             str(ra + 2) + ":" + str(rc), str(ra) + ":" + str(rc + 2), str(ra + 1) + ":" + str(rc + 1)]
    options, ans = _pack(_t(ans_text), [_t(w) for w in wrong], rng)
    question = (
        "If " + _t("x:y=" + str(a) + ":" + str(b1)) + " and " + _t("y:z=" + str(b2) + ":" + str(c))
        + ", what is " + _t("x:z") + "?"
    )
    expl = (
        "Make the value of " + _t("y") + " equal in both ratios, using the LCM " + _t(lcm) + " of " + _t(b1) + " and " + _t(b2) + ". "
        "This gives " + _t("x:y:z=" + str(big_a) + ":" + str(lcm) + ":" + str(big_c)) + ".<br><br>"
        "Hence the required ratio is <b>" + _t(ans_text) + "</b>."
    )
    return "Ratio and Proportion", question, options, ans, expl, "Hard"


def _work_together(rng) -> Item:
    x, y = rng.choice([(10, 15), (12, 24), (20, 30), (15, 30), (6, 12), (12, 36), (18, 36), (30, 60), (8, 24), (9, 18)])
    days = x * y // (x + y)
    options, ans = _pack(_t(days), [_t(c) for c in _near(days, 1, rng)], rng)
    question = (
        "A can finish a job in " + _t(x) + " days and B in " + _t(y) + " days. "
        "Working together, in how many days will they finish it?"
    )
    expl = (
        "In one day A does " + _t(_frac(1, x)) + " of the job and B does " + _t(_frac(1, y)) + ". "
        "Together they do " + _t(_frac(1, x) + "+" + _frac(1, y) + "=" + _frac(x + y, x * y))
        + " of the job per day, so the job takes " + _t(_frac(x * y, x + y) + "=" + str(days)) + " days.<br><br>"
        "They will therefore finish it in <b>" + _t(days) + "</b> days."
    )
    return "Time and Work", question, options, ans, expl, "Medium"


def _tap_fraction(rng) -> Item:
    t = rng.choice([8, 10, 12, 15, 20, 24])
    h = rng.choice([2, 3, 4, 5])
    ra, rb = _reduce(h, t)
    wrong_pairs = [_reduce(h + 1, t), _reduce(h + 2, t), _reduce(h, t + 2), _reduce(h, t - 2), _reduce(t - h, t), _reduce(1, h)]
    wrong = [_t(_frac(*p)) for p in wrong_pairs]
    options, ans = _pack(_t(_frac(ra, rb)), wrong, rng)
    question = "A tap fills a tank in " + _t(t) + " hours. How much of the tank does it fill in " + _t(h) + " hours?"
    expl = (
        "The tap fills " + _t(_frac(1, t)) + " of the tank every hour. "
        "In " + _t(h) + " hours it fills " + _t(str(h) + r"\times" + _frac(1, t) + "=" + _frac(ra, rb)) + " of the tank.<br><br>"
        "The answer is therefore <b>" + _t(_frac(ra, rb)) + "</b>."
    )
    return "Time and Work", question, options, ans, expl, "Easy"


def _si_interest(rng) -> Item:
    p = rng.choice([500, 800, 1000, 1200, 1500, 2000, 2500])
    r = rng.choice([4, 5, 6, 8, 10])
    t = rng.choice([2, 3, 4, 5])
    si = p * r * t // 100
    options, ans = _pack(_t(_rs(si)), [_t(_rs(c)) for c in _near(si, max(10, si // 5 // 10 * 10), rng)], rng)
    question = (
        "What is the simple interest on " + _t(_rs(p)) + " at " + _t(_pct(r))
        + " per annum for " + _t(t) + " years?"
    )
    expl = (
        "Simple interest is given by " + _t(r"SI=\frac{P\times R\times T}{100}") + ". "
        "Substituting the values gives " + _t("SI=" + _frac(str(p) + r"\times" + str(r) + r"\times" + str(t), 100) + "=" + str(si)) + ".<br><br>"
        "The interest earned is therefore <b>" + _t(_rs(si)) + "</b>."
    )
    return "Simple Interest", question, options, ans, expl, "Easy"


def _si_rate(rng) -> Item:
    p = rng.choice([400, 500, 800, 1000, 1200, 1500, 2000])
    r = rng.choice([4, 5, 6, 8, 10, 12])
    t = rng.choice([2, 3, 4, 5])
    si = p * r * t // 100
    options, ans = _pack(_t(_pct(r)), [_t(_pct(c)) for c in _near(r, 2, rng)], rng)
    question = (
        "At what rate of simple interest per annum will " + _t(_rs(p)) + " earn " + _t(_rs(si))
        + " in " + _t(t) + " years?"
    )
    expl = (
        "From " + _t(r"SI=\frac{P\times R\times T}{100}") + " we get " + _t(r"R=\frac{SI\times100}{P\times T}") + ". "
        "Substituting gives " + _t("R=" + _frac(str(si) + r"\times100", str(p) + r"\times" + str(t)) + "=" + str(r)) + ".<br><br>"
        "The required rate is <b>" + _t(_pct(r)) + "</b> per annum."
    )
    return "Simple Interest", question, options, ans, expl, "Medium"


_MATH_MAKERS = [_pct_of, _pct_increase, _pct_reverse, _ratio_divide, _ratio_given,
                _ratio_chain, _work_together, _tap_fraction, _si_interest, _si_rate]


# ---- reasoning ---------------------------------------------------------------


def _series_question(terms: list[int]) -> str:
    return "Find the next number in the series: " + ", ".join(_t(x) for x in terms) + ", ?"


def _s_arith(rng) -> Item:
    s, d = rng.randrange(2, 20), rng.randrange(2, 9)
    terms = [s + i * d for i in range(5)]
    nxt = s + 5 * d
    options, ans = _pack(_t(nxt), [_t(c) for c in _near(nxt, d, rng)], rng)
    expl = (
        "Each term is " + _t(d) + " more than the previous term. "
        "Adding " + _t(d) + " to the last term gives " + _t(str(terms[-1]) + "+" + str(d) + "=" + str(nxt)) + ".<br><br>"
        "The next number is therefore <b>" + _t(nxt) + "</b>."
    )
    return "Number Series", _series_question(terms), options, ans, expl, "Easy"


def _s_geom(rng) -> Item:
    s, mult = rng.choice([1, 2, 3, 5]), rng.choice([2, 3])
    terms = [s * mult ** i for i in range(4)]
    nxt = s * mult ** 4
    options, ans = _pack(_t(nxt), [_t(c) for c in _near(nxt, max(1, nxt // 4), rng)], rng)
    expl = (
        "Each term is " + _t(mult) + " times the previous term. "
        "Multiplying the last term by " + _t(mult) + " gives " + _t(str(terms[-1]) + r"\times" + str(mult) + "=" + str(nxt)) + ".<br><br>"
        "The next number is therefore <b>" + _t(nxt) + "</b>."
    )
    return "Number Series", _series_question(terms), options, ans, expl, "Easy"


def _s_squares(rng) -> Item:
    k = rng.randrange(1, 8)
    terms = [(k + i) ** 2 for i in range(4)]
    nxt = (k + 4) ** 2
    options, ans = _pack(_t(nxt), [_t(c) for c in _near(nxt, max(1, k + 2), rng)], rng)
    powers = ", ".join(_t(str(k + i) + "^2") for i in range(4))
    expl = (
        "The terms are the squares of consecutive natural numbers: " + powers + ". "
        "The next term is " + _t(str(k + 4) + "^2=" + str(nxt)) + ".<br><br>"
        "The answer is therefore <b>" + _t(nxt) + "</b>."
    )
    return "Number Series", _series_question(terms), options, ans, expl, "Easy"


def _s_diffs(rng) -> Item:
    s, d0 = rng.randrange(2, 10), rng.randrange(2, 5)
    diffs = [d0 + 2 * i for i in range(4)]
    terms = [s]
    for d in diffs:
        terms.append(terms[-1] + d)
    next_diff = d0 + 8
    nxt = terms[-1] + next_diff
    options, ans = _pack(_t(nxt), [_t(c) for c in _near(nxt, 2, rng)], rng)
    listed = ", ".join(_t(d) for d in diffs[:-1]) + " and " + _t(diffs[-1])
    expl = (
        "The differences between consecutive terms are " + listed + ". "
        "They grow by " + _t(2) + " each time, so the next difference is " + _t(next_diff) + ". "
        "Adding it to the last term gives " + _t(str(terms[-1]) + "+" + str(next_diff) + "=" + str(nxt)) + ".<br><br>"
        "The next number is therefore <b>" + _t(nxt) + "</b>."
    )
    return "Number Series", _series_question(terms), options, ans, expl, "Medium"


def _s_letters(rng) -> Item:
    start, step = rng.randrange(0, 9), rng.choice([2, 3])
    letters = [chr(65 + start + i * step) for i in range(4)]
    nxt_idx = start + 4 * step
    nxt = chr(65 + nxt_idx)
    wrong = [chr(65 + nxt_idx + k) for k in (-2, -1, 1, 2) if 0 <= nxt_idx + k < 26]
    options, ans = _pack(nxt, wrong, rng)
    words = {2: "two", 3: "three"}[step]
    question = "Find the missing letter: " + ", ".join(letters) + ", ?"
    expl = (
        "The letters move forward by " + words + " places each time. "
        "Moving " + words + " places forward from " + letters[-1] + " gives " + nxt + ".<br><br>"
        "The missing letter is therefore <b>" + nxt + "</b>."
    )
    return "Number Series", question, options, ans, expl, "Easy"


_SERIES_MAKERS = [_s_arith, _s_geom, _s_squares, _s_diffs, _s_letters]

# (A, B, C, D, wrong options, why A-B, why C-D)
_ANALOGIES = [
    ("Book", "Reading", "Fork", "Eating", ["Drawing", "Writing", "Cooking"],
     "A book is an object used for reading", "a fork is an object used for eating"),
    ("Doctor", "Hospital", "Teacher", "School", ["Student", "Pen", "Library"],
     "A doctor works in a hospital", "a teacher works in a school"),
    ("Bird", "Nest", "Bee", "Hive", ["Honey", "Flower", "Wing"],
     "A bird lives in a nest", "a bee lives in a hive"),
    ("Pen", "Writing", "Knife", "Cutting", ["Eating", "Sharpening", "Cooking"],
     "A pen is a tool used for writing", "a knife is a tool used for cutting"),
    ("Fish", "Water", "Camel", "Desert", ["Ocean", "Mountain", "Jungle"],
     "A fish lives in water", "a camel lives in the desert"),
    ("Eye", "Seeing", "Ear", "Hearing", ["Smelling", "Tasting", "Touching"],
     "The eye is the organ used for seeing", "the ear is the organ used for hearing"),
    ("Day", "Night", "Hot", "Cold", ["Warm", "Sunny", "Ice"],
     "Day is the opposite of night", "hot is the opposite of cold"),
    ("Painter", "Brush", "Writer", "Pen", ["Canvas", "Studio", "Story"],
     "A painter works with a brush", "a writer works with a pen"),
    ("Cow", "Milk", "Hen", "Eggs", ["Meat", "Feather", "Corn"],
     "A cow is kept for milk", "a hen is kept for eggs"),
    ("Sculptor", "Statue", "Poet", "Poem", ["Canvas", "Stage", "Camera"],
     "A sculptor creates a statue", "a poet creates a poem"),
]


def _analogy(entry, rng) -> Item:
    a, b, c, d, wrong, rel_ab, rel_cd = entry
    options, ans = _pack(d, wrong, rng)
    question = a + " is to " + b + " as " + c + " is to ?"
    expl = rel_ab + ". In the same way, " + rel_cd + ".<br><br>The correct answer is therefore <b>" + d + "</b>."
    return "Analogies", question, options, ans, expl, "Easy"


_CODE_WORDS = ["CAT", "DOG", "SUN", "BAT", "PEN", "MAP", "RED", "TOP", "JAM", "FAN", "HAT"]


def _shift(word: str, k: int) -> str:
    return "".join(chr((ord(ch) - 65 + k) % 26 + 65) for ch in word)


def _code_shift(rng) -> Item:
    source, target = rng.sample(_CODE_WORDS, 2)
    k = rng.choice([1, 2, 3])
    correct = _shift(target, k)
    wrong = [_shift(target, k + 1), _shift(target, k + 2), _shift(target, k - 1) if k > 1 else _shift(target, k + 3),
             correct[:-1] + chr((ord(correct[-1]) - 65 + 1) % 26 + 65)]
    options, ans = _pack(correct, wrong, rng)
    words = {1: "one place", 2: "two places", 3: "three places"}[k]

    def arrows(word: str) -> str:
        return ", ".join(_t(a + r"\rightarrow " + b) for a, b in zip(word, _shift(word, k)))

    question = "If " + source + " is coded as " + _shift(source, k) + ", how is " + target + " coded?"
    expl = (
        "Each letter in " + source + " is shifted " + words + " forward: " + arrows(source) + ". "
        "Applying the same rule to " + target + " gives " + arrows(target) + ".<br><br>"
        "The code for " + target + " is therefore <b>" + correct + "</b>."
    )
    return "Coding and Decoding", question, options, ans, expl, "Medium"


def _code_sum(rng) -> Item:
    word = rng.choice(["BAD", "BED", "CAB", "DAD", "FAD", "HEN", "JET", "ACE", "BEE"])
    values = [ord(ch) - 64 for ch in word]
    total = sum(values)
    options, ans = _pack(_t(total), [_t(c) for c in _near(total, 1, rng)], rng)
    listed = ", ".join(_t(ch + "=" + str(v)) for ch, v in zip(word[:-1], values[:-1])) + " and " + _t(word[-1] + "=" + str(values[-1]))
    question = (
        "In a certain code, " + _t("A=1") + ", " + _t("B=2") + ", " + _t("C=3") + " and so on. "
        "What is the sum of the values of the letters in the word " + word + "?"
    )
    expl = (
        "The values are " + listed + ". "
        "Adding them gives " + _t("+".join(str(v) for v in values) + "=" + str(total)) + ".<br><br>"
        "The required sum is therefore <b>" + _t(total) + "</b>."
    )
    return "Coding and Decoding", question, options, ans, expl, "Easy"


_SYLLOGISM_OPTIONS = ["Only I follows", "Only II follows", "Both I and II follow", "Neither I nor II follows"]

# (statements, conclusion I, conclusion II, answer, explanation)
_SYLLOGISMS = [
    (["All {X} are {Y}.", "All {Y} are {Z}."], "All {X} are {Z}.", "All {Z} are {X}.", "1",
     "Since all {X} are {Y} and all {Y} are {Z}, all {X} are also {Z}. The reverse does not follow, because some {Z} may not be {X}.<br><br>Hence <b>only conclusion I follows</b>."),
    (["Some {X} are {Y}.", "All {Y} are {Z}."], "Some {X} are {Z}.", "All {X} are {Z}.", "1",
     "Some {X} are {Y}, and all {Y} are {Z}, so those {X} are also {Z}. This gives only a partial link, because not every {X} is known to be {Y}.<br><br>Hence <b>only conclusion I follows</b>."),
    (["All {X} are {Y}.", "Some {Y} are {Z}."], "Some {X} are {Z}.", "Some {Z} are {Y}.", "2",
     "Some {Y} are {Z}, so reversing the statement shows that some {Z} are {Y}. Nothing links the {X} to the {Y} that are {Z}.<br><br>Hence <b>only conclusion II follows</b>."),
    (["No {X} are {Y}.", "All {Z} are {X}."], "No {Z} are {Y}.", "Some {Z} are {Y}.", "1",
     "All {Z} are {X}, and no {X} are {Y}, so no {Z} can be {Y}. This directly contradicts the idea that some {Z} are {Y}.<br><br>Hence <b>only conclusion I follows</b>."),
    (["All {X} are {Y}.", "Some {Z} are {X}."], "Some {Z} are {Y}.", "Some {Y} are {Z}.", "3",
     "Some {Z} are {X} and all {X} are {Y}, so those {Z} are also {Y}. Reversing this shows that some {Y} are {Z} as well.<br><br>Hence <b>both conclusions follow</b>."),
    (["Some {X} are {Y}.", "Some {Y} are {Z}."], "Some {X} are {Z}.", "All {X} are {Z}.", "4",
     "The {Y} that are {X} and the {Y} that are {Z} may be different groups. So no link between {X} and {Z} can be drawn.<br><br>Hence <b>neither conclusion follows</b>."),
]
_NOUNS = [("pens", "books", "tables"), ("cats", "dogs", "birds"), ("roses", "flowers", "plants"),
          ("doctors", "teachers", "artists"), ("cars", "vehicles", "machines")]


def _syllogism(template, rng) -> Item:
    statements, c1, c2, ans, expl = template
    x, y, z = rng.choice(_NOUNS)

    def fill(text: str) -> str:
        return text.format(X=x, Y=y, Z=z)

    question = (
        "Statements:<br>" + "<br>".join(fill(s) for s in statements)
        + "<br><br>Conclusions:<br>I. " + fill(c1) + "<br>II. " + fill(c2)
        + "<br><br>Which of the following follows?"
    )
    return "Syllogism", question, list(_SYLLOGISM_OPTIONS), ans, fill(expl), "Medium"


# ---- general knowledge ----------------------------------------------------------

# (sub_section, question, correct, wrong options, two supporting facts)
_FACTS = [
    ("Geography", "Which is the largest continent by area?", "Asia", ["Africa", "Europe", "North America"],
     ["Asia covers about 44.6 million square kilometres", "That is well ahead of Africa, the second largest continent"]),
    ("Geography", "Which is the largest ocean on Earth?", "Pacific Ocean", ["Atlantic Ocean", "Indian Ocean", "Arctic Ocean"],
     ["The Pacific Ocean covers more area than all of Earth's land combined", "It is larger than the Atlantic, Indian and Arctic Oceans"]),
    ("Geography", "Which line of latitude divides the Earth into the Northern and Southern Hemispheres?", "Equator",
     ["Tropic of Cancer", "Tropic of Capricorn", "Prime Meridian"],
     ["The Equator is the line at 0 degrees latitude", "It lies midway between the poles"]),
    ("Geography", "Which is the largest hot desert in the world?", "Sahara", ["Gobi", "Kalahari", "Thar"],
     ["The Sahara covers much of northern Africa", "Its area is about 9 million square kilometres"]),
    ("Geography", "Which is the longest mountain range on land?", "Andes", ["Himalayas", "Rockies", "Alps"],
     ["The Andes run along the western edge of South America", "They stretch for about 7,000 kilometres"]),
    ("Geography", "What is the capital of Australia?", "Canberra", ["Sydney", "Melbourne", "Perth"],
     ["Canberra was chosen as a compromise between Sydney and Melbourne", "It became the seat of government in 1927"]),
    ("Geography", "In which mountain range does Mount Everest lie?", "Himalayas", ["Andes", "Alps", "Rockies"],
     ["Mount Everest is the highest peak above sea level", "It lies in the Himalayas on the border of Nepal and China"]),
    ("History", "In which year did World War II end?", "1945", ["1943", "1947", "1950"],
     ["The war in Europe ended in May 1945", "The war in Asia ended in September 1945"]),
    ("History", "Who was the first President of the United States?", "George Washington",
     ["Thomas Jefferson", "Abraham Lincoln", "John Adams"],
     ["George Washington took office in 1789 after the Constitution was ratified", "He served two terms before stepping down in 1797"]),
    ("History", "In which year did the French Revolution begin?", "1789", ["1776", "1799", "1815"],
     ["The revolution began in 1789", "It started with the meeting of the Estates General and the storming of the Bastille"]),
    ("History", "Who was the first person to walk on the Moon?", "Neil Armstrong",
     ["Buzz Aldrin", "Yuri Gagarin", "Michael Collins"],
     ["Neil Armstrong stepped onto the Moon during the Apollo 11 mission", "This happened in July 1969"]),
    ("History", "Which empire built the Colosseum in Rome?", "Roman Empire",
     ["Greek Empire", "Ottoman Empire", "Persian Empire"],
     ["The Colosseum was built in Rome under the Flavian emperors", "Construction began around 70 AD and finished around 80 AD"]),
    ("General Science", "What is the chemical formula of water?", "$H_2O$", ["$CO_2$", "$O_2$", "$NaCl$"],
     ["A water molecule contains two hydrogen atoms and one oxygen atom", "This is written as $H_2O$"]),
    ("General Science", "Which gas do plants absorb from the atmosphere for photosynthesis?", "Carbon dioxide",
     ["Oxygen", "Nitrogen", "Hydrogen"],
     ["Plants take in carbon dioxide through small pores called stomata", "They combine it with water, using sunlight, to make glucose"]),
    ("General Science", "What is the SI unit of force?", "Newton", ["Joule", "Watt", "Pascal"],
     ["Force is measured in newtons in the SI system", "One newton is the force needed to accelerate a mass of 1 kilogram by 1 metre per second squared"]),
    ("General Science", "Which planet is known as the Red Planet?", "Mars", ["Venus", "Jupiter", "Mercury"],
     ["Mars looks red because of iron oxide on its surface", "This reddish dust gives the planet its nickname"]),
    ("General Science", "Which part of the cell is known as its powerhouse?", "Mitochondria",
     ["Nucleus", "Ribosome", "Chloroplast"],
     ["Mitochondria release usable energy from food molecules", "This energy is stored in a molecule called ATP"]),
    ("General Science", "What is the SI unit of electric current?", "Ampere", ["Volt", "Ohm", "Coulomb"],
     ["Electric current is the rate of flow of electric charge", "Its SI unit is the ampere, named after André-Marie Ampère"]),
    ("General Science", "Which gas is the most abundant in Earth's atmosphere?", "Nitrogen",
     ["Oxygen", "Carbon dioxide", "Argon"],
     ["Nitrogen makes up about 78 percent of the atmosphere", "Oxygen is the second most abundant at about 21 percent"]),
    ("Computers", "What does CPU stand for?", "Central Processing Unit",
     ["Computer Personal Unit", "Central Program Utility", "Core Processing Utility"],
     ["The CPU is the component that executes program instructions", "Its full form is Central Processing Unit"]),
    ("Computers", "Which of the following is an operating system?", "Linux", ["Python", "Excel", "HTTP"],
     ["An operating system manages hardware and runs other software",
      "Linux is a widely used example, unlike a programming language, a spreadsheet or a network protocol"]),
    ("Computers", "What does RAM stand for?", "Random Access Memory",
     ["Read Access Memory", "Rapid Action Memory", "Random Allocation Module"],
     ["RAM is the working memory a computer uses while running programs", "Its contents are lost when the power is switched off"]),
    ("Computers", "What does URL stand for?", "Uniform Resource Locator",
     ["Universal Routing Link", "Uniform Reference List", "United Resource Locator"],
     ["A URL is the address used to find a resource on the web", "It tells the browser where the resource is stored"]),
    ("Computers", "Which of the following is an input device?", "Keyboard", ["Monitor", "Speaker", "Printer"],
     ["An input device sends data into the computer", "A keyboard does this, while a monitor, speaker and printer show or produce output"]),
    ("Computers", "Which type of software is used to view websites?", "Web browser", ["Compiler", "Antivirus", "Spreadsheet"],
     ["A web browser requests pages from servers and displays them", "Chrome and Firefox are common examples"]),
]


def _fact_item(fact, rng) -> Item:
    sub, question, correct, wrong, support = fact
    options, ans = _pack(correct, wrong, rng)
    expl = support[0] + ". " + support[1] + ".<br><br>The correct answer is therefore <b>" + correct + "</b>."
    return sub, question, options, ans, expl, "Easy"


def _facts_for(sub: str) -> list:
    return [f for f in _FACTS if f[0] == sub]


# ---- the paper ----------------------------------------------------------------------


def make_paper(seed: int) -> list[Row]:
    """30 valid questions for configs/demo_exam.yaml; same seed -> same paper."""
    rng = random.Random(seed)
    items: list[tuple[str, Item]] = []

    for maker in _MATH_MAKERS:
        items.append((M, maker(rng)))

    for maker in rng.sample(_SERIES_MAKERS, 4):
        items.append((R, maker(rng)))
    for entry in rng.sample(_ANALOGIES, 2):
        items.append((R, _analogy(entry, rng)))
    items.append((R, _code_shift(rng)))
    items.append((R, _code_sum(rng)))
    for template in rng.sample(_SYLLOGISMS, 2):
        items.append((R, _syllogism(template, rng)))

    for sub, count in (("Geography", 3), ("History", 2), ("General Science", 3), ("Computers", 2)):
        for fact in rng.sample(_facts_for(sub), count):
            items.append((G, _fact_item(fact, rng)))

    rows = []
    for no, (section, (sub, question, options, ans, expl, diff)) in enumerate(items, start=1):
        rows.append(Row(no=no, section=section, sub_section=sub, question=question, options=options,
                        correct_answer=ans, explanation=expl, difficulty=diff))
    return rows


def paper_text(seed: int) -> str:
    return "\n".join(r.to_pipe_line() for r in make_paper(seed)) + "\n"
