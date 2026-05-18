"""scripts/validate_name_register.py

Harvests persona names from culture persona files and syncs them into
data/names/name_register.json.

The source of truth is the persona file itself, not a hand-authored block:
  - legacy personas:  regions/<region>/<slug>/persona_<name>.md
  - v2 personas:      regions/<region>/<slug>/culture_<adj>_persona_<gender>_<name>.md

For each persona file the script reads:
  - name    -- from the `# Persona: <Name>` heading (ASCII-folded for the key)
  - gender  -- from the v2 filename token, or pronoun frequency for legacy files
  - country -- ISO code + approved name source from data/countries.json

A country must be registered in data/countries.json before its personas can
be synced; an unregistered country is a hard error.

Called by .github/workflows/sync_name_register.yml after culture content
merges to main. The workflow passes each changed country slug via --country.
With no --country, every country in countries.json is harvested (manual reseed).

Usage:
    python scripts/validate_name_register.py [--country SLUG ...] [--dry-run]

Exit codes:
    0  register written (or unchanged / dry-run)
    1  error -- unregistered country, unparseable persona, or name collision
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
REGISTER  = REPO_ROOT / "data" / "names" / "name_register.json"
COUNTRIES = REPO_ROOT / "data" / "countries.json"
REGIONS   = REPO_ROOT / "regions"

# A file is a persona file if its name contains "persona" -- this catches
# every convention (legacy persona_<name>.md, v2 culture_<adj>_persona_<gender>_<name>.md).
_PERSONA_FILE_RE = re.compile(r"persona", re.IGNORECASE)
_HEADING_RE = re.compile(r"^#\s+Persona:\s*(?P<name>.+?)\s*$", re.MULTILINE)
_SHE_RE = re.compile(r"\b(?:she|her|hers|herself)\b", re.IGNORECASE)
_HE_RE  = re.compile(r"\b(?:he|him|his|himself)\b", re.IGNORECASE)

# Fields merge() may update on an existing entry. 'name' is the key and
# 'added' is immutable once first recorded.
_MUTABLE = ("given", "gender", "country", "persona_file", "cultural_source")

# Latin letters NFKD does not decompose into base + combining mark.
_TRANSLIT = str.maketrans({
    "ł": "l", "Ł": "L", "ø": "o", "Ø": "O", "đ": "d", "Đ": "D",
    "ð": "d", "Ð": "D", "ħ": "h", "Ħ": "H", "ı": "i", "ß": "ss",
    "æ": "ae", "Æ": "Ae", "œ": "oe", "Œ": "Oe", "þ": "th", "Þ": "Th",
})


def ascii_key(display: str) -> str:
    """Fold a display name to its ASCII-letter key ('Małgorzata' -> 'Malgorzata')."""
    folded = unicodedata.normalize("NFKD", display.translate(_TRANSLIT))
    folded = "".join(c for c in folded if not unicodedata.combining(c))
    return re.sub(r"[^A-Za-z]", "", folded)


def persona_name(text: str) -> str:
    """Read the display name from a persona file's `# Persona: <Name>` heading."""
    m = _HEADING_RE.search(text)
    if not m:
        raise ValueError("no '# Persona: <Name>' heading")
    return m.group("name").strip()


def persona_gender(filename: str, text: str) -> str:
    """Determine gender: a male/female token following 'persona' in the
    filename, else pronoun frequency in the prose."""
    parts = Path(filename).stem.split("_")
    if "persona" in parts:
        idx = parts.index("persona") + 1
        if idx < len(parts) and parts[idx] in ("male", "female"):
            return parts[idx]
    she = len(_SHE_RE.findall(text))
    he  = len(_HE_RE.findall(text))
    if she > he:
        return "female"
    if he > she:
        return "male"
    raise ValueError(f"{filename}: cannot determine gender (she={she}, he={he})")


def persona_files(country_dir: Path) -> list[Path]:
    """Every .md file in a country folder whose name contains 'persona'."""
    return sorted(
        p for p in country_dir.glob("*.md") if _PERSONA_FILE_RE.search(p.name)
    )


