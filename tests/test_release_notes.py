from __future__ import annotations

import unittest
from pathlib import Path

from scripts.release_notes import notes_for


class ReleaseNotesTests(unittest.TestCase):
    def test_extracts_requested_version_section(self):
        notes = notes_for('v0.2.0')
        self.assertIn('Primeira aplicação web local', notes)
        self.assertNotIn('Catálogo web de produtos', notes)

    def test_unknown_version_fails_clearly(self):
        with self.assertRaisesRegex(ValueError, 'v9.9.9 não encontrada'):
            notes_for('v9.9.9', Path('CHANGELOG.md'))
