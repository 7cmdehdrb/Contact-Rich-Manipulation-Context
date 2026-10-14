"""Small filesystem integration fixtures for the Markdown link checker."""

from pathlib import Path
from tempfile import TemporaryDirectory
from contextlib import redirect_stdout
import csv
import io
import json
import unittest
import zipfile

from scripts.check_document_links import anchors, check_files, extract_links, main


class MarkdownLinkTests(unittest.TestCase):
    def test_balanced_parentheses_angle_spaces_titles_and_escapes(self):
        text = r'''[A](folder/file(1).md#한글 "title")
![B](<images/a b (2).png> 'caption')
[C](folder/file\(1\).md)
[D](a b.md)
[E](other.md (caption))
\[ignored](missing.md)
`[ignored](missing.md)`
```
[ignored](missing.md)
```
'''
        self.assertEqual([link.destination for link in extract_links(text)], [
            'folder/file(1).md#한글', 'images/a b (2).png', 'folder/file(1).md', 'a b.md', 'other.md'])

    def test_references_images_html_and_code(self):
        text = '''[read][Some ID] ![picture][img] [Some ID][] [Some ID]
[Some ID]: <guide (one).md#start> "title"
[img]: image.png
<a href="guide%20(one).md#start"><img src='image.png'></a>
~~~text
[fake]: missing.md
<img src="missing.png">
~~~
'''
        links = extract_links(text)
        self.assertEqual(len(links), 8)
        self.assertFalse(any('missing' in link.destination for link in links))

    def test_korean_duplicate_heading_explicit_ids_and_setext(self):
        text = '''# 한글 제목 (A/B)
## Same
## Same
## Same-1
## `inline_code` and **bold**
Setext Heading
--------------
<a id="Exact-ID"></a><a name='legacy'></a>
```
# Hidden
<a id="hidden"></a>
```
'''
        self.assertEqual(anchors(text), {'한글-제목-ab', 'same', 'same-1', 'same-1-1',
                                        'inline_code-and-bold', 'setext-heading', 'Exact-ID', 'legacy'})

    def test_files_missing_anchors_external_workspace_and_url_skips(self):
        with TemporaryDirectory() as directory:
            workspace = Path(directory)
            root = workspace / 'repo'
            root.mkdir()
            (root / 'guide (1).md').write_text('# 한글\n# 한글\n<a id="Custom"></a>')
            (root / 'image 1.png').write_bytes(b'fixture')
            (workspace / 'other.md').write_text('# Workspace')
            source = root / 'README.md'
            source.write_text('''[one](guide%20(1).md#한글-1)
[custom](<guide (1).md#Custom>)
![image](<image 1.png>)
[missing](lost.md)
[bad-anchor](guide%20(1).md#missing)
[workspace](../other.md#workspace)
[optional](../not-cloned.md)
[web](https://example.com/no-network#anchor)
[email](mailto:a@example.com)
''')
            report = check_files([source], root)
            self.assertEqual([error['error'] for error in report['errors']], ['missing-path', 'missing-anchor'])
            self.assertEqual(report['stats']['external_links'], 2)
            self.assertEqual(report['stats']['external_urls'], 2)
            report = check_files([source], root, check_external=True)
            self.assertEqual(len(report['errors']), 3)
            self.assertTrue(report['errors'][-1]['external'])

    def test_indented_code_and_unclosed_fence_do_not_create_links(self):
        self.assertEqual(extract_links('    [example](missing.md)\n```md\n[also hidden](missing.md)'), [])

    def test_nested_image_link_preserves_both_destinations(self):
        self.assertEqual([link.destination for link in extract_links('[![alt](image(1).png)](guide.md)')],
                         ['guide.md', 'image(1).png'])

    def test_csv_xlsx_note_columns_parent_paths_and_provenance(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            dataset = root / '03_assets/literature/review_dataset/example'
            tables = dataset / 'tables'
            tables.mkdir(parents=True)
            (dataset / 'note.md').write_text('# Section')
            manifest = dataset / 'manifest.csv'
            with manifest.open('w', encoding='utf-8-sig', newline='') as stream:
                writer = csv.writer(stream)
                writer.writerows([
                    ['analysis_file', 'analysis_note_path', 'local_path'],
                    ['note.md', '', 'missing-original.pdf'],
                    ['Not applicable', 'note.md#missing', 'missing-provenance.md'],
                    ['Not stated', '', ''],
                    ['Duplicated note.md', '', ''],
                ])
            workbook = tables / 'comparison.xlsx'
            spreadsheet_ns = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
            document_rel_ns = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
            package_rel_ns = 'http://schemas.openxmlformats.org/package/2006/relationships'
            with zipfile.ZipFile(workbook, 'w') as archive:
                archive.writestr('xl/workbook.xml', f'''<workbook xmlns="{spreadsheet_ns}" xmlns:r="{document_rel_ns}">
<sheets><sheet name="Comparison" sheetId="1" r:id="rData"/><sheet name="Notes" sheetId="2" r:id="rNotes"/></sheets></workbook>''')
                archive.writestr('xl/_rels/workbook.xml.rels', f'''<Relationships xmlns="{package_rel_ns}">
<Relationship Id="rData" Target="worksheets/data.xml"/><Relationship Id="rNotes" Target="/xl/worksheets/notes.xml"/></Relationships>''')
                archive.writestr('xl/sharedStrings.xml', f'''<sst xmlns="{spreadsheet_ns}">
<si><t>analysis_note_path</t></si><si><r><t xml:space="preserve">../</t></r><r><t>note.md#section</t></r></si></sst>''')
                archive.writestr('xl/worksheets/data.xml', f'''<worksheet xmlns="{spreadsheet_ns}"><sheetData>
<row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1" t="inlineStr"><is><t>analysis_file</t></is></c><c r="C1" t="inlineStr"><is><t>local_path</t></is></c></row>
<row r="2"><c r="A2" t="s"><v>1</v></c><c r="B2" t="inlineStr"><is><t>../note.md#missing</t></is></c><c r="C2" t="inlineStr"><is><t>missing-provenance.md</t></is></c></row>
<row r="3"><c r="A3" t="inlineStr"><is><t>../lost.md</t></is></c></row>
<row r="4"><c r="A4" t="inlineStr"><is><t>Not stated</t></is></c></row>
<row r="5"><c r="A5" t="inlineStr"><is><t>Duplicated ../note.md</t></is></c></row>
</sheetData></worksheet>''')
                archive.writestr('xl/worksheets/notes.xml', f'''<worksheet xmlns="{spreadsheet_ns}"><sheetData>
<row r="1"><c r="A1" t="inlineStr"><is><t>Notes</t></is></c></row>
<row r="2"><c r="A2" t="inlineStr"><is><t>ignored-note.md</t></is></c></row>
</sheetData></worksheet>''')
            report = check_files([], root, dataset_paths=[manifest, workbook])
            self.assertEqual(report['stats']['dataset_csv_links'], 2)
            self.assertEqual(report['stats']['dataset_xlsx_links'], 3)
            self.assertEqual([error['error'] for error in report['errors']],
                             ['missing-anchor', 'missing-anchor', 'missing-path'])
            self.assertTrue(report['errors'][1]['kind'].startswith('XLSX:Comparison!B2:analysis_file'))
            self.assertFalse(any('provenance' in error['destination'] for error in report['errors']))

    def test_cli_full_scan_includes_dataset_but_explicit_markdown_skips_it(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'README.md'
            source.write_text('# Fixture')
            dataset = root / '03_assets/literature/review_dataset'
            dataset.mkdir(parents=True)
            (dataset / 'manifest.csv').write_text('analysis_file,local_path\nlost.md,original.pdf\n')
            output = io.StringIO()
            with redirect_stdout(output):
                result = main(['--root', str(root)])
            self.assertEqual(result, 1)
            stats = json.loads(output.getvalue().splitlines()[-1])
            self.assertEqual(stats['dataset_csv_files'], 1)
            output = io.StringIO()
            with redirect_stdout(output):
                result = main(['--root', str(root), str(source)])
            self.assertEqual(result, 0)
            stats = json.loads(output.getvalue().splitlines()[-1])
            self.assertNotIn('dataset_csv_files', stats)

    def test_invalid_dataset_workbook_is_reported_without_crashing(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            workbook = root / 'bad.xlsx'
            workbook.write_text('invalid archive')
            report = check_files([], root, dataset_paths=[workbook])
            self.assertEqual(report['errors'][0]['error'], 'dataset-read-error')


if __name__ == '__main__':
    unittest.main()
