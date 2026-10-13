# Plataformas e implantação

## Matriz de suporte

| Plataforma | Distribuição | Persistência |
|---|---|---|
| Windows 10/11 x64 | Instalador Inno Setup gerado em runner Windows | `%LOCALAPPDATA%\ProductManager\product_manager.db` |
| Debian/Ubuntu x64 | Pacote `.deb` | `${XDG_DATA_HOME:-~/.local/share}/product-manager/product_manager.db` |
| Fedora/RHEL e derivados | Pacote `.rpm` quando `rpmbuild` está disponível no build local; workflow gera o pacote | Diretório de dados do usuário |
| Android | PWA instalável pelo Chrome, não APK | Banco no servidor; o service worker não armazena respostas da API |
| Docker/Compose | Container Python | Volume `product-manager-data` |
| Núcleo C | Binário de terminal independente | Definido pelo próprio núcleo C; separado do SQLite web |

## Desktop

O launcher inicia o servidor HTTP no computador e abre o navegador padrão. O modo local escuta em loopback por padrão. Não exponha diretamente essa porta para outras máquinas.

## Linux

```bash
make package-linux
```

O script gera `.deb`; gera também `.rpm` quando `rpmbuild` está instalado. Os artefatos locais ficam em `build/packages/`.

## Windows

O build nativo requer Windows, Python 3.12, Inno Setup 6 e Chocolatey conforme `docs/platforms.md`. O script é `packaging/windows/build.ps1`; a saída fica em `build/packages/`.

## PWA Android

O PWA usa `ui/manifest.webmanifest`, service worker e ícones em `assets/icons/`. Publique a aplicação atrás de HTTPS e mantenha UI e API na mesma origem. O service worker mantém o shell da interface em cache; requisições `/api/` permanecem online e não são guardadas no dispositivo.

Para gerar o ZIP de implantação:

```bash
make package-pwa
```

O ZIP não é APK. A instalação depende de uma origem HTTPS acessível e de infraestrutura mantida pela organização.

## Docker

```bash
export PRODUCT_MANAGER_SETUP_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
docker compose up --build -d
```

O Compose mapeia a porta para o loopback do host e persiste os dados no volume. A configuração fornecida desativa cookies Secure para permitir teste local em HTTP; não a use inalterada atrás de acesso público.

## GitHub Actions

O workflow `.github/workflows/packages.yml` pode rodar manualmente ou em tags `v*`. Publica artefatos para Windows x64, Linux (.deb/.rpm) e PWA. O workflow de release está em `.github/workflows/release.yml`.

## Checklist de produção

- [ ] HTTPS/TLS no proxy ou servidor de borda.
- [ ] `PRODUCT_MANAGER_COOKIE_SECURE=1`.
- [ ] Segredos armazenados fora do código e dos logs.
- [ ] Rede e portas restritas.
- [ ] Volume/banco persistente e backup automatizado.
- [ ] Restauração de backup testada.
- [ ] Procedimento de atualização e rollback.
- [ ] Monitoramento e política de retenção.
- [ ] Papéis e permissões revisados.
- [ ] Aceitação explícita dos limites de workspace compartilhado e ausência de SSO.

O projeto não inclui TLS embutido, isolamento multi-organização nem infraestrutura gerenciada de produção.