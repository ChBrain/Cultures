"""Read, strip, and classify the metadata block on a culture markdown file.

Single source of truth for culture-file metadata during (and after) the
trailing-footer -> YAML-frontmatter migration. Every consumer -- the zip
builder, the validators, the scaffolding scripts, the migration script --
goes through here instead of parsing footer or frontmatter on its own.

Two on-disk formats are recognised:

  frontmatter (canonical)         footer (legacy)
  -----------------------         ----------------------------------
  ---                             <body>
  khai: position                  ...
  type: Fictional                 ---
  ...                             *khai: position*
  ---                             *hofstede: ...*
  <body>                          *2026-05-13 | owner | v.. | lic.*

API:
  format_of(text)      -> 'frontmatter' | 'footer' | 'none'
  read_metadata(text)  -> dict   (parsed metadata; {} when 'none')
  strip_metadata(text) -> str    (body with the metadata block removed)

``strip_metadata`` is what deployment artifacts use to ship culture
content with zero metadata lines; ``read_metadata`` is the parse layer the
validators and the migration script consume.
"""
from __future__ import annotations

import re

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - PyYAML is in tests/requirements.txt
    yaml = None

# A leading YAML frontmatter block: '---' on line 1, content, closing '---'.
_FRONTMATTER_RE = re.compile(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*\r?\n", re.DOTALL)

# Legacy trailing-footer line shapes. A footer is a contiguous run of these
# at the end of the file, optionally preceded by a '---' rule. Recognising
# every shape matters: an unrecognised line breaks the contiguous run and
# leaks the rest of the footer into deployment artifacts.
_IP_LINE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}\s*\|")          # date | owner | version | license
_VERSION_LINE_RE = re.compile(r"^v\d+\.\d+\.\d+\b", re.IGNORECASE)
_STAMP_LINE_RE = re.compile(r"^culture_[a-z0-9_\-]+\.md\s*-\s*\d", re.IGNORECASE)
_FOOTER_KEYS = ("khai:", "hofstede signal:", "hofstede:", "type:")


def _unwrap_italic(s: str) -> str:
    """Strip a single pair of surrounding '*' markdown-italic markers."""
    if len(s) >= 2 and s.startswith("*") and s.endswith("*"):
        return s[1:-1].strip()
    return s


def _is_footer_line(line: str) -> bool:
    """True if ``line`` is a trailing-footer metadata line (any known shape)."""
    core = _unwrap_italic(line.strip())
    if not core:
        return False
    low = core.lower()
    if low.startswith(_FOOTER_KEYS):
        return True
    return bool(
        _IP_LINE_RE.match(core) or _VERSION_LINE_RE.match(core)
        or _STAMP_LINE_RE.match(low)
    )


def _footer_start(lines: list[str]) -> int | None:
    """Return the line index where the trailing footer begins, or None.

    The index points at the leading '---' rule when one precedes the
    metadata lines, otherwise at the first metadata line.
    """
    end = len(lines) - 1
    while end >= 0 and not lines[end].strip():
        end -= 1
    if end < 0:
        return None

    first_meta = None
    i = end
    while i >= 0:
        if not lines[i].strip():
            i -= 1
            continue
        if _is_footer_line(lines[i]):
            first_meta = i
            i -= 1
            continue
        break
    if first_meta is None:
        return None

    j = first_meta - 1
    while j >= 0 and not lines[j].strip():
        j -= 1
    if j >= 0 and lines[j].strip() == "---":
        return j
    return first_meta


def format_of(text: str) -> str:
    """Return 'frontmatter', 'footer', or 'none' for a culture markdown file."""
    if _FRONTMATTER_RE.match(text):
        return "frontmatter"
    if _footer_start(text.splitlines()) is not None:
        return "footer"
    return "none"


def strip_metadata(text: str) -> str:
    """Return ``text`` with its metadata block removed.

    Removes a leading frontmatter block or a trailing footer block (and the
    footer's '---' rule). Used to build deployment artifacts that carry
    zero metadata lines. A file with no metadata is returned unchanged.
    """
    fm = _FRONTMATTER_RE.match(text)
    if fm is not None:
        return text[fm.end():]

    lines = text.splitlines()
    start = _footer_start(lines)
    if start is None:
        return text
    kept = lines[:start]
    while kept and not kept[-1].strip():
        kept.pop()
    return "\n".join(kept) + ("\n" if kept else "")


def _parse_footer(lines: list[str], start: int) -> dict:
    """Parse legacy footer lines (from ``start`` to EOF) into a metadata dict."""
    meta: dict = {}
    for raw in lines[start:]:
        core = _unwrap_italic(raw.strip())
        if not core or core == "---":
            continue
        low = core.lower()
        if low.startswith("khai:"):
            meta["khai"] = core.split(":", 1)[1].strip()
        elif low.startswith("hofstede signal:"):
            meta["hofstede"] = core.split(":", 1)[1].strip()
        elif low.startswith("hofstede:"):
            meta["hofstede"] = core.split(":", 1)[1].strip()
        elif low.startswith("type:"):
            meta["type"] = core.split(":", 1)[1].strip()
        elif _IP_LINE_RE.match(core):
            parts = [p.strip() for p in core.split("|")]
            if len(parts) == 4:
                date, owner, version, license_ = parts
                meta["stamp"] = {
                    "owner": owner, "version": version, "date": date,
                }
                meta["license"] = license_
    return meta


def read_metadata(text: str) -> dict:
    """Return the file's metadata as a dict, regardless of on-disk format.

    Frontmatter is parsed as YAML; the legacy footer is parsed line by line
    into the same key space. Returns ``{}`` when the file carries neither.
    """
    fm = _FRONTMATTER_RE.match(text)
    if fm is not None:
        if yaml is None:  # pragma: no cover
            raise RuntimeError("PyYAML is required to read frontmatter metadata")
        data = yaml.safe_load(fm.group(1))
        return data if isinstance(data, dict) else {}

    lines = text.splitlines()
    start = _footer_start(lines)
    if start is None:
        return {}
    return _parse_footer(lines, start)
