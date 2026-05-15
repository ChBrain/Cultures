"""tests/test_name_register.py

Validates data/names/name_register.json against the two core rules:
  1. Every name is unique across the entire register.
  2. Every entry has a non-empty cultural_source.

Also smoke-tests the sync script's extract/merge logic in isolation
so regressions are caught before they reach the register.

Run:
    pytest tests/test_name_register.py -v
"""
from __future__ import annotations

import json
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
REGISTER  = REPO_ROOT / "data" / "names" / "name_register.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_register() -> list[dict]:
    """Load the register, or return empty list if it doesn't exist yet."""
    if not REGISTER.exists():
        return []
    data = json.loads(REGISTER.read_text(encoding="utf-8"))
    assert isinstance(data, dict), "name_register.json root must be an object"
    assert "names" in data, "name_register.json must have a 'names' key"
    return data["names"]


# ---------------------------------------------------------------------------
# Register-level tests (run against the real file)
# ---------------------------------------------------------------------------

class TestRegisterFile:
    """Tests that run against data/names/name_register.json."""

    def setup_method(self):
        self.entries = load_register()

    def test_register_is_list(self):
        assert isinstance(self.entries, list)

    def test_names_are_unique(self):
        names = [e["name"] for e in self.entries]
        duplicates = {n for n in names if names.count(n) > 1}
        assert not duplicates, (
            f"Duplicate name(s) found in register: {sorted(duplicates)}\n"
            "Each persona name must be unique across all of Cultures."
        )

    def test_cultural_source_present(self):
        missing = [
            e["name"] for e in self.entries
            if not e.get("cultural_source", "").strip()
        ]
        assert not missing, (
            f"Entries missing cultural_source: {missing}\n"
            "Every name must be backed by a named statistical or reference source."
        )

    def test_required_fields(self):
        required = {"name", "country", "gender", "persona_file", "cultural_source", "added"}
        bad = [
            e.get("name", "<unnamed>")
            for e in self.entries
            if not required.issubset(e.keys())
        ]
        assert not bad, f"Entries missing required fields: {bad}"

    def test_gender_values(self):
        allowed = {"male", "female", "non-binary"}
        bad = [
            (e["name"], e.get("gender"))
            for e in self.entries
            if e.get("gender") not in allowed
        ]
        assert not bad, f"Invalid gender values (must be male/female/non-binary): {bad}"

    def test_country_is_iso2(self):
        """Country codes must be 2-letter uppercase ISO 3166-1 alpha-2."""
        bad = [
            (e["name"], e.get("country"))
            for e in self.entries
            if not (isinstance(e.get("country"), str) and
                    len(e["country"]) == 2 and
                    e["country"].isupper())
        ]
        assert not bad, f"Invalid country codes (must be 2-letter uppercase): {bad}"

    def test_sorted_by_country_then_name(self):
        """Register must stay sorted so diffs are clean."""
        keys = [(e["country"], e["name"]) for e in self.entries]
        assert keys == sorted(keys), (
            "name_register.json is not sorted by (country, name).\n"
            "Re-run sync_name_register.py to restore order."
        )

    def test_persona_file_references_exist(self):
        """Every persona_file path must exist in the repo."""
        missing = [
            (e["name"], e["persona_file"])
            for e in self.entries
            if not (REPO_ROOT / e["persona_file"]).exists()
        ]
        assert not missing, (
            f"persona_file paths not found on disk: {missing}\n"
            "Check filename or update the REFERENCES.md table."
        )


# ---------------------------------------------------------------------------
# Unit tests for the sync script logic (isolated, no file I/O)
# ---------------------------------------------------------------------------

import sys
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from sync_name_register import extract_entries, merge  # noqa: E402


