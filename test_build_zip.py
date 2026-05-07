#!/usr/bin/env python3
import os
import zipfile
import shutil
import re
from pathlib import Path

def is_complete_culture(culture_dir):
    """Check if culture folder has all required components."""
    try:
        culture_path = Path(culture_dir)
        
        has_position = any(culture_path.glob('culture_*_position.md'))
        personas = list(culture_path.glob('culture_*_persona_*.md')) + list(culture_path.glob('persona_*.md'))
        has_personas = len(personas) >= 2
        places = list(culture_path.glob('culture_*_place_*.md'))
        has_places = len(places) >= 1
        pieces = list(culture_path.glob('culture_*_piece_*.md'))
        has_pieces = len(pieces) >= 1
        has_readme = (culture_path / 'README.md').exists()
        
        return has_position and has_personas and has_places and has_pieces and has_readme
    except:
        return False

def rewrite_links_for_flat_zip(content):
    """Rewrite links for flat zip structure."""
    # Pattern 1: Root-relative links like [text](engine/file.md)
    # Strip the engine/ prefix since files are at root
    content = re.sub(
        r'\]\(engine/([^)]+\.md)\)',
        r'](\1)',
        content
    )
    
    # Pattern 2: Relative links like [text](../../../engine/file.md)
    # Strip the ../ traversal and take just filename
    content = re.sub(
        r'\]\(\.\./\.\./\.\./engine/([^)]+\.md)\)',
        r'](\1)',
        content
    )
    
    return content

# Create dist directory
dist_dir = Path('dist')
dist_dir.mkdir(exist_ok=True)

# Find and package complete cultures
regions_path = Path('regions')
for region_dir in regions_path.iterdir():
    if not region_dir.is_dir():
        continue
    
    for country_dir in region_dir.iterdir():
        if not country_dir.is_dir():
            continue
        
        if is_complete_culture(country_dir):
            culture_name = country_dir.name
            print(f"Packaging {culture_name}...")
            
            # Create temp staging directory
            staging_dir = Path(f'dist/staging-{culture_name}')
            if staging_dir.exists():
                shutil.rmtree(staging_dir)
            staging_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy all culture files
            for culture_file in country_dir.glob('culture_*.md'):
                shutil.copy2(culture_file, staging_dir / culture_file.name)
                print(f"  + {culture_file.name}")
            
            # Copy persona files
            for persona_file in country_dir.glob('*_persona_*.md'):
                shutil.copy2(persona_file, staging_dir / persona_file.name)
                print(f"  + {persona_file.name}")
            
            # Copy old-style personas for backward compat
            for persona_file in country_dir.glob('persona_*.md'):
                if not (staging_dir / persona_file.name).exists():
                    shutil.copy2(persona_file, staging_dir / persona_file.name)
                    print(f"  + {persona_file.name}")
            
            # Copy engine files
            engine_path = Path('engine')
            for engine_file in ['stack.md', 'position_male.md', 'position_female.md']:
                src = engine_path / engine_file
                if src.exists():
                    shutil.copy2(src, staging_dir / engine_file)
                    print(f"  + {engine_file}")
            
            # Copy claude instructions
            claude_instructions = engine_path / 'claude' / 'instructions.md'
            if claude_instructions.exists():
                shutil.copy2(claude_instructions, staging_dir / 'claude_instructions.md')
                print(f"  + claude_instructions.md")
            
            # Copy and rewrite README
            readme = country_dir / 'README.md'
            if readme.exists():
                readme_content = readme.read_text(encoding='utf-8')
                readme_content = rewrite_links_for_flat_zip(readme_content)
                (staging_dir / 'README.md').write_text(readme_content, encoding='utf-8')
                print(f"  + README.md (links rewritten)")
            
            # Copy REFERENCES if it exists
            references = country_dir / 'REFERENCES.md'
            if references.exists():
                shutil.copy2(references, staging_dir / 'REFERENCES.md')
                print(f"  + REFERENCES.md")
            
            # Rewrite links in all culture files
            for markdown_file in staging_dir.glob('*.md'):
                try:
                    content = markdown_file.read_text(encoding='utf-8')
                    new_content = rewrite_links_for_flat_zip(content)
                    if new_content != content:
                        markdown_file.write_text(new_content, encoding='utf-8')
                except:
                    pass
            
            # Create flat zip
            zip_path = dist_dir / f'{culture_name}.zip'
            file_count = 0
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for file_path in staging_dir.glob('*.md'):
                    zf.write(file_path, arcname=file_path.name)
                    file_count += 1
            
            print(f"  Created {zip_path.name} with {file_count} files\n")
            
            # Cleanup
            shutil.rmtree(staging_dir)

print("Done. Zips created in dist/")
