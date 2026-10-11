#!/usr/bin/env python3
"""Build a standalone Qt translation dictionary for Halla.
Manual Russian overrides take priority; untranslated strings fall back to
Halla's official English translations (Portuguese source).
"""
from __future__ import annotations
import argparse
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

TOKEN = re.compile(r'%(?:L?\d+|n)')
CYRILLIC = re.compile(r'[А-Яа-яЁё]')

def tokens(s: str) -> list[str]:
    return sorted(TOKEN.findall(s))

def build_catalog(ts: Path, overrides: Path) -> tuple[dict[str, str], dict]:
    manual = json.loads(overrides.read_text(encoding='utf-8'))
    pt_overrides = manual['portuguese_to_russian']
    en_overrides = manual['english_to_russian']
    root = ET.parse(ts).getroot()
    result = {}
    matched_pt, matched_en, invalid = set(), set(), []

    for context in root.findall('context'):
        for msg in context.findall('message'):
            source = msg.findtext('source')
            if not source:
                continue
            tr = msg.find('translation')
            english = ''
            if tr is not None and tr.attrib.get('type') != 'unfinished':
                if tr.find('numerusform') is None:
                    english = ''.join(tr.itertext()).strip()
            english = english or source
            if source in pt_overrides:
                translation = pt_overrides[source]
                matched_pt.add(source)
            elif english in en_overrides:
                translation = en_overrides[english]
                matched_en.add(english)
            else:
                translation = english

            if tokens(source) != tokens(translation):
                invalid.append(source)
                translation = english if tokens(source) == tokens(english) else source
            result[source] = translation

    # Supplement strings absent from upstream's TS catalog.
    for source, translation in pt_overrides.items():
        if source not in result and tokens(source) == tokens(translation):
            result[source] = translation
    for english, translation in en_overrides.items():
        if english not in result and tokens(english) == tokens(translation):
            result[english] = translation

    stats = {
        'total_strings': len(result),
        'ru_strings': sum(bool(CYRILLIC.search(v)) for v in result.values()),
        'matched_pt': len(matched_pt),
        'matched_en': len(matched_en),
        'token_fallbacks': len(invalid),
    }
    return result, stats

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--overrides', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    translations, stats = build_catalog(args.source, args.overrides)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(translations, ensure_ascii=False, sort_keys=True, indent=2) + '\n',
        encoding='utf-8')
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    if stats['ru_strings'] < 120:
        raise SystemExit('ERROR: suspiciously low Russian translation coverage')

if __name__ == '__main__':
    main()
