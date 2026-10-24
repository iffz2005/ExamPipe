# Design notes

## Goal

Exam question banks are produced by a chain of manual steps: extract questions
from papers, format them, check them, split them by topic, merge them into a
bank. This project turns that chain into a tested, config-driven pipeline.
The first stage (this repository's current scope) is the part that is easiest
to automate *reliably*: **parse and validate** the extracted text before any
downstream step touches it.

## Decisions and why

**1. One YAML file per course, no course-specific code.**
Papers differ in section sizes, numbering, labels and language. All of that is
data (`configs/*.yaml`). A new exam is a new file. The config loader also
validates the config itself: sections must tile `1..total_questions` with no
gap, and one alias may not point at two sub-sections. A bad config fails at
load time, not in the middle of processing a paper.

**2. The schema describes shape; validators describe rules.**
`schema.Row` only says what fields exist. `validate.py` holds the domain
rules and returns a list of `Issue` objects. Raising on the first bad value
would hide every later problem; returning issues lets one run report the whole
paper. Each issue has a stable `code`, a severity (`error` / `warning`) and
the question number and source line.

**3. Labels are normalized before comparison.**
Text that looks identical can differ in bytes: non-breaking spaces, en-dash vs
hyphen, zero-width characters, or a letter stored as one code point vs. a base
letter plus a combining mark (Unicode NFC vs. NFD, common in Devanagari). Plain
string equality silently fails on these. `normalize_label` maps all variants to
one form and has tests for each. This class of bug is invisible in review
because the strings look the same.

**4. Warnings are for humans, errors are for rules.**
A missing answer option is wrong. A one-sentence explanation or an
`{{Image}}` placeholder might be fine but deserves a look. `--strict` turns
warnings into failures for CI.

## Known limits (stated honestly)

- The KaTeX checks are *structural* (balanced `$`, braces, no edge spaces, no
  line breaks inside a span). They do not render math, so a syntactically
  balanced but semantically wrong formula passes.
- The validator cannot judge whether an answer is *correct*. That needs a
  second opinion (a model or a human) and an evaluation set.
- Sentence counting is a heuristic (split on `. ! ?` followed by a space), so
  abbreviations such as "Dr. Rao" count as a boundary. It is a warning for
  that reason.

## Roadmap

1. Split a validated paper by sub-section and merge papers into a bank
   (config-driven; Excel export).
2. Optional extraction step that calls an LLM with a structured-output schema,
   feeds failures back for repair, and writes unresolved rows to a review file.
3. Evaluation harness: a small hand-checked gold set, field-level accuracy,
   comparison of prompts or models.
4. Search and similarity over the bank: TF-IDF and BM25 baselines versus
   embeddings, near-duplicate detection, evaluated with recall@k and MRR.
