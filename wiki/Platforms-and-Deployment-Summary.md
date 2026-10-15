# Plataformas, downloads e implantação

Os downloads oficiais por plataforma são anexados às [Releases](https://github.com/mnl-nox/product_manager/releases/latest). O workflow **Cross-platform packages** constrói cada pacote no runner nativo. A execução do workflow também guarda artefatos temporários.

## Matriz de suporte

| Plataforma | Download | Instalação / observação |
|---|---|---|
| Windows 10/11 x64 | `.exe` Inno Setup | Aplicação desktop local; banco em `%LOCALAPPDATA%\\ProductManager\\`. |
| Debian/Ubuntu x64 | `.deb` | Aplicação desktop local; dados no diretório do usuário. |
| Fedora/RHEL x64 | `.rpm` | Aplicação desktop local; dados no diretório do usuário. |
| Android, instalação direta | `.apk` assinado, se a chave estiver configurada | Wrapper da aplicação HTTPS; requer internet e servidor. |
| Android, Google Play | `.aab` assinado | Envie ao Play Console; não pode ser instalado diretamente no aparelho. |
| Android | PWA | Instale o site HTTPS no Chrome; a API e os dados permanecem online. |
| macOS / iOS | Sem pacote nativo | Não há build oficial publicado para essas plataformas. |

## Windows

Baixe `ProductManager-<versão>-windows-x64-setup.exe` na página de Releases. O build local requer Windows, Python 3.12 e Inno Setup 6:

```powershell
./packaging/windows/build.ps1
```

## Linux

Baixe `.deb` para Debian/Ubuntu ou `.rpm` para Fedora/RHEL na página de Releases. Localmente:

```bash
make package-linux
sudo apt install ./build/packages/product-manager_<versão>_amd64.deb
```

O script sempre gera `.deb` e também gera `.rpm` quando `rpmbuild` está disponível. Os pacotes guardam dados no diretório do usuário.

## Android: APK, AAB e PWA

O APK oficial anexado ao Release é um wrapper assinado com a chave Android de release configurada nos secrets. Ele abre a URL HTTPS publicada e depende do servidor; não inclui API ou banco local.

O `.aab` é um bundle para envio ao Google Play Console. Para gerá-lo e anexá-lo ao Release, configure estes Actions secrets:

- `ANDROID_KEYSTORE_BASE64`: arquivo keystore codificado em Base64.
- `ANDROID_KEYSTORE_PASSWORD`: senha do keystore.
- `ANDROID_KEY_ALIAS`: alias da chave de upload.
- `ANDROID_KEY_PASSWORD`: senha da chave.

Use a chave de upload já associada ao app no Play Console e mantenha uma cópia protegida. Sem os quatro secrets, os builds desktop e o PWA continuam; APK/AAB de release não são publicados. O APK de depuração fica restrito ao artefato de validação do Actions. O workflow não gera nem substitui chaves. O `versionCode` deriva do arquivo `VERSION` e deve superar o maior código enviado anteriormente ao Play Console.

O PWA pode ser instalado pelo Chrome: abra a [aplicação Web](https://product-manager-14fq.onrender.com/login) por HTTPS e escolha **Instalar app** ou **Adicionar à tela inicial**. `make package-pwa` gera o ZIP de implantação. O service worker armazena apenas o shell; chamadas da API continuam online.

## Desktop

O launcher inicia o servidor local e abre o navegador:

```bash
make run-desktop
```

## Docker e implantação

```bash
export PRODUCT_MANAGER_SETUP_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
docker compose up --build -d
```

Use HTTPS para qualquer acesso remoto, configure `PRODUCT_MANAGER_COOKIE_SECURE=1`, restrinja a rede, proteja os segredos e mantenha backups persistentes com restauração testada. O projeto não oferece isolamento entre organizações ou login corporativo.
