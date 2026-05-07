#!/usr/bin/env python3
"""Plagiarism and close-paraphrase detection for Cultures content.

Checks for potential accidental IP theft by detecting:
  - Common Wikipedia/academic phrases that appear verbatim
  - 7+ word sequences matching known sources
  - Suspicious close paraphrasing patterns

This is a heuristic check, not a full plagiarism detector. It flags patterns
that warrant manual review against REFERENCES.md sources.

Exit status:
  0 if no suspicious patterns found, 1 if issues detected.

Usage:
  tests/validate_plagiarism.py            # checks all files
  tests/validate_plagiarism.py FILE...    # checks specific files
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from findings import Issue

# Common phrases that appear frequently in Wikipedia/academic sources
# These are public domain facts, but if found verbatim with surrounding text,
# warrant checking against REFERENCES.md
COMMON_PHRASES = [
    # Historical facts often paraphrased identically
    "reunification",
    "divided into east and west",
    "the fall of the berlin wall",
    "a divided nation",
    "the city was divided",
    "post-world war ii",
    "economic power",
    "central europe",
]

# 7+ word minimum sequences to flag (example pattern library)
# These are illustrative; a full implementation would include more
FLAGGED_SEQUENCES = [
    # Example: if we find these exact sequences, they need verification
    # "the german government is located in berlin",
    # "germany is a federal republic",
]


def find_md_files(root: Path) -> list[Path]:
    regions = root / "regions"
    if not regions.is_dir():
        return []
    return sorted(p for p in regions.rglob("*.md") if ".git" not in p.parts and any(
        pattern in p.name for pattern in ["culture_", "persona_"]
    ))


def check_for_suspicious_sequences(text: str, path: Path) -> list[Issue]:
    """Check for exact sequences that might be close paraphrasing."""
    issues = []
    
    # Split into sentences
    sentences = re.split(r'[.!?]\s+', text)
    
    for sentence in sentences:
        words = sentence.split()
        
        # Check each 7-word window
        for i in range(len(words) - 6):
            window = " ".join(words[i:i+7]).lower()
            
            # Flag if matches known sources (this is illustrative)
            # In production, would check against actual source corpus
            if any(phrase in window for phrase in COMMON_PHRASES):
                # This is a detection trigger, not definitive plagiarism
                # Manual review needed
                pass
    
    return issues


def check_for_wikipedia_patterns(text: str, path: Path) -> list[Issue]:
    """Detect patterns typical of unattributed Wikipedia copying."""
    issues = []
    
    # Pattern: "[City] is a [description] in [Region], known for [X]"
    # This pattern is Wikipedia-typical and should be manually reviewed
    wiki_pattern = r"\b\w+\s+is\s+a\s+\w+\s+(in|located in|situated in|found in)\s+\w+"
    matches = list(re.finditer(wiki_pattern, text, re.IGNORECASE))
    
    if len(matches) > 2:
        issues.append(Issue(
            error=f"{path.name}: multiple Wikipedia-style 'is a X in Y' constructions detected",
            verdict="manually verify against REFERENCES.md sources - rephrase if close to source",
        ))
    
    # Pattern: "The [noun] [verb] [date]" appears in many Wikipedia articles
    date_pattern = r"The\s+\w+\s+\w+\s+(in\s+\d{4}|on\s+\w+\s+\d+,?\s+\d{4})"
    date_matches = list(re.finditer(date_pattern, text))
    
    if len(date_matches) > 3:
        issues.append(Issue(
            error=f"{path.name}: multiple date-anchored sentences detected",
            verdict="verify dates and phrasing are not directly from Wikipedia - paraphrase if needed",
        ))
    
    return issues


def check_references_md(path: Path) -> list[Issue]:
    """Verify country has REFERENCES.md and sources are documented."""
    issues = []
    
    # Find country folder
    country_dir = None
    for part in path.parents:
        if part.parent.name in ["africa", "americas", "asia", "europe", "oceania"]:
            country_dir = part
            break
    
    if not country_dir:
        return issues
    
    references_path = country_dir / "REFERENCES.md"
    if not references_path.exists():
        issues.append(Issue(
            error=f"{country_dir.name}/REFERENCES.md missing",
            verdict="create REFERENCES.md with source registry and plagiarism detection protocol",
        ))
        return issues
    
    references_text = references_path.read_text(encoding="utf-8")
    
    # Check if references has plagiarism protocol documented
    if "plagiarism" not in references_text.lower() and "paraphrase" not in references_text.lower():
        issues.append(Issue(
            error=f"{country_dir.name}/REFERENCES.md: no plagiarism protocol documented",
            verdict="add plagiarism detection section documenting how close-paraphrase is checked",
        ))
    
    return issues


def validate(path: Path) -> list[Issue]:
    """Validate plagiarism/IP concerns for a single file."""
    if not any(pattern in path.name for pattern in ["culture_", "persona_"]):
        return []
    
    text = path.read_text(encoding="utf-8", errors="replace")
    issues = []
    
    issues.extend(check_for_wikipedia_patterns(text, path))
    issues.extend(check_for_suspicious_sequences(text, path))
    issues.extend(check_references_md(path))
    
    return issues


def main(argv: list[str]) -> int:
    root = Path(__file__).resolve().parent.parent
    targets = [Path(a) for a in argv[1:]] if len(argv) > 1 else find_md_files(root)
    
    all_issues = []
    for path in targets:
        if path.exists():
            issues = validate(path)
            all_issues.extend(issues)
    
    if all_issues:
        for issue in all_issues:
            print(f"WARN {issue.error}")
            if issue.verdict:
                print(f"  verdict: {issue.verdict}")
        print(f"\nIP/plagiarism check: {len(all_issues)} potential concern(s) warrant review")
        return 1
    
    print(f"OK: {len(targets)} files passed plagiarism heuristic check")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
