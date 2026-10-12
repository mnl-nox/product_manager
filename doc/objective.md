# Objetivo do produto

O Product Manager foi criado para reunir, em uma ferramenta simples, informações que equipes pequenas costumam manter separadas em planilhas ou cadastros diferentes: clientes, produtos e quantidades em estoque. A ideia é facilitar a consulta do catálogo e dar uma visão rápida da operação sem exigir, para começar, a implantação de uma plataforma empresarial complexa.

## Por que foi criado

Quando os dados de clientes e produtos ficam espalhados, é mais difícil encontrar informações, acompanhar o estoque e perceber itens que precisam de atenção. O Product Manager busca reduzir essa fragmentação com um cadastro central, validações básicas e um painel que resume os dados importantes para o acompanhamento diário.

## Para que serve hoje

- Cadastrar e consultar clientes e produtos por uma interface web.
- Manter informações do catálogo, como SKU, categoria, marca, preço, quantidade, fornecedor e status.
- Visualizar totais, categorias, clientes recentes e itens com estoque baixo no dashboard.
- Filtrar produtos por categoria e exportar dados do painel em CSV ou Excel (`.xlsx`); enviar o painel para uma planilha Google quando a integração for configurada pelo administrador.
- Executar localmente com persistência SQLite, sem serviço externo obrigatório.

O público inicial são equipes pequenas que precisam organizar cadastros e acompanhar produtos em um só lugar. O aplicativo também serve como base para validar fluxos e evoluir a solução com segurança.

## Limites atuais

O produto ainda não oferece autenticação, autorização, operação multiusuário ou trilha de auditoria. A integração com Google Sheets depende de credenciais e configuração administrativa; recursos como financeiro, notificações avançadas e publicação em lojas estão no planejamento e não devem ser entendidos como funcionalidades disponíveis.

Antes de uso compartilhado ou com dados corporativos reais, são necessários controles de identidade, acesso, implantação e operação adequados. Consulte [Segurança](../SECURITY.md).
