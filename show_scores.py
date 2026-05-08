#!/usr/bin/env python3
from data.hofstede_keywords import detect_language, DIMENSION_KEYWORDS_BY_LANGUAGE
from pathlib import Path

country_dir = Path('regions/europe/netherlands')
files = {
    'position': country_dir / 'culture_dutch_position.md',
    'language': country_dir / 'culture_dutch_language_nederlands.md',
    'process': country_dir / 'culture_dutch_process_polderen.md',
    'piece': country_dir / 'culture_dutch_piece_poldermodel.md',
    'place': country_dir / 'culture_dutch_place_amsterdam.md',
    'anneke': country_dir / 'culture_dutch_persona_anneke.md',
    'jeroen': country_dir / 'culture_dutch_persona_jeroen.md',
}

# Get keywords
nl_keywords = DIMENSION_KEYWORDS_BY_LANGUAGE.get('nl', {})
all_keywords = {}
for dim, keywords in nl_keywords.items():
    all_keywords[dim] = set(keywords.get('high', []) + keywords.get('low', []))

# Count by file
results = {}
for name, path in files.items():
    if not path.exists():
        continue
    content = path.read_text(encoding='utf-8').lower()
    results[name] = {}
    for dim, kw_set in all_keywords.items():
        matches = sum(1 for kw in kw_set if kw in content)
        results[name][dim] = matches

# Print
print('Keyword matches by file and dimension:\n')
dims = ['PDI', 'IDV', 'MAS', 'UAI', 'LTO', 'IND']
print(f"{'File':<15} {' '.join(f'{d:>5}' for d in dims)}")
print('-' * 50)
for name in files.keys():
    if name not in results:
        continue
    counts = [results[name].get(d, 0) for d in dims]
    print(f"{name:<15} {' '.join(f'{x:>5}' for x in counts)}")

# Totals
print('-' * 50)
totals = {}
for dim in dims:
    totals[dim] = sum(results[n].get(dim, 0) for n in results.keys())
counts = [totals.get(d, 0) for d in dims]
print(f"{'TOTAL':<15} {' '.join(f'{x:>5}' for x in counts)}")

print(f"\nDeclared scores: PDI=38 IDV=80 MAS=14 UAI=53 LTO=67 IND=68")
print(f"README reports: All dimensions EXCELLENT (gaps ±5 or less)")
