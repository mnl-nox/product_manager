# AUD-00 — Revisão estática inicial do ERP

**Data-base:** 2026-10-14  
**Tipo:** revisão documental e estática parcial  
**Estado:** parcial — não equivale a pentest, auditoria independente ou execução completa de testes.

## 1. Escopo executado

Inspecionados os documentos de arquitetura/modelo de dados, esquema SQL, código principal da API e testes de API/segurança no branch principal. A revisão foi limitada ao material acessível nesta análise; não foram executados testes locais, navegador, carga, fuzzing, backup/restauração nem validação de instaladores nesta etapa.

Arquivos de referência:
- api/app.py
- db/schema.sql
- doc/architecture-implementation.md
- doc/data-model.md
- tests/test_api.py
- tests/test_security.py
- .github/workflows/ci.yml
- Makefile

## 2. Resumo executivo

O repositório tem controles e testes úteis já existentes: hashing de senha com scrypt, sessões com token armazenado em hash, cookies HttpOnly/SameSite, validação CSRF, papéis de acesso, constraints SQL, livro-razão append-only de estoque e testes de API/segurança. Esses controles reduzem alguns riscos, mas não comprovam, isoladamente, prontidão para uso empresarial crítico.

Os maiores temas de risco para o perfil PME são: acoplamento do backend em um único módulo; falta de isolamento multi-organização se uma instalação servir várias empresas; diferenças de representação monetária entre catálogo e financeiro; migrações de compatibilidade sem histórico de versões dedicado; cobertura ainda a demonstrar para falhas/repetições/concorrência, E2E, recuperação e usabilidade; lacunas funcionais declaradas nos ciclos de estoque, vendas, RH e fiscal.

Nenhum desses pontos deve ser convertido automaticamente em vulnerabilidade explorável sem teste e contexto de implantação. A severidade final depende de requisitos e evidência adicional.

## 3. Achados preliminares

### AUD-00-01 — Alta concentração de responsabilidades na API

- **Classificação inicial:** S2 — Média (risco arquitetural confirmado).
- **Evidência:** api/app.py contém servidor HTTP, rotas, autenticação/sessões, autorização, validação, SQL, regras de domínio, auditoria, exportações e integrações.
- **Impacto:** aumenta custo de revisão, risco de regressão e dificuldade de testar dependências isoladamente.
- **Recomendação:** executar a modularização incremental #36–#42, começando por caracterização de comportamento (#37), depois configuração/persistência (#38), segurança (#39), serviços de domínio (#40) e observabilidade/integrações (#41).
- **Critério de fechamento:** responsabilidades mapeadas; módulos com dependências explícitas; suíte completa e empacotamento preservados; sem mudança de comportamento não documentada.

### AUD-00-02 — Workspace compartilhado sem isolamento entre organizações

- **Classificação inicial:** S1 — Alta se uma instalação servir a múltiplas empresas; S2 no modelo de uso estritamente single-tenant.
- **Evidência:** arquitetura e modelo de dados declaram que todas as contas compartilham um workspace e que não há isolamento multi-organização.
- **Impacto:** usuários de empresas diferentes poderiam compartilhar dados se o sistema fosse operado nesse modo sem controles adicionais.
- **Recomendação:** limitar claramente o produto a uma organização por instalação até que isolamento completo seja projetado e testado; seguir #26 antes de oferecer multi-tenant.
- **Critério de fechamento:** perfil de implantação explicitado; se multi-tenant for requisito, testes negativos cobrem todas as consultas, relações, relatórios, exportações e tarefas assíncronas.

### AUD-00-03 — Representação monetária divergente

- **Classificação inicial:** S2 — Média; requer análise de impacto.
- **Evidência:** products.price é REAL, enquanto finance_entries.amount_cents e as tabelas de compras/vendas usam centavos inteiros.
- **Impacto:** risco de arredondamento inconsistente ao calcular totais, margens ou transferir valores entre módulos.
- **Recomendação:** inventariar operações monetárias e definir precisão/arredondamento; se a padronização exigir mudança de schema, usar migração versionada com fixtures legadas e reconciliação.
- **Critério de fechamento:** testes cobrem decimais, arredondamento, totais, importação/exportação e consistência entre módulos.

### AUD-00-04 — Atualização do esquema sem mecanismo versionado dedicado

- **Classificação inicial:** S2 — Média.
- **Evidência:** esquema inicial em db/schema.sql; ensure_database() em api/app.py aplica adaptações de compatibilidade.
- **Impacto:** difícil reconstruir e validar a sequência de versões, diagnosticar falhas e testar atualização de instalações antigas.
- **Recomendação:** implementar #30 com versões determinísticas, histórico, testes em banco vazio e fixtures antigas, backup pré-atualização e CI.
- **Critério de fechamento:** migrações testadas em instalações representativas e recuperação demonstrada.

### AUD-00-05 — Livro-razão de estoque não cobre todo o ciclo operacional

- **Classificação inicial:** S1 para operações que dependam de devoluções, estornos, transferências ou inventário físico; S2 nos fluxos já cobertos.
- **Evidência:** a documentação identifica OPENING_BALANCE, ADJUSTMENT, SALE_OUT e PURCHASE_IN e declara lacunas em devoluções, transferências, reservas e reconciliação física.
- **Impacto:** o sistema pode não representar integralmente eventos reais de estoque em empresas que dependam desses fluxos.
- **Recomendação:** mapear estados/invariantes e testes em #49 antes de ampliar funcionalidades; tornar limites claros para usuários.
- **Critério de fechamento:** fluxos suportados têm testes de sucesso, falha, repetição e transação; fluxos não suportados são explicitamente delimitados.

