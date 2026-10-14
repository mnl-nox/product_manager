# Plano de auditoria e profissionalização do ERP

**Objetivo:** tornar o ERP mais confiável, seguro, compreensível e operacional para pequenas e médias empresas antes de ampliar escopo fiscal ou outras funcionalidades específicas.

## 1. Estratégia

A auditoria é incremental e baseada em risco. Primeiro estabelece o estado atual; depois reproduz e prioriza problemas; só então implementa correções pequenas com testes. A ordem evita que uma refatoração ampla esconda defeitos de negócio ou introduza regressões.

### Fase 0 — Baseline e contenção
- Fixar commit/branch e ambiente.
- Executar compilação e suíte existente; registrar resultados sem editar código.
- Confirmar instalação limpa, primeiro acesso e criação do administrador.
- Identificar riscos de segurança ou integridade que exijam contenção imediata.
- Artefato: AUD-00 e baseline de QA.

### Fase 1 — Modelo e rastreabilidade
- Manter o documento de arquitetura e modelo sincronizado com o código.
- Catalogar endpoints, papel/permissão, tabelas afetadas, efeitos colaterais e testes.
- Mapear entidades, relações, estados e invariantes.
- Registrar decisões arquiteturais e lacunas de domínio.
- Artefato: mapa de endpoints/dados, diagramas de fluxo e ADRs necessários.

### Fase 2 — Segurança e privacidade
- Revisar autenticação, bootstrap, senha, sessão, expiração/revogação, CSRF e origem.
- Validar autorização em todas as rotas, incluindo IDOR/controle por objeto, exportações e endpoints secundários.
- Revisar limites de requisição, parsing, erros, logs, segredos e configuração de produção.
- Avaliar dados pessoais, permissões de arquivos, backups, retenção e exposição.
- Não executar pentest contra produção sem autorização e ambiente definido.
- Artefato: AUD-01 com evidência reproduzível, severidade e plano de correção.

### Fase 3 — Integridade de domínio e persistência
- Testar compras, recebimento parcial/final, vendas, movimentos de estoque, financeiro e cancelamentos.
- Verificar atomicidade, constraints, repetição de requisição, concorrência e consistência entre tabelas.
- Revisar dinheiro, arredondamento, datas, estados e transições.
- Validar migrações e instalações legadas com dados sintéticos.
- Artefato: AUD-02, catálogo de invariantes e testes de regressão.

### Fase 4 — Qualidade, desempenho e recuperação
- Executar testes unitários e de integração; ampliar E2E dos fluxos mais usados.
- Medir concorrência e latência com cenários realistas, coordenando com #43.
- Testar backup/restauração, atualização de schema e recuperação de falha.
- Validar empacotamento e instalação por plataforma suportada.
- Artefato: AUD-03 e matriz requisito→teste→resultado.

### Fase 5 — UX, acessibilidade e uso real
- Definir tarefas típicas de PME e critérios de conclusão.
- Avaliar onboarding, estados vazios, mensagens, validação, confirmações e prevenção de erros.
- Verificar teclado, foco, contraste, leitura de rótulos e responsividade.
- Testar fluxos de cadastro, compra, recebimento, venda, financeiro e exportação.
- Artefato: AUD-04 com severidade, frequência, evidência e recomendações.

### Fase 6 — Implantação e suporte
- Revisar configuração, HTTPS, persistência de dados, logs, diagnósticos e atualização.
- Validar guias de instalação, recuperação e suporte.
- Definir SLO, RPO, RTO e responsabilidades conforme perfil, coordenando com #44.
- Artefato: AUD-05.

### Fase 7 — Correções e relatório final
- Priorizar S0/S1 antes de funcionalidades novas.
- Implementar correções em PRs pequenos, com teste que falhava antes e passa depois.
- Rodar suíte completa, revisar diffs e atualizar documentação.
- Emitir relatório final com risco residual, evidências e prontidão por perfil.
- Artefato: AUD-06.

## 2. Regras de priorização

1. Segurança explorável, perda/corrupção de dados e quebra de autorização.
2. Inconsistência em estoque, compras, vendas ou financeiro.
3. Falhas de atualização, backup e recuperação.
4. Bloqueios de uso e riscos de erro operacional na UX.
5. Performance que viola critérios medidos.
6. Dívida arquitetural que impede testes e correções seguras.
7. Melhorias estéticas e novas funcionalidades não essenciais.

## 3. Modelo obrigatório para cada achado

| Campo | Conteúdo |
|---|---|
| ID | AUD-XX-NN |
| Título | Uma frase clara |
| Estado | Confirmado / risco / hipótese / não reproduzido / corrigido |
| Severidade | S0, S1, S2 ou S3 |
| Confiança | Alta, média ou baixa |
| Evidência | Arquivo/linha, teste, cenário ou saída sanitizada |
| Pré-condições | Perfil, papel, estado de dados e configuração |
| Impacto | Negócio, segurança, integridade, disponibilidade ou usabilidade |
| Reprodução | Passos exatos, sem dados pessoais |
| Recomendação | Correção e alternativa |
| Teste de regressão | Como impedir recorrência |
| Rastreamento | Issue/PR/commit |
| Fechamento | Resultado objetivo que comprova a correção |

## 4. Modelo de relatório por fase

Cada relatório deve conter: sumário executivo; escopo e exclusões; ambiente, commit e comandos executados; resultados e evidências; achados por severidade; limitações e áreas não verificadas; correções recomendadas e ordem; risco residual; relação de issues/PRs; apêndice de testes com status passou, falhou, bloqueado ou não executado.

## 5. Regras mínimas para correções

- Um teste reproduz o defeito ou cenário de risco antes da correção.
- A correção é localizada e não muda contratos sem justificativa.
- Testes de regressão cobrem sucesso e falha relevante.
- Migrações de dados têm backup validado, fixture legada e reconciliação.
- Nenhum segredo ou dado pessoal real é adicionado a logs/relatórios.
- A CI é executada e seu resultado é registrado.
- A documentação descreve o comportamento efetivamente implementado.
- Revisão do diff e do impacto operacional antes de integrar.

## 6. Critérios de prontidão para PME

O produto só deve ser declarado pronto para um perfil definido quando os fluxos essenciais forem testados; permissões e limites funcionais forem explícitos; backup e restauração tiverem sido testados; atualização for reproduzível; falhas forem observáveis; documentação corresponder ao pacote publicado; riscos S0/S1 relevantes forem resolvidos ou contidos; e limites de uso fiscal, RH, multi-organização e alta disponibilidade estiverem claros.

## 7. Escopo fora da primeira etapa

- Implementar imediatamente NF-e/NFC-e ou regras fiscais sem requisitos validados.
- Reescrever o backend inteiro de uma vez.
- Declarar multi-tenant sem isolamento completo demonstrado.
- Adotar PostgreSQL ou HA sem evidência de capacidade/requisitos.
- Introduzir automação financeira/contábil além do domínio atualmente especificado.
