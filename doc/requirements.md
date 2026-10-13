# Requisitos do sistema

Este documento distingue capacidades funcionais existentes de limites conhecidos. O contrato executável permanece no código da API, no esquema SQLite e nos testes.

## Requisitos funcionais

- **RF01 — Dashboard:** apresentar totais de clientes, produtos, clientes ativos e unidades em estoque, além de categorias, clientes recentes e itens críticos.
- **RF02 — Clientes:** cadastrar e consultar clientes com validação de campos e unicidade de username/CPF.
- **RF03 — Catálogo:** cadastrar, consultar, buscar e filtrar produtos por categoria, estado, nome, SKU, marca ou fornecedor.
- **RF04 — Ciclo de vida do produto:** editar, desativar e reativar produtos; remoção definitiva é administrativa e bloqueada quando existe histórico de estoque.
- **RF05 — Livro-razão de estoque:** registrar saldo inicial, ajuste manual, baixa de venda realizada e recebimento de compra; consultar histórico autenticado por produto.
- **RF06 — Estoque crítico:** calcular alertas pelo limite padrão ou mínimo configurado por produto e permitir reconhecimento do alerta.
- **RF07 — Compras:** manter fornecedores, solicitações, cotações, aprovação, pedidos e recebimentos parciais/totais, atualizando o estoque dos produtos vinculados.
- **RF08 — Vendas:** registrar vendas planejadas ou realizadas; vendas realizadas baixam estoque e geram receita conforme o fluxo implementado.
- **RF09 — Financeiro operacional:** registrar receitas e despesas previstas, realizadas ou canceladas e calcular saldos/indicadores operacionais.
- **RF10 — Relatórios:** apresentar indicadores por período, vendas, categorias e dimensões organizacionais disponíveis.
- **RF11 — Recursos humanos:** manter departamentos, colaboradores, ausências, decisões de aprovação, metadados documentais e minutos de jornada; exportar os registros de jornada para processamento externo.
- **RF12 — Acesso:** autenticar contas locais, provisionar o primeiro administrador com token temporário, aplicar papéis na API e revogar sessões de contas desativadas.
- **RF13 — Exportação:** gerar CSV/XLSX e permitir exportação opcional para Google Sheets quando configurada por administrador.
- **RF14 — Saúde do serviço:** disponibilizar probes de liveness/readiness e rota autenticada de saúde da aplicação.
- **RF15 — Riscos e bugs:** registrar e acompanhar itens internos com prioridade, estado e campos de probabilidade/impacto para riscos.
- **RF16 — Auditoria:** registrar operações relevantes com ator, ação, entidade e horário, sem afirmar que existe histórico antes/depois para todas as entidades.

## Requisitos não funcionais

- **RNF01 — Persistência:** SQLite para execução local/instalações pequenas; o banco não deve ser compartilhado entre réplicas concorrentes por cópia de arquivo.
- **RNF02 — Segurança de entrada:** validar dados no servidor e usar consultas SQL parametrizadas.
- **RNF03 — Sessão:** derivar senhas com scrypt, armazenar hash do token de sessão, usar cookie HttpOnly/SameSite e proteger mutações com token CSRF.
- **RNF04 — Interface:** oferecer layout responsivo e escapar conteúdo dinâmico antes de inseri-lo no HTML.
- **RNF05 — Testabilidade:** executar a suíte automatizada com `make test`, usando banco temporário quando aplicável.
- **RNF06 — Desktop local:** manter o servidor desktop vinculado ao loopback por padrão.
- **RNF07 — Integridade do estoque:** gravar movimentação e alteração do saldo na mesma transação; impedir UPDATE/DELETE de movimentos já registrados.
- **RNF08 — Auditoria:** manter registro de ações críticas de autenticação, administração, financeiro, alertas e operações de estoque suportadas.

## Restrições e limites conhecidos

As contas compartilham um único workspace; isolamento multi-organização e login corporativo não estão implementados. O servidor Python não fornece TLS e uma implantação compartilhada exige HTTPS externo, gestão de segredos, backup e recuperação testada. O financeiro é operacional e não realiza escrituração contábil/fiscal. O módulo de RH não calcula folha. O livro-razão não implementa todos os fluxos de inventário: devoluções, transferências entre depósitos, reservas formais, estornos e reconciliação física completa ainda precisam ser desenvolvidos. O núcleo C23 é independente e não participa do fluxo web Python.

## Critérios de aceite para mudanças

1. Atualizar este documento e a referência da API quando o comportamento ou os contratos mudarem.
2. Adicionar testes para fluxo feliz, validação, autorização, transação e falhas.
3. Testar migração com banco novo e banco legado sintético, sem dados pessoais reais.
4. Confirmar CI verde no commit final e descrever o que não foi validado em ambiente nativo.
5. Não declarar capacidade de produção, conformidade fiscal/trabalhista ou isolamento multi-tenant sem implementação e evidência verificável.
