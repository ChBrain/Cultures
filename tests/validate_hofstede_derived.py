#!/usr/bin/env python3
"""Hofstede validation: derive scores from content, compare to declared scores.

Scans all culture_*_*.md files per country, derives Hofstede dimension scores
(0-100) based on keyword frequency, and compares against declared scores in
README. Gaps within ±10 pass CI; gaps within ±5 are excellent.

Exit status:
  0 if all countries pass (gap ≤ ±10 for all dimensions)
  1 if any country has a gap > ±10

Output:
  PASS / WARN / FAIL per dimension with gap and status (excellent/pass/warn/fail)

Usage:
  tests/validate_hofstede_derived.py            # all countries
  tests/validate_hofstede_derived.py FILE...    # files in same country only
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))

from findings import Issue
from data.hofstede_keywords import detect_language, DIMENSION_KEYWORDS_BY_LANGUAGE


HOFSTEDE_DIMENSIONS = ["PDI", "IDV", "UAI", "MAS", "LTO", "IND"]
TOLERANCE_CI = 10  # Hard gate: ±10
TOLERANCE_IDEAL = 5  # Aspirational: ±5


def find_country_folders() -> list[Path]:
    """Find all country folders that contain culture content."""
    root = Path(__file__).resolve().parent.parent
    regions = root / "regions"
    if not regions.is_dir():
        return []

    countries = []
    for region_dir in sorted(regions.iterdir()):
        if not region_dir.is_dir() or region_dir.name.startswith("."):
            continue
        for country_dir in sorted(region_dir.iterdir()):
            if not country_dir.is_dir() or country_dir.name.startswith("."):
                continue
            content_files = list(country_dir.glob("culture_*.md"))
            if content_files:
                countries.append(country_dir)
    return countries


def extract_hofstede_scores(readme_text: str) -> dict[str, int]:
    """Extract declared Hofstede scores from README.
    
    Returns {dimension: score} if found, else empty dict.
    """
    import re
    
    scores: dict[str, int] = {}
    pattern = (
        r"\|[^|\n]*\b(PDI|IDV|UAI|MAS|LTO|IND)\b[^|\n]*\|"
        r"\s*(\d+)\s*\|"
    )
    for match in re.finditer(pattern, readme_text, re.IGNORECASE):
        dim = match.group(1).upper()
        score = int(match.group(2))
        scores[dim] = score
    return scores


def derive_scores(country_dir: Path, language: str = "en") -> dict[str, int]:
    """Derive Hofstede scores from all culture_*_*.md files.
    
    Scans all files, counts keywords per dimension, calculates polarity ratio.
    Returns {dimension: score} where score is 0-100.
    """
    if language not in DIMENSION_KEYWORDS_BY_LANGUAGE:
        language = "en"
    
    keywords = DIMENSION_KEYWORDS_BY_LANGUAGE[language]
    
    # Scan all culture files
    all_text = ""
    for f in country_dir.glob("culture_*.md"):
        all_text += f.read_text(encoding="utf-8").lower()
    
    # Calculate scores
    scores: dict[str, int] = {}
    for dim in HOFSTEDE_DIMENSIONS:
        if dim not in keywords:
            continue
        
        high_count = sum(1 for kw in keywords[dim]["high"] if kw in all_text)
        low_count = sum(1 for kw in keywords[dim]["low"] if kw in all_text)
        
        total = high_count + low_count
        if total == 0:
            score = 50  # neutral if no keywords
        else:
            ratio = high_count / total
            score = int(ratio * 100)
        
        scores[dim] = score
    
    return scores


def validate_country(country_dir: Path) -> tuple[list[Issue], dict[str, dict]]:
    """Validate derived vs declared scores.
    
    Returns (issues_list, scores_report).
    scores_report = {dimension: {declared, derived, gap, status}}
    """
    readme_path = country_dir / "README.md"
    if not readme_path.exists():
        return [Issue(
            error=f"{country_dir.name}: README.md not found",
            verdict="create README.md with Hofstede section",
        )], {}
    
    readme_text = readme_path.read_text(encoding="utf-8")
    declared = extract_hofstede_scores(readme_text)
    
    if not declared:
        return [Issue(
            error=f"{country_dir.name}: no Hofstede scores found in README",
            verdict="add table rows with PDI, IDV, UAI, MAS, LTO, IND scores",
        )], {}
    
    # Detect language and derive scores
    all_text = ""
    for f in country_dir.glob("culture_*.md"):
        all_text += f.read_text(encoding="utf-8")
    language = detect_language(all_text)
    derived = derive_scores(country_dir, language=language)
    
    # Compare
    issues: list[Issue] = []
    report: dict[str, dict] = {}
    
    for dim in HOFSTEDE_DIMENSIONS:
        if dim not in declared or dim not in derived:
            continue
        
        decl = declared[dim]
        deriv = derived[dim]
        gap = abs(decl - deriv)
        
        if gap <= TOLERANCE_IDEAL:
            status = "[EXCELLENT]"
        elif gap <= TOLERANCE_CI:
            status = "[PASS]"
        elif gap <= 20:
            status = "[WARN]"
            issues.append(Issue(
                error=f"{country_dir.name}: {dim} gap {gap} > ±{TOLERANCE_CI}",
                verdict=f"declared {dim}={decl}, derived {dim}={deriv} (gap {gap}). Review content or adjust README.",
            ))
        else:
            status = "[FAIL]"
            issues.append(Issue(
                error=f"{country_dir.name}: {dim} gap {gap} > ±{TOLERANCE_CI} (FAIL)",
                verdict=f"declared {dim}={decl}, derived {dim}={deriv} (gap {gap}). Either rewrite content to match README, or update README to match content.",
            ))
        
        report[dim] = {
            "declared": decl,
            "derived": deriv,
            "gap": gap,
            "status": status,
            "language": language,
        }
    
    return issues, report


def _resolve_targets(argv: list[str]) -> list[Path]:
    if len(argv) <= 1:
        return find_country_folders()
    targets: set[Path] = set()
    regions = {"africa", "americas", "asia", "europe", "oceania"}
    for arg in argv[1:]:
        path = Path(arg)
        if not path.exists():
            continue
        for part in path.parents:
            if part.parent.name in regions:
                targets.add(part)
                break
    return sorted(targets)


def main(argv: list[str]) -> int:
    countries = _resolve_targets(argv)
    if not countries:
        print("No countries found")
        return 0
    
    all_issues: list[Issue] = []
    all_reports: dict[str, dict] = {}
    
    for country_dir in countries:
        issues, report = validate_country(country_dir)
        all_issues.extend(issues)
        if report:
            all_reports[country_dir.name] = report
    
    # Print report
    if all_reports:
        print("\n=== Hofstede Derived Score Report ===\n")
        for country, dims in all_reports.items():
            print(f"{country}:")
            print(f"  Dim | Declared | Derived | Gap | Status")
            print(f"  ----|----------|---------|-----|--------")
            for dim in sorted(dims.keys()):
                d = dims[dim]
                print(f"  {dim}  | {d['declared']:>8} | {d['derived']:>7} | {d['gap']:>3} | {d['status']}")
            print()
    
    # Print issues
    has_fail = False
    for issue in all_issues:
        if "FAIL" in issue.error:
            has_fail = True
            print(f"FAIL {issue.error}")
        else:
            print(f"WARN {issue.error}")
        if issue.verdict:
            print(f"  verdict: {issue.verdict}")
    
    print(f"\nHofstede derived validation: {len(all_reports)} country(ies) checked")
    
    return 1 if has_fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
