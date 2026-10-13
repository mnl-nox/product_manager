# Engenharia de plataforma — Product Manager

## Objetivo

Evoluir o Product Manager existente para uma aplicação sustentável em web, PWA, Android e desktop, com API estável, dados protegidos, implantação repetível e operações observáveis. Este documento separa o que já existe do que ainda precisa ser implementado e validado; documentação não é evidência de funcionalidade entregue.

## Estado técnico observado no repositório

- API HTTP e interface web implementadas em Python/JavaScript, com banco SQLite.
- Login por sessão, senhas com scrypt, papéis de usuário, proteção CSRF e limite de tentativas documentados no código.
- Funcionalidades de catálogo, clientes, dashboard, alertas, financeiro operacional e exportação.
- Dockerfile executa como usuário não privilegiado; Render Blueprint usa disco persistente.
- PWA possui manifest e service worker; as rotas `/api/` são excluídas do cache.
- Wrapper Android abre uma instância HTTPS hospedada; não é um cliente offline independente.
- A API ainda não separa dados por organização. O SQLite e o servidor HTTP da biblioteca padrão são escolhas simples para uma implantação pequena, não uma arquitetura automaticamente escalável.
- A release 1.1.0 está registrada nos arquivos do repositório, mas a existência da tag, a publicação dos artefatos e a aprovação dos testes precisam ser verificadas no GitHub Actions.

## Arquitetura-alvo

```text
Web / PWA / Android / Desktop
            |
       HTTPS + JSON
            |
       API de aplicação
  autenticação, autorização,
  validação, limites e auditoria
            |
     camada de serviços
            |
  repositórios + migrações
            |
 PostgreSQL em produção
 SQLite para desenvolvimento
            |
 backups cifrados + restauração testada

Serviços transversais: logs estruturados, métricas, health/readiness,
gestão de segredos, monitoramento, alertas e pipeline de releases.
```

A interface deve continuar sendo um cliente da API. Regras de negócio, permissões, validação e isolamento de tenant devem residir no servidor, nunca depender apenas de controles da interface.

## Princípios de engenharia

1. **API como contrato:** documentar endpoints, esquemas, paginação, erros, autenticação e versão; adotar OpenAPI antes de criar novos clientes independentes.
2. **Compatibilidade:** manter clientes atuais funcionando durante mudanças; versionar mudanças incompatíveis e publicar política de descontinuação.
3. **Dados:** introduzir migrações numeradas, transações, índices e constraints. PostgreSQL passa a ser o banco de produção quando houver múltiplos usuários/instâncias; não copiar SQLite para múltiplas réplicas.
4. **Multi-tenancy seguro:** cada registro de negócio pertence a uma organização; o tenant é derivado da sessão/identidade no servidor, nunca confiado a um ID enviado pelo cliente. Aplicar escopo em toda consulta e escrita, constraints compostas, auditoria e testes negativos de acesso cruzado.
5. **Segredos:** nunca armazenar tokens no repositório, logs, URLs ou frontend. Rotacionar credenciais e usar o gerenciador de segredos do provedor.
6. **Observabilidade:** separar liveness e readiness; healthcheck não deve exigir login nem expor detalhes internos. Logs não devem conter senhas, cookies, tokens ou dados pessoais desnecessários.
7. **Resiliência:** backup automático com retenção definida, teste periódico de restauração, timeout para integrações externas, limites de payload e requisição, e procedimento de reversão.
8. **Acessibilidade:** objetivo WCAG 2.2 AA nos fluxos críticos, com testes de teclado, foco, contraste, zoom e leitor de tela.
9. **Privacidade:** documentar finalidade, dados coletados, retenção, exportação, exclusão e incidentes; telemetria deve ser opt-in ou justificada e minimizada.
10. **Entrega reproduzível:** CI obrigatório para testes, lint, análise de dependências, build dos artefatos e validação de migrações; release apenas após checks verdes.

## Plano de execução

### P0 — reduzir risco antes de dados reais

