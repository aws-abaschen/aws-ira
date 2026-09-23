"""Regression tests for document validation failures that must block CI."""
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, main
from unittest.mock import patch
import json
import validate_docs


class DocumentValidationTests(TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.bundle = self.root / 'bundles' / 'example'
        self.bundle.mkdir(parents=True)
        (self.root / 'README.md').write_text('# Documentation\n', encoding='utf-8')
        (self.bundle / 'index.md').write_text('---\nokf_version: 0.2\n---\n# Index\n\n- [Concept](./concept.md)\n', encoding='utf-8')
        self.concept = self.bundle / 'concept.md'
        self.concept.write_text('---\ntype: Reference\n---\n# Concept\n\n## Valid heading\n', encoding='utf-8')

    def result(self):
        output = StringIO()
        with patch.object(validate_docs, 'ROOT', self.root), redirect_stdout(output):
            failed = validate_docs.main()
        report = json.loads(output.getvalue())
        self.assertEqual(failed, bool(report['errors']))
        return report

    def append(self, text):
        with self.concept.open('a', encoding='utf-8') as stream:
            stream.write(text)

    def test_minimal_okf_and_numeric_version_are_valid(self):
        self.assertEqual(self.result()['errors'], [])

    def test_missing_type_fails(self):
        self.concept.write_text('---\ntitle: Missing type\n---\n# Concept\n', encoding='utf-8')
        self.assertTrue(self.result()['errors'])

    def test_invalid_yaml_fails(self):
        self.concept.write_text('---\ntype: [\n---\n# Concept\n', encoding='utf-8')
        self.assertTrue(self.result()['errors'])

    def test_missing_link_and_heading_fail(self):
        self.append('\n[Missing](missing.md)\n[Heading](#absent)\n')
        self.assertEqual(len(self.result()['errors']), 2)

    def test_bundle_relative_link_and_anchor_work(self):
        self.append('\n[Self](/concept.md#valid-heading)\n')
        self.assertEqual(self.result()['errors'], [])

    def test_local_source_must_exist(self):
        self.concept.write_text('---\ntype: Reference\nsources:\n  - resource: missing.md\n---\n# Concept\n', encoding='utf-8')
        self.assertTrue(self.result()['errors'])

    def test_invalid_json_fails(self):
        self.append('\n```json\n{"key": }\n```\n')
        self.assertTrue(self.result()['errors'])

    def test_diagram_count_is_not_fixed(self):
        self.append('\n```mermaid\nflowchart LR\n  A --> B\n```\n' * 6)
        report = self.result()
        self.assertEqual(report['errors'], [])
        self.assertEqual(report['checks']['diagrams'], 6)

    def test_standalone_diagram_fails(self):
        (self.bundle / 'unexpected.mmd').write_text('flowchart LR\n', encoding='utf-8')
        self.assertTrue(self.result()['errors'])


if __name__ == '__main__':
    main()
