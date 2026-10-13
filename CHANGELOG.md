## [Unreleased]

### Documentação e manutenção

- Revisadas as referências de arquitetura, modelo de dados, requisitos, API, instalação, segurança/privacidade, Wiki e roadmap contra o código atual.
- Corrigidas descrições de movimentações de estoque, regras de exclusão de produtos, migração de saldos legados e limites dos módulos ERP.
- Corrigida nesta branch a divergência de `VERSION`; o workflow sincroniza a versão antes de criar tags futuras e exclui o commit técnico de sincronização das notas de release.

## [v1.7.5] - 2026-10-13

### Alterações

- docs(changelog): record stock ledger and documentation corrections
- docs(privacy): include inventory, purchasing, sales and HR records

## [v1.7.4] - 2026-10-13

### Alterações

- docs(readme): describe stock ledger and ERP scope

## [v1.7.3] - 2026-10-13

### Alterações

- docs(requirements): align requirements with implemented ERP modules

## [v1.7.2] - 2026-10-13

### Alterações

- docs(data): correct entity fields and document ERP data model

## [v1.7.1] - 2026-10-13

### Alterações

- docs(architecture): reflect current ERP modules and stock ledger

## [v1.7.0] - 2026-10-13

### Alterações

- Merge pull request #16 from mnl-nox/feature/erp-stock-ledger-foundation
- docs: place inventory route in API table
- docs(data): document append-only stock ledger
- docs(api): document inventory movement endpoint
- test(inventory): verify legacy stock baseline migration
- fix(inventory): establish opening balances for existing products
- test: reset immutable stock ledger in disposable fixtures
- test(inventory): add isolated stock ledger coverage
- test: isolate inventory ledger tests from API fixtures
- docs(inventory): document stock movement ledger
- test(inventory): cover append-only stock ledger
- feat(inventory): record stock changes transactionally
- feat(inventory): add append-only stock movement ledger

## [v1.6.0] - 2026-10-13

### Alterações

- feat(reports): add unit and department dimensions

## [v1.5.0] - 2026-10-13

### Alterações

- feat(erp): integrate purchasing HR and reporting

## [v1.4.0] - 2026-10-13

### Alterações

- feat(purchasing): add supplier and purchase workflows

## [v1.3.4] - 2026-10-13

### Alterações

- fix(site): remove escaped newline artifacts

## [v1.3.3] - 2026-10-13

### Alterações

- docs(quality): document feedback and contact limitations

## [v1.3.2] - 2026-10-13

### Alterações

- docs(quality): track reviews and contact UI checks

## [v1.3.1] - 2026-10-13

### Alterações

- fix(site): keep contact section inside main content

## [v1.3.0] - 2026-10-13

### Alterações

- feat(site): add user feedback and maintainer contacts

## [v1.2.13] - 2026-10-13

### Alterações

- docs(readme): link organized quality reports
- docs(reports): document current risk and release analysis

## [v1.2.12] - 2026-10-13

### Alterações

- docs(reports): specify web performance validation plan

## [v1.2.11] - 2026-10-13

### Alterações

- docs(reports): define quality and reliability metrics
- docs(reports): establish repeatable quality execution protocol

## [v1.2.10] - 2026-10-13

### Alterações

- docs(reports): add reproducible validation examples

## [v1.2.9] - 2026-10-13

### Alterações

- docs(reports): document user journeys by role and platform

## [v1.2.8] - 2026-10-13

### Alterações

- docs(reports): define functional and security test cases

## [v1.2.7] - 2026-10-13

### Alterações

- docs(reports): add quality evidence index

## [v1.2.6] - 2026-10-13

### Alterações

- docs(quality): record version synchronization risk

## [v1.2.5] - 2026-10-13

### Alterações

- docs(quality): update readiness hardening evidence

## [v1.2.4] - 2026-10-13

### Alterações

- docs(api): document liveness and readiness probes

## [v1.2.3] - 2026-10-13

### Alterações

- docs(quality): record readiness probes and pending validation

## [v1.2.2] - 2026-10-13

### Alterações

- test(api): cover public health and readiness probes
- fix(container): healthcheck application readiness

## [v1.2.1] - 2026-10-13

### Alterações

- fix(deploy): use database readiness probe

## [v1.2.0] - 2026-10-13

### Alterações

- feat(web): add safe liveness and readiness endpoints
- docs(platform): refresh release and packaging status

## [v1.1.6] - 2026-10-13

### Alterações

- docs(readme): link cross-platform quality report

## [v1.1.5] - 2026-10-13

### Alterações

- docs(quality): add cross-platform robustness audit report

## [v1.1.4] - 2026-10-13

### Alterações

- fix(packaging): read RPM docs from staged paths

## [v1.1.3] - 2026-10-13

### Alterações

- fix(packaging): include required documentation in RPM

## [v1.1.2] - 2026-10-13

### Alterações

- fix(release): recover missing release notes

## [v1.1.1] - 2026-10-13

### Alterações

- fix(ci): dispatch package builds for token-created release tags

## [v1.1.0] - 2026-10-13

### Publicação e documentação

- Adicionado endereço público da aplicação Web hospedada no Render.
- Documentada implantação Web/Android, acesso HTTPS e limitações operacionais.
- Atualizada a Wiki e o roadmap interno para refletir o estado inicial de publicação.
- Preparada a documentação de capturas de tela sem dados sensíveis.
- Adicionado projeto Android wrapper e workflow para gerar APK vinculado à URL HTTPS publicada.

### Limites desta versão

- A publicação Web não equivale a auditoria de segurança ou SLA de disponibilidade.
- O banco permanece compartilhado entre as contas desta instalação; não há isolamento multi-organização.
- O APK precisa ser compilado e validado em dispositivo; não declarar assinatura de produção nem publicação na Play Store.


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
