# Como contribuir

O Product Manager é mantido por [Manoel E. S. S. (`@mnl-nox`)](https://github.com/mnl-nox). Contribuições da comunidade são bem-vindas; siga as orientações abaixo para facilitar a revisão.

## Preparação

1. Use Python 3.10+; a aplicação não exige pacotes Python externos.
2. Crie uma branch com nome descritivo, por exemplo `feat/product-search`.
3. Mantenha mudanças focadas e atualize a documentação quando alterar comportamento ou rotas.
4. Não inclua arquivos `.env`, bancos SQLite, dados de clientes, logs, exportações, chaves ou credenciais. Use dados sintéticos nos exemplos.

## Validar antes de abrir uma contribuição

```bash
make test
python3 -m compileall -q api scripts tests
python3 scripts/check_conventional_commits.py --range origin/main..HEAD
```

Para mudanças no núcleo legado em C, compile também com `make`.

## Commits e pull requests

Use mensagens no padrão Conventional Commits, como `feat(products): add category filter` ou `fix(api): reject negative stock`. A CI valida o título do PR e as mensagens de cada commit. Descreva o problema, a solução e os comandos de validação executados. Não inclua banco local, exportações ou segredos.

## Política de contribuição

Ao enviar uma contribuição, você confirma que tem direito de licenciá-la sob a licença MIT deste projeto. Contribuições devem ser originais ou ter sua licença e atribuição documentadas. Não envie conteúdo confidencial, dados pessoais, credenciais ou código de terceiros sem permissão. Os mantenedores podem pedir alterações, aceitar ou rejeitar contribuições; enviar uma contribuição não garante sua inclusão.
