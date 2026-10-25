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
# Only the four imported 0.1 records retain their published legacy paths. Every
# later version (and every new package name) uses NAME/VERSION/NAME.rnl so that
# multiple versions can coexist in a viewer's file pool without overwriting one.
LEGACY_VERSIONS = {(name, '0.1') for name in (
    'analog-canvas-extensions', 'eda-symbol', 'eda-style', 'pdk-sky130')}
LANGUAGE = re.compile(r'[a-z]{2,3}(?:-[a-z0-9]+)*')

def norm(text):
    return ' '.join(text.split())

def sha(data):
    return hashlib.sha256(data).hexdigest()

def unique_paths(packages):
    paths = {}
    for package in packages:
        path = package['path']
        key = package['name'], package['version']
        if path in paths:
            raise ValueError(f'duplicate catalog path {path!r}: {paths[path]} and {key}')
        paths[path] = key

def summary_of(name, version, meta, description):
    """The summary of a record. English is RNL's only core language (its decision 0015): a record has the
    English alone, and the translations are in summaries/, outside the records. The four imported 0.1
    records keep the Chinese they were published with, from metadata.json, as they cannot change."""
    summary = meta['summary']
    if summary and not (isinstance(summary.get('en'), str) and summary['en'] and all(
            LANGUAGE.fullmatch(lang) and isinstance(text, str) and text for lang, text in summary.items())):
        raise ValueError(f'{name}: the summary needs an English text, and a text for each of its other languages')
    if (name, version) in LEGACY_VERSIONS:
        return summary or {'zh': description, 'en': description}
    return {'en': summary['en'] if summary else description}

def summaries(root, catalog):
    """The translations of the records' summaries: summaries/LANG.json, an object keyed by the English
    of a record's summary, with its runs of white space as one space, whose values are the translations,
    or null where there is none yet. They are published beside the catalog and are not part of any
    record, so a translation can be added or corrected at any time."""
    english = {norm(p['summary']['en']) for p in catalog['packages']}
    found = {}
    for file in sorted((root / 'summaries').glob('*')):
        lang = file.stem
        if file.suffix != '.json' or not LANGUAGE.fullmatch(lang) or lang == 'en':
            raise ValueError(f'{file}: a file of summaries is LANG.json, for a language other than English')
        data = json.loads(file.read_text(encoding='utf-8'))
        if not isinstance(data, dict) or not all(isinstance(text, (str, type(None))) for text in data.values()):
            raise ValueError(f'{file}: an object whose values are translations, or null where there is none yet')
        unknown = [key for key in data if key not in english]
        if unknown:
            raise ValueError(f'{file}: not the English summary of any record: {unknown[0]!r}')
        found[lang] = data
    return found

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
        summary = summary_of(name, version, meta, description)
        path = primary.relative_to(root).as_posix()
        pool_path = (meta['legacyPath'] if (name, version) in LEGACY_VERSIONS
                     else primary.relative_to(root / 'packages').as_posix())
        assets = []
        for file in sorted(directory.rglob('*'), key=lambda p: p.as_posix().casefold()):
            if file.is_symlink():
                raise ValueError(f'{file}: symlinks are not published')
            if file.is_file():
                rel = file.relative_to(root).as_posix()
                assets.append({'path': file.relative_to(directory).as_posix(), 'url': BASE_URL + rel, 'sha256': sha(file.read_bytes())})
        packages.append({'name': name, 'version': version, 'kind': meta['kind'], 'summary': summary,
                         'description': description, 'path': pool_path, 'url': BASE_URL + path,
                         'source': 'https://github.com/rich-netlist/rnl-packages/blob/main/' + path,
                         'sha256': sha(data), 'assets': assets})
    unique_paths(packages)
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
    translations = summaries(ROOT, catalog)
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
        if translations:
            shutil.copytree(ROOT/'summaries', args.out/'summaries', dirs_exist_ok=True)
        (args.out/'.nojekyll').touch()
        (args.out/'index.html').write_text('<!doctype html><title>RNL public packages</title><a href="catalog.json">Package catalog</a>\n', encoding='utf-8')
    print(f"ok: {len(catalog['packages'])} immutable package versions; summaries in "
          f"{', '.join(translations) or 'English alone'}")

if __name__ == '__main__':
    main()
