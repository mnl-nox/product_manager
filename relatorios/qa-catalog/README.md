# Catálogo de QA — Product Manager

Data-base: 13/10/2026. Repositório: https://github.com/mnl-nox/product_manager

Este catálogo organiza casos, métricas, exemplos e evidências de aceite para catálogo, estoque, compras/fornecedores, vendas, RH, financeiro e relatórios/indicadores. Os módulos de compras, RH, relatórios e livro-razão de estoque já foram integrados à `main`; isso não equivale a homologação completa em navegador ou ambiente produtivo. O aceite final exige todos os checks obrigatórios aprovados no mesmo commit, nenhum defeito P0/P1 aberto e artefatos por plataforma gerados e verificados. Isso reduz o risco, mas não prova ausência absoluta de bugs.

## Índice
- [Casos](casos-de-teste.md): cenários funcionais, negativos e de segurança.
- [Usos](casos-de-uso.md): jornadas por perfil e plataforma.
- [Exemplos](exemplos.md): comandos e resultados esperados.
- [Execução](execucao.md): procedimento reproduzível.
- [Métricas](metricas.md): metas e evidências.
- [Desempenho](desempenho.md): plano de carga e latência.
- [Análise](analise.md): riscos e decisão de liberação.

## Estado das evidências — snapshot 13/10/2026
- O commit de merge do PR #16 (`ed2c2cb564958e6a6f06cf395a07b3a0f0113175`) teve checks Python, C23, validação de commits, build, deploy e jobs Windows/Linux/PWA concluídos com sucesso.
- A evidência anterior de falha RPM v1.1.3 é histórica; não deve ser usada para descrever o resultado do workflow posterior.
- A suíte de estoque inclui testes de saldo inicial, migração legada, imutabilidade e endpoint de consulta. Esses testes não substituem testes E2E manuais, inventário físico ou ensaio de restauração.
- A auditoria documental foi integrada pelo PR #17 e publicada na release `v1.7.6`; CI Python/C23 e builds Windows/Linux/PWA passaram. A publicação do site e a operação real continuam sujeitas aos checks de deploy e às limitações listadas abaixo.
- Backup/restauração de produção, pentest independente, acessibilidade WCAG e homologação em dispositivos reais continuam sem evidência nesta revisão.

## Evidência obrigatória
Registrar commit SHA, URL do workflow, resultado por job, data, plataforma, artefato e defeitos. Estados permitidos: APROVADO, FALHOU, BLOQUEADO e NÃO EXECUTADO. Nunca marcar como aprovado algo não executado.

O aceite final depende dos checks no commit candidato e de evidências explícitas para as verificações que CI não cobre. Não marcar um teste manual, restauração ou validação de produção como aprovado sem executar e registrar o resultado.
