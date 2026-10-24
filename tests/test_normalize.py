import unicodedata

import pytest

from exampipe.normalize import normalize_label


@pytest.mark.parametrize(
    "raw",
    [
        "Statement-Conclusion",
        "statement–conclusion",      # en-dash instead of hyphen
        "Statement — Conclusion",    # em-dash with spaces
        "  STATEMENT  -  CONCLUSION ",   # extra whitespace, other case
        "Statement - Conclusion",  # non-breaking spaces
        "State​ment-Conclusion",     # zero-width space inside a word
    ],
)
def test_visually_identical_labels_normalize_to_the_same_string(raw):
    assert normalize_label(raw) == "statement-conclusion"


def test_nfc_and_nfd_forms_match():
    """Devanagari nukta letters: precomposed vs. base + combining mark."""
    precomposed = "ज़"          # DEVANAGARI LETTER ZA
    decomposed = "ज़"      # JA + NUKTA
    assert precomposed != decomposed
    assert normalize_label(precomposed) == normalize_label(decomposed)
    assert normalize_label(precomposed) == unicodedata.normalize("NFC", decomposed)


def test_different_labels_stay_different():
    assert normalize_label("Percentage") != normalize_label("Percentile")
