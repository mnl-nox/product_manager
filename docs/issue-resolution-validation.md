# Relatório de resolução de issues e validação

**Data de referência:** 16/10/2026  
**Repositório:** https://github.com/mnl-nox/product_manager  
**Objetivo:** registrar o que foi corrigido, quais evidências de teste existem, o que ainda precisa ser executado e quais issues podem ser encerradas sem afirmar resultados não comprovados.

## 1. Regra de status

- **Corrigido no código, validação pendente:** existe implementação/teste preparado, mas não há resultado de CI ou execução reproduzível confirmado para o commit.
- **Parcial:** parte do escopo foi entregue, mas os critérios de aceite continuam incompletos.
- **Validado historicamente:** existe resultado registrado para um commit/ambiente anterior; não é prova automática do estado atual.
- **Aberto:** faltam implementação, cobertura ou evidência operacional.
- **Concluído:** todos os critérios de aceite relevantes foram cumpridos e a evidência está disponível. Não atribuir este estado apenas porque um PR foi fechado.

O fechamento de um Pull Request não comprova que ele foi mesclado. Antes de encerrar uma issue de trabalho, confirme o merge e os checks do commit integrado.

## 2. Correções e mudanças recentes

### 2.1 Validação de CPF — PR #63

**Problema observado:** a validação anterior removia pontuação e verificava principalmente o comprimento de 11 dígitos. Isso permitia CPFs com dígitos verificadores incorretos e sequências repetidas.

**Correção preparada:** validar comprimento, rejeitar sequências com todos os dígitos iguais, calcular e conferir os dois dígitos verificadores e normalizar o valor válido para 11 dígitos. Foram adicionados casos de teste em `tests/test_api.py`.

**Testes adicionados:** CPF válido formatado e sem pontuação; dígitos verificadores inválidos; sequência repetida; comprimento/entrada inválidos.

