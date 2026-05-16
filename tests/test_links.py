"""Cultures-specific link integrity checks.

Covers what khai-links does NOT check:
  - Orphan detection: non-leaf regions/ files added in this PR that are
    never referenced by any other file
  - Engine link integrity: broken links in engine/*.md files

khai-links handles broken links in changed regions/ files via --khai-files.
test_no_orphans scopes to --khai-files so it only checks files in the PR,
not the entire 198-country tree.

Leaf-node file types are excluded from orphan detection because they are
never linked to by design: persona, place, language, process, README,
REFERENCES, hofstede_decisions.
"""
import re
from pathlib import Path
import pytest

_LINK_RE = re.compile(r'\[[^\]]*\]\(([^)]+)\)')

# Filename stems that are expected to be leaf nodes (no inbound links needed).
_LEAF_NAMES = frozenset({"README", "REFERENCES", "hofstede_decisions"})

# culture_*_<type>_*.md type segments that mark leaf nodes.
# position and piece are the only types expected to have inbound links;
# process, language, place, and persona are standalone by design.
_LEAF_SEGMENTS = frozenset({"persona", "place", "language", "process"})


def _is_leaf(path: Path) -> bool:
    """Return True for file types that need no inbound link."""
    if path.stem in _LEAF_NAMES:
        return True
    # culture_<lang>_<type>_<name>.md  →  parts[2] is the type segment
    parts = path.stem.split("_")
    if len(parts) >= 3 and parts[2] in _LEAF_SEGMENTS:
        return True
    # Stub persona files: persona_<name>.md (no culture_ prefix)
    if parts[0] == "persona":
        return True
    return False


def _broken_links(md_file: Path) -> list[str]:
    try:
        text = md_file.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    broken = []
    for m in _LINK_RE.finditer(text):
        target = m.group(1).strip()
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        anchor_idx = target.find("#")
        if anchor_idx != -1:
            target = target[:anchor_idx]
        if not target:
            continue
        if not (md_file.parent / target).resolve().exists():
            broken.append(target)
    return broken


def _build_referenced_set(root: Path) -> set[Path]:
    """Collect every file that is the target of at least one markdown link."""
    regions = root / "regions"
    engine = root / "engine"
    all_files: list[Path] = list(regions.rglob("*.md")) if regions.is_dir() else []
    if engine.is_dir():
        all_files += list(engine.glob("*.md"))

    referenced: set[Path] = set()
    for f in all_files:
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for m in _LINK_RE.finditer(text):
            target = m.group(1).strip()
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            anchor_idx = target.find("#")
            if anchor_idx != -1:
                target = target[:anchor_idx]
            if not target:
                continue
            resolved = (f.parent / target).resolve()
            if resolved.exists():
                referenced.add(resolved)
    return referenced


def test_engine_links_resolve(md_file: Path):
    broken = _broken_links(md_file)
    assert not broken, f"{md_file.name}: {len(broken)} broken link(s): {broken}"


def test_no_orphans(pytestconfig):
    root = Path(pytestconfig.rootdir)
    regions = root / "regions"
    if not regions.is_dir():
        pytest.skip("no regions/ directory")

    # Scope to PR files when --khai-files is provided; skip otherwise.
    try:
        khai_files_raw = pytestconfig.getoption("--khai-files") or ""
    except ValueError:
        khai_files_raw = ""

    if not khai_files_raw.strip():
        pytest.skip("--khai-files not provided; orphan check skipped outside PR context")

    pr_paths = [
        (root / p.strip()).resolve()
        for p in khai_files_raw.split()
        if p.strip().endswith(".md") and p.strip().startswith("regions/")
    ]
    candidates = [p for p in pr_paths if p.exists() and not _is_leaf(p)]
    if not candidates:
        pytest.skip("no non-leaf .md files in regions/ in this PR")

    referenced = _build_referenced_set(root)
    orphans = [f for f in candidates if f not in referenced]
    assert not orphans, (
        f"{len(orphans)} orphaned file(s) added in this PR (never referenced):\n"
        + "\n".join(f"  {f.relative_to(root)}" for f in sorted(orphans))
    )
