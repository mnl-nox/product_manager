# Tutorial visual do Product Manager

As capturas abaixo foram feitas em 13/10/2026 no build local em Podman, com dados sintéticos de QA. Não representam dados ou configuração da instância pública.

## Primeiro acesso e login

No primeiro acesso, o operador configura `PRODUCT_MANAGER_SETUP_TOKEN` no servidor. Crie a conta administradora com uma senha de pelo menos 12 caracteres. O token de bootstrap é de uso único. Depois do cadastro, entre com suas credenciais; não existe senha padrão.

![Login](https://raw.githubusercontent.com/mnl-nox/product_manager/main/docs/screenshots/login.png)

## Dashboard

Consulte os indicadores, resumo por categoria, estoque crítico e clientes recentes. Baixe CSV ou XLSX. A integração Google Sheets exige configuração pelo administrador.

![Dashboard](https://raw.githubusercontent.com/mnl-nox/product_manager/main/docs/screenshots/dashboard.png)

## Produtos e estoque

Pesquise por nome, SKU, marca ou fornecedor e filtre por categoria/situação. Cadastre os dados do produto. Faça movimentações de estoque pelas operações do sistema; desativar preserva o histórico e produtos com movimentos não podem ser removidos definitivamente.

![Produtos](https://raw.githubusercontent.com/mnl-nox/product_manager/main/docs/screenshots/products.png)

## Compras e recebimentos

Cadastre fornecedor e solicitação, registre cotações, aprove e crie pedido. Informe recebimentos parciais quando as quantidades chegarem em etapas. Só o recebido incrementa o estoque.

![Compras](https://raw.githubusercontent.com/mnl-nox/product_manager/main/docs/screenshots/purchasing.png)

## Financeiro

Cadastre receitas/despesas com categoria, valor, data e estado previsto ou pago. A área é operacional e não substitui contabilidade.

![Financeiro](https://raw.githubusercontent.com/mnl-nox/product_manager/main/docs/screenshots/finance.png)

## Alertas

Revise produtos abaixo do limite, ajuste o limite individual e reconheça alertas acompanhados.

![Alertas](https://raw.githubusercontent.com/mnl-nox/product_manager/main/docs/screenshots/alerts.png)

## Relatórios

Filtre indicadores e vendas por período. A venda paga baixa estoque e lança o financeiro na mesma transação.

![Relatórios](https://raw.githubusercontent.com/mnl-nox/product_manager/main/docs/screenshots/reports.png)

## Riscos e bugs

Registre bugs e riscos, prioridade, responsável e prazo; atualize o estado durante o acompanhamento.

![Riscos e bugs](https://raw.githubusercontent.com/mnl-nox/product_manager/main/docs/screenshots/work-items.png)

## Usuários e papéis

Administradores criam e desativam usuários. Papéis controlam leitura, catálogo, financeiro e administração. A API aplica a autorização independentemente da interface.

![Usuários](https://raw.githubusercontent.com/mnl-nox/product_manager/main/docs/screenshots/users.png)

## Recursos humanos

A área administrativa reúne departamentos, colaboradores, ausências, documentos e horas. Restrinja acesso aos dados pessoais.

![Recursos humanos](https://raw.githubusercontent.com/mnl-nox/product_manager/main/docs/screenshots/hr.png)

## Encerrar sessão, exportar e limites

Use **Sair** para invalidar a sessão. Proteja os arquivos exportados. Nesta versão não há fluxo rastreável de cancelamento/estorno de vendas ou compras. Para instalação, atualização e recuperação do banco, veja [Instalação e uso](Installation-and-Usage.md) e [Configuração](Configuration.md).
