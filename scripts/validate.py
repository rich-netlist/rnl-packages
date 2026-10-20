#!/usr/bin/env python3
"""Check all versions and render every symbol with the pinned RNL checkout."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from catalog import ROOT, generate

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--rnl-root', type=Path, required=True)
    args = ap.parse_args()
    rnl = args.rnl_root.resolve()
    cli = rnl/'target/debug/rnl'
    catalog = generate()
    directories = sorted((ROOT/'packages').glob('*/*'))
    paths = [a for d in directories for a in ('--path', str(d))]
    for p in catalog['packages']:
        file = ROOT/'packages'/p['name']/p['version']/f"{p['name']}.rnl"
        subprocess.run([str(cli), 'check', str(file), *paths], check=True)
    with tempfile.TemporaryDirectory() as temp:
        temp = Path(temp)
        libraries = temp/'libraries'
        shutil.copytree(rnl/'libraries/standard', libraries/'standard')
        for p in catalog['packages']:
            shutil.copytree(ROOT/'packages'/p['name']/p['version'], libraries/p['name']/p['version'])
        subprocess.run(['node', str(rnl/'site/gallery/build.mjs'), '--libraries', str(libraries), '--out', str(temp/'site')], check=True, cwd=rnl)
        for file in (temp/'site/gallery').glob('*.js'):
            if file.name == 'index.js':
                continue
            group = json.loads(file.read_text(encoding='utf-8').split('(',1)[1].rsplit(');',1)[0])
            for p in group['packages']:
                problems = p.get('problems', []) + [problem for s in p['statements'] for problem in s.get('problems', [])]
                if any('error:' in str(problem) for problem in problems):
                    raise ValueError(f"{p['name']}: {problems}")
    subprocess.run(['python3', str(ROOT/'scripts/pdk/sky130.py'), '--check', '--rnl', str(cli)], check=True)

if __name__ == '__main__':
    main()
