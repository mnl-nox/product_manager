from __future__ import annotations

import unittest
from pathlib import Path

from scripts.release_notes import notes_for, release_entries


class ReleaseNotesTests(unittest.TestCase):
    def test_extracts_requested_version_section(self):
        notes = notes_for('v0.2.0')
        self.assertIn('Primeira aplicação web local', notes)
        self.assertNotIn('Catálogo web de produtos', notes)

    def test_version_sync_commit_is_excluded_from_release_notes(self):
        entries = release_entries(
            "docs(readme): update guide\n"
            "chore(release): sync VERSION to v1.7.6\n"
            "fix(api): validate request"
        )
        self.assertEqual(entries, ["docs(readme): update guide", "fix(api): validate request"])

    def test_unknown_version_fails_clearly(self):
        with self.assertRaisesRegex(ValueError, 'v9.9.9 não encontrada'):
            notes_for('v9.9.9', Path('CHANGELOG.md'))