**Evidência e estado:** PR [#63](https://github.com/mnl-nox/product_manager/pull/63). O registro do PR declara que a suíte não foi executada nesta sessão e que a CI deve confirmar a alteração. Portanto, a correção está **preparada, não validada por execução confirmada neste relatório**.

**Ainda falta:** executar os testes da API e a suíte completa; verificar os checks do commit que será integrado. Fazer auditoria separada dos CPFs legados formatados, detectar colisões após normalização e planejar migração sem perda antes de afirmar unicidade histórica. A alteração não reescreve registros existentes.

### 2.2 Migração financeira legada — PR #64

**Problema observado:** a migração de `finance_entries` filtrava linhas com `amount > 0`, podendo omitir valores zero, negativos ou nulos sem preservar os registros.

**Correção preparada:** fazer preflight antes de reconstruir a tabela e abortar com erro explícito que lista os IDs inválidos. A fixture legada foi ajustada para permitir `NULL`; o teste insere valor positivo, zero, negativo e nulo, espera a exceção e verifica que o schema original e todas as linhas permanecem intactos, além de verificar `PRAGMA integrity_check`.

**Evidência e estado:** PR [#64](https://github.com/mnl-nox/product_manager/pull/64). O teste de regressão foi adicionado, mas a execução e a CI constam como pendentes. A mudança está **preparada, validação pendente**.

**Ainda falta:** executar `python -m unittest discover -s tests -v` e os testes específicos de migração; verificar a CI do commit integrado; testar também banco vazio e fixtures de versões anteriores. A regra de abortar é uma proteção de preservação, não uma decisão de negócio sobre como corrigir lançamentos inválidos. É necessário documentar como o operador identifica/corrige os registros e repete a migração após backup.

### 2.3 CI de builds multiplataforma — PR #65

**Objetivo:** adicionar `.github/workflows/platform-ci.yml` para executar compilação Python e testes em Ubuntu/Windows, gerar instalador Windows, pacotes Linux DEB/RPM, APK Android de depuração e ZIP da PWA, armazenando artefatos temporários.

**Testes/verificações configurados:** `python -m compileall -q api scripts tests`; `python -m unittest discover -s tests -v`; build do instalador Windows; build DEB/RPM; build APK debug; empacotamento PWA.

**Evidência e estado:** PR [#65](https://github.com/mnl-nox/product_manager/pull/65). A descrição inicial registra que o workflow ainda não havia sido executado. Não há neste relatório resultado de workflow que comprove sucesso. Estado: **workflow preparado, execução pendente**.

**Ainda falta:** verificar os checks após o workflow ser acionado; corrigir falhas de dependências, paths ou empacotamento; inspecionar os artefatos gerados. APK debug é apenas validação, não substitui APK/AAB de release assinado. O workflow de pacotes por tags continua responsável pela publicação dos artefatos em Releases.

### 2.4 Documentação e links locais — PRs #58, #60, #61 e #62

As mudanças anteriores criaram/reorganizaram o índice documental, mapearam fontes canônicas, preservaram relatórios históricos e adicionaram verificação automatizada de links Markdown. A PR #62 também propôs normalização de nomes de arquivos e ampliação do verificador.

Fontes atuais de orientação incluem [README](../README.md), [índice documental](README.md), [inventário documental](documentation-inventory.md), [plano de QA](qa-plan-and-results.md) e [resultados históricos](test-results.md).

**Limite:** os registros dos PRs descrevem a intenção e os checks esperados, mas o estado fechado de um PR, isoladamente, não comprova merge nem aprovação da CI. A consolidação completa continua acompanhada pela issue [#57](https://github.com/mnl-nox/product_manager/issues/57), que exige comparação da Wiki, arquivos históricos, referências e conteúdo antes de remover duplicatas. Não apagar relatórios apenas por semelhança de título.

## 3. Estado das issues de auditoria

| Issue | Estado desta revisão | O que existe | O que falta para concluir |
| --- | --- | --- | --- |
| [#30 — Migrações versionadas](https://github.com/mnl-nox/product_manager/issues/30) | **Aberta** | Há lógica de migração e a proteção preparada para valores financeiros legados no PR #64. | Registro de versões aplicadas, migrações imutáveis e ordenadas, idempotência, transações/recuperação, matriz de fixtures legadas, backup/restauração e CI confirmada. Uma correção isolada não satisfaz o escopo inteiro. |
| [#36 — Modularização do backend](https://github.com/mnl-nox/product_manager/issues/36) | **Aberta** | Plano de extração incremental e testes de caracterização descritos na issue. | Implementar etapas #37–#42, demonstrar dependências sem ciclos, manter contratos HTTP e validar suíte completa/CI. Não foi demonstrada resolução nesta rodada. |
| [#49 — Fluxos críticos](https://github.com/mnl-nox/product_manager/issues/49) | **Aberta** | Testes existentes para cenários selecionados de compras, vendas, estoque e financeiro estão descritos nos documentos de QA. | Matriz completa de invariantes; falha entre gravações; repetição/idempotência; concorrência; cancelamento, devolução e estorno; reconciliação dos saldos. |
| [#51 — Estratégia de QA](https://github.com/mnl-nox/product_manager/issues/51) | **Aberta** | Suíte automatizada existente e resultados históricos registrados em [test-results.md](test-results.md). | Matriz requisito→teste→resultado atualizada; CI dos commits recentes; E2E, carga/concorrência, backup/restauração e instalação nativa nas plataformas suportadas. |
| [#57 — Documentação canônica](https://github.com/mnl-nox/product_manager/issues/57) | **Parcial / aberta** | Índice e inventário documental existem; verificação de links locais foi introduzida em PRs anteriores. | Confirmar quais PRs foram integrados e os checks; comparar Wiki e todo o conteúdo legado; validar links e âncoras em todos os documentos mantidos; registrar destino de cada migração; preservar relatórios históricos. |
| [#59 — Precisão monetária](https://github.com/mnl-nox/product_manager/issues/59) | **Aberta** | A diferença de tipos entre `products.price` (REAL) e valores em centavos foi identificada por inspeção estática. | Inventário de todos os campos/cálculos, regra de arredondamento documentada, testes de limites e reconciliação com dados sintéticos. A divergência de tipo ainda não demonstra, sozinha, erro reproduzível. |

**Nota:** a grafia correta do título da issue #51 é “Completar estratégia de QA: integração, ponta a ponta, carga e recuperação”.

## 4. Testes existentes e resultados que podem ser citados

### 4.1 Evidência histórica registrada

O documento [Resultados dos testes](test-results.md) registra uma execução local de 12/10/2026, na versão 1.0.0, em Debian 13 x86_64 com Python 3.13.5:

- `make test`: 13 testes passaram naquele ambiente.
- `python3 -m compileall -q api scripts tests`: aprovado naquele ambiente.
- `make -B`: compilação do núcleo C23 aprovada.
- `make package-linux`: pacote DEB gerado e inspecionado; não instalado.
- `make package-pwa`: ZIP gerado e validado com `unzip -t`.
- `git diff --check`: aprovado.
- Smoke test de container: build, healthcheck e fluxo HTTP registrados como aprovados.
- O documento também registra resultados históricos de CI das PRs #20 e #22, incluindo 40 e 49 testes Python aprovados, respectivamente.

Esses são **resultados históricos**, não a confirmação de que os PRs #63, #64 ou #65 passam hoje. Consulte o documento original para escopo, ambiente e limitações.

### 4.2 Testes preparados nesta rodada, ainda sem resultado confirmado

| Alteração | Teste adicionado/configurado | Resultado confirmado neste relatório |
| --- | --- | --- |
| CPF (#63) | Válido formatado/não formatado, dígitos verificadores, repetidos, comprimento/entrada inválidos | **Não** — execução pendente |
| Migração financeira (#64) | Valores zero, negativo e NULL; erro com IDs; preservação do schema/linhas; integridade SQLite | **Não** — execução pendente |
| CI multiplataforma (#65) | Testes Python em Ubuntu/Windows e builds por plataforma | **Não** — workflow sem resultado de sucesso confirmado |

### 4.3 Comandos para reproduzir

Na raiz do repositório, com a versão de Python suportada e dependências do projeto instaladas:

```bash
python -m compileall -q api scripts tests
python -m unittest discover -s tests -v
make test
python scripts/check_markdown_links.py
git diff --check
```

Se o verificador de links não aceitar execução sem argumentos na versão integrada, usar os pontos de entrada documentados no `docs/README.md`. Registrar versão de Python, commit, comando completo, resultado e logs. Não marcar um teste como aprovado apenas porque foi adicionado ao código.

## 5. Plano de validação pendente

1. Confirmar, na página de cada PR, se foi **merged** ou apenas fechado; obter o SHA integrado.
2. Consultar os checks de CI desse SHA e registrar links diretos para os jobs.
3. Executar a suíte completa e os testes específicos de CPF/migração; corrigir falhas e repetir.
4. Validar migrações com banco vazio e cópias sintéticas representativas de versões antigas. Fazer backup antes de qualquer teste destrutivo e verificar integridade e reconciliação após a operação.
5. Quando a CI multiplataforma rodar, inspecionar o conteúdo e metadados dos artefatos. Complementar builds com smoke tests de instalação/primeiro acesso nos sistemas suportados.
6. Completar testes de integração/E2E, concorrência, recuperação e segurança de acordo com as issues #49 e #51.
7. Atualizar a documentação e fechar cada issue somente quando todos os critérios de aceite daquela issue tiverem evidência rastreável.

## 6. Decisão de encerramento

Nesta revisão **não se encerra nenhuma das issues #30, #36, #49, #51, #57 ou #59**: os critérios completos de aceite ainda não foram comprovados. A #57 está parcialmente atendida, mas a comparação integral da documentação e a validação global continuam pendentes.

As PRs #63–#65 tiveram mudanças preparadas e descrições de validação pendente; não devem ser apresentadas como correções aprovadas sem confirmar merge e checks. PRs de documentação anteriores também precisam ter o merge/CI verificados antes de serem tratados como evidência de conclusão.

Este relatório separa implementação, testes escritos, testes executados e validação operacional para evitar encerramentos prematuros ou afirmações de sucesso sem evidência.
