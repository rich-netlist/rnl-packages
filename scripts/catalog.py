#!/usr/bin/env python3
"""Generate the public catalog and enforce append-only version records."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = 'https://rich-netlist.github.io/rnl-packages/'
PACKAGE = re.compile(r'@PACKAGE\(\s*name="([a-z0-9-]+)"\s*,\s*version="([0-9]+\.[0-9]+)"\s*\)')

def sha(data):
    return hashlib.sha256(data).hexdigest()

def generate(root=ROOT):
    metadata = json.loads((root / 'metadata.json').read_text(encoding='utf-8'))
    packages = []
    for directory in sorted((root / 'packages').glob('*/*')):
        if not directory.is_dir():
            continue
        name, version = directory.parent.name, directory.name
        if not re.fullmatch(r'[0-9]+\.[0-9]+', version):
            raise ValueError(f'{directory}: versions must be major.minor (RNL 0.3, 16.2)')
        primary = directory / f'{name}.rnl'
        data = primary.read_bytes()
        if (name, version) not in PACKAGE.findall(data.decode('utf-8')):
            raise ValueError(f'{primary}: @PACKAGE does not match directory name and version')
        meta = metadata[name]
        if meta['kind'] not in ('pdk', 'extension'):
            raise ValueError(f'{name}: invalid kind')
        # Keep the viewer's original first-paragraph description, including non-ASCII punctuation.
        head = re.search(r'/\*(.*?)\*/', data.decode('utf-8'), re.S).group(1)
        lines = head.splitlines()
        indent = min((len(line)-len(line.lstrip()) for line in lines[1:] if line.strip()), default=0)
        description = '\n'.join(line.strip() if i == 0 else line[indent:].rstrip() for i, line in enumerate(lines)).strip().split('\n\n')[0]
        summary = meta['summary'] or {'zh': description, 'en': description}
        if not all(isinstance(summary.get(lang), str) and summary[lang] for lang in ('zh','en')):
            raise ValueError(f'{name}: both summary languages are required')
        path = primary.relative_to(root).as_posix()
        assets = []
        for file in sorted(directory.rglob('*')):
            if file.is_symlink():
                raise ValueError(f'{file}: symlinks are not published')
            if file.is_file():
                rel = file.relative_to(root).as_posix()
                assets.append({'path': file.relative_to(directory).as_posix(), 'url': BASE_URL + rel, 'sha256': sha(file.read_bytes())})
        packages.append({'name': name, 'version': version, 'kind': meta['kind'], 'summary': summary,
                         'description': description, 'path': meta['legacyPath'], 'url': BASE_URL + path,
                         'source': 'https://github.com/rich-netlist/rnl-packages/blob/main/' + path,
                         'sha256': sha(data), 'assets': assets})
    return {'schemaVersion': 1, 'packages': packages}

def immutable(old, new):
    records = {(p['name'], p['version']): p for p in new['packages']}
    for p in old['packages']:
        key = p['name'], p['version']
        if records.get(key) != p:
            raise ValueError(f'{key[0]} {key[1]} is already published; restore it and publish a new version')

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--base', help='Git revision whose published records must remain unchanged')
    ap.add_argument('--out', type=Path, help='Pages output directory')
    args = ap.parse_args()
    catalog = generate()
    text = json.dumps(catalog, ensure_ascii=False, indent=2) + '\n'
    if args.base:
        result = subprocess.run(['git', 'show', f'{args.base}:catalog.json'], cwd=ROOT, capture_output=True)
        if result.returncode:
            raise ValueError('cannot read the baseline catalog; immutability check must not be skipped')
        immutable(json.loads(result.stdout), catalog)
    target = ROOT / 'catalog.json'
    if args.check:
        if not target.exists() or target.read_text(encoding='utf-8') != text:
            raise ValueError('catalog.json differs: run python scripts/catalog.py and commit it')
    else:
        target.write_text(text, encoding='utf-8', newline='\n')
    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(target, args.out/'catalog.json')
        shutil.copytree(ROOT/'packages', args.out/'packages', dirs_exist_ok=True)
        (args.out/'.nojekyll').touch()
        (args.out/'index.html').write_text('<!doctype html><title>RNL public packages</title><a href="catalog.json">Package catalog</a>\n', encoding='utf-8')
    print(f"ok: {len(catalog['packages'])} immutable package versions")

if __name__ == '__main__':
    main()