def load_countries() -> dict[str, dict]:
    """Load data/countries.json as an id -> registry-entry map."""
    data = json.loads(COUNTRIES.read_text(encoding="utf-8"))
    return {c["id"]: c for c in data.get("countries", [])}


def find_country_dir(slug: str) -> Path:
    """Locate regions/<region>/<slug>/."""
    matches = sorted(REGIONS.glob(f"*/{slug}"))
    if not matches:
        raise ValueError(f"no country folder regions/*/{slug}")
    return matches[0]


def extract_country(slug: str, countries: dict[str, dict]) -> list[dict]:
    """Extract name register entries for every persona in one country folder.

    Raises ValueError on an unregistered country or an unparseable persona.
    """
    meta = countries.get(slug)
    if meta is None:
        raise ValueError(
            f"country '{slug}' is not in data/countries.json -- register it there first"
        )

    entries = []
    for pf in persona_files(find_country_dir(slug)):
        text = pf.read_text(encoding="utf-8")
        rel = pf.relative_to(REPO_ROOT)
        try:
            display = persona_name(text)
            gender  = persona_gender(pf.name, text)
        except ValueError as exc:
            raise ValueError(f"{rel}: {exc}") from exc
        entries.append({
            "name":            ascii_key(display),
            "given":           display,
            "gender":          gender,
            "country":         meta["anchor"]["iso"],
            "persona_file":    str(rel),
            "cultural_source": meta["name_source"],
            "added":           str(date.today()),
        })
    return entries


def merge(existing: list[dict], fresh: list[dict]) -> tuple[list[dict], list[str]]:
    """Merge fresh entries into existing, keyed by globally-unique 'name'.

    Returns (merged_list, change_log). Raises ValueError on a name collision
    (same name, different persona file).
    """
    index = {e["name"]: e for e in existing}
    log = []

    for entry in fresh:
        key = entry["name"]
        if key not in index:
            index[key] = entry
            log.append(f"ADD  {key} ({entry['country']} / {entry['gender']})")
            continue

        old = index[key]
        if old.get("persona_file") != entry.get("persona_file"):
            raise ValueError(
                f"name collision: '{key}' is used by {old.get('persona_file')} "
                f"and {entry.get('persona_file')} -- names must be globally unique"
            )
        changed = [f for f in _MUTABLE if old.get(f) != entry.get(f)]
        if changed:
            index[key] = {**old, **{f: entry[f] for f in changed}}
            log.append(f"UPD  {key}: {', '.join(changed)}")

    merged = sorted(index.values(), key=lambda e: (e["country"], e["name"]))
    return merged, log


def main(country_slugs: list[str] | None = None, dry_run: bool = False) -> int:
    countries = load_countries()
    slugs = country_slugs if country_slugs else sorted(countries)

    errors: list[str] = []
    fresh: list[dict] = []
    for slug in slugs:
        try:
            fresh.extend(extract_country(slug, countries))
        except ValueError as exc:
            errors.append(str(exc))

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1

    register = json.loads(REGISTER.read_text(encoding="utf-8")) if REGISTER.exists() else {}
    existing = register.get("names", [])

    try:
        merged, log = merge(existing, fresh)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if not log:
        print("name_register.json is already up to date.")
        return 0

    print(f"{len(log)} change(s):")
    for line in log:
        print(f"  {line}")

    if dry_run:
        print("[dry-run] no file written.")
        return 0

    register["names"] = merged
    register.setdefault("_meta", {})["updated"] = str(date.today())
    REGISTER.parent.mkdir(parents=True, exist_ok=True)
    REGISTER.write_text(
        json.dumps(register, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Written: {REGISTER.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync name register from culture persona files")
    parser.add_argument(
        "--country", action="append", dest="countries", metavar="SLUG",
        help="country folder slug to harvest (repeatable); default: all registered countries",
    )
    parser.add_argument("--dry-run", action="store_true", help="parse and diff without writing")
    args = parser.parse_args()
    sys.exit(main(country_slugs=args.countries, dry_run=args.dry_run))
