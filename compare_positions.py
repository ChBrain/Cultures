#!/usr/bin/env python3
from data.hofstede_keywords import detect_language, DIMENSION_KEYWORDS_BY_LANGUAGE
from pathlib import Path

countries = {
    'Denmark': {
        'da': 'regions/europe/denmark/culture_danish_position.md',
    },
    'Germany': {
        'de': 'regions/europe/germany/culture_german_position.md',
    },
    'Netherlands': {
        'nl': 'regions/europe/netherlands/culture_dutch_position.md',
    }
}

dims = ['PDI', 'IDV', 'MAS', 'UAI', 'LTO', 'IND']

print("POSITION FILE KEYWORD COUNTS (isolate validator check):\n")
print(f"{'Country':<15} {' '.join(f'{d:>6}' for d in dims)}")
print('-' * 55)

for country, lang_files in countries.items():
    for lang, path in lang_files.items():
        if not Path(path).exists():
            print(f"{country:<15} [File not found]")
            continue
        
        keywords = DIMENSION_KEYWORDS_BY_LANGUAGE.get(lang, {})
        all_kw = {}
        for dim, kw_dict in keywords.items():
            all_kw[dim] = set(kw_dict.get('high', []) + kw_dict.get('low', []))
        
        content = Path(path).read_text(encoding='utf-8').lower()
        counts = []
        for dim in dims:
            matches = sum(1 for kw in all_kw[dim] if kw in content)
            counts.append(matches)
        
        print(f"{country:<15} {' '.join(f'{x:>6}' for x in counts)}")
