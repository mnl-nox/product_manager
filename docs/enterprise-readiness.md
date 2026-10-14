# Plano de robustez operacional e prontidão empresarial

## Objetivo e escopo

Este documento estabelece critérios de engenharia para operar o Product Manager em ambientes empresariais com dados relevantes, concorrência de escrita, requisitos de auditoria e recuperação. O plano é incremental: controles de segurança, integridade e recuperação precedem novas operações administrativas e a ampliação do volume de dados.

**Estado:** especificação de trabalho; os recursos descritos não devem ser considerados implementados até que os respectivos testes e evidências estejam disponíveis.

## Princípios de controle

1. **Integridade antes de disponibilidade aparente:** operações críticas devem ser transacionais, idempotentes quando aplicável e verificáveis após falhas.
2. **Privilégio mínimo:** cada rota valida autorização no servidor; ocultar controles na interface não constitui controle de acesso.
3. **Recuperação comprovada:** backup só é considerado válido após verificação e ensaio de restauração.
4. **Migração reversível por desenho:** toda mudança de esquema deve ter versão, pré-condições, pós-condições e plano de recuperação. Para mudanças irreversíveis, documentar estratégia compensatória.
5. **Observabilidade sem vazamento:** eventos operacionais devem conter contexto útil para diagnóstico, mas nunca senhas, hashes de senha, cookies, tokens, segredos ou payloads sensíveis.
6. **Mudança auditável:** importações, alterações de permissões, migrações e ações de manutenção devem registrar ator, horário, resultado e identificador de correlação.
7. **Sem promessa de prontidão crítica sem evidência:** disponibilidade, segurança e recuperação exigem testes representativos, métricas e procedimentos operacionais aprovados.

## Priorização

### P0 — proteger dados e estabelecer recuperação

- **Backup e restauração:** automatizar backup consistente, validar integridade e testar restauração em ambiente isolado; definir RPO/RTO com responsáveis de negócio.
- **Migrações versionadas:** substituir evolução implícita de esquema como único mecanismo por migrações numeradas com checksum, controle de versão aplicada, lock de migração, pré/pós-verificações e registro de falhas.
- **Controle de acesso administrativo:** garantir que endpoints de manutenção sejam exclusivos de administradores e cobertos por testes negativos de autorização e CSRF.
- **Integridade transacional:** identificar operações multi-etapa de estoque, compras e financeiro; definir invariantes e testar rollback sob falhas.
- **Exposição de rede:** exigir HTTPS/TLS na terminação de tráfego não local, documentar proxy confiável, cabeçalhos e configuração segura; não publicar diretamente o servidor HTTP sem proteção.
- **Segregação de dados:** definir o limite de organização/tenant antes de oferecer instâncias compartilhadas a várias empresas.

### P1 — migração de clientes e administração operacional

- **Importação de catálogo existente:** fluxo de prévia, mapeamento, validação, reconciliação e confirmação explícita; detalhes no tópico abaixo.
- **Console operacional:** saúde, eventos de erro, auditoria, usuários e manutenção com RBAC, paginação, redação de segredos e trilha append-only.
- **Gestão de usuários:** desativação, revogação de sessões e auditoria; recuperação de conta deve usar fluxo de verificação seguro, não revelar se um usuário existe.
- **Observabilidade de produção:** logs estruturados, correlation ID, métricas de erro/latência e retenção definida; a ausência de telemetria não pode ser interpretada como ausência de incidentes.
- **Testes E2E e de falha:** fluxos HTTP reais com cookies/CSRF, concorrência, reinício durante operação, disco cheio, banco bloqueado e recuperação de backup.

### P2 — escala e disponibilidade

- Medir volume, contenção de escrita, taxa de SQLITE_BUSY, latências p95/p99, duração de transações e crescimento do banco.
- Avaliar PostgreSQL quando métricas, concorrência ou requisitos de operação excederem limites aceitos para SQLite.
- Separar a camada de persistência da lógica HTTP para evitar que diferenças de dialeto e transação contaminem regras de negócio.
- Tratar alta disponibilidade como arquitetura completa: banco gerenciado ou cluster, réplica/failover, monitoramento, backups, gestão de segredos, teste de desastre e procedimentos operacionais.

