"""Unit tests for scripts/migrate_footer_to_frontmatter.py.

Pins the footer -> frontmatter conversion: a converted file round-trips
through culture_metadata, the body is preserved, and the conversion is
idempotent (a frontmatter file is left untouched).
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scripts"))

from culture_metadata import format_of, read_metadata, strip_metadata  # noqa: E402
from migrate_footer_to_frontmatter import to_frontmatter  # noqa: E402

_BODY = "# German Culture\n\nBody one.\n\nBody two.\n"

_FOOTER = _BODY + (
    "\n---\n"
    "*hofstede: aggregate in [README.md](README.md).*\n"
    "*khai: position*\n"
    "*2026-05-13 | KAI HACKS AI | v0.2.0 | CC-BY-NC-4.0*\n"
)


def test_to_frontmatter_produces_frontmatter():
    out = to_frontmatter(_FOOTER)
    assert out is not None
    assert format_of(out) == "frontmatter"
    assert out.startswith("---\n")


def test_to_frontmatter_preserves_body():
    out = to_frontmatter(_FOOTER)
    assert strip_metadata(out) == _BODY


def test_to_frontmatter_carries_metadata():
    meta = read_metadata(to_frontmatter(_FOOTER))
    assert meta["khai"] == "position"
    assert meta["license"] == "CC-BY-NC-4.0"
    assert meta["stamp"] == {
        "owner": "KAI HACKS AI", "version": "v0.2.0", "date": "2026-05-13",
    }


def test_to_frontmatter_normalises_hofstede_pointer():
    """The free-text footer pointer collapses to the controlled token."""
    meta = read_metadata(to_frontmatter(_FOOTER))
    assert meta["hofstede"] == "aggregate"


def test_to_frontmatter_idempotent_on_frontmatter():
    converted = to_frontmatter(_FOOTER)
    assert to_frontmatter(converted) is None


def test_to_frontmatter_none_when_no_footer():
    assert to_frontmatter(_BODY) is None
