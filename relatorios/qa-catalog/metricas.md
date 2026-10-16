# Métricas de qualidade

Metas propostas para aceite. O merge do PR #16 tem checks CI registrados, mas métricas de produção, backup/restauração, acessibilidade e desempenho continuam sem medição. Valores reais só devem ser preenchidos após execução.

| Métrica | Meta | Método | Estado |
|---|---|---|---|
| Testes obrigatórios aprovados | 100% | CI no commit candidato | NÃO MEDIDO |
| Testes ignorados sem justificativa | 0 | Relatório do runner | NÃO MEDIDO |
| Defeitos P0/P1 abertos | 0 | Issues e revisão técnica | NÃO MEDIDO |
| Builds obrigatórios | Todos verdes | Workflow multiplataforma | PR #16 merge: jobs Windows/Linux/PWA aprovados; falha RPM v1.1.3 é histórica |
| Artefatos esperados válidos | 100% | Inspeção dos arquivos | NÃO MEDIDO no commit atual |
| Segredos em logs | 0 ocorrências | Revisão automatizada/manual | NÃO MEDIDO |
| Erros 5xx em carga nominal | 0 no perfil de referência | Teste de carga | NÃO MEDIDO |
| Latência API p95 | Definir após baseline real | Benchmark repetível | NÃO MEDIDO |
| Restauração de backup | Exercício concluído | Restore em ambiente isolado | NÃO EXECUTADO |
| Acessibilidade | Sem bloqueios críticos; avaliar WCAG 2.2 AA | Scanner e revisão manual | NÃO MEDIDO |
| Versão/tag/changelog | Alinhados | Check no CI | `VERSION=1.7.6` após release v1.7.6; sincronização executada. Monitorar releases futuras e manter changelog versionado |

## Registro de medição
| Commit | Passaram | Falharam | Ignorados | Duração | p95 | 5xx | Artefatos |
|---|---:|---:|---:|---:|---:|---:|---|
| PENDENTE | — | — | — | — | — | — | — |

Registrar unidades, perfil de carga, hardware/runner, versões, duração e comandos. Não inventar percentis ou capacidade; cobertura de código não substitui testes comportamentais.