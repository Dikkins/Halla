"""Fast offline tests for the catalog and package metadata."""
from __future__ import annotations
import gzip
import json
import sys
import tempfile
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / 'scripts'))
from build_catalog import build_catalog, tokens
from package_addon import MANIFEST

class TranslationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = BASE / 'translations/overrides.json'
        if not path.exists():
            path.write_bytes(gzip.decompress(
                (BASE / 'translations/overrides.json.gz').read_bytes()))

    def test_override_count(self):
        obj = json.loads((BASE / 'translations/overrides.json').read_text('utf-8'))
        self.assertGreaterEqual(len(obj['english_to_russian']), 400)
        self.assertGreaterEqual(len(obj['portuguese_to_russian']), 150)

    def test_placeholder_preservation(self):
        self.assertEqual(tokens('Foo %1 %2'), tokens('Привет %2 %1'))
        self.assertNotEqual(tokens('Foo %1'), tokens('Привет %2'))

    def test_pt_precedence_and_english_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'en.ts'
            p.write_text('''<?xml version="1.0"?><TS><context><name>Example</name>
<message><source>Sobre o Halla</source><translation>About Halla</translation></message>
<message><source>Frase sem tradução</source><translation>English fallback</translation></message>
</context></TS>''', encoding='utf-8')
            dictionary, stats = build_catalog(p, BASE / 'translations/overrides.json')
            self.assertEqual(dictionary['Sobre o Halla'], 'О программе Halla')
            self.assertEqual(dictionary['Frase sem tradução'], 'English fallback')
            self.assertGreater(stats['total_strings'], 150)

    def test_manifest_matches_abi(self):
        self.assertEqual(MANIFEST['id'], 'local.halla-ru')
        self.assertEqual(MANIFEST['apiVersion'], 1)
        self.assertEqual(
            MANIFEST['platforms']['windows-x64']['library'],
            'bin/windows-x64/halla_ru.dll')

if __name__ == '__main__':
    unittest.main()
