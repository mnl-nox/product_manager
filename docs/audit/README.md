# Auditoria do ERP — índice de relatórios

**Estado geral:** auditoria em andamento; não há certificação de prontidão para produção crítica.  
**Data-base:** 2026-10-14  
**Repositório:** mnl-nox/product_manager

## Relatórios

| ID | Relatório | Estado | Conteúdo |
|---|---|---|---|
| AUD-00 | [Revisão estática inicial](initial-static-review.md) | Parcial | Fatos observados, riscos preliminares e áreas não verificadas |
| AUD-01 | Segurança e privacidade | Planejado | Autenticação, autorização, sessão, CSRF, segredos, dados e exportações |
| AUD-02 | Integridade de domínio e persistência | Planejado | Estoque, compras, vendas, financeiro, transações e migrações |
| AUD-03 | QA, desempenho e recuperação | Planejado | Testes, E2E, concorrência, carga, backup/restore e atualização |
| AUD-04 | UX e acessibilidade | Planejado | Tarefas de PME, onboarding, formulários, feedback, teclado e responsividade |
| AUD-05 | Implantação e operação | Planejado | Empacotamento, configuração, logs, monitoramento, atualização e incidentes |
| AUD-06 | Prontidão e risco residual | Planejado | Consolidação de achados, decisões e avaliação por perfil de implantação |

## Como ler os relatórios

Cada achado deve incluir ID único, título, severidade e confiança, evidência reproduzível, impacto, condição de ocorrência, recomendação, issue/PR relacionada, critério de fechamento e estado: confirmado, corrigido, mitigado, aceito ou não reproduzido.

Separar explicitamente:
- **Fato observado:** demonstrado pelo código, teste ou execução.
- **Risco:** consequência plausível que precisa de validação.
- **Hipótese:** possível problema ainda sem evidência suficiente.
- **Não verificado:** atividade ainda não executada.

## Severidade

- **S0 — Crítica:** risco imediato de comprometimento amplo, perda/corrupção de dados ou falha de controle fundamental. Contenção antes de releases.
- **S1 — Alta:** risco material em dados, autorização, operações financeiras/estoque ou recuperação. Corrigir antes de ampliar uso.
- **S2 — Média:** falha relevante, fragilidade de manutenção ou UX com contorno conhecido.
- **S3 — Baixa:** melhoria incremental, inconsistência menor ou dívida sem impacto imediato demonstrado.

A severidade final considera probabilidade, impacto e exposição, não apenas o local do código.

## Regras de execução

1. Começar por leitura estática e testes de caracterização, sem alterar comportamento.
2. Reproduzir achados em banco temporário e dados sintéticos; nunca incluir dados pessoais reais em relatórios/Issues.
3. Não executar testes destrutivos em produção.
4. Antes de mudanças de schema/dados, criar migração, backup validado e plano de recuperação.
5. Fazer correções em PRs pequenos e executar a suíte completa.
6. Atualizar o status com comando, ambiente, resultado e limitações; não declarar teste executado se foi apenas planejado.

## Roadmap relacionado

- Auditoria principal: #48
- Fluxos críticos de domínio: #49
- Usabilidade e acessibilidade: #50
- QA, carga e recuperação: #51
- Modularização: #36–#42
- SQLite e migração: #34, #43–#46
- Backup/recuperação: #28
- Migrações de esquema: #30
- Integração fiscal futura: #47
