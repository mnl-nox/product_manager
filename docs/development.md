# Desenvolvimento e operação

## Inicializar

```bash
python3 api/app.py
```

O servidor escuta em `127.0.0.1:8000`. `PRODUCT_MANAGER_HOST` e `PRODUCT_MANAGER_PORT` podem alterar o endereço. Na primeira inicialização, o esquema definido em `db/schema.sql` é aplicado e registros demonstrativos são inseridos quando as tabelas estão vazias. `PRODUCT_MANAGER_DB` pode apontar para um arquivo SQLite alternativo.

## API

As respostas são JSON, exceto os downloads CSV/XLSX.

| Método | Rota | Uso |
|---|---|---|
| GET | `/api/health` | Estado básico do serviço |
| GET | `/api/dashboard` | Indicadores, categorias, clientes recentes e estoque crítico |
| GET | `/api/categories` | Categorias e contagem de produtos |
| GET | `/api/clients` | Clientes cadastrados |
| GET | `/api/products?category=Hardware` | Catálogo; `category=all` lista todos |
| POST | `/api/clients` | Cadastra cliente |
| POST | `/api/products` | Cadastra produto |
| GET | `/api/dashboard/export.csv` | Exporta indicadores e dados em CSV |
| GET | `/api/dashboard/export.xlsx` | Baixa uma planilha Excel `.xlsx` |
| GET | `/api/integrations/google-sheets/status` | Informa se a integração está configurada, sem expor credenciais |
| POST | `/api/integrations/google-sheets/export` | Envia os indicadores e o catálogo exportável à planilha configurada |

## Exportações para planilhas

CSV e `.xlsx` podem ser baixados sem credenciais. O Excel é gerado localmente pela API. Para habilitar Google Sheets, ative a Google Sheets API no projeto Google Cloud, crie uma credencial de serviço ou obtenha um access token OAuth com escopo `https://www.googleapis.com/auth/spreadsheets`, compartilhe a planilha de destino com a identidade dessa credencial e configure no ambiente do servidor:

```ini
PRODUCT_MANAGER_GOOGLE_SHEETS_SPREADSHEET_ID=ID_DA_PLANILHA
PRODUCT_MANAGER_GOOGLE_SHEETS_ACCESS_TOKEN=TOKEN_OAUTH_DE_CURTA_DURACAO
PRODUCT_MANAGER_GOOGLE_SHEETS_RANGE=Export!A1
```

O token não deve ser colocado no repositório, frontend, SQLite, URL ou logs. Injete-o por um gerenciador de segredos e renove-o conforme sua validade; o app não executa o fluxo de renovação OAuth. O servidor usa `spreadsheets.values.update` com `valueInputOption=RAW` e grava no intervalo configurado. Prepare a aba/intervalo de destino com antecedência, restrinja o compartilhamento ao necessário e limpe manualmente células antigas caso a nova exportação contenha menos linhas. A planilha recebe agregados do dashboard e campos de produto (nome, categoria, SKU, marca, preço, quantidade e status); não exporta os registros pessoais dos clientes.

O endpoint usa a API oficial [`spreadsheets.values.update`](https://developers.google.com/workspace/sheets/api/reference/rest/v4/spreadsheets.values/update). O envio direto transfere os dados à infraestrutura Google associada à credencial e à planilha configurada.

Exemplo de criação de produto:

```bash
curl -X POST http://127.0.0.1:8000/api/products \
  -H 'Content-Type: application/json' \
  -d '{"name":"Notebook Pro","category":"Computadores","sku":"NB-PRO-1","reference":"REF-1","brand":"Acme","status":"available","price":4200,"quantity":4,"supplier":"Fornecedor Exemplo","notes":""}'
```

Erros de validação retornam HTTP 400; conflito de unicidade retorna HTTP 409. O esquema SQLite documenta campos obrigatórios e restrições de domínio.

## Verificações

```bash
make test
python3 -m compileall -q api scripts tests
make
```

O dashboard fica em `/` e o catálogo em `/products`.
