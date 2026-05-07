#!/usr/bin/env python3
"""L1b validator: Language policy (configurable per culture).

Language policy is determined per culture folder by:
1. README.md Language(s): specification (e.g., **Language(s):** German)
2. ALLOWED_LANGUAGES env variable (default: english)

Infrastructure files (README.md, REFERENCES.md) are always validated as English.
Culture content files use the language declared in their folder's README.

  ALLOWED_LANGUAGES=english python tests/validate_language.py
  ALLOWED_LANGUAGES=english,german python tests/validate_language.py

Exit codes:
  0 = language policy satisfied
  1 = policy violation found
  2 = error reading files
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

from lingua import Language, LanguageDetectorBuilder

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from findings import Issue

ROOT = HERE.parent

# Read from env; default to english-only.
ALLOWED_LANGUAGES: set[str] = set(
    os.getenv("ALLOWED_LANGUAGES", "english").lower().split(",")
)

# Exceptions: proper nouns that should never trigger detection.
# One word or phrase per line. Add here when lingua produces a false positive.
EXCEPTIONS_FILE = HERE / "language_exceptions.txt"

# All languages lingua will consider. Extend this dict to add new languages.
LINGUA_LANGUAGES = {
    "english": Language.ENGLISH,
    "french": Language.FRENCH,
    "german": Language.GERMAN,
    "spanish": Language.SPANISH,
    "italian": Language.ITALIAN,
    "dutch": Language.DUTCH,
}

_detector = LanguageDetectorBuilder.from_languages(
    *LINGUA_LANGUAGES.values()
).build()

_EXCEPTIONS: set[str] = set()  # loaded once at module init below

# Prose sections - only these are checked for language violations.
# Sections like Holds and Owner carry structured data by design and are skipped.
PROSE_SECTIONS: set[str] = {"tagline", "shown", "offers", "withheld", "projection", "action", "shadow", "tell", "load bearing", "apparent", "yearbook", "drives", "loses", "orders"}

# Minimum word count of a non-allowed language span to count as a violation.
# Short spans are proper nouns. Long spans are sentences.
# If the validator fires, fix the content - do not raise this threshold.
_MIN_SPAN_WORDS = 15

# -----------------------------------------------------------------------

SECTION_RE = re.compile(
    r"^##\s+(\S.*?)\r?\n(.*?)(?=^##\s+|^---\s*$|\Z)",
    re.MULTILINE | re.DOTALL,
)


def _load_exceptions() -> set[str]:
    if not EXCEPTIONS_FILE.exists():
        return set()
    return {
        line.strip().lower()
        for line in EXCEPTIONS_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    }


_EXCEPTIONS = _load_exceptions()


def _get_allowed_languages_for_file(file_path: Path) -> set[str]:
    """Determine allowed languages for a file based on culture README.
    
    Strategy:
    1. Skip infrastructure files (README.md, REFERENCES.md) - always English
    2. For culture content files: read ../README.md for Language: specification
    3. Parse "**Language(s):** <language_list>" line
    4. Fall back to ALLOWED_LANGUAGES env var if not found
    
    Returns set of allowed language codes (e.g., {'german', 'english'})
    """
    # Infrastructure files are always validated as English
    if file_path.name in ('README.md', 'REFERENCES.md'):
        return {'english'}
    
    # Try to read Language from ../README.md
    readme_path = file_path.parent / 'README.md'
    if readme_path.exists():
        try:
            readme_text = readme_path.read_text(encoding='utf-8')
            # Look for pattern: **Language(s):** <language_list>
            for line in readme_text.split('\n'):
                if '**Language(s):**' in line:
                    # Extract language list (e.g., "German (Hochdeutsch)" → "german")
                    lang_spec = line.split('**Language(s):**')[1].strip()
                    # Parse comma-separated languages, extract language name
                    langs = set()
                    for lang in lang_spec.split(','):
                        # Take first word before space/paren, convert to lowercase
                        lang_name = lang.split('(')[0].strip().lower()
                        if lang_name and lang_name in LINGUA_LANGUAGES:
                            langs.add(lang_name)
                    if langs:
                        return langs
        except Exception:
            pass
    
    # Fall back to environment variable
    return ALLOWED_LANGUAGES



def _strip_exceptions(text: str, exceptions: set[str]) -> str:
    for word in exceptions:
        text = re.sub(re.escape(word), " ", text, flags=re.IGNORECASE)
    return text


# Strip markdown links, list bullets, and inline code before detection.
_MD_LINK_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")   # [text](url) -> text
_MD_NOISE_RE = re.compile(r"[`*_~|]|^\s*[-*+]\s+", re.MULTILINE)


def _clean(text: str) -> str:
    """Strip markdown links and noise, leaving readable prose."""
    text = _MD_LINK_RE.sub(r"\1", text)
    text = _MD_NOISE_RE.sub(" ", text)
    return text


def _detect_violation(body: str, effective_allowed: set[str]) -> str | None:
    """Return the language name if a non-allowed span of 15+ words is found.

    Uses detect_multiple_languages_of so both languages in mixed text are
    identified. Proper nouns produce short spans; prose produces long spans.
    """
    clean = _strip_exceptions(_clean(body), _EXCEPTIONS)
    spans = _detector.detect_multiple_languages_of(clean)
    for span in spans:
        lang = span.language.name.lower()
        if lang in effective_allowed:
            continue
        span_text = clean[span.start_index:span.end_index].strip()
        if len(span_text.split()) >= _MIN_SPAN_WORDS:
            return lang
    return None


def _check_content(text: str, allowed: set[str] | None = None) -> list[tuple[str, str]]:
    """Return list of (section, language) violations found."""
    effective_allowed = allowed if allowed is not None else ALLOWED_LANGUAGES
    violations = []

    for m in SECTION_RE.finditer(text):
        heading = m.group(1).strip()
        if heading.lower() not in PROSE_SECTIONS:
            continue
        body = m.group(2).strip()
        if not body:
            continue
        lang = _detect_violation(body, effective_allowed)
        if lang:
            violations.append((heading, lang))

    return violations


def validate(path: Path) -> list[Issue]:
    """Per-file entry for the orchestrator. Returns one Issue per violation."""
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []
    
    # Get allowed languages for this specific file
    allowed_langs = _get_allowed_languages_for_file(path)
    
    violations = _check_content(text, allowed_langs)
    allowed_str = " and ".join(sorted(allowed_langs))
    
    return [
        Issue(
            error=f"{path}: {lang.capitalize()} prose in ## {section}",
            verdict=f"rewrite the passage in {allowed_str}"
        )
        for section, lang in violations
    ]


def main(argv: list[str] | None = None) -> int:
    """Enforce the language policy.

    With no arguments: walks all regions files.
    With file arguments: checks only the given files (CI mode).
    """
    if argv is None:
        argv = sys.argv[1:]

    if argv:
        targets = [Path(a) for a in argv]
    else:
        targets = sorted(
            p for p in (ROOT / "regions").rglob("*.md")
            if ".git" not in p.parts
        )

    allowed_str = " and ".join(sorted(ALLOWED_LANGUAGES))
    all_issues = []

    try:
        for file_path in targets:
            if not file_path.exists():
                continue
            try:
                issues = validate(file_path)
                all_issues.extend(issues)
            except Exception as e:
                print(f"Error reading {file_path}: {e}", file=sys.stderr)
                return 2
    except Exception as e:
        print(f"Error scanning files: {e}", file=sys.stderr)
        return 2

    if all_issues:
        print(f"Language policy ({allowed_str}) failed:\n")
        for issue in all_issues:
            print(f"FAIL {issue.error}")
            if issue.verdict:
                print(f"  verdict: {issue.verdict}")
        return 1

    total = len(targets)
    print(f"OK: {total} file(s) passed language policy ({allowed_str})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
