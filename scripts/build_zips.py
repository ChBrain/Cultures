#!/usr/bin/env python3
"""Zip build engine for Cultures releases.

Produces two zip families that a deployer combines himself:

  culture zips -- culture content only, three granularities:
    cultures-<region>-<country>.zip   one complete country
    cultures-<region>.zip             every complete country in a region
    cultures-world.zip                every complete country

  engine zips -- the engine layer:
    engine-<target>.zip   for claude / copilot / gemini / notebooklm /
                          perplexity -- the shared scaffold + that target's
                          instructions and deployment README
    engine-raw.zip        the shared scaffold only, flat, no target files

A culture zip carries no engine files; the deployer extracts one culture zip
and one engine zip into the same folder. Inside that combined folder every
relative link resolves -- tests/test_build_zips.py verifies it by pairing
each culture zip with engine-raw.zip.

Shipped markdown has its metadata block stripped (tests/culture_metadata) and
its relative links flattened to bare basenames so a flat zip is self-resolving.

  python scripts/build_zips.py <dist-dir>
"""
from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "tests"))
from culture_metadata import strip_metadata  # noqa: E402

_REGIONS = _ROOT / "regions"
_ENGINE = _ROOT / "engine"
_ENGINE_TARGETS = ("claude", "copilot", "gemini", "notebooklm", "perplexity")

_LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")


def flatten_links(text: str, target: str = "default") -> str:
    """Rewrite relative markdown links so a flat zip resolves.

    A link to a markdown file becomes its bare basename
    (``../../engine/stack.md`` -> ``stack.md``). A link to a directory or a
    non-markdown target is unwrapped to plain text -- a flat zip has no
    directory structure to traverse. http / anchor / mailto links are left
    untouched. ``target`` is a per-deployment seam; the rewrite is uniform
    for now.
    """
    def repl(m: re.Match) -> str:
        label, href = m.group(1), m.group(2).strip()
        if href.startswith(("http://", "https://", "#", "mailto:")):
            return m.group(0)
        path, _, anchor = href.partition("#")
        base = path.rstrip("/").rsplit("/", 1)[-1]
        if not base.endswith(".md"):
            return label  # directory / non-md link -- drop link, keep text
        return f"[{label}]({base}{('#' + anchor) if anchor else ''})"
    return _LINK_RE.sub(repl, text)


def _ship(text: str, target: str = "default") -> str:
    """Deployment form of a markdown file: metadata stripped, links flat."""
    return flatten_links(strip_metadata(text), target)


def is_complete_culture(country: Path) -> bool:
    """A country folder ready to ship: position + 2 personas + place + piece + README."""
    if not country.is_dir():
        return False
    personas = [
        p for p in country.glob("*.md")
        if "_persona_" in p.name or p.name.startswith("persona_")
    ]
    return (
        any(country.glob("culture_*_position.md"))
        and len(personas) >= 2
        and any(country.glob("culture_*_place_*.md"))
        and any(country.glob("culture_*_piece_*.md"))
        and (country / "README.md").is_file()
    )


def complete_countries() -> list[tuple[str, Path]]:
    """(region_name, country_dir) for every complete culture, sorted."""
    out: list[tuple[str, Path]] = []
    if not _REGIONS.is_dir():
        return out
    for region in sorted(p for p in _REGIONS.iterdir() if p.is_dir() and not p.name.startswith(".")):
        for country in sorted(p for p in region.iterdir() if p.is_dir() and not p.name.startswith(".")):
            if is_complete_culture(country):
                out.append((region.name, country))
    return out


def _write_zip(path: Path, items: list[tuple[str, str]]) -> None:
    """Write a flat zip from (arcname, text-content) pairs."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        for arcname, content in items:
            zf.writestr(arcname, content)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


# ---------------------------------------------------------------------------
# Culture zips
# ---------------------------------------------------------------------------

def _country_culture_items(country: Path) -> list[tuple[str, str]]:
    """The country's own culture content -- culture_*.md only, shipped."""
    return [
        (f.name, _ship(_read(f)))
        for f in sorted(country.glob("culture_*.md"))
    ]


