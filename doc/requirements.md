# Requisitos do sistema

## Requisitos funcionais

- **RF01 Dashboard:** apresentar totais de clientes, produtos, clientes ativos e unidades em estoque.
- **RF02 Categorias:** agrupar produtos e exibir proporção por categoria.
- **RF03 Clientes:** cadastrar cliente com username e CPF únicos e listar cadastros recentes.
- **RF04 Produtos:** cadastrar produto com SKU único, categoria, marca, preço, quantidade e status.
- **RF05 Catálogo:** listar produtos, filtrar por categoria e calcular unidades e valor de estoque exibidos.
- **RF06 Estoque crítico:** mostrar itens com quantidade igual ou inferior a cinco.
- **RF07 Exportação:** exportar indicadores e listagens em CSV compatível com planilhas.
- **RF08 Saúde:** disponibilizar rota simples para verificar o serviço e a conexão com banco.

## Requisitos não funcionais

- **RNF01:** persistência local em SQLite, sem dependências de execução externas.
- **RNF02:** validação no servidor e consultas SQL parametrizadas.
- **RNF03:** interface responsiva e conteúdo dinâmico escapado antes de inserção no HTML.
- **RNF04:** testes executáveis com `make test`, usando banco temporário.
- **RNF05:** servidor vinculado ao loopback para uso local.

## Restrições conhecidas

Não há login, permissões, trilha de auditoria ou suporte a implantação pública. O núcleo C23 existe em paralelo e ainda não participa do fluxo da aplicação web.
