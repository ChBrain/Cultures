#!/usr/bin/env python3
"""
Native-speaker writing check for culture_*.md files.
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
        f"You are checking whether a short cultural prose fragment reads as "
        f"writing by a native {language} speaker.\n"
        f"File: {filename}\n\n"
        f"It should read as natural, fluent prose in complete, flowing sentences. "
        f"Flag anything a careful native {language} speaker would not write:\n"
        f"1. Phrasing that sounds machine-translated or unnatural: wrong idiom, "
        f"English word order, word-for-word calques.\n"
        f"2. Terse, fragmented writing: one-word sentences, sentence fragments, "
        f"or keyword lists dressed as prose. These must be rewritten as full, "
        f"flowing sentences.\n"
        f"Judge the language only, not the cultural content.\n\n"
        f"Reply in exactly this format:\n"
        f"First line: PASS if every line reads as natural native writing, "
        f"otherwise FLAG.\n"
        f"If FLAG, add one bullet per problem, each quoting the phrase:\n"
        f"- \"<quoted phrase>\" - <one-line reason>\n\n"
        f"Text:\n{prose}"
    )
    payload = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 800,
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

    print("## Native-speaker writing check\n")
    if not results:
        print("No prose content found in changed files.")
        return

    def verdict_pass(finding: str) -> bool:
        return finding.strip().upper().startswith("PASS")

    if all(verdict_pass(r) for _, r in results):
        print("✅ All files read as natural native-speaker writing.")
        return

    for filename, finding in results:
        if verdict_pass(finding):
            print(f"### `{filename}` — ✅ PASS\n")
            continue
        # Drop a leading bare "FLAG" line; keep the bulleted findings.
        body = finding.strip()
        lines = body.splitlines()
        if lines and lines[0].strip().upper().startswith("FLAG"):
            body = "\n".join(lines[1:]).strip()
        print(f"### `{filename}` — flagged\n\n{body}\n")

    print("---\n*Advisory only — does not block merge.*")


if __name__ == "__main__":
    main()
