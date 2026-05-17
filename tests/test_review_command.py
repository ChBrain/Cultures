"""Unit tests for scripts/parse_review_command.py.

Pins the `/review` comment-command grammar consumed by
.github/workflows/prose-review-on-comment.yml:
- non-/review comments resolve to mode 'none' (workflow stays silent)
- help / changed / file / files modes
- non-culture paths, traversal and odd input become errors, not crashes
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "scripts"))

from parse_review_command import parse_command  # noqa: E402

CULTURE_A = "regions/europe/germany/culture_german_position.md"
CULTURE_B = "regions/asia/japan/culture_japanese_piece_war.md"


# ---------------------------------------------------------------------------
# mode: none - not a /review command
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("body", [
    "",
    "just a normal review comment",
    "looks good to me",
    "/reviewer is not the command",
    "please /review prose changed",  # /review not at line start
])
def test_non_command_is_none(body):
    result = parse_command(body)
    assert result["mode"] == "none"
    assert result["files"] == []
    assert result["errors"] == []


# ---------------------------------------------------------------------------
# mode: help
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("body", [
    "/review",
    "/review help",
    "/review prose",
    "/review prose help",
])
def test_help_variants(body):
    result = parse_command(body)
    assert result["mode"] == "help"
    assert result["errors"] == []


@pytest.mark.parametrize("body", [
    "/review nonsense",
    "/review prose wibble",
])
def test_unknown_command_is_help_with_error(body):
    result = parse_command(body)
    assert result["mode"] == "help"
    assert result["errors"]


# ---------------------------------------------------------------------------
# mode: changed
# ---------------------------------------------------------------------------

def test_changed():
    result = parse_command("/review prose changed")
    assert result["mode"] == "changed"
    assert result["files"] == []
    assert result["errors"] == []


def test_changed_rejects_extra_args():
    result = parse_command(f"/review prose changed {CULTURE_A}")
    assert result["mode"] == "changed"
    assert result["errors"]


# ---------------------------------------------------------------------------
# mode: file / files
# ---------------------------------------------------------------------------

def test_file_single():
    result = parse_command(f"/review prose file {CULTURE_A}")
    assert result["mode"] == "file"
    assert result["files"] == [CULTURE_A]
    assert result["errors"] == []


def test_files_multiple():
    result = parse_command(f"/review prose files {CULTURE_A} {CULTURE_B}")
    assert result["mode"] == "files"
    assert result["files"] == [CULTURE_A, CULTURE_B]
    assert result["errors"] == []


def test_file_without_path_is_error():
    result = parse_command("/review prose file")
    assert result["mode"] == "file"
    assert result["files"] == []
    assert result["errors"]


# ---------------------------------------------------------------------------
# path validation - rejected paths land in errors, not files
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("path", [
    "regions/europe/germany/persona_christian.md",   # not culture_*
    "regions/europe/germany/README.md",              # not culture_*
    "scripts/prose_review.py",                       # outside regions/
    "culture_german_position.md",                    # no regions/ prefix
    "regions/europe/germany/culture_german.txt",     # not .md
])
def test_non_culture_path_rejected(path):
    result = parse_command(f"/review prose file {path}")
    assert result["files"] == []
    assert result["errors"]


@pytest.mark.parametrize("path", [
    "regions/../regions/europe/germany/culture_german_position.md",
    "/regions/europe/germany/culture_german_position.md",
    "regions\\europe\\germany\\culture_german_position.md",
    "regions/europe/./germany/culture_german_position.md",
])
def test_unsafe_path_rejected(path):
    result = parse_command(f"/review prose file {path}")
    assert result["files"] == []
    assert result["errors"]


def test_mixed_valid_and_invalid_paths():
    bad = "regions/europe/germany/README.md"
    result = parse_command(f"/review prose files {CULTURE_A} {bad}")
    assert result["files"] == [CULTURE_A]
    assert len(result["errors"]) == 1


# ---------------------------------------------------------------------------
# robustness - odd input must not crash
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("body", [
    "/review\n",
    "/review prose changed\r\n",
    "  /review prose changed  ",
    "thanks!\n/review prose changed\nmore text",
    "/review   prose    changed",
])
def test_whitespace_and_multiline(body):
    # Should parse without raising; the changed command resolves to 'changed'.
    result = parse_command(body)
    assert result["mode"] in ("help", "changed")
