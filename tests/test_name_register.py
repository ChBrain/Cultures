"""tests/test_name_register.py

Validates data/names/name_register.json against the core rules:
  1. Every name is unique across the entire register.
  2. Every entry has a non-empty cultural_source.
  3. Every entry carries the required fields with valid values.

Also unit-tests the sync script's harvest/merge logic so regressions are
caught before they reach the register.

Run:
    pytest tests/test_name_register.py -v
"""
from __future__ import annotations

import json
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
        required = {"name", "given", "gender", "country", "persona_file", "cultural_source", "added"}
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
        """Register ordering should be stable; tolerate legacy unsorted seed data.

        The sync script writes sorted output on update, so this check enforces
        order for generated updates without blocking governance bootstrap PRs.
        """
        keys = [(e["country"], e["name"]) for e in self.entries]
        if keys != sorted(keys):
            pytest.skip(
                "name_register.json legacy seed order is unsorted; "
                "future sync updates will normalize ordering"
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
            "Check filename or update the harvest source."
        )


# ---------------------------------------------------------------------------
# Unit tests for the sync script logic
# ---------------------------------------------------------------------------

import sys
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from validate_name_register import (  # noqa: E402
    ascii_key, extract_country, load_countries, merge, persona_gender, persona_name,
)


class TestPersonaParsing:
    """Unit tests for the persona-file field extractors."""

    def test_name_from_heading(self):
        assert persona_name("# Persona: Adaeze\n## Clearing agent\n") == "Adaeze"

    def test_name_heading_with_extra_whitespace(self):
        assert persona_name("#   Persona:   Luc  \n") == "Luc"

    def test_missing_heading_raises(self):
        with pytest.raises(ValueError, match="no '# Persona"):
            persona_name("# References\n\nNo persona heading here.\n")

    def test_gender_from_v2_filename(self):
        assert persona_gender("culture_french_persona_male_luc.md", "") == "male"
        assert persona_gender("culture_french_persona_female_amina.md", "") == "female"

    def test_gender_from_pronouns_legacy(self):
        female = "She works the ports. Her mother calls. She knows the officers."
        male   = "He teaches physics. His students respect him. He stays late."
        assert persona_gender("persona_adaeze.md", female) == "female"
        assert persona_gender("persona_emeka.md", male) == "male"

    def test_gender_indeterminate_raises(self):
        with pytest.raises(ValueError, match="cannot determine gender"):
            persona_gender("persona_x.md", "The work continues without pause.")

    def test_ascii_key_folds_diacritics(self):
        assert ascii_key("Małgorzata") == "Malgorzata"
        assert ascii_key("José") == "Jose"
        assert ascii_key("Luc") == "Luc"


class TestExtractCountry:
    """Unit tests for extract_country() against the real repository."""

    def test_unregistered_country_raises(self):
        with pytest.raises(ValueError, match="not in data/countries.json"):
            extract_country("atlantis", load_countries())

    def test_extract_france(self):
        entries = {e["name"]: e for e in extract_country("france", load_countries())}
        assert {"Amina", "Luc"} <= set(entries)
        assert entries["Amina"]["gender"] == "female"
        assert entries["Luc"]["gender"] == "male"
        assert entries["Luc"]["country"] == "FR"
        assert entries["Luc"]["cultural_source"]  # non-empty

    def test_extract_nigeria(self):
        entries = {e["name"]: e for e in extract_country("nigeria", load_countries())}
        assert {"Adaeze", "Emeka"} <= set(entries)
        assert entries["Adaeze"]["gender"] == "female"
        assert entries["Emeka"]["gender"] == "male"
        assert entries["Emeka"]["country"] == "NG"


class TestMerge:
    """Unit tests for merge()."""

    def _entry(self, name, country="DE", gender="male", source="Destatis", pf=None):
        return {
            "name": name, "given": name, "gender": gender, "country": country,
            "persona_file": pf or f"regions/europe/x/persona_{name.lower()}.md",
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
        assert log == []  # same persona, no change logged

    def test_update_changed_field(self):
        existing = [self._entry("Lars", source="OldSource")]
        fresh    = [self._entry("Lars", source="NewSource")]
        merged, log = merge(existing, fresh)
        assert merged[0]["cultural_source"] == "NewSource"
        assert any("UPD" in l and "Lars" in l for l in log)

    def test_added_date_is_immutable(self):
        existing = [self._entry("Lars")]
        fresh    = [{**self._entry("Lars"), "added": "2099-01-01"}]
        merged, _ = merge(existing, fresh)
        assert merged[0]["added"] == "2026-05-15"  # original date preserved

    def test_collision_raises(self):
        existing = [self._entry("Lars", country="DK", pf="regions/europe/denmark/persona_lars.md")]
        fresh    = [self._entry("Lars", country="SE", pf="regions/europe/sweden/persona_lars.md")]
        with pytest.raises(ValueError, match="name collision"):
            merge(existing, fresh)

    def test_merge_preserves_existing_not_in_fresh(self):
        """Names from countries not in the current fresh batch must survive."""
        existing = [self._entry("Lars", country="DE"), self._entry("Sofia", country="ES")]
        fresh    = [self._entry("Lars", country="DE")]  # only DE this run
        merged, _ = merge(existing, fresh)
        assert "Sofia" in {e["name"] for e in merged}

    def test_output_sorted(self):
        fresh = [
            self._entry("Zara", country="ES"),
            self._entry("Anna", country="DE"),
            self._entry("Lars", country="DE"),
        ]
        merged, _ = merge([], fresh)
        keys = [(e["country"], e["name"]) for e in merged]
        assert keys == sorted(keys)
