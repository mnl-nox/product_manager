# Modelo do sistema e arquitetura do ERP

**Estado:** referência arquitetural inicial  
**Escopo:** aplicação atual para uso inicial em pequenas e médias empresas (PME)  
**Atualizado:** 2026-10-14

Este documento consolida a visão de contexto, componentes, domínios, persistência, fluxos, controles e limitações conhecidas. Descreve o estado observado no repositório; não significa que o sistema tenha sido certificado para operações críticas.

Documentos complementares:
- [Arquitetura existente](../doc/architecture.md)
- [Modelo de dados funcional](../doc/data-model.md)
- [Plano de auditoria](audit/plan.md)
- [Revisão estática inicial](audit/initial-static-review.md)
- [Relatórios de auditoria](audit/README.md)

## 1. Objetivo do produto e limites

O Product Manager é um sistema de gestão operacional com interface web responsiva, PWA e launcher desktop. O conjunto atual abrange catálogo, clientes, estoque, compras, vendas, financeiro operacional, recursos humanos, alertas, relatórios e exportações.

O alvo inicial de profissionalização é uma PME que precisa de processos operacionais rastreáveis, permissões por papel, dados consistentes, instalação previsível, relatórios compreensíveis e recuperação testada.

O sistema não deve ser descrito como um ERP fiscal/contábil completo. No estado documentado:
- as contas compartilham um workspace; não há isolamento multi-organização;
- não há ciclo fiscal completo de NF-e/NFC-e, assinatura/transmissão de documentos fiscais ou gestão integral de XML fiscal;
- o módulo de RH não equivale a folha de pagamento completa;
- indicadores financeiros operacionais não substituem escrituração contábil ou apuração tributária;
- o livro-razão de estoque não cobre todos os casos de devolução, estorno, transferência, reserva e inventário;
- alta disponibilidade depende da arquitetura de implantação e operação, não apenas da escolha do banco.

## 2. Contexto e topologia atual

Usuário → navegador/PWA ou launcher desktop → UI web → HTTP/JSON → API Python em api/app.py → SQLite.

O módulo api/app.py concentra servidor HTTP, rotas, autenticação/sessões, autorização, validação, regras de domínio, auditoria, exportações, integrações e acesso SQL/transações. Essa concentração é um risco de manutenção e revisão já tratado pelo roadmap #36–#42. A separação deve ocorrer incrementalmente, mantendo contratos e comportamento, não por reescrita ampla.

## 3. Componentes e responsabilidades desejadas

| Camada | Responsabilidade | Regra de dependência |
|---|---|---|
| UI / apresentação | Exibir dados, capturar entrada, validar o básico e comunicar estados | Não decide autorização final nem é fonte de verdade das regras críticas |
| HTTP / rotas | Interpretar requisição, validar formato e converter resultado em resposta | Não deve concentrar regras de domínio ou SQL complexo |
| Aplicação / casos de uso | Coordenar operações, transações e políticas do caso de uso | Depende de serviços e contratos, não da UI |
| Domínio | Definir invariantes, estados e regras operacionais | Não depende de HTTP nem de detalhes do banco |
| Persistência | Consultas, comandos, transações, constraints e mapeamento de dados | Isola peculiaridades SQLite e futura compatibilidade com outro engine |
| Segurança transversal | Sessões, hashing, CSRF, autorização, segredos e auditoria | Política centralizada e testável |
| Observabilidade / integrações | Logs, métricas, exportações e chamadas externas | Falhas externas não podem corromper transações locais |

Esta é uma arquitetura-alvo incremental. Não significa que todas as camadas já existam como módulos independentes.

## 4. Domínios funcionais e fronteiras

### 4.1 Identidade e acesso
Entidades: app_users, app_sessions e auth_login_limits. Papéis: admin, operator, finance e viewer. A API deve impor autenticação e autorização em cada operação; esconder botões na UI não é controle de segurança.

### 4.2 Catálogo, clientes e fornecedores
products representa itens com SKU único, quantidade atual, preço e estado de atividade. clients armazena dados cadastrais e pessoais. suppliers é entidade separada. A modelagem atual de cliente contém campos obrigatórios de usuário/CPF e precisa ser revisada contra cenários comerciais reais.

### 4.3 Estoque
products.quantity é o saldo corrente. stock_movements registra movimentos append-only, incluindo saldo anterior/posterior, delta, motivo, referência, ator e horário. A atualização do saldo e o lançamento do movimento devem ser atômicos na mesma transação.

