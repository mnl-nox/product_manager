# Índice da documentação

Este diretório contém a documentação operacional, de desenvolvimento e auditoria. Mantenha um ponto de entrada por assunto e use links relativos para referências relacionadas.

## Instalação e operação

- [Instalação e primeiro acesso](installation-usage.md)
- [Plataformas, downloads e empacotamento](platforms.md)
- [Desenvolvimento e configuração](development.md)

## Arquitetura e dados

- [Modelo do sistema e arquitetura — visão consolidada](system-model-and-architecture.md)
- [Arquitetura técnica existente](../doc/architecture-implementation.md)
- [Modelo de dados](../doc/data-model.md)
- [Requisitos](../doc/requirements.md)
- [Inventário e política de consolidação documental](documentation-inventory.md)

A arquitetura e o modelo de dados também aparecem na Wiki. O inventário documental distingue sobreposição provável de evidências históricas ou documentos com finalidades diferentes. Arquivos legados permanecem preservados até que conteúdo, links e histórico tenham sido comparados na [issue #57](https://github.com/mnl-nox/product_manager/issues/57).

## Qualidade e auditoria

- [Plano e resultados de QA](qa-plan-and-results.md)
- [Resultados históricos de validação](test-results.md)
- [Relatório de robustez e engenharia multiplataforma](quality-report.md)
- [Plano de prontidão operacional](enterprise-readiness.md)
- [Auditoria — índice](audit/README.md)
- [Tutorial visual](tutorial-visual.md)
- [Relatórios de execução e correções](../relatorios/README.md)
- [Catálogo de casos, métricas e exemplos de QA](../relatorios/qa-catalog/README.md)

Os relatórios possuem datas, escopos e evidências diferentes. Não combinar resultados históricos como se tivessem sido executados no mesmo commit nem marcar validações como aprovadas sem evidência reproduzível.

## Políticas do repositório

- [Como contribuir](../CONTRIBUTING.md)
- [Política de segurança](../SECURITY.md)
- [Privacidade](../PRIVACY.md)
- [Changelog](../CHANGELOG.md)

## Convenções

1. Atualize este índice ao adicionar, renomear ou migrar documentação.
2. Prefira links relativos para arquivos versionados no repositório.
3. Não mantenha cópias integrais do mesmo conteúdo em `doc/`, `docs/`, `wiki/` ou diretórios de relatórios.
4. Preserve relatórios históricos como evidência; marque documentos obsoletos em vez de apagá-los sem revisão.
5. Antes de excluir um documento, procure referências internas e externas e registre o destino canônico.
6. Valide links locais e âncoras com `python scripts/check_markdown_links.py README.md docs/README.md`.
7. Não declare testes aprovados sem execução reproduzível e evidência registrada.
