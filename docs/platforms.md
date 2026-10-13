# Plataformas, downloads e instalação

Os binários publicados ficam na página [Releases](https://github.com/mnl-nox/product_manager/releases/latest). O workflow `Cross-platform packages` gera pacotes por runner nativo e anexa os arquivos ao release da tag. Os artefatos temporários também ficam na execução do GitHub Actions.

## Matriz de distribuição

| Plataforma | Pacote | Observação |
|---|---|---|
| Windows 10/11 x64 | `.exe` Inno Setup | Aplicação desktop local; banco em `%LOCALAPPDATA%\\ProductManager\\`. |
| Debian/Ubuntu x64 | `.deb` | Aplicação desktop local; banco no diretório de dados do usuário. |
| Fedora/RHEL x64 | `.rpm` | Aplicação desktop local; banco no diretório de dados do usuário. |
| Android | APK assinado, se a chave estiver configurada | Wrapper da aplicação HTTPS; precisa de internet e servidor. |
| Android / Play Console | `.aab` assinado | Bundle de publicação; o AAB não é instalável diretamente. |
| Android | PWA | Instale o site HTTPS pelo Chrome; os dados continuam no servidor. |

Não há instalador nativo publicado para macOS ou iOS.

## Windows

Baixe o instalador `ProductManager-<versão>-windows-x64-setup.exe` na página de Releases. O build local requer Windows, Python 3.12, Inno Setup 6 e Chocolatey:

```powershell
./packaging/windows/build.ps1
```

## Linux

Baixe o `.deb` para Debian/Ubuntu ou `.rpm` para Fedora/RHEL na página de Releases. Builds locais:

```bash
make package-linux
sudo apt install ./build/packages/product-manager_<versão>_amd64.deb
```

O comando cria `.deb`; cria também `.rpm` quando `rpmbuild` está instalado. Os pacotes guardam dados no diretório do usuário e iniciam o servidor local com navegador padrão.

## Android: APK e AAB

O APK de release é um wrapper de instalação direta, assinado pela chave Android de release. Sem os secrets, o workflow guarda apenas um APK de depuração como artefato de validação, sem publicá-lo como download oficial. Ele abre a URL HTTPS publicada configurada em `APP_URL`; portanto, requer conexão e não contém o servidor nem banco local.

O `.aab` é destinado ao Google Play Console e exige assinatura de release. O APK assinado e o AAB usam a mesma chave de upload. Configure estes GitHub Actions secrets no repositório:

- `ANDROID_KEYSTORE_BASE64`: arquivo keystore codificado em Base64.
- `ANDROID_KEYSTORE_PASSWORD`: senha do keystore.
- `ANDROID_KEY_ALIAS`: alias da chave de upload.
- `ANDROID_KEY_PASSWORD`: senha da chave.

Mantenha cópia segura da chave de upload. Sem todos esses secrets, o workflow ainda produz os pacotes desktop e PWA, mas não publica APK/AAB Android de release. O workflow não cria nem substitui uma chave existente. Configure uma URL HTTPS de produção em `APP_URL` no workflow antes da distribuição, caso o endereço padrão mude.

O `versionCode` é calculado a partir do `VERSION`; confirme que seja maior que qualquer versão já enviada ao Play Console. Para inspecionar o bundle localmente, use `bundleRelease` com as mesmas propriedades `releaseStore*` e `releaseKey*` passadas pelo workflow.

### PWA

Abra a [aplicação Web](https://product-manager-14fq.onrender.com/login) no Chrome para Android e selecione **Instalar app** ou **Adicionar à tela inicial**. `make package-pwa` gera o ZIP de implantação. O cache guarda somente o shell da interface: a API e os dados permanecem online.

## Execução desktop

O launcher inicia um servidor HTTP local e abre o navegador padrão:

```bash
make run-desktop
```

## Requisitos de produção

O servidor Python não fornece TLS. Para acesso remoto, use proxy HTTPS, `PRODUCT_MANAGER_COOKIE_SECURE=1`, rede restrita e armazenamento persistente. Configure e teste backup e restauração. Contas compartilham o mesmo workspace; o sistema não fornece isolamento multi-organização ou login corporativo.
