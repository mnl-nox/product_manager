# Arquitetura do Product Manager

## Visão geral

O produto atual é uma aplicação local multiplataforma. Windows e Linux iniciam um servidor HTTP local e abrem a interface no navegador padrão; Android instala a mesma interface como PWA. A API escrita com a biblioteca padrão do Python valida entradas e persiste os dados em SQLite.

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
- `desktop.py`: launcher do servidor local para os pacotes desktop.
- `packaging/`: build PyInstaller/Inno Setup para Windows e pacotes `.deb`/`.rpm` para Linux.
- `ui/manifest.webmanifest` e `ui/service-worker.js`: instalação e cache offline do shell PWA.

## Fluxo de uma requisição

1. O JavaScript envia uma requisição para `/api`.
2. O handler valida formato, tamanho, valores permitidos e campos obrigatórios.
3. A API usa parâmetros SQL para ler ou alterar o SQLite.
4. A resposta inclui JSON e cabeçalhos HTTP de segurança básicos.
5. A interface escapa valores dinâmicos antes de incluí-los no HTML.

## Persistência e dados de demonstração

Em desenvolvimento, o caminho padrão é `db/product_manager.db`; `PRODUCT_MANAGER_DB` permite selecionar outro arquivo. Pacotes desktop usam o diretório de dados do usuário. A aplicação cria as tabelas se necessário e insere registros de exemplo quando cada tabela está vazia. O arquivo de banco é dado de runtime.

## Limites atuais

O modo desktop é local e não tem autenticação. O PWA deve ser hospedado em HTTPS atrás de infraestrutura corporativa apropriada; a API ainda requer autenticação e autorização antes de ser aberta a uma rede. O núcleo C não é conectado à aplicação web. As rotas atuais não incluem edição/exclusão, paginação ou busca textual.
