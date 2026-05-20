"""Smoke tests for scripts/build_pdfs.py.

Mirrors tests/test_build_zips.py's intent: the build script is the
single source of truth for what ships, so a test imports and exercises
its public surface. The pandoc subprocess is mocked -- this gates the
PRE-pandoc work (enumeration, markdown assembly, the completeness
filter) without requiring pandoc + weasyprint in the test environment.

The cross-check that PDFs and zips ship the SAME culture set lives in
the alignment test (test_culture_completeness_alignment.py); here we
verify build_pdfs alone is internally correct.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest import mock

import pytest

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "scripts"))

from build_pdfs import build_region_pdfs, build_world_pdf  # noqa: E402
from culture_completeness import complete_countries  # noqa: E402


@pytest.fixture
def fake_pandoc(monkeypatch):
    """Replace subprocess.run so the build doesn't shell out to pandoc.

    Each call writes a tiny placeholder PDF at the expected output path so
    the script's contract (file appears at dist/<name>.pdf) holds.
    """
    calls: list[list[str]] = []

    def fake_run(cmd, check=False, **kwargs):
        calls.append(list(cmd))
        # The script writes a sidecar .md and asks pandoc to produce a .pdf at -o <path>.
        # Find the -o argument and touch the path.
        if "-o" in cmd:
            out = Path(cmd[cmd.index("-o") + 1])
            out.write_bytes(b"%PDF-1.4\n%%EOF\n")
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr("build_pdfs.subprocess.run", fake_run)
    return calls


def test_region_pdfs_one_per_region_with_complete_country(tmp_path, fake_pandoc):
    """build_region_pdfs writes exactly one PDF per region that has
    at least one complete culture."""
    built = build_region_pdfs(tmp_path)
    expected_regions = sorted({region for region, _country in complete_countries()})
    expected_names = [f"cultures-{r}.pdf" for r in expected_regions]
    assert built == expected_names
    for name in expected_names:
        assert (tmp_path / name).is_file(), f"{name} not produced"


def test_world_pdf_produced_when_any_complete_culture(tmp_path, fake_pandoc):
    """build_world_pdf writes cultures-world.pdf iff at least one
    complete culture exists."""
    built = build_world_pdf(tmp_path)
    if complete_countries():
        assert built == ["cultures-world.pdf"]
        assert (tmp_path / "cultures-world.pdf").is_file()
    else:
        assert built == []


def test_build_uses_complete_countries_only(tmp_path, fake_pandoc):
    """The markdown handed to pandoc must reference only complete cultures.

    Inspects the sidecar .md content (build_pdfs writes one per render call
    next to the PDF) and asserts no incomplete country's name appears.
    """
    build_region_pdfs(tmp_path)
    complete_names = {c.name for _r, c in complete_countries()}
    # Any region folder with a README but failing is_complete_culture() is
    # incomplete; its slug must not appear inside any of the sidecar .md
    # files build_pdfs wrote (build_pdfs cleans them up after pandoc, but
    # in the mock pandoc never deleted them).
    incomplete_names: set[str] = set()
    regions = _ROOT / "regions"
    for region_dir in regions.iterdir():
        if not region_dir.is_dir() or region_dir.name.startswith("."):
            continue
        for country_dir in region_dir.iterdir():
            if not country_dir.is_dir() or country_dir.name.startswith("."):
                continue
            if country_dir.name not in complete_names:
                incomplete_names.add(country_dir.name)
    # If the build wrote .md sidecars (the mock pandoc doesn't delete them
    # the way the real script does after success), they're hidden dotfiles.
    sidecars = list(tmp_path.glob(".*.md"))
    for sc in sidecars:
        body = sc.read_text(encoding="utf-8")
        for inc in incomplete_names:
            # exclude false-positive substring hits ("china" inside "machinery") by
            # requiring the slug as a culture_*_<adj>_ token boundary -- the slug
            # appears only as a region/country path segment in markdown headings,
            # never as a casual prose word in the shipped culture content. A
            # contained mention here means the build pulled the country in.
            assert f"culture_{inc}_" not in body, (
                f"incomplete country '{inc}' referenced in PDF body for {sc.name}"
            )
