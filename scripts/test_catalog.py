"""Regression tests for immutable records and version-qualified pool paths."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from catalog import ROOT, generate, immutable, unique_paths


class CatalogPaths(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(ROOT / 'packages', self.root / 'packages')
        shutil.copyfile(ROOT / 'metadata.json', self.root / 'metadata.json')
        self.published = json.loads((ROOT / 'catalog.json').read_text(encoding='utf-8'))

    def add_version(self, name, version):
        directory = self.root / 'packages' / name / version
        shutil.copytree(self.root / 'packages' / 'eda-symbol' / '0.1', directory)
        old = directory / 'eda-symbol.rnl'
        data = old.read_bytes().replace(
            b'@PACKAGE(name="eda-symbol", version="0.1")',
            f'@PACKAGE(name="{name}", version="{version}")'.encode())
        old.unlink()
        (directory / f'{name}.rnl').write_bytes(data)

    def test_imported_catalog_bytes_unchanged(self):
        actual = (json.dumps(generate(self.root), ensure_ascii=False, indent=2) + '\n').encode()
        # Git normalizes catalog.json to LF; compare its complete serialized bytes.
        expected = (ROOT / 'catalog.json').read_bytes().replace(b'\r\n', b'\n')
        self.assertEqual(actual, expected)

    def test_new_version_coexists_with_unchanged_imported_records(self):
        existing = {p['version']: p['path'] for p in self.published['packages'] if p['name'] == 'eda-symbol'}
        minor = max(int(v.split('.')[1]) for v in existing if v.startswith('0.')) + 1
        version = f'0.{minor}'
        self.add_version('eda-symbol', version)
        catalog = generate(self.root)
        immutable(self.published, catalog)
        paths = {p['version']: p['path'] for p in catalog['packages'] if p['name'] == 'eda-symbol'}
        self.assertEqual(paths, {**existing, version: f'eda-symbol/{version}/eda-symbol.rnl'})
        self.assertEqual(len({p['path'] for p in catalog['packages']}), len(self.published['packages']) + 1)

    def test_new_name_needs_no_legacy_path(self):
        self.add_version('new-symbol', '0.1')
        metadata = json.loads((self.root / 'metadata.json').read_text(encoding='utf-8'))
        metadata['new-symbol'] = {'kind': 'extension', 'summary': {'en': 'New', 'zh': '新包'}}
        (self.root / 'metadata.json').write_text(json.dumps(metadata), encoding='utf-8')
        catalog = generate(self.root)
        immutable(self.published, catalog)
        package = next(p for p in catalog['packages'] if p['name'] == 'new-symbol')
        self.assertEqual(package['path'], 'new-symbol/0.1/new-symbol.rnl')

    def test_duplicate_generated_paths_rejected(self):
        metadata = json.loads((self.root / 'metadata.json').read_text(encoding='utf-8'))
        metadata['eda-style']['legacyPath'] = metadata['eda-symbol']['legacyPath']
        (self.root / 'metadata.json').write_text(json.dumps(metadata), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'duplicate catalog path'):
            generate(self.root)

    def test_duplicate_paths_rejected_across_names_and_versions(self):
        with self.assertRaisesRegex(ValueError, 'duplicate catalog path'):
            unique_paths([{'name': 'a', 'version': '0.1', 'path': 'same.rnl'},
                          {'name': 'b', 'version': '0.2', 'path': 'same.rnl'}])


if __name__ == '__main__':
    unittest.main()
