#!/usr/bin/env python3
"""L1b validator: Language policy (configurable per culture).

Policy is owned by `data/language_policy.yaml`. The validator reads:
- which languages this repo allows
- which `##` sections get language-checked
- the minimum span-word threshold for a violation to fire

Each culture folder declares its allowed languages via the README's
``**Language(s):**`` line. Values are cross-checked against the policy
registry -- a typo fails the validator with a clear message instead of
silently degrading to english-only.

Infrastructure files (README.md, REFERENCES.md) are always validated as
English. Culture content files use the language declared in their
folder's README.

  python tests/validate_language.py                            # check everything
  python tests/validate_language.py FILE...                    # check specific files
  python tests/validate_language.py --list-repo-languages      # registry view
  python tests/validate_language.py --list-country-languages   # per-culture view

Exit codes:
  0 = language policy satisfied
  1 = policy violation found
  2 = error reading files / lingua not installed / policy file invalid
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from findings import Issue  # noqa: E402

ROOT = HERE.parent
POLICY_PATH = ROOT / "data" / "language_policy.yaml"


def _lingua_language_map():
    """Build {slug: lingua.Language} lazily so the import only happens
    when the validator actually runs. Returns None if lingua isn't
    installed -- callers should surface that as a skip, not a crash.

    Adding a new language: append a slug to data/language_policy.yaml
    AND add the corresponding lingua.Language entry here. The README
    cross-check catches drift between the two.
    """
    try:
        from lingua import Language  # type: ignore
    except ImportError:
        return None
    return {
        "english": Language.ENGLISH,
        "french": Language.FRENCH,
        "german": Language.GERMAN,
        "spanish": Language.SPANISH,
        "italian": Language.ITALIAN,
        "dutch": Language.DUTCH,
        "danish": Language.DANISH,
        "polish": Language.POLISH,
    }


# ---------------------------------------------------------------------
# Policy loading
# ---------------------------------------------------------------------

def load_policy(path: Path = POLICY_PATH) -> dict:
    """Load and validate data/language_policy.yaml.

    Returns ``{languages, prose_sections, min_span_words}``. Raises
    ValueError if the file is missing or malformed -- the validator
    can't run without a policy.
    """
    if not path.is_file():
        raise ValueError(
            f"Language policy file missing: {path}. "
            "data/language_policy.yaml is the single source of truth for "
            "language config; check tests/requirements.txt and rerun."
        )
    try:
        import yaml  # type: ignore
    except ImportError as e:
        raise ValueError(
            "PyYAML is required to read the language policy. "
            "Run `pip install -r tests/requirements.txt`."
        ) from e
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    languages = raw.get("languages") or []
    sections = raw.get("prose_sections") or []
    min_words = raw.get("min_span_words")
    if not isinstance(languages, list) or not languages:
        raise ValueError(f"{path}: `languages` must be a non-empty list.")
    if not isinstance(sections, list) or not sections:
        raise ValueError(f"{path}: `prose_sections` must be a non-empty list.")
    if not isinstance(min_words, int) or min_words < 1:
        raise ValueError(f"{path}: `min_span_words` must be a positive integer.")
    return {
        "languages": [s.lower() for s in languages],
        "prose_sections": {s.lower() for s in sections},
        "min_span_words": min_words,
    }


_POLICY: dict | None = None  # lazy module-level cache; tests override via load_policy()


def _policy() -> dict:
    global _POLICY
    if _POLICY is None:
        _POLICY = load_policy()
    return _POLICY


# Proper-noun exceptions are layered:
#  - GLOBAL: tests/language_exceptions.txt  (governance-tracked, repo-wide)
#  - PER-CULTURE: regions/<region>/<country>/language_exceptions.txt
#    (lives with the culture content; e.g. `Vergangenheitsbewältigung`
#    is a German proper noun, not something to allow globally)
#
# The per-culture overlay is the Phase-2 friction reducer: contributors
# add country-specific names alongside the culture work in the same PR,
# without needing a separate governance/* change to widen the global
# allowlist.
GLOBAL_EXCEPTIONS_FILE = HERE / "language_exceptions.txt"
PER_CULTURE_EXCEPTIONS_FILENAME = "language_exceptions.txt"
_REGIONS = frozenset({"africa", "americas", "asia", "europe", "oceania"})


def _parse_exceptions(path: Path) -> set[str]:
    """Read one exceptions file. Lowercase-trim each non-comment line."""
    if not path.is_file():
        return set()
    return {
        line.strip().lower()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    }


_GLOBAL_EXCEPTIONS: set[str] = _parse_exceptions(GLOBAL_EXCEPTIONS_FILE)
_culture_exception_cache: dict[Path, set[str]] = {}


def _country_dir_for(file_path: Path) -> Path | None:
    """Return the country directory owning ``file_path``, or None.

    A country directory is any path of the form
    ``<repo>/regions/<region>/<country>/`` where region is in _REGIONS.
    For paths outside that pattern (infrastructure files, etc.), returns
    None -- there's no culture-specific overlay to load.
    """
    try:
        resolved = file_path.resolve()
    except OSError:
        return None
    for parent in resolved.parents:
        if parent.parent.name in _REGIONS:
            return parent
    return None


def _culture_exceptions_for(file_path: Path) -> set[str]:
    """Return per-culture exceptions for ``file_path``, with caching.

    Cache keyed by country directory so a multi-file run validates each
    country's exceptions file once. Cache lifetime is the process; the
    pre-commit hook is short-lived, so staleness isn't a concern.
    """
    country = _country_dir_for(file_path)
    if country is None:
        return set()
    if country not in _culture_exception_cache:
        _culture_exception_cache[country] = _parse_exceptions(
            country / PER_CULTURE_EXCEPTIONS_FILENAME,
        )
    return _culture_exception_cache[country]


def _exceptions_for(file_path: Path) -> set[str]:
    """All proper-noun exceptions applying to ``file_path``."""
    return _GLOBAL_EXCEPTIONS | _culture_exceptions_for(file_path)


# ---------------------------------------------------------------------
# README cross-check
# ---------------------------------------------------------------------

# Format: `**Language(s):** <name>[, <name>...]`. The first word before
# any parenthesis is the lingua slug; everything in parens is
# informational (`German (Hochdeutsch)` -> "german").
_LANG_LINE_RE = re.compile(r"^\*\*Language\(s\):\*\*\s*(.+)$", re.MULTILINE)


def parse_readme_languages(readme_text: str) -> list[str]:
    """Return the lingua slugs declared in a README, lowercased.

    Returns ``[]`` if no `**Language(s):**` line is found -- caller
    decides whether that's a hard failure (registry cross-check) or a
    soft fallback (per-file resolution).
    """
    m = _LANG_LINE_RE.search(readme_text)
    if not m:
        return []
    out: list[str] = []
    for chunk in m.group(1).split(","):
        head = chunk.split("(")[0].strip().lower()
        if head:
            out.append(head)
    return out


def _country_dirs() -> list[Path]:
    """All on-disk culture-bearing country directories."""
    regions = ROOT / "regions"
    if not regions.is_dir():
        return []
    out: list[Path] = []
    for region in sorted(regions.iterdir()):
        if not region.is_dir() or region.name.startswith("."):
            continue
        for country in sorted(region.iterdir()):
            if not country.is_dir() or country.name.startswith("."):
                continue
            if any(country.glob("culture_*.md")):
                out.append(country)
    return out


def _resolve_allowed_languages(file_path: Path, policy: dict) -> set[str]:
    """Determine allowed languages for ``file_path``.

    README.md and REFERENCES.md are always english. For culture content,
    read the owning README's `**Language(s):**` and keep only slugs in
    the registry. Slugs not in the registry are flagged by
    `_readme_registry_violations`; the resolved set falls back to english
    so the file isn't completely orphaned.
    """
    if file_path.name in ("README.md", "REFERENCES.md"):
        return {"english"}
    readme_path = file_path.parent / "README.md"
    if not readme_path.is_file():
        return {"english"}
    declared = parse_readme_languages(readme_path.read_text(encoding="utf-8"))
    valid = [d for d in declared if d in policy["languages"]]
    return set(valid) if valid else {"english"}


def _readme_registry_violations(policy: dict) -> list[Issue]:
    """Flag README declarations that don't resolve against the registry.

    Two failure modes:
    - the README exists but has no `**Language(s):**` line
    - the line names a language that isn't in data/language_policy.yaml

    Both are loud failures -- silent english-only fallback was the bug
    that motivated Phase 1.

    Countries with no README at all are SKIPPED here: that's a culture-
    completeness gap (L4's job), not a language-policy gap. Flagging them
    would dilute the signal in busy repos with many stub countries.
    """
    issues: list[Issue] = []
    registry = set(policy["languages"])
    for country in _country_dirs():
        readme = country / "README.md"
        if not readme.is_file():
            continue
        rel = readme.relative_to(ROOT)
        declared = parse_readme_languages(readme.read_text(encoding="utf-8"))
        if not declared:
            issues.append(Issue(
                error=f"{rel}: no `**Language(s):**` line found",
                verdict=(
                    "add `**Language(s):** <lang>` so language validation "
                    "knows what to allow"
                ),
            ))
            continue
        unknown = [d for d in declared if d not in registry]
        if unknown:
            issues.append(Issue(
                error=(
                    f"{rel}: declared language(s) {sorted(unknown)} "
                    f"not in data/language_policy.yaml registry"
                ),
                verdict=(
                    "fix the typo in the README, or add the slug to "
                    "`data/language_policy.yaml` + lingua mapping in "
                    "tests/validate_language.py (governance/* PR)"
                ),
            ))
    return issues


# ---------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------

SECTION_RE = re.compile(
    r"^##\s+(\S.*?)\r?\n(.*?)(?=^##\s+|^---\s*$|\Z)",
    re.MULTILINE | re.DOTALL,
)

_MD_LINK_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")   # [text](url) -> text
_MD_NOISE_RE = re.compile(r"[`*_~|]|^\s*[-*+]\s+", re.MULTILINE)
# Blockquoted lines are skipped before detection. Citations of foreign-
# language source material belong here -- they should pass the validator
# without polluting language_exceptions.txt with every quoted word.
_MD_BLOCKQUOTE_RE = re.compile(r"^\s*>.*$", re.MULTILINE)


def _strip_exceptions(text: str, exceptions: set[str]) -> str:
    for word in exceptions:
        text = re.sub(re.escape(word), " ", text, flags=re.IGNORECASE)
    return text


def _clean(text: str) -> str:
    text = _MD_BLOCKQUOTE_RE.sub(" ", text)
    text = _MD_LINK_RE.sub(r"\1", text)
    text = _MD_NOISE_RE.sub(" ", text)
    return text


def _build_detector(policy: dict):
    """Build a lingua detector restricted to the policy's language set.

    Returns None when lingua isn't installed; callers print a skip and
    return success (the hook becomes a no-op rather than a crash).
    """
    lang_map = _lingua_language_map()
    if lang_map is None:
        return None
    try:
        from lingua import LanguageDetectorBuilder  # type: ignore
    except ImportError:
        return None
    enums = [lang_map[s] for s in policy["languages"] if s in lang_map]
    if not enums:
        return None
    return LanguageDetectorBuilder.from_languages(*enums).build()


def _detect_violation(
    body: str,
    effective_allowed: set[str],
    detector,
    min_words: int,
    exceptions: set[str],
) -> tuple[str, str, int] | None:
    """Return (language, span_text, word_count) for the first violation.

    None when every span either matches the allowed languages or is
    shorter than ``min_words`` (proper-noun territory). The triple
    powers the actionable error message:

        FAIL <file>: German span (18 words) in ## Shown:
          'Die Wuerde des Menschen ist unantastbar...'
    """
    clean = _strip_exceptions(_clean(body), exceptions)
    spans = detector.detect_multiple_languages_of(clean)
    for span in spans:
        lang = span.language.name.lower()
        if lang in effective_allowed:
            continue
        span_text = clean[span.start_index:span.end_index].strip()
        word_count = len(span_text.split())
        if word_count >= min_words:
            return lang, span_text, word_count
    return None


def _check_content(
    text: str,
    allowed: set[str],
    policy: dict,
    detector,
    exceptions: set[str],
) -> list[tuple[str, str, str, int]]:
    """Return ``[(heading, language, span_text, word_count), ...]``."""
    violations: list[tuple[str, str, str, int]] = []
    sections = policy["prose_sections"]
    min_words = policy["min_span_words"]
    for m in SECTION_RE.finditer(text):
        heading = m.group(1).strip()
        if heading.lower() not in sections:
            continue
        body = m.group(2).strip()
        if not body:
            continue
        violation = _detect_violation(body, allowed, detector, min_words, exceptions)
        if violation is not None:
            lang, span_text, words = violation
            violations.append((heading, lang, span_text, words))
    return violations


def _violation_issue(
    file_path: Path,
    heading: str,
    lang: str,
    span_text: str,
    word_count: int,
    allowed: set[str],
) -> Issue:
    """Render a single violation into a contributor-readable Issue.

    The verdict text is the LLM fix-suggestion ladder, cheapest first:
    blockquote -> per-culture exception -> rewrite. The country-specific
    exception path is rendered explicitly so the contributor knows
    exactly which file to touch without scanning the validator source.
    """
    snippet = span_text.replace("\n", " ").strip()
    if len(snippet) > 80:
        snippet = snippet[:77] + "..."
    allowed_str = " and ".join(sorted(allowed))
    country = _country_dir_for(file_path)
    if country is not None:
        try:
            exc_path = (
                country.relative_to(ROOT) / PER_CULTURE_EXCEPTIONS_FILENAME
            )
        except ValueError:
            exc_path = Path(country.name) / PER_CULTURE_EXCEPTIONS_FILENAME
        exc_hint = f"add proper nouns to {exc_path}"
    else:
        exc_hint = (
            f"add proper nouns to {GLOBAL_EXCEPTIONS_FILE.relative_to(ROOT)}"
        )
    return Issue(
        error=(
            f"{file_path}: {lang.capitalize()} span ({word_count} words) "
            f"in ## {heading}: '{snippet}'"
        ),
        verdict=(
            f"if a quoted source, wrap as `> ...` blockquote (skipped); "
            f"if proper nouns, {exc_hint}; "
            f"otherwise rewrite in {allowed_str}"
        ),
    )


# ---------------------------------------------------------------------
# Public entry: per-file
# ---------------------------------------------------------------------

def explain(path: Path) -> list[str]:
    """Render a per-section trace of detected spans for ``path``.

    Diagnostic output for ``--explain`` mode. Each prose section's body
    is run through the detector and every detected span (allowed or
    not) is listed with its language, word count, and a snippet. This
    is the "why is my file failing?" lookup an LLM (or human) needs to
    pick the right fix -- without re-implementing the detector loop.

    Returns lines as strings rather than printing so callers can pipe
    or test the output without capturing stdout.
    """
    out: list[str] = [f"=== {path} ==="]
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError) as e:
        out.append(f"  (could not read: {e})")
        return out
    try:
        policy = _policy()
    except ValueError as e:
        out.append(f"  (policy invalid: {e})")
        return out
    detector = _build_detector(policy)
    if detector is None:
        out.append("  (lingua not installed; install via tests/requirements.txt)")
        return out
    allowed = _resolve_allowed_languages(path, policy)
    out.append(f"  allowed languages: {sorted(allowed)}")
    exceptions = _exceptions_for(path)
    out.append(f"  exceptions in scope: {len(exceptions)} entries")
    sections = policy["prose_sections"]
    min_words = policy["min_span_words"]
    for m in SECTION_RE.finditer(text):
        heading = m.group(1).strip()
        body = m.group(2).strip()
        if heading.lower() not in sections:
            out.append(f"  ## {heading}    (skipped: not in prose_sections)")
            continue
        if not body:
            out.append(f"  ## {heading}    (skipped: empty body)")
            continue
        clean = _strip_exceptions(_clean(body), exceptions)
        spans = detector.detect_multiple_languages_of(clean)
        out.append(f"  ## {heading}")
        for span in spans:
            lang = span.language.name.lower()
            text_span = clean[span.start_index:span.end_index].strip()
            words = len(text_span.split())
            snippet = text_span.replace("\n", " ")
            if len(snippet) > 60:
                snippet = snippet[:57] + "..."
            if lang in allowed:
                marker = "OK"
            elif words < min_words:
                marker = "ok (short)"
            else:
                marker = f"FAIL (>= {min_words} words)"
            out.append(f"    [{marker}] {lang:10s} {words:3d}w  '{snippet}'")
    return out


def validate(path: Path) -> list[Issue]:
    """Per-file entry for the orchestrator. Returns one Issue per violation.

    Returns [] when lingua isn't installed (treated as a skip, not a
    crash). The standalone CLI prints an explicit skip line; the
    orchestrator simply sees no findings.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []
    try:
        policy = _policy()
    except ValueError as e:
        return [Issue(error=str(e), verdict="fix data/language_policy.yaml")]
    detector = _build_detector(policy)
    if detector is None:
        return []
    allowed = _resolve_allowed_languages(path, policy)
    exceptions = _exceptions_for(path)
    violations = _check_content(text, allowed, policy, detector, exceptions)
    return [
        _violation_issue(path, section, lang, snippet, words, allowed)
        for section, lang, snippet, words in violations
    ]


