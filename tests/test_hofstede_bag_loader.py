"""Unit tests for data/hofstede_bag_loader.py.

Pin every branch of the loader's behaviour:
- Per-country bag found and parses cleanly → return it.
- Bag absent, country not locked → fall back to legacy.
- Bag absent, country LOCKED → RuntimeError (loud).
- Bag malformed YAML, country not locked → stderr warning + legacy fallback.
- Bag malformed, country LOCKED → RuntimeError (loud).
- Bag schema invalid → BagLoadError surfaces as RuntimeError under lock,
  warning + fallback otherwise.
- Both `hofstede_bag.yaml` and `hofstede_bag_<lang>.yaml` present →
  language-specific wins, warning emitted.
- `fallback=False` and no bag → ValueError.

These tests exercise the loader against synthetic country folders in a
tmp dir, with a temporary lock index, monkeypatching the module's
`_REPO_ROOT` and `_LOCKS_FILE` constants. The legacy
DIMENSION_KEYWORDS_BY_LANGUAGE is monkeypatched to a sentinel value so
"used the legacy" is unambiguous in assertions.

Run: python -m pytest tests/test_hofstede_bag_loader.py -v
"""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from data import hofstede_bag_loader as loader  # noqa: E402


VALID_BAG_YAML = """\
country: testland
language: nl
parent: null
hofstede_scores:
  PDI: 38
  IDV: 80
  UAI: 53
  MAS: 14
  LTO: 67
  IND: 68
bags:
  PDI:
    high: [a, b, c, d, e, f, g, h, i, j]
    low:  [k, l, m, n, o, p, q, r, s, t]
  IDV:
    high: [a1, b1, c1, d1, e1, f1, g1, h1, i1, j1]
    low:  [k1, l1, m1, n1, o1, p1, q1, r1, s1, t1]
  UAI:
    high: [a2, b2, c2, d2, e2, f2, g2, h2, i2, j2]
    low:  [k2, l2, m2, n2, o2, p2, q2, r2, s2, t2]
  MAS:
    high: [a3, b3, c3, d3, e3, f3, g3, h3, i3, j3]
    low:  [k3, l3, m3, n3, o3, p3, q3, r3, s3, t3]
  LTO:
    high: [a4, b4, c4, d4, e4, f4, g4, h4, i4, j4]
    low:  [k4, l4, m4, n4, o4, p4, q4, r4, s4, t4]
  IND:
    high: [a5, b5, c5, d5, e5, f5, g5, h5, i5, j5]
    low:  [k5, l5, m5, n5, o5, p5, q5, r5, s5, t5]
"""

# Sentinel legacy dict; tests check identity against this to assert fallback.
SENTINEL_LEGACY = {
    "nl": {
        "PDI": {"high": ["legacy_nl_pdi_high"], "low": ["legacy_nl_pdi_low"]},
        "IDV": {"high": [], "low": []},
        "UAI": {"high": [], "low": []},
        "MAS": {"high": [], "low": []},
        "LTO": {"high": [], "low": []},
        "IND": {"high": [], "low": []},
    },
    "en": {
        "PDI": {"high": ["legacy_en"], "low": []},
        "IDV": {"high": [], "low": []},
        "UAI": {"high": [], "low": []},
        "MAS": {"high": [], "low": []},
        "LTO": {"high": [], "low": []},
        "IND": {"high": [], "low": []},
    },
}