### AUD-00-06 — Indicadores operacionais não equivalem a contabilidade fiscal

- **Classificação inicial:** S1 para qualquer uso que dependa de escrituração/apuração fiscal; não é achado de bug por si só.
- **Evidência:** o modelo de dados declara que as métricas são operacionais e que o ciclo fiscal completo não está implementado.
- **Impacto:** decisões incorretas se o usuário interpretar proxies operacionais como números contábeis/fiscais oficiais.
- **Recomendação:** definir linguagem e rótulos dos relatórios, documentar limites e manter integração fiscal como requisito futuro #47, validado por especialistas e fontes oficiais.
- **Critério de fechamento:** relatórios distinguem claramente indicadores operacionais de apuração contábil/fiscal; requisitos legais são validados antes da implementação fiscal.

### AUD-00-07 — Cobertura de testes não comprova ainda a operação ponta a ponta

- **Classificação inicial:** S2 — Média, pendente de inventário completo.
- **Evidência:** existem tests/test_api.py, tests/test_security.py e CI com compilação/testes Python; a inspeção estática não demonstrou execução E2E, carga, backup/restauração ou validação de todos os pacotes.
- **Impacto:** regressões de UI, implantação, concorrência e recuperação podem passar sem serem detectadas.
- **Recomendação:** seguir #51 e publicar uma matriz requisito→teste→resultado com evidência.
- **Critério de fechamento:** cada teste declara ambiente/comando/resultado; gaps permanecem visíveis até serem executados.

## 4. Controles positivos observados

- Senhas derivadas com scrypt, em vez de armazenamento em texto puro.
- Hash do token de sessão persistido, com cookie HttpOnly/SameSite conforme documentação.
- Validação de CSRF e checagem de origem em testes de segurança.
- Testes de autorização por papel e de rotas autenticadas.
- Constraints de esquema e chaves estrangeiras.
- Livro-razão de estoque com proteção contra UPDATE/DELETE no esquema.
- Valores de financeiro e compras representados em centavos inteiros.
- Probes de liveness/readiness com resposta mínima, segundo testes existentes.

Esses itens precisam ser confirmados por execução da CI e revisão de código completa antes de serem considerados evidência de liberação.

## 5. Áreas ainda não verificadas

- Execução atual da suíte completa e status do CI.
- Revisão linha a linha de todas as rotas, permissões por objeto e operações de exportação.
- UI em navegador, acessibilidade, responsividade e testes com usuários.
- Concorrência e carga sob dados representativos.
- Backup/restauração com WAL e bancos anonimizados representativos.
- Instalação/upgrade em Windows, Linux e PWA/Android.
- Análise de dependências, segredos, configuração de produção e segurança de infraestrutura.
- Falhas de rede/serviços externos, retentativas e idempotência.
- Integridade histórica de instalações legadas.

## 6. Próximas ações

1. Executar baseline de testes e registrar ambiente/saída (#37, #51).
2. Mapear todos os endpoints, permissões e tabelas tocadas.
3. Testar invariantes de estoque/compras/vendas/financeiro (#49).
4. Conduzir auditoria específica de segurança e privacidade (#48).
5. Fazer avaliação de tarefas de PME e acessibilidade (#50).
6. Atualizar este relatório com referências a issues/PRs e estado verificado.

## 7. Limitações

Esta revisão não afirma que a aplicação foi executada ou explorada. As classificações são preliminares, condicionadas ao perfil de implantação e devem ser revistas quando houver reprodução, testes e contexto adicional. Não contém dados reais de clientes.


## 8. Pendências explícitas — não executadas nesta revisão

Os itens abaixo permanecem **pendentes**. A revisão atual foi estática/documental; não se deve interpretar a existência deste plano como execução ou aprovação.

| Atividade | Estado atual | Evidência exigida para conclusão |
|---|---|---|
| Executar a suíte automatizada | **Não executado nesta etapa** | Registrar commit, ambiente, comando e saída de `python -m compileall -q api scripts tests` e `make test`; identificar falhas e testes ignorados |
| Auditar todas as rotas da API | **Parcial / pendente** | Inventário completo de métodos, caminhos, autenticação, permissão, validação, tabelas tocadas, efeitos colaterais e testes; revisão de acesso por objeto e exportações |
| Testes de carga e concorrência | **Não executado** | Cenários, volume de dados, concorrência, latência/throughput, erros e limites observados em ambiente isolado |
| Validar backup e restauração | **Não executado** | Criar backup consistente, restaurar em ambiente separado e verificar integridade, contagens e invariantes; registrar tempos e limitações |
| Avaliar a interface no navegador | **Não executado** | Navegador/viewport, telas e fluxos avaliados, problemas visuais e funcionais reproduzíveis, acessibilidade básica e evidências sanitizadas |
| Validar instalação e atualização | **Não executado** | Resultados por plataforma suportada, instalação limpa, upgrade, primeiro acesso e recuperação de falha |

### Condição para atualizar o estado

Cada atividade deve passar de **Não executado** para **Executado** somente quando houver evidência registrada. Falhas encontradas devem virar achados com ID, severidade, passos de reprodução, impacto, issue relacionada e critério de fechamento. Se uma atividade for bloqueada, registrar o motivo e o que falta para executá-la.

Os comandos de teste acima são comandos planejados; nenhuma saída foi produzida por esta revisão documental. Não declarar que a suíte passou até executar os comandos no branch/commit a validar.
