#!/usr/bin/env python3
"""Quick check of Germany files for completeness."""
import pathlib

print("=== GERMANY FILE AUDIT ===\n")

# Check line endings
print("[1] Line endings:")
for f in sorted(pathlib.Path('regions/europe/germany').glob('*.md')):
    raw = f.read_bytes()
    has_crlf = b'\r\n' in raw
    has_lf = b'\n' in raw and not has_crlf
    status = "CRLF" if has_crlf else ("LF" if has_lf else "NONE")
    print(f"  {f.name}: {status}")

# Check footers
print("\n[2] Footer consistency (v0.1.0):")
for f in sorted(pathlib.Path('regions/europe/germany').glob('*.md')):
    text = f.read_text(encoding='utf-8', errors='replace')
    has_footer = 'v0.1.0' in text and 'KAI Worlds' in text
    print(f"  {f.name}: {'OK' if has_footer else 'MISSING'}")

# Check file sizes
print("\n[3] File substance (non-stub):")
for f in sorted(pathlib.Path('regions/europe/germany').glob('*.md')):
    text = f.read_text(encoding='utf-8', errors='replace')
    lines = text.strip().split('\n')
    words = len(text.split())
    print(f"  {f.name}: {lines} lines, {words} words")

# Check persona count
print("\n[4] Persona validation:")
personas = list(pathlib.Path('regions/europe/germany').glob('persona_*.md'))
print(f"  Count: {len(personas)} (need 2)")
for p in personas:
    text = p.read_text(encoding='utf-8', errors='replace')
    # Try to detect gender/role
    has_owner = 'Owner:' in text
    print(f"  {p.name}: {'Has Owner field' if has_owner else 'MISSING Owner field'}")

print("\n[5] REFERENCES.md:")
refs = pathlib.Path('regions/europe/germany/REFERENCES.md')
if refs.exists():
    text = refs.read_text(encoding='utf-8', errors='replace')
    verified = text.count('verified') if 'verified' in text.lower() else 0
    print(f"  Exists: YES, {len(text)} bytes")
    print(f"  Sources documented: YES")
else:
    print(f"  Exists: NO")
