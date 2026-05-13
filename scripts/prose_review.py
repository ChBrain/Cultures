#!/usr/bin/env python3
"""
Prose naturalness review for culture_*.md files.
Uses GitHub Models API (GITHUB_TOKEN) — no external key needed.

Usage: python3 scripts/prose_review.py regions/.../culture_*.md ...
Exits 0 always. Output is markdown for posting as a PR comment.
"""

import sys
import os
import re
import json
import urllib.request
import urllib.error
from pathlib import Path

import yaml

MODELS_ENDPOINT = "https://models.inference.ai.azure.com/chat/completions"
MODEL = "gpt-4o-mini"

LANGUAGE_NAMES = {
    "da": "Danish", "de": "German", "nl": "Dutch", "fr": "French",
    "es": "Spanish", "it": "Italian", "pt": "Portuguese", "pl": "Polish",
    "sv": "Swedish", "no": "Norwegian", "fi": "Finnish", "ru": "Russian",
    "ja": "Japanese", "zh": "Chinese", "ko": "Korean", "ar": "Arabic",
}

SKIP_SECTIONS = {"Owner"}

STRIP_PATTERNS = [
    re.compile(r"^\s*$"),
    re.compile(r"^#{1,6}\s"),
    re.compile(r"^-\s+(Project|Culture):"),
    re.compile(r"^\*.*\*\s*$"),
    re.compile(r"^---+\s*$"),
    re.compile(r"^v\d+\.\d+"),
    re.compile(r"^\[.*\]\(.*\)\s*$"),
]


def extract_prose(path: Path) -> str:
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    prose, skip_section = [], False
    for line in lines:
        m = re.match(r"^##\s+(.+)", line)
        if m:
            skip_section = m.group(1).strip() in SKIP_SECTIONS
            continue
        if skip_section:
            continue
        if any(p.match(line) for p in STRIP_PATTERNS):
            continue
        prose.append(line)
    return "\n".join(prose).strip()


def get_language(path: Path) -> str:
    bag = path.parent / "hofstede_bag.yaml"
    if not bag.exists():
        return "the target language"
    data = yaml.safe_load(bag.read_text(encoding="utf-8-sig"))
    code = data.get("language", "")
    return LANGUAGE_NAMES.get(code, code or "the target language")


def call_model(prose: str, language: str, filename: str) -> str:
    token = os.environ.get("GITHUB_TOKEN", "")
    prompt = (
        f"You are reviewing a short cultural prose fragment written in {language}.\n"
        f"File: {filename}\n\n"
        f"Flag only sentences that sound unnatural, mechanical, translated word-for-word, "
        f"or like a keyword list dressed as prose. Do not comment on cultural content — "
        f"only on whether the language sounds natural to a native {language} speaker.\n"
        f"If everything reads naturally, reply with just: OK\n\n"
        f"Text:\n{prose}"
    )
    payload = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 512,
    }).encode()
    req = urllib.request.Request(
        MODELS_ENDPOINT,
        data=payload,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())["choices"][0]["message"]["content"].strip()
    except urllib.error.HTTPError as e:
        return f"⚠️ Model call failed: HTTP {e.code}"
    except Exception as e:
        return f"⚠️ Model call failed: {e}"


def main():
    paths = [
        Path(p) for p in sys.argv[1:]
        if Path(p).name.startswith("culture_") and Path(p).suffix == ".md"
    ]
    paths = [p for p in paths if p.exists()]

    if not paths:
        print("No culture_*.md files to review.")
        return

    results = []
    for p in paths:
        prose = extract_prose(p)
        if prose:
            results.append((p.name, call_model(prose, get_language(p), p.name)))

    print("## Prose naturalness review\n")
    if not results:
        print("No prose content found in changed files.")
        return

    all_ok = all(r.strip().upper() == "OK" for _, r in results)
    if all_ok:
        print("✅ All files read naturally in their target language.")
        return

    for filename, finding in results:
        if finding.strip().upper() == "OK":
            print(f"### `{filename}` — ✅ OK\n")
        else:
            print(f"### `{filename}`\n\n{finding}\n")

    print("---\n*Advisory only — does not block merge.*")


if __name__ == "__main__":
    main()
