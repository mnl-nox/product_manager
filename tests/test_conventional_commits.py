from __future__ import annotations

import unittest

from scripts.check_conventional_commits import invalid_subject


class ConventionalCommitTests(unittest.TestCase):
    def test_accepts_supported_subject_forms(self):
        for subject in (
            'feat: add product search',
            'fix(api): reject negative quantity',
            'refactor(ui)!: remove old dashboard contract',
            'Merge pull request #12 from feature/search',
        ):
            with self.subTest(subject=subject):
                self.assertIsNone(invalid_subject(subject))

    def test_rejects_unknown_types_and_missing_subjects(self):
        self.assertIn('unsupported type', invalid_subject('feature: add search'))
        self.assertEqual(invalid_subject('feat(scope): '), 'expected type(scope)!: description')


if __name__ == '__main__':
    unittest.main()
