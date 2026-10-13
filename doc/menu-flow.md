# Fluxo de navegação

## Dashboard (`/`)

Apresenta totais do catálogo, resumo por categoria, clientes recentes, produtos com estoque crítico e ações de exportação. Os indicadores dependem dos registros existentes no workspace.

## Produtos (`/products`)

Apresenta busca e filtros de catálogo, resumo de unidades/valor de estoque e cadastro/edição de produtos. Produtos com histórico de estoque podem ser desativados, mas não removidos definitivamente. O histórico de movimentações é consultado pela API autenticada `GET /api/inventory/movements`.

## Financeiro (`/finance`)

Permite consultar e registrar receitas/despesas operacionais conforme o papel de acesso. Não substitui contabilidade ou escrituração fiscal.

## Alertas (`/alerts`)

Lista estoque crítico e permite reconhecimento/configuração de limites de acordo com as permissões aplicáveis. Não envia e-mail ou push nesta versão.

## Compras (`/purchasing`)

Reúne fornecedores, solicitações, cotações, aprovação, pedidos e recebimentos. O recebimento de itens vinculados atualiza o estoque e registra movimentação `PURCHASE_IN`.

## Recursos humanos (`/hr`)

Área administrativa restrita ao perfil `admin`. Inclui departamentos, colaboradores, ausências, metadados documentais e registros de jornada. Não calcula folha.

## Relatórios (`/reports`)

Apresenta indicadores de vendas, receita/despesas, resultado operacional e agrupamentos por período/categoria/departamento/unidade. Métricas como margem e giro são proxies operacionais e devem ser interpretadas conforme as limitações documentadas.

## Usuários (`/admin/users`)

Área de administração de contas, papéis e estado dos usuários. Desativar uma conta revoga suas sessões.

## Riscos e bugs (`/work-items`)

Permite registrar e acompanhar riscos e defeitos internos, com prioridade, estado e responsável.

## Navegação e acessibilidade

O cabeçalho oferece acesso aos módulos conforme a interface e o papel atual. A autorização efetiva é verificada pela API, não apenas por ocultação de elementos na interface. Cada página deve manter link para pular ao conteúdo principal, rótulos de formulário e região de status acessível.
