# Plano e relatório de QA — Product Manager

**Data de referência:** 13/10/2026  
**Versão observada antes desta rodada:** 1.7.9  
**Repositório:** https://github.com/mnl-nox/product_manager  
**Escopo:** API Python, autenticação, autorização, compras, vendas, estoque, financeiro, RH, SQLite, PWA, documentação e CI.

## 1. Objetivo e critério de conclusão

Este documento registra uma auditoria de Quality Assurance orientada a evidências. Uma funcionalidade só é considerada aprovada quando existe um teste reproduzível ou uma evidência operacional identificada. Revisão de código, compilação e publicação de uma versão não equivalem a homologação de produção.

Estados usados neste relatório:

- **APROVADO:** teste ou verificação executada com resultado satisfatório e evidência identificável.
- **REPROVADO:** defeito reproduzido por teste ou execução.
- **PARCIAL:** há teste ou revisão, mas a cobertura não prova todo o comportamento.
- **NÃO VERIFICADO:** depende de ambiente, credencial, dispositivo, serviço externo ou procedimento ainda não executado.
- **NÃO SUPORTADO:** capacidade não implementada ou explicitamente fora do escopo atual.

## 2. Resumo executivo

O repositório contém uma aplicação funcional com API Python, interface Web/PWA, SQLite, autenticação por sessão, papéis de acesso, catálogo, compras, vendas, estoque, financeiro operacional, RH, relatórios e empacotamento multiplataforma.

A última rodada funcional encontrou e corrigiu defeitos concretos nas rotas de recebimento de compras: padrões regex com barras invertidas duplicadas faziam IDs numéricos não corresponderem, e uma consulta SQL fornecia dois parâmetros a um único placeholder. Os testes de integração reproduziram os problemas antes da correção. Também foram adicionados testes de venda realizada/planejada e testes unitários para a matriz de permissões e CSRF.

**Conclusão provisória:** base funcional com regressões importantes corrigidas e cobertura automatizada ampliada; ainda **não certificada para uso crítico em produção**. A suíte exercita handlers e banco de teste, mas não substitui E2E no navegador, ensaio de restauração, teste de carga, revisão independente de segurança nem homologação nativa de todas as plataformas.

## 3. Matriz de QA

| Área | O que deve ser provado | Estado | Evidência / lacuna |
|---|---|---|---|
| Compilação Python | Módulos compilam sem erro | APROVADO na CI da PR de correção | Job Python da PR #20 |
| Núcleo C23 | Build com flags do projeto | APROVADO na CI da PR de correção | Job C23 da PR #20 |
| Conventional Commits | Mensagens obedecem ao padrão | APROVADO na CI da PR de correção | Workflow Conventional Commits da PR #20 |
| Catálogo | Cadastro, validação, unicidade e saldo inicial | PARCIAL | Testes de API e livro-razão; falta E2E de navegador |
| Livro-razão de estoque | Imutabilidade, saldo inicial, movimentos e histórico | PARCIAL | tests/test_inventory_ledger.py; falta teste de concorrência e reconciliação completa |
| Recebimento de compras | Recebimento parcial/final, limite de quantidade, autorização e transação | APROVADO para os cenários automatizados | tests/test_purchasing.py; cobertura não representa todos os cenários reais |
| Vendas | Venda paga gera baixa, movimento e receita coerentes; planejada não baixa estoque | APROVADO para os cenários automatizados | tests/test_reports.py |
| Permissões | Admin, operação, financeiro, leitura e papel desconhecido | TESTE ADICIONADO; CI PENDENTE | tests/test_security.py; ainda requer auditoria de cada endpoint |
| CSRF | Token ausente/inválido e origem estrangeira são rejeitados | TESTE ADICIONADO; CI PENDENTE | tests/test_security.py; falta E2E HTTP com cookies reais |
| RH | Constraints de esquema, matrícula, datas e jornada | PARCIAL | tests/test_hr.py; falta cobertura dos endpoints e segregação por papel |
| Login e sessões | Senha, expiração, revogação, bloqueio e recuperação de sessão | PARCIAL | Revisão de código e testes existentes limitados; ampliar testes de integração |
| Migrações | Banco novo e banco legado são atualizados sem perda | PARCIAL | Migrações em ensure_database() e testes específicos; falta matriz representativa de versões antigas e backup pré-migração |
| Exportações | CSV/XLSX corretos e sem fórmula maliciosa | NÃO VERIFICADO de ponta a ponta | Cobertura E2E e validação de conteúdo exportado ainda necessárias |
| PWA | Manifest, ícones e API fora do cache | APROVADO para verificações estáticas | tests/test_pwa.py; instalação real em dispositivos não comprovada nesta rodada |
| Windows/Linux/Android | Instalação, inicialização, atualização e persistência nativa | NÃO VERIFICADO nesta rodada | Exige execução dos workflows de artefatos e smoke tests por plataforma |
| Backup/restauração | Backup íntegro, recuperação e RPO/RTO demonstrados | NÃO VERIFICADO | Nenhum ensaio de restauração de produção foi demonstrado |
| Desempenho/concorrência | Latência, carga, bloqueios SQLite e submissões duplicadas | NÃO VERIFICADO | Não há baseline de carga nem teste de concorrência registrado |
| Acessibilidade | Teclado, leitor de tela, contraste e WCAG 2.2 AA | NÃO VERIFICADO | Requer avaliação automatizada e manual |
| Segurança independente | Revisão de ameaças, pentest e dependências | NÃO VERIFICADO | A revisão de repositório não é certificação nem pentest |
| Multiempresa | Isolamento de dados entre organizações | NÃO SUPORTADO | O banco atual representa um espaço de trabalho compartilhado; não usar como SaaS multi-tenant |