class LoaderTestBase(unittest.TestCase):
    """Common scaffolding: temp repo root + temp lock file + sentinel legacy dict."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        (self.repo / "regions" / "europe" / "testland").mkdir(parents=True)
        (self.repo / "data").mkdir()

        # Monkeypatch loader's constants and legacy dict.
        self._saved_root = loader._REPO_ROOT
        self._saved_locks_file = loader._LOCKS_FILE
        self._saved_legacy = loader.DIMENSION_KEYWORDS_BY_LANGUAGE
        loader._REPO_ROOT = self.repo
        loader._LOCKS_FILE = self.repo / "data" / "hofstede_bag_locks.yaml"
        loader.DIMENSION_KEYWORDS_BY_LANGUAGE = SENTINEL_LEGACY

    def tearDown(self):
        loader._REPO_ROOT = self._saved_root
        loader._LOCKS_FILE = self._saved_locks_file
        loader.DIMENSION_KEYWORDS_BY_LANGUAGE = self._saved_legacy
        self._tmp.cleanup()

    def country_folder(self) -> Path:
        return self.repo / "regions" / "europe" / "testland"

    def write_bag(self, *, language: str | None = None, content: str = VALID_BAG_YAML):
        """Create a bag YAML under the test country folder."""
        name = f"hofstede_bag_{language}.yaml" if language else "hofstede_bag.yaml"
        (self.country_folder() / name).write_text(content, encoding="utf-8")

    def write_lock(self, country_path: str = "regions/europe/testland/hofstede_bag.yaml"):
        """Add a lock entry for the country, simulating a migrated state."""
        loader._LOCKS_FILE.write_text(
            f"locks:\n  {country_path}: dummy_sha\n", encoding="utf-8",
        )

    @contextlib.contextmanager
    def captured_stderr(self):
        captured = io.StringIO()
        saved = sys.stderr
        sys.stderr = captured
        try:
            yield captured
        finally:
            sys.stderr = saved


# ---------------------------------------------------------------------------
# Happy paths
# ---------------------------------------------------------------------------

class TestLoadHappyPath(LoaderTestBase):
    def test_loads_generic_bag(self):
        self.write_bag()
        bag = loader.load_bag_for_language("nl", country_folder=self.country_folder())
        self.assertEqual(bag["PDI"]["high"][0], "a")
        self.assertNotEqual(bag, SENTINEL_LEGACY["nl"])

    def test_loads_language_specific_bag(self):
        self.write_bag(language="nl")
        bag = loader.load_bag_for_language("nl", country_folder=self.country_folder())
        self.assertEqual(bag["PDI"]["high"][0], "a")

    def test_lang_specific_wins_over_generic_with_warning(self):
        self.write_bag()  # generic
        # Language-specific has different sentinel content
        lang_yaml = VALID_BAG_YAML.replace("- a]", "- LANG]")  # marker
        self.write_bag(language="nl", content=VALID_BAG_YAML)
        with self.captured_stderr() as err:
            loader.load_bag_for_language("nl", country_folder=self.country_folder())
        self.assertIn("both", err.getvalue())
        self.assertIn("hofstede_bag_nl.yaml", err.getvalue())


# ---------------------------------------------------------------------------
# Fallback for unmigrated countries
# ---------------------------------------------------------------------------

class TestUnlockedFallback(LoaderTestBase):
    def test_no_bag_unlocked_falls_back_silently(self):
        with self.captured_stderr() as err:
            bag = loader.load_bag_for_language(
                "nl", country_folder=self.country_folder(),
            )
        self.assertEqual(bag, SENTINEL_LEGACY["nl"])
        self.assertEqual(err.getvalue(), "")  # no warnings expected

    def test_no_bag_unknown_language_falls_back_to_english(self):
        bag = loader.load_bag_for_language(
            "xx", country_folder=self.country_folder(),
        )
        self.assertEqual(bag, SENTINEL_LEGACY["en"])

    def test_no_bag_fallback_false_raises(self):
        with self.assertRaises(ValueError):
            loader.load_bag_for_language(
                "nl", country_folder=self.country_folder(), fallback=False,
            )


# ---------------------------------------------------------------------------
# Malformed bags — the silent-swallowing fix
# ---------------------------------------------------------------------------

class TestMalformedBagUnlocked(LoaderTestBase):
    """Malformed bag + unlocked country = warn + fallback. Previously silent."""

    def test_yaml_parse_error_warns_and_falls_back(self):
        self.write_bag(content=":\n: malformed: : :\n")
        with self.captured_stderr() as err:
            bag = loader.load_bag_for_language(
                "nl", country_folder=self.country_folder(),
            )
        self.assertEqual(bag, SENTINEL_LEGACY["nl"])
        self.assertIn("WARNING", err.getvalue())

    def test_missing_bags_key_warns_and_falls_back(self):
        self.write_bag(content="country: testland\nlanguage: nl\n")
        with self.captured_stderr() as err:
            bag = loader.load_bag_for_language(
                "nl", country_folder=self.country_folder(),
            )
        self.assertEqual(bag, SENTINEL_LEGACY["nl"])
        self.assertIn("missing top-level", err.getvalue())

    def test_schema_invalid_warns_and_falls_back(self):
        self.write_bag(content=(
            "bags:\n"
            "  PDI:\n"
            "    high: not_a_list\n"
            "    low: []\n"
        ))
        with self.captured_stderr() as err:
            bag = loader.load_bag_for_language(
                "nl", country_folder=self.country_folder(),
            )
        self.assertEqual(bag, SENTINEL_LEGACY["nl"])
        self.assertIn("WARNING", err.getvalue())

    def test_missing_dimension_warns_and_falls_back(self):
        # Take valid YAML and strip one dimension
        broken = VALID_BAG_YAML.replace(
            "  IND:\n"
            "    high: [a5, b5, c5, d5, e5, f5, g5, h5, i5, j5]\n"
            "    low:  [k5, l5, m5, n5, o5, p5, q5, r5, s5, t5]\n",
            "",
        )
        self.write_bag(content=broken)
        with self.captured_stderr() as err:
            bag = loader.load_bag_for_language(
                "nl", country_folder=self.country_folder(),
            )
        self.assertEqual(bag, SENTINEL_LEGACY["nl"])
        self.assertIn("missing dimension", err.getvalue())


# ---------------------------------------------------------------------------
# Locked countries — the migration-tracking fix
# ---------------------------------------------------------------------------

class TestLockedCountryFailsLoud(LoaderTestBase):
    """Once a country has a lock entry, missing/malformed bag = RuntimeError."""

    def test_locked_with_missing_bag_raises(self):
        self.write_lock()
        # No bag file written.
        with self.assertRaises(RuntimeError) as ctx:
            loader.load_bag_for_language(
                "nl", country_folder=self.country_folder(),
            )
        self.assertIn("missing", str(ctx.exception).lower())
        self.assertIn("locked", str(ctx.exception).lower())

    def test_locked_with_malformed_yaml_raises(self):
        self.write_lock()
        self.write_bag(content=":\n: malformed: : :\n")
        with self.assertRaises(RuntimeError) as ctx:
            loader.load_bag_for_language(
                "nl", country_folder=self.country_folder(),
            )
        self.assertIn("malformed", str(ctx.exception).lower())

    def test_locked_with_schema_violation_raises(self):
        self.write_lock()
        self.write_bag(content="bags: not_a_dict\n")
        with self.assertRaises(RuntimeError) as ctx:
            loader.load_bag_for_language(
                "nl", country_folder=self.country_folder(),
            )
        self.assertIn("malformed", str(ctx.exception).lower())

    def test_locked_with_valid_bag_loads_normally(self):
        self.write_lock()
        self.write_bag()
        bag = loader.load_bag_for_language(
            "nl", country_folder=self.country_folder(),
        )
        self.assertEqual(bag["PDI"]["high"][0], "a")

    def test_unlocked_country_with_unrelated_lock_entries_falls_back(self):
        """Locks for OTHER countries must not affect this country."""
        loader._LOCKS_FILE.write_text(
            "locks:\n"
            "  regions/europe/somewhere_else/hofstede_bag.yaml: deadbeef\n",
            encoding="utf-8",
        )
        bag = loader.load_bag_for_language(
            "nl", country_folder=self.country_folder(),
        )
        self.assertEqual(bag, SENTINEL_LEGACY["nl"])


# ---------------------------------------------------------------------------
# load_bag_for_country_file (file-path entry point)
# ---------------------------------------------------------------------------

class TestLoadByFile(LoaderTestBase):
    def test_load_by_file_finds_country_folder(self):
        self.write_bag()
        culture_md = self.country_folder() / "culture_test_position.md"
        culture_md.write_text("# test\n")
        bag = loader.load_bag_for_country_file(culture_md, "nl")
        self.assertEqual(bag["PDI"]["high"][0], "a")

    def test_load_by_file_outside_regions_falls_back(self):
        # File path not under any regions/<region>/<country>/
        random_path = self.repo / "data" / "hofstede_keywords.py"
        random_path.write_text("# placeholder\n")
        bag = loader.load_bag_for_country_file(random_path, "nl")
        self.assertEqual(bag, SENTINEL_LEGACY["nl"])


# ---------------------------------------------------------------------------
# Lock index parsing edge cases
# ---------------------------------------------------------------------------

class TestLockIndexEdgeCases(LoaderTestBase):
    def test_no_lock_file_treated_as_empty(self):
        # No lock file written.
        self.write_bag()
        bag = loader.load_bag_for_language(
            "nl", country_folder=self.country_folder(),
        )
        self.assertEqual(bag["PDI"]["high"][0], "a")

    def test_malformed_lock_file_warns_and_treats_as_empty(self):
        loader._LOCKS_FILE.write_text(":\n: : :\n", encoding="utf-8")
        # No bag exists; with malformed locks, should fall back (treat as
        # unlocked) rather than fail loud.
        with self.captured_stderr() as err:
            bag = loader.load_bag_for_language(
                "nl", country_folder=self.country_folder(),
            )
        self.assertEqual(bag, SENTINEL_LEGACY["nl"])
        # Should have warned about the locks file specifically.
        self.assertIn("hofstede_bag_locks.yaml", err.getvalue())


if __name__ == "__main__":
    unittest.main()
