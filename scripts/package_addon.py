#!/usr/bin/env python3
"""Package Halla Russian plug-in as a standard .halla-addon (ZIP)."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

MANIFEST = {
    'id': 'local.halla-ru',
    'name': 'Halla RU',
    'version': '0.2.0',
    'author': 'Halla RU Community',
    'description': 'Русская локализация интерфейса Halla Desktop 1.1.37 (Qt)',
    'type': 'native',
    'apiVersion': 1,
    'defaultEnabled': True,
    'capabilities': [],
    'platforms': {'windows-x64': {'library': 'bin/windows-x64/halla_ru.dll'}},
}

def add(zf: ZipFile, filename: str, contents: bytes):
    info = ZipInfo(filename, date_time=(2026, 10, 11, 0, 0, 0))
    info.compress_type = ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    zf.writestr(info, contents)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dll', type=Path, required=True)
    ap.add_argument('--dictionary', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    data = args.dll.read_bytes()
    if not data.startswith(b'MZ') or len(data) < 4096:
        raise SystemExit('Not a valid PE DLL (missing MZ header or too small)')
    catalog = args.dictionary.read_bytes()
    if not isinstance(json.loads(catalog), dict):
        raise SystemExit('Invalid translation catalog')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(args.out, 'w') as zf:
        add(zf, 'manifest.json',
            (json.dumps(MANIFEST, ensure_ascii=False, indent=2) + '\n').encode())
        add(zf, 'bin/windows-x64/halla_ru.dll', data)
        add(zf, 'assets/halla_ru.json', catalog)
    digest = hashlib.sha256(args.out.read_bytes()).hexdigest()
    args.out.with_name(args.out.name + '.sha256').write_text(
        f'{digest}  {args.out.name}\n', encoding='ascii')
    print(f'Package: {args.out}, bytes={args.out.stat().st_size}, SHA256={digest}')

if __name__ == '__main__':
    main()