def build_country_zips(dist: Path) -> list[str]:
    """One zip per complete country: its culture files + README/REFERENCES/hofstede."""
    built = []
    for region, country in complete_countries():
        items = _country_culture_items(country)
        for name in ("README.md", "REFERENCES.md"):
            f = country / name
            if f.is_file():
                items.append((name, _ship(_read(f))))
        for f in sorted(country.glob("hofstede_*")):
            items.append((f.name, _ship(_read(f)) if f.suffix == ".md" else _read(f)))
        name = f"cultures-{region}-{country.name}.zip"
        _write_zip(dist / name, items)
        built.append(name)
    return built


def _combined_culture_items(countries: list[Path]) -> list[tuple[str, str]]:
    """culture_*.md for several countries (names already unique) + namespaced
    hofstede files, so one zip can hold a whole region or the world."""
    items: list[tuple[str, str]] = []
    for country in countries:
        items += _country_culture_items(country)
        for f in sorted(country.glob("hofstede_*")):
            arc = f"hofstede_{country.name}_{f.name[len('hofstede_'):]}"
            items.append((arc, _ship(_read(f)) if f.suffix == ".md" else _read(f)))
    return items


def build_region_zips(dist: Path) -> list[str]:
    """One zip per region with >=1 complete country."""
    built = []
    by_region: dict[str, list[Path]] = {}
    for region, country in complete_countries():
        by_region.setdefault(region, []).append(country)
    for region, countries in sorted(by_region.items()):
        items = _combined_culture_items(countries)
        readme = _REGIONS / region / "README.md"
        if readme.is_file():
            items.append(("README.md", _ship(_read(readme))))
        name = f"cultures-{region}.zip"
        _write_zip(dist / name, items)
        built.append(name)
    return built


def build_world_zip(dist: Path) -> list[str]:
    """A single zip with every complete country."""
    countries = [c for _region, c in complete_countries()]
    if not countries:
        return []
    items = _combined_culture_items(countries)
    root_readme = _ROOT / "README.md"
    if root_readme.is_file():
        items.append(("README.md", _ship(_read(root_readme))))
    _write_zip(dist / "cultures-world.zip", items)
    return ["cultures-world.zip"]


# ---------------------------------------------------------------------------
# Engine zips
# ---------------------------------------------------------------------------

def _engine_scaffold_items() -> list[tuple[str, str]]:
    """The shared engine scaffold -- every engine/*.md except the repo-nav
    README. Stack, positions, and the process files (incl. the ladder)."""
    return [
        (f.name, _ship(_read(f)))
        for f in sorted(_ENGINE.glob("*.md"))
        if f.name != "README.md"
    ]


def build_engine_zips(dist: Path) -> list[str]:
    """engine-raw.zip (scaffold only) + one engine-<target>.zip per target."""
    scaffold = _engine_scaffold_items()
    _write_zip(dist / "engine-raw.zip", scaffold)
    built = ["engine-raw.zip"]
    for target in _ENGINE_TARGETS:
        tdir = _ENGINE / target
        items = list(scaffold)
        for name in ("instructions.md", "README.md"):
            f = tdir / name
            if f.is_file():
                items.append((name, _ship(_read(f), target)))
        name = f"engine-{target}.zip"
        _write_zip(dist / name, items)
        built.append(name)
    return built


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def build_all(dist: Path) -> list[str]:
    """Build every zip into ``dist``; return the produced filenames."""
    dist.mkdir(parents=True, exist_ok=True)
    built: list[str] = []
    built += build_country_zips(dist)
    built += build_region_zips(dist)
    built += build_world_zip(dist)
    built += build_engine_zips(dist)
    return built


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: python scripts/build_zips.py <dist-dir>", file=sys.stderr)
        return 2
    dist = Path(argv[1])
    built = build_all(dist)
    for name in built:
        print(f"  built {name}")
    print(f"build_zips: {len(built)} zip(s) into {dist}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
