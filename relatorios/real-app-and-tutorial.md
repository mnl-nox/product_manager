# Execução real da aplicação e tutorial visual

**Data:** 13/10/2026
**Build:** `product-manager:security-qa`
**Ambiente:** Podman rootless, rede publicada apenas em `127.0.0.1:18002`, `/data` em tmpfs, conta e registros sintéticos.

## Execução e cenários HTTP

A aplicação iniciou e os endpoints `/healthz` e `/readyz` responderam `ok`/`ready`. O roteiro `/tmp/pm_live_http_test.py` executou via HTTP real: bootstrap, login, cadastro de produto e fornecedor, solicitação de compra, cotação, aprovação, criação do pedido, recebimento parcial e final, venda paga, lançamento financeiro, leitura do livro-razão e exportações CSV/XLSX. Resultado: **PASS**; estoque final esperado e observado: 6 unidades. CSV iniciou com BOM UTF-8; XLSX com assinatura ZIP.

## Interface real

Chrome headless acessou a aplicação pelo loopback, concluiu login pelo formulário web e abriu todas as áreas autenticadas. Foi submetido o formulário de cadastro de produto; a interface exibiu “Produto criado com sucesso” e a tabela passou a conter o SKU sintético `REAL-UI-QA-2`. Esse teste confirma navegação e escrita por UI; os fluxos de compra/venda/financeiro foram exercitados por API, não clicados integralmente no navegador.

Capturas atualizadas em `docs/screenshots/`: login, dashboard, produtos, compras, financeiro, alertas, relatórios, riscos/bugs, usuários e RH. Os dados exibidos são de QA e não pertencem a usuários reais.

## Cancelamento

Não existe endpoint nem fluxo de interface para cancelamento/estorno rastreável de venda ou compra nesta versão. O endpoint de exclusão de lançamento financeiro não representa cancelamento de negócio com histórico de reversão. O guia informa esse limite explicitamente.

## Documentação atualizada

- [Tutorial visual para o site](../docs/tutorial.html) e [versão Markdown](../docs/tutorial-visual.md).
- [Tutorial visual da Wiki local](../wiki/Tutorial-Visual-Wiki.md), linkado pela Home, sidebar e instalação/uso.
- [Guia de instalação e uso](../docs/installation-usage.md), README e página inicial do site agora apontam para o tutorial.

O site e a Wiki hospedados não foram publicados neste passo; os arquivos fonte estão prontos no checkout. É necessário publicar a atualização do repositório/Wiki para que os links externos exibam as novas páginas e capturas.
