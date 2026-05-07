#!/usr/bin/env python3
import zipfile
from pathlib import Path

zip_path = Path('dist/germany.zip')
with zipfile.ZipFile(zip_path, 'r') as zf:
    entries = zf.namelist()
    print(f"Total files: {len(entries)}")
    print("\nFile list:")
    for entry in sorted(entries):
        print(f"  {entry}")
    
    # Check for duplicates
    if len(entries) != len(set(entries)):
        print("\nWARNING: Duplicate files detected!")
    else:
        print("\nOK: No duplicates")
