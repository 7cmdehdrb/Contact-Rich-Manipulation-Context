import tempfile
import unittest
from pathlib import Path

from scripts.copy_bib_attachments import attachment_paths, copy_attachments


class CopyBibAttachmentsTests(unittest.TestCase):
    def test_extracts_multiple_escaped_windows_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            bib = Path(temp_dir) / "references.bib"
            bib.write_text(
                "@article{x,\n"
                "  file = {G\\:\\\\논문\\\\one.pdf;G:\\논문\\two.pdf}\n"
                "}\n",
                encoding="utf-8",
            )

            paths = attachment_paths(bib)

            self.assertEqual(paths, [Path(r"G:\논문\one.pdf"), Path(r"G:\논문\two.pdf")])

    def test_copies_relative_paths_and_renames_conflicts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            first = root / "first"
            second = root / "second"
            destination = root / "output"
            first.mkdir()
            second.mkdir()
            (first / "paper.pdf").write_bytes(b"first")
            (second / "paper.pdf").write_bytes(b"second")
            bib = root / "references.bib"
            bib.write_text(
                "@article{a, file = {first/paper.pdf}}\n"
                "@article{b, file = {second/paper.pdf}}\n",
                encoding="utf-8",
            )

            summary = copy_attachments([bib], destination, "rename", False)

            self.assertEqual(summary.copied, 2)
            self.assertEqual((destination / "paper.pdf").read_bytes(), b"first")
            self.assertEqual((destination / "paper (2).pdf").read_bytes(), b"second")

    def test_dry_run_does_not_create_destination(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "paper.pdf"
            source.write_bytes(b"pdf")
            bib = root / "references.bib"
            bib.write_text("@article{x,\n file = {paper.pdf}\n}\n", encoding="utf-8")
            destination = root / "output"

            summary = copy_attachments([bib], destination, "rename", True)

            self.assertEqual(summary.copied, 1)
            self.assertFalse(destination.exists())


if __name__ == "__main__":
    unittest.main()
