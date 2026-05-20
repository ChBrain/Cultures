"""Test bag coverage: every country with culture files must have a bag YAML
or an explicit `.no-bag-yet` marker.

Run: python3 -m unittest tests.test_hofstede_bag_completeness
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

import pytest


# Anchor at this file so tests work regardless of CWD.
REPO_ROOT = Path(__file__).resolve().parent.parent
REGIONS = REPO_ROOT / "regions"

sys.path.insert(0, str(REPO_ROOT / "tests"))

from culture_metadata import read_metadata  # noqa: E402
from validate_language import load_policy, POLICY_PATH  # noqa: E402


# NLP-only language files (Igbo, Hausa, Pidgin, ...) are not "scored
# culture content" for bag-completeness purposes -- there's no bag for
# the language, and the NLP language_faithful check (from
# culture-review.yml) is the gate that covers them. Counting an NLP
# file as content would force the country to ship a bag for a language
# no bag exists for.
try:
    _POLICY = load_policy(POLICY_PATH)
    _NLP_LANGUAGES = set(_POLICY.get("nlp_languages") or [])
    _ISO_MAP = _POLICY.get("iso_map") or {}
except Exception:
    _NLP_LANGUAGES = set()
    _ISO_MAP = {}


def _is_nlp_language_file(file_path: Path) -> bool:
    """True if ``file_path``'s frontmatter declares an NLP-only language."""
    if not _NLP_LANGUAGES:
        return False
    try:
        text = file_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    try:
        meta = read_metadata(text)
    except Exception:
        return False
    if not isinstance(meta, dict):
        return False
    raw = meta.get("language")
    if raw is None:
        return False
    iso = str(raw).strip().lower()
    return _ISO_MAP.get(iso) in _NLP_LANGUAGES


def find_countries_with_content() -> dict[Path, list[Path]]:
    """Map each country folder under regions/ to the list of culture content files.

    A country has "content" if it contains at least one `culture_*.md`
    file. Skips README, REFERENCES, decisions, persona files, and all
    hofstede_*.{yaml,md} files since those are not scored culture content.

    Personas are excluded: a persona inhabits a culture, it is not the
    culture, so it carries no culture_ prefix and feeds no Hofstede bag.
    """
    if not REGIONS.exists():
        return {}

    countries: dict[Path, list[Path]] = {}
    for md_file in REGIONS.rglob("*.md"):
        name = md_file.name
        # Positive match: only culture_*.md counts as scored culture content.
        if not name.startswith("culture_"):
            continue
        # NLP-only language files (e.g. culture_nigerian_position_language_igbo.md)
        # are gated by the LLM language_faithful check, not by a keyword
        # bag. Skip them here so a country isn't required to ship a bag
        # for a language no bag exists for.
        if _is_nlp_language_file(md_file):
            continue

        # regions/<region>/<country>/<file>.md → country folder is parts[:3]
        parts = md_file.relative_to(REPO_ROOT).parts
        if len(parts) < 4 or parts[0] != "regions":
            continue
        country_folder = REPO_ROOT / parts[0] / parts[1] / parts[2]
        countries.setdefault(country_folder, []).append(md_file)

    return countries


def find_hofstede_bag_folders() -> set[Path]:
    """Return the set of country folders that contain a hofstede_bag*.yaml."""
    if not REGIONS.exists():
        return set()
    folders: set[Path] = set()
    for bag_file in REGIONS.rglob("hofstede_bag*.yaml"):
        if "lock" in bag_file.name or "decision" in bag_file.name:
            continue
        folders.add(bag_file.parent)
    return folders


class TestBagCompleteness:
    """Every country with content must have bag(s) or an exemption marker."""

    def test_all_countries_have_bags_or_exemption(self):
        """During the migration window (any bag exists), every country with
        content must have either a bag or a `.no-bag-yet` marker. Before
        any country has been migrated (zero bags), the test surfaces the
        un-migrated countries as a warning rather than a failure — there's
        no practical way to land bag-test infrastructure before any bags
        exist otherwise.
        """
        countries = find_countries_with_content()
        bag_countries = find_hofstede_bag_folders()

        missing = []
        for country_folder, content_files in countries.items():
            has_bag = country_folder in bag_countries
            has_exemption = (country_folder / ".no-bag-yet").exists()
            if not has_bag and not has_exemption:
                missing.append({
                    "country": country_folder.relative_to(REPO_ROOT),
                    "n_files": len(content_files),
                    "files": [f.name for f in content_files],
                })

        if not missing:
            return  # everyone has a bag or marker

        if not bag_countries:
            # Pre-migration: zero bags exist anywhere. Surface the un-migrated
            # countries as a warning so the list is visible in CI output, but
            # don't fail — we're still in the bootstrap phase.
            warnings.warn(
                f"Pre-migration state: no bags exist yet, {len(missing)} "
                f"countries with content await migration or `.no-bag-yet` "
                f"marker. This test will start failing once any country is "
                f"migrated; add markers to remaining countries at that point.",
                UserWarning,
                stacklevel=2,
            )
            return

        # Mid-migration: some bags exist, others don't, some have no marker.
        # That's a real gap — fail loudly with the list.
        assert not missing, (
            "Countries with content missing bags or exemption markers:\n"
            + "\n".join(
                f"  {m['country']}: {m['n_files']} files "
                f"({', '.join(m['files'])})"
                for m in missing
            )
        )

    def test_exemption_marker_alongside_content_only(self):
        """`.no-bag-yet` must sit next to content files (not in empty folders)."""
        if not REGIONS.exists():
            pytest.skip("no regions/ folder yet")
        for marker in REGIONS.rglob(".no-bag-yet"):
            country_folder = marker.parent
            content = [
                f for f in country_folder.glob("*.md")
                if f.name.startswith("culture_")
            ]
            assert content, (
                f"{country_folder.relative_to(REPO_ROOT)}/.no-bag-yet exists "
                f"but no culture_*.md files found alongside."
            )

    def test_exempted_countries_are_visible(self):
        """Surface the exemption list as a warning so it stays auditable.

        `.no-bag-yet` is intentionally a stop-gap, not a permanent state.
        Listing exempted countries on every run keeps reviewers reminded.
        """
        if not REGIONS.exists():
            pytest.skip("no regions/ folder yet")
        exempted = sorted(
            str(m.parent.relative_to(REGIONS))
            for m in REGIONS.rglob(".no-bag-yet")
        )
        if exempted:
            warnings.warn(
                f"Countries exempted from bag requirement (.no-bag-yet): "
                f"{', '.join(exempted)}",
                UserWarning,
                stacklevel=2,
            )
