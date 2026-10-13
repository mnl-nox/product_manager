# Modelo de dados

A persistência usa SQLite. O esquema inicial está em `db/schema.sql`; regras de domínio adicionais são aplicadas pela API.

## Entidades principais

| Tabela | Finalidade |
|---|---|
| `app_users` | Contas locais, hash de senha, papel e estado ativo |
| `app_sessions` | Hash de token de sessão, token CSRF, usuário e expiração |
| `auth_login_limits` | Limitação temporária de tentativas inválidas por identificador derivado |
| `clients` | Dados cadastrais dos clientes |
| `products` | Catálogo, SKU, categoria, marca, fornecedor, preço, quantidade e estado |
| `stock_movements` | Livro-razão append-only de entradas, saídas e ajustes com saldo anterior/posterior, motivo, ator e referência |
| `stock_thresholds` | Limite mínimo individual de estoque por produto |
| `stock_alert_acknowledgements` | Reconhecimento de alerta, quantidade observada, usuário e horário |
| `finance_entries` | Receitas/despesas previstas, realizadas ou canceladas |
| `work_items` | Registro interno de bugs e riscos |
| `suppliers` e tabelas de compras | Fornecedores, solicitações, cotações, pedidos e itens de pedido |
| `sales`, `sales_items` | Vendas e itens, com quantidades, preços e estado |
| Tabelas `hr_*` | Departamentos, colaboradores, ausências, metadados documentais e jornada |
| `org_units` | Unidades organizacionais usadas como dimensão de relatórios; não são tenants |
| `audit_log` | Ator, ação, entidade, identificador e data/hora |

## Cliente

A tabela `clients` inclui nome, username, e-mail, telefone, CPF, estado, cidade, papel/função, observações e metadados de criação. Username e CPF são únicos; a API valida o CPF como 11 dígitos. Campos de cadastro indicados no esquema são obrigatórios, salvo observações.

## Produto

A tabela `products` inclui nome, categoria, SKU, referência, marca, estado, preço, quantidade, fornecedor, observações, metadados de criação e indicador de ativo.

- SKU é obrigatório e único.
- Preço não pode ser negativo.
- Quantidade é inteira e não pode ser negativa.
- O estado de domínio pode ser `available`, `reserved` ou `out_of_stock`.
- O campo `active` controla o ciclo de vida do registro; desativação preserva o cadastro.

O dashboard calcula valor de estoque como preço multiplicado pela quantidade. O campo de preço do produto é `REAL` no SQLite; no financeiro, os valores usam centavos inteiros.

## Usuários e sessões

`app_users.role` aceita `admin`, `operator`, `finance` ou `viewer`. Senhas são armazenadas como derivação scrypt. `app_sessions` guarda o hash do token de sessão, o token CSRF e a expiração; desativar usuário revoga sessões associadas.

## Financeiro operacional

`finance_entries` armazena tipo (`income` ou `expense`), categoria, descrição, `amount_cents`, data, estado (`planned`, `paid` ou `cancelled`), autor e data de criação. `amount_cents` deve ser maior que zero, reduzindo problemas de arredondamento monetário. O módulo não é um sistema contábil/fiscal.

## Alertas de estoque

`stock_thresholds` armazena o mínimo por produto. `stock_alert_acknowledgements` registra a quantidade no momento do reconhecimento, usuário e horário. As referências a produtos usam chaves estrangeiras com exclusão em cascata para essas tabelas auxiliares.

## Bugs e riscos

`work_items` distingue `bug` e `risk`, com título, descrição, severidade, probabilidade/impacto (quando aplicável), estado, responsável, prazo opcional e autoria. Estados possíveis: `open`, `in_progress`, `resolved` e `closed`.

## Livro-razão de estoque

A tabela `stock_movements` registra `OPENING_BALANCE`, `ADJUSTMENT`, `SALE_OUT` e `PURCHASE_IN`, com delta, quantidade anterior/posterior, motivo, usuário e referência de origem. A API grava a movimentação na mesma transação que altera `products.quantity`. Triggers impedem UPDATE e DELETE; produtos com histórico devem ser desativados, não removidos definitivamente. Na primeira inicialização após a migração, produtos antigos sem movimentações recebem um saldo de abertura igual à quantidade atual. Isso estabelece um ponto de partida, não recria histórico anterior.

O endpoint `GET /api/inventory/movements` exige autenticação, aceita filtro opcional `product_id` e `limit` de 1 a 500, e retorna os movimentos mais recentes primeiro.

## Integridade e migrações

O esquema habilita chaves estrangeiras. Há índices para expiração de sessões, datas financeiras e estado/tipo de itens de trabalho. A API possui lógica de atualização compatível com versões anteriores do banco. Faça backup antes de atualizar o aplicativo e teste restauração em ambiente controlado.

## Privacidade

O banco pode conter CPF, telefone, e-mail e informações financeiras. Restrinja permissões de arquivo, proteja backups e não envie banco ou dados reais em issues públicas.