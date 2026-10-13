# Publicação Web e Android

## Instância pública

A instância disponibilizada para acesso pelo navegador está em **[https://product-manager-14fq.onrender.com/login](https://product-manager-14fq.onrender.com/login)**. Use HTTPS e conclua o login ou o provisionamento inicial se a instalação ainda não tiver administrador. Não compartilhe credenciais nem tokens de configuração. A disponibilidade depende do serviço de hospedagem.

![Dashboard do Product Manager](screenshots/dashboard.png)

![Catálogo de produtos](screenshots/products.png)

As capturas de tela do repositório são referências visuais; atualize-as quando a interface mudar. Não inclua dados pessoais, tokens ou informações reais de clientes nas capturas.

O Product Manager usa uma API Python e um banco SQLite. O site informativo do GitHub Pages não hospeda a API nem o banco. Para uso real, publique o serviço completo em um servidor HTTPS com armazenamento persistente.

## 1. Implantar no Render

1. Entre em https://render.com e conecte sua conta GitHub.
2. No painel, selecione **New → Blueprint** e escolha o repositório `mnl-nox/product_manager`.
3. O Render lerá `render.yaml`, criará o serviço Docker, reservará um disco persistente de 1 GB em `/data` e configurará HTTPS e cookies seguros.
4. Aguarde o primeiro deploy e copie a URL HTTPS atribuída ao serviço.
5. No painel do serviço, abra **Environment** e copie o valor de `PRODUCT_MANAGER_SETUP_TOKEN`. Trate-o como segredo; não o publique nem o envie em issues.
6. Abra a URL HTTPS. Conclua a configuração inicial usando o token e crie a conta administradora com uma senha forte.

O blueprint usa um serviço Render pago compatível com disco persistente. Não remova o disco nem recrie o banco sem um backup. Antes de armazenar dados reais, configure e teste backups periódicos e recuperação. O plano e o preço vigentes aparecem no painel do provedor.

## 2. Usar no navegador e instalar como PWA

Abra a URL HTTPS do serviço no Chrome, Edge ou navegador compatível. No Android, use o menu do Chrome e selecione **Instalar app** ou **Adicionar à tela inicial**. A instalação PWA não exige APK, mas precisa da API online para operações com dados.

## 3. Gerar um APK Android

O repositório inclui um wrapper Android nativo que abre a aplicação hospedada por HTTPS. Depois que o serviço estiver publicado:

1. Abra a aba **Actions** do GitHub.
2. Selecione o workflow **Android APK** e clique em **Run workflow**.
3. Informe a URL HTTPS exata do serviço implantado.
4. Quando terminar, abra a execução e baixe o artefato `product-manager-android-apk`.
5. Extraia `app-debug.apk`, transfira-o para o Android e abra o arquivo para instalar. Se necessário, autorize temporariamente a instalação para o aplicativo usado para abrir o arquivo.

Esse APK é um pacote de instalação para teste/distribuição direta, assinado com a chave de depuração automática do Android Gradle Plugin. Não é adequado para publicação na Play Store; para isso, gere uma versão release com uma chave de assinatura protegida. O APK depende do servidor HTTPS configurado no build e não funciona como sistema independente/offline.

## Limites operacionais

- O servidor precisa permanecer ativo e acessível para login, consultas e gravações.
- O banco é compartilhado por todos os usuários desta implantação; não há isolamento entre organizações.
- Mantenha o token de configuração e senhas fora do código-fonte.
- Teste o fluxo de primeiro acesso, login, cadastro, exportação e restauração de backup antes de uso produtivo.
