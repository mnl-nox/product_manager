# Índice da documentação

Este diretório contém a documentação operacional e de desenvolvimento. Para evitar divergência, mantenha um documento principal por assunto e use links relativos para referências relacionadas.

## Instalação e operação

- [Instalação e primeiro acesso](installation-usage.md)
- [Plataformas, downloads e empacotamento](platforms.md)
- [Desenvolvimento e configuração](development.md)

## Arquitetura e dados

- [Modelo do sistema e arquitetura — visão consolidada](system-model-and-architecture.md)
- [Arquitetura técnica existente](../doc/architecture.md)
- [Modelo de dados](../doc/data-model.md)
- [Requisitos](../doc/requirements.md)

> **Estado de organização:** há sobreposição entre `docs/system-model-and-architecture.md`, `doc/architecture.md` e `wiki/Architecture.md`, além de sobreposição entre os documentos de modelo de dados. A visão consolidada em `docs/` é o ponto de entrada recomendado; os arquivos legados permanecem preservados até que a issue #57 conclua a comparação de conteúdo, referências e histórico. A remoção ou migração deve atualizar links internos, Wiki e referências externas relevantes.

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
