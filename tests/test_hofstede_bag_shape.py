"""Test bag YAML structural compliance.

Per Strategy v2:
- Exactly 6 dimensions: PDI, IDV, UAI, MAS, LTO, IND.
- Each dimension has both `high` and `low` polarities.
- Each polarity has exactly 10 keywords (non-empty strings).
- Required metadata: country, language, parent, hofstede_scores.

Run: python3 -m unittest tests.test_hofstede_bag_shape
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
REGIONS = REPO_ROOT / "regions"

REQUIRED_DIMENSIONS = {"PDI", "IDV", "UAI", "MAS", "LTO", "IND"}
REQUIRED_POLARITIES = {"high", "low"}
KEYWORDS_PER_POLARITY = 10


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


_BAGS = find_hofstede_bags()


class TestBagShape:
    """Bag structure compliance per Strategy v2."""

    @pytest.mark.parametrize("bag_file", _BAGS)
    def test_bag_has_all_dimensions(self, bag_file: Path):
        bag = load_bag(bag_file)
        rel = bag_file.relative_to(REPO_ROOT)

        assert "bags" in bag, f"{rel}: missing top-level `bags` key"
        bag_dimensions = set(bag["bags"].keys())
        missing = REQUIRED_DIMENSIONS - bag_dimensions
        extra = bag_dimensions - REQUIRED_DIMENSIONS
        assert not missing, f"{rel}: missing dimensions {missing}"
        assert not extra, f"{rel}: unexpected dimensions {extra}"

    @pytest.mark.parametrize("bag_file", _BAGS)
    def test_each_dimension_has_high_and_low(self, bag_file: Path):
        bag = load_bag(bag_file)
        rel = bag_file.relative_to(REPO_ROOT)
        for dimension, polarities in bag["bags"].items():
            assert isinstance(polarities, dict), (
                f"{rel}: bags.{dimension} is not a dict"
            )
            found = set(polarities.keys())
            missing = REQUIRED_POLARITIES - found
            extra = found - REQUIRED_POLARITIES
            assert not missing, f"{rel}: bags.{dimension} missing {missing}"
            assert not extra, f"{rel}: bags.{dimension} has extra {extra}"

    @pytest.mark.parametrize("bag_file", _BAGS)
    def test_each_polarity_has_exact_keywords(self, bag_file: Path):
        bag = load_bag(bag_file)
        rel = bag_file.relative_to(REPO_ROOT)
        for dimension, polarities in bag["bags"].items():
            for polarity, keywords in polarities.items():
                assert isinstance(keywords, list), (
                    f"{rel}: bags.{dimension}.{polarity} not a list"
                )
                count = len(keywords)
                assert count == KEYWORDS_PER_POLARITY, (
                    f"{rel}: bags.{dimension}.{polarity} has {count} keywords, "
                    f"expected exactly {KEYWORDS_PER_POLARITY}"
                )

    @pytest.mark.parametrize("bag_file", _BAGS)
    def test_keywords_are_non_empty_strings(self, bag_file: Path):
        bag = load_bag(bag_file)
        rel = bag_file.relative_to(REPO_ROOT)
        for dimension, polarities in bag["bags"].items():
            for polarity, keywords in polarities.items():
                for i, keyword in enumerate(keywords):
                    assert isinstance(keyword, str), (
                        f"{rel}: bags.{dimension}.{polarity}[{i}] is "
                        f"{type(keyword).__name__}, expected str"
                    )
                    assert keyword.strip(), (
                        f"{rel}: bags.{dimension}.{polarity}[{i}] is empty"
                    )


class TestBagMetadata:
    """Required top-level metadata fields per Strategy v2."""

    @pytest.mark.parametrize("bag_file", _BAGS)
    def test_required_metadata_fields(self, bag_file: Path):
        bag = load_bag(bag_file)
        rel = bag_file.relative_to(REPO_ROOT)
        for field in ("country", "language", "parent", "hofstede_scores", "denylist"):
            assert field in bag, (
                f"{rel}: missing required field `{field}`. "
                f"Per Strategy v2: country, language, parent (null or path), "
                f"hofstede_scores, and denylist (country-specific rejected "
                f"words; empty list `[]` acceptable) are all mandatory."
            )

    @pytest.mark.parametrize("bag_file", _BAGS)
    def test_denylist_field_is_list_of_strings(self, bag_file: Path):
        bag = load_bag(bag_file)
        rel = bag_file.relative_to(REPO_ROOT)
        denylist = bag.get("denylist")
        assert isinstance(denylist, list), (
            f"{rel}: `denylist` must be a list (use `[]` if no country-specific "
            f"rejections). Got {type(denylist).__name__}."
        )
        for i, entry in enumerate(denylist):
            assert isinstance(entry, str), (
                f"{rel}: denylist[{i}] is {type(entry).__name__}, expected str"
            )
            assert entry == entry.lower(), (
                f"{rel}: denylist[{i}] (`{entry}`) must be lowercase"
            )

    @pytest.mark.parametrize("bag_file", _BAGS)
    def test_parent_field_is_null_or_path_string(self, bag_file: Path):
        bag = load_bag(bag_file)
        rel = bag_file.relative_to(REPO_ROOT)
        parent = bag.get("parent")
        assert parent is None or isinstance(parent, str), (
            f"{rel}: `parent` must be null (canonical) or a string path "
            f"(fork from sibling). Got {type(parent).__name__}."
        )

    @pytest.mark.parametrize("bag_file", _BAGS)
    def test_scores_are_integers_0_to_100(self, bag_file: Path):
        bag = load_bag(bag_file)
        rel = bag_file.relative_to(REPO_ROOT)
        scores = bag.get("hofstede_scores", {})
        assert isinstance(scores, dict), (
            f"{rel}: hofstede_scores is not a dict"
        )
        for dimension in REQUIRED_DIMENSIONS:
            assert dimension in scores, (
                f"{rel}: hofstede_scores missing {dimension}"
            )
            score = scores[dimension]
            assert isinstance(score, int), (
                f"{rel}: {dimension} score is {type(score).__name__}, "
                f"expected int"
            )
            assert 0 <= score <= 100, (
                f"{rel}: {dimension} score {score} out of range [0, 100]"
            )

    @pytest.mark.parametrize("bag_file", _BAGS)
    def test_language_field_matches_filename_suffix(self, bag_file: Path):
        """For multilingual countries, `hofstede_bag_<lang>.yaml`'s language
        field must equal `<lang>`."""
        bag = load_bag(bag_file)
        rel = bag_file.relative_to(REPO_ROOT)
        stem = bag_file.stem  # hofstede_bag or hofstede_bag_<lang>
        if stem == "hofstede_bag":
            return  # single-language country; no constraint
        # stem == "hofstede_bag_<lang>"
        prefix = "hofstede_bag_"
        if not stem.startswith(prefix):
            return
        suffix_lang = stem[len(prefix):]
        bag_lang = bag.get("language")
        assert bag_lang == suffix_lang, (
            f"{rel}: filename suffix is `_{suffix_lang}` but `language` "
            f"field is `{bag_lang}`. Multilingual country bags must match."
        )


# Pre-migration state visibility — pytest.skip (not pass) when zero bags exist.
def test_bag_collection_status():
    """Surface bag-collection state explicitly. During pre-migration (zero
    bags), skip with a clear message so 'no parametrized cases ran' isn't
    silently green. Once bags exist, the parametrized tests above run."""
    bags = find_hofstede_bags()
    if not bags:
        pytest.skip(
            "No bags found — parametrized tests above collected zero cases. "
            "This is expected during pre-migration; once any country is "
            "migrated the bag tests start firing."
        )
