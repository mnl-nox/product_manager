# Arquitetura do Product Manager

## Visão geral

O Product Manager é uma aplicação web responsiva com empacotamento desktop para Windows/Linux e instalação PWA para Android. O desktop abre um servidor local no loopback; a instalação PWA usa um servidor HTTPS administrado pela organização. A API Python usa bibliotecas padrão e persiste o workspace em SQLite.

```text
UI web / PWA / desktop
       │ mesma origem: HTML, CSS, JS e API JSON
       ▼
API Python ─ autenticação, papéis, CSRF, validação e auditoria
       │ SQL parametrizado
       ▼
SQLite ─ contas, catálogo, estoque, compras, vendas, RH, financeiro e relatórios
```

## Componentes

- `ui/`: login, dashboard, catálogo, usuários, compras, RH, financeiro, alertas, relatórios, riscos/bugs e instalação PWA.
- `api/`: servidor HTTP, sessão, controle de acesso, validação, auditoria, integrações e exportações.
- `db/schema.sql`: esquema inicial; `ensure_database()` aplica atualizações compatíveis ao banco existente, inclusive saldo de abertura para produtos legados com quantidade positiva.
- `assets/icons/`: ícones do aplicativo e selo vetorial próprio Open Source · MIT.
- `desktop.py`: launcher que mantém o servidor local e abre o navegador. Na primeira execução, cria um segredo efêmero e conduz o bootstrap do administrador sem senha padrão.
- `packaging/`: instalador Windows, pacotes Linux e ZIP de implantação do PWA Android.
- `src/` e `include/`: núcleo C23 legado, ainda separado da aplicação web.

## Acesso e sessão

As rotas de negócio exigem uma conta ativa. A senha é derivada com scrypt. O servidor persiste somente o hash do token de sessão; o navegador recebe cookie HttpOnly/SameSite com prazo de 12 horas. Escritas verificam o token CSRF e o papel do usuário. Administradores gerenciam contas; papéis de operação, financeiro e leitura limitam as operações autorizadas também na API.

## Persistência e atualização

O desktop usa diretório de dados do usuário; `PRODUCT_MANAGER_DB` permite selecionar outro caminho. O modo fonte usa `db/product_manager.db`. O workspace começa vazio; `PRODUCT_MANAGER_DEMO_DATA=1` habilita registros de avaliação. O banco contém dados pessoais e financeiros e deve entrar na política de backup e controle de acesso da instalação.

Atualizações de esquema são aplicadas por `ensure_database()` e incluem compatibilidade para campos antigos, conversão do financeiro para centavos inteiros e criação do livro-razão `stock_movements`. Na primeira inicialização com essa versão, produtos legados com quantidade positiva e sem movimentos recebem um `OPENING_BALANCE` correspondente ao saldo atual; isso estabelece uma referência inicial, não reconstrói eventos anteriores. O histórico não pode ser editado/excluído por triggers SQLite. Faça backup e teste a restauração antes de atualizar.

## Limites

As contas compartilham um workspace. Não há isolamento entre organizações, identidade federada, TLS embutido, recuperação de senha, notificações externas ou contabilidade fiscal. O livro-razão de estoque existe, mas ainda não cobre integralmente devoluções, estornos, transferências entre depósitos, reservas formais e reconciliação física. O PWA exige serviço HTTPS/proxy e operação de infraestrutura pela organização. O selo Open Source · MIT usa arte própria e identifica a licença do repositório; não representa certificação de terceiros.
