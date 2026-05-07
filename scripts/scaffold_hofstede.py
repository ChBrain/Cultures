#!/usr/bin/env python3
"""Generate Hofstede documentation for all countries.

Scaffolds country README.md and REFERENCES.md sections with Hofstede dimensions
from a central database (data/hofstede_scores.json). This enables consistent,
scale-able Hofstede integration across all cultures.

Usage:
  scripts/scaffold_hofstede.py                    # shows what would be generated
  scripts/scaffold_hofstede.py --apply            # generates files (creates/updates)
  scripts/scaffold_hofstede.py COUNTRY            # dry-run for specific country
  scripts/scaffold_hofstede.py --apply COUNTRY    # apply for specific country
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def load_hofstede_database() -> dict:
    """Load Hofstede scores from data/hofstede_scores.json."""
    db_path = Path(__file__).parent.parent / "data" / "hofstede_scores.json"
    if not db_path.exists():
        raise FileNotFoundError(f"Hofstede database not found: {db_path}")
    
    with open(db_path) as f:
        return json.load(f)


def find_countries() -> list[tuple[Path, str]]:
    """Find all country folders with content.
    
    Returns: list of (country_dir, country_key) tuples
    """
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
    """Map country directory name to Hofstede database key.
    
    Examples:
      germany → germany
      united_kingdom → united_kingdom
      czech_republic → (no direct match - approximation needed)
    """
    db = load_hofstede_database()
    
    # Direct match
    if country_dir_name in db["scores"]:
        return country_dir_name
    
    # Try lowercase replacement
    key = country_dir_name.lower().replace("-", "_")
    if key in db["scores"]:
        return key
    
    return None


def generate_hofstede_readme_section(scores: dict) -> str:
    """Generate README Hofstede section from scores dict."""
    rows = []
    for dim in ["PDI", "IDV", "UAI", "MAS", "LTO", "IND"]:
        score = scores[dim]
        
        # Determine level (Low/High/Very High)
        if dim in ["PDI", "IDV", "UAI", "MAS"]:
            if score < 33:
                level = "**Low**"
            elif score < 67:
                level = "**Medium**"
            else:
                level = "**High**"
        elif dim == "LTO":
            if score < 33:
                level = "**Short-term Orientation**"
            elif score < 67:
                level = "**Balanced**"
            else:
                level = "**Long-term Orientation**"
        elif dim == "IND":
            if score < 33:
                level = "**Restraint**"
            elif score < 67:
                level = "**Balanced**"
            else:
                level = "**Indulgence**"
        
        # Meaning column
        meanings = {
            "PDI": {"Low": "Equality valued; hierarchy questioned", "Medium": "Moderate hierarchy", "High": "Hierarchy accepted as natural"},
            "IDV": {"Low": "Collective orientation; group harmony", "Medium": "Moderate balance", "High": "Individual achievement prioritized"},
            "UAI": {"Low": "Flexible; comfortable with ambiguity", "Medium": "Moderate; balanced approach", "High": "Structure and predictability preferred"},
            "MAS": {"Low": "Caring; cooperation valued", "Medium": "Moderate balance", "High": "Competitive; achievement focused"},
            "LTO": {"Short-term Orientation": "Present/past focused; tradition", "Balanced": "Balanced perspective", "Long-term Orientation": "Future focused; long-term planning"},
            "IND": {"Restraint": "Self-discipline and restraint", "Balanced": "Balanced approach", "Indulgence": "Gratification and freedom"},
        }
        
        meaning = meanings[dim].get(level.replace("**", ""), "")
        rows.append(f"| {dim} | {score} | {level} - {meaning} |")
    
    table = "\n".join(rows)
    
    section = f"""## Hofstede Cultural Dimensions

This culture is rooted in Hofstede's Cultural Dimensions framework. These scores are **empirical research** from Hofstede's multi-country studies:

| Dimension | Score | Meaning |
|-----------|-------|---------|
{table}

### How Dimensions Shape This Culture

The six dimensions inform the **Position** (how the culture operates), **Pieces** (historical moments where dimensions intersected), **Place** (where dimensions are visible daily), and **Personas** (how individuals navigate these cultural pressures).

**Source:** Hofstede, G., Hofstede, G. J., & Minkov, M. (2010). *Cultures and Organizations: Software of the Mind* (3rd rev. ed.). New York: McGraw-Hill.

