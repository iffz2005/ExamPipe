"""Text normalization for comparing labels.

Why this module exists
----------------------
The same sub-section label can reach us in many visually identical but
byte-different forms: a non-breaking space, an en-dash instead of a hyphen,
a zero-width character, or a letter stored as one code point vs. two
(Unicode NFC vs. NFD, which matters a lot for Devanagari "nukta" letters).
If we compare raw strings, a label that *looks* correct silently fails to match.

``normalize_label`` maps all those variants to one canonical form, so the
alias lookup in config.py can use plain dictionary equality.
"""

from __future__ import annotations

import re
import unicodedata

# Characters that are invisible but break string equality.
_ZERO_WIDTH = dict.fromkeys(map(ord, "​‌‍⁠﻿"), None)

# Different kinds of dash/minus -> plain hyphen.
_DASHES = dict.fromkeys(map(ord, "‐‑‒–—―−"), "-")

_WHITESPACE = re.compile(r"\s+")
_SPACED_HYPHEN = re.compile(r"\s*-\s*")


def normalize_label(text: str) -> str:
    """Return a canonical, comparison-safe form of ``text``.

    Steps (order matters):
      1. NFC normalization (merge combining marks into precomposed letters)
      2. drop zero-width characters
      3. map every dash variant to "-"
      4. collapse whitespace (this also turns NBSP into a normal space)
      5. remove spaces around hyphens ("Statement - Conclusion" == "Statement-Conclusion")
      6. casefold (a stronger lower())
    """
    text = unicodedata.normalize("NFC", text)
    text = text.translate(_ZERO_WIDTH).translate(_DASHES)
    text = _WHITESPACE.sub(" ", text).strip()
    text = _SPACED_HYPHEN.sub("-", text)
    return text.casefold()
