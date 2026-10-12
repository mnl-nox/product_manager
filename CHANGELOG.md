# Changelog

Mudanças notáveis do projeto são registradas neste arquivo.

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