---
"""
    return section


def generate_hofstede_references_section(scores: dict) -> str:
    """Generate REFERENCES Hofstede section from scores dict."""
    rows = []
    for dim in ["PDI", "IDV", "UAI", "MAS", "LTO", "IND"]:
        score = scores[dim]
        rows.append(f"| {dim} | {score} | Hofstede Insights | Hofstede et al. (2010), Cultural Database |")
    
    table = "\n".join(rows)
    
    section = f"""### Cultural Dimensions Research

| Source | Scope | Trust Level |
|--------|-------|------------|
| Hofstede Insights (hofstede-insights.com) | Cultural Dimensions scores by country | ⭐⭐⭐⭐⭐ |
| Hofstede, G., Hofstede, G. J., & Minkov, M. (2010). *Cultures and Organizations* | Foundational research on 6 dimensions | ⭐⭐⭐⭐⭐ |
| ITIM International (geert-hofstede.com) | Original Hofstede research database | ⭐⭐⭐⭐⭐ |

---

## Hofstede Dimensions Sourcing

### Culture's Scores (Empirical Research)

| Dimension | Score | Source | Publication |
|-----------|-------|--------|-------------|
{table}

**Status:** Empirical - All scores derived from Hofstede's peer-reviewed multi-country research.

---
"""
    return section


def scaffold_country(country_dir: Path, dry_run: bool = True) -> bool:
    """Scaffold Hofstede documentation for a single country.
    
    Returns:
        True if changes made, False otherwise
    """
    db = load_hofstede_database()
    country_name = country_dir.name
    
    # Find Hofstede key
    hof_key = get_hofstede_key(country_name)
    if not hof_key:
        print(f"-- {country_name}: No Hofstede data found (approximation needed)")
        return False
    
    scores = db["scores"][hof_key]
    
    # Check README
    readme_path = country_dir / "README.md"
    readme_updated = False
    
    if readme_path.exists():
        readme_text = readme_path.read_text(encoding="utf-8")
        if "## Hofstede" not in readme_text:
            if not dry_run:
                # Insert after the title/overview section
                hofstede_section = generate_hofstede_readme_section(scores)
                # Insert before "Sourcing Principle" or at top if not found
                if "## Sourcing" in readme_text:
                    readme_text = readme_text.replace("## Sourcing", hofstede_section + "## Sourcing")
                else:
                    readme_text = hofstede_section + readme_text
                readme_path.write_text(readme_text, encoding="utf-8")
            readme_updated = True
            print(f"  + README: add Hofstede section")
    
    # Check REFERENCES
    refs_path = country_dir / "REFERENCES.md"
    refs_updated = False
    
    if refs_path.exists():
        refs_text = refs_path.read_text(encoding="utf-8")
        if "Hofstede Dimensions Sourcing" not in refs_text:
            if not dry_run:
                hofstede_refs = generate_hofstede_references_section(scores)
                # Insert before "Verified Facts by File" or at end
                if "## Verified Facts" in refs_text:
                    refs_text = refs_text.replace("## Verified Facts", hofstede_refs + "## Verified Facts")
                else:
                    refs_text = refs_text + "\n" + hofstede_refs
                refs_path.write_text(refs_text, encoding="utf-8")
            refs_updated = True
            print(f"  + REFERENCES: add Hofstede sourcing section")
    
    return readme_updated or refs_updated


def main():
    parser = argparse.ArgumentParser(description="Scaffold Hofstede documentation for all countries")
    parser.add_argument("--apply", action="store_true", help="Actually apply changes (default is dry-run)")
    parser.add_argument("country", nargs="?", help="Specific country to scaffold (optional)")
    args = parser.parse_args()
    
    countries = find_countries()
    
    if args.country:
        countries = [(d, n) for d, n in countries if n == args.country]
        if not countries:
            print(f"Country not found: {args.country}")
            return 1
    
    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"=== Hofstede Scaffolding ({mode}) ===\n")
    
    updated_count = 0
    for country_dir, country_name in countries:
        print(f"{country_name}:")
        if scaffold_country(country_dir, dry_run=not args.apply):
            updated_count += 1
    
    print(f"\n{updated_count} countries need Hofstede documentation")
    if not args.apply and updated_count > 0:
        print("\nRun with --apply to apply changes:")
        print(f"  python3 scripts/scaffold_hofstede.py --apply")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
