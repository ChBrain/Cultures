"""Shared pytest hooks for local reproducibility hints.

This keeps local repro guidance centralized instead of embedding custom
messages in individual test cases.
"""
from __future__ import annotations

from pathlib import Path


def _nodeid_to_local_cmd(nodeid: str) -> str:
    """Build a generic local repro command from a pytest nodeid."""
    parts = nodeid.split("::")
    rel_file = parts[0]
    test_name = parts[1] if len(parts) > 1 else ""
    # Drop parametrization suffix for a stable -k expression.
    test_name = test_name.split("[", 1)[0]

    if test_name:
        return f'python -m pytest -q {rel_file} -k "{test_name}"'
    return f"python -m pytest -q {rel_file}"


def pytest_terminal_summary(terminalreporter, exitstatus, config):  # type: ignore[no-untyped-def]
    """Emit one local repro command per failed test at the end of the run."""
    failed = terminalreporter.stats.get("failed", [])
    if not failed:
        return

    tr = terminalreporter
    tr.write_sep("-", "Local Repro Hints")

    seen: set[str] = set()
    for report in failed:
        nodeid = getattr(report, "nodeid", "")
        if not nodeid or nodeid in seen:
            continue
        seen.add(nodeid)

        cmd = _nodeid_to_local_cmd(nodeid)
        tr.write_line(f"{nodeid}")
        tr.write_line(f"  Local repro: {cmd}")

        # PR-scoped orphan checks require --khai-files context.
        if "tests/test_links.py::test_no_orphans" in nodeid:
            tr.write_line(
                '  Note: add --khai-files="<space-separated regions/*.md paths>"'
            )
