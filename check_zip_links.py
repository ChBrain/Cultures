#!/usr/bin/env python3
import zipfile
from pathlib import Path

zip_path = Path('dist/germany.zip')
with zipfile.ZipFile(zip_path, 'r') as zf:
    # Extract and read persona file
    content = zf.read('culture_german_persona_brigitte.md').decode('utf-8')
    lines = content.split('\n')
    
    # Find and print Projection section
    for i, line in enumerate(lines):
        if '## Projection' in line:
            print("Projection section (first 5 lines):")
            for j in range(i, min(i + 5, len(lines))):
                print(lines[j])
            break
