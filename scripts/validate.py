#!/usr/bin/env python3
"""Cultures validator orchestrator.

Schedules validation as a linear chain (L1a → L1b → L4):

  L1a: General file format (UTF-8 no BOM, ASCII filenames, no em-dash)
  L1b: English-only language policy
  L4: Culture completeness (per-country minimums)

L2 (section structure) and L3 (link integrity) are now handled by CI-only
pytest jobs (khai component tests + cultures-sections + khai-links + cultures-links).

Each layer blocks subsequent layers on failure. This script provides a single
entry point for local validation, but CI jobs call validators individually
to preserve job visibility in GitHub Actions.

Exit status:
  0 if every file passes all layers, 1 if any fail.

Usage:
  scripts/validate.py                # validates every regions/**/*.md (audit mode)
  scripts/validate.py FILE...        # validates only the given files (CI mode)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "tests"))

from findings import Issue
import validate_general
import validate_language
import validate_culture

ROOT = HERE.parent


def find_all_content_files() -> list[str]:
    """Discover all regions/**/*.md files (audit mode)."""
    files = []
    for p in sorted((ROOT / "regions").rglob("*.md")):
        if ".git" not in p.parts:
            files.append(str(p.relative_to(ROOT)))
    return files


def run_layer(name: str, module, files: list[str]) -> tuple[int, list[Issue]]:
    """Run a single validation layer.
    
    Args:
        name: Display name (e.g., "L1a")
        module: Validator module with validate() function
        files: List of file paths to validate (relative or absolute)
    
    Returns:
        (exit_code, findings_list)
        - exit_code 0 if all pass, 1 if any fail
        - findings_list: all Issue objects from this layer
    """
    try:
        all_findings = []
        failed_count = 0
        
        # Convert string paths to Path objects
        file_paths = []
        for file_arg in files:
            path = Path(file_arg)
            if not path.is_absolute():
                path = ROOT / path
            file_paths.append(path)
        
        # Validators have different signatures:
        # - validate_general, validate_language, validate_sections: validate(path: Path)
        # - validate_links, validate_culture: validate(changed_files: list[Path] | None)
        
        if "links" in module.__name__ or "culture" in module.__name__:
            # These validators accept a list of changed files
            issues = module.validate(file_paths if file_paths else None)
            all_findings.extend(issues)
            if issues:
                failed_count = 1
                for issue in issues:
                    print(f"  {issue.error}")
        else:
            # These validators accept a single path at a time
            for path in file_paths:
                issues = module.validate(path)
                all_findings.extend(issues)
                if issues:
                    failed_count += 1
                    for issue in issues:
                        print(f"  {path.name}: {issue.error}")
        
        if failed_count > 0:
            return 1, all_findings
        return 0, all_findings
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1, []


def main():
    parser = argparse.ArgumentParser(
        description="Validate all Cultures regions/**/*.md files"
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Files to validate (if omitted, validates all regions/**/*.md)"
    )
    args = parser.parse_args()
    
    # Determine file scope
    if args.files:
        files = args.files
    else:
        files = find_all_content_files()
    
    if not files:
        print("No files to validate.")
        return 0
    
    print(f"Validating {len(files)} file(s)...")
    print()
    
    # Run validation chain (L1a → L1b → L4)
    # Note: L0 (stamp gate) only runs in CI (see .github/workflows/validate.yml)
    # Note: L2 (sections) and L3 (links) are CI-only via khai pytest jobs

    all_passed = True
    layers = [
        ("L1a - General format", validate_general),
        ("L1b - English-only language", validate_language),
        ("L4 - Culture completeness", validate_culture),
    ]
    
    for layer_name, module in layers:
        print(f"[{layer_name}]")
        exit_code, findings = run_layer(layer_name, module, files)
        
        if exit_code != 0:
            all_passed = False
            print(f"  FAILED ({len(findings)} issue(s))")
        else:
            print(f"  OK")
        print()
    
    if all_passed:
        print("[OK] All validation layers passed")
        return 0
    else:
        print("[FAILED] Validation failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
