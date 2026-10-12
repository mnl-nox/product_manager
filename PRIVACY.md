# Política de privacidade

**Última atualização: 12 de outubro de 2026**

Product Manager pode ser usado localmente ou implantado por uma organização. Esta política descreve o comportamento do software fornecido neste repositório. A organização que o instala define seus próprios tratamentos e deve informar seus usuários.

## Dados operacionais e financeiros

Clientes, produtos, notas, limites de estoque, confirmações de alertas, lançamentos financeiros e registros internos de riscos/bugs são armazenados no banco SQLite da instalação, no caminho indicado no [guia de instalação e uso](docs/installation-usage.md). Os lançamentos financeiros são registros operacionais e não constituem escrituração contábil. O app não envia esses dados aos mantenedores.

Downloads CSV e Excel são gerados localmente. Se um administrador configurar Google Sheets e acionar a exportação, o app envia indicadores agregados e campos de catálogo à planilha escolhida; dados pessoais de clientes não fazem parte dessa exportação. O Google processa os dados conforme a conta e as configurações da organização.

## Contas, autenticação e auditoria

O app armazena nomes de usuário, hashes de senha derivados com scrypt, papéis, estado da conta, datas de criação e registros de auditoria de ações relevantes. Senhas em texto puro não são armazenadas. Para manter sessões, o banco armazena o hash do token de sessão, um token CSRF e o prazo de expiração. O navegador recebe um cookie de sessão HttpOnly e SameSite; em implantações HTTPS, configure o cookie Secure.

Tentativas de login são limitadas por uma chave derivada do nome de usuário e do endereço de rede; o endereço bruto não é gravado nessa tabela. A instalação pode manter metadados de conexão em logs do sistema ou do proxy, conforme sua configuração. Administradores controlam contas, papéis, acesso e retenção do banco.

## Diagnósticos opcionais

O diagnóstico de erros no navegador está desativado por padrão e só é enviado após consentimento explícito. A preferência fica no armazenamento local do navegador e pode ser revogada pelo usuário.

Quando habilitado, o cliente informa apenas um evento permitido (`javascript_error` ou `unhandled_rejection`). O servidor acrescenta nome e versão do aplicativo e encaminha o conjunto para `PRODUCT_MANAGER_TELEMETRY_URL`, se o administrador configurou um endereço HTTPS. Não são enviados texto de exceção, stack trace, URL, formulário, banco de dados ou identificador persistente. O endpoint é operado pelo administrador e pode registrar metadados de rede e horário. Sem endpoint configurado, os eventos não são transmitidos nem persistidos pelo Product Manager.

## Cookies e armazenamento no navegador

O aplicativo não usa cookies de publicidade nem analytics de terceiros. O cookie `pm_session` mantém a autenticação e expira após 12 horas; sair invalida a sessão no servidor. A preferência de diagnóstico e recursos estáticos do PWA podem ser guardados localmente. Respostas da API não são guardadas no cache do service worker.

## Retenção, segurança e direitos

Os registros locais permanecem até que o usuário ou administrador os remova. Backups e exportações ficam sob controle de quem os cria. Para exercer direitos sobre dados de negócio, contate a organização que opera a instalação; os mantenedores do código não recebem esses dados.

## Alterações e contato

Mudanças nesta política serão publicadas no repositório com atualização da data acima. Para dúvidas sobre a instalação, abra uma issue sem incluir dados pessoais. Vulnerabilidades devem seguir a [Política de segurança](SECURITY.md).
