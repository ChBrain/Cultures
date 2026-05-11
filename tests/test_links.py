"""Cultures-specific link integrity checks.

Covers what khai-links does NOT check:
  - Orphan detection: regions/ files that are never referenced by any other file
  - Engine link integrity: broken links in engine/*.md files

khai-links handles broken links in changed regions/ files via --khai-files.
This file handles the whole-repo checks that need full context.
"""
import re
from pathlib import Path
import pytest

_LINK_RE = re.compile(r'\[[^\]]*\]\(([^)]+)\)')


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


def test_engine_links_resolve(md_file: Path):
    broken = _broken_links(md_file)
    assert not broken, f"{md_file.name}: {len(broken)} broken link(s): {broken}"


def test_no_orphans(pytestconfig):
    root = Path(pytestconfig.rootdir)
    regions = root / "regions"
    engine = root / "engine"
    if not regions.is_dir():
        pytest.skip("no regions/ directory")

    all_files: list[Path] = list(regions.rglob("*.md"))
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

    region_files = list(regions.rglob("*.md"))
    orphans = [f for f in region_files if f.resolve() not in referenced]
    assert not orphans, (
        f"{len(orphans)} orphaned file(s) in regions/ (never referenced):\n"
        + "\n".join(f"  {f.relative_to(root)}" for f in sorted(orphans))
    )
