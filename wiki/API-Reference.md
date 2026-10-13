# Referência da API

A API é implementada em `api/app.py`. As respostas de negócio são JSON, exceto downloads CSV/XLSX e arquivos estáticos. Os endpoints abaixo foram conferidos em `docs/development.md`.

## Autenticação e sessões

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/auth/setup-status` | Verifica se o primeiro administrador precisa ser criado |
| POST | `/api/auth/setup` | Provisiona o administrador usando token temporário |
| POST | `/api/auth/login` | Inicia sessão |
| GET | `/api/auth/me` | Retorna usuário atual e token CSRF |
| POST | `/api/auth/logout` | Revoga a sessão atual |
| GET | `/api/auth/users` | Lista usuários; acesso administrativo |
| POST | `/api/auth/users` | Cria usuário; acesso administrativo |
| POST | `/api/auth/users/{id}/deactivate` | Desativa usuário e revoga sessões; acesso administrativo |

## Saúde e catálogo

| Método | Rota | Descrição |
|---|---|---|
| GET | `/healthz` | Probe público de liveness, resposta mínima |
| GET | `/readyz` | Probe público de readiness; verifica conexão SQLite |
| GET | `/api/health` | Estado básico do serviço; exige sessão autenticada |
| GET | `/api/dashboard` | Indicadores, categorias, clientes recentes e estoque crítico |
| GET | `/api/categories` | Categorias e contagem de produtos |
| GET | `/api/clients` | Consulta clientes |
| POST | `/api/clients` | Cadastra cliente; admin/operação |
| GET | `/api/products` | Lista produtos; aceita filtro `category` |
| GET | `/api/inventory/movements?product_id=ID&limit=100` | Lista histórico de estoque; limite máximo de 500 registros |
| POST | `/api/products` | Cadastra produto; admin/operação |
| POST | `/api/products/{id}` | Atualiza produto; admin/operação |
| POST | `/api/products/{id}/deactivate` | Desativa produto sem apagar seu cadastro |
| POST | `/api/products/{id}/activate` | Reativa produto desativado |
| POST | `/api/products/{id}/delete` | Remove produto e alertas associados; admin; rejeita com conflito se houver histórico de estoque |
| GET | `/api/dashboard/export.csv` | Exporta dashboard em CSV |
| GET | `/api/dashboard/export.xlsx` | Exporta dashboard em XLSX |

Exemplo de filtro: `GET /api/products?category=Hardware`. Use `category=all` para todas as categorias.

O endpoint `GET /api/inventory/movements?product_id=ID&limit=100` retorna o histórico mais recente primeiro. `product_id` é opcional; `limit` deve ficar entre 1 e 500. Os movimentos incluem saldo inicial, ajustes, baixas de vendas realizadas e recebimentos de compras. Movimentos registrados não podem ser editados ou excluídos; produtos com histórico não podem ser removidos definitivamente.

## Financeiro, alertas e itens de trabalho

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/finance/summary` | Totais realizados e saldo projetado |
| GET/POST | `/api/finance/entries` | Lista/cria receitas e despesas |
| GET | `/api/alerts/stock` | Consulta alertas ativos de estoque |
| GET | `/api/alerts/config` | Consulta limite padrão |
| POST | `/api/alerts/stock/{id}/threshold` | Atualiza mínimo do produto |
| POST | `/api/alerts/stock/{id}/acknowledge` | Reconhece um alerta |
| GET/POST | `/api/work-items` | Lista/registra bugs e riscos |
| POST | `/api/work-items/{id}` | Atualiza estado/responsável; admin/operação |