- [ ] Confirmar status de CI, tag/release e artefatos 1.1.0.
- [ ] Executar testes de autenticação, CSRF, papéis, sessão expirada, validação, concorrência e exportações.
- [ ] Validar que health/readiness é apropriado ao provedor e não expõe segredos.
- [ ] Criar backup automático e demonstrar restauração em ambiente separado.
- [ ] Definir responsável, política de incidentes, retenção e recuperação de desastre.
- [ ] Revisar CORS, cabeçalhos de segurança, cookies, limites de requisição e tratamento de erros.
- [ ] Confirmar que o service worker não armazena respostas privadas nem arquivos de sessão.

### P1 — API e persistência profissionais

- [ ] Formalizar contrato OpenAPI e gerar/validar exemplos de requisição e resposta.
- [ ] Criar camada de serviços e repositórios, separando roteamento HTTP, regras de negócio e SQL.
- [ ] Introduzir migrações de banco versionadas e execução de migração controlada em deploy.
- [ ] Preparar PostgreSQL, índices e política de conexão para implantação multiusuário.
- [ ] Adicionar paginação, filtros e ordenação validados para coleções extensas.
- [ ] Padronizar erros JSON, IDs de correlação e timeouts de integrações.
- [ ] Implementar idempotência para operações financeiras/importações quando necessário.

### P2 — organizações, identidade e auditoria

- [ ] Criar organizações e associação usuário-organização.
- [ ] Aplicar tenant scope no servidor em todas as entidades e endpoints.
- [ ] Escrever testes de isolamento cross-tenant para leitura, alteração, exportação e exclusão.
- [ ] Registrar auditoria com ator, tenant, ação, entidade, timestamp e alterações relevantes sem guardar segredos.
- [ ] Definir fluxo de convite, recuperação de senha, revogação de sessões e MFA.
- [ ] Avaliar OIDC para SSO corporativo; SAML só se os clientes-alvo exigirem.

### P3 — experiência multiplataforma

- [ ] Automatizar testes de interface para desktop e tamanhos móveis.
- [ ] Testar instalação/atualização PWA, modo offline limitado e recuperação de conexão.
- [ ] Construir Android release assinado com chave protegida, política de atualização e validação em dispositivos reais.
- [ ] Decidir empacotamento desktop (PyInstaller ou alternativa), instaladores, assinatura e atualização segura.
- [ ] Definir estratégia iOS: PWA ou cliente nativo conforme requisitos de loja e recursos necessários.
- [ ] Criar testes E2E cobrindo login, catálogo, alertas, financeiro e exportação em cada cliente suportado.

### P4 — operação e integrações

- [ ] Monitoramento de disponibilidade, latência, erros e uso de recursos, com alertas acionáveis.
- [ ] Ambiente de staging com dados sintéticos e promoção controlada para produção.
- [ ] Rate limiting por IP e identidade, proteção de abuso e limites de exportação.
- [ ] Integrações com fila de tarefas apenas quando operações demoradas justificarem complexidade.
- [ ] Webhooks autenticados, retries com backoff e registro de entregas caso integrações externas sejam adicionadas.
- [ ] Processo de release com notas, SBOM, análise de dependências, artefatos assinados e rollback documentado.

## Critérios mínimos para declarar produção

- Testes e build obrigatórios verdes no commit da release.
- Nenhum segredo ou dado real nos artefatos e capturas.
- TLS válido, cookies seguros e configuração de bootstrap encerrada após provisionamento.
- Backup e restauração demonstrados; RPO/RTO definidos.
- Auditoria de autorização e testes de isolamento aprovados antes de habilitar multi-tenancy.
- Migrações ensaiadas com backup e plano de reversão.
- APK/instaladores testados em dispositivos/sistemas-alvo e assinados para distribuição pública.
- Política de privacidade, termos, canal de suporte e processo de vulnerabilidade publicados.
- Monitoramento ativo e um responsável operacional identificado.

## Não prometer antes de implementar

Não declarar como prontos: isolamento entre organizações, SSO/MFA, PostgreSQL, backup restaurável, notificações push/e-mail, sincronização offline completa, APK assinado para loja, instaladores desktop assinados, suporte iOS nativo, SLA ou conformidade certificada. Cada item precisa de implementação, teste e evidência operacional.
