#!/usr/bin/env python3
"""Load Hofstede bags from per-country files with fallback to legacy central dict.

This module implements the routing strategy for Hofstede Bag Infrastructure v2.0:
1. Try to load from regions/<region>/<country>/hofstede_bag.yaml (or hofstede_bag_<lang>.yaml)
2. Fall back to legacy data/hofstede_keywords.py DIMENSION_KEYWORDS_BY_LANGUAGE dict
3. Support multilingual countries (one bag per language)

Usage:
  from data.hofstede_bag_loader import load_bag_for_country_file, load_bag_for_language

Where to use:
  validate_hofstede_derived.py
  validate_hofstede_alignment.py
"""
from __future__ import annotations

import yaml
from pathlib import Path
from typing import Optional
from data.hofstede_keywords import DIMENSION_KEYWORDS_BY_LANGUAGE


def _find_country_folder(file_path: Path) -> Optional[Path]:
    """Extract country folder from file path.
    
    Expects: regions/<region>/<country>/file.md
    Returns: regions/<region>/<country>/ or None if not in expected structure
    """
    parts = file_path.parts
    for i, part in enumerate(parts):
        if part == "regions" and i + 2 < len(parts):
            # Found regions; next is region, then country
            country_folder = Path(*parts[:i+3])  # regions/region/country
            if country_folder.exists() and country_folder.is_dir():
                return country_folder
    return None


def _load_bag_from_file(country_folder: Path, language: str) -> Optional[dict]:
    """Load bag YAML from country folder.
    
    Tries:
    1. hofstede_bag_<language>.yaml (multilingual country)
    2. hofstede_bag.yaml (single-language country)
    
    Returns dict with keys {PDI, IDV, UAI, MAS, LTO, IND} -> {high: [], low: []}
    or None if no file found or parsing failed.
    """
    # Try language-specific first
    lang_bag_path = country_folder / f"hofstede_bag_{language}.yaml"
    if lang_bag_path.exists():
        try:
            with open(lang_bag_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if data and "bags" in data:
                    return data["bags"]
        except Exception:
            pass  # Fall through to legacy
    
    # Try generic bag
    generic_bag_path = country_folder / "hofstede_bag.yaml"
    if generic_bag_path.exists():
        try:
            with open(generic_bag_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if data and "bags" in data:
                    return data["bags"]
        except Exception:
            pass  # Fall through to legacy
    
    return None


def _convert_bag_to_keywords_dict(bag: dict) -> dict:
    """Convert per-country bag format to legacy DIMENSION_KEYWORDS_BY_LANGUAGE format.
    
    Input (per-country bag):
      {PDI: {high: [...], low: [...]}, IDV: {...}, ...}
    
    Output (legacy format):
      {PDI: {high: [...], low: [...]}, IDV: {...}, ...}
    
    The formats are already compatible; this is a passthrough for clarity.
    """
    result = {}
    for dim in ["PDI", "IDV", "UAI", "MAS", "LTO", "IND"]:
        if dim in bag and isinstance(bag[dim], dict):
            result[dim] = {
                "high": bag[dim].get("high", []),
                "low": bag[dim].get("low", []),
            }
    return result


def load_bag_for_country_file(
    file_path: Path,
    language: str,
    fallback: bool = True,
) -> dict:
    """Load Hofstede bag for a specific file in a country folder.
    
    Args:
        file_path: Path to a culture_*.md file (or any file in a country folder)
        language: Detected language code (en, de, nl, da, etc.)
        fallback: If True, fall back to legacy dict if per-country file not found
    
    Returns:
        Dict mapping dimension -> {high: [...], low: [...]}
        Falls back to legacy DIMENSION_KEYWORDS_BY_LANGUAGE[language] if:
        - fallback=True and per-country file not found
        - per-country file parsing fails
    
    Raises ValueError if fallback=False and no per-country file exists.
    """
    country_folder = _find_country_folder(file_path)
    
    if country_folder:
        bag = _load_bag_from_file(country_folder, language)
        if bag:
            return _convert_bag_to_keywords_dict(bag)
    
    # Fallback to legacy dict
    if fallback:
        if language in DIMENSION_KEYWORDS_BY_LANGUAGE:
            return DIMENSION_KEYWORDS_BY_LANGUAGE[language]
        else:
            return DIMENSION_KEYWORDS_BY_LANGUAGE.get("en", {})
    else:
        raise ValueError(
            f"No per-country bag found for {file_path} (language={language}) "
            "and fallback=False"
        )


def load_bag_for_language(
    language: str,
    country_folder: Optional[Path] = None,
    fallback: bool = True,
) -> dict:
    """Load Hofstede bag for a language, optionally scoped to a country folder.
    
    Args:
        language: Detected language code (en, de, nl, da, etc.)
        country_folder: If provided, try to load bag from this specific country folder
        fallback: If True, fall back to legacy dict if per-country file not found
    
    Returns:
        Dict mapping dimension -> {high: [...], low: [...]}
    """
    if country_folder and country_folder.exists():
        bag = _load_bag_from_file(country_folder, language)
        if bag:
            return _convert_bag_to_keywords_dict(bag)
    
    # Fallback to legacy dict
    if fallback:
        if language in DIMENSION_KEYWORDS_BY_LANGUAGE:
            return DIMENSION_KEYWORDS_BY_LANGUAGE[language]
        else:
            return DIMENSION_KEYWORDS_BY_LANGUAGE.get("en", {})
    else:
        raise ValueError(
            f"No per-country bag found for language={language}, "
            f"country_folder={country_folder} and fallback=False"
        )
