# Como contribuir

## Preparação

1. Use Python 3.10+; a aplicação não exige pacotes Python externos.
2. Crie uma branch com nome descritivo, por exemplo `feat/product-search`.
3. Mantenha mudanças focadas e atualize a documentação quando alterar comportamento ou rotas.

## Validar antes de abrir uma contribuição

```bash
make test
python3 -m compileall -q api scripts tests
python3 scripts/check_conventional_commits.py --range origin/main..HEAD
```

Para mudanças no núcleo legado em C, compile também com `make`.

## Commits e pull requests

Use mensagens no padrão Conventional Commits, como `feat(products): add category filter` ou `fix(api): reject negative stock`. A CI valida o título do PR e as mensagens de cada commit. Descreva o problema, a solução e os comandos de validação executados. Não inclua banco local, exportações ou segredos.
