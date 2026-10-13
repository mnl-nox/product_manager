# Segurança e privacidade

Esta página resume os controles documentados no código e nas políticas do repositório. Consulte também `SECURITY.md` e `PRIVACY.md`.

## Controles implementados

- Contas locais com papéis de acesso.
- Hash de senha usando scrypt.
- Token de sessão armazenado no banco como hash.
- Cookies de sessão HttpOnly e SameSite=Strict, com expiração de 12 horas.
- Atributo Secure configurável e usado por padrão quando a aplicação não está vinculada ao loopback.
- Token CSRF obrigatório para requisições de escrita.
- Limitação temporária de tentativas de login.
- Validação no servidor e SQL parametrizado.
- Revogação de sessões ao desativar usuário.
- Bootstrap inicial protegido por token temporário; não há credenciais padrão.
- Telemetria opcional, desativada por padrão e condicionada a consentimento e endpoint HTTPS.

## Papéis

| Papel | Acesso geral |
|---|---|
| `admin` | Administração completa, gerenciamento de usuários, exportação Google Sheets e remoção permanente de produtos |
| `operator` | Operações de catálogo, limites e alertas |
| `finance` | Área financeira e leitura de catálogo |
| `viewer` | Leitura do dashboard, catálogo e alertas |

A autorização é verificada pela API. A interface não deve ser tratada como fronteira de segurança.

## Dados sensíveis

O banco pode conter CPF, e-mail, telefone, dados de catálogo e lançamentos financeiros. Proteja o arquivo SQLite e os backups com permissões adequadas, criptografia de armazenamento quando aplicável e controle de acesso. Faça cópias com o aplicativo encerrado e teste a restauração.

## Requisitos para implantação compartilhada

1. Coloque o serviço atrás de HTTPS/TLS gerenciado.
2. Defina `PRODUCT_MANAGER_COOKIE_SECURE=1`.
3. Restrinja portas e acesso de rede; não exponha o servidor desktop.
4. Use um gerenciador de segredos para tokens e credenciais.
5. Mantenha o banco e backups fora de áreas públicas e versionamento.
6. Planeje atualização, rollback, retenção, backup e resposta a incidentes.
7. Monitore sem registrar senhas, cookies, tokens, CPF ou conteúdo de formulários.
8. Antes de atualização de esquema, faça backup e valide restauração.

## Google Sheets

Ao habilitar a integração, dados exportados são enviados para a infraestrutura Google associada à conta e à planilha configuradas. Use escopos mínimos, acesso restrito, token de curta duração e rotação/renovação fora do aplicativo. Não inclua o token no frontend, URLs, logs ou Git.

## Telemetria

A opção de diagnóstico é desativada inicialmente. O envio requer consentimento do usuário e `PRODUCT_MANAGER_TELEMETRY_URL` configurado pelo administrador com endpoint HTTPS. Segundo a política do projeto, os eventos incluem somente identificador técnico permitido, nome e versão do aplicativo; não incluem campos de formulário, banco de dados, stack trace, URL, e-mail ou identificador persistente. A infraestrutura do destino ainda pode registrar o IP de conexão.

## Limitações de segurança conhecidas

- Não há isolamento entre organizações: todas as contas acessam o mesmo workspace conforme seus papéis.
- Não há identidade corporativa OIDC/SAML.
- Não há recuperação automatizada de senha.
- O servidor Python não fornece TLS por conta própria.
- Não há fluxo avançado de resposta a incidentes ou recuperação de desastre embutido.
- A trilha de auditoria é básica, sem histórico completo antes/depois para todas as alterações.

Não use a instalação como serviço corporativo exposto à internet sem avaliar esses limites e completar os controles operacionais necessários.

## Reportar vulnerabilidades

Siga as instruções e os canais indicados em [SECURITY.md](../SECURITY.md). Não publique detalhes exploráveis ou dados reais em issues públicas.