## 4. Testes automatizados adicionados ou reforçados

### 4.1 Compras e estoque

A suíte tests/test_purchasing.py cobre:

- Recebimento parcial e recebimento final.
- Quantidade recebida acumulada, saldo do produto e movimentos PURCHASE_IN.
- Atualização do estado do pedido e da solicitação.
- Rejeição de recebimento acima da quantidade pedida sem alterar saldo, item ou livro-razão.
- Bloqueio do recebimento para o papel financeiro.
- Constraints básicas do modelo de compras.

Durante a execução inicial, três cenários falharam com HTTP 404 porque as expressões regulares das rotas não reconheciam IDs numéricos. Após corrigir os padrões, a suíte expôs um segundo defeito: a consulta do item usava um placeholder SQL e dois parâmetros. A consulta foi corrigida para vincular item_id e order_id, verificando também que o item pertence ao pedido recebido.

### 4.2 Vendas e financeiro

A suíte tests/test_reports.py verifica:

- Venda realizada: registro da venda, total em centavos, baixa do estoque, movimento SALE_OUT e lançamento de receita com o mesmo valor.
- Venda planejada: não reduz estoque nem cria movimento de saída e mantém o lançamento como previsto.
- Validação de período dos relatórios e comportamento da margem sem receita.

Os testes não provam ainda cancelamentos, estornos, devoluções, submissões duplicadas nem concorrência entre vendas do mesmo produto.

### 4.3 Segurança

A suíte tests/test_security.py verifica:

- Administrador autorizado nas permissões avaliadas.
- Operação com permissão de catálogo e alertas, sem permissão financeira.
- Financeiro limitado às permissões financeiras e leitura.
- Leitor restrito à leitura.
- Papel desconhecido negado.
- Token CSRF ausente ou inválido rejeitado.
- Origem estrangeira rejeitada mesmo com token CSRF válido.
- Origem correspondente ao host e token correto aceitos.

Esses testes exercitam as funções de controle diretamente. Eles não substituem testes HTTP com cookie real, sessão persistida, expiração e revogação.

### 4.4 Higiene dos testes

Foi removida uma duplicação de setUpClass/tearDownClass em tests/test_hr.py. A segunda definição substituía silenciosamente a primeira em Python; a remoção deixa explícita uma única configuração de banco temporário para a classe.

## 5. Regressões e incidentes observados

| ID | Defeito | Impacto | Correção | Estado |
|---|---|---|---|---|
| QA-001 | Regex de rotas de compra/RH com barras invertidas duplicadas em string raw | IDs numéricos não correspondiam; recebimento retornava 404 | Padrões corrigidos para aceitar dígitos | Corrigido; testes da PR passaram |
| QA-002 | Consulta de item de recebimento com um placeholder e dois parâmetros | Exceção SQL durante o recebimento | Consulta passou a filtrar por id e order_id com dois placeholders | Corrigido; testes da PR passaram |
| QA-003 | Cobertura insuficiente de permissões/CSRF em testes dedicados | Risco de regressões silenciosas nos controles | Criada tests/test_security.py | Testes adicionados; execução da CI pendente |
| QA-004 | setUpClass duplicado em teste de RH | Setup anterior sobrescrito e fixture confusa | Duplicação removida | Alteração aplicada; execução da CI pendente |

Não há, neste relatório, declaração de que todas as vulnerabilidades ou defeitos possíveis foram encontrados. A tabela lista apenas problemas identificados nesta rodada.

## 6. Procedimento reproduzível