## Importação de banco já existente no cliente

### Objetivo

Permitir que o cliente traga produtos ativos e quantidades atuais do sistema anterior, preservando o catálogo e reduzindo recadastro. A primeira versão deve priorizar **catálogo e saldo inicial de estoque**; não deve fingir reconstruir movimentações históricas que não existem na origem.

### Formatos e limites iniciais

- CSV documentado como formato portátil e fácil de validar.
- SQLite (.db ou .sqlite) como fonte adicional, com seleção explícita de tabela e mapeamento de colunas.
- Não aceitar caminho de arquivo arbitrário informado pelo cliente para leitura no servidor.
- Não importar usuários, credenciais, sessões, permissões, dados financeiros ou dados pessoais não necessários por padrão.
- Limitar tamanho, número de linhas, duração, quantidade de tabelas e tipos de dados; validar encoding e rejeitar conteúdo inesperado.

### Fluxo obrigatório

1. **Receber em área temporária isolada:** nome do arquivo tratado como dado não confiável; gerar nome interno aleatório, limitar tamanho e restringir permissões.
2. **Inspecionar sem executar conteúdo:** para SQLite, abrir uma cópia em modo somente leitura, verificar integrity_check, listar apenas metadados e ler tabelas explicitamente selecionadas. Nunca executar SQL vindo do arquivo.
3. **Mapear campos:** código/SKU, nome, descrição, categoria, preço, quantidade e estado; exibir campos obrigatórios, opcionais e valores padrão.
4. **Pré-validar sem alterar o destino:** validar tipos, valores, limites, duplicidades e referências; retornar um relatório de erros por linha sem expor stack traces.
5. **Reconciliar duplicidades:** usar chave de negócio estável quando disponível (SKU/código); nunca presumir que nome é identificador único. Permitir política explícita de rejeitar, ignorar ou atualizar campos autorizados.
6. **Apresentar plano de importação:** contagens de novos, atualizados, ignorados e rejeitados; mostrar conflitos e política selecionada antes da confirmação.
7. **Criar backup verificável:** o backup deve ser validado e associado ao lote antes da gravação.
8. **Executar transação:** gravar o lote com identificador idempotente; falha deve resultar em rollback integral ou em retomada controlada e documentada, nunca em estado parcial silencioso.
9. **Registrar auditoria e reconciliação:** ator, data/hora, hash do arquivo, origem declarada, versão do importador, política de conflito, contagens e resultado. Não registrar conteúdo sensível completo.
10. **Limpar temporários:** remover arquivos de origem e artefatos temporários conforme política documentada; nunca incluir uploads em logs ou backups não autorizados.

### Estoque e histórico

- Se a origem fornecer apenas quantidade atual, registrar saldo inicial como movimento OPENING_BALANCE quando compatível com o livro-razão atual.
- Marcar o movimento como saldo inicial de migração e registrar o lote de origem.
- Não gerar movimentos fictícios para compras, vendas ou ajustes históricos.
- Após importar, reconciliar quantidade por produto e contagens totais; divergências bloqueiam a conclusão até serem resolvidas.

### Critérios de aceite

- Prévia não grava nem altera registros.
- Mesmo lote não cria duplicatas quando repetido.
- Arquivo corrompido, tabela não selecionada, schema desconhecido, tamanho excessivo e dados inválidos são rejeitados de forma segura.
- Política de conflito é explícita e auditável.
- Falhas simuladas no meio da transação não deixam catálogo parcialmente atualizado.
- Testes cobrem Unicode, delimitadores/aspas CSV, números inválidos, duplicidades, estoque negativo, chaves ausentes, banco legado, rollback e autorização.
- Guia de importação inclui amostra de arquivo, mapeamento, limitações e procedimento de recuperação.

## Console de administração do sistema

### Áreas

