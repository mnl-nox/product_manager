# Desenvolvimento e operação

## Inicializar

```bash
python3 api/app.py
```

O servidor escuta em `127.0.0.1:8000`. `PRODUCT_MANAGER_HOST` e `PRODUCT_MANAGER_PORT` podem alterar o endereço. Na primeira inicialização, o esquema definido em `db/schema.sql` é aplicado e registros demonstrativos são inseridos quando as tabelas estão vazias. `PRODUCT_MANAGER_DB` pode apontar para um arquivo SQLite alternativo.

## API

Todas as respostas de leitura são JSON, salvo a exportação CSV.

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
