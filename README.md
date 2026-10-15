# Product Manager

<p align="center"><img src="assets/icons/product-manager-brand.svg" alt="Product Manager" width="240"></p>

Aplicação de gestão operacional para catálogo, clientes, estoque, compras, vendas, financeiro e exportação. O projeto combina uma interface web, launcher desktop e PWA; o Android também pode ser empacotado como APK e Android App Bundle (`.aab`). Licença MIT.

**[Baixar a versão mais recente](https://github.com/mnl-nox/product_manager/releases/latest)** · [Aplicação Web](https://product-manager-14fq.onrender.com/login) · [Site](https://mnl-nox.github.io/product_manager/) · [Wiki](https://github.com/mnl-nox/product_manager/wiki)

## Downloads oficiais

Os instaladores para cada plataforma ficam anexados à página da versão. Os assets aparecem quando o workflow de release termina.

| Plataforma | Download | Uso |
|---|---|---|
| Windows 10/11, x64 | `ProductManager-<versão>-windows-x64-setup.exe` | Instalador desktop; banco local no perfil do usuário. |
| Debian/Ubuntu, x64 | Pacote `.deb` | Instalação desktop via APT/dpkg. |
| Fedora/RHEL, x64 | Pacote `.rpm` | Instalação desktop via DNF/RPM. |
| Android, instalação direta | APK assinado anexado ao release, se a chave Android estiver configurada | Wrapper que abre a aplicação HTTPS publicada; requer conexão com o servidor. |
| Android, Google Play | `.aab` assinado, quando a chave de release estiver configurada | Bundle para envio ao Play Console; não pode ser instalado diretamente no aparelho. |
| Android, PWA | [Aplicação Web](https://product-manager-14fq.onrender.com/login) | No Chrome, use **Instalar app** ou **Adicionar à tela inicial**. Requer HTTPS. |

**macOS e iOS não têm pacote nativo publicado.** O APK de instalação direta depende da instância web e não funciona como servidor independente. O AAB só é publicado quando os secrets de assinatura Android estão configurados no GitHub Actions; consulte [Plataformas e instalação](docs/platforms.md#android-apk-e-aab).

## Funcionalidades

- Dashboard, catálogo de produtos e clientes, pesquisa e filtros.
- Compras com cotações, aprovação, recebimentos parciais/finais e atualização transacional do estoque.
- Vendas com baixa de estoque e lançamento financeiro.
- Livro-razão append-only de estoque e histórico de movimentos.
- Financeiro operacional, relatórios, alertas de estoque e exportação CSV/XLSX.
- Usuários com papéis de acesso, sessões protegidas e API JSON.
- Recursos de RH e exportação de dados para folha.

As contas compartilham um único workspace SQLite; não há isolamento multi-organização. Consulte [segurança e limitações](docs/platforms.md#requisitos-de-produção) antes de usar dados reais.

## Início rápido

Requisitos: Python 3.10 ou superior. Para compilar o núcleo C legado, também é necessário GCC/Clang com suporte a C23 e GNU Make.

```bash
git clone https://github.com/mnl-nox/product_manager.git
cd product_manager
python3 api/app.py
```

Abra <http://127.0.0.1:8000>. No primeiro acesso, configure o administrador pelo fluxo de bootstrap; não existe usuário ou senha padrão. Consulte [instalação e primeiro acesso](docs/installation-usage.md).

### Executar com Docker Compose

```bash
export PRODUCT_MANAGER_SETUP_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
docker compose up --build -d
```

O Compose persiste o banco no volume `product-manager-data` e publica a porta em loopback. Para uso remoto, configure HTTPS, cookies Secure, rede restrita e backup com restauração testada.

## Desenvolvimento, build e testes

```bash
make test
python3 -m compileall -q api scripts tests
```

- [Desenvolvimento e configuração](docs/development.md)
- [Plataformas, downloads e empacotamento](docs/platforms.md)
- [Estratégia de testes e QA](docs/qa-plan-and-results.md)
- [Resultados de validação](docs/test-results.md)
- [Relatórios de qualidade](relatórios/README.md)

Builds por plataforma:
- **Windows:** `packaging/windows/build.ps1` (runner Windows, Python 3.12 e Inno Setup).
- **Linux:** `make package-linux` cria `.deb` e, se `rpmbuild` estiver instalado, `.rpm`.
- **PWA Android:** `make package-pwa` gera o ZIP de implantação.
- **APK/AAB Android:** workflow [Cross-platform packages](https://github.com/mnl-nox/product_manager/actions/workflows/packages.yml).

## Documentação

Consulte o [índice da documentação](docs/README.md) para encontrar o documento canônico de cada assunto.

- [Arquitetura](doc/architecture.md)
- [Modelo de dados](doc/data-model.md)
- [Requisitos](doc/requirements.md)
- [Tutorial visual](docs/tutorial-visual.md)
- [Wiki do projeto](https://github.com/mnl-nox/product_manager/wiki)

A documentação ainda está distribuída entre `doc/`, `docs/`, `wiki/` e diretórios de relatórios com nomes semelhantes. A consolidação desses materiais deve preservar histórico, referências externas e evidências de QA; não remova arquivos até verificar duplicação real e atualizar todos os links.

## Estrutura principal

```text
api/          servidor HTTP e API JSON
ui/           interface web e PWA
android/      wrapper Android e configuração de APK/AAB
db/           esquema SQLite e banco local
docs/         guias operacionais e índice documental
doc/          arquitetura, modelo de dados e requisitos (consolidação pendente)
relatórios/   casos, evidências e relatórios de qualidade
packaging/    empacotamento Windows, Linux e PWA
tests/        testes automatizados
src/, include/ núcleo C23 legado
```

## Segurança, privacidade e licença

Proteja o banco e os backups, configure segredos fora do código e use HTTPS para acesso remoto. Leia [política de segurança](SECURITY.md), [política de privacidade](PRIVACY.md) e [licença MIT](LICENSE). Contribuições seguem [CONTRIBUTING.md](CONTRIBUTING.md).
