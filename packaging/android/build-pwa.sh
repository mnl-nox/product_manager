#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VERSION="${1:-$(cat "$ROOT/VERSION")}"
OUT="$ROOT/build/packages"

if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Versão inválida: $VERSION" >&2
  exit 2
fi

python3 - "$ROOT" "$VERSION" <<'PY'
import json
import sys
from zipfile import ZIP_DEFLATED, ZipFile
from pathlib import Path

root = Path(sys.argv[1])
version = sys.argv[2]
manifest = json.loads((root / 'ui' / 'manifest.webmanifest').read_text(encoding='utf-8'))
assert manifest['display'] == 'standalone'
assert manifest['scope'] == '/'
for icon in manifest['icons']:
    if not (root / icon['src'].lstrip('/')).is_file():
        raise SystemExit(f"Ícone não encontrado: {icon['src']}")

archive = root / 'build' / 'packages' / f'product-manager-pwa-{version}.zip'
archive.parent.mkdir(parents=True, exist_ok=True)
included = [root / 'api', root / 'desktop.py', root / 'ui', root / 'db' / 'schema.sql', root / 'assets' / 'icons']
with ZipFile(archive, 'w', ZIP_DEFLATED) as bundle:
    for entry in included:
        files = [entry] if entry.is_file() else entry.rglob('*')
        for path in files:
            if not path.is_file() or '__pycache__' in path.parts or path.suffix == '.pyc':
                continue
            bundle.write(path, path.relative_to(root))
print(f'PWA deployment package: {archive}')
PY
