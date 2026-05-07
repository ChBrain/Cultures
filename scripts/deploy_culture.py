#!/usr/bin/env python3
"""Deploy culture content files to a target culture folder.

This script deploys only culture content files (pattern: culture_*.md), skipping
infrastructure files (README.md, REFERENCES.md, metadata). Supports targeted
deployments to specific culture folders with replace and delete operations.

Usage:
    python3 scripts/deploy_culture.py \
        --source <source_dir> \
        --target regions/europe/germany \
        --replace culture_german_position.md,culture_german_place_berlin.md \
        --delete culture_german_piece_old.md
"""

import argparse
import shutil
from pathlib import Path
import sys


def is_culture_content_file(filename: str) -> bool:
    """Check if file is culture content (not infrastructure)."""
    # Culture content files match: culture_*_*.md or culture_*_*_*.md
    # Skip: README.md, REFERENCES.md, *.md without culture_ prefix, .py files, etc.
    if not filename.endswith('.md'):
        return False
    if not filename.startswith('culture_'):
        return False
    if filename in ('README.md', 'REFERENCES.md'):
        return False
    return True


def deploy_culture(source_dir: Path, target_dir: Path, replace_files: list[str], 
                   delete_files: list[str], dry_run: bool = False) -> int:
    """Deploy culture content files from source to target.
    
    Args:
        source_dir: Source directory containing files to deploy
        target_dir: Target culture directory
        replace_files: List of filenames to forcefully replace
        delete_files: List of filenames to delete from target
        dry_run: If True, show what would happen without executing
        
    Returns:
        0 if successful, 1 if errors
    """
    errors = 0
    deployed = []
    replaced = []
    deleted = []
    skipped = []
    
    # Ensure target exists
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Get all .md files from source
    source_files = sorted(source_dir.glob('*.md'))
    
    if not source_files:
        print(f"ERROR: No .md files found in {source_dir}", file=sys.stderr)
        return 1
    
    print(f"Deploy Culture Content")
    print(f"  Source: {source_dir}")
    print(f"  Target: {target_dir}")
    print(f"  Dry-run: {dry_run}")
    print()
    
    # Deploy culture content files
    for src_file in source_files:
        if not is_culture_content_file(src_file.name):
            skipped.append(src_file.name)
            continue
        
        tgt_file = target_dir / src_file.name
        
        # Check if this file should be replaced
        should_replace = src_file.name in replace_files
        
        if tgt_file.exists() and not should_replace:
            print(f"SKIP: {src_file.name} (exists, not in --replace list)")
            skipped.append(src_file.name)
            continue
        
        # Copy file
        if not dry_run:
            shutil.copy2(src_file, tgt_file)
        
        if tgt_file.exists():
            status = "REPLACE" if should_replace else "CREATE"
            replaced.append(src_file.name) if should_replace else deployed.append(src_file.name)
            print(f"{status}: {src_file.name}")
        else:
            deployed.append(src_file.name)
            print(f"CREATE: {src_file.name}")
    
    # Delete files
    for del_file in delete_files:
        tgt_file = target_dir / del_file
        if tgt_file.exists():
            if not dry_run:
                tgt_file.unlink()
            deleted.append(del_file)
            print(f"DELETE: {del_file}")
        else:
            print(f"SKIP DELETE: {del_file} (not found)")
    
    # Summary
    print()
    print(f"Summary:")
    print(f"  Created: {len(deployed)}")
    print(f"  Replaced: {len(replaced)}")
    print(f"  Deleted: {len(deleted)}")
    print(f"  Skipped: {len(skipped)}")
    
    if dry_run:
        print()
        print("(dry-run: no files actually modified)")
    
    return 0 if errors == 0 else 1


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Deploy culture content files to target folder"
    )
    parser.add_argument('--source', required=True, help='Source directory')
    parser.add_argument('--target', required=True, help='Target culture folder (relative to repo root)')
    parser.add_argument('--replace', default='', help='Comma-separated files to replace')
    parser.add_argument('--delete', default='', help='Comma-separated files to delete')
    parser.add_argument('--dry-run', action='store_true', help='Show what would happen without executing')
    
    args = parser.parse_args(argv)
    
    source_dir = Path(args.source)
    if not source_dir.exists():
        print(f"ERROR: Source directory not found: {source_dir}", file=sys.stderr)
        return 1
    
    # Target is relative to repo root
    repo_root = Path.cwd()
    target_dir = repo_root / args.target
    
    replace_files = [f.strip() for f in args.replace.split(',') if f.strip()]
    delete_files = [f.strip() for f in args.delete.split(',') if f.strip()]
    
    return deploy_culture(source_dir, target_dir, replace_files, delete_files, args.dry_run)


if __name__ == '__main__':
    sys.exit(main())
