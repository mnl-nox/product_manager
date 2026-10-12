# Política de privacidade

**Última atualização: 12 de outubro de 2026**

Product Manager pode ser usado localmente ou implantado por uma organização. Esta política descreve o comportamento do software fornecido neste repositório. A organização que o instala pode definir outros tratamentos e deve documentá-los aos seus usuários.

## Dados operacionais

Clientes, produtos, notas e demais registros inseridos no app são armazenados no banco SQLite local, no caminho específico da plataforma descrito no [guia de instalação e uso](docs/installation-usage.md). No modo desktop, o servidor escuta em loopback. A aplicação não envia esses registros para os mantenedores.

Downloads CSV e Excel são gerados localmente. Se o administrador configurar o Google Sheets e um usuário acionar **Exportar para Google Sheets**, o app transmite os indicadores agregados e os campos de catálogo descritos na documentação técnica para a planilha selecionada. Registros pessoais de clientes não fazem parte dessa exportação. O Google processa os dados conforme a conta, planilha e configuração da organização; o administrador deve controlar permissões e informar os usuários.

## Diagnósticos opcionais

O diagnóstico de erros no navegador está desativado por padrão e só é enviado após consentimento explícito no controle da interface. A preferência é guardada no armazenamento local do navegador. O usuário pode revogá-la a qualquer momento desmarcando o controle ou apagando os dados do site.

Quando habilitado, o cliente informa apenas um dos eventos técnicos permitidos (`javascript_error` ou `unhandled_rejection`). O servidor acrescenta o nome e a versão do aplicativo e encaminha esse conjunto a `PRODUCT_MANAGER_TELEMETRY_URL`, se o administrador tiver configurado um endereço HTTPS. Nenhum endpoint é fornecido pelo projeto por padrão. O sistema não envia texto de exceção, stack trace, URL, conteúdo dos formulários, banco de dados, identificador de usuário ou identificador persistente.

O endpoint de destino é operado pelo administrador da implantação e pode registrar metadados de rede, como endereço IP e horário de conexão. O administrador é responsável por informar os usuários, definir a base legal, controlar acesso e retenção dos registros e atender solicitações aplicáveis. Se o endpoint não estiver configurado, os eventos não são transmitidos nem persistidos pelo Product Manager.

## Cookies e armazenamento no navegador

O aplicativo não usa cookies de publicidade nem analytics de terceiros. A preferência de diagnóstico e os recursos estáticos do PWA podem ser guardados localmente no navegador. Dados de API não são armazenados no cache do service worker.

## Retenção, segurança e direitos

Os registros locais permanecem até que o usuário ou administrador os apague. Backups e exportações ficam sob controle de quem os cria. Para exercer direitos sobre os dados de negócio, contate a organização que opera a instalação; os mantenedores do código não recebem esses dados.

## Alterações e contato

Mudanças nesta política serão publicadas no repositório com atualização da data acima. Para dúvidas sobre a instalação, abra uma issue sem incluir dados pessoais. Vulnerabilidades devem seguir a [Política de segurança](SECURITY.md).
