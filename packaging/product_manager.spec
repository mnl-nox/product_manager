# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

ROOT = Path.cwd().resolve()
datas = [
    (str(path), str(path.relative_to(ROOT)))
    for folder in (ROOT / 'ui', ROOT / 'assets' / 'icons')
    for path in folder.rglob('*')
    if path.is_file()
]
datas.append((str(ROOT / 'db' / 'schema.sql'), 'db'))
datas.append((str(ROOT / 'VERSION'), '.'))
datas.append((str(ROOT / 'PRIVACY.md'), '.'))

a = Analysis(
    [str(ROOT / 'desktop.py')],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ProductManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=str(ROOT / 'packaging' / 'windows' / 'product-manager.ico'),
)
