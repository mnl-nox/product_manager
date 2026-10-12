# Product Manager

Aplicação web local para gestão de clientes e catálogo de produtos, com dashboard, estoque, API HTTP em Python e persistência SQLite.

## Funcionalidades

- Dashboard com totais, distribuição por categoria, clientes recentes e estoque crítico.
- Cadastro de clientes e produtos com validação de campos e unicidade.
- Filtro do catálogo por categoria e resumo de unidades e valor em estoque.
- Exportação do dashboard em CSV compatível com Excel e Google Sheets.
- API JSON e banco SQLite inicializado com dados de demonstração quando vazio.

## Tela de exemplo

Captura do dashboard carregado com os dados de demonstração:

![Dashboard do Product Manager](docs/screenshots/dashboard.png)

Catálogo de produtos:

![Catálogo do Product Manager](docs/screenshots/products.png)

## Pré-requisitos

- Python 3.10 ou superior (sem dependências externas para API e testes).
- GCC ou Clang com suporte a C23 e GNU Make, somente para o núcleo C legado.

## Executar a aplicação web

```bash
python3 api/app.py
```

Abra <http://127.0.0.1:8000>. O banco padrão é `db/product_manager.db`. Para usar outro caminho, defina `PRODUCT_MANAGER_DB` antes de iniciar o servidor:

```bash
PRODUCT_MANAGER_DB=/caminho/product_manager.db python3 api/app.py
```

As rotas principais são `GET /api/health`, `GET /api/dashboard`, `GET /api/products`, `POST /api/products` e `POST /api/clients`. Veja [API e desenvolvimento](docs/development.md) para exemplos.

## Instalar por plataforma

- **Windows 10/11 x64:** o workflow para tags `v*` gera um instalador `.exe` com Inno Setup.
- **Linux x64:** `make package-linux` gera `.deb` e também `.rpm` quando `rpmbuild` estiver instalado.
- **Android:** o frontend é um PWA instalável pelo Chrome. Hospede a aplicação atrás de HTTPS e escolha **Instalar app** ou **Adicionar à tela inicial**. O workflow publica um ZIP do PWA para implantação.

Para criar localmente o ZIP de implantação do PWA, use `make package-pwa`.

No Linux, os pacotes guardam o banco no diretório de dados do usuário. Para obter o instalador Windows e pacotes Linux construídos em seus ambientes nativos, execute o workflow **Cross-platform packages** no GitHub Actions. Os artefatos aparecem na execução do workflow.

O desktop inicia um servidor local e abre o navegador padrão:

```bash
make run-desktop
```

Detalhes, limitações do PWA e comandos de build estão em [Plataformas e instalação](docs/platforms.md).

O passo a passo de instalação, primeiro uso, backup e relato de erros está em [Guia de instalação e uso](docs/installation-usage.md).

## Testes

```bash
make test
```

Os testes usam banco temporário e não alteram o banco de desenvolvimento.

## Núcleo C

O repositório mantém um núcleo C23 em desenvolvimento, ainda separado da aplicação web:

```bash
make
./build/product_manager
```

## Exportar CSV

Com o servidor em execução:

```bash
python3 scripts/export_dashboard.py
```

O arquivo é salvo em `exports/`. A exportação é local e não envia dados a serviços externos.

## Estrutura

```text
api/          servidor HTTP e API
ui/           interface web
db/           esquema SQLite e banco local
config/       mapeamentos de campos
tests/        testes automatizados
docs/         arquitetura, operação e contribuição
scripts/      utilitários locais
src/, include/ núcleo C23 legado/em evolução
```

## Segurança e dados

O modo desktop escuta somente no loopback. O PWA Android exige hospedagem HTTPS e uma implantação corporativa protegida com autenticação, autorização, TLS e gestão de segredos; a API atual ainda não implementa autenticação. O banco contém dados de demonstração e pode conter dados locais; não compartilhe o arquivo SQLite sem revisar seu conteúdo.

Consulte [Política de privacidade](PRIVACY.md), [Política de segurança](SECURITY.md), [Contribuição](CONTRIBUTING.md), [arquitetura](doc/architecture.md), [requisitos](doc/requirements.md), [modelo de dados](doc/data-model.md) e [operação da API](docs/development.md).

O diagnóstico de erros é opcional, desativado por padrão e só transmite eventos técnicos mínimos após consentimento, caso o administrador configure um endpoint HTTPS. O app não envia os registros de clientes/produtos nem stack traces. Detalhes e limites estão na [política de privacidade](PRIVACY.md).

## Licença

O Product Manager é distribuído sob a licença [MIT](LICENSE). A política de contribuição e os termos aplicáveis a contribuições estão em [CONTRIBUTING.md](CONTRIBUTING.md).
