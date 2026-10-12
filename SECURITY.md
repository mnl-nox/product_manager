# Política de segurança

## Escopo e limitações

Product Manager é uma aplicação local em desenvolvimento. A API não implementa autenticação, autorização, CSRF, limitação de taxa ou implantação TLS e não deve ser exposta a redes públicas. Use apenas dados fictícios durante avaliação.

## Reportar uma vulnerabilidade

Não publique detalhes exploráveis em issues públicas. Até existir um canal privado configurado pelo mantenedor, reporte apenas a existência do problema em uma issue sem dados de exploração e solicite um canal privado. Não envie credenciais ou dados pessoais.

## Boas práticas de desenvolvimento

- Não comite credenciais, dados pessoais nem arquivos de banco com dados reais.
- Use consultas parametrizadas para SQL e escape conteúdo renderizado no HTML.
- Mantenha dependências mínimas e aplique atualizações de segurança antes de qualquer implantação.
