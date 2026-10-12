# Plataformas e instalação

Product Manager oferece dois modos desktop (Windows e Linux) e um PWA para Android. O desktop executa o serviço HTTP no próprio computador e abre o navegador padrão. O PWA é uma aplicação web instalável, não um APK.

## Windows 10/11 x64

O workflow **Cross-platform packages** gera `ProductManager-<versão>-windows-x64-setup.exe` em um runner Windows. O instalador cria atalhos do menu Iniciar e, opcionalmente, da área de trabalho. O executável grava o banco em `%LOCALAPPDATA%\ProductManager\product_manager.db`.

Build local em Windows com Python 3.12, Inno Setup 6 e Chocolatey:

```powershell
./packaging/windows/build.ps1
```

O instalador aparece em `build/packages/`.

## Linux

O desktop usa Python 3.10+, o navegador padrão e `xdg-utils`. A base instalada grava dados em `$XDG_DATA_HOME/product-manager/` ou `~/.local/share/product-manager/`.

```bash
make package-linux
```

O comando sempre cria um `.deb`. Se `rpmbuild` estiver instalado, também cria um `.rpm`. Saídas ficam em `build/packages/`. O workflow Linux do GitHub instala o builder RPM e exige a criação dos dois pacotes.

Instale o `.deb` com:

```bash
sudo apt install ./build/packages/product-manager_<versão>_amd64.deb
```

Para RPM use `sudo dnf install ./build/packages/product-manager-<versão>-1.x86_64.rpm`.

## Android (PWA)

O PWA usa `ui/manifest.webmanifest`, o service worker e os ícones em `assets/icons/`. O usuário abre o endereço HTTPS no Chrome para Android e escolhe **Instalar app** ou **Adicionar à tela inicial**. O botão de instalação aparece quando o navegador considera o site instalável.

O deployment ZIP gerado pelo workflow inclui API, frontend, esquema SQLite e ícones. Configure o serviço atrás de um proxy HTTPS corporativo e exponha uma única origem para a UI e `/api`. A aplicação fornece autenticação local e autorização por papel, mas o servidor Python não fornece TLS. Defina `PRODUCT_MANAGER_COOKIE_SECURE=1`, restrinja o acesso de rede e proteja banco, backups e segredos. As contas compartilham o mesmo espaço de trabalho; não há isolamento entre organizações ou login corporativo.

O service worker mantém apenas o shell da interface em cache. Requisições `/api/` permanecem online e não são guardadas no dispositivo.

## Gerar os artefatos no GitHub Actions

O workflow `.github/workflows/packages.yml` roda em tags `v*` ou manualmente e publica artefatos separados:

- Instalador Windows x64.
- Pacote `.deb` e `.rpm` Linux x64.
- ZIP do PWA para Android.

No workflow manual, a versão vem de `VERSION`; para uma tag, o nome da tag é usado. Tags históricas anteriores a estes arquivos são ignoradas.

O build Windows precisa rodar em Windows; este ambiente Linux só consegue gerar o `.deb` diretamente. O `.rpm` local requer `rpmbuild`; os três artefatos são gerados pelos runners nativos do workflow.
