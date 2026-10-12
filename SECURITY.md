# Política de segurança

## Escopo e limitações

Product Manager é uma aplicação local em desenvolvimento. A API não implementa autenticação, autorização, CSRF, limitação de taxa ou implantação TLS e não deve ser exposta a redes públicas. Use apenas dados fictícios durante avaliação.

## Reportar uma vulnerabilidade

Não publique detalhes exploráveis em issues públicas. Até existir um canal privado configurado pelo mantenedor, reporte apenas a existência do problema em uma issue sem dados de exploração e solicite um canal privado. Não envie credenciais ou dados pessoais.

## Boas práticas de desenvolvimento

- Não comite credenciais, dados pessoais nem arquivos de banco com dados reais.
- Credenciais de Google Sheets devem permanecer em um gerenciador de segredos do servidor; nunca as inclua em arquivos versionados, frontend, URLs ou logs. Como a aplicação ainda não implementa autenticação, proteja qualquer implantação compartilhada com um proxy de identidade antes de habilitar a rota de exportação.
- Não comite arquivos `.env` (exceto `.env.example`), bancos SQLite, chaves privadas, certificados, dumps, backups ou exportações. Esses padrões estão ignorados pelo Git; confirme também `git status` antes de cada commit.
- Remova credenciais que tenham sido expostas e rotacione-as. Apagar um arquivo em um commit novo não apaga cópias em commits anteriores, forks ou clones.
- Use consultas parametrizadas para SQL e escape conteúdo renderizado no HTML.
- Mantenha dependências mínimas e aplique atualizações de segurança antes de qualquer implantação.

## Telemetria

O diagnóstico no cliente exige consentimento explícito e um endpoint HTTPS configurado pelo operador. O formato permitido contém apenas tipo de evento, nome e versão do app. Não coloque segredos, conteúdo de requisições ou dados pessoais no endpoint nem em logs. Consulte [Política de privacidade](PRIVACY.md).
