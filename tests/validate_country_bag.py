#!/usr/bin/env python3
"""Validate a single Hofstede country bag YAML before commit.

Standalone CLI for the migration workflow. Takes one or more bag YAML
paths and reports schema, quality, and denylist coherence in one pass:

  python3 tests/validate_country_bag.py regions/europe/denmark/hofstede_bag.yaml
  python3 tests/validate_country_bag.py /tmp/dk_draft.yaml      # out-of-repo path works too

Use this as a pre-flight before opening a `feat/culture-<name>-bag` PR:
- catches schema gaps the Skill might leave (missing `denylist:` field, etc.)
- catches the country-denylist-vs-bags coherence failure (denylist is for
  words NOT in any bag; words moved between bags during conflict resolution
  are kept, not denylisted)
- catches global denylist violations (data/hofstede_denylist.yaml)
- catches within-country collisions, off-by-N word counts, formatting drift

This is NOT a replacement for the pytest bag-integrity suite. The pytest
suite runs cross-country checks (opposing-polarity collisions across
countries, SHA lock matching, completeness) that this script does not.
Run pytest for full coverage:

  python3 -m pytest tests/test_hofstede_bag_*.py

Exit status:
  0 if every bag passes (warnings only)
  1 if any bag has errors
  2 if invoked incorrectly (no args)
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
GLOBAL_DENYLIST_FILE = REPO_ROOT / "data" / "hofstede_denylist.yaml"

DIMENSIONS: tuple[str, ...] = ("PDI", "IDV", "UAI", "MAS", "LTO", "IND")
POLARITIES: tuple[str, ...] = ("high", "low")
KEYWORDS_PER_POLARITY: int = 10
REQUIRED_FIELDS: tuple[str, ...] = (
    "country", "language", "parent", "hofstede_scores", "denylist", "bags",
)


def _load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def _load_global_denylist() -> set[str]:
    """Union of pronouns/function/polysemous from data/hofstede_denylist.yaml."""
    if not GLOBAL_DENYLIST_FILE.exists():
        return set()
    try:
        data = _load_yaml(GLOBAL_DENYLIST_FILE)
    except yaml.YAMLError:
        return set()
    words: set[str] = set()
    for category in ("pronouns_and_deictics", "function_words", "polysemous_english"):
        entries = data.get(category, [])
        if isinstance(entries, list):
            words.update(
                str(w).strip().lower()
                for w in entries
                if isinstance(w, str)
            )
    return words


def validate_bag(bag_path: Path) -> tuple[list[str], list[str]]:
    """Run all single-bag checks. Returns (errors, warnings)."""
    errors: list[str] = []
    warnings: list[str] = []

    if not bag_path.exists():
        return [f"file does not exist: {bag_path}"], []

    try:
        bag = _load_yaml(bag_path)
    except yaml.YAMLError as exc:
        return [f"YAML parse error: {exc}"], []

    if not bag:
        return ["top-level YAML is empty or not a mapping"], []

    # ---- Schema: required fields -------------------------------------------
    missing_fields = [f for f in REQUIRED_FIELDS if f not in bag]
    if missing_fields:
        errors.append(f"missing required field(s): {', '.join(missing_fields)}")
        # Short-circuit if the structural fields aren't present;
        # downstream checks would crash.
        return errors, warnings

    # ---- parent: null or string --------------------------------------------
    if bag["parent"] is not None and not isinstance(bag["parent"], str):
        errors.append(
            f"`parent` must be null or a string path, got "
            f"{type(bag['parent']).__name__}"
        )

    # ---- hofstede_scores ---------------------------------------------------
    scores = bag["hofstede_scores"]
    if not isinstance(scores, dict):
        errors.append("`hofstede_scores` must be a mapping")
    else:
        for dim in DIMENSIONS:
            if dim not in scores:
                errors.append(f"hofstede_scores missing `{dim}`")
                continue
            v = scores[dim]
            if not isinstance(v, int) or isinstance(v, bool) or not (0 <= v <= 100):
                errors.append(
                    f"hofstede_scores.{dim} = {v!r} (must be int 0-100)"
                )

    # ---- country denylist --------------------------------------------------
    denylist = bag["denylist"]
    country_denylist: set[str] = set()
    if not isinstance(denylist, list):
        errors.append("`denylist` must be a list (use `[]` if empty)")
    else:
        for i, w in enumerate(denylist):
            if not isinstance(w, str):
                errors.append(
                    f"denylist[{i}] is {type(w).__name__}, expected str"
                )
                continue
            if w != w.lower():
                errors.append(f"denylist[{i}] (`{w}`) must be lowercase")
            country_denylist.add(w.strip().lower())

    # ---- bags structure ----------------------------------------------------
    bags = bag["bags"]
    if not isinstance(bags, dict):
        errors.append("`bags` must be a mapping")
        return errors, warnings

    missing_dims = set(DIMENSIONS) - set(bags.keys())
    extra_dims = set(bags.keys()) - set(DIMENSIONS)
    if missing_dims:
        errors.append(f"bags missing dimensions: {sorted(missing_dims)}")
    if extra_dims:
        errors.append(f"bags has unexpected dimensions: {sorted(extra_dims)}")

    # ---- per-bag content + within-country collision tracking ---------------
    seen: dict[str, tuple[str, str]] = {}  # word -> (dim, polarity)

    for dim in DIMENSIONS:
        if dim not in bags:
            continue
        polarities = bags[dim]
        if not isinstance(polarities, dict):
            errors.append(f"bags.{dim} must be a mapping")
            continue
        for pol in POLARITIES:
            if pol not in polarities:
                errors.append(f"bags.{dim} missing `{pol}`")
                continue
            words = polarities[pol]
            if not isinstance(words, list):
                errors.append(f"bags.{dim}.{pol} must be a list")
                continue
            if len(words) != KEYWORDS_PER_POLARITY:
                errors.append(
                    f"bags.{dim}.{pol} has {len(words)} words "
                    f"(expected exactly {KEYWORDS_PER_POLARITY})"
                )
            for i, w in enumerate(words):
                if not isinstance(w, str):
                    errors.append(
                        f"bags.{dim}.{pol}[{i}] is {type(w).__name__}, expected str"
                    )
                    continue
                if not w or w != w.strip():
                    errors.append(
                        f"bags.{dim}.{pol}[{i}] (`{w}`) is empty or has "
                        f"leading/trailing whitespace"
                    )
                    continue
                if w != w.lower():
                    errors.append(
                        f"bags.{dim}.{pol}[{i}] (`{w}`) must be lowercase"
                    )
                wl = w.lower()

                # within-country collision (across all bags)
                if wl in seen:
                    prev_dim, prev_pol = seen[wl]
                    errors.append(
                        f"within-country collision: `{w}` appears in "
                        f"{dim}.{pol} AND {prev_dim}.{prev_pol}"
                    )
                else:
                    seen[wl] = (dim, pol)

                # country-denylist coherence: bag word ≠ denylist word
                if wl in country_denylist:
                    errors.append(
                        f"country-denylist conflict: `{w}` appears in "
                        f"bags.{dim}.{pol} AND in the country `denylist:` field. "
                        f"The denylist is for words NOT in any bag (rejected during "
                        f"bootstrap). Words moved between bags during conflict "
                        f"resolution are kept, not denylisted."
                    )

                # multi-word phrase warning (matcher fires only on verbatim)
                if " " in w:
                    warnings.append(
                        f"bags.{dim}.{pol}[{i}] (`{w}`) is multi-word — "
                        f"matcher uses \\bword\\b regex; only matches verbatim"
                    )

    # ---- global denylist (data/hofstede_denylist.yaml) ---------------------
    global_denylist = _load_global_denylist()
    if global_denylist:
        for word, (dim, pol) in seen.items():
            if word in global_denylist:
                errors.append(
                    f"global denylist violation: `{word}` in bags.{dim}.{pol} "
                    f"is in data/hofstede_denylist.yaml. Hard rule, no contextual "
                    f"override — the matcher does exact-word string comparison."
                )
    else:
        warnings.append(
            "global denylist (data/hofstede_denylist.yaml) not found or empty; "
            "skipping global check"
        )

    return errors, warnings


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: python3 tests/validate_country_bag.py <bag.yaml> [<bag.yaml>...]")
        print("       Validates schema, quality, and denylist coherence per bag.")
        return 2

    total_errors = 0
    total_warnings = 0
    for arg in argv[1:]:
        path = Path(arg)
        errors, warnings = validate_bag(path)

        rel = path
        try:
            rel = path.resolve().relative_to(REPO_ROOT)
        except ValueError:
            pass

        if not errors and not warnings:
            print(f"OK  {rel}")
            continue

        status = "FAIL" if errors else "OK  "
        print(f"{status} {rel}")
        for e in errors:
            print(f"  ERROR: {e}")
        for w in warnings:
            print(f"  WARN:  {w}")

        total_errors += len(errors)
        total_warnings += len(warnings)

    print()
    print(
        f"Summary: {total_errors} error(s), {total_warnings} warning(s) "
        f"across {len(argv) - 1} bag(s)"
    )
    return 1 if total_errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
