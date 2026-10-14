# Inventário inicial de rotas da API

**Estado:** baseline preliminar para caracterização; não é inventário completo validado em runtime.  
**Fonte:** listas de caminhos exercitadas em `tests/test_security.py` e inspeção estática de `api/app.py`.  
**Issue relacionada:** #37.

## Como interpretar

As listas abaixo registram contratos de segurança já representados nos testes existentes: requisições sem sessão devem ser recusadas e, para escritas, a proteção CSRF também deve ser aplicada. Elas não provam, por si só, que todos os caminhos dinâmicos, métodos HTTP, permissões por objeto, exportações ou efeitos colaterais foram cobertos. Rotas parametrizadas são mostradas com exemplos concretos.

## GET — caminhos presentes nos testes de sessão

| Área | Caminhos testados |
|---|---|
| Dashboard e relatórios | `/api/dashboard`, `/api/dashboard/export.csv`, `/api/dashboard/export.xlsx`, `/api/summary`, `/api/reports/dimensions`, `/api/reports/summary`, `/api/reports/sales` |
| Catálogo e clientes | `/api/categories`, `/api/clients`, `/api/products` |
| Estoque e alertas | `/api/inventory/movements`, `/api/alerts/stock`, `/api/alerts/config` |
| Compras | `/api/purchasing/suppliers`, `/api/purchasing/requests`, `/api/purchasing/orders`, `/api/purchasing/orders/1`, `/api/purchasing/requests/1` |
| Financeiro | `/api/finance/summary`, `/api/finance/entries` |
| RH | `/api/hr/departments`, `/api/hr/employees`, `/api/hr/absences`, `/api/hr/documents`, `/api/hr/work-time`, `/api/hr/payroll-export.csv` |
| Administração e integrações | `/api/auth/me`, `/api/auth/users`, `/api/telemetry/status`, `/api/integrations/google-sheets/status`, `/api/work-items`, `/api/health` |

## POST — caminhos presentes nos testes de sessão e CSRF

- Autenticação/administração: `/api/auth/logout`, `/api/auth/users`, `/api/org-units`
- Relatórios: `/api/reports/sales`
- RH: `/api/hr/departments`, `/api/hr/employees`, `/api/hr/absences`, `/api/hr/documents`, `/api/hr/work-time`
- Compras: `/api/purchasing/suppliers`, `/api/purchasing/requests`, `/api/purchasing/quotes`, `/api/purchasing/requests/1/approve`, `/api/purchasing/requests/1/order`, `/api/purchasing/orders/1/receive`
- Financeiro: `/api/finance/entries`, `/api/finance/entries/1/delete`
- Catálogo: `/api/clients`, `/api/products`, `/api/products/1`, `/api/products/1/deactivate`, `/api/products/1/activate`, `/api/products/1/delete`
- Alertas: `/api/alerts/stock/1/threshold`, `/api/alerts/stock/1/acknowledge`
- Operação/integrações: `/api/work-items`, `/api/telemetry`, `/api/integrations/google-sheets/export`

## Endpoints públicos e de prontidão

Os testes também cobrem `/healthz` como liveness público e `/readyz` como readiness que consulta o banco sem exigir autenticação. Esses caminhos não devem ser confundidos com `/api/health`, que os testes existentes tratam como autenticado.

## Lacunas que precisam ser fechadas

- Extrair a lista completa diretamente dos dispatchers GET/POST/PUT/PATCH/DELETE de `AppHandler`, incluindo todos os padrões regex.
- Registrar para cada rota: método, padrão, sessão, permissão, CSRF, validação, tabelas lidas/escritas, auditoria, exportação e código de status.
- Verificar rotas que usam query strings; confirmar se o despacho normaliza caminho e consulta como esperado.
- Comparar a matriz derivada do código com as listas de teste para detectar omissões e caminhos obsoletos.
- Adicionar testes de contrato para cada linha da matriz; não remover entradas sem demonstrar que a rota deixou de existir.
- Executar `python -m compileall -q api scripts tests` e `make test` na CI e registrar os resultados antes de refatorar.

## Critério de conclusão

A baseline só estará completa quando cada rota do código estiver classificada e vinculada a pelo menos um teste de autenticação/autorização apropriado e a testes de contrato para sucesso, validação e falhas relevantes. Este documento é uma primeira extração a partir dos testes atuais, não uma declaração de cobertura total.
