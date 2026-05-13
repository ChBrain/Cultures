"""CLI smoke tests for tests/validate_pr_base.py.

Verifies the script that pr-gate.yml's base-branch-check job actually calls
exits with the right codes and prints the right messages. The routing logic
is pinned in test_validate_pr_base.py; these tests confirm the CLI wrapper
plumbs it correctly end-to-end.

Run: python -m pytest tests/test_validate_pr_base_cli.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "validate_pr_base.py"


def _run(head: str, base: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), head, base],
        capture_output=True, text=True, check=False,
    )


def test_cli_allowed_pair_exits_zero():
    result = _run("culture/germany", "culture/release")
    assert result.returncode == 0
    assert "OK" in result.stdout


def test_cli_disallowed_pair_exits_one():
    result = _run("culture/germany", "main")
    assert result.returncode == 1
    assert "not allowed" in result.stdout
    assert "culture/release" in result.stdout


def test_cli_main_as_head_exits_one():
    result = _run("main", "main")
    assert result.returncode == 1
    assert "not a valid PR head" in result.stdout


def test_cli_missing_args_exits_two():
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 2
