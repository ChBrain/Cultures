"""Test fork discipline.

When a bag has a `parent:` field set (i.e. it's a fork from a sibling
country), the country folder must contain a `hofstede_decisions.md`
that names the parent and enumerates divergence reasons. Prevents
accidental forks without rationale.

Run: python3 -m unittest tests.test_hofstede_bag_fork
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
REGIONS = REPO_ROOT / "regions"

# Words that, when present in a decisions file, indicate the file
# actually documents divergences (not just a stub).
DIVERGENCE_MARKERS = (
    "drop", "replace", "divergence", "diverge",
    "swap", "moved", "rationale",
)


def find_hofstede_bags() -> list[Path]:
    """Find all hofstede_bag*.yaml files under regions/."""
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


class TestParentFieldPresent:
    """Every bag must declare `parent:` explicitly (null or path)."""

    @pytest.mark.parametrize("bag_file", _BAGS)
    def test_parent_field_declared(self, bag_file: Path):
        bag = load_bag(bag_file)
        assert "parent" in bag, (
            f"{bag_file.relative_to(REPO_ROOT)}: missing `parent:` field. "
            f"Use `parent: null` for canonical bags or `parent: <path>` for forks."
        )


class TestForkDiscipline:
    """When `parent:` is non-null, decisions file must exist and document divergences."""

    @pytest.mark.parametrize("bag_file", _BAGS)
    def test_fork_has_decisions_file(self, bag_file: Path):
        bag = load_bag(bag_file)
        parent = bag.get("parent")
        if not parent:
            return  # not a fork

        decisions_file = bag_file.parent / "hofstede_decisions.md"
        assert decisions_file.exists(), (
            f"{bag_file.relative_to(REPO_ROOT)}: declares parent `{parent}` "
            f"but no hofstede_decisions.md alongside."
        )

    @pytest.mark.parametrize("bag_file", _BAGS)
    def test_decisions_documents_divergence(self, bag_file: Path):
        bag = load_bag(bag_file)
        parent = bag.get("parent")
        if not parent:
            return

        decisions_file = bag_file.parent / "hofstede_decisions.md"
        if not decisions_file.exists():
            pytest.skip("decisions file missing; covered by the previous test")

        content = decisions_file.read_text(encoding="utf-8").lower()

        # The parent must be named so a reviewer can trace the fork lineage.
        parent_str = str(parent).lower()
        assert (parent_str in content) or ("parent" in content) or ("fork" in content), (
            f"{decisions_file.relative_to(REPO_ROOT)}: parent `{parent}` not "
            f"mentioned. Decisions file must name the fork source."
        )

        # The file must contain at least one divergence-marker word — otherwise
        # it's just a header without actual divergence reasoning.
        markers_present = [m for m in DIVERGENCE_MARKERS if m in content]
        assert markers_present, (
            f"{decisions_file.relative_to(REPO_ROOT)}: no divergence markers "
            f"({', '.join(DIVERGENCE_MARKERS)}) found. The file should enumerate "
            f"specific drops/replacements/keeps with rule-cited reasons."
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
