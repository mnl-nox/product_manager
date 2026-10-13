# Relatórios de qualidade — Product Manager

Data-base: 13/10/2026. Repositório: https://github.com/mnl-nox/product_manager

Esta pasta organiza os casos e evidências de aceite, incluindo os módulos de compras/fornecedores, RH e relatórios/indicadores introduzidos nas branches semânticas. O aceite final exige todos os checks obrigatórios aprovados no mesmo commit, nenhum defeito P0/P1 aberto e artefatos por plataforma gerados e verificados. Isso reduz o risco, mas não prova ausência absoluta de bugs.

## Índice
- [Casos](casos.md): cenários funcionais, negativos e de segurança.
- [Usos](usos.md): jornadas por perfil e plataforma.
- [Exemplos](exemplos.md): comandos e resultados esperados.
- [Execução](execução.md): procedimento reproduzível.
- [Métricas](métricas.md): metas e evidências.
- [Desempenho](desempenho.md): plano de carga e latência.
- [Análise](análise.md): riscos e decisão de liberação.

## Estado inicial
- CI principal e release anteriores: aprovados em execuções anteriores.
- Windows e PWA v1.1.3: aprovados no workflow 38348165447.
- Linux/RPM v1.1.3: falhou antes da correção do spec; requer nova execução.
- /healthz e /readyz, configuração Docker/Render e testes associados foram adicionados; CI e deploy ainda precisam confirmar a alteração.
- Podman: análise de ambiente reservada para uma etapa posterior; não iniciada.

## Evidência obrigatória
Registrar commit SHA, URL do workflow, resultado por job, data, plataforma, artefato e defeitos. Estados permitidos: APROVADO, FALHOU, BLOQUEADO e NÃO EXECUTADO. Nunca marcar como aprovado algo não executado.