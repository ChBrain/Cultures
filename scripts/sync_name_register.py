"""scripts/sync_name_register.py

Reads Name Sources sections from every country REFERENCES.md,
diffs against data/names/name_register.json, and writes an updated register.

Called by .github/workflows/sync_name_register.yml after a culture/* branch
merges to main. Never run manually on a culture branch — that would violate
branch scope rules. The workflow opens a governance/* PR with the result.

Usage (called by the Action, or dry-run locally):
    python scripts/sync_name_register.py [--dry-run]

Exit codes:
    0  register written (or unchanged in dry-run)
    1  parse error in a REFERENCES.md — aborts without writing
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
REGISTER  = REPO_ROOT / "data" / "names" / "name_register.json"
REGIONS   = REPO_ROOT / "regions"

# HTML comment block that carries machine-readable metadata
_META_RE = re.compile(
    r"<!-- name_sources\s+(.*?)-->",
    re.DOTALL,
)
# Markdown table row: | Name | Gender | File | ... |
_ROW_RE = re.compile(
    r"^\|\s*(?P<name>[A-Za-zÀ-ÖØ-öø-ÿ]+)\s*"
    r"\|\s*(?P<gender>male|female|non-binary)\s*"
    r"\|\s*(?P<file>[^|]+?)\s*"
    r"\|.*$"
)


def _parse_meta(block: str) -> dict:
    """Parse key: value lines from the HTML comment block."""
    meta = {}
    for line in block.strip().splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip()
    return meta


def _country_path(references_path: Path) -> str:
    """Derive the repo-relative country folder path from a REFERENCES.md path."""
    return str(references_path.parent.relative_to(REPO_ROOT))


def extract_entries(references_path: Path) -> list[dict]:
    """Extract name register entries from a single REFERENCES.md.

    Returns a list of dicts ready for name_register.json.
    Raises ValueError on parse errors.
    """
    text = references_path.read_text(encoding="utf-8")

    meta_match = _META_RE.search(text)
    if not meta_match:
        return []  # No name_sources section — country not yet registered

    meta = _parse_meta(meta_match.group(1))
    country     = meta.get("country", "").strip()
    cultural_source = meta.get("cultural_source", "").strip()

    if not country:
        raise ValueError(f"{references_path}: name_sources block missing 'country'")
    if not cultural_source:
        raise ValueError(f"{references_path}: name_sources block missing 'cultural_source'")

    # Find the Name Sources table — lines after the comment block
    post = text[meta_match.end():]
    entries = []
    country_folder = _country_path(references_path)

    for line in post.splitlines():
        m = _ROW_RE.match(line.strip())
        if not m:
            continue
        name = m.group("name")
        gender = m.group("gender")
        persona_file = f"{country_folder}/{m.group('file').strip()}"
        entries.append({
            "name":            name,
            "country":         country,
            "gender":          gender,
            "persona_file":    persona_file,
            "cultural_source": cultural_source,
            "added":           str(date.today()),
        })

    return entries


def load_register() -> list[dict]:
    if not REGISTER.exists():
        return []
    data = json.loads(REGISTER.read_text(encoding="utf-8"))
    return data.get("names", [])


def merge(existing: list[dict], fresh: list[dict]) -> tuple[list[dict], list[str]]:
    """Merge fresh entries into existing, keyed by 'name'.

    Returns (merged_list, change_log).
    """
    index = {e["name"]: e for e in existing}
    log = []

    for entry in fresh:
        key = entry["name"]
        if key not in index:
            index[key] = entry
            log.append(f"ADD  {key} ({entry['country']} / {entry['gender']})")
        else:
            old = index[key]
            changed_fields = [
                f for f in ("country", "gender", "persona_file", "cultural_source")
                if old.get(f) != entry.get(f)
            ]
            if changed_fields:
                index[key] = {**old, **{f: entry[f] for f in changed_fields}}
                log.append(f"UPD  {key}: {', '.join(changed_fields)}")

    merged = sorted(index.values(), key=lambda e: (e["country"], e["name"]))
    return merged, log


def main(dry_run: bool = False) -> int:
    errors = []
    fresh_entries: list[dict] = []

    for ref_file in sorted(REGIONS.rglob("REFERENCES.md")):
        try:
            entries = extract_entries(ref_file)
            fresh_entries.extend(entries)
        except ValueError as exc:
            errors.append(str(exc))

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1

    existing = load_register()
    merged, log = merge(existing, fresh_entries)

    if not log:
        print("name_register.json is already up to date.")
        return 0

    print(f"{len(log)} change(s):")
    for line in log:
        print(f"  {line}")

    if dry_run:
        print("[dry-run] no file written.")
        return 0

    REGISTER.parent.mkdir(parents=True, exist_ok=True)
    REGISTER.write_text(
        json.dumps({"names": merged}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Written: {REGISTER.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync name register from REFERENCES.md files")
    parser.add_argument("--dry-run", action="store_true", help="Parse and diff without writing")
    args = parser.parse_args()
    sys.exit(main(dry_run=args.dry_run))
