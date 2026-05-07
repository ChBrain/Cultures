#!/usr/bin/env python3
import os
import zipfile
import shutil
from pathlib import Path

def is_complete_culture(culture_dir):
    """Check if culture folder has all required components."""
    try:
        culture_path = Path(culture_dir)
        
        # Must have position file
        has_position = any(culture_path.glob('culture_*_position.md'))
        
        # Must have at least 2 personas
        personas = list(culture_path.glob('culture_*_persona_*.md')) + list(culture_path.glob('persona_*.md'))
        has_personas = len(personas) >= 2
        
        # Must have at least 1 place
        places = list(culture_path.glob('culture_*_place_*.md'))
        has_places = len(places) >= 1
        
        # Must have at least 1 piece
        pieces = list(culture_path.glob('culture_*_piece_*.md'))
        has_pieces = len(pieces) >= 1
        
        # Must have README
        has_readme = (culture_path / 'README.md').exists()
        
        print(f"Checking {culture_dir}:")
        print(f"  Position: {has_position}")
        print(f"  Personas ({len(personas)}): {has_personas}")
        print(f"  Places ({len(places)}): {has_places}")
        print(f"  Pieces ({len(pieces)}): {has_pieces}")
        print(f"  README: {has_readme}")
        
        return has_position and has_personas and has_places and has_pieces and has_readme
    except Exception as e:
        print(f"Error checking {culture_dir}: {e}")
        return False

# Find all complete cultures
regions_path = Path('regions')
complete_cultures = []

for region_dir in regions_path.iterdir():
    if not region_dir.is_dir():
        continue
    
    for country_dir in region_dir.iterdir():
        if not country_dir.is_dir():
            continue
        
        if is_complete_culture(country_dir):
            complete_cultures.append(country_dir)
            print(f"[COMPLETE] {country_dir.name}\n")

print(f"\nFound {len(complete_cultures)} complete culture(s)")
for culture in complete_cultures:
    print(f"  - {culture.name}")

