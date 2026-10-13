# Objetivo do produto

O Product Manager centraliza informações que equipes pequenas costumam manter em planilhas e cadastros diferentes. O objetivo é oferecer um workspace operacional para clientes, produtos, estoque, compras, vendas, financeiro, RH e indicadores, sem se apresentar como substituto automático de um ERP contábil/fiscal completo.

## Problema que resolve

Quando cadastros, quantidades e transações ficam espalhados, é difícil localizar informações, identificar estoque crítico e acompanhar o andamento das operações. O aplicativo reúne esses dados em uma interface web autenticada, com permissões aplicadas no servidor e persistência SQLite.

## Capacidades atuais

- Cadastrar e consultar clientes e produtos, com validação e busca no catálogo.
- Acompanhar saldo de estoque e alertas por limite padrão ou mínimo individual.
- Registrar saldos iniciais, ajustes manuais, baixas de vendas realizadas e recebimentos de compras em um livro-razão append-only.
- Consultar o histórico de estoque pela API autenticada `GET /api/inventory/movements`.
- Gerir fornecedores, solicitações, cotações, aprovações, pedidos e recebimentos de compras.
- Registrar vendas planejadas/realizadas e gerar indicadores operacionais de receita, despesa, resultado, contas vencidas e ranking de produtos.
- Registrar receitas/despesas e exportar dados em CSV/XLSX; a integração com Google Sheets é opcional e administrativa.
- Manter departamentos, colaboradores, ausências, metadados documentais e minutos de jornada para exportação; não calcula folha de pagamento.
- Gerir usuários locais com papéis, sessões e proteção CSRF.
- Registrar e acompanhar riscos e bugs internos.
- Executar localmente com SQLite; disponibilizar a aplicação por desktop, PWA e wrapper Android dependente de servidor HTTPS.

## Integridade de estoque

O saldo corrente é armazenado em `products.quantity`; o livro-razão registra operações suportadas na mesma transação da alteração de saldo. Movimentos são imutáveis e produtos com histórico não podem ser removidos definitivamente. Para produtos legados com saldo positivo, a migração registra um saldo inicial de referência; não reconstrói operações anteriores. O livro-razão ainda não cobre integralmente devoluções, estornos, transferências entre depósitos, reservas formais e reconciliação física.

## Público-alvo

O público inicial são equipes pequenas que precisam organizar cadastros e acompanhar operações em um só lugar. O sistema também serve como base de evolução técnica, desde que cada novo módulo seja validado por testes e documentação compatíveis.

## Limites atuais

As contas compartilham um único workspace; não há isolamento multi-organização nem identidade corporativa federada. O servidor Python não fornece TLS. A área financeira é operacional e não substitui contabilidade ou sistema fiscal. O módulo de RH não calcula folha. A integração com Google Sheets depende de credenciais configuradas por administrador. O wrapper APK depende da aplicação HTTPS publicada e não constitui um cliente independente/offline.

Antes de implantar com dados reais, configure HTTPS, cookies Secure, controle de acesso de rede, backups e gestão de segredos. Teste a restauração e valide se o workspace compartilhado atende ao escopo da instalação. Consulte [Segurança](../SECURITY.md), [implantação](../docs/deployment.md) e [resultado dos testes](../docs/test-results.md).
