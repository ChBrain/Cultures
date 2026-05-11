"""Test bag keyword quality.

Hard rules (test failures):
- No within-country collisions: a keyword appears in at most one bag per country.
- Common-word denylist violations are not allowed.
- Keywords are lowercase and use only letters/digits/hyphens (closed compounds OK,
  no leading/trailing hyphens).

Cross-country opposing-polarity is checked as a hard rule with a documented
escape: a divergence is allowed only if BOTH countries' decision logs name
the keyword. Otherwise it fails.

Run: python3 -m unittest tests.test_hofstede_bag_quality
"""
from __future__ import annotations

from pathlib import Path

import re

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
REGIONS = REPO_ROOT / "regions"


# ---------------------------------------------------------------------------
# Global denylist — loaded from data/hofstede_denylist.yaml
# ---------------------------------------------------------------------------
#
# Single source of truth for cross-country denylist words: pronouns,
# deictics, function words across supported languages, and polysemous
# high-frequency English words flagged across NL/IE/SC/WE reviews.
#
# This is a HARD rule with no contextual override. The denylist file is
# locked via SHA in data/hofstede_bag_locks.yaml and protected by
# CODEOWNERS; changes require a deliberate, reviewed PR.
#
# Per-country bags additionally carry their own `denylist:` field — words
# rejected during that country's bootstrap. The combined check is
# (global denylist) ∪ (country denylist).

GLOBAL_DENYLIST_FILE = REPO_ROOT / "data" / "hofstede_denylist.yaml"


def _load_global_denylist() -> set[str]:
    """Load and union all categories from data/hofstede_denylist.yaml."""
    if not GLOBAL_DENYLIST_FILE.exists():
        # Fallback to empty — completeness handled by test_global_denylist_present
        return set()
    with GLOBAL_DENYLIST_FILE.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        return set()
    words: set[str] = set()
    for category in ("pronouns_and_deictics", "function_words", "polysemous_english"):
        entries = data.get(category, [])
        if isinstance(entries, list):
            words.update(str(w).strip().lower() for w in entries if isinstance(w, str))
    return words


GLOBAL_DENYLIST: set[str] = _load_global_denylist()


def _country_denylist(bag: dict) -> set[str]:
    """Return the country-specific denylist from a bag YAML, lowercased."""
    raw = bag.get("denylist", []) or []
    if not isinstance(raw, list):
        return set()
    return {str(w).strip().lower() for w in raw if isinstance(w, str)}


# ---------------------------------------------------------------------------
# Bag discovery + loading
# ---------------------------------------------------------------------------

def find_hofstede_bags() -> list[Path]:
    if not REGIONS.exists():
        return []
    return [
        bag for bag in REGIONS.rglob("hofstede_bag*.yaml")
        if "lock" not in bag.name and "decision" not in bag.name
    ]


def load_bag(bag_file: Path) -> dict:
    with bag_file.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def country_decisions_text(bag_file: Path) -> str:
    """Return decisions.md content as lowercase string, or empty if absent."""
    decisions = bag_file.parent / "hofstede_decisions.md"
    if not decisions.exists():
        return ""
    return decisions.read_text(encoding="utf-8").lower()


_BAGS = find_hofstede_bags()


def test_global_denylist_present_and_nonempty():
    """data/hofstede_denylist.yaml must exist and have all three categories."""
    assert GLOBAL_DENYLIST_FILE.exists(), (
        f"{GLOBAL_DENYLIST_FILE.relative_to(REPO_ROOT)} missing. The global "
        f"denylist is required infrastructure as of Strategy v2."
    )
    with GLOBAL_DENYLIST_FILE.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    assert isinstance(data, dict), "denylist YAML top-level must be a mapping"
    for category in ("pronouns_and_deictics", "function_words", "polysemous_english"):
        assert category in data, f"denylist missing required category `{category}`"
        assert isinstance(data[category], list), f"`{category}` must be a list"
        assert data[category], f"`{category}` is empty — at minimum the listed examples must be present"
    assert GLOBAL_DENYLIST, "GLOBAL_DENYLIST union came out empty after loading"


