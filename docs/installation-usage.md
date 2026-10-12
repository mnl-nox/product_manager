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

O pacote Android é um PWA, não um APK. Abra a URL HTTPS publicada pela organização no Chrome para Android e escolha **Instalar app** ou **Adicionar à tela inicial**. A implantação precisa de um servidor HTTPS e controles de autenticação e autorização antes de receber dados corporativos.

## Primeiro uso

No Windows ou Linux, inicie o aplicativo pelo menu ou terminal. Ele abre o navegador no computador e mantém a API ligada enquanto a janela do terminal/processo estiver ativa. Use Ctrl+C para encerrar quando iniciado no terminal.

O dashboard resume clientes, produtos e estoque. Em **Produtos**, cadastre itens, filtre por categoria e acompanhe disponibilidade. No dashboard, baixe CSV ou Excel (`.xlsx`). Para enviar diretamente ao Google Sheets, o administrador precisa configurar o ID da planilha e um token de acesso no servidor, conforme [Desenvolvimento e operação](development.md#exportacoes-para-planilhas). O banco local é criado automaticamente; faça cópias de segurança com o aplicativo encerrado e proteja-as como dados corporativos.

Os dados iniciais são exemplos de demonstração. Remova-os e verifique o banco antes de uso real. A aplicação atual não tem autenticação incorporada; não exponha o servidor desktop na rede.

## Relato de erros e telemetria

O compartilhamento de diagnósticos fica desativado inicialmente. Para participar, marque **Compartilhar diagnóstico técnico de erros (opcional)**. É possível revogar a escolha desmarcando a opção ou limpando os dados do site no navegador.

O administrador precisa configurar `PRODUCT_MANAGER_TELEMETRY_URL` com um endpoint HTTPS controlado pela organização. Sem essa configuração, nenhum evento é transmitido. A integração envia somente o identificador técnico do evento permitido, nome e versão do aplicativo; não envia conteúdo de campos, dados do banco, stack trace, URL, endereço de e-mail ou identificador persistente. O serviço de destino pode receber o endereço IP da conexão nos logs de infraestrutura. Consulte [Política de privacidade](PRIVACY.md).

Para relatar um erro manualmente, abra uma issue usando o modelo **Bug report**, descreva os passos e resultado esperado e remova dados pessoais e confidenciais. Veja [Contribuição](../CONTRIBUTING.md) e [Segurança](../SECURITY.md).
