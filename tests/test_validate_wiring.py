"""Meta-gate: every tests/test_*.py is invoked by a validate.yml job.

`validate.yml` runs an explicit per-file allowlist -- one job per test
file. A new `tests/test_*.py` therefore silently never runs in CI unless
a job is added for it; there is no catch-all `pytest tests/`. A validator
is dead weight until something invokes it, and nothing checked that
everything is invoked -- the loophole this closes.

This test fails when a test file is neither referenced by a validate.yml
job nor explicitly exempted, so "forgot to wire the gate" cannot pass
review.
"""
from __future__ import annotations

import re
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_WORKFLOW = _ROOT / ".github" / "workflows" / "validate.yml"
_TESTS = _ROOT / "tests"

# Pre-existing test files not yet wired into validate.yml. A visible
# backlog, not a blessing: wire each into a job (then drop it from here)
# or justify the exemption. A NEW test file must NOT be added here -- it
# gets a job instead.
_EXEMPT = frozenset({
    "test_culture_metadata.py",
    "test_generate_available_json.py",
    "test_generate_country_entry.py",
    "test_migrate_footer.py",
    "test_name_register.py",
    "test_release_gating.py",
    "test_validate_language.py",
})


def _test_files_on_disk() -> set[str]:
    return {p.name for p in _TESTS.glob("test_*.py")}


def _test_files_wired() -> set[str]:
    """Test files referenced by a `run:` line in validate.yml."""
    text = _WORKFLOW.read_text(encoding="utf-8")
    return set(re.findall(r"tests/(test_[A-Za-z0-9_]+\.py)", text))


def test_every_test_file_is_wired_or_exempt():
    unwired = sorted(_test_files_on_disk() - _test_files_wired() - _EXEMPT)
    assert not unwired, (
        "test file(s) invoked by no validate.yml job and not exempt: "
        f"{unwired}\n"
        "Add a job to .github/workflows/validate.yml that runs the file, "
        "and add that job to the validate-gate aggregator's `needs`."
    )


def test_exempt_list_has_no_stale_entries():
    """An exempt file that has since been wired -- or deleted -- must drop
    out of _EXEMPT, so the backlog reflects reality."""
    on_disk = _test_files_on_disk()
    wired = _test_files_wired()
    stale = sorted(e for e in _EXEMPT if e not in on_disk or e in wired)
    assert not stale, (
        f"_EXEMPT has stale entries (now wired, or deleted): {stale} -- "
        "remove them from _EXEMPT in tests/test_validate_wiring.py."
    )
