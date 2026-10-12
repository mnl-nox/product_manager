# Modelo de dados

O esquema é mantido em `db/schema.sql`.

## Cliente (`clients`)

| Campo | Regra |
|---|---|
| `id` | Chave primária autoincremental |
| `name`, `email`, `phone`, `city`, `role` | Obrigatórios |
| `username` | Obrigatório e único |
| `cpf` | Obrigatório e único; a API valida formato de 11 dígitos |
| `status` | `active`, `inactive` ou `pending` |
| `notes` | Observações opcionais |
| `created_at` | Data de criação gerada pelo SQLite |

## Produto (`products`)

| Campo | Regra |
|---|---|
| `id` | Chave primária autoincremental |
| `name`, `category`, `reference`, `brand`, `supplier` | Obrigatórios |
| `sku` | Obrigatório e único |
| `status` | `available`, `reserved` ou `out_of_stock` |
| `price` | Número maior ou igual a zero |
| `quantity` | Inteiro maior ou igual a zero |
| `notes` | Observações opcionais |
| `created_at` | Data de criação gerada pelo SQLite |

No dashboard, estoque total é a soma das quantidades. Valor em estoque é calculado no navegador como preço vezes quantidade para os itens filtrados/exibidos.
