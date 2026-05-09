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

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
REGIONS = REPO_ROOT / "regions"


# ---------------------------------------------------------------------------
# Common-word denylist
# ---------------------------------------------------------------------------
#
# Words that fire on virtually any prose, regardless of cultural context.
# The matcher does exact-word matching, so polysemy + frequency = noise.
#
# This is a HARD rule with no contextual override. Documented examples
# from prior reviews are explicitly listed so they fail loudly if anyone
# tries to add them back.

# Pronouns and deictics across en/de/nl/da/pl/sv/no — these fire on every
# sentence regardless of dimensional content.
PRONOUNS_AND_DEICTICS = {
    # English
    "i", "we", "he", "she", "it", "they", "you", "me", "us", "him", "her", "them",
    "my", "your", "our", "his", "their",
    "this", "that", "these", "those", "here", "there", "now", "then",
    # Dutch
    "ik", "wij", "we", "hij", "zij", "ze", "het", "jij", "u", "men",
    "mijn", "jouw", "uw", "zijn", "haar", "hun",
    "deze", "die", "dat", "hier", "daar", "nu",
    # German
    "ich", "wir", "er", "sie", "es", "du", "ihr", "man",
    "mein", "dein", "sein", "ihr", "unser", "euer",
    "dieser", "jener", "hier", "dort", "jetzt", "da",
    # Danish
    "jeg", "vi", "han", "hun", "den", "det", "du", "I",
    "min", "din", "sin", "vores", "deres",
    "her", "der", "nu", "dengang",
    # Polish
    "ja", "my", "on", "ona", "ono", "ty", "wy", "oni",
    "moj", "twoj", "jego", "jej", "nasz", "wasz", "ich",
    "tu", "tam", "teraz",
}

# Articles, particles, conjunctions, prepositions — function words.
FUNCTION_WORDS = {
    # English
    "a", "an", "the", "and", "or", "but", "if", "as", "of", "to", "in", "on",
    "at", "by", "for", "with", "from", "into", "onto", "out", "up", "down",
    "is", "are", "was", "were", "be", "been", "being", "has", "have", "had",
    "do", "does", "did", "can", "could", "will", "would", "shall", "should",
    "may", "might", "must", "not", "no", "yes", "so", "than",
    "more", "most", "very", "also", "just", "only", "even",
    "all", "each", "every", "both", "some", "any", "few", "many", "much",
    "what", "which", "who", "whom", "whose", "how", "when", "where", "why",
    # Dutch (high-frequency)
    "de", "het", "een", "en", "of", "maar", "want", "dus",
    "is", "zijn", "was", "waren", "ben", "bent", "wordt", "worden",
    "heb", "hebt", "heeft", "hebben", "had", "hadden",
    "doe", "doet", "doen", "deed", "deden",
    "te", "om", "voor", "naar", "op", "in", "uit", "aan", "bij", "met", "van",
    "ook", "wel", "niet", "geen", "meer", "minder",
    # German (high-frequency)
    "der", "die", "das", "den", "dem", "des",
    "ein", "eine", "einen", "einem", "einer", "eines",
    "und", "oder", "aber", "sondern", "denn",
    "ist", "sind", "war", "waren", "bin", "bist", "sein",
    "habe", "hast", "hat", "haben", "hatte", "hatten",
    "tue", "tut", "tun", "tat", "taten",
    "zu", "an", "in", "auf", "bei", "mit", "von", "aus", "nach", "zur",
    "auch", "nur", "noch", "mehr", "weniger",
    # Danish (high-frequency)
    "en", "et", "den", "det", "de",
    "og", "eller", "men", "fordi",
    "er", "var", "været", "har", "havde", "havde",
    "til", "fra", "med", "om", "ved", "for", "af", "pa",
    "ogsa", "kun", "endnu", "mere", "mindre",
    # Polish (high-frequency)
    "i", "a", "ale", "lub", "albo", "ze", "bo", "wiec",
    "jest", "sa", "byl", "byla", "bylo", "byly",
    "do", "od", "z", "w", "na", "po", "przed", "za", "pod", "nad",
    "tez", "tylko", "juz", "wiecej", "mniej",
}

# Polysemous high-frequency English words flagged in prior reviews.
# Each fires on multiple unrelated meanings; the cultural reading would be
# real but cannot be isolated by exact-word matching.
POLYSEMOUS_ENGLISH = {
    "flat",       # tire, note, rate, structure, apartment
    "open",       # door, mind, file, question, wound
    "own",        # verb, pronoun, adjective
    "shared",     # service, mission, file
    "drive",      # verb, car, computer drive
    "past",       # time, prep, adjective
    "support",    # verb, noun, technical
    "together",   # very high frequency
    "control",    # verb, noun, multiple registers
    "concern",    # noun, verb
    "process",    # noun, verb
    "strong",     # too generic
    "direct",     # adjective, verb, noun
    "level",      # noun, adjective, verb
}

COMMON_WORD_DENYLIST = PRONOUNS_AND_DEICTICS | FUNCTION_WORDS | POLYSEMOUS_ENGLISH


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
    def test_keywords_not_in_denylist(self, bag_file: Path):
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
                    assert keyword.lower() not in COMMON_WORD_DENYLIST, (
                        f"{bag_file.relative_to(REPO_ROOT)} ({country}): "
                        f"`{keyword}` in {dimension}.{polarity} is in the "
                        f"common-word denylist (pronouns, function words, or "
                        f"polysemous high-frequency English). Hard rule, "
                        f"no contextual override — the matcher does exact-word "
                        f"matching."
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
                    documented = keyword in log1 and keyword in log2
                    if not documented:
                        violations.append(
                            f"`{keyword}`: {c1}.{d1}.{p1} vs {c2}.{d2}.{p2} — "
                            f"undocumented divergence (decisions logs missing entry "
                            f"in {c1 if keyword not in log1 else c2})"
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
