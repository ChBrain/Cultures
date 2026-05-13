#!/usr/bin/env python3
"""Generate complete country documentation with Hofstede integration.

Scaffolds README.md and REFERENCES.md for countries from templates, using
Hofstede scores from data/hofstede_scores.json. This enables consistent,
scalable Hofstede integration across all 198+ cultures.

For countries without empirical Hofstede data, provides approximation guidance
and prompts for best judgment reasoning.

The Content Overview table reflects the **Cultures v2 schema**: 8 canonical
kinds (language, history, position, process, piece, place, male, female)
layered on the 5 KAI structural types (process, position, piece, place,
persona). Every `culture_*.md` file in a v2-migrated country carries a
``*khai: <type>*`` footer declaration that validators read to apply the
right structural contract -- see PR #118 (step 1/5) and
docs/migration/cultures-kind-schema-history-piece-split.md.

Band labels (Low / Moderate / High) match the canonical Hofstede band
contract: 0-39 Low, 40-69 Moderate, 70-100 High. Keep in sync with
``score_to_band()`` in ``scripts/audit_readme_bands.py``.

Usage:
  scripts/scaffold_all_hofstede.py                    # shows what would be generated
  scripts/scaffold_all_hofstede.py --apply            # generates files
  scripts/scaffold_all_hofstede.py --apply COUNTRY    # apply for specific country
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_hofstede_database() -> dict:
    """Load Hofstede scores from data/hofstede_scores.json."""
    db_path = Path(__file__).parent.parent / "data" / "hofstede_scores.json"
    if not db_path.exists():
        raise FileNotFoundError(f"Hofstede database not found: {db_path}")
    
    with open(db_path) as f:
        return json.load(f)


def find_countries() -> list[tuple[Path, str]]:
    """Find all country folders with content."""
    root = Path(__file__).resolve().parent.parent
    regions = root / "regions"
    countries = []
    
    for region_dir in sorted(regions.iterdir()):
        if not region_dir.is_dir() or region_dir.name.startswith("."):
            continue
        for country_dir in sorted(region_dir.iterdir()):
            if not country_dir.is_dir() or country_dir.name.startswith("."):
                continue
            if list(country_dir.glob("culture_*.md")) or list(country_dir.glob("persona_*.md")):
                countries.append((country_dir, country_dir.name))
    
    return countries


def get_hofstede_key(country_dir_name: str) -> str | None:
    """Map country directory name to Hofstede database key."""
    db = load_hofstede_database()
    
    # Direct match
    if country_dir_name in db["scores"]:
        return country_dir_name
    
    # Try variations
    key = country_dir_name.lower().replace("-", "_")
    if key in db["scores"]:
        return key
    
    return None


def generate_readme(country_name: str, scores: dict | None) -> str:
    """Generate README.md content for a country."""
    hofstede_section = ""
    
    if scores:
        rows = []
        for dim in ["PDI", "IDV", "UAI", "MAS", "LTO", "IND"]:
            score = scores[dim]
            
            # Canonical Hofstede band contract: 0-39 Low, 40-69 Moderate,
            # 70-100 High. Keep in sync with score_to_band() in
            # scripts/audit_readme_bands.py.
            if score <= 39:
                level = "**Low**"
            elif score <= 69:
                level = "**Moderate**"
            else:
                level = "**High**"
            
            meanings = {
                "PDI": {"Low": "Equality valued; hierarchy questioned", "Moderate": "Moderate hierarchy", "High": "Hierarchy accepted"},
                "IDV": {"Low": "Collective; group harmony", "Moderate": "Balanced", "High": "Individual achievement"},
                "UAI": {"Low": "Flexible; comfortable with ambiguity", "Moderate": "Balanced", "High": "Structure and predictability"},
                "MAS": {"Low": "Caring and cooperation", "Moderate": "Balanced", "High": "Competitive and achievement-focused"},
                "LTO": {"Low": "Short-term focused", "Moderate": "Balanced", "High": "Long-term planning oriented"},
                "IND": {"Low": "Restraint and discipline", "Moderate": "Balanced", "High": "Indulgence and gratification"},
            }
            
            meaning = meanings[dim].get(level.replace("**", ""), "")
            rows.append(f"| {dim} | {score} | {level} - {meaning} |")
        
        table = "\n".join(rows)
        hofstede_section = f"""## Hofstede Cultural Dimensions - {country_name.replace('_', ' ').title()}

{country_name.replace('_', ' ').title()}'s cultural profile measured against Hofstede's framework:

| Dimension | Score | Profile |
|-----------|-------|---------|
{table}

**Source:** Hofstede et al. (2010). Empirical research published in *Cultures and Organizations*.

### How Dimensions Shape This Culture

The six dimensions inform all eight v2 kinds -- **Language**, **History**, **Position**, **Process**, **Piece**, **Place**, and the **Male / Female personas** -- shaping how each surface expresses the cultural profile. The eight Cultures kinds map to the five KAI structural types (language -> position, history -> piece, male/female -> persona); validators read the `*khai: <type>*` footer on every `culture_*.md` to apply the right structural contract.

