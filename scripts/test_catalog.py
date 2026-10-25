"""Regression tests for immutable records and version-qualified pool paths."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from catalog import ROOT, generate, immutable, summaries, unique_paths


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
        # a later record has the English summary alone; the Chinese of 0.1 stays in its record
        summary = {p['version']: p['summary'] for p in catalog['packages'] if p['name'] == 'eda-symbol'}
        self.assertEqual(set(summary['0.1']), {'zh', 'en'})
        self.assertEqual(summary[version], {'en': summary['0.1']['en']})

    def test_new_name_needs_no_legacy_path(self):
        self.add_version('new-symbol', '0.1')
        metadata = json.loads((self.root / 'metadata.json').read_text(encoding='utf-8'))
        metadata['new-symbol'] = {'kind': 'extension', 'summary': {'en': 'New'}}
        (self.root / 'metadata.json').write_text(json.dumps(metadata), encoding='utf-8')
        catalog = generate(self.root)
        immutable(self.published, catalog)
        package = next(p for p in catalog['packages'] if p['name'] == 'new-symbol')
        self.assertEqual(package['path'], 'new-symbol/0.1/new-symbol.rnl')
        self.assertEqual(package['summary'], {'en': 'New'})

    def test_a_version_may_have_its_own_summary(self):
        existing = [p['version'] for p in self.published['packages'] if p['name'] == 'eda-symbol']
        version = f"0.{max(int(v.split('.')[1]) for v in existing) + 1}"
        self.add_version('eda-symbol', version)
        metadata = json.loads((self.root / 'metadata.json').read_text(encoding='utf-8'))
        metadata['eda-symbol']['versions'] = {version: {'summary': {'en': 'What this version adds'}}}
        (self.root / 'metadata.json').write_text(json.dumps(metadata), encoding='utf-8')
        catalog = generate(self.root)
        # the version's own summary; the published records keep theirs
        immutable(self.published, catalog)
        summary = {p['version']: p['summary'] for p in catalog['packages'] if p['name'] == 'eda-symbol'}
        self.assertEqual(summary[version], {'en': 'What this version adds'})
        self.assertEqual(set(summary['0.1']), {'zh', 'en'})

    def test_a_summary_needs_its_english(self):
        self.add_version('new-symbol', '0.1')
        metadata = json.loads((self.root / 'metadata.json').read_text(encoding='utf-8'))
        for summary in ({'zh': '只有中文'}, {'en': ''}, {'en': 'New', 'zh': ''}, {'en': 'New', 'Not a code': 'x'}):
            metadata['new-symbol'] = {'kind': 'extension', 'summary': summary}
            (self.root / 'metadata.json').write_text(json.dumps(metadata, ensure_ascii=False), encoding='utf-8')
            with self.subTest(summary=summary), self.assertRaisesRegex(ValueError, 'English text'):
                generate(self.root)

    def test_translations_of_the_summaries_outside_the_records(self):
        catalog = generate(self.root)
        english = next(p['summary']['en'] for p in catalog['packages'] if p['name'] == 'eda-style')
        directory = self.root / 'summaries'
        directory.mkdir()
        key = ' '.join(english.split())
        (directory / 'ja.json').write_text(json.dumps({key: '訳'}, ensure_ascii=False), encoding='utf-8')
        self.assertEqual(summaries(self.root, catalog), {'ja': {key: '訳'}})
        (directory / 'ja.json').write_text(json.dumps({key: None}), encoding='utf-8')
        self.assertEqual(summaries(self.root, catalog), {'ja': {key: None}})
        for name, data in (('ja.json', {'Not a summary': '訳'}), ('ja.json', {english: 1}), ('ja.json', []),
                           ('en.json', {}), ('JA.json', {})):
            for file in directory.iterdir():
                file.unlink()
            (directory / name).write_text(json.dumps(data), encoding='utf-8')
            with self.subTest(name=name, data=data), self.assertRaises(ValueError):
                summaries(self.root, catalog)

    def test_the_repository_summaries(self):
        catalog = json.loads((ROOT / 'catalog.json').read_text(encoding='utf-8'))
        self.assertIn('zh', summaries(ROOT, catalog))

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
