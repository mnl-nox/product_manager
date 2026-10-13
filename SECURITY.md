# Política de segurança

## Escopo e implantação

O Product Manager agora oferece contas locais, papéis de acesso, sessões com cookie HttpOnly e SameSite, token CSRF e limitação de tentativas de login. As permissões são verificadas na API. A aplicação ainda usa um único espaço de trabalho SQLite compartilhado: não há isolamento entre organizações, SSO, recuperação de senha nem implantação TLS embutida.

Para uso compartilhado, publique atrás de um proxy HTTPS confiável e defina `PRODUCT_MANAGER_COOKIE_SECURE=1`. Não exponha diretamente o servidor de desenvolvimento à internet. Defina um token aleatório temporário em `PRODUCT_MANAGER_SETUP_TOKEN` para criar o primeiro administrador e remova-o da configuração após o provisionamento. Nunca use senha padrão.

## Reportar uma vulnerabilidade

Não publique detalhes exploráveis em issues públicas. Até existir um canal privado configurado pelo mantenedor, reporte apenas a existência do problema em uma issue sem dados de exploração e solicite um canal privado. Não envie credenciais ou dados pessoais.

## Boas práticas de desenvolvimento

- Não comite credenciais, dados pessoais nem arquivos de banco com dados reais.
- Credenciais de Google Sheets devem permanecer em um gerenciador de segredos do servidor; nunca as inclua em arquivos versionados, frontend, URLs ou logs. O envio direto para Sheets é restrito a administradores.
- Não comite arquivos `.env` (exceto `.env.example`), bancos SQLite, chaves privadas, certificados, dumps, backups ou exportações. Confirme também `git status` antes de cada commit.
- Remova credenciais expostas e rotacione-as. Apagar um arquivo em um commit novo não apaga cópias em commits anteriores, forks ou clones.
- Use consultas parametrizadas para SQL e escape conteúdo renderizado no HTML.
- Preserve a integridade do livro-razão de estoque: movimentos são append-only, e produtos com histórico não devem ser removidos definitivamente. Proteja o arquivo SQLite e seus backups.
- Mantenha dependências mínimas e aplique atualizações de segurança antes de qualquer implantação.

## Telemetria

O diagnóstico no cliente exige consentimento explícito e um endpoint HTTPS configurado pelo operador. O formato permitido contém apenas tipo de evento, nome e versão do app. Não coloque segredos, conteúdo de requisições ou dados pessoais no endpoint nem em logs. Consulte [Política de privacidade](PRIVACY.md).
