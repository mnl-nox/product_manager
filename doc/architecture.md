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
SQLite ─ contas, catálogo, limites/alertas e financeiro operacional
```

## Componentes

- `ui/`: login, dashboard, catálogo, usuários, financeiro, alertas, registro de riscos/bugs e instalação PWA.
- `api/`: servidor HTTP, sessão, controle de acesso, validação, auditoria, integrações e exportações.
- `db/schema.sql`: esquema inicial; `ensure_database()` aplica atualizações compatíveis ao banco existente.
- `assets/icons/`: ícones do aplicativo e selo vetorial próprio Open Source · MIT.
- `desktop.py`: launcher que mantém o servidor local e abre o navegador. Na primeira execução, cria um segredo efêmero e conduz o bootstrap do administrador sem senha padrão.
- `packaging/`: instalador Windows, pacotes Linux e ZIP de implantação do PWA Android.
- `src/` e `include/`: núcleo C23 legado, ainda separado da aplicação web.

## Acesso e sessão

As rotas de negócio exigem uma conta ativa. A senha é derivada com scrypt. O servidor persiste somente o hash do token de sessão; o navegador recebe cookie HttpOnly/SameSite com prazo de 12 horas. Escritas verificam o token CSRF e o papel do usuário. Administradores gerenciam contas; papéis de operação, financeiro e leitura limitam as operações autorizadas também na API.

## Persistência e atualização

O desktop usa diretório de dados do usuário; `PRODUCT_MANAGER_DB` permite selecionar outro caminho. O modo fonte usa `db/product_manager.db`. O workspace começa vazio; `PRODUCT_MANAGER_DEMO_DATA=1` habilita registros de avaliação. O banco contém dados pessoais e financeiros e deve entrar na política de backup e controle de acesso da instalação.

Atualizações de esquema são idempotentes para os campos de autoria e estado de produto; a migração financeira converte valores decimais anteriores em centavos inteiros. Backups prévios são recomendados antes de atualizar a instalação.

## Limites

As contas compartilham um workspace. Não há isolamento entre organizações, identidade federada, TLS embutido, recuperação de senha, movimentações imutáveis de estoque, notificações externas ou contabilidade fiscal. O PWA exige serviço HTTPS/proxy e operação de infraestrutura pela organização. O selo Open Source · MIT usa arte própria e identifica a licença do repositório; não representa certificação de terceiros.
