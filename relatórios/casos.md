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
| WEB-003 | Seção de avaliações sem depoimentos cadastrados | Nenhuma nota ou testemunho fictício apresentado; CTA abre canal de feedback | P1 |
| WEB-004 | Links de contato | E-mail abre `mailto:`; Instagram aponta ao perfil correto e abre em nova aba com `rel` seguro | P1 |
| PUR-001 | Solicitação com itens válidos/inválidos | Sem escrita parcial; quantidade e produto validados | P0 |
| PUR-002 | Aprovação e alçada financeira | Valor acima do limite exige administrador | P0 |
| PUR-003 | Recebimento duplicado/parcial | Quantidade recebida não ultrapassa pedido; estoque só atualizado após validação integral | P0 |
| HR-001 | Acesso a dados de colaboradores | Perfil não administrador recebe 403 | P0 |
| HR-002 | Período de ausência inválido | API rejeita data final anterior à inicial | P0 |
| HR-003 | Jornada duplicada | Um registro por colaborador/data | P1 |
| REP-001 | Período de relatório inválido | HTTP 400 para intervalo invertido | P0 |
| REP-002 | Venda realizada | Estoque e receita atualizados na mesma transação | P0 |
| REP-003 | Venda prevista | Não reduz estoque nem conta como venda realizada | P0 |
| REP-004 | Sem receita | Margem indefinida, sem divisão por zero | P1 |
| REP-005 | Dimensões organizacionais | Receita/despesas agregadas por departamento e unidade, inclusive registros sem classificação | P1 |
| HR-004 | Exportação de jornada para folha | CSV limitado ao período solicitado, sem cálculo salarial e sem fórmulas executáveis | P1 |
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
| WEB-003/WEB-004 | 6a5cc528 | Revisão de conteúdo/HTML; teste manual de navegador pendente | IMPLEMENTAÇÃO REGISTRADA; NÃO VALIDADO EM NAVEGADOR | — |
| PUR/HR/REP | branches de funcionalidade | Testes adicionados; CI e execução local pendentes | NÃO EXECUTADO | — |
| PKG-001 a PKG-004 | PENDENTE | PENDENTE | NÃO EXECUTADO | — |

Qualquer caso P0/P1 pendente ou com falha bloqueia o aceite final.