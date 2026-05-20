"""Tests for the per-file language dispatcher in tests/validate_language.py.

The dispatcher routes each culture file by its frontmatter ``language:``
field through one of four lanes (Stage 2c of the Nigeria mother-tongue
arc):

    absent / english       -> ROUTE_DEFAULT  (back-compat, runs lingua)
    lingua-known language  -> ROUTE_LINGUA   (deterministic span check)
    NLP-only language      -> ROUTE_NLP      (LLM check from culture-review.yml)
    unknown ISO code       -> ROUTE_UNKNOWN  (hard fail with a named error)

These tests pin the routing contract: absence defaults, lingua-known
files reach the span check, NLP-only files are skipped locally, and an
unregistered code surfaces a clear actionable Issue.

Live smoke test at the end: every ISO in the real policy iso_map resolves
into either the lingua or NLP lane (no registry drift).

Run: python3 -m pytest tests/test_validate_language_dispatch.py -v
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import validate_language  # noqa: E402
from validate_language import (  # noqa: E402
    DEFAULT_LANGUAGE_ISO,
    POLICY_PATH,
    ROUTE_DEFAULT,
    ROUTE_LINGUA,
    ROUTE_NLP,
    ROUTE_UNKNOWN,
    _file_language_iso,
    dispatch_route,
    load_policy,
    unknown_language_issue,
    validate,
)


# A miniature policy that exercises both lanes without depending on the
# repo's live policy. Tests that mean to assert against the real registry
# load POLICY_PATH explicitly.
POLICY_MINI = {
    "languages": ["english", "yoruba"],
    "nlp_languages": ["igbo", "hausa", "pidgin"],
    "prose_sections": {"shown"},
    "min_span_words": 15,
    "iso_map": {
        "en": "english",
        "yo": "yoruba",
        "ig": "igbo",
        "ha": "hausa",
        "pcm": "pidgin",
    },
}


_counter = 0


def _make_culture(tmp_path: Path, body: str, frontmatter: str | None = None) -> Path:
    """Write a culture file with optional frontmatter; return its path."""
    global _counter
    _counter += 1
    country = tmp_path / "regions" / "africa" / "nigeria"
    country.mkdir(parents=True, exist_ok=True)
    text = ""
    if frontmatter is not None:
        text += "---\n" + frontmatter.strip() + "\n---\n"
    text += body
    file_path = country / f"culture_nigerian_position_language_{_counter}.md"
    file_path.write_text(text, encoding="utf-8")
    return file_path


# ---------------------------------------------------------------------
# load_policy: nlp_languages
# ---------------------------------------------------------------------

class TestLoadPolicyNlpLanguages:
    """The new nlp_languages section is optional but must round-trip when
    present. Default-empty keeps every existing test green."""

    def test_repo_policy_includes_nlp_languages(self):
        policy = load_policy(POLICY_PATH)
        assert "nlp_languages" in policy
        assert isinstance(policy["nlp_languages"], list)
        # The Nigeria mother-tongue arc's MVP set.
        for slug in ("igbo", "hausa", "pidgin"):
            assert slug in policy["nlp_languages"], (
                f"{slug!r} expected in data/language_policy.yaml nlp_languages"
            )

    def test_iso_map_covers_every_registered_language(self):
        """Every entry in iso_map must point at a name in either
        `languages` or `nlp_languages`. Drift here means the dispatcher
        can't route the code."""
        policy = load_policy(POLICY_PATH)
        registry = set(policy["languages"]) | set(policy["nlp_languages"])
        unmapped = [
            (iso, name) for iso, name in policy["iso_map"].items()
            if name not in registry
        ]
        assert not unmapped, (
            "iso_map values must appear in `languages` or `nlp_languages`. "
            f"Unmapped: {unmapped}"
        )

    def test_every_registered_language_has_iso_code(self):
        """Every name in `languages` and `nlp_languages` must have at
        least one iso_map entry pointing at it, otherwise the dispatcher
        can never route a file to that lane."""
        policy = load_policy(POLICY_PATH)
        named = set(policy["iso_map"].values())
        missing = [
            slug for slug in policy["languages"] + policy["nlp_languages"]
            if slug not in named
        ]
        assert not missing, (
            "Every registered language must have an iso_map entry "
            f"pointing at it. Missing: {missing}"
        )

    def test_missing_nlp_languages_field_defaults_to_empty(self, tmp_path):
        p = tmp_path / "p.yaml"
        p.write_text(
            "languages: [english]\n"
            "prose_sections: [shown]\n"
            "min_span_words: 15\n"
            "iso_map:\n  en: english\n"
        )
        policy = load_policy(p)
        assert policy["nlp_languages"] == []

    def test_non_list_nlp_languages_raises(self, tmp_path):
        p = tmp_path / "p.yaml"
        p.write_text(
            "languages: [english]\n"
            "nlp_languages: igbo\n"  # string, not list
            "prose_sections: [shown]\n"
            "min_span_words: 15\n"
        )
        with pytest.raises(ValueError):
            load_policy(p)


