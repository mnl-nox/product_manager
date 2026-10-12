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
| `created_by` | Usuário que criou o registro, quando disponível |
| `active` | 1 para produto ativo; desativação preserva cadastro |

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

## Contas e sessões

- `app_users`: usuário, hash scrypt da senha, papel e estado ativo.
- `app_sessions`: hash do token de sessão, token CSRF e expiração; desativar conta revoga as sessões.
- `auth_login_limits`: contador de tentativas indexado por identificador derivado, sem guardar endereço de rede bruto.
- `audit_log`: ator, ação, tipo/ID de entidade e horário.

## Estoque e financeiro operacional

- `stock_thresholds`: limite mínimo individual e autoria da configuração.
- `stock_alert_acknowledgements`: usuário, quantidade e horário em que reconheceu o alerta.
- `finance_entries`: receitas/despesas, categoria, descrição, data e estado. O valor é armazenado em `amount_cents` como inteiro para evitar erro de arredondamento.
- `work_items`: bugs e riscos internos, com prioridade, probabilidade/impacto para riscos, estado e responsável opcional.
