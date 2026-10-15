# Inventário e política de consolidação documental

**Estado:** inventário inicial; nenhuma remoção autorizada por este documento.  
**Issue de acompanhamento:** [#57 — Consolidar documentação duplicada e definir uma fonte canônica](https://github.com/mnl-nox/product_manager/issues/57).

## Objetivo

Reduzir divergência entre documentos sem perder histórico de QA, evidências de release, requisitos ou conteúdo da Wiki. O diretório `docs/` é o ponto de entrada recomendado para documentação mantida no repositório. A Wiki deve servir como navegação e resumo, apontando para fontes canônicas sempre que possível.

## Mapa de fontes canônicas proposto

| Assunto | Fonte canônica proposta | Conteúdo relacionado | Ação segura |
|---|---|---|---|
| Visão do sistema e arquitetura | [Modelo do sistema e arquitetura](system-model-and-architecture.md) | `doc/architecture-implementation.md`, `wiki/Architecture-Summary.md` | Comparar detalhes únicos; migrar conteúdo relevante e transformar os demais em referências curtas. |
| Modelo de dados | [Modelo de dados técnico](../doc/data-model.md) | `wiki/Data-Model-Summary.md` | Manter `doc/data-model.md` como referência detalhada de tabelas e invariantes; atualizar a Wiki para resumir e apontar para ele. |
| Requisitos funcionais | [Requisitos do sistema](../doc/requirements.md) | Roadmap e descrições de funcionalidades na Wiki | Usar o documento de requisitos como contrato descritivo; manter o roadmap como planejamento, não como cópia. |
| Instalação e uso | [Instalação e primeiro acesso](installation-usage.md) | `wiki/Installation-and-Usage-Summary.md`, `wiki/Platforms-and-Deployment-Summary.md` | Unificar instruções operacionais; manter na Wiki apenas navegação/resumo se for útil. |
| QA e evidências históricas | [Plano e resultados de QA](qa-plan-and-results.md) | `docs/test-results.md`, `docs/quality-report.md`, `relatorios/`, `relatorios/qa-catalog/` | Não apagar relatórios por semelhança de título. Separar estado atual de snapshots datados e evidências de execução. |
| Auditoria | [Índice de auditoria](audit/README.md) | `docs/audit/*` | Preservar como conjunto próprio de achados, plano e evidências. |
| Relatórios de QA recentes | [Relatórios da rodada de correções](../relatorios/README.md) | `relatorios/*.md` | Preservar os relatórios de execução, correções e segurança; evitar copiar seu conteúdo para o relatório geral. |
| Casos e métricas de QA | [Relatórios de qualidade](../relatórios/README.md) | `relatórios/*.md` | Preservar como catálogo de casos e critérios de aceite. O nome com acento é legado válido, não prova duplicação. |

## Duplicação provável versus conteúdo distinto

### Sobreposição alta — revisar primeiro

- `doc/architecture-implementation.md`, `docs/system-model-and-architecture.md` e `wiki/Architecture-Summary.md` descrevem topologia e componentes. A visão consolidada deve ser a fonte narrativa principal; migrar apenas informações técnicas que ainda não estejam cobertas.
- `doc/data-model.md` e `wiki/Data-Model-Summary.md` descrevem as mesmas entidades, mas a versão em `doc/` contém regras de domínio adicionais. Não substituir a versão detalhada por um resumo da Wiki.

### Sobreposição parcial — preservar até comparar evidências

- `docs/qa-plan-and-results.md`, `docs/quality-report.md` e `docs/test-results.md` têm escopos e datas de referência diferentes. Os resultados datados são snapshots históricos e não devem ser combinados como se tivessem sido executados no mesmo commit.
- `relatorios/` contém relatórios de correções e validações da rodada recente; `relatorios/qa-catalog/` contém casos, jornadas, exemplos, métricas, desempenho e análise de aceite. Os dois diretórios não são intercambiáveis.
- Documentos da Wiki podem conter detalhes de configuração, privacidade, limitações e operação que não aparecem integralmente nos documentos locais. A Wiki precisa ser comparada antes de ser encurtada.

## Regras de consolidação

1. Comparar conteúdo, data, commit de referência e links de cada documento antes de migrar.
2. Preservar evidências históricas com data, versão/commit e estado explícito; não reescrever snapshots para aparentar estado atual.
3. Atualizar links relativos, README, índice documental, Wiki e referências nos workflows quando aplicável.
4. Não excluir arquivos só porque os títulos ou os primeiros parágrafos são semelhantes.
5. Após migração, deixar documentos secundários como redirecionamentos textuais curtos para a fonte canônica quando referências externas puderem existir.
6. Validar links locais e âncoras com `python scripts/check_markdown_links.py README.md docs/README.md`; ampliar o escopo do verificador apenas após corrigir os links legados inventariados.
7. Registrar cada remoção/migração em PR com origem, destino, conteúdo preservado e validações executadas.

## Sequência sugerida

- [ ] Confirmar este mapa e escolher uma área por PR.
- [ ] Consolidar arquitetura e atualizar a Wiki de arquitetura.
- [ ] Consolidar modelo de dados e atualizar a Wiki de dados.
- [ ] Comparar guias de instalação/plataformas e remover apenas passos obsoletos.
- [ ] Separar QA atual de relatórios históricos sem descartar evidências.
- [ ] Corrigir links locais e ampliar a validação automatizada.
- [ ] Fazer uma última busca por referências a arquivos migrados antes de qualquer remoção.
