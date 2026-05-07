#!/usr/bin/env python3
"""General validation for all *.md files under the Cultures regions tree.

Checks each file for:
  - Filename format: ASCII only, underscores only (no hyphens or special chars)
  - UTF-8 encoding with no byte-order mark
  - No Unicode replacement character (U+FFFD)
  - No em-dash (U+2014) - forbidden by repository style
  - No literal Unicode escape sequences
  - Trailing newline at end of file (POSIX, .editorconfig insert_final_newline)

Read-only. Emits Issue records with verdicts where the rule determines
the fix. Per-document-type schema (required sections, footers) is
intentionally out of scope for this layer; Cultures has four shapes
(culture_*_position, culture_*_piece_*, culture_*_place_*, persona_*)
and each warrants its own schema validator.

Exit status:
  0 if every file passes, 1 otherwise.

Usage:
  tests/validate_general.py            # walks regions/
  tests/validate_general.py FILE...    # validates only the given files
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from findings import Issue

EM_DASH = "—"


def find_md_files(root: Path) -> list[Path]:
    regions = root / "regions"
    if not regions.is_dir():
        return []
    return sorted(p for p in regions.rglob("*.md") if ".git" not in p.parts)


def validate(path: Path) -> list[Issue]:
    issues: list[Issue] = []

    if "-" in path.name:
        issues.append(Issue(
            error="filename contains hyphen: use underscore instead",
            verdict=f"rename to {path.name.replace('-', '_')}",
        ))

    try:
        path.name.encode("ascii")
    except UnicodeEncodeError:
        issues.append(Issue(
            error="filename contains non-ASCII characters",
            verdict="use ASCII characters only (a-z, 0-9, underscore, dot)",
        ))

    raw = path.read_bytes()

    # Check for CRLF line endings (Windows)
    if b"\r\n" in raw:
        issues.append(Issue(
            error="contains Windows CRLF line endings (\\r\\n)",
            verdict="convert to POSIX LF line endings (\\n) - use `dos2unix` or Git auto-normalization",
        ))

    if raw.startswith(b"\xef\xbb\xbf"):
        issues.append(Issue(
            error="starts with UTF-8 BOM",
            verdict="strip the leading 3 bytes (EF BB BF)",
        ))

    if raw and not raw.endswith(b"\n"):
        issues.append(Issue(
            error="file does not end with a trailing newline",
            verdict="append a newline (`\\n`) to the end of the file",
        ))

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        return [Issue(
            error=f"not valid UTF-8: {exc}",
            verdict=None,
        )]

    if "�" in text:
        issues.append(Issue(
            error="contains U+FFFD replacement character",
            verdict=None,
        ))

    if EM_DASH in text:
        issues.append(Issue(
            error="contains em-dash (U+2014) - forbidden in this repository",
            verdict="replace each em-dash with a hyphen `-` or rephrase",
        ))

    if re.search(r"\\u[0-9a-fA-F]{4}", text):
        issues.append(Issue(
            error="contains literal Unicode escape sequences",
            verdict="decode each `\\uXXXX` to its UTF-8 character",
        ))

    # Check for footer in content files (culture_*, persona_*)
    if any(pattern in path.name for pattern in ["culture_", "persona_"]):
        if "KAI Worlds" not in text or not re.search(r"v\d+\.\d+\.\d+ - KAI Worlds", text):
            issues.append(Issue(
                error="missing or malformed footer",
                verdict="add footer line: `v0.1.0 - KAI Worlds`",
            ))
        else:
            # Check that footer is on last non-empty line
            lines = text.rstrip('\n').split('\n')
            if lines and not re.match(r"v\d+\.\d+\.\d+ - KAI Worlds", lines[-1]):
                issues.append(Issue(
                    error="footer not on last line of file",
                    verdict="move footer to final line (after all content)",
                ))

    return issues


def main(argv: list[str]) -> int:
    root = Path(__file__).resolve().parent.parent
    targets = [Path(a) for a in argv[1:]] if len(argv) > 1 else find_md_files(root)

    failed = 0
    for path in targets:
        issues = validate(path)
        if issues:
            failed += 1
            print(f"FAIL {path}")
            for issue in issues:
                print(f"  - {issue.error}")
                if issue.verdict:
                    print(f"    verdict: {issue.verdict}")

    total = len(targets)
    if failed:
        print(f"\n{failed}/{total} files failed general validation")
        return 1
    print(f"OK: {total} files passed general validation")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
