# Arquitetura do Product Manager

## Visão geral

O produto atual é uma aplicação web local. A interface HTML/CSS/JavaScript consome uma API HTTP escrita com a biblioteca padrão do Python; a API valida entradas e persiste os dados em SQLite.

```text
Navegador (ui/)
      │ HTTP / JSON
      ▼
API Python (api/app.py)
      │ consultas parametrizadas
      ▼
SQLite (db/schema.sql → db/product_manager.db)
```

## Componentes

- `ui/`: dashboard, catálogo, formulários e renderização dos resultados.
- `api/`: servidor HTTP, validação, operações SQL, resposta JSON e exportação CSV.
- `db/schema.sql`: tabelas `clients` e `products`, chaves, unicidade e restrições.
- `config/field-mapping.json`: mapeamento explícito entre os nomes de campos do produto e do banco.
- `tests/`: testes de integração da API usando banco temporário.
- `src/` e `include/`: núcleo C23 legado/em evolução, não usado pelo servidor web atual.

## Fluxo de uma requisição

1. O JavaScript envia uma requisição para `/api`.
2. O handler valida formato, tamanho, valores permitidos e campos obrigatórios.
3. A API usa parâmetros SQL para ler ou alterar o SQLite.
4. A resposta inclui JSON e cabeçalhos HTTP de segurança básicos.
5. A interface escapa valores dinâmicos antes de incluí-los no HTML.

## Persistência e dados de demonstração

O caminho padrão é `db/product_manager.db`; `PRODUCT_MANAGER_DB` permite selecionar outro arquivo. A aplicação cria as tabelas se necessário e insere registros de exemplo quando cada tabela está vazia. O arquivo de banco é dado de runtime e deve permanecer fora do controle de versão.

## Limites atuais

O servidor atende desenvolvimento local, sem autenticação, autorização, controle de concorrência avançado ou implantação de produção. O núcleo C não é conectado à aplicação web. As rotas atuais não incluem edição/exclusão, paginação ou busca textual.
