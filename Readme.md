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

O servidor é destinado a desenvolvimento local e escuta em `127.0.0.1`. Não há autenticação nem proteção para exposição pública; não o publique na internet sem implementar autenticação, autorização, gestão de segredos, TLS e controles de produção. O banco contém dados de demonstração e pode conter dados locais; não compartilhe o arquivo SQLite sem revisar seu conteúdo.

Consulte [Política de segurança](SECURITY.md), [Contribuição](CONTRIBUTING.md), [arquitetura](doc/architecture.md), [requisitos](doc/requirements.md), [modelo de dados](doc/data-model.md) e [operação da API](docs/development.md).

## Licença

Ainda não definida. Todos os direitos permanecem com seus respectivos titulares até a inclusão de uma licença.
