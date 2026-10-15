from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
from scripts.check_markdown_links import check_document, heading_slug

class MarkdownLinkCheckerTests(unittest.TestCase):
    def test_heading_slug(self):
        self.assertEqual(heading_slug("First Access & Setup"), "first-access-setup")
        self.assertEqual(heading_slug("Missing Local Links"), "missing-local-links")

    def test_detects_missing_local_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "README.md").write_text("[missing](docs/missing.md)\n", encoding="utf-8")
            errors = check_document(Path("README.md"), root)
            self.assertEqual(len(errors), 1)
            self.assertIn("missing target", errors[0])

    def test_detects_missing_heading_anchor(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "README.md").write_text("[section](guide.md#not-there)\n", encoding="utf-8")
            (root / "guide.md").write_text("# Existing heading\n", encoding="utf-8")
            errors = check_document(Path("README.md"), root)
            self.assertEqual(len(errors), 1)
            self.assertIn("missing anchor", errors[0])

    def test_accepts_existing_relative_link_and_anchor(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "README.md").write_text("[section](guide.md#existing-heading)\n", encoding="utf-8")
            (root / "guide.md").write_text("# Existing heading\n", encoding="utf-8")
            self.assertEqual(check_document(Path("README.md"), root), [])

if __name__ == "__main__":
    unittest.main()
