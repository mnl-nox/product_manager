# Casos de teste

## Casos prioritários

| ID | Cenário | Resultado esperado | Prioridade |
|---|---|---|---|
| API-001 | GET /healthz sem sessão | HTTP 200, JSON mínimo de liveness | P0 |
| API-002 | GET /readyz com SQLite saudável | HTTP 200, estado ready | P0 |
| API-003 | SQLite indisponível | HTTP 503, sem detalhes internos | P0 |
| AUTH-001 | Login válido/inválido | Sessão criada ou acesso negado sem revelar se usuário existe | P0 |
| AUTH-002 | Sessão expirada/revogada | API de negócio nega acesso | P0 |
| AUTH-003 | Escrita sem CSRF ou token inválido | Requisição rejeitada, banco inalterado | P0 |
| AUTHZ-001 | Viewer tenta escrever | HTTP 403 e banco inalterado | P0 |
| AUTHZ-002 | Papel financeiro tenta ação não autorizada | HTTP 403 | P0 |
| DATA-001 | SKU duplicado | HTTP 409, sem duplicação | P0 |
| DATA-002 | Quantidade negativa/preço inválido | HTTP 400, sem escrita parcial | P0 |
| DATA-003 | Escritas concorrentes de estoque | Integridade preservada, conflito tratado | P1 |
| DATA-004 | Reinício do processo | Dados persistem no caminho configurado | P0 |
| EXP-001 | CSV/XLSX | Arquivo legível, colunas corretas, proteção contra fórmula injetável | P0 |
| EXP-002 | Exportação sem permissão | Acesso negado, sem vazamento | P0 |
| PWA-001 | Cache autenticado | Respostas de API/dados privados não são cacheados | P0 |
| PWA-002 | Atualização do service worker | Shell novo carregado sem loop de cache | P1 |
| WEB-001 | Viewports 320, 768 e desktop | Sem overflow em fluxos críticos | P1 |
| WEB-002 | Teclado e leitor de tela | Foco e erros acessíveis nos fluxos críticos | P1 |
| OPS-001 | Logs de falha | Sem senha, token, cookie ou dados pessoais desnecessários | P0 |
| PKG-001 | Build DEB | Pacote criado, instalável e com dados persistentes | P0 |
| PKG-002 | Build RPM | Pacote criado; arquivos declarados existem | P0 |
| PKG-003 | Build Windows | Instalador produzido e testado em ambiente limpo | P0 |
| PKG-004 | Workflow multiplataforma | Todos os artefatos esperados presentes | P0 |

## Registro de resultados

| ID | Commit | Evidência | Resultado | Defeito |
|---|---|---|---|---|
| API-001 a API-003 | PENDENTE | PENDENTE | NÃO EXECUTADO | — |
| AUTH/AUTHZ | PENDENTE | PENDENTE | NÃO EXECUTADO | — |
| DATA/EXP | PENDENTE | PENDENTE | NÃO EXECUTADO | — |
| PWA/WEB | PENDENTE | PENDENTE | NÃO EXECUTADO | — |
| PKG-001 a PKG-004 | PENDENTE | PENDENTE | NÃO EXECUTADO | — |

Qualquer caso P0/P1 pendente ou com falha bloqueia o aceite final.