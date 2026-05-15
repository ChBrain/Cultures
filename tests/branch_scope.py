"""Branch classification and scope rules for the Cultures repo.

Single source of truth for the scope contract:
- Which branch names count as "culture" work
- Which branch names count as "governance" work
- Which paths each branch kind may modify

Culture work has three nesting scopes, all of which converge on
``culture/release`` (the integration target):

  Scope     Branch name pattern        Allowed paths under regions/
  -------   ------------------------   ------------------------------
  country   ``culture/<country>``      ``regions/<region>/<country>/**``
  region    ``culture/<region>``       ``regions/<region>/**``
  world     ``culture/staging``        ``regions/**``
            ``culture/release``        ``regions/**``

Country and region slugs are resolved against the actual ``regions/``
directory layout — a typo in the branch name fails fast instead of
silently widening scope to all cultures.

Governance work is anything that defines or enforces repository rules:
the pre-commit hook, CI workflows, branch-scope module, validators,
and the data sources those validators consult. Editing these from a
generic ``chore/*`` or ``fix/*`` branch would let an automated
contributor (or an LLM) silently weaken the very gates that protect
culture content. So governance edits are walled into their own kind:

  Scope          Branch name pattern         Allowed paths
  ------------   -------------------------   --------------------------------
  governance     ``governance/<name>``       governance paths + safe metadata
  other          ``chore/*``, ``fix/*``, …   everything except regions/** and
                                              governance paths

Used by:
- .githooks/pre-commit (local enforcement, all four directions)
- (planned) CI workflow (server-side mirror — closes --no-verify and Web UI bypass)

Don't relax the regex or paths without understanding the security model.
See .github/copilot-instructions.md > "Branch Scope Guards".
"""
from __future__ import annotations

import fnmatch
import re
from pathlib import Path

# Anchored regex avoids silent bypasses on near-miss branch names.
# Country/region/world culture work all share this shape; the slug after
# the slash is resolved against the on-disk regions/ tree to pick the
# narrower allowed-path prefix.
CULTURE_BRANCH_PATTERN = re.compile(r"^culture/[a-z0-9][a-z0-9_.-]*$")

# Governance work: dedicated kind so edits to the rules themselves are
# visible in the branch name and gateable in CI.
GOVERNANCE_BRANCH_PATTERN = re.compile(r"^governance/[a-z0-9][a-z0-9_.-]*$")

# Sync branches funnel main's HEAD into culture/release. They carry no new
# commits — the branch is a snapshot of main used as a PR head so the merge
# into culture/release can be reviewed and audited. Because the content is
# identical to main, scope is unrestricted (anything main has is allowed).
SYNC_BRANCH_PATTERN = re.compile(r"^sync/[a-z0-9][a-z0-9_.-]*$")

# World-level integration slugs: may touch all of regions/**.
# These are the integration targets feature branches merge into;
# everything else under culture/* must resolve to a country or region.
WORLD_SLUGS = frozenset({"staging", "release"})

# Metadata files allowed on culture branches alongside regions/** changes.
# Exact path match — `subdir/.gitignore` is NOT safe; only the listed paths.
#
# Cross-boundary files (data lives outside regions/ but belongs in a culture
# migration PR alongside the per-country changes):
#   - ``data/hofstede_bag_locks.yaml`` — bag migration PRs (culture/<country>)
#     update the lock entry for the country in the same commit that adds the
#     bag YAML. Strategy v2 carves it out explicitly.
#   - ``data/v2_migrated_countries.txt`` — per-country opt-in to v2-strict L4a
#     validation. Migration PRs (culture/<country>) add the country here in
#     the same commit that renames persona_* -> male_*/female_* and adds the
#     khai declaration footers.
SAFE_PATTERNS = frozenset({
    ".validation-stamp",
    ".bump-type",
    ".gitignore",
    ".editorconfig",
    "data/hofstede_bag_locks.yaml",
    "data/v2_migrated_countries.txt",
})

# Governance territory: files that define or enforce repository rules.
# Two surfaces:
#   - GOVERNANCE_DIR_PREFIXES: every path under these prefixes is governance.
#   - GOVERNANCE_GLOB_PATTERNS: fnmatch globs, evaluated against the full path.
#
# Editing any of these on a non-governance branch is rejected so weakening
# the gates is never a silent change; it has to happen on a ``governance/*``
# branch where CI can require an explicit justification.
GOVERNANCE_DIR_PREFIXES = (
    ".githooks/",
    ".github/workflows/",
)

GOVERNANCE_GLOB_PATTERNS = (
    "tests/branch_scope.py",
    "tests/test_*.py",
    "tests/validate_*.py",
    "tests/requirements.txt",
    "tests/language_exceptions.txt",
    "scripts/validate.py",
    "scripts/validate_*.py",
    "scripts/setup-hooks.sh",
    "scripts/setup-hooks.bat",
    "scripts/audit_readme_bands.py",
    "scripts/update_hofstede_readme.py",
    "data/hofstede_denylist.yaml",
    "data/hofstede_keywords.py",
    "data/hofstede_scores.json",
    "data/hofstede_bag_loader.py",
    "data/language_policy.yaml",
    "data/phrase_denylist.txt",
    "docs/BRANCHING.md",
    ".worktree/WORKTREES.md",
    ".worktree/.gitignore",
)