## Compras e fornecedores

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/purchasing/suppliers` | Lista fornecedores |
| POST | `/api/purchasing/suppliers` | Cadastra fornecedor |
| GET/POST | `/api/purchasing/requests` | Lista ou cria solicitações de compra |
| GET | `/api/purchasing/requests/{id}` | Consulta solicitação, itens e cotações |
| POST | `/api/purchasing/quotes` | Registra cotação |
| POST | `/api/purchasing/requests/{id}/approve` | Aprova/rejeita solicitação conforme papel e alçada |
| POST | `/api/purchasing/requests/{id}/order` | Emite pedido com cotação escolhida |
| GET | `/api/purchasing/orders` | Lista pedidos |
| POST | `/api/purchasing/orders/{id}/receive` | Registra recebimento parcial ou total e entrada de estoque |

## Vendas e relatórios

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/reports/summary?from=YYYY-MM-DD&to=YYYY-MM-DD` | Indicadores operacionais por período |
| GET | `/api/reports/sales` | Lista registros recentes de vendas |
| POST | `/api/reports/sales` | Registra venda planejada ou realizada |
| GET | `/api/reports/dimensions` | Lista departamentos/unidades disponíveis para classificação |
| POST | `/api/org-units` | Cadastra unidade organizacional; somente administrador |

Vendas realizadas baixam estoque e geram receita dentro do fluxo implementado; vendas planejadas não baixam estoque. O sistema ainda não oferece fluxo completo de cancelamento, devolução, estorno ou custo de mercadoria vendida. As dimensões organizacionais são classificadores de relatório, não isolamento multi-organização.

## Recursos humanos

| Método | Rota | Descrição |
|---|---|---|
| GET/POST | `/api/hr/departments` | Consulta/cadastra departamentos |
| GET/POST | `/api/hr/employees` | Consulta/cadastra colaboradores |
| GET/POST | `/api/hr/absences` | Consulta/registra ausências |
| POST | `/api/hr/absences/{id}/decision` | Aprova/rejeita solicitação |
| GET/POST | `/api/hr/documents` | Consulta/cadastra metadados documentais |
| GET/POST | `/api/hr/work-time` | Consulta/registra minutos de jornada |
| GET | `/api/hr/payroll-export.csv?from=YYYY-MM-DD&to=YYYY-MM-DD` | Exporta registros de jornada para sistema de folha |

A área `/hr` e as rotas `/api/hr/` são restritas ao administrador. O módulo guarda metadados documentais, não arquivos, e não calcula folha de pagamento ou encargos.

## Google Sheets

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/integrations/google-sheets/status` | Informa se a integração está configurada, sem expor credenciais |
| POST | `/api/integrations/google-sheets/export` | Exporta indicadores e catálogo para a planilha configurada |

## Requisitos de autenticação

Todas as rotas, exceto `/api/auth/setup-status`, `/api/auth/setup`, `/api/auth/login` e arquivos estáticos, exigem sessão autenticada. Rotas de escrita exigem o cookie `pm_session` e o cabeçalho `X-CSRF-Token`, cujo valor é obtido em `GET /api/auth/me`. Os papéis são verificados no servidor.

## Erros e validação

A documentação do projeto indica HTTP 400 para erros de validação e HTTP 409 para conflitos de unicidade. Os campos obrigatórios e restrições devem ser consultados em `db/schema.sql` e `doc/data-model.md`. Não presuma que endpoints de escrita aceitam chamadas sem sessão/CSRF.

## Exportações

CSV e XLSX são gerados localmente. Google Sheets é uma integração opcional que usa um token OAuth de curta duração configurado no ambiente do servidor; o aplicativo não renova esse token automaticamente. O envio transfere os dados selecionados à conta/planilha configurada.

## Exemplo de chamada autenticada

O fluxo geral de integração é:

1. Autenticar-se por `POST /api/auth/login` e conservar o cookie de sessão.
2. Consultar `GET /api/auth/me` para obter o token CSRF.
3. Enviar o cookie e `X-CSRF-Token` nas requisições de escrita.
4. Tratar respostas de erro e conflitos; não repetir escritas sem avaliar idempotência.

O contrato exato de campos JSON deve ser validado no código de `api/app.py`; esta página resume rotas, não substitui os validadores implementados.