# Validação de segurança e recuperação

**Data:** 13/10/2026
**Escopo:** autorização da API, sessões e cookies, configuração de segredos, migração SQLite, backup/restauração e imagem Podman.

## Resultado

Os controles revisados passaram nos testes automatizados. Foi acrescentado um fluxo manual de backup e restauração verificável para SQLite e ele foi executado dentro da imagem Podman reconstruída. A configuração versionada não contém valores ativos de segredos: existe apenas `.env.example` com campos vazios; não havia arquivo `.env` local no ambiente examinado.

## Autorização e CSRF

- As rotas de negócio `/api/*` passam pelo gate de sessão em `do_GET` e `do_POST`. As exceções deliberadas incluem login, status de provisionamento e endpoints de prontidão/vida; setup exige o token temporário de bootstrap. Arquivos estáticos e páginas de login são públicos.
- Testes exercitam todas as rotas GET e POST declaradas nas matrizes de `tests/test_security.py` sem sessão; todas retornam 401. Também cobrem todas as rotas POST declaradas sem token CSRF; retornam 403.
- Foram exercitados papéis e grupos restritos: viewer e finance sem escrita de catálogo, operator sem escrita financeira, finance sem recebimento de compra, HR e exportação Sheets limitados a admin, e administração de usuários limitada a admin.
- CSRF exige token correto e rejeita origem externa mesmo com token válido.
- A matriz de autorização chama diretamente o dispatcher HTTP com sessão simulada. Isso prova o gate e os grupos de autorização do backend, mas não substitui uma varredura dinâmica por proxy/servidor em todas as URLs.

## Sessões e cookies

- O token de sessão tem 256 bits aleatórios, é guardado como SHA-256 no banco e expira em 12 horas.
- Sessões expiradas e de usuários desativados são rejeitadas; logout apaga a sessão e limpa o cookie.
- Cookie validado com `HttpOnly`, `SameSite=Strict`, `Path=/`, expiração e atributo `Secure` quando configurado. `render.yaml` define Secure; Compose local HTTP deixa Secure desligado para desenvolvimento.

## Segredos de configuração

- `.env.example` possui placeholders vazios. `.env` não estava presente e é ignorado pelo Git.
- Render gera o token inicial de configuração e usa cookies Secure. O token de bootstrap deve ser removido após criar o primeiro admin; as credenciais Google Sheets devem ficar no ambiente/gerenciador de segredos, nunca no frontend.
- A inspeção foi limitada à configuração e aos arquivos presentes no checkout. Não é uma auditoria do histórico Git, das variáveis de produção do provedor ou dos segredos armazenados externamente.

## Migrações e recuperação

- Migração legada: teste cria esquema antigo com `finance_entries.amount` e produtos sem colunas atuais, executa migração duas vezes e verifica conversão monetária, colunas novas, saldo de abertura único e `PRAGMA integrity_check=ok`.
- `ensure_database()` agora fecha explicitamente a conexão SQLite de migração.
- `scripts/database_recovery.py` usa a API de backup online do SQLite, valida `integrity_check` e tabelas mínimas, restringe o arquivo criado a modo 0600 em POSIX, não sobrescreve backup existente e só substitui banco existente com `--replace` explícito.
- Testes cobrem backup/restauração com preservação dos dados, rejeição de arquivo corrompido e substituição explícita.
- A imagem foi construída sem rede como `product-manager:security-qa`; o container ficou `healthy`, `/readyz` respondeu HTTP 200 e backup + restauração em outro arquivo dentro do container passaram com `integrity_check=ok`. O container de validação foi removido.

## Evidências e alterações

- `python3 -m unittest discover -s tests -q`: **66 testes passaram**.
- `podman build --network=none --format docker -t product-manager:security-qa .`: passou.
- `podman exec ... database_recovery.py backup ...` e `restore ...`: passaram; integridade SQLite `ok`.
- O Dockerfile inclui o utilitário de recuperação. `.dockerignore` permite apenas `scripts/database_recovery.py` do diretório de scripts na imagem.
- Procedimento operacional e limites documentados em [docs/deployment.md](../docs/deployment.md).

## Limites pendentes

O backup é manual: ainda não há agenda, rotação, armazenamento fora do host nem criptografia do arquivo. A recuperação foi testada em banco temporário do container, não no disco persistente da implantação pública. Antes de uso com dados reais, configure cópias protegidas e retenção, e faça um ensaio de restauração no ambiente de implantação. Também não foi feita análise de histórico Git, teste de penetração externo ou auditoria independente de dependências.