# ---------------------------------------------------------------------------
# Within-country tests
# ---------------------------------------------------------------------------

class TestBagQuality:
    """Per-bag rules: no collisions, no denylist words, proper formatting."""

    @pytest.mark.parametrize("bag_file", _BAGS)
    def test_no_within_country_collisions(self, bag_file: Path):
        bag = load_bag(bag_file)
        bags = bag.get("bags", {})

        seen: dict[str, tuple[str, str]] = {}
        for dimension, polarities in bags.items():
            if not isinstance(polarities, dict):
                continue
            for polarity, keywords in polarities.items():
                if not isinstance(keywords, list):
                    continue
                for keyword in keywords:
                    if not isinstance(keyword, str):
                        continue
                    key = keyword.lower()
                    if key in seen:
                        prev_dim, prev_pol = seen[key]
                        pytest.fail(
                            f"{bag_file.relative_to(REPO_ROOT)}: collision "
                            f"on `{keyword}` — appears in both "
                            f"{prev_dim}.{prev_pol} and {dimension}.{polarity}"
                        )
                    seen[key] = (dimension, polarity)

    @pytest.mark.parametrize("bag_file", _BAGS)
    def test_keywords_not_in_global_denylist(self, bag_file: Path):
        """No bag word may appear in data/hofstede_denylist.yaml."""
        bag = load_bag(bag_file)
        country = bag.get("country", "unknown")

        for dimension, polarities in bag.get("bags", {}).items():
            if not isinstance(polarities, dict):
                continue
            for polarity, keywords in polarities.items():
                if not isinstance(keywords, list):
                    continue
                for keyword in keywords:
                    if not isinstance(keyword, str):
                        continue
                    assert keyword.lower() not in GLOBAL_DENYLIST, (
                        f"{bag_file.relative_to(REPO_ROOT)} ({country}): "
                        f"`{keyword}` in {dimension}.{polarity} is in the "
                        f"global denylist (data/hofstede_denylist.yaml). "
                        f"Hard rule, no contextual override — the matcher "
                        f"does exact-word matching."
                    )

    @pytest.mark.parametrize("bag_file", _BAGS)
    def test_keywords_not_in_country_denylist(self, bag_file: Path):
        """No bag word may appear in this country's own `denylist:` field."""
        bag = load_bag(bag_file)
        country = bag.get("country", "unknown")
        country_deny = _country_denylist(bag)

        if not country_deny:
            return  # empty country denylist is acceptable

        for dimension, polarities in bag.get("bags", {}).items():
            if not isinstance(polarities, dict):
                continue
            for polarity, keywords in polarities.items():
                if not isinstance(keywords, list):
                    continue
                for keyword in keywords:
                    if not isinstance(keyword, str):
                        continue
                    assert keyword.lower() not in country_deny, (
                        f"{bag_file.relative_to(REPO_ROOT)} ({country}): "
                        f"`{keyword}` in {dimension}.{polarity} is in this "
                        f"country's own denylist field. The Skill rejected "
                        f"this word for this country; the bag must not contain it."
                    )

    @pytest.mark.parametrize("bag_file", _BAGS)
    def test_country_denylist_field_present(self, bag_file: Path):
        """Bag YAML must have a `denylist:` field (empty list acceptable)."""
        bag = load_bag(bag_file)
        country = bag.get("country", "unknown")
        assert "denylist" in bag, (
            f"{bag_file.relative_to(REPO_ROOT)} ({country}): missing required "
            f"`denylist:` field. Use `denylist: []` if no country-specific "
            f"rejections; the field itself is mandatory per the Skill contract."
        )

    @pytest.mark.parametrize("bag_file", _BAGS)
    def test_keywords_properly_formatted(self, bag_file: Path):
        """Lowercase, alphanumeric + hyphens + apostrophes only.

        Multi-word phrases with spaces are NOT allowed under the closed-compound
        convention (`langetermijn`, not `lange termijn`). The matcher uses
        word-boundary regex; spaces would split keywords across boundaries.
        """
        bag = load_bag(bag_file)
        country = bag.get("country", "unknown")

        for dimension, polarities in bag.get("bags", {}).items():
            if not isinstance(polarities, dict):
                continue
            for polarity, keywords in polarities.items():
                if not isinstance(keywords, list):
                    continue
                for keyword in keywords:
                    if not isinstance(keyword, str):
                        continue
                    location = f"{dimension}.{polarity}"
                    rel = bag_file.relative_to(REPO_ROOT)

                    assert keyword == keyword.lower(), (
                        f"{rel} ({country}): `{keyword}` in {location} "
                        f"is not lowercase."
                    )
                    assert all(c.isalnum() or c in "-'" for c in keyword), (
                        f"{rel} ({country}): `{keyword}` in {location} "
                        f"has invalid characters (only letters, digits, "
                        f"hyphens, apostrophes allowed; no spaces)."
                    )
                    assert not (keyword.startswith("-") or keyword.endswith("-")), (
                        f"{rel} ({country}): `{keyword}` in {location} "
                        f"has leading or trailing hyphen."
                    )