class TestExtract:
    """Unit tests for extract_entries() using tmp files."""

    def _write(self, tmp_path: Path, content: str) -> Path:
        f = tmp_path / "REFERENCES.md"
        f.write_text(textwrap.dedent(content), encoding="utf-8")
        return f

    def test_no_section_returns_empty(self, tmp_path):
        f = self._write(tmp_path, "# References\n\nNo name sources here.\n")
        assert extract_entries(f) == []

    def test_extracts_two_names(self, tmp_path):
        f = self._write(tmp_path, """
            ## Name Sources

            <!-- name_sources
            country: DE
            cultural_source: Destatis 2023
            -->

            | Name      | Gender | File                      | Notes |
            |-----------|--------|---------------------------|-------|
            | Christian | male   | persona_christian.md      | top name |
            | Brigitte  | female | persona_brigitte.md       | postwar |
        """)
        entries = extract_entries(f)
        assert len(entries) == 2
        names = {e["name"] for e in entries}
        assert names == {"Christian", "Brigitte"}

    def test_all_fields_populated(self, tmp_path):
        f = self._write(tmp_path, """
            <!-- name_sources
            country: DE
            cultural_source: Destatis 2023
            -->

            | Name | Gender | File          | Notes |
            |------|--------|---------------|-------|
            | Lars | male   | persona_lars.md | - |
        """)
        entry = extract_entries(f)[0]
        assert entry["name"] == "Lars"
        assert entry["country"] == "DE"
        assert entry["gender"] == "male"
        assert entry["cultural_source"] == "Destatis 2023"
        assert entry["persona_file"].endswith("persona_lars.md")
        assert entry["added"]  # non-empty date string

    def test_missing_country_raises(self, tmp_path):
        f = self._write(tmp_path, """
            <!-- name_sources
            cultural_source: Destatis 2023
            -->

            | Name | Gender | File | Notes |
            |------|--------|------|-------|
            | Lars | male   | x.md | - |
        """)
        with pytest.raises(ValueError, match="missing 'country'"):
            extract_entries(f)

    def test_missing_cultural_source_raises(self, tmp_path):
        f = self._write(tmp_path, """
            <!-- name_sources
            country: DE
            -->

            | Name | Gender | File | Notes |
            |------|--------|------|-------|
            | Lars | male   | x.md | - |
        """)
        with pytest.raises(ValueError, match="missing 'cultural_source'"):
            extract_entries(f)

    def test_header_row_skipped(self, tmp_path):
        """The | Name | Gender | ... header row must not become an entry."""
        f = self._write(tmp_path, """
            <!-- name_sources
            country: DE
            cultural_source: Destatis 2023
            -->

            | Name | Gender | File | Notes |
            |------|--------|------|-------|
            | Lars | male   | persona_lars.md | - |
        """)
        entries = extract_entries(f)
        assert len(entries) == 1
        assert entries[0]["name"] == "Lars"


class TestMerge:
    """Unit tests for merge()."""

    def _entry(self, name, country="DE", gender="male", source="Destatis"):
        return {
            "name": name, "country": country, "gender": gender,
            "persona_file": f"regions/{country}/{name}.md",
            "cultural_source": source, "added": "2026-05-15",
        }

    def test_add_new_name(self):
        merged, log = merge([], [self._entry("Lars")])
        assert len(merged) == 1
        assert any("ADD" in l and "Lars" in l for l in log)

    def test_no_duplicate_on_re_run(self):
        existing = [self._entry("Lars")]
        merged, log = merge(existing, [self._entry("Lars")])
        assert len(merged) == 1
        assert log == []  # no change logged

    def test_update_changed_field(self):
        existing = [self._entry("Lars", source="OldSource")]
        fresh    = [self._entry("Lars", source="NewSource")]
        merged, log = merge(existing, fresh)
        assert merged[0]["cultural_source"] == "NewSource"
        assert any("UPD" in l and "Lars" in l for l in log)

    def test_merge_preserves_existing_not_in_fresh(self):
        """Names from countries not in the current fresh batch must survive."""
        existing = [self._entry("Lars", country="DE"), self._entry("Sofia", country="ES")]
        fresh    = [self._entry("Lars", country="DE")]  # only DE this run
        merged, _ = merge(existing, fresh)
        names = {e["name"] for e in merged}
        assert "Sofia" in names  # ES name preserved

    def test_output_sorted(self):
        fresh = [
            self._entry("Zara", country="ES"),
            self._entry("Anna", country="DE"),
            self._entry("Lars", country="DE"),
        ]
        merged, _ = merge([], fresh)
        keys = [(e["country"], e["name"]) for e in merged]
        assert keys == sorted(keys)
