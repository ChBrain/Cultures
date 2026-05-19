"""Output validator for the zip build engine (scripts/build_zips.py).

Runs the real build into a temp dir and checks every produced zip. This is
the per-PR clean-build gate: build-zips.yml only fires on `release` /
`workflow_dispatch`, so this test is what proves on a PR that the build is
sound.

  - engine zips are self-consistent on their own;
  - culture zips are self-consistent extracted *together with* engine-raw.zip
    -- the real deployment unit, since a deployer mixes one culture zip and
    one engine zip;
  - shipped markdown carries no metadata block (it was stripped).
"""
from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "scripts"))
sys.path.insert(0, str(_ROOT / "tests"))

import build_zips  # noqa: E402
from culture_metadata import format_of  # noqa: E402

_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
_ENGINE_ZIPS = (
    "engine-raw", "engine-claude", "engine-copilot",
    "engine-gemini", "engine-notebooklm", "engine-perplexity",
)


@pytest.fixture(scope="module")
def dist(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("dist")
    build_zips.build_all(out)
    return out


def _extract(zip_paths, into: Path) -> None:
    for zp in zip_paths:
        with zipfile.ZipFile(zp) as zf:
            zf.extractall(into)


def _broken_links(folder: Path) -> list[str]:
    """Relative markdown links in the folder that resolve to no file."""
    broken: list[str] = []
    for md in sorted(folder.glob("*.md")):
        for m in _LINK_RE.finditer(md.read_text(encoding="utf-8", errors="replace")):
            href = m.group(1).strip()
            if href.startswith(("http://", "https://", "#", "mailto:")):
                continue
            target = href.split("#", 1)[0]
            if target and not (folder / target).is_file():
                broken.append(f"{md.name} -> {target}")
    return broken


def test_expected_zips_exist(dist):
    names = {p.name for p in dist.glob("*.zip")}
    for engine in _ENGINE_ZIPS:
        assert f"{engine}.zip" in names, f"missing {engine}.zip"
    assert "cultures-world.zip" in names, "missing cultures-world.zip"
    assert any(
        n.startswith("cultures-") and n != "cultures-world.zip"
        for n in names
    ), "no country/region culture zips built"


@pytest.mark.parametrize("engine", _ENGINE_ZIPS)
def test_engine_zip_self_consistent(dist, engine, tmp_path):
    zp = dist / f"{engine}.zip"
    if not zp.is_file():
        pytest.skip(f"{engine}.zip not built")
    _extract([zp], tmp_path)
    broken = _broken_links(tmp_path)
    assert not broken, f"{engine}.zip has unresolved link(s): {broken}"


def test_culture_zips_resolve_mixed_with_engine(dist, tmp_path_factory):
    """A culture zip + engine-raw.zip, extracted together, is link-complete."""
    raw = dist / "engine-raw.zip"
    assert raw.is_file(), "engine-raw.zip is required for the mix check"
    culture_zips = sorted(dist.glob("cultures-*.zip"))
    assert culture_zips, "no culture zips built"
    for cz in culture_zips:
        combined = tmp_path_factory.mktemp(cz.stem)
        _extract([cz, raw], combined)
        broken = _broken_links(combined)
        assert not broken, (
            f"{cz.name} + engine-raw.zip has unresolved link(s): {broken}"
        )


def test_shipped_markdown_has_no_metadata(dist, tmp_path_factory):
    """Every shipped markdown file had its metadata block stripped."""
    for zp in sorted(dist.glob("*.zip")):
        out = tmp_path_factory.mktemp(zp.stem + "-meta")
        _extract([zp], out)
        for md in sorted(out.glob("*.md")):
            fmt = format_of(md.read_text(encoding="utf-8", errors="replace"))
            assert fmt == "none", (
                f"{zp.name}:{md.name} still carries a {fmt} metadata block"
            )
