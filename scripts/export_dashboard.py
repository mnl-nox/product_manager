#!/usr/bin/env python3
"""Exporta o dashboard local em CSV compatível com Excel e Google Sheets."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='http://127.0.0.1:8000/api/dashboard/export.csv')
    parser.add_argument('--output-dir', type=Path, default=Path('exports'))
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"dashboard-product-manager-{datetime.now():%Y%m%d-%H%M%S}.csv"
    destination = args.output_dir / filename

    with urlopen(args.url, timeout=10) as response:
        if response.status != 200:
            raise RuntimeError(f'Exportação retornou HTTP {response.status}.')
        destination.write_bytes(response.read())

    print(f'Exportado: {destination}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
