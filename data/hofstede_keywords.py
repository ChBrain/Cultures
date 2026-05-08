#!/usr/bin/env python3
"""Shared Hofstede keywords and language detection for all validators.

This module is the SINGLE SOURCE OF TRUTH for:
1. Language detection (using lingua library)
2. Hofstede dimension keywords per language

Both validate_hofstede_derived.py and validate_hofstede_alignment.py
import from here to ensure consistent scoring locally and in CI.

Usage:
  from data.hofstede_keywords import detect_language, DIMENSION_KEYWORDS_BY_LANGUAGE
"""
from __future__ import annotations

from lingua import Language, LanguageDetectorBuilder

# Language mapping for lingua library
LINGUA_LANGUAGES = {
    "english": Language.ENGLISH,
    "german": Language.GERMAN,
    "danish": Language.DANISH,
}

_detector = LanguageDetectorBuilder.from_languages(
    *LINGUA_LANGUAGES.values()
).build()


def detect_language(text: str) -> str:
    """Detect language using lingua library (single source of truth).
    
    Returns language code: "en", "de", "da", or defaults to "en".
    This is the ONLY language detection function used by Hofstede validators.
    """
    if not text or len(text.strip()) < 50:
        return "en"  # Too short to detect reliably
    
    detected = _detector.detect_language_of(text)
    if detected == Language.ENGLISH:
        return "en"
    elif detected == Language.GERMAN:
        return "de"
    elif detected == Language.DANISH:
        return "da"
    
    return "en"  # Default


# Hofstede dimension keywords per language
# These are the ONLY keyword sets used for scoring.
DIMENSION_KEYWORDS_BY_LANGUAGE = {
    "en": {
        "PDI": {
            "high": ["hierarchy", "status", "rank", "authority", "obey", "deference", "respect", "leader"],
            "low": ["equal", "equality", "merit", "question", "challenge", "democratic", "egalitarian"],
        },
        "IDV": {
            "high": ["individual", "autonomy", "personal", "achievement", "self", "independent"],
            "low": ["group", "collective", "harmony", "loyalty", "team", "community", "belonging"],
        },
        "UAI": {
            "high": ["rule", "structure", "plan", "clarity", "precise", "precision", "stability", "order", "protocol"],
            "low": ["flexible", "adapt", "improvise", "ambiguous", "risk", "spontaneous"],
        },
        "MAS": {
            "high": ["achieve", "compete", "win", "success", "ambitious", "assert", "power", "strength"],
            "low": ["care", "cooperate", "relationship", "compassion", "community", "modest"],
        },
        "LTO": {
            "high": ["long-term", "future", "plan", "save", "invest", "persist", "tradition", "foundation"],
            "low": ["immediate", "present", "quick", "instant", "result", "heritage"],
        },
        "IND": {
            "high": ["enjoy", "pleasure", "freedom", "indulge", "relax", "gratif"],
            "low": ["restrain", "discipline", "control", "self-control", "duty", "obligation"],
        },
    },
    "de": {
        "PDI": {
            "high": ["hierarchie", "status", "rang", "respekt", "autorität", "führung", "gehorsam"],
            "low": ["gleichheit", "gleichberechtigung", "verdienst", "demokratisch", "egalitär"],
        },
        "IDV": {
            "high": ["individuell", "eigenverantwortlich", "autonomie", "persönlich", "selbst", "unabhängig"],
            "low": ["gruppe", "gemeinschaft", "harmonie", "treue", "team", "zusammenhalt", "loyalität"],
        },
        "UAI": {
            "high": ["regel", "struktur", "planung", "klarheit", "präzision", "direktheit", "stabilität", "ordnung", "protokoll", "sicherheit", "verfahren", "korrekt"],
            "low": ["flexibel", "anpassung", "improvisieren", "mehrdeutig", "risiko", "spontan"],
        },
        "MAS": {
            "high": ["leistung", "erfolg", "wettkampf", "gewinnen", "ehrgeiz", "durchsetzung", "kraft", "stärke", "kompetenz", "ergebnis"],
            "low": ["fürsorge", "kooperation", "beziehung", "mitgefühl", "gemeinschaft", "rücksicht"],
        },
        "LTO": {
            "high": ["langfristig", "zukunft", "planung", "sparen", "investition", "beharrlichkeit", "kontinuität", "nachhaltigkeit", "wiedervereinigung", "ausgangszustand", "boden", "vertrag", "pflicht", "erinnern", "grundgesetz"],
            "low": ["sofort", "gegenwart", "schnell", "unmittelbar", "tradition", "vergangenheit", "erbe"],
        },
        "IND": {
            "high": ["genießen", "vergnügen", "freiheit", "spaß", "entspannung", "freude", "wärme"],
            "low": ["zurückhaltung", "disziplin", "mäßigung", "selbstbeherrschung", "pflicht", "verpflichtung", "erfüllung", "widerstand"],
        },
    },
    "da": {
        "PDI": {
            "high": ["hierarki", "status", "autoritet", "ledelse", "kommando", "respektere"],
            "low": ["lighed", "demokratisk", "ligestilling", "ligeværd", "respekt", "verdier"],
        },
        "IDV": {
            "high": ["individuelt", "personlig", "selvbestemmelse", "autonomi", "egen", "uafhængig"],
            "low": ["gruppe", "fællesskab", "samarbejde", "tilhørighed", "team", "loyalitet"],
        },
        "UAI": {
            "high": ["regel", "struktur", "orden", "system", "klart", "sikkerhed", "procedure", "præcision"],
            "low": ["fleksibel", "fleksibilitet", "pragmatisk", "improvisere", "risiko", "tilpasning", "tilpas", "skiftende"],
        },
        "MAS": {
            "high": ["præstation", "succes", "gevinst", "sejr", "konkurrence", "styrke", "kraft"],
            "low": ["samarbejde", "omsorg", "omhu", "fællesskab", "medmenneskelig", "rørende", "empati"],
        },
        "LTO": {
            "high": ["fremtid", "plan", "investering", "kontinuitet", "ansvar", "forpligtelse", "langsigtet"],
            "low": ["nu", "øjeblikket", "straks", "nyder", "spontan", "øjebliks", "nu"],
        },
        "IND": {
            "high": ["nyde", "nydelse", "frihed", "tilfredsstillelse", "fryd", "hygge", "frejdig"],
            "low": ["tilbageholdenhed", "disciplin", "pligt", "mådehold", "selvkontrol", "forsigtig"],
        },
    },
}


def get_keywords_for_language(language: str) -> dict[str, dict[str, list[str]]] | None:
    """Get Hofstede keywords for a language.
    
    Falls back to English if language not found.
    """
    if language in DIMENSION_KEYWORDS_BY_LANGUAGE:
        return DIMENSION_KEYWORDS_BY_LANGUAGE[language]
    return DIMENSION_KEYWORDS_BY_LANGUAGE["en"]