_DEFAULT_REPO_ROOT = Path(__file__).resolve().parent.parent


def classify_branch(branch: str) -> str:
    """Return 'main', 'culture', 'governance', 'sync', or 'other'."""
    if branch == "main":
        return "main"
    if CULTURE_BRANCH_PATTERN.match(branch):
        return "culture"
    if GOVERNANCE_BRANCH_PATTERN.match(branch):
        return "governance"
    if SYNC_BRANCH_PATTERN.match(branch):
        return "sync"
    return "other"


def is_governance_path(path: str) -> bool:
    """Return True if the path is governance territory.

    Governance = files that define or enforce repository rules: hooks,
    workflows, the branch-scope module, validators, and the data the
    validators consult. The check is the single source of truth used by
    both the ``governance`` kind (must touch only these) and the
    ``other`` kind (must touch none of these).
    """
    for prefix in GOVERNANCE_DIR_PREFIXES:
        if path.startswith(prefix):
            return True
    for pat in GOVERNANCE_GLOB_PATTERNS:
        if fnmatch.fnmatchcase(path, pat):
            return True
    return False


def _world_topology(repo_root: Path) -> tuple[set[str], dict[str, str]]:
    """Walk regions/ and return (region_slugs, country_to_region).

    The topology is derived from disk so the contract self-updates when
    a country or region is added. A missing regions/ dir returns empties,
    which makes every culture/<slug> branch fall through to ``None`` in
    ``culture_scope`` and surface as a scope error.
    """
    regions_dir = repo_root / "regions"
    region_slugs: set[str] = set()
    country_to_region: dict[str, str] = {}
    if not regions_dir.is_dir():
        return region_slugs, country_to_region
    for region_path in sorted(regions_dir.iterdir()):
        if not region_path.is_dir() or region_path.name.startswith("."):
            continue
        region = region_path.name
        region_slugs.add(region)
        for country_path in sorted(region_path.iterdir()):
            if country_path.is_dir() and not country_path.name.startswith("."):
                country_to_region[country_path.name] = region
    return region_slugs, country_to_region


def culture_scope(
    branch_name: str,
    repo_root: Path = _DEFAULT_REPO_ROOT,
) -> str | None:
    """Resolve a ``culture/<slug>`` branch to its allowed path prefix.

    Returns the prefix that every staged file under regions/ must start
    with, or ``None`` if the slug doesn't resolve to a known world,
    region, or country. Resolution order is world > region > country, so
    a slug that collides between layers always picks the broader scope
    (the broader name is what a maintainer would type for the broader
    branch).
    """
    if not CULTURE_BRANCH_PATTERN.match(branch_name):
        return None
    slug = branch_name[len("culture/"):]
    if slug in WORLD_SLUGS:
        return "regions/"
    region_slugs, country_to_region = _world_topology(repo_root)
    if slug in region_slugs:
        return f"regions/{slug}/"
    if slug in country_to_region:
        return f"regions/{country_to_region[slug]}/{slug}/"
    return None


def check_scope(
    branch_kind: str,
    staged: list[str],
    branch_name: str = "",
    repo_root: Path = _DEFAULT_REPO_ROOT,
) -> tuple[bool, list[str]]:
    """Verify staged files match the branch's allowed scope.

    Returns (ok, offending_files). Caller prints the failure message;
    keeping this helper print-free makes it easy to unit-test and to
    reuse from CI.

    Culture branches resolve to a country, region, or world-level prefix
    via ``culture_scope``. If ``branch_name`` is missing or its slug
    doesn't resolve, every staged file outside SAFE_PATTERNS is flagged
    as unsafe so the caller can surface the missing-context error rather
    than silently widening scope.

    Governance branches may only touch governance paths (plus the
    SAFE_PATTERNS root files like ``.validation-stamp``). Other branches
    may touch anything except ``regions/`` and governance paths — this is
    the tightening that protects the gates from silent edits.

    'main' is gated separately (no commits at all) and is treated as a
    no-op here so a dry-run on main doesn't claim scope violations.
    """
    if branch_kind == "culture":
        prefix = culture_scope(branch_name, repo_root) if branch_name else None
        if prefix is None:
            unsafe = [f for f in staged if f not in SAFE_PATTERNS]
        else:
            unsafe = [
                f for f in staged
                if not f.startswith(prefix) and f not in SAFE_PATTERNS
            ]
    elif branch_kind == "governance":
        unsafe = [
            f for f in staged
            if not is_governance_path(f) and f not in SAFE_PATTERNS
        ]
    elif branch_kind == "other":
        unsafe = [
            f for f in staged
            if f.startswith("regions/") or is_governance_path(f)
        ]
    elif branch_kind == "sync":
        # Sync branches carry main's content unchanged into culture/release.
        # No scope restriction: the diff reflects whatever main has accumulated.
        unsafe = []
    else:
        unsafe = []
    return not unsafe, unsafe
