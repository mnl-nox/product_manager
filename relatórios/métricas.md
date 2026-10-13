# Métricas de qualidade

Metas propostas para aceite; valores reais só serão preenchidos após execução.

| Métrica | Meta | Método | Estado |
|---|---|---|---|
| Testes obrigatórios aprovados | 100% | CI no commit candidato | NÃO MEDIDO |
| Testes ignorados sem justificativa | 0 | Relatório do runner | NÃO MEDIDO |
| Defeitos P0/P1 abertos | 0 | Issues e revisão técnica | NÃO MEDIDO |
| Builds obrigatórios | Todos verdes | Workflow multiplataforma | PARCIAL; RPM anterior falhou |
| Artefatos esperados válidos | 100% | Inspeção dos arquivos | NÃO MEDIDO no commit atual |
| Segredos em logs | 0 ocorrências | Revisão automatizada/manual | NÃO MEDIDO |
| Erros 5xx em carga nominal | 0 no perfil de referência | Teste de carga | NÃO MEDIDO |
| Latência API p95 | Definir após baseline real | Benchmark repetível | NÃO MEDIDO |
| Restauração de backup | Exercício concluído | Restore em ambiente isolado | NÃO EXECUTADO |
| Acessibilidade | Sem bloqueios críticos; avaliar WCAG 2.2 AA | Scanner e revisão manual | NÃO MEDIDO |
| Versão/tag/changelog | Alinhados | Check no CI | PENDENTE |

## Registro de medição
| Commit | Passaram | Falharam | Ignorados | Duração | p95 | 5xx | Artefatos |
|---|---:|---:|---:|---:|---:|---:|---|
| PENDENTE | — | — | — | — | — | — | — |

Registrar unidades, perfil de carga, hardware/runner, versões, duração e comandos. Não inventar percentis ou capacidade; cobertura de código não substitui testes comportamentais.