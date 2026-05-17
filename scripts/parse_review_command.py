#!/usr/bin/env python3
"""Parse `/review` PR-comment commands for the on-demand prose review workflow.

Pure parser: no filesystem, no network. The workflow checks file existence
and runs the review; this module only turns comment text into a structured
command so it can be unit-tested in isolation.

Command grammar (see .github/workflows/prose-review-on-comment.yml):
    /review help
    /review prose help
    /review prose changed
    /review prose file  <path>
    /review prose files <pathA> <pathB> ...

Usage:
    python3 scripts/parse_review_command.py "<comment body>"
    echo "<comment body>" | python3 scripts/parse_review_command.py

Prints a single JSON line: {"mode": ..., "files": [...], "errors": [...]}.
  mode    one of: none | help | changed | file | files
  files   explicit culture_*.md paths (for mode file/files)
  errors  human-readable rejection messages; non-empty means do not run
Exits 0 always.
"""
from __future__ import annotations

import json
import re
import sys

# Mirrors the changed-file filter in prose-review.yml.
CULTURE_PATH_RE = re.compile(r"^regions/.*/culture_.*\.md$")


def _validate_path(path: str) -> str | None:
    """Return an error message for an unusable path, or None if it is safe."""
    if not path:
        return "empty file path"
    if "\\" in path or path.startswith("/"):
        return f"`{path}`: paths must be repo-relative with forward slashes"
    if any(part in ("", ".", "..") for part in path.split("/")):
        return f"`{path}`: path traversal and empty segments are not allowed"
    if not CULTURE_PATH_RE.match(path):
        return f"`{path}`: only `regions/.../culture_*.md` files can be reviewed"
    return None


def parse_command(body: str) -> dict:
    """Parse a PR comment body into {mode, files, errors}.

    Returns mode 'none' when the comment is not a `/review` command, so the
    workflow can stay silent on unrelated comments.
    """
    result: dict = {"mode": "none", "files": [], "errors": []}

    # Find the first line whose leading token is exactly `/review`
    # (tolerate surrounding text; do not match `/reviewer` etc.).
    tokens: list[str] = []
    command_line = ""
    for line in body.splitlines():
        parts = line.split()
        if parts and parts[0] == "/review":
            command_line = line.strip()
            tokens = parts
            break
    if not tokens:
        return result

    # `/review` or `/review help`
    if len(tokens) == 1 or tokens[1] == "help":
        result["mode"] = "help"
        return result

    if tokens[1] != "prose":
        result["mode"] = "help"
        result["errors"].append(f"Unknown command: `{command_line}`")
        return result

    # `/review prose` or `/review prose help`
    if len(tokens) == 2 or tokens[2] == "help":
        result["mode"] = "help"
        return result

    subcommand = tokens[2]
    paths = tokens[3:]

    if subcommand == "changed":
        result["mode"] = "changed"
        if paths:
            result["errors"].append(
                "`/review prose changed` takes no file arguments"
            )
        return result

    if subcommand in ("file", "files"):
        result["mode"] = subcommand
        if not paths:
            result["errors"].append(
                f"`/review prose {subcommand}` needs at least one file path"
            )
            return result
        for path in paths:
            error = _validate_path(path)
            if error:
                result["errors"].append(error)
            else:
                result["files"].append(path)
        return result

    result["mode"] = "help"
    result["errors"].append(f"Unknown subcommand: `{subcommand}`")
    return result


def main() -> None:
    body = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read()
    print(json.dumps(parse_command(body)))


if __name__ == "__main__":
    main()