# ---------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------

def _cmd_list_repo_languages() -> int:
    policy = _policy()
    for lang in policy["languages"]:
        print(lang)
    return 0


def _cmd_list_country_languages() -> int:
    """Walk regions/ and print each country's README-declared languages.

    Marks countries whose README is missing or has no parsable
    `**Language(s):**` line with ``<...>`` so they stand out in a scan.
    Slugs not present in the registry get a trailing ``!``.
    """
    policy = _policy()
    registry = set(policy["languages"])
    rows: list[tuple[str, str]] = []
    for country in _country_dirs():
        rel = country.relative_to(ROOT)
        readme = country / "README.md"
        if not readme.is_file():
            rows.append((str(rel), "<no README>"))
            continue
        declared = parse_readme_languages(readme.read_text(encoding="utf-8"))
        if not declared:
            rows.append((str(rel), "<no Language(s) line>"))
            continue
        flagged = [d if d in registry else f"{d}!" for d in declared]
        rows.append((str(rel), ", ".join(flagged)))
    width = max((len(r[0]) for r in rows), default=0)
    for path, langs in rows:
        print(f"{path:<{width}}  {langs}")
    if any("!" in langs or langs.startswith("<") for _, langs in rows):
        print()
        print(
            "Legend: <...> = README problem; trailing `!` = language "
            "not in data/language_policy.yaml"
        )
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="L1b language policy validator. Reads data/language_policy.yaml.",
    )
    parser.add_argument(
        "files", nargs="*",
        help="files to validate; omit to walk regions/",
    )
    parser.add_argument(
        "--list-repo-languages", action="store_true",
        help="print the languages registered in data/language_policy.yaml",
    )
    parser.add_argument(
        "--list-country-languages", action="store_true",
        help="print each country's declared languages from its README",
    )
    parser.add_argument(
        "--check-readmes-only", action="store_true",
        help="only run the registry cross-check on every country README; "
             "skip per-file language detection",
    )
    parser.add_argument(
        "--explain", action="store_true",
        help="diagnostic mode: dump every detected language span per "
             "section for the given files. Useful for LLM-driven authoring "
             "and debugging 'why does my file fail/pass'.",
    )
    args = parser.parse_args(argv)

    try:
        policy = _policy()
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    if args.list_repo_languages:
        return _cmd_list_repo_languages()
    if args.list_country_languages:
        return _cmd_list_country_languages()

    if args.explain:
        if not args.files:
            print(
                "ERROR: --explain requires one or more file arguments.",
                file=sys.stderr,
            )
            return 2
        for arg in args.files:
            for line in explain(Path(arg)):
                print(line)
        return 0

    # README registry cross-check runs in all detection modes -- it
    # catches the silent-fallback bug that motivated Phase 1 and costs
    # nothing.
    readme_issues = _readme_registry_violations(policy)

    if args.check_readmes_only:
        for issue in readme_issues:
            print(f"FAIL {issue.error}")
            if issue.verdict:
                print(f"  verdict: {issue.verdict}")
        return 1 if readme_issues else 0

    detector = _build_detector(policy)
    if detector is None:
        print(
            "SKIP: `lingua` not installed; L1b language detection skipped. "
            "Run `pip install -r tests/requirements.txt` to enable.",
            file=sys.stderr,
        )
        for issue in readme_issues:
            print(f"FAIL {issue.error}")
            if issue.verdict:
                print(f"  verdict: {issue.verdict}")
        return 1 if readme_issues else 0

    if args.files:
        targets = [Path(a) for a in args.files]
    else:
        targets = sorted(
            p for p in (ROOT / "regions").rglob("*.md")
            if ".git" not in p.parts
        )

    all_issues: list[Issue] = list(readme_issues)
    for file_path in targets:
        if not file_path.is_file():
            continue
        try:
            text = file_path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        allowed = _resolve_allowed_languages(file_path, policy)
        exceptions = _exceptions_for(file_path)
        violations = _check_content(text, allowed, policy, detector, exceptions)
        for section, lang, snippet, words in violations:
            all_issues.append(
                _violation_issue(file_path, section, lang, snippet, words, allowed)
            )

    allowed_str = " and ".join(sorted(policy["languages"]))
    if all_issues:
        print(f"Language policy ({allowed_str}) failed:\n")
        for issue in all_issues:
            print(f"FAIL {issue.error}")
            if issue.verdict:
                print(f"  verdict: {issue.verdict}")
        return 1
    print(f"OK: {len(targets)} file(s) passed language policy ({allowed_str})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
