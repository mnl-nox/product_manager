#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VERSION="${1:-$(cat "$ROOT/VERSION")}"
REQUIRE_RPM=false
if [[ "${2:-}" == "--require-rpm" ]]; then
  REQUIRE_RPM=true
elif [[ "$#" -gt 1 ]]; then
  echo "Uso: $0 [versão] [--require-rpm]" >&2
  exit 2
fi
OUT="$ROOT/build/packages"
STAGE="$ROOT/build/package-root"
RPM_TOP="$ROOT/build/rpm"

if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Versão inválida: $VERSION" >&2
  exit 2
fi

rm -rf "$STAGE" "$RPM_TOP"
mkdir -p "$OUT" "$STAGE/usr/bin" "$STAGE/usr/lib/product-manager/api" \
  "$STAGE/usr/lib/product-manager/ui" "$STAGE/usr/lib/product-manager/db" \
  "$STAGE/usr/lib/product-manager/assets/icons" \
  "$STAGE/usr/share/applications" "$STAGE/usr/share/icons/hicolor/scalable/apps" \
  "$STAGE/usr/share/doc/product-manager"

install -m 0644 "$ROOT/desktop.py" "$STAGE/usr/lib/product-manager/desktop.py"
install -m 0644 "$ROOT/VERSION" "$STAGE/usr/lib/product-manager/VERSION"
install -m 0644 "$ROOT/PRIVACY.md" "$STAGE/usr/lib/product-manager/PRIVACY.md"
install -m 0644 "$ROOT/LICENSE" "$ROOT/PRIVACY.md" "$STAGE/usr/share/doc/product-manager/"
install -m 0644 "$ROOT/api/__init__.py" "$ROOT/api/app.py" "$STAGE/usr/lib/product-manager/api/"
cp -R "$ROOT/ui/." "$STAGE/usr/lib/product-manager/ui/"
install -m 0644 "$ROOT/db/schema.sql" "$STAGE/usr/lib/product-manager/db/schema.sql"
install -m 0644 "$ROOT/assets/icons/product-manager.svg" \
  "$ROOT/assets/icons/product-manager-192.png" "$ROOT/assets/icons/product-manager-512.png" \
  "$ROOT/assets/icons/open-source-mark.svg" \
  "$STAGE/usr/lib/product-manager/assets/icons/"
install -m 0644 "$ROOT/assets/icons/product-manager.svg" \
  "$STAGE/usr/share/icons/hicolor/scalable/apps/product-manager.svg"
install -m 0644 "$ROOT/packaging/linux/product-manager.desktop" \
  "$STAGE/usr/share/applications/product-manager.desktop"

cat > "$STAGE/usr/bin/product-manager" <<'LAUNCHER'
#!/bin/sh
set -eu
DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
export PRODUCT_MANAGER_DB="${PRODUCT_MANAGER_DB:-$DATA_HOME/product-manager/product_manager.db}"
mkdir -p "$(dirname "$PRODUCT_MANAGER_DB")"
exec /usr/bin/python3 /usr/lib/product-manager/desktop.py "$@"
LAUNCHER
chmod 0755 "$STAGE/usr/bin/product-manager"

ARCH="$(dpkg --print-architecture)"
DEB_ROOT="$ROOT/build/deb-root"
rm -rf "$DEB_ROOT"
mkdir -p "$DEB_ROOT/DEBIAN"
cp -a "$STAGE/." "$DEB_ROOT/"
cat > "$DEB_ROOT/DEBIAN/control" <<CONTROL
Package: product-manager
Version: $VERSION
Section: utils
Priority: optional
Architecture: $ARCH
Depends: python3 (>= 3.10), xdg-utils
Maintainer: Product Manager maintainers
Description: Gestão corporativa de clientes e produtos
 Aplicação desktop local com catálogo de produtos e painel de gestão.
CONTROL
dpkg-deb --build --root-owner-group "$DEB_ROOT" "$OUT/product-manager_${VERSION}_${ARCH}.deb"

if [[ "$REQUIRE_RPM" == true ]] && ! command -v rpmbuild >/dev/null 2>&1; then
  echo 'rpmbuild é obrigatório para esta execução; instale o pacote rpm.' >&2
  exit 1
fi

if command -v rpmbuild >/dev/null 2>&1; then
  mkdir -p "$RPM_TOP"/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}
  RPM_SOURCE="$ROOT/build/rpm-source/product-manager"
  rm -rf "$ROOT/build/rpm-source"
  mkdir -p "$(dirname "$RPM_SOURCE")"
  cp -a "$STAGE/." "$RPM_SOURCE/"
  tar -czf "$RPM_TOP/SOURCES/product-manager-${VERSION}.tar.gz" \
    -C "$ROOT/build/rpm-source" product-manager
  sed "s/@VERSION@/$VERSION/g" "$ROOT/packaging/rpm/product-manager.spec.in" \
    > "$RPM_TOP/SPECS/product-manager.spec"
  rpmbuild -bb --define "_topdir $RPM_TOP" "$RPM_TOP/SPECS/product-manager.spec"
  find "$RPM_TOP/RPMS" -type f -name '*.rpm' -exec cp {} "$OUT/" \;
else
  echo 'rpmbuild indisponível: RPM será gerado pelo workflow Linux.' >&2
fi

echo "Pacotes em $OUT"
