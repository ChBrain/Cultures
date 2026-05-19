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
    world     ``culture/release``        ``regions/**``

Country and region slugs are resolved against the actual ``regions/``
directory layout - a typo in the branch name fails fast instead of
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
  fork           ``fork/<name>``             regions/** + safe metadata only

The ``fork`` kind is the lane for external / contributor culture content.
It is the narrowest write scope in the repo - culture files under
``regions/**`` and nothing else: no engine, no scripts, no validators, no
workflows, no governance data. A contribution that arrives as a GitHub fork
PR is re-homed onto a ``fork/<name>`` branch so it runs under the full
same-repo gate set before it can reach ``culture/release``.

Used by:
- .githooks/pre-commit (local enforcement, all four directions)
- (planned) CI workflow (server-side mirror - closes --no-verify and Web UI bypass)

Don't relax the regex or paths without understanding the security model.
See .github/copilot-instructions.md > "Branch Scope Guards".
"""
from __future__ import annotations

import argparse
import fnmatch
import re
import sys
from pathlib import Path
from typing import NamedTuple

# Anchored regex avoids silent bypasses on near-miss branch names.
# Country/region/world culture work all share this shape; the slug after
# the slash is resolved against the on-disk regions/ tree to pick the
# narrower allowed-path prefix.
CULTURE_BRANCH_PATTERN = re.compile(r"^culture/[a-z0-9][a-z0-9_.-]*$")

# Governance work: dedicated kind so edits to the rules themselves are
# visible in the branch name and gateable in CI.
GOVERNANCE_BRANCH_PATTERN = re.compile(r"^governance/[a-z0-9][a-z0-9_.-]*$")

# Sync branches funnel main's HEAD into culture/release. They carry no new
# commits - the branch is a snapshot of main used as a PR head so the merge
# into culture/release can be reviewed and audited. Because the content is
# identical to main, scope is unrestricted (anything main has is allowed).
SYNC_BRANCH_PATTERN = re.compile(r"^sync/[a-z0-9][a-z0-9_.-]*$")

# Fork branches carry external / contributor culture content. They are
# confined to regions/** -- the narrowest write scope -- so an outside
# contribution cannot touch anything executable (hooks, workflows,
# validators) or any governance data. <name> is the contributor handle.
FORK_BRANCH_PATTERN = re.compile(r"^fork/[a-z0-9][a-z0-9_.-]*$")

# World-level integration slug: may touch all of regions/**.
# This is the integration target feature branches merge into;
# everything else under culture/* must resolve to a country or region.
WORLD_SLUGS = frozenset({"release"})

# Metadata files allowed on culture branches alongside regions/** changes.
# Exact path match - `subdir/.gitignore` is NOT safe; only the listed paths.
#
# Cross-boundary files (data lives outside regions/ but belongs in a culture
# migration PR alongside the per-country changes):
#   - ``data/hofstede_bag_locks.yaml`` - bag migration PRs (culture/<country>)
#     update the lock entry for the country in the same commit that adds the
#     bag YAML. Strategy v2 carves it out explicitly.
#   - ``data/v2_migrated_countries.txt`` - per-country opt-in to v2-strict L4a
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
    "tests/culture_metadata.py",
    "tests/conftest.py",
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
    "scripts/migrate_footer_to_frontmatter.py",
    "scripts/build_zips.py",
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
    """Return 'main', 'culture', 'governance', 'sync', 'fork', or 'other'."""
    if branch == "main":
        return "main"
    if CULTURE_BRANCH_PATTERN.match(branch):
        return "culture"
    if GOVERNANCE_BRANCH_PATTERN.match(branch):
        return "governance"
    if SYNC_BRANCH_PATTERN.match(branch):
        return "sync"
    if FORK_BRANCH_PATTERN.match(branch):
        return "fork"
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
    may touch anything except ``regions/`` and governance paths - this is
    the tightening that protects the gates from silent edits.

    Fork branches are the mirror of that: ``regions/**`` plus safe
    metadata and nothing else, so an external contribution is confined
    to culture content and cannot reach an executable or governance path.

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
    elif branch_kind == "fork":
        # Fork branches carry external culture content: regions/** only,
        # plus safe metadata. Everything else -- engine, scripts, tests,
        # workflows, governance data -- is out of scope, so an outside
        # contribution cannot reach an executable or rule-defining surface.
        unsafe = [
            f for f in staged
            if not f.startswith("regions/") and f not in SAFE_PATTERNS
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


# ---------------------------------------------------------------------------
# PR base routing
# ---------------------------------------------------------------------------
#
# classify_branch says what KIND a head branch is; allowed_bases says what it
# is allowed to be PR'd INTO. This is the single source of truth for the
# integration flow -- the pr-gate base check (tests/validate_pr_base.py), the
# operation advisor below, and docs/BRANCHING.md all derive their base routing
# from here, so they cannot drift.
#
# The failure this encodes against: a sync of culture/release's content into
# main, filed as `sync/* -> main`. `sync/*` is the main -> culture/release
# lane; carrying culture/release UP into main is the release PR, whose head
# is culture/release itself.


def allowed_bases(head: str) -> set[str]:
    """Return the PR base branches ``head`` is allowed to target.

    An empty set means ``head`` is not a valid PR head at all (``main``).
    Callers gate on ``base in allowed_bases(head)``.

      culture/<country|region>   -> {culture/release}   funnel through release
      culture/release            -> {main}              release PR
      governance/<name>          -> {main}
      sync/<name>                -> {culture/release}   main -> culture/release
      fork/<name>                -> {culture/release}   external culture content
      chore|fix|feat/*, other    -> {main}
      main                       -> set()               not a valid head
    """
    kind = classify_branch(head)
    if kind == "main":
        return set()
    if kind == "culture":
        slug = head[len("culture/"):]
        # culture/release integrates UP into main; country/region branches
        # must funnel through culture/release first.
        return {"main"} if slug in WORLD_SLUGS else {"culture/release"}
    if kind == "sync":
        return {"culture/release"}
    if kind == "fork":
        # Fork branches carry external culture content; like culture/<country>
        # branches they funnel through the integration branch.
        return {"culture/release"}
    # governance and other (chore/fix/feat/...) both target main.
    return {"main"}


def base_remedy(head: str, base: str) -> str | None:
    """Return a prescriptive fix when ``base`` is wrong for ``head``, else None.

    The single source of the pr-gate base-check teaching output: a rejection
    names the exact correct head/base pair and how to reach it, not just
    "wrong base". Returns ``None`` when the pair is valid.
    """
    allowed = allowed_bases(head)
    if not allowed:
        return (
            f">>> ERROR: '{head}' is not a valid PR head branch.\n"
            "\n"
            "   'main' cannot be a PR head. Move the work onto a culture/*,\n"
            "   governance/*, sync/*, or chore|fix|feat/* branch.\n"
            "   Advisor: python tests/branch_scope.py advise --op <operation>"
        )
    if base in allowed:
        return None

    kind = classify_branch(head)
    lines = [
        f">>> ERROR: PR base '{base}' is not allowed for head '{head}'.",
        "",
        f"   Allowed base for '{head}': {sorted(allowed)}",
        "",
    ]
    if kind == "sync":
        lines += [
            "   A sync/* branch funnels main -> culture/release; its only",
            "   valid base is 'culture/release'.",
            "",
            "   To take culture/release CONTENT INTO main you do not want a",
            "   sync branch at all -- that is the release PR: open a PR with",
            "   head 'culture/release' and base 'main'. Close this PR and",
            "   open culture/release -> main instead.",
        ]
    elif kind == "culture" and head[len("culture/"):] in WORLD_SLUGS:
        lines += [
            "   culture/release is the integration branch; it PRs up into",
            "   'main'. Retarget this PR's base to 'main'.",
        ]
    elif kind == "culture":
        lines += [
            "   Country/region culture work funnels through the integration",
            "   branch first:",
            "     culture/<slug>  -> culture/release   (this PR)",
            "     culture/release -> main              (release PR)",
            "   Retarget this PR's base to 'culture/release'.",
        ]
        if base not in ("main", "culture/release"):
            lines += [
                "",
                f"   '{base}' is not an integration branch. If you based this",
                "   on another feature branch because your culture content",
                "   links files that branch adds (e.g. engine/* files), that",
                "   is a sequencing dependency, not a base: engine work reaches",
                "   culture/release via engine -> main -> sync. Base on",
                "   culture/release and wait for the sync to carry those files",
                "   down -- do not stack on the feature branch (validate.yml",
                "   does not even run for a PR based outside main/culture/release).",
            ]
    elif kind == "fork":
        lines += [
            "   A fork/* branch carries external culture content; like a",
            "   culture/<country> branch it funnels through the integration",
            "   branch. Retarget this PR's base to 'culture/release'.",
        ]
    elif kind == "governance":
        lines.append(
            "   Governance changes go directly to main. Retarget base to 'main'.")
    else:
        lines.append(
            "   chore/fix/feat branches target 'main'. Retarget base to 'main'.")

    lines += [
        "",
        "   Confirm routing: python tests/branch_scope.py advise --op <operation>",
        "   Integration flow: docs/BRANCHING.md",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Failure diagnosis
# ---------------------------------------------------------------------------
#
# check_scope answers "which files are out of scope". That is not enough for a
# contributor -- least of all an LLM -- to act on, because a bare file list has
# two very different causes that demand opposite fixes:
#
#   1. The branch was cut from (or merged) main while its PR base -- typically
#      culture/release -- is stale. The base...HEAD diff then surfaces every
#      file main changed in that gap as if this branch authored it. The fix is
#      to rebase; touching those files is actively wrong.
#   2. The branch genuinely changed an out-of-scope file. The fix is to revert
#      it or move it to the correct branch kind.
#
# diagnose_scope_failure separates the two so render_scope_failure can tell the
# contributor which one they are looking at. The git plumbing (which commit
# touched which file, which commits are on main) is injected, so both helpers
# stay pure and unit-testable without a repo.


def diagnose_scope_failure(
    unsafe,
    *,
    commits_for_file,
    is_on_main,
):
    """Split scope-violating files into (inherited_from_main, genuine).

    ``commits_for_file(path)`` returns the commit SHAs in the PR's
    ``base..HEAD`` range that touched ``path``. ``is_on_main(sha)`` returns
    True when ``sha`` is reachable from ``origin/main``.

    A file is *inherited* when every range commit that touched it is already
    on main: the branch absorbed main's lead over a stale base, so the file
    is not this branch's work. Otherwise it is a *genuine* violation -- this
    branch actually changed an out-of-scope file.

    A file with no range commits is treated as genuine: never silently
    excuse a flagged file just because its history could not be resolved.
    """
    inherited: list[str] = []
    genuine: list[str] = []
    for path in unsafe:
        commits = list(commits_for_file(path))
        if commits and all(is_on_main(sha) for sha in commits):
            inherited.append(path)
        else:
            genuine.append(path)
    return inherited, genuine


def render_scope_failure(
    branch: str,
    base_ref: str,
    inherited: list[str],
    genuine: list[str],
    base_behind_main: int = 0,
) -> str:
    """Render a branch-scope failure as a contributor- and LLM-readable report.

    ``base_behind_main`` is how many commits ``origin/main`` is ahead of the
    PR base; when positive, the base itself needs a sync and the remedy says
    so. The output names the cause explicitly and, for the inherited case,
    states plainly that editing validators/hooks/workflows is the wrong fix
    -- the failure mode this whole helper exists to stop.
    """
    total = len(inherited) + len(genuine)
    lines: list[str] = [
        f"FAIL: branch '{branch}' has {total} file(s) outside its scope.",
        "",
    ]
    if inherited:
        lines.append(
            f"{len(inherited)} of {total} were last changed by commit(s) "
            f"already on 'main' but absent from '{base_ref}'. This branch "
            f"carries main's history -- these files are NOT your work:"
        )
        lines += [f"  - {p}" for p in inherited]
        lines.append("")
    if genuine:
        lines.append(
            f"{len(genuine)} of {total} are genuine scope violations -- "
            f"this branch actually changed out-of-scope file(s):"
        )
        lines += [f"  - {p}" for p in genuine]
        lines.append("")

    if inherited and not genuine:
        lines += [
            f"Cause: this branch was based on 'main' (or had it merged in), "
            f"not on '{base_ref}'. Every flagged file is main's lead, not a "
            f"real violation.",
            "",
            "Do NOT move these files, and do NOT edit validators, hooks, or "
            "workflows to make this check pass -- that is the wrong fix and "
            "will be rejected.",
            "",
            "Fix (no file edits):",
        ]
        step = 1
        if base_behind_main > 0:
            lines.append(
                f"  {step}. sync 'main' -> '{base_ref}' "
                f"({base_behind_main} commit(s) behind) via a sync/* PR"
            )
            step += 1
        lines.append(f"  {step}. git fetch origin")
        lines.append(f"  {step + 1}. git rebase origin/{base_ref}")
    elif inherited and genuine:
        lines += [
            "Cause: this branch carries main's history AND has genuine "
            "out-of-scope edits. Rebase first to clear the inherited files, "
            "then address the genuine violations.",
            "",
            "Fix:",
        ]
        step = 1
        if base_behind_main > 0:
            lines.append(
                f"  {step}. sync 'main' -> '{base_ref}' via a sync/* PR"
            )
            step += 1
        lines.append(
            f"  {step}. git fetch origin && git rebase origin/{base_ref}"
        )
        lines.append(
            f"  {step + 1}. revert the genuine violation(s), or move them to "
            f"the correct branch (governance/* for hooks, workflows, and "
            f"validators)"
        )
    else:  # genuine only
        lines += [
            "Cause: this branch changed file(s) outside its allowed scope. "
            "Hooks, workflows, and validators belong on a governance/* "
            "branch; they cannot ride on a culture/* or other branch.",
            "",
            "Fix: revert the out-of-scope change(s), or move them to the "
            "correct branch kind.",
        ]

    lines += ["", "See docs/BRANCHING.md for the integration flow."]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Culture branch base check
# ---------------------------------------------------------------------------
#
# A culture/<country|region> branch must be cut from culture/release, the
# integration branch -- never from main. Branch creation itself cannot be
# gated (there is no base-aware "branch created" event), so this is detection
# after the first push: a branch cut from main carries commits that are
# already on main but absent from culture/release. The scope check only
# catches that incidentally (when main's lead happens to include out-of-scope
# files); this check catches it directly, on commit ancestry alone.


def misbased_commits(commits, *, is_on_main):
    """Return the commits that prove a culture branch has the wrong base.

    ``commits`` is a list of ``(short_sha, subject)`` pairs reachable from
    the branch's HEAD but not from ``origin/culture/release`` -- the output
    of ``git log culture/release..HEAD``. For a branch correctly cut from
    culture/release these are only its own culture commits, none of which
    are on main yet. ``is_on_main(short_sha)`` returns True when the commit
    is reachable from origin/main; any such commit here means the branch
    was cut from main (or merged it in) instead of the integration branch.
    """
    return [(sha, subject) for sha, subject in commits if is_on_main(sha)]


def render_misbased_branch(
    branch: str,
    offending: list,
    base_ref: str = "culture/release",
) -> str:
    """Render the 'culture branch cut from the wrong base' failure report.

    ``offending`` is the list of ``(short_sha, subject)`` commits on the
    branch that are already on main but absent from ``base_ref`` -- the
    proof the branch was started from main. The remedy replays only the
    branch's own culture commits onto the integration branch.
    """
    lines = [
        f"FAIL: culture branch '{branch}' was started from the wrong base.",
        "",
        f"It carries {len(offending)} commit(s) that are already on 'main' "
        f"but not on '{base_ref}'. A culture/* branch must be cut from the "
        f"integration branch '{base_ref}', never from 'main' -- a branch "
        f"cut from main drags main's lead into the PR diff.",
        "",
        "Commits that should not be here (main's history, not your work):",
    ]
    lines += [f"  {sha}  {subject}" for sha, subject in offending]
    lines += [
        "",
        "Do not edit or revert these commits, and do not edit validators "
        "or workflows to silence this check.",
        "",
        f"Fix: replay only your culture commits onto '{base_ref}':",
        "  git fetch origin",
        f"  git rebase --onto origin/{base_ref} origin/main {branch}",
        "  git push --force-with-lease",
        "",
        "See docs/BRANCHING.md for the integration flow.",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Branch advisor (operation -> prescribed branch)
# ---------------------------------------------------------------------------
#
# classify_branch / check_scope answer "is this branch name wrong?" -- checks
# that fire only AFTER a name was chosen, as a rejection. The advisor answers
# the question a contributor actually has BEFORE `git checkout -b`: "I am
# about to do X; which branch and base must I use?"
#
# Routing is keyed on the *operation*, on purpose. The recurring contributor
# (and LLM) failure is routing by file type -- "this touches a .yml, so it is
# governance" -- when the operation owns the lane: a sync touches workflow
# files too, but it is a sync, not governance.


class BranchAdvice(NamedTuple):
    operation: str
    kind: str       # culture / sync / governance / other
    branch: str     # concrete name when resolvable, else a <template>
    base: str       # required PR base
    start: str      # ref to branch from, "" when not applicable
    scope: str      # human-readable allowed-paths summary
    note: str


# Operation -> lane. The key is what the contributor is trying to DO.
# The PR base is NOT stored here -- advise_operation derives it from
# allowed_bases() so the advisor and the pr-gate base check cannot drift.
_OPERATIONS: dict[str, dict] = {
    "new-country": dict(
        kind="culture", branch="culture/<country>",
        start="origin/culture/release",
        scope="regions/<region>/<country>/** + safe metadata",
        note="One country's culture package.",
    ),
    "new-region": dict(
        kind="culture", branch="culture/<region>",
        start="origin/culture/release",
        scope="regions/<region>/** + safe metadata",
        note="Culture work spanning several countries in one region.",
    ),
    "release": dict(
        kind="culture", branch="culture/release", start="",
        scope="regions/** + safe metadata",
        note="culture/release is the long-lived integration branch -- you do "
             "not create it; you PR it into main.",
    ),
    "sync": dict(
        kind="sync", branch="sync/release-from-main-<date>",
        start="origin/main",
        scope="unrestricted (a snapshot of main)",
        note="Funnel main's HEAD into culture/release. The branch IS main's "
             "tip -- it carries no commits of its own.",
    ),
    "fork": dict(
        kind="fork", branch="fork/<name>",
        start="origin/culture/release",
        scope="regions/** + safe metadata only",
        note="External / contributor culture content. The narrowest write "
             "scope -- culture files only, nothing executable or governance. "
             "Re-home a fork PR's commits here so they run the full gate set.",
    ),
    "governance": dict(
        kind="governance", branch="governance/<name>",
        start="origin/main",
        scope=".githooks/**, .github/workflows/**, validators, the branch "
              "contract, validator data files",
        note="Any change to hooks, CI workflows, validators, or the branch "
             "contract itself.",
    ),
    "chore": dict(
        kind="other", branch="chore/<name>", start="origin/main",
        scope="anything except regions/** and governance paths",
        note="General tooling or docs -- including agent instruction files "
             "(.github/copilot-instructions.md, .claude/, .gemini/, ...).",
    ),
    "fix": dict(
        kind="other", branch="fix/<name>", start="origin/main",
        scope="anything except regions/** and governance paths",
        note="Bug fix outside culture content and governance.",
    ),
    "feat": dict(
        kind="other", branch="feat/<name>", start="origin/main",
        scope="anything except regions/** and governance paths",
        note="New non-culture, non-governance feature.",
    ),
}


def valid_operations() -> list[str]:
    """The operation keys ``advise_operation`` accepts, in registry order."""
    return list(_OPERATIONS)


def advise_operation(
    operation: str,
    slug: str | None = None,
    repo_root: Path = _DEFAULT_REPO_ROOT,
) -> BranchAdvice | None:
    """Return the prescribed branch / base / scope for an intended operation.

    ``slug`` fills the ``<country>``/``<region>`` placeholder for culture
    operations; when it resolves against the on-disk ``regions/`` tree the
    scope is made concrete, and when it does not the scope says so loudly.
    Returns ``None`` for an unknown operation -- callers list
    ``valid_operations()``.
    """
    spec = _OPERATIONS.get(operation)
    if spec is None:
        return None
    branch = spec["branch"]
    scope = spec["scope"]
    if operation in ("new-country", "new-region") and slug:
        branch = f"culture/{slug}"
        prefix = culture_scope(branch, repo_root)
        if prefix is not None:
            scope = f"{prefix}** + safe metadata"
        else:
            noun = "country" if operation == "new-country" else "region"
            scope = (
                f"UNRESOLVED: '{slug}' is not an existing {noun} folder under "
                "regions/ -- check the spelling, or create the folder in the "
                "branch's first commit"
            )
    # Base is derived from allowed_bases (the routing matrix), never stored
    # per-operation, so the advisor and the pr-gate base check cannot drift.
    probe = re.sub(r"<[^>]+>", "x", branch)
    candidates = allowed_bases(probe)
    base = sorted(candidates)[0] if candidates else "main"
    return BranchAdvice(
        operation, spec["kind"], branch, base,
        spec["start"], scope, spec["note"],
    )


def _lane_base(lane: str) -> str:
    """PR base for a lane label from lanes_for_files (may hold a <template>).

    Derived from allowed_bases so the advisor's --files output and the
    pr-gate base check share one routing source.
    """
    candidates = allowed_bases(re.sub(r"<[^>]+>", "x", lane))
    return sorted(candidates)[0] if candidates else "main"


def lane_of_path(path: str, repo_root: Path = _DEFAULT_REPO_ROOT) -> tuple[str, str]:
    """Classify one repo-relative path into the branch lane that owns it.

    Returns ``(lane, kind)``:
      - ``("(safe metadata)", "safe")`` -- SAFE_PATTERNS, allowed on any branch
      - ``("governance/<name>", "governance")``
      - ``("culture/<slug>", "culture")``
      - ``("chore/<name>", "other")``
    """
    if path in SAFE_PATTERNS:
        return ("(safe metadata)", "safe")
    if path.startswith("regions/"):
        parts = path.split("/")
        region_slugs, country_to_region = _world_topology(repo_root)
        if len(parts) >= 3 and parts[2] in country_to_region:
            return (f"culture/{parts[2]}", "culture")
        if len(parts) >= 2 and parts[1] in region_slugs:
            return (f"culture/{parts[1]}", "culture")
        return ("culture/release", "culture")
    if is_governance_path(path):
        return ("governance/<name>", "governance")
    return ("chore/<name>", "other")


def lanes_for_files(
    files, repo_root: Path = _DEFAULT_REPO_ROOT,
) -> dict[str, list[str]]:
    """Group files by the branch lane that owns them.

    More than one non-safe lane in the result means the change spans branch
    kinds and MUST be split into separate branches/PRs -- one cannot ride on
    the other.
    """
    lanes: dict[str, list[str]] = {}
    for f in files:
        lane, _kind = lane_of_path(f, repo_root)
        lanes.setdefault(lane, []).append(f)
    return lanes


def render_operation_advice(advice: BranchAdvice) -> str:
    """Render a BranchAdvice as a copy-pasteable report."""
    lines = [
        f"Operation: {advice.operation}",
        f"Kind:      {advice.kind}",
        f"Branch:    {advice.branch}",
        f"Base:      {advice.base}  (PR target -- nothing else is allowed)",
        f"Scope:     {advice.scope}",
        f"Note:      {advice.note}",
    ]
    if advice.start:
        lines += [
            "",
            "Create it:",
            "  git fetch origin",
            f"  git checkout -b {advice.branch} {advice.start}",
        ]
        if "<" in advice.branch:
            lines.append(
                "  (replace <...> with a short, lowercase, hyphenated name)"
            )
    else:
        lines += ["", "  (existing long-lived branch -- do not create it)"]
    return "\n".join(lines)


def render_files_advice(lanes: dict[str, list[str]]) -> str:
    """Render lanes_for_files() output: one lane, or a SPLIT instruction."""
    non_safe = {k: v for k, v in lanes.items() if k != "(safe metadata)"}
    safe = lanes.get("(safe metadata)", [])

    if not non_safe:
        return ("All listed files are safe metadata -- allowed on any branch "
                "alongside its primary scope.")

    if len(non_safe) == 1:
        lane, files = next(iter(non_safe.items()))
        base = _lane_base(lane)
        lines = [f"All files belong to one lane: {lane}  (base: {base})"]
        lines += [f"  {f}" for f in files]
        if safe:
            lines.append("safe metadata (rides along): " + ", ".join(safe))
        return "\n".join(lines)

    lines = [
        f"SPLIT REQUIRED: these files span {len(non_safe)} branch lanes. "
        "One PR cannot carry them -- open one PR per lane:",
    ]
    for lane, files in non_safe.items():
        base = _lane_base(lane)
        lines.append("")
        lines.append(f"  {lane}  (base: {base})")
        lines += [f"    {f}" for f in files]
    if sum(1 for k in non_safe if k.startswith("culture/")) > 1:
        lines += [
            "",
            "The culture lanes could instead share one culture/<region> "
            "branch if every country is in the same region, or "
            "culture/release for cross-region work.",
        ]
    if safe:
        lines += ["", "Safe metadata rides with any of the above: "
                  + ", ".join(safe)]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """CLI: `python tests/branch_scope.py advise --op OP | --files PATH...`."""
    parser = argparse.ArgumentParser(
        prog="branch_scope.py",
        description=(
            "Branch advisor -- before `git checkout -b`, ask which branch "
            "and base an operation requires."
        ),
    )
    parser.add_argument("mode", choices=["advise"])
    parser.add_argument(
        "--op", metavar="OPERATION",
        help="intended operation: " + ", ".join(valid_operations()),
    )
    parser.add_argument(
        "--slug", metavar="NAME",
        help="country or region slug, for culture operations",
    )
    parser.add_argument(
        "--files", nargs="+", metavar="PATH",
        help="repo-relative paths -- report which lane(s) they belong to",
    )
    args = parser.parse_args(argv)

    if args.op:
        advice = advise_operation(args.op, args.slug)
        if advice is None:
            print(f"Unknown operation: {args.op!r}", file=sys.stderr)
            print("Valid operations: " + ", ".join(valid_operations()),
                  file=sys.stderr)
            return 2
        if "<date>" in advice.branch:
            from datetime import date
            advice = advice._replace(
                branch=advice.branch.replace(
                    "<date>", date.today().isoformat()),
            )
        print(render_operation_advice(advice))
        return 0

    if args.files:
        print(render_files_advice(lanes_for_files(args.files)))
        return 0

    parser.error("give --op OPERATION or --files PATH [PATH ...]")
    return 2


if __name__ == "__main__":
    sys.exit(main())
