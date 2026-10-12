# Requisitos do sistema

## Requisitos funcionais

- **RF01 Dashboard:** apresentar totais de clientes, produtos, clientes ativos e unidades em estoque.
- **RF02 Categorias:** agrupar produtos e exibir proporção por categoria.
- **RF03 Clientes:** cadastrar cliente com username e CPF únicos e listar cadastros recentes.
- **RF04 Produtos:** cadastrar produto com SKU único, categoria, marca, preço, quantidade e status.
- **RF12 Ciclo de vida do produto:** editar, desativar e reativar itens; permitir remoção permanente somente a administradores.
- **RF13 Riscos e bugs:** registrar itens internos com prioridade, campos de probabilidade/impacto para riscos e estado de acompanhamento.
- **RF05 Catálogo:** listar produtos, filtrar por categoria e calcular unidades e valor de estoque exibidos.
- **RF14 Busca:** localizar produtos por nome, SKU, marca ou fornecedor e filtrar por estado/categoria.
- **RF06 Estoque crítico:** mostrar itens no limite padrão configurável ou no mínimo definido para o produto.
- **RF07 Exportação:** exportar indicadores e listagens em CSV, Excel e, quando configurado, Google Sheets.
- **RF08 Saúde:** disponibilizar rota simples para verificar o serviço e a conexão com banco.
- **RF09 Acesso:** autenticar contas locais, aplicar papéis de administrador, operação, financeiro e leitura no servidor e encerrar sessões revogadas.
- **RF10 Financeiro:** registrar receitas/despesas previstas ou realizadas e exibir totais e saldo operacional.
- **RF11 Alertas de estoque:** listar estoque crítico por limite padrão ou limite individual, permitir confirmação de leitura e configurar limites com permissão de operação.

## Requisitos não funcionais

- **RNF01:** persistência local em SQLite, sem dependências de execução externas.
- **RNF02:** validação no servidor e consultas SQL parametrizadas.
- **RNF03:** interface responsiva e conteúdo dinâmico escapado antes de inserção no HTML.
- **RNF04:** testes executáveis com `make test`, usando banco temporário.
- **RNF05:** servidor vinculado ao loopback para uso desktop local.
- **RNF06:** senhas derivadas com scrypt; sessões aleatórias guardadas como hash, cookie HttpOnly/SameSite e mutações protegidas por token CSRF.
- **RNF07:** registrar auditoria para operações administrativas, financeiras, de alertas e acompanhamento interno.

## Restrições conhecidas

As contas pertencem a um único espaço de trabalho compartilhado; isolamento multiempresa, SSO, recuperação de conta e notificações externas ainda não estão disponíveis. O financeiro é operacional e não realiza escrituração fiscal. O núcleo C23 existe em paralelo e ainda não participa do fluxo da aplicação web.