# ---------------------------------------------------------------------
# _file_language_iso: reading the frontmatter field
# ---------------------------------------------------------------------

class TestFileLanguageISO:
    """The dispatcher reads the ISO via culture_metadata.read_metadata,
    so it works on both YAML frontmatter (canonical) and the legacy
    footer (during the v2 migration window)."""

    def test_returns_iso_from_frontmatter(self, tmp_path):
        f = _make_culture(
            tmp_path, "# Body\n", frontmatter="khai: position\nlanguage: ig\n"
        )
        assert _file_language_iso(f) == "ig"

    def test_lowercases_and_trims(self, tmp_path):
        f = _make_culture(
            tmp_path, "# Body\n", frontmatter='khai: position\nlanguage: "  EN  "\n'
        )
        assert _file_language_iso(f) == "en"

    def test_absent_field_returns_none(self, tmp_path):
        f = _make_culture(
            tmp_path, "# Body\n", frontmatter="khai: position\n"
        )
        assert _file_language_iso(f) is None

    def test_no_frontmatter_returns_none(self, tmp_path):
        f = _make_culture(tmp_path, "# Body\n")
        assert _file_language_iso(f) is None

    def test_unreadable_file_returns_none(self, tmp_path):
        ghost = tmp_path / "missing.md"
        assert _file_language_iso(ghost) is None


# ---------------------------------------------------------------------
# dispatch_route: the routing matrix
# ---------------------------------------------------------------------

class TestDispatchRoute:
    """The three-tier dispatch is the heart of Stage 2c. Every routing
    decision here is encoded as a behavioural test so a regression
    surfaces immediately."""

    def test_absent_language_routes_default_to_english(self, tmp_path):
        """Back-compat: a file with no `language:` field is treated as
        english and routed through lingua. Every existing file in the
        corpus relies on this."""
        f = _make_culture(tmp_path, "# Body\n")
        route, iso, name = dispatch_route(f, POLICY_MINI)
        assert route == ROUTE_DEFAULT
        assert iso == DEFAULT_LANGUAGE_ISO
        assert name == "english"

    def test_lingua_known_routes_lingua(self, tmp_path):
        f = _make_culture(
            tmp_path, "# Body\n", frontmatter="khai: position\nlanguage: yo\n"
        )
        route, iso, name = dispatch_route(f, POLICY_MINI)
        assert route == ROUTE_LINGUA
        assert iso == "yo"
        assert name == "yoruba"

    def test_nlp_only_routes_nlp(self, tmp_path):
        """An ISO that maps to an nlp_languages name skips lingua. The
        NLP gate is the workflow-side language_faithful check."""
        f = _make_culture(
            tmp_path, "# Body\n", frontmatter="khai: position\nlanguage: ig\n"
        )
        route, iso, name = dispatch_route(f, POLICY_MINI)
        assert route == ROUTE_NLP
        assert iso == "ig"
        assert name == "igbo"

    def test_three_letter_iso_routes(self, tmp_path):
        """`pcm` (Nigerian Pidgin) uses a 639-3 code because no 639-1
        exists. The dispatcher must accept any length code in iso_map."""
        f = _make_culture(
            tmp_path, "# Body\n", frontmatter="khai: position\nlanguage: pcm\n"
        )
        route, _, name = dispatch_route(f, POLICY_MINI)
        assert route == ROUTE_NLP
        assert name == "pidgin"

    def test_unknown_iso_hard_fails(self, tmp_path):
        """A code that isn't in iso_map is the most common contributor
        bug -- a typo or a language they forgot to register. Hard fail
        so it surfaces immediately, not as silent english fallback."""
        f = _make_culture(
            tmp_path, "# Body\n", frontmatter="khai: position\nlanguage: xx\n"
        )
        route, iso, name = dispatch_route(f, POLICY_MINI)
        assert route == ROUTE_UNKNOWN
        assert iso == "xx"
        assert name is None

    def test_iso_maps_to_unregistered_name_hard_fails(self, tmp_path):
        """Drift: iso_map points at a name absent from BOTH `languages`
        and `nlp_languages`. Treat the same as an unknown ISO -- the
        registry is broken and the file can't be routed."""
        broken_policy = {
            **POLICY_MINI,
            "iso_map": {**POLICY_MINI["iso_map"], "qq": "quenya"},
        }
        f = _make_culture(
            tmp_path, "# Body\n", frontmatter="khai: position\nlanguage: qq\n"
        )
        route, iso, name = dispatch_route(f, broken_policy)
        assert route == ROUTE_UNKNOWN
        assert iso == "qq"

    def test_default_policy_argument_falls_back_to_repo_policy(self, tmp_path):
        """When called without a policy arg, dispatch_route consults the
        cached repo policy. Tests that don't override it must still get
        a sane answer."""
        validate_language._POLICY = None
        f = _make_culture(
            tmp_path, "# Body\n", frontmatter="khai: position\nlanguage: ig\n"
        )
        route, iso, name = dispatch_route(f)
        assert route == ROUTE_NLP
        assert iso == "ig"
        assert name == "igbo"


