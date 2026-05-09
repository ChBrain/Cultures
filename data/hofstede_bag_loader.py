#!/usr/bin/env python3
"""Load Hofstede bags from per-country files with controlled fallback.

Per-country routing for Hofstede Bag Infrastructure v2.0:

1. Try `regions/<region>/<country>/hofstede_bag_<lang>.yaml` (multilingual).
2. Then `regions/<region>/<country>/hofstede_bag.yaml` (single-language).
3. Fall back to legacy `data/hofstede_keywords.py` only if the country has
   NOT been migrated (i.e. has no entry in `data/hofstede_bag_locks.yaml`).
   Migrated countries fail loud on parse errors or missing bags — the lock
   index is the migration tracker, and a missing bag for a migrated country
   means the contract was violated.

Failure modes:
- Locked country, bag missing            → RuntimeError (loud)
- Locked country, bag malformed          → RuntimeError (loud)
- Locked country, bag schema invalid     → RuntimeError (loud)
- Unlocked country, bag malformed        → stderr warning + legacy fallback
- Unlocked country, bag absent           → silent legacy fallback
- Unlocked country, fallback=False, no bag → ValueError

The previous version of this module silently swallowed every YAML parse
error via `except Exception: pass`, masking malformed bags. That's the
LLM-changes-the-rules vector at the validator level. This version narrows
the exception types and reports through stderr so failures are visible.

Usage:
  from data.hofstede_bag_loader import load_bag_for_country_file, load_bag_for_language
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import yaml
from data.hofstede_keywords import DIMENSION_KEYWORDS_BY_LANGUAGE


# Anchor at this file so paths work regardless of CWD.
_REPO_ROOT = Path(__file__).resolve().parent.parent
_LOCKS_FILE = _REPO_ROOT / "data" / "hofstede_bag_locks.yaml"

DIMENSIONS = ("PDI", "IDV", "UAI", "MAS", "LTO", "IND")


# ---------------------------------------------------------------------------
# Lock index helpers
# ---------------------------------------------------------------------------

def _load_locks_index() -> dict[str, str]:
    """Read `data/hofstede_bag_locks.yaml`. Returns `{path: sha256}` or `{}`.

    Returns empty dict if the file is absent or unparseable. The lock file's
    integrity is the SHA test's responsibility; the loader only consults it
    for migration-tracking purposes (which countries have been migrated).
    """
    if not _LOCKS_FILE.exists():
        return {}
    try:
        with _LOCKS_FILE.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        sys.stderr.write(
            f"WARNING: {_LOCKS_FILE} unparseable ({exc}); treating as empty.\n"
        )
        return {}
    if not isinstance(data, dict):
        return {}
    locks = data.get("locks", {})
    return locks if isinstance(locks, dict) else {}


def _country_has_lock(country_folder: Path) -> bool:
    """True if any bag path under this country folder has a lock entry."""
    locks = _load_locks_index()
    if not locks:
        return False
    try:
        rel = country_folder.resolve().relative_to(_REPO_ROOT).as_posix()
    except ValueError:
        # country_folder isn't under the repo root; can't compare.
        return False
    prefix = f"{rel}/"
    return any(k.startswith(prefix) for k in locks.keys())


# ---------------------------------------------------------------------------
# Bag file loading
# ---------------------------------------------------------------------------

class BagLoadError(Exception):
    """Per-country bag exists but is malformed or schema-invalid."""


def _validate_bag_schema(bag: object) -> dict:
    """Confirm `bag` is dict-of-dict-of-list-of-string per Strategy v2.

    Raises BagLoadError on any structural problem. Returns the bag dict
    cast to its expected shape on success.
    """
    if not isinstance(bag, dict):
        raise BagLoadError(
            f"`bags` is {type(bag).__name__}, expected dict of dimensions"
        )
    for dim in DIMENSIONS:
        if dim not in bag:
            raise BagLoadError(f"missing dimension `{dim}` in bags")
        polarities = bag[dim]
        if not isinstance(polarities, dict):
            raise BagLoadError(
                f"`bags.{dim}` is {type(polarities).__name__}, expected dict"
            )
        for pol in ("high", "low"):
            if pol not in polarities:
                raise BagLoadError(f"missing polarity `bags.{dim}.{pol}`")
            words = polarities[pol]
            if not isinstance(words, list):
                raise BagLoadError(
                    f"`bags.{dim}.{pol}` is {type(words).__name__}, expected list"
                )
            for i, w in enumerate(words):
                if not isinstance(w, str):
                    raise BagLoadError(
                        f"`bags.{dim}.{pol}[{i}]` is {type(w).__name__}, expected str"
                    )
    return bag


def _read_bag_file(path: Path) -> dict:
    """Load and schema-validate a single bag YAML file.

    Raises BagLoadError on parse failure, missing `bags` key, or schema
    violation. Caller decides whether to fall back or fail loud.
    """
    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except (yaml.YAMLError, OSError) as exc:
        raise BagLoadError(f"cannot read {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise BagLoadError(f"{path}: top-level YAML is not a mapping")
    if "bags" not in data:
        raise BagLoadError(f"{path}: missing top-level `bags` key")
    return _validate_bag_schema(data["bags"])


def _try_load_country_bag(
    country_folder: Path, language: str,
) -> tuple[Optional[dict], Optional[BagLoadError]]:
    """Attempt to load a per-country bag. Returns (bag, error).

    Lookup order:
      1. hofstede_bag_<language>.yaml (multilingual country)
      2. hofstede_bag.yaml (single-language country)

    Both forms returns (bag, None) on success or (None, error) on first
    failure. If both files exist, the language-specific one wins and a
    warning is emitted so the conflict is visible.

    Returns (None, None) if no bag file exists in the folder.
    """
    lang_path = country_folder / f"hofstede_bag_{language}.yaml"
    generic_path = country_folder / "hofstede_bag.yaml"

    if lang_path.exists() and generic_path.exists():
        sys.stderr.write(
            f"WARNING: both {lang_path.name} and {generic_path.name} exist in "
            f"{country_folder}; using language-specific.\n"
        )

    target = lang_path if lang_path.exists() else (
        generic_path if generic_path.exists() else None
    )
    if target is None:
        return None, None
    try:
        return _read_bag_file(target), None
    except BagLoadError as exc:
        return None, exc


def _find_country_folder(file_path: Path) -> Optional[Path]:
    """Extract `regions/<region>/<country>/` from a file path."""
    parts = file_path.parts
    for i, part in enumerate(parts):
        if part == "regions" and i + 2 < len(parts):
            country_folder = Path(*parts[: i + 3])
            if country_folder.exists() and country_folder.is_dir():
                return country_folder
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def _legacy_keywords(language: str) -> dict:
    """Fetch legacy DIMENSION_KEYWORDS_BY_LANGUAGE entry, falling back to en."""
    if language in DIMENSION_KEYWORDS_BY_LANGUAGE:
        return DIMENSION_KEYWORDS_BY_LANGUAGE[language]
    return DIMENSION_KEYWORDS_BY_LANGUAGE.get("en", {})


def _resolve(
    country_folder: Optional[Path],
    language: str,
    fallback: bool,
    *,
    target_label: str,
) -> dict:
    """Shared logic for both public entry points."""
    bag: Optional[dict] = None
    parse_error: Optional[BagLoadError] = None

    if country_folder and country_folder.exists():
        bag, parse_error = _try_load_country_bag(country_folder, language)

    if bag is not None:
        return bag  # already validated by _read_bag_file

    # Per-country bag missing or unparseable. Lock check decides severity.
    if country_folder and _country_has_lock(country_folder):
        if parse_error:
            raise RuntimeError(
                f"Locked country {country_folder} has malformed bag: "
                f"{parse_error}. The lock index says this bag must exist "
                f"and parse cleanly. Fix the bag or unlock the country."
            )
        raise RuntimeError(
            f"Locked country {country_folder} has no bag YAML for language "
            f"`{language}`. The lock index says this country has been "
            f"migrated; the per-country bag is missing. Restore it or "
            f"unlock the country."
        )

    # Unlocked country: warn on parse error, then optionally fall back.
    if parse_error is not None:
        sys.stderr.write(
            f"WARNING: {parse_error}. Falling back to legacy keywords for "
            f"language `{language}`.\n"
        )

    if fallback:
        return _legacy_keywords(language)

    raise ValueError(
        f"No per-country bag found for {target_label} (language={language}) "
        f"and fallback=False"
    )


def load_bag_for_country_file(
    file_path: Path,
    language: str,
    fallback: bool = True,
) -> dict:
    """Load Hofstede bag for a specific file in a country folder.

    Args:
        file_path: Path to a `culture_*.md` file (or any file in a country folder).
        language: Detected language code (`en`, `de`, `nl`, `da`, …).
        fallback: If True, fall back to legacy dict for unmigrated countries.

    Returns:
        Dict mapping `dimension -> {high: [...], low: [...]}`.

    Raises:
        RuntimeError if the country is in the lock index but its bag is missing
            or malformed.
        ValueError if `fallback=False` and no per-country bag exists.
    """
    country_folder = _find_country_folder(file_path)
    return _resolve(
        country_folder, language, fallback, target_label=str(file_path),
    )


def load_bag_for_language(
    language: str,
    country_folder: Optional[Path] = None,
    fallback: bool = True,
) -> dict:
    """Load Hofstede bag for a language, optionally scoped to a country folder.

    Args:
        language: Detected language code.
        country_folder: If provided, try the per-country bag there first.
        fallback: If True, fall back to legacy dict for unmigrated countries.

    Returns:
        Dict mapping `dimension -> {high: [...], low: [...]}`.

    Raises:
        RuntimeError if the country is in the lock index but its bag is missing
            or malformed.
        ValueError if `fallback=False` and no per-country bag exists.
    """
    return _resolve(
        country_folder, language, fallback,
        target_label=f"language={language}, country_folder={country_folder}",
    )
