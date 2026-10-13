# Relatório: correções e pendências de QA

**Data:** 13/10/2026
**Checkout base:** `068f4c0` (mudanças locais desta rodada ainda não commitadas)
**Repositório:** <https://github.com/mnl-nox/product_manager>

## Resumo

Corrigi o ciclo de vida das conexões SQLite, incluí auditoria na transação dos fluxos críticos e acrescentei testes de falha injetada. A suíte agora executa **54 testes, todos aprovados** e sem os `ResourceWarning` observados na rodada anterior.

As jornadas completas pela interface autenticada e o cancelamento auditável de compras/vendas continuam pendentes. Abri issues com contexto, proposta de comportamento e critérios de aceite para que não sejam tratados como já implementados.

## Correção implementada

O helper `get_db()` retornava uma conexão SQLite usada em blocos `with`. O contexto padrão da conexão confirma ou desfaz transações, mas não fecha o handle; por isso, testes do endpoint de movimentações emitiam avisos de conexões abertas.

O helper agora é um context manager que mantém o commit/rollback e fecha a conexão em `finally`, inclusive quando a operação gera erro. Um teste usa uma conexão simulada para confirmar que `close()` é chamado ao sair do contexto.

Também movi os registros de auditoria para dentro da mesma transação de venda, emissão de pedido de compra e recebimento. Assim, falha ao gravar a auditoria não deixa a alteração de negócio comprometida sem seu evento de auditoria.

## Evidência de atomicidade

Dois testes de compra e dois de venda provocam `sqlite3.IntegrityError` em pontos diferentes da operação: na inserção do movimento do livro-razão e na gravação da auditoria, depois das escritas de negócio. Após cada falha, os testes consultam o banco e verificam que saldo do produto, quantidade recebida, status do pedido/solicitação, venda, itens de venda, lançamento financeiro, movimento e auditoria retornam ao estado anterior.

Os testes verificam também que nenhum evento de auditoria fica órfão nem desaparece parcialmente. Os testes de sucesso existentes complementam a prova verificando que recebimento parcial/final e venda paga persistem os estados, movimentos, valores financeiros e auditoria coerentes juntos. Os casos são determinísticos e usam banco temporário; não simulam falha de energia, corrupção física do arquivo ou concorrência entre processos.

## Execução

Comando executado:

```text
python3 -m unittest discover -s tests -v
```

Resultado final: **54 testes em 0,147 s; OK**. Passaram o teste `test_database_context_closes_connection` e os quatro testes de rollback por falha injetada. Não houve `ResourceWarning` nesta execução.

## Validação do container Podman

- Podman: `5.4.2`, modo rootless.
- Build: `podman build --network=none --format docker -t product-manager:qa .` — **passou**. Image ID: `8d0b0ae190fe4be93e92e867c2f2446534f7f9811f28473c2bd166456ff672f1`.
- Runtime: rede `slirp4netns`, porta publicada somente em `127.0.0.1:18000`, banco SQLite em `tmpfs` de 64 MiB e token sintético temporário.
- Health: `/healthz` retornou `ok`, `/readyz` retornou `ready` e `podman inspect` reportou `running / healthy`.
- API HTTP dentro do container: bootstrap e novo login; criação de produto e fornecedor; solicitação, cotação, aprovação e emissão do pedido; recebimento parcial e final; venda paga; lançamento financeiro; consulta do livro-razão; exportações CSV e XLSX — **passou**.
- Invariante conferida: saldo final 6 unidades (3 iniciais + 5 recebidas − 2 vendidas), com dois movimentos `PURCHASE_IN` e um `SALE_OUT`.
- Limpeza: o container foi parado/removido; banco efêmero não persistiu.

O Podman avisou que o binário opcional `/usr/bin/pasta` falhava ao responder `--version`; isso não bloqueou a execução porque o teste usou `slirp4netns`. A execução não percorreu a interface autenticada no navegador nem testou volume persistente ou upgrade de banco.

Na rodada anterior, em banco descartável por HTTP, também passaram setup/login, cadastro de produto, recebimento parcial/final, venda paga com baixa, lançamento financeiro/remoção e exportação CSV/XLSX. O Chrome confirmou somente a renderização da tela de login; os fluxos autenticados não foram automatizados no navegador. O pedido usado no recebimento foi preparado diretamente no banco. Portanto, essa evidência não representa E2E completo pela interface.

## Issues abertas

### [#24 — Automatizar os fluxos críticos completos na interface real](https://github.com/mnl-nox/product_manager/issues/24)

Descreve a lacuna entre chamadas HTTP bem-sucedidas e jornadas reais no navegador. Pede E2E com login por formulário, compras do início ao fim, recebimentos, venda, baixa de estoque, financeiro, exportação e verificação dos estados persistidos, executados em banco descartável e CI.

### [#25 — Implementar cancelamento auditável de compras e vendas](https://github.com/mnl-nox/product_manager/issues/25)

Registra que não existem operações de cancelamento de compra/venda. Propõe preservar itens já recebidos em pedidos parciais; estornar venda paga com movimento `RETURN_IN` imutável e lançamento financeiro cancelado; não apagar histórico; proteger contra repetição; adicionar confirmação/motivo na interface. A política proposta precisa de validação do responsável de produto/financeiro antes de uso operacional.

O issue [#3 — Engineering: harden API, persistence, multi-tenancy and platform releases](https://github.com/mnl-nox/product_manager/issues/3) já inclui E2E web/PWA como iniciativa ampla. O #24 torna o critério dos fluxos críticos desta rodada concreto e verificável.

## Estado por item

| Item | Estado | Evidência |
|---|---|---|
| Conexões SQLite fechadas | Corrigido | `get_db()` fecha em `finally`; teste de regressão passou |
| Venda/recebimento atômicos sob falha no ledger e auditoria | Aprovado nos cenários exercitados | Quatro falhas injetadas revertem todas as escritas verificadas |
| Build e smoke da imagem Podman | Aprovado | Build offline; healthcheck saudável e fluxo HTTP de negócio em banco tmpfs |
| API HTTP dos fluxos já implementados | Aprovado nos cenários exercitados | Rodada anterior em banco descartável; recebimento usou pedido semeado diretamente |
| Fluxos críticos pela interface autenticada | Pendente | Issue #24; Chrome cobriu só a página de login |
| Cancelamento de compra/venda | Pendente | Issue #25; não há rota/ação implementada |

## Limites

Não foi implementado cancelamento nesta alteração: a regra de estorno afeta inventário, receita, relatórios e trilha de auditoria, então foi registrada para decisão explícita e implementação com regressões próprias. Também não foi declarada aprovação E2E de interface, porque o navegador não percorreu os formulários de negócio.
