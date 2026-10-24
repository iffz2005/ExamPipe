# exampipe

A config-driven toolkit that **parses and validates exam question banks** before they go any further down a content pipeline.

Preparing a question bank involves many manual steps: extracting questions from papers, formatting them, checking them, splitting them by topic and merging them into a bank. Mistakes made early (a missing option, a broken math formula, a mislabelled topic, a skipped question number) are expensive to find later. `exampipe` catches them at the start and tells you exactly which question and which rule failed.

> **Status:** early. Stage 1 (parsing + validation + CLI + tests) is done. See the [roadmap](#roadmap). All data in this repository is synthetic.

## Quickstart

```bash
git clone <this repo>
cd exampipe
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

pytest                            # run the tests
exampipe validate sample_data/demo_paper_clean.txt  --course configs/demo_exam.yaml
exampipe validate sample_data/demo_paper_broken.txt --course configs/demo_exam.yaml
```

Exit code: `0` no errors, `1` errors found, `2` bad file or config. `--strict` also fails on warnings.

## What it does

Input: a text file, one question per line, 11 columns separated by ` | `:

```
No | Section | Sub-Section | Question | Answer 1 | Answer 2 | Answer 3 | Answer 4 | Correct Answer | Explanation | Difficulty
```

`demo_paper_broken.txt` contains one planted defect per rule. Running the validator on it:

```
[ERROR  ] (line 16) PARSE_COLUMNS: expected 11 columns separated by ' | ', found 10
[ERROR  ] (Q2, line 2) KATEX_BR: in question: line break inside a math span: $20<br>0$
[ERROR  ] (Q3, line 3) SUBSECTION_UNKNOWN: sub-section 'Percentge' is not in the config. Did you mean 'Percentage'?
[ERROR  ] (Q4, line 4) SECTION_MISMATCH: sub-section 'Geography' belongs to 'General Knowledge', not 'Mathematics'
[ERROR  ] (Q9, line 9) ANSWER_INVALID: correct answer '5' must be one of 1/2/3/4/UNCERTAIN
[WARNING] (Q28, line 28) EXPL_SENTENCES: explanation has 1 sentence(s); expected 3 to 5
[ERROR  ] NUMBER_MISSING: 2 question number(s) missing: 16, 25
...
Demo Aptitude Exam (synthetic): parsed 29 row(s), 12 error(s), 2 warning(s)
```

### Rules

| Code | Level | Checks |
|---|---|---|
| `PARSE_COLUMNS`, `PARSE_NUMBER` | error | line has 11 columns; question number is an integer |
| `SECTION_UNKNOWN` | error | section is one of the config's sections |
| `SUBSECTION_UNKNOWN` | error | label (or any alias) exists in the config; suggests the closest match |
| `SECTION_MISMATCH` | error | the sub-section belongs to the row's section |
| `OPTION_COUNT`, `OPTION_EMPTY` | error | exactly 4 non-empty options |
| `OPTION_DUPLICATE`, `OPTION_PREFIX` | error | no repeated options; no leading `1.` / `A)` / `(b)` labels |
| `ANSWER_INVALID`, `DIFFICULTY_INVALID` | error | answer and difficulty come from the config's allowed values |
| `KATEX_UNBALANCED`, `KATEX_SPACE`, `KATEX_BR`, `KATEX_BRACES`, `KATEX_EMPTY` | error | structural checks on `$...$` in every text field |
| `EXPL_OPTION_REF` | error | explanation must not say "option 2" |
| `EXPL_SENTENCES` | warning | explanation length within the configured range |
| `IMAGE_PLACEHOLDER` | warning | `{{Image}}` present; needs a human look |
| `NUMBER_MISSING`, `NUMBER_DUPLICATE`, `NUMBER_OUT_OF_RANGE`, `NUMBER_ORDER`, `NUMBER_SECTION_MISMATCH` | error | paper numbering matches the config's section ranges |

## How it is built

```
configs/demo_exam.yaml   one course = one YAML (sections, number ranges, labels, aliases, rules)
        │
        ▼
config.py     load + validate the config itself, build alias lookup
normalize.py  canonical form for labels (NFC, dashes, zero-width, whitespace, case)
io.py         parse " | " text into Row objects (bad lines become Issues, not crashes)
schema.py     Row: the shape of one question
validate.py   row rules + whole-paper numbering rules  ->  list[Issue]
katex.py      structural checks for $...$ spans
cli.py        `exampipe validate`, `exampipe sample`
```

Design choices and known limits are in [docs/design.md](docs/design.md). In short: one YAML per course and no course-specific code; validators return issues instead of raising, so one run reports a whole paper; labels are normalized so visually identical strings actually match.

## Adding a new course

Copy `configs/demo_exam.yaml`, change the sections, number ranges, sub-sections and aliases, and run `exampipe validate paper.txt --course your_config.yaml`. The loader rejects configs whose sections leave gaps or whose aliases collide. Keep real or private configs in `configs/private/`, which is git-ignored.

## Roadmap

- [x] Parse, validate, CLI, tests
- [ ] Split a paper by sub-section and merge papers into a bank (Excel export)
- [ ] Optional LLM extraction step with a structured-output schema and a repair loop
- [ ] Evaluation harness with a small hand-checked gold set
- [ ] Search and similarity over the bank: TF-IDF / BM25 baselines vs embeddings, near-duplicate detection, recall@k and MRR

## Data

Every question in `sample_data/` is invented for this repository. Do not commit real exam papers or answer keys; `.gitignore` excludes PDF, Word and Excel files by default.
