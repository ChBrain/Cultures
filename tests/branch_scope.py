"""Branch classification and scope rules for the Cultures repo.

Single source of truth for the scope contract:
- Which branch names count as "culture" work
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

Used by:
- .githooks/pre-commit (local enforcement, both directions)
- (planned) CI workflow (server-side mirror — closes --no-verify and Web UI bypass)

Don't relax the regex or paths without understanding the security model.
See .github/copilot-instructions.md > "Branch Scope Guards".
"""
from __future__ import annotations

import re
from pathlib import Path

# Anchored regex avoids silent bypasses on near-miss branch names.
# Country/region/world culture work all share this shape; the slug after
# the slash is resolved against the on-disk regions/ tree to pick the
# narrower allowed-path prefix.
CULTURE_BRANCH_PATTERN = re.compile(r"^culture/[a-z0-9][a-z0-9_-]*$")

# World-level integration slugs: may touch all of regions/**.
# These are the integration targets feature branches merge into;
# everything else under culture/* must resolve to a country or region.
WORLD_SLUGS = frozenset({"staging", "release"})

# Metadata files allowed on culture branches alongside regions/** changes.
# Exact path match — `subdir/.gitignore` is NOT safe; only the listed paths.
#
# `data/hofstede_bag_locks.yaml` is the one cross-boundary file: bag migration
# PRs (culture/<country>) need to update the lock entry for the country in
# the same commit that adds the bag YAML. Strategy v2 carves it out explicitly.
SAFE_PATTERNS = frozenset({
    ".validation-stamp",
    ".bump-type",
    ".gitignore",
    ".editorconfig",
    "data/hofstede_bag_locks.yaml",
})

_DEFAULT_REPO_ROOT = Path(__file__).resolve().parent.parent


def classify_branch(branch: str) -> str:
    """Return 'main', 'culture', or 'other'."""
    if branch == "main":
        return "main"
    if CULTURE_BRANCH_PATTERN.match(branch):
        return "culture"
    return "other"


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
    elif branch_kind == "other":
        unsafe = [f for f in staged if f.startswith("regions/")]
    else:
        unsafe = []
    return not unsafe, unsafe
