#!/usr/bin/env python3
"""Check local Markdown links in explicitly supplied repository documents."""
from __future__ import annotations
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

LINK_RE = re.compile(r"!?\[[^\]]*\]\((?:<([^>]+)>|([^\s)]+))(?:\s+[^)]*)?\)")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$")

def heading_slug(text: str) -> str:
    text = text.replace(chr(96), "").strip().lower()
    text = re.sub(r"[^\w\- ]", "", text, flags=re.UNICODE)
    return re.sub(r"[ -]+", "-", text).strip("-")

def anchors_for(path: Path) -> set[str]:
    anchors: set[str] = set()
    counts: dict[str, int] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        return anchors
    for line in lines:
        match = HEADING_RE.match(line)
        if match:
            base = heading_slug(match.group(1))
            count = counts.get(base, 0)
            counts[base] = count + 1
            anchors.add(base if count == 0 else f"{base}-{count}")
    return anchors

def check_document(path: Path, repo_root: Path) -> list[str]:
    source = (repo_root / path).resolve() if not path.is_absolute() else path.resolve()
    if not source.is_file():
        return [f"{path}: input document does not exist"]
    try:
        content = source.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return [f"{path}: cannot read document: {exc}"]
    errors: list[str] = []
    in_fence = False
    fence_marker = ""
    for line_number, line in enumerate(content.splitlines(), 1):
        stripped = line.lstrip()
        if stripped.startswith((chr(96) * 3, "~~~")):
            marker = stripped[:3]
            if not in_fence:
                in_fence, fence_marker = True, marker
            elif marker == fence_marker:
                in_fence, fence_marker = False, ""
            continue
        if in_fence:
            continue
        for match in LINK_RE.finditer(line):
            target = unquote((match.group(1) or match.group(2) or "").strip())
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not target:
                continue
            if target.startswith("#"):
                destination, fragment = source, target[1:]
            else:
                destination = (source.parent / parsed.path).resolve()
                fragment = parsed.fragment
            if not destination.exists():
                errors.append(f"{source.relative_to(repo_root)}:{line_number}: missing target {target}")
                continue
            if fragment and destination.is_file() and destination.suffix.lower() in {".md", ".markdown"}:
                if fragment not in anchors_for(destination):
                    errors.append(f"{source.relative_to(repo_root)}:{line_number}: missing anchor {target}")
    return errors

def main(argv: list[str]) -> int:
    repo_root = Path.cwd().resolve()
    documents = [Path(arg) for arg in argv]
    if not documents:
        print("Usage: python scripts/check_markdown_links.py README.md docs/README.md", file=sys.stderr)
        return 2
    errors = [error for document in documents for error in check_document(document, repo_root)]
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Markdown links OK ({len(documents)} document(s) checked).")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