---

"""
    else:
        # No Hofstede data - provide template for best judgment approximation
        hofstede_section = """## Hofstede Cultural Dimensions - Approximation

This culture does not have published Hofstede research. Use the table below with **best judgment approximation** based on historical, social, and economic factors:

| Dimension | Score | Reasoning |
|-----------|-------|-----------|
| PDI | TBD | Research power distance orientation |
| IDV | TBD | Research individualism vs. collectivism |
| UAI | TBD | Research tolerance for uncertainty |
| MAS | TBD | Research achievement vs. care orientation |
| LTO | TBD | Research long-term vs. short-term focus |
| IND | TBD | Research indulgence vs. restraint |

**Source:** Best judgment approximation - see REFERENCES.md for reasoning.

**Bands:** Low 0-39, Moderate 40-69, High 70-100 (canonical Hofstede contract).

### How Dimensions Shape This Culture

The six dimensions inform all eight v2 kinds -- **Language**, **History**, **Position**, **Process**, **Piece**, **Place**, and the **Male / Female personas** -- shaping how each surface expresses the cultural profile. The eight Cultures kinds map to the five KAI structural types (language -> position, history -> piece, male/female -> persona); validators read the `*khai: <type>*` footer on every `culture_*.md` to apply the right structural contract.

---

"""
        
    content = f"""# {country_name.replace('_', ' ').title()} - Culture Content

This folder contains culture content for {country_name.replace('_', ' ').lower()}: the language that carries meaning, the pivotal moments of history, the position the culture occupies, the recurring processes, the artifacts and pieces, the defining places, and the male and female personas that inhabit this society.

## Content Overview

The v2 schema requires 8 canonical kinds per country, mapped to the 5 KAI structural types. The KAI type column determines which structural contract (section order, fields, links) validators apply.

| File pattern | Cultures kind | KAI structural type | Purpose |
|------|------|------|---------|
| `culture_*_language_*.md` | Language | position | Language as cultural position (Has / Orders / Loses / Drives) |
| `culture_*_history_*.md` | History | piece | Pivotal historical moment or formative event (Place / Load-bearing / Apparent / Yearbook) |
| `culture_*_position.md` | Position | position | Culture position (state role) - narrative anchor |
| `culture_*_process_*.md` | Process | process | Recurring practice or ritual (Is / Drives / Leaves / Ends) |
| `culture_*_piece_*.md` | Piece | piece | Cultural artifact or concept |
| `culture_*_place_*.md` | Place | place | Defining geographical location |
| `culture_*_male_*.md` | Male persona | persona | Male character carrying the culture's position (Projection / Action / Shadow / Tell) |
| `culture_*_female_*.md` | Female persona | persona | Female character carrying the culture's position |

> Every `culture_*.md` file ends with a `*khai: <type>*` footer where `<type>` is one of `process`, `position`, `piece`, `place`, `persona`. The declaration tells validators which KAI structural contract to apply -- Cultures-specific kinds (`language`, `history`, `male`, `female`) map to a KAI type via the table above. Filename token and footer must agree.

{hofstede_section}

## Content Audit Status

The audit table is ordered by the 8 v2 kinds (language, history, position, process, piece, place, male, female) so reviewers can scan for gaps at a glance.

| File | Audit Status | Verified | Auditor | Date |
|------|--------------|----------|---------|------|
| (pending) | pending | - | - | - |

Audit verdicts: **clean** (fully verified), **minor** (one minor inaccuracy), **issues** (factual error or paraphrase risk).

See [REFERENCES.md](REFERENCES.md) for source attribution and sourcing methodology.

---

*v0.2.0 - Kai Schlueter - Cultures - May 2026*
"""
    return content


def generate_references(country_name: str, scores: dict | None) -> str:
    """Generate REFERENCES.md content for a country."""
    hofstede_section = ""
    
    if scores:
        rows = []
        for dim in ["PDI", "IDV", "UAI", "MAS", "LTO", "IND"]:
            score = scores[dim]
            rows.append(f"| {dim} | {score} | Hofstede Insights | Hofstede et al. (2010), Cultural Database |")
        
        table = "\n".join(rows)
        hofstede_section = f"""## Hofstede Dimensions Sourcing

### {country_name.replace('_', ' ').title()}'s Scores (Empirical Research)

| Dimension | Score | Source | Publication |
|-----------|-------|--------|-------------|
{table}

**Status:** Empirical - All scores derived from Hofstede's peer-reviewed multi-country research.

---

"""
    else:
        hofstede_section = """## Hofstede Dimensions Sourcing

### Best Judgment Approximation

For countries without empirical Hofstede research, this section documents the reasoning behind each dimension score.

| Dimension | Score | Reasoning | Sources |
|-----------|-------|-----------|---------|
| PDI | TBD | Document your reasoning for power distance score | See below |
| IDV | TBD | Document your reasoning for individualism score | See below |
| UAI | TBD | Document your reasoning for uncertainty avoidance score | See below |
| MAS | TBD | Document your reasoning for masculinity score | See below |
| LTO | TBD | Document your reasoning for long-term orientation score | See below |
| IND | TBD | Document your reasoning for indulgence score | See below |