# ---------------------------------------------------------------------
# unknown_language_issue: the hard-fail message
# ---------------------------------------------------------------------

class TestUnknownLanguageIssue:
    """The Issue text is the contributor's first encounter with a routing
    failure; the names of both the file and the offending code must
    appear so the fix is obvious."""

    def test_names_file_and_iso(self, tmp_path):
        f = _make_culture(
            tmp_path, "# Body\n", frontmatter="khai: position\nlanguage: xx\n"
        )
        issue = unknown_language_issue(f, "xx")
        assert "xx" in issue.error
        assert "iso_map" in issue.error
        assert issue.verdict
        assert "language_policy.yaml" in issue.verdict


# ---------------------------------------------------------------------
# validate(): end-to-end dispatch
# ---------------------------------------------------------------------

class TestValidateDispatch:
    """validate() is what the orchestrator calls per-file; the dispatch
    behaviour must hold at this layer, not just at dispatch_route."""

    @pytest.fixture(autouse=True)
    def _swap_policy(self, monkeypatch):
        """Use the miniature policy so tests don't depend on the live
        registry (which may add languages over time)."""
        monkeypatch.setattr(validate_language, "_POLICY", POLICY_MINI)
        yield
        monkeypatch.setattr(validate_language, "_POLICY", None)

    def test_nlp_file_returns_no_issues_locally(self, tmp_path):
        """NLP files are skipped locally -- the LLM gate fires from
        culture-review.yml, not from this validator."""
        f = _make_culture(
            tmp_path, "# Body\n", frontmatter="khai: position\nlanguage: ig\n"
        )
        issues = validate(f)
        assert issues == []

    def test_unknown_iso_returns_one_issue(self, tmp_path):
        f = _make_culture(
            tmp_path, "# Body\n", frontmatter="khai: position\nlanguage: xx\n"
        )
        issues = validate(f)
        assert len(issues) == 1
        assert "xx" in issues[0].error

    def test_default_route_runs_through_lingua(self, tmp_path, monkeypatch):
        """A file with no `language:` field falls into ROUTE_DEFAULT,
        which is the same code path as ROUTE_LINGUA. The detector being
        None (lingua not installed) returns [] cleanly -- no crash."""
        f = _make_culture(tmp_path, "# Body\n")
        # Force "lingua absent" so the test doesn't depend on the wheel.
        monkeypatch.setattr(validate_language, "_build_detector", lambda p: None)
        issues = validate(f)
        assert issues == []
