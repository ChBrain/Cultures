"""Unit tests for tests/culture_metadata.py.

Pins the dual-format contract used through the footer -> frontmatter
migration: format detection, metadata read, and metadata strip must each
behave identically in intent across both on-disk formats.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from culture_metadata import format_of, read_metadata, strip_metadata  # noqa: E402

_BODY = "# Mexican Culture\n\nBody paragraph one.\n\nBody paragraph two.\n"

_FRONTMATTER = (
    "---\n"
    "khai: position\n"
    "type: Fictional\n"
    "hofstede: aggregate\n"
    "license: CC-BY-NC-4.0\n"
    "stamp:\n"
    "  owner: KAI HACKS AI\n"
    "  version: v0.2.0\n"
    "  date: 2026-05-13\n"
    "---\n"
) + _BODY

# v2 footer ending on the Type: line (the case build-zips mis-stripped).
_FOOTER_TYPE = _BODY + (
    "\n---\n"
    "*hofstede: aggregate in README.md*\n"
    "*khai: position*\n"
    "*Type: Fictional*\n"
)

# v2 footer ending on the IP-safeguard line (germany's real shape).
_FOOTER_IP = _BODY + (
    "\n---\n"
    "*hofstede: aggregate in [README.md](README.md).*\n"
    "*khai: position*\n"
    "*2026-05-13 | KAI HACKS AI | v0.2.0 | CC-BY-NC-4.0*\n"
)


# --------------------------------------------------------------------------
# format_of
# --------------------------------------------------------------------------

def test_format_of_frontmatter():
    assert format_of(_FRONTMATTER) == "frontmatter"


@pytest.mark.parametrize("text", [_FOOTER_TYPE, _FOOTER_IP])
def test_format_of_footer(text):
    assert format_of(text) == "footer"


def test_format_of_none():
    assert format_of(_BODY) == "none"


# --------------------------------------------------------------------------
# strip_metadata - must leave zero metadata lines
# --------------------------------------------------------------------------

@pytest.mark.parametrize("text", [_FRONTMATTER, _FOOTER_TYPE, _FOOTER_IP])
def test_strip_metadata_removes_all_metadata(text):
    body = strip_metadata(text)
    assert "khai" not in body
    assert "hofstede" not in body
    assert "Fictional" not in body
    assert "CC-BY-NC" not in body
    assert "---" not in body
    assert body.startswith("# Mexican Culture")
    assert "Body paragraph two." in body


def test_strip_metadata_none_unchanged():
    assert strip_metadata(_BODY) == _BODY


def test_strip_metadata_idempotent():
    once = strip_metadata(_FOOTER_TYPE)
    assert strip_metadata(once) == once


# --------------------------------------------------------------------------
# read_metadata
# --------------------------------------------------------------------------

def test_read_metadata_frontmatter():
    meta = read_metadata(_FRONTMATTER)
    assert meta["khai"] == "position"
    assert meta["type"] == "Fictional"
    assert meta["stamp"]["version"] == "v0.2.0"
    assert meta["license"] == "CC-BY-NC-4.0"


def test_read_metadata_footer_type():
    meta = read_metadata(_FOOTER_TYPE)
    assert meta["khai"] == "position"
    assert meta["type"] == "Fictional"
    assert meta["hofstede"] == "aggregate in README.md"


def test_read_metadata_footer_ip_line_decomposed():
    meta = read_metadata(_FOOTER_IP)
    assert meta["khai"] == "position"
    assert meta["stamp"] == {
        "owner": "KAI HACKS AI", "version": "v0.2.0", "date": "2026-05-13",
    }
    assert meta["license"] == "CC-BY-NC-4.0"


def test_read_metadata_none_is_empty():
    assert read_metadata(_BODY) == {}
