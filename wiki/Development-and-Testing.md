# Desenvolvimento e testes

## Ambiente

Para API e testes, Python 3.10+ é suficiente; a aplicação usa bibliotecas padrão. O container é construído com Python 3.12. Para compilar o núcleo C, instale GNU Make e GCC/Clang com suporte a C23.

## Comandos Make

| Comando | Ação |
|---|---|
| `make` | Compila o núcleo C para `build/product_manager` |
| `make run` | Executa o binário C |
| `make run-api` | Executa `python3 api/app.py` |
| `make run-desktop` | Executa `python3 desktop.py` |
| `make test` | Executa testes Python com unittest |
| `make package-linux` | Gera pacote Linux via script de empacotamento |
| `make package-pwa` | Gera ZIP de implantação PWA |
| `make clean` | Remove objetos e binário do núcleo C |

O núcleo C é separado da aplicação web. A API e a interface atuais são implementadas em Python e arquivos web, não no binário C.

## Executar verificações

```bash
make test
python3 -m compileall -q api scripts tests
make
```

Os testes usam banco temporário segundo o README e não devem alterar o banco de desenvolvimento. Confira `docs/test-results.md` para resultados documentados por ambiente.

## Organização dos testes

- `tests/test_api.py`: testes da API.
- `tests/test_pwa.py`: verificações relacionadas ao PWA.
- `tests/test_conventional_commits.py`: validações de mensagens de commit.
- `tests/test_release_notes.py`: validações de notas de release.

## CI

Os workflows ficam em `.github/workflows/`. Incluem CI, validação de commits convencionais, gerenciamento de issues/labels, empacotamento e release. Consulte os arquivos de workflow para gatilhos, permissões e artefatos atuais.

## Convenções de contribuição

Leia `CONTRIBUTING.md` e `doc/github-workflow.md`. O repositório inclui template de Pull Request e modelos de issue. Em termos gerais:

1. Abra uma issue para discutir defeitos ou mudanças relevantes.
2. Crie uma branch de trabalho.
3. Faça mudanças pequenas e verificáveis.
4. Execute testes e verificações locais.
5. Atualize documentação e changelog quando necessário.
6. Abra Pull Request com objetivo, escopo, testes e limitações.

## Boas práticas de manutenção

- Não comite `.env`, tokens, banco real ou dados pessoais.
- Preserve compatibilidade com bancos existentes; alterações de esquema precisam de migração e teste.
- Prefira SQL parametrizado e validação no servidor.
- Adicione testes para autorização, CSRF, unicidade e casos de erro.
- Faça backup antes de validar migrações em uma instalação que contenha dados.
- Documente diferenças entre comportamento implementado e itens planejados.