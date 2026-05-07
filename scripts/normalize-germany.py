#!/usr/bin/env python3
"""Normalize Germany files to repo standards."""
import re
from pathlib import Path

germany_dir = Path("regions/europe/germany")
if not germany_dir.exists():
    print("Germany directory not found")
    exit(1)

print("=== Normalizing Germany files ===\n")

for f in sorted(germany_dir.glob("*.md")):
    # Read raw bytes (no platform conversion)
    raw = f.read_bytes()
    
    # 1. Normalize CRLF to LF
    text = raw.decode("utf-8", errors="replace")
    text = text.replace("\r\n", "\n")
    
    # 2. Strip trailing whitespace from lines but keep one final newline
    lines = text.rstrip("\n").split("\n")
    
    # 3. For content files, fix footer
    if any(p in f.name for p in ["culture_", "persona_"]):
        # Remove old footers
        while lines and re.match(r"^v\d+\.\d+\.\d+ - (KAI Worlds|Kai Schlueter)", lines[-1]):
            lines.pop()
        
        # Add new footer
        lines.append("v0.1.0 - KAI Worlds")
    
    # 4. Ensure single trailing newline and encode as UTF-8 bytes
    normalized = "\n".join(lines) + "\n"
    normalized_bytes = normalized.encode("utf-8")
    
    # Write back as bytes to preserve exact line endings
    f.write_bytes(normalized_bytes)
    
    print(f"✓ {f.name}")
    print(f"  - CRLF → LF")
    if any(p in f.name for p in ["culture_", "persona_"]):
        print(f"  - Footer normalized to: v0.1.0 - KAI Worlds")
    print()

print("✅ Germany normalization complete")
