$ErrorActionPreference = 'Stop'

$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
Set-Location $root
$version = $env:PRODUCT_MANAGER_VERSION
if (-not $version) {
    $version = (Get-Content (Join-Path $root 'VERSION') -Raw).Trim()
}
$env:PRODUCT_MANAGER_VERSION = $version

python -m pip install --upgrade pip
python -m pip install -r (Join-Path $root 'requirements-build.txt')
python -m PyInstaller --clean --noconfirm (Join-Path $root 'packaging\product_manager.spec')

$compiler = Join-Path ${env:ProgramFiles(x86)} 'Inno Setup 6\ISCC.exe'
if (-not (Test-Path $compiler)) {
    choco install innosetup --no-progress -y
}
if (-not (Test-Path $compiler)) {
    throw 'Inno Setup não foi encontrado após a instalação.'
}

& $compiler "/DMyAppVersion=$version" (Join-Path $root 'packaging\windows\product-manager.iss')
