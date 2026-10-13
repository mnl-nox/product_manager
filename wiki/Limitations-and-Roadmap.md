# Limitações e roadmap

O roadmap interno em `.product-manager-roadmap.md` descreve intenções futuras, não compromissos de entrega. Os itens abaixo separam capacidades atuais de evoluções planejadas.

## Limitações atuais

| Área | Estado atual | Impacto |
|---|---|---|
| Organizações | Um workspace compartilhado entre contas | Não adequado a isolamento multi-tenant |
| Identidade | Contas locais | Sem OIDC/SAML corporativo |
| Recuperação de conta | Não há recuperação automatizada de senha | Processo operacional precisa ser definido |
| Estoque | Quantidade atual e alertas | Não há livro imutável completo de entradas/saídas |
| Financeiro | Receitas/despesas operacionais | Não substitui contabilidade, fiscal ou ERP |
| Notificações | Alertas dentro do aplicativo | Sem e-mail/push externo |
| TLS | Não fornecido pelo servidor Python | PWA/serviço compartilhado precisa de HTTPS externo |
| Auditoria | Registro básico de ações | Não há trilha completa antes/depois para todas as entidades |
| Google Sheets | Exportação unidirecional por token configurado | Sem fluxo de renovação OAuth automático ou sincronização bidirecional |
| PWA | UI instalável, API online | Não é aplicação Android APK nem operação offline de dados |
| Núcleo C | Separado da aplicação web | Não é o backend da aplicação Python |

## Evoluções descritas no roadmap

- Identidade corporativa, isolamento por organização e auditoria ampliada.
- Migrações versionadas, backup/restauração testados e operação segura por ambiente.
- Melhorias de acessibilidade com objetivo WCAG 2.2 AA.
- Busca avançada, paginação, variantes, fornecedores como entidade e operações em lote.
- Movimentações imutáveis, múltiplos depósitos, inventário e alertas configuráveis.
- Relatórios com filtros, métricas de giro e exportação auditável.
- Importação CSV/XLSX com pré-visualização e validação.
- Expansão financeira operacional, aprovações, conciliação e integração com provedores, condicionadas a requisitos de negócio e validação jurídica.
- Central de bugs/riscos com filtros, anexos controlados, comentários e SLA.

A presença de uma funcionalidade no roadmap não significa que esteja implementada. Verifique o código e o changelog antes de planejar uma dependência operacional.

## Critérios para priorização

Antes de iniciar uma evolução, valide usuários-alvo, dados tratados, requisitos de segurança, custo operacional e cenários de falha. Para recursos financeiros ou de pagamento, não gere códigos Pix/boleto fictícios nem declare liquidação sem confirmação de provedor autorizado.

## Fontes

- `.product-manager-roadmap.md`
- `CHANGELOG.md`
- `doc/requirements.md`
- `docs/test-results.md`