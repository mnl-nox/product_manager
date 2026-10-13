# Guia de instalação e uso

## Instalação

### Windows 10/11

Baixe o instalador `ProductManager-<versão>-windows-x64-setup.exe` nos artefatos da release ou do workflow **Cross-platform packages**, execute-o e abra **Product Manager** pelo menu Iniciar. O banco fica em `%LOCALAPPDATA%\ProductManager\product_manager.db`.

### Debian e Ubuntu

Baixe o arquivo `.deb` correspondente à arquitetura do computador e instale:

```bash
sudo apt install ./product-manager_<versão>_amd64.deb
```

Abra **Product Manager** pelo menu de aplicativos ou execute `product-manager`. O banco fica em `${XDG_DATA_HOME:-~/.local/share}/product-manager/product_manager.db`.

### Fedora, RHEL e derivados

Baixe o RPM compatível e instale com:

```bash
sudo dnf install ./product-manager-<versão>-1.x86_64.rpm
```

### Android

A opção recomendada é o PWA: abra a URL HTTPS publicada pela organização no Chrome para Android e escolha **Instalar app** ou **Adicionar à tela inicial**. Há também um workflow opcional para gerar um wrapper APK de depuração que abre essa mesma URL; ele depende do servidor HTTPS e não deve ser tratado como release assinada para Play Store. A implantação precisa de um servidor HTTPS e controles de autenticação e autorização antes de receber dados corporativos.

## Primeiro uso

### Primeira configuração

Não há conta ou senha padrão. No aplicativo desktop instalado, a primeira execução gera um token temporário no processo local e abre diretamente o formulário de configuração inicial. Crie a conta administradora com uma senha de pelo menos 12 caracteres. O token não aparece nos logs e é invalidado depois do primeiro cadastro.

Ao executar o servidor diretamente ou preparar uma instalação PWA, gere um token aleatório, defina-o no ambiente do servidor e inicie o app. Exemplo no Linux/macOS:

```bash
export PRODUCT_MANAGER_SETUP_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
printf 'Token de configuração: %s
' "$PRODUCT_MANAGER_SETUP_TOKEN"
python3 api/app.py
```

No Windows PowerShell:

```powershell
$rng = [Security.Cryptography.RandomNumberGenerator]::Create()
$bytes = New-Object byte[] 32
$rng.GetBytes($bytes)
$env:PRODUCT_MANAGER_SETUP_TOKEN = ([BitConverter]::ToString($bytes) -replace '-', '').ToLowerInvariant()
$rng.Dispose()
Write-Host "Token de configuração: $env:PRODUCT_MANAGER_SETUP_TOKEN"
python api/app.py
```

Abra `/login`, use o token no formulário **Configuração inicial** e crie o usuário administrador. O token é removido do processo após o uso; os próximos usuários são criados pelo administrador em **Usuários**.

No Windows ou Linux, depois da configuração, inicie o aplicativo pelo menu ou terminal. Ele abre o navegador no computador e mantém a API ligada enquanto a janela do terminal/processo estiver ativa. Use Ctrl+C para encerrar quando iniciado no terminal. Para implantação atrás de HTTPS, configure `PRODUCT_MANAGER_COOKIE_SECURE=1`.

### Papéis

- **Administrador:** usuários, catálogo, financeiro, alertas e exportação Google Sheets.
- **Operação:** leitura e escrita de clientes/produtos, limites e alertas de estoque.
- **Financeiro:** leitura do catálogo e escrita/consulta da área financeira.
- **Somente leitura:** consulta de catálogo, dashboard e alertas.

As contas compartilham o mesmo espaço de trabalho e banco. Não há isolamento entre organizações nem recuperação automatizada de senha. A administração de usuários permite criar contas e desativá-las, revogando suas sessões.

O dashboard resume clientes, produtos e estoque. Em **Produtos**, cadastre, edite, desative e reative itens; administradores podem remover definitivamente apenas produtos sem histórico de movimentações. Produtos com histórico devem ser desativados para preservar rastreabilidade. Produtos desativados ficam ocultos das consultas e relatórios comuns. O histórico de estoque é registrado para saldo inicial, ajustes manuais, vendas realizadas e recebimentos de compras; movimentos são imutáveis e a consulta está disponível pela API autenticada `GET /api/inventory/movements`. Na primeira inicialização após a migração, produtos antigos com saldo positivo recebem uma referência de saldo inicial, sem reconstrução de eventos passados.

Em **Alertas**, configure o limite por item e reconheça alertas; o padrão é `PRODUCT_MANAGER_LOW_STOCK_DEFAULT` (5 unidades se não configurado). Em **Financeiro**, usuários autorizados registram receitas/despesas previstas ou realizadas, consultam saldo e removem lançamentos incorretos. Isso não substitui contabilidade ou sistema fiscal.

Em **Riscos e bugs**, qualquer conta pode registrar um problema ou risco. Administração/operação pode atualizar o estado e o responsável. O formulário não envia anexos nem transmite os registros para fora da instalação.

No dashboard, baixe CSV ou Excel (`.xlsx`). Para enviar diretamente ao Google Sheets, o administrador configura o ID da planilha e um token de acesso no servidor, conforme [Desenvolvimento e operação](development.md#exportacoes-para-planilhas). O banco local é criado automaticamente; faça cópias de segurança com o aplicativo encerrado e proteja-as como dados corporativos.

O workspace começa vazio. Se `PRODUCT_MANAGER_DEMO_DATA=1` estiver definido, a aplicação cria registros de exemplo para avaliação local; não use os dados fictícios como dados de clientes reais. Não exponha o servidor desktop na rede; para serviço compartilhado use HTTPS, cookies Secure, controle de acesso de rede, backups e gestão segura dos segredos.

## Relato de erros e telemetria

O compartilhamento de diagnósticos fica desativado inicialmente. Para participar, marque **Compartilhar diagnóstico técnico de erros (opcional)**. É possível revogar a escolha desmarcando a opção ou limpando os dados do site no navegador.

O administrador precisa configurar `PRODUCT_MANAGER_TELEMETRY_URL` com um endpoint HTTPS controlado pela organização. Sem essa configuração, nenhum evento é transmitido. A integração envia somente o identificador técnico do evento permitido, nome e versão do aplicativo; não envia conteúdo de campos, dados do banco, stack trace, URL, endereço de e-mail ou identificador persistente. O serviço de destino pode receber o endereço IP da conexão nos logs de infraestrutura. Consulte [Política de privacidade](../PRIVACY.md).

Para relatar um erro manualmente, abra uma issue usando o modelo **Bug report**, descreva os passos e resultado esperado e remova dados pessoais e confidenciais. Veja [Contribuição](../CONTRIBUTING.md) e [Segurança](../SECURITY.md).
