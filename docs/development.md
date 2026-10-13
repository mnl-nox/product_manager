# Desenvolvimento e operação

## Inicializar

```bash
python3 api/app.py
```

O servidor escuta em `127.0.0.1:8000`. `PRODUCT_MANAGER_HOST` e `PRODUCT_MANAGER_PORT` podem alterar o endereço. Na primeira inicialização, o esquema definido em `db/schema.sql` é aplicado; o workspace começa vazio por padrão. Para avaliação local com exemplos, defina `PRODUCT_MANAGER_DEMO_DATA=1`. `PRODUCT_MANAGER_DB` pode apontar para um arquivo SQLite alternativo.

## API

As respostas são JSON, exceto os downloads CSV/XLSX.

| Método | Rota | Uso |
|---|---|---|
| GET | `/api/auth/setup-status` | Indica se precisa criar o primeiro administrador |
| POST | `/api/auth/setup` | Cria o administrador inicial usando token temporário |
| POST | `/api/auth/login` | Inicia sessão |
| GET | `/api/auth/me` | Conta atual e token CSRF |
| POST | `/api/auth/logout` | Revoga a sessão atual |
| GET/POST | `/api/auth/users` | Lista/cria contas (admin) |
| POST | `/api/auth/users/{id}/deactivate` | Desativa conta e revoga as sessões (admin) |
| GET | `/healthz` | Liveness público, resposta mínima sem dados internos |
| GET | `/readyz` | Readiness público; valida acesso ao SQLite e retorna 503 se indisponível |
| GET | `/api/health` | Estado básico do serviço, exige sessão autenticada |
| GET | `/api/dashboard` | Indicadores, categorias, clientes recentes e estoque crítico |
| GET | `/api/categories` | Categorias e contagem de produtos |
| GET | `/api/clients` | Clientes cadastrados |
| GET | `/api/products?category=Hardware` | Catálogo; `category=all` lista todos |
| POST | `/api/clients` | Cadastra cliente (admin/operação) |
| POST | `/api/products` | Cadastra produto (admin/operação) |
| POST | `/api/products/{id}` | Atualiza produto (admin/operação) |
| POST | `/api/products/{id}/deactivate` | Desativa produto sem apagar o histórico |
| POST | `/api/products/{id}/activate` | Reativa produto desativado |
| POST | `/api/products/{id}/delete` | Remove produto e alertas associados (admin) |
| GET | `/api/dashboard/export.csv` | Exporta indicadores e dados em CSV |
| GET | `/api/dashboard/export.xlsx` | Baixa uma planilha Excel `.xlsx` |
| GET | `/api/finance/summary` | Totais realizados e saldo projetado |
| GET/POST | `/api/finance/entries` | Lista/cria receitas e despesas |
| GET | `/api/alerts/stock` | Alertas de estoque ativos |
| GET | `/api/alerts/config` | Limite padrão atual |
| POST | `/api/alerts/stock/{id}/threshold` | Atualiza limite mínimo do produto |
| POST | `/api/alerts/stock/{id}/acknowledge` | Marca alerta como visto |
| GET/POST | `/api/work-items` | Lista e registra bugs/riscos |
| POST | `/api/work-items/{id}` | Atualiza estado/responsável (admin/operação) |
| GET | `/api/integrations/google-sheets/status` | Informa se a integração está configurada, sem expor credenciais |
| POST | `/api/integrations/google-sheets/export` | Envia os indicadores e o catálogo exportável à planilha configurada |

Todas as rotas de negócio, exceto `/api/auth/setup-status`, `/api/auth/setup`, `/api/auth/login` e arquivos estáticos, exigem uma sessão autenticada. `/healthz` e `/readyz` são exceções operacionais públicas e retornam somente estados mínimos, sem detalhes de conexão. As rotas de escrita exigem `X-CSRF-Token`, obtido em `/api/auth/me`. Os papéis são verificados no servidor.

