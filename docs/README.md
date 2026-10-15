# Índice da documentação

Este diretório contém a documentação operacional e de desenvolvimento. Para evitar divergência, mantenha um documento principal por assunto e use links relativos para referências relacionadas.

## Instalação e operação

- [Instalação e primeiro acesso](installation-usage.md)
- [Plataformas, downloads e empacotamento](platforms.md)
- [Desenvolvimento e configuração](development.md)

## Arquitetura e dados

- [Arquitetura](../doc/architecture.md)
- [Modelo de dados](../doc/data-model.md)
- [Requisitos](../doc/requirements.md)

> **Estado de organização:** arquitetura, modelo de dados e requisitos ainda residem em `doc/`. A migração para este diretório só deve ocorrer em uma alteração dedicada que atualize todos os links internos, links da Wiki e referências externas relevantes.

## Qualidade

- [Plano e resultados de QA](qa-plan-and-results.md)
- [Resultados de validação](test-results.md)
- [Tutorial visual](tutorial-visual.md)
- [Relatórios de qualidade](../relatórios/README.md)

## Políticas do repositório

- [Como contribuir](../CONTRIBUTING.md)
- [Política de segurança](../SECURITY.md)
- [Privacidade](../PRIVACY.md)
- [Changelog](../CHANGELOG.md)

## Convenções

1. Atualize este índice quando adicionar, renomear ou remover documentação.
2. Prefira links relativos para arquivos versionados no repositório.
3. Não mantenha cópias integrais do mesmo conteúdo em `doc/`, `docs/`, `wiki/` ou diretórios de relatórios.
4. Preserve relatórios históricos como evidência; marque claramente documentos obsoletos em vez de apagá-los sem revisão.
5. Não declare testes aprovados sem execução reproduzível e evidência registrada.
