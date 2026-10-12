# Changelog

Mudanças notáveis do projeto são registradas neste arquivo.

## [v1.0.0] - 2026-10-12

### Implementado

- Primeira versão completa da aplicação web multiplataforma para desktop Windows/Linux e PWA Android.
- Provisionamento local seguro do primeiro administrador ao abrir o aplicativo desktop.
- Ciclo de vida do produto: criar, editar, desativar, reativar e remover com permissões administrativas.
- Remoção de lançamentos financeiros com confirmação e auditoria.
- Registro e acompanhamento interno de bugs e riscos com prioridade e estados.
- Selo visual próprio Open Source · MIT na interface e no README.
- Indicadores, categorias, exportações e alertas passam a desconsiderar produtos desativados.
- Busca e filtro de catálogo e selo Open Source próprio distribuído nos pacotes.
- Atualizações da documentação de instalação, segurança, operação e limites multiempresa.

### Limites conhecidos

- O app trabalha em um espaço SQLite compartilhado, sem isolamento multiempresa ou login corporativo.
- A área financeira é operacional; alertas são apresentados no app e não enviam e-mail/push.
- O PWA Android requer implantação HTTPS administrada pela organização.

## [v0.7.0] - 2026-10-12

### Implementado

- Autenticação local com bootstrap do primeiro administrador, sessões revogáveis e proteção CSRF.
- Papéis de administrador, operação, financeiro e leitura, aplicados nas rotas da API.
- Gerenciamento de usuários com desativação e revogação das sessões.
- Área financeira para receitas e despesas previstas ou realizadas, com saldo operacional.
- Central de alertas de estoque com limites globais e por produto e reconhecimento de alertas.
- Registro de auditoria para autenticação e operações administrativas, financeiras e de alertas.
- Atualização das políticas, requisitos, guia de instalação e documentação de operação.

### Limites

- Contas compartilham um único espaço de trabalho; não há SSO, recuperação de senha, isolamento multiempresa ou alertas externos.
- Financeiro é operacional, não contábil/fiscal.

## [v0.6.0] - 2026-10-12

### Implementado

- API para download do dashboard em Excel `.xlsx`, gerado sem dependências extras.
- Integração administrativa opcional para enviar os dados do dashboard à planilha Google configurada.
- Ações de exportação CSV, Excel e Google Sheets na interface do dashboard.
- Documentação de escopos, credenciais, dados enviados e configuração segura da integração.

## [v0.5.0] - 2026-10-12

### Implementado

- Licença MIT e termos claros para contribuições.
- Guia de instalação e uso e política de privacidade acessível pelo app.
- Telemetria de diagnóstico opcional, com consentimento explícito, desligada por padrão e limitada a eventos técnicos mínimos enviados somente a endpoint HTTPS configurado pelo operador.
- Integração do ícone SVG do Product Manager ao tema de aplicativos Linux e inclusão da licença/política nos pacotes.

### Segurança

- Remoção do banco SQLite versionado e regras para ignorar bancos, arquivos de ambiente, chaves, certificados e credenciais.

## [v0.4.0] - 2026-10-12

### Implementado

- Launcher desktop que inicia o serviço local e abre a interface no navegador padrão.
- PWA instalável no Android, com manifest, ícones, botão de instalação e cache do shell offline.
- Build Windows x64 com PyInstaller e instalador Inno Setup.
- Geração de pacotes Linux `.deb` e `.rpm`, com build local e workflow multiplataforma.
- ZIP de implantação PWA e pipeline de artefatos para Windows, Linux e Android.

### Aprimorado

- Banco do desktop passa a usar diretório de dados do usuário em Windows/Linux.
- Documentação de instalação e execução multiplataforma.

## [v0.3.1] - 2026-10-12

### Aprimorado

- CI valida as mensagens de cada commit no padrão Conventional Commits.
- Issues recebem labels de tipo e status conforme criação, fechamento e reabertura.
- Release workflow filtra tags SemVer e calcula incremento major/minor/patch sem falha para valores zero.

## [v0.3.0] - 2026-10-12

### Implementado

- Catálogo web de produtos, filtros por categoria e cadastro via API.
- Configuração do endereço, porta e arquivo SQLite por variáveis de ambiente.
- Testes de integração para saúde da API, criação, unicidade, validação e dashboard.
- Capturas reais do dashboard e do catálogo com dados de demonstração.

### Aprimorado

- Marca renomeada para Product Manager em telas, exportações, configuração e documentação.
- Observações opcionais aceitam valor vazio no cadastro.
- Documentação de arquitetura, API, operação, requisitos e modelo de dados atualizada.
- Adicionados CI, changelog, contribuição, política de segurança, código de conduta e configuração do editor.

## [v0.2.0] - 2026-10-12

### Implementado

- Primeira aplicação web local com dashboard administrativo e persistência SQLite.
- Cadastro de clientes, indicadores de estoque, categorias e exportação CSV.
- Interface inicial responsiva com dados de demonstração.
