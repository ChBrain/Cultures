"""Test SHA256 lock integrity for bag YAMLs.

Each bag in `regions/<region>/<country>/hofstede_bag*.yaml` may have an
entry in `data/hofstede_bag_locks.yaml` recording its SHA256. When the
entry exists, the actual file hash must match — any drift means the bag
was modified without updating the lock, which the diff would normally
catch but might not in CI if the lock entry is updated silently. This
test pins the contract.

Run: python3 -m unittest tests.test_hofstede_bag_locked
"""
from __future__ import annotations

import hashlib
import warnings
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
REGIONS = REPO_ROOT / "regions"
LOCKS_FILE = REPO_ROOT / "data" / "hofstede_bag_locks.yaml"
GLOBAL_DENYLIST_FILE = REPO_ROOT / "data" / "hofstede_denylist.yaml"


def find_hofstede_bags() -> list[Path]:
    if not REGIONS.exists():
        return []
    return [
        bag for bag in REGIONS.rglob("hofstede_bag*.yaml")
        if "lock" not in bag.name and "decision" not in bag.name
    ]


def load_locks() -> dict[str, str]:
    if not LOCKS_FILE.exists():
        return {}
    with LOCKS_FILE.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        return {}
    locks = data.get("locks", {})
    return locks if isinstance(locks, dict) else {}


def compute_sha256(file_path: Path) -> str:
    h = hashlib.sha256()
    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


_BAGS = find_hofstede_bags()


class TestBagLocks:
    """Bag file integrity via SHA256 lock index."""

    def test_locks_file_present(self):
        """The lock index must exist (added in PR #34)."""
        assert LOCKS_FILE.exists(), (
            f"{LOCKS_FILE.relative_to(REPO_ROOT)} missing. The lock index "
            f"is required infrastructure as of Strategy v2."
        )

    @pytest.mark.parametrize("bag_file", _BAGS)
    def test_bag_sha256_matches_lock_when_present(self, bag_file: Path):
        """Bag SHA256 must match lock entry if one exists.

        When no entry exists yet (migration in progress), emit a real
        warning — this is the LLM-changes-the-rules signal. Once a country
        is migrated, the lock entry should land in the same PR as the bag.
        """
        locks = load_locks()
        rel_path = str(bag_file.relative_to(REPO_ROOT))

        if rel_path not in locks:
            warnings.warn(
                f"No lock entry for {rel_path}. After migration, every bag "
                f"must have a SHA in data/hofstede_bag_locks.yaml.",
                UserWarning,
                stacklevel=2,
            )
            return

        expected = locks[rel_path]
        actual = compute_sha256(bag_file)
        assert actual == expected, (
            f"{rel_path}: SHA256 mismatch! "
            f"Expected {expected}, got {actual}. "
            f"The bag was modified without updating data/hofstede_bag_locks.yaml. "
            f"Either revert the bag change or update the lock entry deliberately."
        )

    def test_global_denylist_sha_matches_lock(self):
        """data/hofstede_denylist.yaml is locked the same way as bags.

        Per Strategy v2: the denylist is "another bag-list element" and
        gets the same SHA-protection treatment. A drift means someone
        modified the denylist without updating the lock — visible in the
        diff and required to be intentional.
        """
        if not GLOBAL_DENYLIST_FILE.exists():
            pytest.skip("Global denylist file not present")
        locks = load_locks()
        rel = str(GLOBAL_DENYLIST_FILE.relative_to(REPO_ROOT))
        assert rel in locks, (
            f"{rel}: no lock entry. Add SHA256 to data/hofstede_bag_locks.yaml "
            f"to lock the global denylist as part of the bag-system contract."
        )
        expected = locks[rel]
        actual = compute_sha256(GLOBAL_DENYLIST_FILE)
        assert actual == expected, (
            f"{rel}: SHA256 mismatch! Expected {expected}, got {actual}. "
            f"The denylist was modified without updating its lock entry. "
            f"Either revert the change or update the lock deliberately."
        )

    def test_no_orphan_locks(self):
        """Every lock entry must correspond to an existing tracked file."""
        locks = load_locks()
        if not locks:
            pytest.skip("No locks file or empty locks")

        # Tracked = bag YAMLs in regions/ + the global denylist file.
        # Other infrastructure files lock via CODEOWNERS, not SHA.
        tracked_paths = {str(b.relative_to(REPO_ROOT)) for b in _BAGS}
        if GLOBAL_DENYLIST_FILE.exists():
            tracked_paths.add(str(GLOBAL_DENYLIST_FILE.relative_to(REPO_ROOT)))

        orphans = [p for p in locks if p not in tracked_paths]
        if orphans:
            warnings.warn(
                f"Orphan lock entries (files no longer exist): "
                f"{', '.join(orphans)}. Remove from data/hofstede_bag_locks.yaml.",
                UserWarning,
                stacklevel=2,
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
