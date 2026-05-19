"""Gate for the engine language-as-process ladder (issue #281 / PR #283).

The ladder is 21 engine files under ``engine/``:

  - 1 root    -- ``process_using_language.md``
  - 4 parents -- ``process_{speaking,hearing,writing,reading}.md``
  - 16 leaves -- ``process_<channel>_<width>.md``

It is universal engine content (``Scope: Universal``), not scoped to a
country, but it is solution-grade culture material and is gated like one.
khai does not see engine files -- its ``--khai-files`` scope is
``regions/*.md`` -- so the ladder's structural contract is enforced here:
completeness, the IDLE section set, ``Scope: Universal``, and the link graph.

The whole module skips when the ladder is absent. The 21 files land in one
PR (#283); before that there is nothing to check, and this gate must not
fail an unrelated PR for a not-yet-built ladder.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent
_ENGINE = _ROOT / "engine"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from culture_metadata import format_of, read_metadata  # noqa: E402

_ROOT_FILE = "process_using_language.md"

# channel -> its four width slugs. The shared scale, surfaced per channel;
# the deepest width is always mother_tongue.
_WIDTHS = {
    "speaking": ["borrowed", "carried", "worn", "mother_tongue"],
    "hearing": ["decoded", "followed", "caught", "mother_tongue"],
    "writing": ["copied", "drafted", "polished", "mother_tongue"],
    "reading": ["deciphered", "followed", "caught", "mother_tongue"],
}

# The v2 Process IDLE section set.
_IDLE = ("Initiated by", "Direction", "Lever", "Echo")


def _parent(channel: str) -> str:
    return f"process_{channel}.md"


def _leaf(channel: str, width: str) -> str:
    return f"process_{channel}_{width}.md"


def _ladder_files() -> list[str]:
    files = [_ROOT_FILE]
    for channel, widths in _WIDTHS.items():
        files.append(_parent(channel))
        files += [_leaf(channel, w) for w in widths]
    return files


_LADDER = _ladder_files()


def _present() -> bool:
    """True once the ladder has landed (its root file exists)."""
    return (_ENGINE / _ROOT_FILE).is_file()


def _links(text: str) -> set[str]:
    return {
        m.group(1).split("#", 1)[0].strip()
        for m in re.finditer(r"\[[^\]]*\]\(([^)]+)\)", text)
    }


# ---------------------------------------------------------------------------
# Set completeness
# ---------------------------------------------------------------------------

def test_ladder_complete():
    """All 21 ladder files exist -- 1 root + 4 parents + 16 leaves."""
    if not _present():
        pytest.skip("language-process ladder not present yet (lands in PR #283)")
    missing = [f for f in _LADDER if not (_ENGINE / f).is_file()]
    assert not missing, f"engine language-process ladder missing file(s): {missing}"
    assert len(_LADDER) == 21


def test_no_stray_ladder_leaves():
    """No process_<channel>_*.md beyond the 16 declared widths.

    Catches a mistyped or extra leaf -- e.g. process_speaking_warn.md.
    """
    if not _present():
        pytest.skip("language-process ladder not present yet")
    expected = set(_LADDER)
    for channel in _WIDTHS:
        for path in _ENGINE.glob(f"process_{channel}_*.md"):
            assert path.name in expected, (
                f"unexpected ladder leaf {path.name} -- not a declared width "
                f"of '{channel}' ({_WIDTHS[channel]})"
            )


# ---------------------------------------------------------------------------
# Per-file structure
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("fname", _LADDER)
def test_ladder_file_has_idle_sections(fname):
    """Every ladder file carries the v2 Process IDLE section set."""
    if not _present():
        pytest.skip("language-process ladder not present yet")
    path = _ENGINE / fname
    if not path.is_file():
        pytest.skip(f"{fname} absent -- caught by test_ladder_complete")
    text = path.read_text(encoding="utf-8", errors="replace")
    missing = [
        s for s in _IDLE
        if not re.search(rf"^##\s+{re.escape(s)}\s*$", text, re.MULTILINE)
    ]
    assert not missing, f"{fname}: missing IDLE section(s): {missing}"


@pytest.mark.parametrize("fname", _LADDER)
def test_ladder_file_scope_universal(fname):
    """Every ladder file's Owner block declares Scope: Universal."""
    if not _present():
        pytest.skip("language-process ladder not present yet")
    path = _ENGINE / fname
    if not path.is_file():
        pytest.skip(f"{fname} absent -- caught by test_ladder_complete")
    text = path.read_text(encoding="utf-8", errors="replace")
    assert re.search(
        r"^-\s*\*{0,2}Scope:?\*{0,2}\s*Universal\b", text, re.MULTILINE
    ), f"{fname}: Owner block must declare 'Scope: Universal'"


@pytest.mark.parametrize("fname", _LADDER)
def test_ladder_file_declares_khai_process_in_frontmatter(fname):
    """Every ladder file declares its kind via YAML frontmatter.

    khai is path-independent and declaration-driven: it classifies a file
    from its `khai:` declaration, not its location. Engine ladder files are
    Process kind, so each carries frontmatter with `khai: process` -- the
    same YAML-frontmatter form culture files use. The legacy trailing-footer
    form is not accepted.
    """
    if not _present():
        pytest.skip("language-process ladder not present yet")
    path = _ENGINE / fname
    if not path.is_file():
        pytest.skip(f"{fname} absent -- caught by test_ladder_complete")
    text = path.read_text(encoding="utf-8", errors="replace")
    fmt = format_of(text)
    assert fmt == "frontmatter", (
        f"{fname}: metadata must be YAML frontmatter (got {fmt!r}) -- the "
        f"engine ladder uses the frontmatter form, not the legacy footer"
    )
    assert read_metadata(text).get("khai") == "process", (
        f"{fname}: frontmatter must declare `khai: process` so khai "
        f"classifies it as a Process component"
    )


# ---------------------------------------------------------------------------
# Link graph
# ---------------------------------------------------------------------------

def test_root_links_every_parent():
    """The root links all four channel parents."""
    if not _present():
        pytest.skip("language-process ladder not present yet")
    links = _links((_ENGINE / _ROOT_FILE).read_text(encoding="utf-8", errors="replace"))
    missing = [_parent(c) for c in _WIDTHS if _parent(c) not in links]
    assert not missing, f"{_ROOT_FILE}: root does not link parent(s): {missing}"


@pytest.mark.parametrize("channel", sorted(_WIDTHS))
def test_parent_links_its_four_leaves(channel):
    """Each channel parent links all four of its width leaves."""
    if not _present():
        pytest.skip("language-process ladder not present yet")
    path = _ENGINE / _parent(channel)
    if not path.is_file():
        pytest.skip(f"{_parent(channel)} absent -- caught by test_ladder_complete")
    links = _links(path.read_text(encoding="utf-8", errors="replace"))
    missing = [
        _leaf(channel, w) for w in _WIDTHS[channel]
        if _leaf(channel, w) not in links
    ]
    assert not missing, f"{_parent(channel)}: does not link leaf/leaves: {missing}"
