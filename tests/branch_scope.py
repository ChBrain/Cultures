"""Branch classification and scope rules for the Cultures repo.

Single source of truth for the scope contract:
- Which branch names count as "culture" work
- Which paths each branch kind may modify

Used by:
- .githooks/pre-commit (local enforcement, both directions)
- (planned) CI workflow (server-side mirror — closes --no-verify and Web UI bypass)

Don't relax the regex or paths without understanding the security model.
See .github/copilot-instructions.md > "Branch Scope Guards".
"""
from __future__ import annotations

import re

# Anchored regex avoids silent bypasses on near-miss branch names like
# `feat/culture/x` (slash), `feat/cultures-x` (typo plural),
# `feat/culture` (no name), or `feat/Culture-x` (uppercase). All such
# names classify as 'other' and are blocked from regions/.
CULTURE_BRANCH_PATTERN = re.compile(r"^feat/culture-[a-z0-9][a-z0-9_-]*$")

# Metadata files allowed on culture branches alongside regions/** changes.
# Exact basename match at repo root only — `subdir/.gitignore` is NOT safe.
SAFE_PATTERNS = frozenset({
    ".validation-stamp",
    ".bump-type",
    ".gitignore",
    ".editorconfig",
})


def classify_branch(branch: str) -> str:
    """Return 'main', 'culture', or 'other'."""
    if branch == "main":
        return "main"
    if CULTURE_BRANCH_PATTERN.match(branch):
        return "culture"
    return "other"


def check_scope(branch_kind: str, staged: list[str]) -> tuple[bool, list[str]]:
    """Verify staged files match the branch's allowed scope.

    Returns (ok, offending_files). Caller prints the failure message;
    keeping this helper print-free makes it easy to unit-test and to
    reuse from CI.

    'main' is gated separately (no commits at all) and is treated as a
    no-op here so a dry-run on main doesn't claim scope violations.
    """
    if branch_kind == "culture":
        unsafe = [
            f for f in staged
            if not f.startswith("regions/") and f not in SAFE_PATTERNS
        ]
    elif branch_kind == "other":
        unsafe = [f for f in staged if f.startswith("regions/")]
    else:
        unsafe = []
    return not unsafe, unsafe