Tipos documentados incluem OPENING_BALANCE, ADJUSTMENT, SALE_OUT e PURCHASE_IN. O histórico criado por saldo de abertura de produtos legados é um ponto de partida, não reconstrução de movimentações antigas.

Lacunas a avaliar: depósitos/localizações, inventário físico, reservas formais, devoluções, estornos, transferências, unidades de medida, custo médio/PEPS, rastreio por lote/serial e prevenção de baixa duplicada.

### 4.4 Compras
O fluxo usa purchase_requests, purchase_request_items, supplier_quotes, purchase_orders, purchase_order_items e purchase_approvals. Há estados de solicitação, aprovação, pedido e recebimento parcial/final. A auditoria deve validar transições legais, autoridade para aprovar, repetição de recebimento, divergência entre pedido e recebido e atomicidade entre saldo e movimento.

### 4.5 Vendas
sales e sales_items representam vendas. Vendas realizadas baixam estoque e criam receita; planejadas não devem baixar estoque. O ciclo completo de cancelamento, devolução e estorno deve ser especificado e testado antes de tratar o fluxo como apto a operações críticas.

### 4.6 Financeiro operacional
finance_entries usa amount_cents para valores em centavos inteiros e estados planned, paid e cancelled. products.price usa atualmente REAL, diferente do padrão de centavos inteiros do financeiro e compras/vendas. Essa divergência precisa de análise e testes; não converter dados sem migração testada.

Relatórios precisam diferenciar receitas/despesas operacionais de caixa, competência, margem, lucro contábil e obrigações fiscais. Não rotular proxies como métricas contábeis definitivas.

### 4.7 Recursos humanos
As tabelas incluem departamentos, colaboradores, ausências, referências a documentos e minutos trabalhados. Não inferir armazenamento do conteúdo de documentos a partir de uma referência, nem tratar o módulo como folha completa. Dados de RH requerem controle de acesso, retenção e minimização específicos.

### 4.8 Alertas, relatórios e itens de trabalho
stock_thresholds e stock_alert_acknowledgements suportam alertas de estoque. work_items representa bugs e riscos. Exportações CSV/XLSX e integrações são superfícies de saída de dados, com controle de acesso e proteção contra exposição indevida.

## 5. Modelo de dados: relações principais

Visão simplificada, sujeita ao esquema efetivo em db/schema.sql:

- app_users relaciona-se com app_sessions, audit_log e registros criados/aprovados por usuário.
- products relaciona-se com stock_movements, limites de estoque e reconhecimentos de alerta.
- purchase_requests relaciona-se com itens, cotações, aprovações e pedido; pedidos relacionam-se com itens de pedido.
- suppliers relaciona-se com cotações e pedidos.
- sales relaciona-se com sales_items.
- finance_entries pode referenciar departamento e unidade organizacional.
- hr_departments relaciona-se com hr_employees; colaboradores relacionam-se com ausências, documentos e apontamentos de tempo.
- work_items registra riscos e bugs operacionais.

As chaves estrangeiras e constraints de db/schema.sql são a referência executável. Esta visão não substitui a inspeção de FKs, índices, triggers, colunas opcionais ou compatibilidade aplicada em ensure_database().

## 6. Invariantes de negócio a verificar

1. O saldo de estoque nunca pode ficar negativo.
2. Cada movimento deve satisfazer quantity_after = quantity_before + quantity_delta.
3. Alteração do saldo e inserção do movimento ocorrem na mesma transação.
4. Recebimento parcial não pode exceder a quantidade pedida; recebimento repetido não pode duplicar entrada.
5. Venda realizada não pode baixar estoque nem lançar receita mais de uma vez por repetição de requisição.
6. Valores monetários devem ter representação consistente e regra de arredondamento definida.
7. Registros cancelados, estornados ou devolvidos precisam de semântica explícita e histórico, sem apagar fatos financeiros/estoque.
8. Autorização é validada no servidor em cada endpoint, incluindo exportações e rotas secundárias.
9. Ações sensíveis deixam evidência de ator, entidade, ação e horário; operações de maior risco precisam de contexto suficiente para reconstrução.
10. Importações, exportações, migrações e restaurações são auditáveis, validáveis e não expõem segredos.
11. Atualizações de esquema preservam dados legados e podem ser recuperadas a partir de backup testado.
12. Não misturar dados de organizações diferentes se o produto passar a suportar multiempresa; o isolamento deve alcançar consultas, relações, relatórios, exportações e processos em segundo plano.

## 7. Segurança, privacidade e confiança operacional