# ---------------------------------------------------------------------------
# Cross-country opposing-polarity (hard rule with documented exception)
# ---------------------------------------------------------------------------

class TestCrossCountryQuality:
    """Cross-country opposing-polarity is a hard rule with documented exception.

    A keyword appearing in (country A, dim X, high) and (country B, dim X, low)
    means the validator scores the same word as evidence for opposite cultural
    traits across countries — incoherent unless explicitly justified.

    Exception: if BOTH countries' `hofstede_decisions.md` mention the keyword
    by name, the per-country register reasoning is documented and the
    divergence is allowed.
    """

    def test_no_undocumented_cross_country_opposing_collisions(self):
        if not _BAGS:
            pytest.skip("No bags to compare")

        # Build global index: keyword (lowercase) -> list of (country, dim, polarity, bag_file)
        index: dict[str, list[tuple[str, str, str, Path]]] = {}
        for bag_file in _BAGS:
            bag = load_bag(bag_file)
            country = bag.get("country", str(bag_file.parent.name))
            for dimension, polarities in bag.get("bags", {}).items():
                if not isinstance(polarities, dict):
                    continue
                for polarity, keywords in polarities.items():
                    if not isinstance(keywords, list):
                        continue
                    for kw in keywords:
                        if not isinstance(kw, str):
                            continue
                        index.setdefault(kw.lower(), []).append(
                            (country, dimension, polarity, bag_file)
                        )

        violations = []
        for keyword, locations in index.items():
            if len(locations) < 2:
                continue
            for i, (c1, d1, p1, bf1) in enumerate(locations):
                for c2, d2, p2, bf2 in locations[i + 1:]:
                    if d1 != d2 or p1 == p2 or c1 == c2:
                        continue
                    # Same dimension, opposite polarities, different countries.
                    # Check that BOTH countries' decision logs reference the keyword.
                    log1 = country_decisions_text(bf1)
                    log2 = country_decisions_text(bf2)
                    kw_pat = re.compile(r'\b' + re.escape(keyword) + r'\b')
                    in_log1 = bool(kw_pat.search(log1))
                    in_log2 = bool(kw_pat.search(log2))
                    documented = in_log1 and in_log2
                    if not documented:
                        violations.append(
                            f"`{keyword}`: {c1}.{d1}.{p1} vs {c2}.{d2}.{p2} — "
                            f"undocumented divergence (decisions logs missing entry "
                            f"in {c1 if not in_log1 else c2})"
                        )

        assert not violations, (
            "Cross-country opposing-polarity collisions without documented "
            "per-country register reasoning:\n  "
            + "\n  ".join(violations)
            + "\n\nResolve each by either dropping the keyword from one country "
            "or adding an entry to BOTH countries' hofstede_decisions.md "
            "explaining the per-country register difference."
        )


# Pre-migration state visibility — pytest.skip (not pass) when zero bags exist.
def test_bag_collection_status():
    """During pre-migration (zero bags), skip rather than silently pass."""
    bags = find_hofstede_bags()
    if not bags:
        pytest.skip(
            "No bags found — parametrized tests above collected zero cases. "
            "Expected during pre-migration."
        )
