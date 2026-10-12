#!/usr/bin/env python3
"""Print release notes for a version from CHANGELOG.md."""

from __future__ import annotations

import argparse
from pathlib import Path


def notes_for(version: str, changelog: Path = Path('CHANGELOG.md')) -> str:
    heading = f'## [{version}]'
    lines = changelog.read_text(encoding='utf-8').splitlines()
    try:
        start = next(index for index, line in enumerate(lines) if line.startswith(heading))
    except StopIteration as error:
        raise ValueError(f'Versão {version} não encontrada em {changelog}.') from error

    end = next((index for index in range(start + 1, len(lines)) if lines[index].startswith('## ')), len(lines))
    section = '\n'.join(lines[start + 1:end]).strip()
    if not section:
        raise ValueError(f'A seção {version} não contém notas.')
    return section


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('version', help='Tag SemVer, por exemplo v0.3.0')
    args = parser.parse_args()
    print(notes_for(args.version))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
