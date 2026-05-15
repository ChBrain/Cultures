"""CLI wrapper for Hofstede reference-score validation.

Pre-commit passes changed culture file paths to this script. The script
forwards them via PR-style env vars so tests/test_hofstede_reference.py
validates only affected countries.
"""
from __future__ import annotations

import os
import subprocess
import sys


def _norm(path: str) -> str:
    return path.replace("\\", "/")


def main() -> int:
    changed = [_norm(p) for p in sys.argv[1:] if p.strip()]
    if not changed:
        return 0

    env = os.environ.copy()
    env["PR_CHANGED_FILES"] = " ".join(changed)
    env["PR_DATA_CHANGED"] = "true" if any(p.startswith("data/") for p in changed) else "false"

    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "tests/test_hofstede_reference.py"],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )

    if result.returncode != 0:
        if result.stdout.strip():
            print(result.stdout.strip())
        if result.stderr.strip():
            print(result.stderr.strip())
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
