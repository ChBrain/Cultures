#!/usr/bin/env python3
"""Language detection for Hofstede validators.

The keyword bags that previously lived in this module have been retired.
Per Strategy v2 (Hofstede Bag Infrastructure), keyword bags are now per
country in `regions/<region>/<country>/hofstede_bag.yaml` and are loaded
via `data/hofstede_bag_loader.py`. This module retains only:

  - `detect_language(text)`  — language detection used by validators.
  - `LINGUA_LANGUAGES`       — language → lingua-language enum mapping.
  - `DIMENSION_KEYWORDS_BY_LANGUAGE` — empty dict, kept as a stable import
    target so the loader's fallback branch returns `{}` cleanly. This
    means: every country falls through to the per-country bag system,
    and any country without a per-country bag yields zero-derived scores
    until migrated. That degenerate output is the intentional pre-migration
    signal — it tells you exactly which countries still need a Skill pass.

Restoring keyword data here is forbidden. The contract for which words
score which dimension is the per-country bag YAML, plus the shared
`data/hofstede_denylist.yaml`. See `.claude/skills/khai-create-hofstede-bag/`
for the Skill that produces them.
"""
from __future__ import annotations

from lingua import Language, LanguageDetectorBuilder

# Language mapping for lingua library.
LINGUA_LANGUAGES = {
    "english": Language.ENGLISH,
    "french": Language.FRENCH,
    "german": Language.GERMAN,
    "danish": Language.DANISH,
    "dutch": Language.DUTCH,
    "japanese": Language.JAPANESE,
}

_detector = LanguageDetectorBuilder.from_languages(
    *LINGUA_LANGUAGES.values()
).build()


def detect_language(text: str) -> str:
    """Detect language. Returns ISO 639-1 code or 'en' as default."""
    if not text or len(text.strip()) < 50:
        return "en"
    detected = _detector.detect_language_of(text)
    if detected == Language.ENGLISH:
        return "en"
    if detected == Language.FRENCH:
        return "fr"
    if detected == Language.GERMAN:
        return "de"
    if detected == Language.DANISH:
        return "da"
    if detected == Language.DUTCH:
        return "nl"
    if detected == Language.JAPANESE:
        return "ja"
    return "en"


# Empty by design. See module docstring.
DIMENSION_KEYWORDS_BY_LANGUAGE: dict[str, dict[str, dict[str, list[str]]]] = {}
