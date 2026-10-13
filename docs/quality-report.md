# Relatório de robustez e engenharia multiplataforma

**Data da auditoria:** 2026-10-13  
**Repositório:** [mnl-nox/product_manager](https://github.com/mnl-nox/product_manager)  
**Aplicação Web:** https://product-manager-14fq.onrender.com/login  
**Escopo:** Web como plataforma principal, PWA/Android e desktop Windows/Linux.

## 1. Resumo executivo

O Product Manager já possui uma base funcional: API Python, interface Web responsiva, autenticação por sessão, permissões por papel, SQLite, exportações, PWA e empacotamento para Windows/Linux. O trabalho de robustez deve preservar a API como contrato comum, evitando regras de negócio específicas por plataforma.

**Estado atual: funcional, mas ainda não certificado para uso crítico em produção.** A implantação pública, por si só, não comprova disponibilidade, recuperação de desastres, isolamento organizacional, acessibilidade WCAG ou segurança auditada.

Durante a verificação do pipeline multiplataforma da versão v1.1.3, os jobs Windows e PWA passaram, mas o job Linux falhou no RPM: o spec procurava `LICENSE` e `PRIVACY.md` na raiz do diretório de build, enquanto o script já os preparava em `usr/share/doc/product-manager/`. O spec foi corrigido para usar os caminhos preparados pelo empacotador. Também foram adicionados `/healthz` (liveness) e `/readyz` (readiness com teste de SQLite), e o Docker/Render passaram a usar `/readyz`. Os testes novos foram adicionados, mas precisam ser confirmados por uma execução CI posterior.

## 2. Arquitetura observada

- **Web/API:** servidor HTTP Python em `api/app.py`, interface HTML/CSS/JavaScript em `ui/`, endpoints JSON em mesma origem.
- **Persistência:** SQLite; caminho configurável por `PRODUCT_MANAGER_DB`. O blueprint Render usa disco persistente em `/data`.
- **Autenticação:** senhas com scrypt, sessões por token aleatório armazenado como hash, cookie HttpOnly/SameSite, proteção CSRF, limite de tentativas e papéis `admin`, `operator`, `finance` e `viewer`.
- **PWA:** manifest e service worker; chamadas `/api/` não são armazenadas no cache. Recursos do shell usam cache para suportar carregamento de arquivos estáticos.
- **Desktop:** launcher local e pacotes Windows/Linux; os clientes usam o mesmo código de interface e API.
- **Android:** PWA ou wrapper que abre a aplicação HTTPS publicada; o wrapper não é um cliente independente e depende da rede/servidor.
- **CI/CD:** CI executa compilação Python, testes de API, validação de Conventional Commits e build do núcleo C; workflow de pacotes produz artefatos Windows, Linux e PWA. O status do RPM v1.1.3 permanece falho no run anterior à correção.

## 3. Alteração aplicada nesta etapa

### Empacotamento Linux RPM

**Causa:** `packaging/rpm/product-manager.spec.in` copiava os documentos a partir da raiz, mas `packaging/linux/build-packages.sh` coloca os arquivos em `usr/share/doc/product-manager/` dentro da árvore de staging e do arquivo-fonte RPM.

**Correção:** o spec agora copia:
- `usr/share/doc/product-manager/LICENSE`
- `usr/share/doc/product-manager/PRIVACY.md`

para o diretório de documentação do buildroot. Isso alinha o spec ao contrato real do script de empacotamento. A validação conclusiva depende de executar novamente o workflow de pacotes.

## 4. Verificações e evidências disponíveis

| Verificação | Resultado observado | Evidência / ressalva |
|---|---|---|
| CI principal após a correção anterior | Aprovado | [Run 38348153696](https://github.com/mnl-nox/product_manager/actions/runs/38348153696) |
| Workflow de release | Aprovado | [Run 38348153800](https://github.com/mnl-nox/product_manager/actions/runs/38348153800) |
| Pacote Windows v1.1.3 | Aprovado | [Workflow de pacotes 38348165447](https://github.com/mnl-nox/product_manager/actions/runs/38348165447) |
| Arquivo PWA v1.1.3 | Aprovado | [Workflow de pacotes 38348165447](https://github.com/mnl-nox/product_manager/actions/runs/38348165447) |
| RPM v1.1.3 | Falhou antes da correção do spec | Caminhos dos documentos incorretos no buildroot |
| Correção do spec RPM | Aplicada | [Commit 4141f7b](https://github.com/mnl-nox/product_manager/commit/4141f7b58a9312b2a37a21868250df8ec9570eba); aguarda workflow posterior |
| Testes automatizados de API | Testes básicos existentes; três testes de liveness/readiness adicionados | Execução CI dos novos testes ainda não confirmada; faltam E2E reais de navegador e cobertura sistemática de autorização |
| Segurança independente | Não realizada | Este relatório é revisão técnica de repositório e CI, não pentest/certificação |
| Backup e restauração de produção | Não demonstrados nesta auditoria | Definir retenção/RPO/RTO e executar ensaio de restauração |
| Acessibilidade WCAG 2.2 AA | Não certificada | Requer testes automáticos e manuais com teclado/leitor de tela |

Os estados acima são um retrato do momento da auditoria. Um commit de correção não substitui uma execução bem-sucedida do workflow.

## 5. Riscos prioritários

### P0 — antes de uso com dados reais ou críticos

1. **Recuperação de dados:** não foi apresentada evidência de backup restaurado em ambiente isolado. Criar política de backup, retenção, criptografia, teste de restauração e objetivos RPO/RTO.
2. **Operação do serviço:** foram adicionados `/healthz` (liveness sem detalhes internos) e `/readyz` (verifica conexão SQLite e retorna 503 sem expor exceções). Docker e Render usam `/readyz`; confirmar CI e healthcheck após deploy.
3. **Controles de acesso:** ampliar testes negativos para cada papel, sessão expirada, CSRF ausente, desativação de usuário, exportações e rotas administrativas.
4. **Configuração inicial:** confirmar que o token de bootstrap foi removido/invalidado após o primeiro administrador em implantação real e manter segredos exclusivamente no ambiente seguro do provedor.
5. **CI/CD:** aguardar validação da correção RPM e estabelecer um único status de release que dependa dos testes e dos builds obrigatórios, sem declarar artefatos aprovados quando algum job falhar.

### P1 — robustez Web

1. Padronizar erros JSON, limites de payload, timeouts, identificador de correlação e logs estruturados sem credenciais/dados pessoais.
2. Adicionar testes E2E de login, logout, catálogo, filtros, alertas, financeiro, exportações e permissões, com viewport móvel e desktop.
3. Verificar cache e atualização do service worker em nova versão; nenhuma resposta autenticada ou dado de API deve entrar no cache offline.
4. Medir desempenho com catálogos maiores; implementar paginação/filtros no servidor antes de ampliar volume de dados.
5. Auditar acessibilidade: navegação por teclado, foco, contraste, zoom, formulários, mensagens de erro e leitor de tela.
6. Adicionar monitoramento externo de disponibilidade, latência e erros, com alerta e procedimento de reversão.

### P1 — dados e API

1. Criar migrações versionadas e testadas; evitar depender apenas de alterações ad hoc no startup.
2. Preservar SQLite para desktop/instalação pequena; avaliar PostgreSQL antes de múltiplas instâncias ou carga concorrente maior.
3. Definir contrato OpenAPI com esquemas, status HTTP, autenticação, CSRF, paginação e compatibilidade.
4. Revisar uso de transações, índices, constraints e concorrência em operações financeiras e de estoque.

### P2 — multi-organização e identidade

1. A instalação atual compartilha um workspace entre usuários e não oferece isolamento multi-organização.
2. Para SaaS multi-tenant, adicionar organização ao modelo de dados e derivar o tenant da identidade no servidor; nunca confiar em tenant enviado pelo navegador.
3. Escrever testes que provem isolamento em leitura, escrita, pesquisa, exportação, alertas e exclusão antes de habilitar a função.
4. Avaliar convite, recuperação de senha, MFA e OIDC conforme os requisitos reais.

### P2 — distribuição nativa

- **Windows/Linux:** testar instalação, upgrade, desinstalação, persistência do banco e abertura de links em máquinas limpas; definir assinatura e política de atualização.
- **Android:** diferenciar claramente APK de depuração e release; proteger chave de assinatura e testar em dispositivos físicos. O wrapper continuará dependente do servidor.
- **iOS:** decidir entre PWA e cliente nativo apenas depois de definir os recursos e requisitos de distribuição; ainda não declarar suporte nativo.
- **Offline:** manter offline limitado a recursos estáticos. Operações de negócio precisam indicar ausência de rede e não podem simular gravação bem-sucedida sem sincronização confiável.

## 6. Plano de trabalho e critérios de aceite

| Fase | Entrega | Critério verificável |
|---|---|---|
| 1. Pipeline | Corrigir RPM e verificar release/builds | CI, Windows, Debian, RPM e PWA verdes; artefatos presentes |
| 2. Segurança de API | Cobrir sessão, CSRF, papéis, validação e limites | Testes negativos para rotas e papéis; nenhum segredo em logs |
| 3. Saúde e operação | Liveness/readiness, monitoramento e runbook | Endpoint mínimo testado; alerta de indisponibilidade; reversão documentada |
| 4. Dados | Backup, restauração, migrações e política de retenção | Restauração ensaiada com dados sintéticos; RPO/RTO definidos |
| 5. Web UX | E2E, responsividade, acessibilidade e desempenho | Fluxos críticos aprovados em desktop e móvel; WCAG 2.2 AA avaliada |
| 6. Contrato de API | OpenAPI, paginação e erros padronizados | Contrato validado no CI e compatibilidade documentada |
| 7. Multi-plataforma | Testes de instaladores, PWA e Android | Instalação/upgrade testados em ambientes limpos; assinatura de produção verificada |
| 8. Multi-tenant | Organizações e isolamento completo, se requerido | Testes de acesso cruzado aprovados em todas as entidades e exportações |

## 7. Decisões arquiteturais recomendadas

- Manter **Web-first**: um único frontend responsivo e uma API estável compartilhada pelos clientes.
- Evitar reescrita integral antes de testes e observabilidade; endurecer a arquitetura incrementalmente.
- Não escalar horizontalmente com SQLite compartilhado. Fazer a transição de banco antes de múltiplas réplicas.
- Manter cache offline apenas para shell estático, sem cache de API ou documentos autenticados.
- Bloquear releases quando testes ou artefatos obrigatórios falharem.
- Registrar limitações conhecidas no changelog e na documentação, sem tratar roadmap como funcionalidade entregue.

## 8. Conclusão

A base multiplataforma existe e a correção do caminho dos documentos RPM foi aplicada. O próximo marco verificável é deixar o pipeline Linux verde. Para tornar o produto profissional de forma sustentável, a prioridade deve ser: pipeline reproduzível, testes de segurança/autorização, saúde operacional e backup restaurável; em seguida, E2E/acessibilidade/desempenho Web; depois, migrações, contrato de API e isolamento multi-organização caso o produto passe a atender organizações distintas.

Este relatório diferencia implementação existente, correções aplicadas e trabalho pendente. Não afirma que o aplicativo foi submetido a pentest, certificado, validado em dispositivos físicos ou aprovado para uso crítico.
