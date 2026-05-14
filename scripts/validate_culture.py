#!/usr/bin/env python3
"""L4 validator compatibility shim.

The old `tests/validate_culture.py` script was removed during pytest migration,
but `scripts/validate.py` still imports `validate_culture` and expects a
`validate(changed_files)` function.

This shim restores that interface and delegates L4 completeness checks to the
pytest-based suite in `tests/test_completeness.py`.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from findings import Issue

ROOT = Path(__file__).resolve().parent.parent


def _run_pytest() -> subprocess.CompletedProcess[str]:
    """Run the pytest-based completeness checks."""
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "tests/test_completeness.py",
    ]
    return subprocess.run(
        cmd,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def _extract_failures(pytest_output: str) -> list[str]:
    """Extract concise failure lines from pytest output."""
    failures: list[str] = []

    # Typical pytest assertion line:
    # E       AssertionError: country: expected ...
    for line in pytest_output.splitlines():
        match = re.search(r"AssertionError:\s*(.+)$", line)
        if match:
            failures.append(match.group(1).strip())

    return failures


def validate(changed_files: list[Path] | None = None) -> list[Issue]:
    """Validate L4 completeness.

    The `changed_files` parameter is accepted to preserve the original API
    expected by the orchestrator.
    """
    result = _run_pytest()

    if result.returncode == 0:
        return []

    issues: list[Issue] = []

    for msg in _extract_failures(result.stdout + "\n" + result.stderr):
        issues.append(Issue(error=f"L4 completeness: {msg}"))

    if not issues:
        issues.append(
            Issue(
                error=(
                    "L4 completeness failed via tests/test_completeness.py. "
                    "Run `python -m pytest -q tests/test_completeness.py` "
                    "for details."
                )
            )
        )

    return issues
