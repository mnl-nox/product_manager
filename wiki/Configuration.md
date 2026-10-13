# Configuração

A aplicação lê configurações do ambiente. O arquivo `.env.example` é uma referência de nomes; não contém credenciais válidas. O processo não depende de instalar bibliotecas Python externas para a API básica.

## Variáveis

| Variável | Finalidade | Observações |
|---|---|---|
| `PRODUCT_MANAGER_DB` | Caminho do banco SQLite | Padrão de desenvolvimento: `db/product_manager.db`; container: `/data/product_manager.db` |
| `PRODUCT_MANAGER_HOST` | Interface de escuta | Desktop: `127.0.0.1`; container define `0.0.0.0) dentro do container |
| `PRODUCT_MANAGER_PORT` | Porta HTTP | Padrão: `8000`; launcher desktop aceita `0` para porta livre |
| `PRODUCT_MANAGER_SETUP_TOKEN` | Token temporário para criar primeiro administrador | Gere aleatoriamente; use apenas durante bootstrap |
| `PRODUCT_MANAGER_COOKIE_SECURE` | Configura atributo Secure do cookie | Defina `1` atrás de HTTPS |
| `PRODUCT_MANAGER_LOW_STOCK_DEFAULT` | Limite padrão para alerta de estoque baixo | O exemplo de configuração usa `5` |
| `PRODUCT_MANAGER_DEMO_DATA` | Insere registros demonstrativos para avaliação local | Desativado por padrão; use `1` somente para teste |
| `PRODUCT_MANAGER_TELEMETRY_URL` | Endpoint opcional de diagnóstico técnico | Deve ser HTTPS e controlado pela organização |
| `PRODUCT_MANAGER_GOOGLE_SHEETS_SPREADSHEET_ID` | ID da planilha de destino | Opcional |
| `PRODUCT_MANAGER_GOOGLE_SHEETS_ACCESS_TOKEN` | Token OAuth de curta duração | Opcional; não versionar nem registrar em logs |
| `PRODUCT_MANAGER_GOOGLE_SHEETS_RANGE` | Intervalo de destino | Exemplo: `Export!A1` |

## Configuração local

Exemplo para iniciar uma instância com banco alternativo:

```bash
export PRODUCT_MANAGER_DB="$HOME/product-manager.db"
export PRODUCT_MANAGER_HOST=127.0.0.1
export PRODUCT_MANAGER_PORT=8000
python3 api/app.py
```

Não exponha o servidor desktop à rede local sem arquitetura de implantação e controles de segurança apropriados.

## Bootstrap do administrador

Gere o segredo apenas no ambiente do processo:

```bash
export PRODUCT_MANAGER_SETUP_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
python3 api/app.py
```

Após criar o primeiro administrador, o fluxo de bootstrap é bloqueado pelo estado do banco. Não reutilize o token, não o coloque no repositório e não o compartilhe em canais públicos.

## Cookies e HTTPS

O desktop local pode operar em HTTP no loopback. Para implantação HTTPS, configure `PRODUCT_MANAGER_COOKIE_SECURE=1`. O servidor Python não termina TLS; use um proxy/servidor HTTPS e mantenha a UI e a API na mesma origem.

O Compose do repositório é voltado a teste local e define `PRODUCT_MANAGER_COOKIE_SECURE=0`; ajuste a arquitetura e a configuração antes de uso público.

## Google Sheets

Configure ID, token de acesso e intervalo no ambiente do servidor. Ative a API Google Sheets, conceda à identidade configurada acesso apenas à planilha necessária e mantenha o token em um gerenciador de segredos. O app usa a operação de atualização de valores e não executa renovação OAuth automática. O envio exporta agregados do dashboard e campos de produto; não exporta os cadastros pessoais dos clientes.

## Telemetria opcional

A telemetria é desativada por padrão. Só há envio quando o usuário consente e o administrador configura um endpoint HTTPS. Não configure endpoint de terceiros sem revisar destino, dados e política de retenção.