Controles documentados incluem hashing scrypt de senha, hash de token de sessão persistido, cookie HttpOnly/SameSite, token CSRF e papéis de acesso. Testes existentes verificam rotas autenticadas, restrições de papéis e cenários CSRF. Isso é evidência de controles implementados, não uma auditoria independente nem garantia completa.

Áreas que requerem validação específica: ciclo de vida/revogação de sessão; bootstrap; limites de tentativas e enumeração de usuários; autorização por rota e por objeto; proteção de segredos; exposição em logs/exportações/erros; permissões do banco e backups; configuração HTTPS/TLS; dados pessoais de clientes/colaboradores e segregação multi-organização.

## 8. Persistência e migrações

O banco principal é SQLite. O esquema inicial está em db/schema.sql; compatibilidade de bancos antigos é aplicada por ensure_database(). Isso não substitui migrações versionadas e auditáveis.

Requisitos de evolução: versionar migrações e histórico aplicado; testar banco vazio e fixtures antigas; usar transações curtas e revisar contenção de escrita; definir backup consistente considerando WAL quando aplicável; provar restauração; medir antes de escolher outro engine; isolar acesso ao banco após caracterização do comportamento.

## 9. Fluxos de ponta a ponta prioritários

1. Primeiro acesso → bootstrap seguro → criação de administrador → login/logout.
2. Cadastro de produto → ajuste de saldo → consulta do livro-razão.
3. Solicitação de compra → cotação → aprovação → pedido → recebimento parcial/final → atualização de estoque.
4. Venda planejada → conclusão da venda → baixa de estoque → registro financeiro.
5. Lançamento financeiro → consulta de relatório → exportação autorizada.
6. Cadastro de colaborador → solicitação/decisão de ausência → validação de permissões.
7. Configuração de alerta → reconhecimento → atualização do estoque → reavaliação.
8. Backup → restauração em ambiente isolado → verificação de integridade.
9. Atualização de versão → migração → validação de invariantes → plano de recuperação.

## 10. Decisões e pendências

| Tema | Estado observado | Ação |
|---|---|---|
| Banco | SQLite em uso | Medir concorrência e definir gatilhos; #34, #43 |
| Modularização | Backend concentrado em api/app.py | Extração incremental; #36–#42 |
| Multi-organização | Sem isolamento entre organizações | Não oferecer multi-tenant até demonstrar isolamento; #26 |
| Fiscal | Sem ciclo fiscal completo | Requisito futuro planejado; #47 |
| Migrações | Compatibilidade em ensure_database() | Criar migrações versionadas; #30 |
| Recuperação | Procedimentos precisam de validação operacional | Backup/restore testado; #28 |
| UX | Auditoria formal pendente | Baseline de tarefas e acessibilidade; #50 |
| QA | Testes de API e segurança existentes | Completar integração, E2E, carga e recuperação; #51 |
| Alta disponibilidade | Depende da implantação | Definir SLO/RPO/RTO e topologia; #44 |

## 11. Prontidão por perfil

**Perfil A — instalação local / uso individual:** instalação e primeiro acesso claros, backup/restauração reproduzíveis, permissões locais adequadas, testes dos fluxos essenciais e mensagens de erro acionáveis.

**Perfil B — PME com vários usuários em rede interna:** além do Perfil A, autenticação/autorização auditadas, implantação de servidor documentada, HTTPS conforme exposição, concorrência testada, backup centralizado, controle de acesso e plano de atualização/recuperação.

**Perfil C — operações empresariais críticas:** além do Perfil B, objetivos formais de disponibilidade/recuperação, observabilidade, failover testado quando exigido, segregação de organizações quando aplicável, auditoria de operações sensíveis, testes de carga/recuperação, gestão de incidentes e validação regulatória especializada.

Nenhum perfil deve ser marcado como aprovado apenas por ter documentação escrita; exige evidência de testes e operação.

## 12. Glossário

- **API:** interface HTTP/JSON usada pela UI.
- **Append-only:** registro que aceita inserção, mas impede alteração/exclusão do histórico.
- **Cutover:** troca controlada para nova infraestrutura ou banco.
- **E2E:** teste ponta a ponta de um fluxo real.
- **HA:** alta disponibilidade.
- **Idempotência:** repetir a mesma operação não duplica seus efeitos.
- **RPO:** perda máxima de dados tolerada, medida em tempo.
- **RTO:** tempo máximo desejado para recuperar o serviço.
- **SLO:** objetivo mensurável de nível de serviço.
- **Tenant:** organização isolada logicamente dentro de uma instalação compartilhada.
