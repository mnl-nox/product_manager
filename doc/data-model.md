# Modelo de dados

O esquema SQLite está definido em `db/schema.sql`; a função `ensure_database()` em `api/app.py` aplica compatibilidade com bancos existentes. Este documento descreve o modelo funcional, não substitui as constraints do esquema.

## Clientes (`clients`)

| Campo | Regra |
|---|---|
| `id` | Chave primária autoincremental |
| `name`, `email`, `phone`, `city`, `role` | Campos cadastrais obrigatórios |
| `username` | Obrigatório e único |
| `cpf` | Obrigatório e único; a API valida formato de 11 dígitos |
| `status` | `active`, `inactive` ou `pending` |
| `notes` | Observações opcionais |
| `created_at`, `created_by` | Metadados de criação |

A tabela de clientes não usa o campo `active` do catálogo de produtos; o estado do cliente é representado por `status`.

## Produtos (`products`)

| Campo | Regra |
|---|---|
| `id` | Chave primária autoincremental |
| `name`, `category`, `reference`, `brand`, `supplier` | Campos cadastrais obrigatórios |
| `sku` | Obrigatório e único |
| `status` | `available`, `reserved` ou `out_of_stock` |
| `price` | Número maior ou igual a zero |
| `quantity` | Inteiro maior ou igual a zero; representa o saldo atual |
| `notes` | Observações opcionais |
| `active` | Indicador de ciclo de vida; desativação preserva o registro |
| `created_at`, `created_by` | Metadados de criação |

O dashboard calcula o valor de estoque como preço multiplicado pela quantidade. O campo `price` do produto é numérico no SQLite; o financeiro e as vendas armazenam valores monetários em centavos inteiros.

## Identidade, sessão e auditoria

- `app_users`: nome de usuário, hash scrypt da senha, papel, estado e metadados.
- `app_sessions`: hash do token de sessão, token CSRF, usuário e expiração.
- `auth_login_limits`: contadores de tentativas inválidas por identificador derivado.
- `audit_log`: ator, ação, tipo e ID da entidade e horário. A auditoria existente não é um histórico completo antes/depois para todas as entidades.

Os papéis incluem `admin`, `operator`, `finance` e `viewer`. As contas compartilham o mesmo workspace; não existe isolamento multi-organização.

## Livro-razão de estoque (`stock_movements`)

O saldo corrente permanece em `products.quantity`. A tabela `stock_movements` registra tipo, variação, quantidade anterior e posterior, motivo, referência da operação, usuário responsável e horário. O esquema valida a relação `quantity_after = quantity_before + quantity_delta`, impede deltas zero e usa triggers SQLite para bloquear UPDATE e DELETE.

Tipos atualmente usados pelos fluxos implementados:

- `OPENING_BALANCE`: saldo inicial informado no cadastro ou saldo de referência migrado.
- `ADJUSTMENT`: ajuste manual feito na edição da quantidade.
- `SALE_OUT`: baixa de estoque de uma venda realizada.
- `PURCHASE_IN`: entrada de mercadorias no recebimento de um pedido de compra.

O movimento e a atualização do saldo devem ser gravados na mesma transação. O endpoint autenticado `GET /api/inventory/movements` aceita filtro opcional `product_id` e `limit` de 1 a 500, ordenando os movimentos mais recentes primeiro.

Na primeira inicialização após a introdução do livro-razão, produtos legados com quantidade positiva e sem movimentos recebem um `OPENING_BALANCE) igual ao saldo atual. Isso cria um ponto de partida verificável, não reconstitui as vendas/entradas anteriores. Produtos com histórico não podem ser excluídos definitivamente; devem ser desativados. Devoluções, transferências entre depósitos, reservas formais e estornos não constituem fluxos completos nesta versão.

## Compras e vendas

- Fornecedores, solicitações, cotações, pedidos e itens de pedido representam o fluxo de compras. O recebimento parcial ou total atualiza os produtos vinculados e gera `PURCHASE_IN`.
- `sales` e `sales_items` representam os registros de venda. Vendas realizadas baixam estoque e criam receita; vendas planejadas não baixam estoque. O fluxo atual não implementa o ciclo completo de cancelamento, devolução, estorno ou custo de mercadoria vendida.

## Financeiro e relatórios

- `finance_entries`: receitas e despesas, categoria, descrição, valor em `amount_cents`, data, estado e autoria. Os estados incluem `planned`, `paid` e `cancelled`.
- `org_units` e referências opcionais a departamentos classificam vendas e lançamentos. Essas dimensões organizacionais não são tenants e não isolam dados.
- Os relatórios calculam indicadores operacionais a partir dos registros disponíveis. Margem líquida e proxy de giro não devem ser interpretadas como margem bruta ou giro contábil.

## Recursos humanos

As tabelas de RH representam departamentos, colaboradores, solicitações de ausência, metadados documentais e minutos trabalhados por dia. O módulo não calcula folha de pagamento, encargos, horas extras ou banco de horas; referências documentais não significam que o conteúdo do arquivo esteja armazenado ou servido pela API.

## Alertas e itens de trabalho

- `stock_thresholds`: limite mínimo individual de estoque.
- `stock_alert_acknowledgements`: usuário, quantidade observada e horário de reconhecimento.
- `work_items`: bugs e riscos, com prioridade, probabilidade/impacto quando aplicável, estado e responsável opcional.

## Migrações e privacidade

A inicialização mantém compatibilidade com bancos existentes, mas não substitui um sistema de migrações versionadas. Faça backup e teste a restauração antes de atualizar. O banco pode conter CPF, telefone, e-mail, informações de RH e dados financeiros; restrinja permissões do arquivo, proteja backups e não publique dados reais em issues.
