#!/usr/bin/env python3
"""Hofstede bag validation: denylist conflicts and word collisions.

Checks that:
1. No word in a bag also appears in the country denylist
2. No word appears in multiple dimensions (collisions)
3. Each dimension has exactly 10 words (5 high + 5 low)

Exit status:
  0 if all bags pass validation
  1 if any bag has denylist conflicts, collisions, or wrong word count

Usage:
  tests/validate_hofstede_bag_denylist.py           # all countries
  tests/validate_hofstede_bag_denylist.py COUNTRY   # single country
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))

import yaml
from findings import Issue

HOFSTEDE_DIMENSIONS = ["PDI", "IDV", "UAI", "MAS", "LTO", "IND"]


def find_bag_files() -> list[Path]:
    """Find all hofstede_bag.yaml files."""
    bags = []
    regions = ROOT / "regions"
    if not regions.is_dir():
        return []
    for region_dir in sorted(regions.iterdir()):
        if not region_dir.is_dir() or region_dir.name.startswith("."):
            continue
        for country_dir in sorted(region_dir.iterdir()):
            if not country_dir.is_dir() or country_dir.name.startswith("."):
                continue
            bag_file = country_dir / "hofstede_bag.yaml"
            if bag_file.exists():
                bags.append(bag_file)
    return bags


def validate_bag(bag_path: Path) -> list[Issue]:
    """Validate a single hofstede_bag.yaml file."""
    issues = []

    try:
        with open(bag_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        return [Issue(
            error=f"{bag_path}: BAG_LOAD_FAILED - Could not load bag: {e}"
        )]

    country = data.get("country", "unknown")
    denylist = set(data.get("denylist", []))
    bags = data.get("bags", {})

    # Collect all words from all bags
    all_bag_words = {}  # word -> [dimensions it appears in]

    for dim in HOFSTEDE_DIMENSIONS:
        if dim not in bags:
            continue

        dim_data = bags[dim]
        high_count = 0
        low_count = 0

        if "high" in dim_data:
            words = dim_data["high"]
            if not isinstance(words, list):
                issues.append(Issue(
                    error=f"{bag_path}: bags.{dim}.high must be a list, got {type(words)}"
                ))
            else:
                high_count = len(words)
                for word in words:
                    # Check denylist conflict
                    if word in denylist:
                        issues.append(Issue(
                            error=f"{bag_path}: DENYLIST_CONFLICT - Word '{word}' in bags.{dim}.high AND in denylist"
                        ))

                    # Track word for collision detection
                    if word not in all_bag_words:
                        all_bag_words[word] = []
                    all_bag_words[word].append(dim)

        if "low" in dim_data:
            words = dim_data["low"]
            if not isinstance(words, list):
                issues.append(Issue(
                    error=f"{bag_path}: bags.{dim}.low must be a list, got {type(words)}"
                ))
            else:
                low_count = len(words)
                for word in words:
                    # Check denylist conflict
                    if word in denylist:
                        issues.append(Issue(
                            error=f"{bag_path}: DENYLIST_CONFLICT - Word '{word}' in bags.{dim}.low AND in denylist"
                        ))

                    # Track word for collision detection
                    if word not in all_bag_words:
                        all_bag_words[word] = []
                    all_bag_words[word].append(dim)

        # Check high/low counts
        if high_count != 10:
            issues.append(Issue(
                error=f"{bag_path}: WORD_COUNT_MISMATCH - Dimension {dim} high has {high_count} words (expected 10)"
            ))
        if low_count != 10:
            issues.append(Issue(
                error=f"{bag_path}: WORD_COUNT_MISMATCH - Dimension {dim} low has {low_count} words (expected 10)"
            ))

    # Check for within-country collisions
    for word, dims in all_bag_words.items():
        if len(dims) > 1:
            issues.append(Issue(
                error=f"{bag_path}: WITHIN_COUNTRY_COLLISION - Word '{word}' in multiple dimensions: {', '.join(sorted(set(dims)))}"
            ))

    return issues


def main():
    """Validate all or specified bags."""
    if len(sys.argv) > 1:
        # Validate specific country
        target = sys.argv[1].lower()
        bags = [p for p in find_bag_files() if target in p.parts]
    else:
        bags = find_bag_files()

    if not bags:
        print("No bags found to validate")
        return 0

    all_issues = []
    for bag_path in bags:
        issues = validate_bag(bag_path)
        all_issues.extend(issues)
        if issues:
            print(f"\n❌ {bag_path.parent.name}")
            for issue in issues:
                print(f"   {issue.error}")
        else:
            print(f"✓ {bag_path.parent.name}")

    if all_issues:
        print(f"\n\n>>> BAG DENYLIST VALIDATION FAILED")
        print(f"FAIL {len(all_issues)} issue(s) across {len(bags)} bag(s)")
        return 1

    print(f"\n✓ All {len(bags)} bags passed denylist validation")
    return 0


if __name__ == "__main__":
    sys.exit(main())