- **Visão geral:** versão da aplicação, uptime, disponibilidade da API, estado e tamanho do banco, última migração, integridade e horário/resultado do último backup verificado.
- **Incidentes e logs:** erros da API, exceções, falhas de autenticação, importações e migrações; filtro por severidade, componente, intervalo e correlation ID.
- **Usuários e sessões:** consultar usuários, papéis, status e sessões ativas; desativar usuário e revogar sessões com confirmação e trilha de auditoria.
- **Manutenção:** executar verificação de integridade, backup, limpeza de sessões expiradas e exportação de diagnóstico sanitizado.
- **Migrações:** exibir versão atual e pendente; execução somente com backup verificado, autorização elevada e registro de resultado.

### Controles obrigatórios

- Rotas administrativas com autorização no servidor, CSRF/origin validation e política de sessão; testar explicitamente usuários não administradores.
- Reautenticação ou confirmação reforçada para ações de alto impacto.
- Logs estruturados e paginados; nunca renderizar logs como HTML confiável.
- Redação de tokens, cookies, senhas, hashes, segredos e dados pessoais desnecessários.
- Auditoria append-only para ações administrativas, incluindo ator, alvo, ação, timestamp, resultado e correlation ID.
- Sem execução arbitrária de SQL, shell ou arquivos fornecidos pelo usuário.
- Retenção, exportação e acesso aos logs documentados e limitados por privilégio.

## Estratégia SQLite e migração para PostgreSQL

SQLite continua adequado para uso local, instalação individual e cargas moderadas com contenção controlada. A decisão de migrar deve decorrer de métricas e requisitos operacionais, não apenas de expectativa de crescimento.

### Métricas de decisão

- Frequência e duração de locks; erros SQLITE_BUSY e retries.
- Latência p95/p99 das operações de leitura e escrita.
- Escritas concorrentes, duração e tamanho das transações.
- Tamanho do banco, crescimento, duração de backup/restauração.
- RPO/RTO exigidos, janelas de manutenção e disponibilidade esperada.
- Número de instâncias e necessidade de múltiplos processos/hosts acessarem o mesmo banco.

### Caminho de migração

1. Inventariar SQL, triggers, constraints, tipos, datas, IDs e transações dependentes de SQLite.
2. Criar migrações versionadas e testes de contrato de persistência.
3. Isolar acesso a dados em repositórios/serviços e evitar SQL específico espalhado.
4. Provisionar PostgreSQL com credenciais e permissões mínimas, TLS, backup e monitoramento.
5. Executar migração em ambiente de teste com cópia representativa e reconciliação de contagens, chaves, saldos e constraints.
6. Ensaiar cutover e rollback, definindo janela de congelamento ou estratégia de sincronização; impedir escrita concorrente em dois bancos sem protocolo explícito.
7. Executar smoke tests de operações críticas e obter aprovação de negócio antes de produção.
8. Monitorar divergências e latência após cutover; preservar cópia de origem conforme política de retenção.

PostgreSQL não entrega alta disponibilidade automaticamente. HA exige desenho e operação de failover, monitoramento, backups testados, gestão de incidentes e metas RPO/RTO.

## Critério de saída para operação crítica

Não declarar o sistema pronto para operação crítica até que haja evidência versionada de:
- testes de autorização, CSRF e isolamento de dados;
- backup e restauração bem-sucedidos em ambiente isolado;
- migração de esquema e migração de dados com reconciliação;
- testes de concorrência e falha para fluxos de estoque/financeiro;
- observabilidade com redação e retenção;
- procedimento de incidente, rollback, recuperação e responsáveis;
- homologação dos limites operacionais, SLOs, RPO e RTO.

## Issues relacionadas

- #26 — isolamento entre organizações/tenants.
- #27 — HTTPS/TLS e implantação.
- #28 — backup, proteção e recuperação SQLite.
- #29 — recuperação segura de senha e avaliação de SSO.
- #30 — migrações de esquema versionadas.
- #31 — canal privado para vulnerabilidades.
- #32 — importação de catálogo existente.
- #33 — console de administração operacional.
- #34 — estratégia SQLite/PostgreSQL, concorrência e HA.