Execute em um clone limpo, em ambiente de desenvolvimento ou CI. Não execute testes destrutivos contra um banco com dados reais.

    python3 -m compileall -q api scripts tests
    make test
    make -B

Quando as ferramentas e dependências estiverem disponíveis, valide também os artefatos:

    make package-linux
    make package-pwa

Para plataformas que exigem runners específicos, execute os workflows de CI/pacotes no GitHub Actions. Registre o link do run, SHA do commit, artefato, sistema operacional e resultado. Para validação manual, use banco temporário e dados sintéticos.

## 7. Critérios de aceite para produção

A aplicação não deve ser classificada como pronta para operação crítica até que os itens abaixo tenham evidência registrada:

1. CI verde no commit exato que será publicado.
2. Testes E2E do login, cadastro, compras, recebimento, venda, financeiro, alertas e exportações.
3. Matriz de autorização exercitada em cada endpoint, incluindo acesso direto à API sem passar pela interface.
4. Teste de concorrência para duas operações sobre o mesmo saldo, com ausência de saldo negativo, movimento duplicado ou receita duplicada.
5. Migração ensaiada sobre cópia de banco legado, com backup anterior e comparação de contagens/valores.
6. Backup e restauração executados em ambiente isolado; documentar RPO, RTO, retenção e responsável.
7. Artefatos Windows/Linux/PWA construídos; smoke test de instalação e persistência. Android requer instalação em dispositivo ou emulador se o APK for distribuído.
8. Revisão de segurança operacional: HTTPS, cookie Secure, segredo de bootstrap removido, permissões de arquivo, gestão de segredos e logs sem dados sensíveis.
9. Política de privacidade, retenção, exclusão e acesso a dados de RH validada para o ambiente real.
10. Teste de acessibilidade e desempenho com resultados mensuráveis.

## 8. Riscos conhecidos e limites de arquitetura

- **Banco e servidor:** SQLite e o servidor HTTP da biblioteca padrão atendem a instalações pequenas, mas exigem testes de bloqueio, concorrência, backup e restauração. Não presumir escalabilidade horizontal.
- **Multi-tenancy:** não existe isolamento por organização. Um único banco representa um espaço de trabalho compartilhado.
- **Auditoria financeira:** vendas e compras cobrem fluxos básicos; estornos, devoluções, conciliação, fechamento contábil e trilha completa de alterações financeiras ainda precisam de validação e escopo formal.
- **Livro-razão:** os movimentos registrados são append-only, mas isso não implementa por si só inventário físico, transferências entre depósitos, reservas formais, devoluções ou reconciliação completa.
- **Interface:** testes de handler não validam foco, acessibilidade, responsividade, erros apresentados ao usuário nem comportamento real de service worker.
- **Release:** VERSION, tags e changelog precisam permanecer sincronizados. O estado de uma release deve ser verificado no run correspondente; a publicação automática de uma tag não comprova homologação funcional.

## 9. Q&A operacional

**O sistema está pronto para uso crítico em produção?**  
Ainda não. A base funcional e os testes automatizados não substituem os ensaios de backup/restauração, concorrência, E2E e segurança independente listados acima.

**Os testes de compras e vendas verificam o banco?**  
Sim, os cenários automatizados verificam os registros relevantes em banco temporário: quantidades, estados, movimentos e valores financeiros. A cobertura continua limitada aos cenários descritos.

**A interface pode impedir sozinha uma operação não autorizada?**  
Não deve ser considerada uma barreira de segurança. A autorização precisa ser aplicada no servidor e exercitada diretamente na API.

**Podemos usar o mesmo banco para várias empresas?**  
Não com isolamento seguro entre organizações. Multi-tenancy não é uma capacidade suportada pelo desenho atual.

**O que fazer antes de migrar um banco real?**  
Criar backup verificável, ensaiar a migração em cópia, comparar contagens e valores antes/depois, validar o fluxo de negócio e só então planejar a janela de mudança.

**Um build aprovado significa que a plataforma foi homologada?**  
Não. Build prova que o artefato foi produzido; homologação exige instalação, inicialização, persistência, atualização e testes de operação na plataforma-alvo.

## 10. Atualização deste relatório

**Estado desta rodada documental:** a correção funcional anterior foi aprovada com 40 testes Python, C23 e Conventional Commits na CI da PR #20. A nova cobertura de segurança contém oito testes adicionais e a limpeza da fixture de RH; estes ainda não foram executados em CI. Atualize esta página após cada rodada com data, SHA testado, link da CI, quantidade de testes, artefatos testados, defeitos abertos/fechados e ressalvas. Não altere estados para APROVADO sem evidência verificável.