### Configuração do acesso inicial

Não existe senha padrão. Gere um valor aleatório e injete `PRODUCT_MANAGER_SETUP_TOKEN` no ambiente do primeiro processo. A tela `/login` apresenta o formulário de criação do primeiro administrador somente enquanto não houver conta ativa e o token estiver definido. Use senha de pelo menos 12 caracteres. Após o cadastro, o processo remove o token do próprio ambiente e a rota de bootstrap fica bloqueada pelo estado do banco.

As sessões duram 12 horas, os cookies são HttpOnly/SameSite=Strict e usam `Secure` por padrão quando o servidor não está vinculado ao loopback. Atrás de HTTPS, defina explicitamente `PRODUCT_MANAGER_COOKIE_SECURE=1`. Senhas usam scrypt, os tokens de sessão são armazenados como hash e tentativas inválidas recebem limitação temporária.

Papéis disponíveis: `admin` (configuração completa), `operator` (catálogo, limites e alertas), `finance` (leitura do catálogo e escrita/consulta financeira) e `viewer` (leitura). Exportação direta ao Google Sheets e remoção permanente de produtos são restritas ao admin. Eles compartilham o mesmo espaço de trabalho; ainda não há separação por organização.

### Financeiro e alertas

O financeiro mantém lançamentos de receita/despesa previstos ou realizados e calcula saldos operacionais em BRL. Não é módulo contábil/fiscal. Alertas de estoque são exibidos no app; use `PRODUCT_MANAGER_LOW_STOCK_DEFAULT` para alterar o limite padrão ou configure um mínimo por produto. O reconhecimento oculta o alerta até que a quantidade mude ou o limite seja atualizado. Não há envio de e-mail ou push nesta versão.

## Exportações para planilhas

CSV e `.xlsx` podem ser baixados sem credenciais. O Excel é gerado localmente pela API. Para habilitar Google Sheets, ative a Google Sheets API no projeto Google Cloud, crie uma credencial de serviço ou obtenha um access token OAuth com escopo `https://www.googleapis.com/auth/spreadsheets`, compartilhe a planilha de destino com a identidade dessa credencial e configure no ambiente do servidor:

```ini
PRODUCT_MANAGER_GOOGLE_SHEETS_SPREADSHEET_ID=ID_DA_PLANILHA
PRODUCT_MANAGER_GOOGLE_SHEETS_ACCESS_TOKEN=TOKEN_OAUTH_DE_CURTA_DURACAO
PRODUCT_MANAGER_GOOGLE_SHEETS_RANGE=Export!A1
```

O token não deve ser colocado no repositório, frontend, SQLite, URL ou logs. Injete-o por um gerenciador de segredos e renove-o conforme sua validade; o app não executa o fluxo de renovação OAuth. O servidor usa `spreadsheets.values.update` com `valueInputOption=RAW` e grava no intervalo configurado. Prepare a aba/intervalo de destino com antecedência, restrinja o compartilhamento ao necessário e limpe manualmente células antigas caso a nova exportação contenha menos linhas. A planilha recebe agregados do dashboard e campos de produto (nome, categoria, SKU, marca, preço, quantidade e status); não exporta os registros pessoais dos clientes.

O endpoint usa a API oficial [`spreadsheets.values.update`](https://developers.google.com/workspace/sheets/api/reference/rest/v4/spreadsheets.values/update). O envio direto transfere os dados à infraestrutura Google associada à credencial e à planilha configurada.

Chamadas de escrita feitas por cliente HTTP precisam enviar o cookie `pm_session` obtido no login e o `X-CSRF-Token` retornado no corpo da resposta. Erros de validação retornam HTTP 400; conflito de unicidade retorna HTTP 409. O esquema SQLite documenta campos obrigatórios e restrições de domínio.

## Verificações

```bash
make test
python3 -m compileall -q api scripts tests
make
```

O dashboard fica em `/` e o catálogo em `/products`.
