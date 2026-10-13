# Product Manager — Wiki

**Mantenedor:** [Manoel E. S. S. (`@mnl-nox`)](https://github.com/mnl-nox) · [Site do projeto](https://mnl-nox.github.io/product_manager/) · [Código-fonte](https://github.com/mnl-nox/product_manager)

> Aplicativo de gestão de produtos para Windows e Linux desktop e Android via PWA. Reúne catálogo, clientes, estoque, usuários, financeiro operacional, alertas e exportação de dados.

## Navegação

- [Visão geral e arquitetura](Architecture.md)
- [Instalação e primeiro acesso](Installation-and-Usage.md)
- [Referência da API](API-Reference.md)
- [Modelo de dados](Data-Model.md)
- [Configuração](Configuration.md)
- [Segurança e privacidade](Security-and-Privacy.md)
- [Desenvolvimento e testes](Development-and-Testing.md)
- [Plataformas e implantação](Platforms-and-Deployment.md)
- [Limitações e roadmap](Limitations-and-Roadmap.md)

## Objetivo

O Product Manager centraliza cadastros de clientes e produtos, acompanha quantidades e itens com estoque crítico, oferece um dashboard operacional e registra receitas/despesas previstas ou realizadas. O workspace é compartilhado pelas contas locais da instalação.

## Funcionalidades atuais

- Dashboard com indicadores, categorias, clientes recentes e estoque crítico.
- Cadastro e consulta de clientes e produtos; busca por nome, SKU, marca e fornecedor.
- Edição, desativação e reativação de produtos; remoção permanente restrita a administradores.
- Contas locais com papéis de administrador, operação, financeiro e leitura.
- Sessões com expiração, hash de senha scrypt, proteção CSRF e limitação de tentativas de login.
- Alertas de estoque com limite padrão e limite individual por produto.
- Financeiro operacional para receitas e despesas, com saldo agregado.
- Registro interno de bugs e riscos.
- Exportação CSV e XLSX; integração opcional de exportação para Google Sheets.
- Aplicação web responsiva, launcher desktop e PWA instalável para Android.
- Banco SQLite local; API Python usando bibliotecas padrão.

## Tecnologias verificadas

| Camada | Implementação |
|---|---|
| API/servidor | Python 3.10+; o container usa Python 3.12 |
| Interface | HTML, CSS e JavaScript em `ui/` |
| Persistência | SQLite; esquema em `db/schema.sql` |
| Desktop | `desktop.py`, servidor local e navegador padrão |
| PWA | `ui/manifest.webmanifest` e service worker |
| Container | Dockerfile e Docker Compose |
| Núcleo C | C23 separado da aplicação web; em evolução |
| Testes | `unittest` |
| Build | GNU Make; GCC/Clang para o núcleo C |

## Início rápido

Requisitos: Python 3.10 ou superior. Clone o projeto e inicie a API:

```bash
git clone https://github.com/mnl-nox/product_manager.git
cd product_manager
python3 api/app.py
```

Abra http://127.0.0.1:8000. Na primeira configuração, crie o administrador usando o fluxo de bootstrap descrito em [Instalação e primeiro acesso](Installation-and-Usage.md). Não existe senha padrão.

Para executar os testes:

```bash
make test
```

## Limites importantes

- As contas compartilham um único workspace; não existe isolamento multi-organização.
- O financeiro é operacional e não substitui contabilidade ou escrituração fiscal.
- O PWA exige implantação externa atrás de HTTPS; o servidor Python não fornece TLS.
- O núcleo C é independente e não substitui a aplicação web Python.
- O envio ao Google Sheets é opcional e exige credenciais configuradas pelo administrador.

## Fontes do repositório

Esta documentação foi preparada a partir da estrutura e dos arquivos da branch `main`, incluindo `README.md`, `api/app.py`, `db/schema.sql`, `docs/`, `doc/`, `Makefile`, `Dockerfile` e `compose.yaml`. Revise estas páginas quando o código ou os contratos da API mudarem.