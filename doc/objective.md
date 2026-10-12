# Objetivo do produto

O Product Manager foi criado para reunir, em uma ferramenta simples, informações que equipes pequenas costumam manter separadas em planilhas ou cadastros diferentes: clientes, produtos e quantidades em estoque. A ideia é facilitar a consulta do catálogo e dar uma visão rápida da operação sem exigir, para começar, a implantação de uma plataforma empresarial complexa.

## Por que foi criado

Quando os dados de clientes e produtos ficam espalhados, é mais difícil encontrar informações, acompanhar o estoque e perceber itens que precisam de atenção. O Product Manager busca reduzir essa fragmentação com um cadastro central, validações básicas e um painel que resume os dados importantes para o acompanhamento diário.

## Para que serve hoje

- Cadastrar e consultar clientes e produtos por uma interface web autenticada com papéis de acesso.
- Manter informações do catálogo, como SKU, categoria, marca, preço, quantidade, fornecedor e status.
- Visualizar totais, categorias, clientes recentes e itens com estoque baixo no dashboard.
- Filtrar produtos por categoria e exportar dados do painel em CSV ou Excel (`.xlsx`); enviar o painel para uma planilha Google quando a integração for configurada pelo administrador.
- Registrar receitas e despesas operacionais e acompanhar alertas configuráveis de estoque baixo.
- Registrar e acompanhar riscos e bugs internos sem enviá-los a serviços externos.
- Executar localmente com persistência SQLite, sem serviço externo obrigatório.

O público inicial são equipes pequenas que precisam organizar cadastros e acompanhar produtos em um só lugar. O aplicativo também serve como base para validar fluxos e evoluir a solução com segurança.

## Limites atuais

O app oferece contas locais em um espaço de trabalho compartilhado, mas ainda não possui isolamento entre organizações, login federado, recuperação de senha ou notificações por e-mail/push. A área financeira é operacional e não substitui contabilidade ou sistema fiscal. A integração com Google Sheets depende de credenciais e configuração administrativa.

Antes de implantar em produção, a organização deve configurar HTTPS, cookies Secure, controle de acesso de rede, backups e gestão de segredos. Como as contas compartilham um único workspace, confirme que essa arquitetura atende ao escopo da instalação. Consulte [Segurança](../SECURITY.md).
