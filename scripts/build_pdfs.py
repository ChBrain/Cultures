#!/usr/bin/env python3
"""PDF build engine for Cultures releases.

Mirrors scripts/build_zips.py: produces per-region and world PDFs from
the same complete-cultures set the zips ship. The two pipelines share
``scripts.culture_completeness`` so the question "which cultures ship?"
has one answer for both formats.

  cultures-<region>.pdf   one PDF per region with >=1 complete culture
  cultures-world.pdf      one PDF covering every complete culture

Each PDF concatenates each complete culture's ``culture_*.md`` content
plus its README and REFERENCES, with relative markdown links flattened
to bare basenames (the flat-zip rule, reused -- a PDF reader follows no
filesystem paths, but flattened links read cleanly inside the PDF and
match what the corresponding zip ships).

Build prerequisites on the host: pandoc + weasyprint installed. The
release workflow installs them; running locally without them will fail
at the pandoc subprocess step.

  python scripts/build_pdfs.py <dist-dir>
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "scripts"))
sys.path.insert(0, str(_ROOT / "tests"))
from build_zips import _country_culture_items, _read, _ship  # noqa: E402
from culture_completeness import complete_countries  # noqa: E402

_REGIONS = _ROOT / "regions"


def _country_pdf_markdown(country: Path) -> str:
    """Markdown body for one country: culture_*.md + README + REFERENCES.

    Reuses ``build_zips._country_culture_items`` so the file set is
    identical to what ships in the zip. README and REFERENCES are added
    after, mirroring ``build_country_zips``. Operational files
    (``hofstede_decisions.md``, ``hofstede_bag.yaml``) are NOT included
    -- a PDF is a deployable artifact, not an audit trail.
    """
    parts: list[str] = []
    for _arcname, content in _country_culture_items(country):
        parts.append(content)
    for name in ("README.md", "REFERENCES.md"):
        f = country / name
        if f.is_file():
            parts.append(_ship(_read(f)))
    return "\n\n---\n\n".join(parts)


def _region_pdf_markdown(countries: list[Path]) -> str:
    """Concatenate every complete culture's PDF body for a region/world."""
    return "\n\n---\n\n".join(_country_pdf_markdown(c) for c in countries)


def _render_pdf(markdown: str, dist: Path, name: str, title: str) -> None:
    """Render a markdown blob to a PDF via pandoc + weasyprint."""
    dist.mkdir(parents=True, exist_ok=True)
    md_path = dist / f".{name}.md"
    md_path.write_text(markdown, encoding="utf-8")
    pdf_path = dist / name
    subprocess.run(
        [
            "pandoc",
            str(md_path),
            "--from", "markdown-yaml_metadata_block",
            "--to", "pdf",
            "--pdf-engine=weasyprint",
            "--metadata", f"title={title}",
            "-o", str(pdf_path),
        ],
        check=True,
    )
    md_path.unlink()


def build_region_pdfs(dist: Path) -> list[str]:
    """One PDF per region with >=1 complete culture."""
    built: list[str] = []
    by_region: dict[str, list[Path]] = {}
    for region, country in complete_countries():
        by_region.setdefault(region, []).append(country)
    for region, countries in sorted(by_region.items()):
        name = f"cultures-{region}.pdf"
        title = f"Cultures - {region.title()}"
        _render_pdf(_region_pdf_markdown(countries), dist, name, title)
        built.append(name)
    return built


def build_world_pdf(dist: Path) -> list[str]:
    """A single PDF covering every complete culture."""
    countries = [c for _region, c in complete_countries()]
    if not countries:
        return []
    _render_pdf(
        _region_pdf_markdown(countries),
        dist,
        "cultures-world.pdf",
        "Cultures - All Regions",
    )
    return ["cultures-world.pdf"]


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        sys.stderr.write("usage: build_pdfs.py <dist-dir>\n")
        return 2
    dist = Path(argv[1]).resolve()
    built = build_region_pdfs(dist) + build_world_pdf(dist)
    for name in built:
        print(name)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
