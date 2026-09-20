import tempfile
import unittest
from pathlib import Path

from scripts.check_markdown_math import check_file


class MarkdownMathCheckTest(unittest.TestCase):
    def write_md(self, text: str) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        path = Path(temp_dir.name) / "sample.md"
        path.write_text(text, encoding="utf-8")
        return path

    def test_safe_single_line_display_math(self):
        path = self.write_md(
            "$$\n"
            "\\mathbf{s}=[\\mathbf{s}_{pp},\\mathbf{s}_{visual}].\n"
            "$$\n"
        )
        self.assertEqual(check_file(path), [])

    def test_detects_standalone_equals_inside_display_math(self):
        path = self.write_md(
            "$$\n"
            "\\mathbf{s}\n"
            "=\n"
            "[\\mathbf{s}_{pp},\\mathbf{s}_{visual}]\n"
            "$$\n"
        )
        errors = check_file(path)
        self.assertEqual(len(errors), 1)
        self.assertIn("Setext heading underline", errors[0])

    def test_ignores_bad_example_inside_fenced_code(self):
        path = self.write_md(
            "~~~markdown\n"
            "$$\n"
            "\\mathbf{s}\n"
            "=\n"
            "[\\mathbf{s}_{pp}]\n"
            "$$\n"
            "~~~\n"
        )
        self.assertEqual(check_file(path), [])

    def test_detects_unclosed_display_math(self):
        path = self.write_md(
            "$$\n"
            "\\mathbf{s}=\\mathbf{x}\n"
        )
        errors = check_file(path)
        self.assertEqual(len(errors), 1)
        self.assertIn("unclosed", errors[0])


if __name__ == "__main__":
    unittest.main()