**Status:** Best judgment approximation - reasoning documented below.

---

"""
    
    content = f"""# {country_name.replace('_', ' ').title()} - References & Source Attribution

**Authorship:** Kai Schlueter with AI-assisted drafting
**Content Model:** Facts (verified via sources) + Original expression
**Last Updated:** May 7, 2026

---

## Source Registry

### Official & Institutional Sources

| Source | Scope | Trust Level |
|--------|-------|------------|
| National government websites | Official information | ***** |
| National archives / historical records | Historical documents | ***** |
| National statistical office | Official statistics | ***** |

### Academic & Historical References

| Source | Scope | Trust Level |
|--------|-------|------------|
| University press publications | Historical scholarship | **** |
| National historical institutes | Academic research | **** |

### Secondary References

| Source | Scope | Trust Level |
|--------|-------|------------|
| Wikipedia | General facts, cultural context | *** |
| Britannica | Historical overviews | **** |
| CIA World Factbook | Geographic, demographic data | **** |

### Journalistic & Media Archives

| Source | Scope | Trust Level |
|--------|-------|------------|
| National newspapers | News and investigations | **** |
| International media | External perspective | **** |

---

### Cultural Dimensions Research

| Source | Scope | Trust Level |
|--------|-------|------------|
| Hofstede Insights (hofstede-insights.com) | Cultural Dimensions scores by country | ***** |
| Hofstede, G., Hofstede, G. J., & Minkov, M. (2010). *Cultures and Organizations* | Foundational research on 6 dimensions | ***** |
| ITIM International (geert-hofstede.com) | Original Hofstede research database | ***** |

---

{hofstede_section}

## Verified Facts by File

(To be completed: List each content file with verified facts, grouped by the 8 v2 kinds: language, history, position, process, piece, place, male, female.)

---

## Plagiarism Detection Protocol

### Close-Paraphrase Detection

To avoid accidental plagiarism, we check for **7+ consecutive non-trivial words verbatim** from any source.

### Audit Workflow

When content is spot-checked:

1. **Extract claims:** Identify all distinct factual claims
2. **Verify each:** Search sources in hierarchy order
3. **Check paraphrase risk:** Search source text for 7+ consecutive word matches
4. **Mark verdict:**
   - **clean** - All facts verified, no paraphrase risk
   - **minor** - One minor inaccuracy or weak paraphrase
   - **issues** - Factual error or significant paraphrase risk

---

## How to Report Source Concerns

If you find potential issues:

1. **Open a GitHub issue** in the Cultures repository
2. **Title:** `IP concern: {country_name.replace('_', ' ').title()} - [file name]`
3. **Include:**
   - The file and specific passage
   - The suspected source with link
   - Why you think it's a concern

---

*v0.2.0 - Kai Schlueter - Cultures - May 2026*
"""
    return content


def scaffold_country(country_dir: Path, country_name: str, dry_run: bool = True) -> int:
    """Scaffold or update documentation for a country.
    
    Returns:
        Number of files generated/updated
    """
    db = load_hofstede_database()
    hof_key = get_hofstede_key(country_name)
    scores = db["scores"].get(hof_key) if hof_key else None
    
    changes = 0
    
    # Generate or update README
    readme_path = country_dir / "README.md"
    if not readme_path.exists():
        readme_content = generate_readme(country_name, scores)
        if not dry_run:
            readme_path.write_text(readme_content, encoding="utf-8")
        print(f"  + README.md (created)")
        changes += 1
    
    # Generate or update REFERENCES
    refs_path = country_dir / "REFERENCES.md"
    if not refs_path.exists():
        refs_content = generate_references(country_name, scores)
        if not dry_run:
            refs_path.write_text(refs_content, encoding="utf-8")
        print(f"  + REFERENCES.md (created)")
        changes += 1
    
    if hof_key:
        status = "empirical"
    else:
        status = "needs approximation"
    print(f"  Hofstede: {status}")
    
    return changes


def main():
    parser = argparse.ArgumentParser(description="Scaffold Hofstede documentation for all countries")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default is dry-run)")
    parser.add_argument("country", nargs="?", help="Specific country to scaffold")
    args = parser.parse_args()
    
    countries = find_countries()
    
    if args.country:
        countries = [(d, n) for d, n in countries if n == args.country]
        if not countries:
            print(f"Country not found: {args.country}")
            return 1
    
    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"=== Hofstede Documentation Scaffolding ({mode}) ===\n")
    
    total_changes = 0
    for country_dir, country_name in countries:
        print(f"{country_name}:")
        changes = scaffold_country(country_dir, country_name, dry_run=not args.apply)
        total_changes += changes
    
    print(f"\n{total_changes} files would be created/updated")
    if not args.apply and total_changes > 0:
        print("\nRun with --apply to apply changes:")
        print(f"  python3 scripts/scaffold_all_hofstede.py --apply")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
