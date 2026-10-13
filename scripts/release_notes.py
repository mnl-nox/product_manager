#!/usr/bin/env python3
"""Print release notes from CHANGELOG.md, with a git-history fallback."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def git_output(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def notes_for(version: str, changelog: Path = Path("CHANGELOG.md")) -> str:
    normalized = version.removeprefix("v")
    heading = f"## [v{normalized}]"
    lines = changelog.read_text(encoding="utf-8").splitlines()

    for start, line in enumerate(lines):
        if line.startswith(heading):
            end = next(
                (index for index in range(start + 1, len(lines)) if lines[index].startswith("## ")),
                len(lines),
            )
            section = "\n".join(lines[start + 1 : end]).strip()
            if section:
                return section
            break

    # A tag can be created successfully while release publication fails.
    # Recover by deriving notes from commits between this tag and its predecessor.
    previous_tag = git_output("describe", "--tags", "--abbrev=0", f"{version}^")
    revision_range = f"{previous_tag}..{version}" if previous_tag else version
    commits = git_output("log", revision_range, "--pretty=format:%s")
    if commits:
        entries = [line.strip() for line in commits.splitlines() if line.strip()]
        return "### Changes\n\n" + "\n".join(f"- {entry}" for entry in entries)

    raise ValueError(
        f"Versão {version} não encontrada em {changelog} e não há commits para gerar notas."
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", help="Tag SemVer, por exemplo v1.1.0")
    args = parser.parse_args()
    print(notes_for(args.version))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
