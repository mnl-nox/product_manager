#!/usr/bin/env python3
"""Validate commit subjects in a Git revision range."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys

ALLOWED_TYPES = {
    'feat', 'fix', 'docs', 'style', 'refactor', 'perf', 'test',
    'build', 'ci', 'chore', 'revert',
}
SUBJECT_PATTERN = re.compile(r'^([a-z]+)(?:\([^)]+\))?(!)?:\s+\S.*$')


def invalid_subject(subject: str) -> str | None:
    if subject.startswith('Merge '):
        return None
    match = SUBJECT_PATTERN.fullmatch(subject)
    if not match:
        return 'expected type(scope)!: description'
    if match.group(1) not in ALLOWED_TYPES:
        return f"unsupported type '{match.group(1)}'"
    return None


def subjects_in_range(revision_range: str) -> list[str]:
    result = subprocess.run(
        ['git', 'log', '--format=%s', revision_range],
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--range', required=True, dest='revision_range', help='Git range, for example base..head')
    args = parser.parse_args()

    try:
        subjects = subjects_in_range(args.revision_range)
    except subprocess.CalledProcessError as error:
        print(f'Não foi possível ler o histórico Git: {error}', file=sys.stderr)
        return 2

    failures = [(subject, invalid_subject(subject)) for subject in subjects]
    failures = [(subject, reason) for subject, reason in failures if reason]
    if failures:
        print('Commits fora do padrão Conventional Commits:')
        for subject, reason in failures:
            print(f'  - {subject} ({reason})')
        return 1

    print(f'{len(subjects)} commit(s) válido(s).')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
