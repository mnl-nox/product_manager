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

## 3. Baixar APK ou publicar AAB Android

Quando a chave de assinatura Android está configurada, o workflow **Cross-platform packages** gera o APK assinado de instalação direta em cada release. O APK abre a aplicação hospedada por HTTPS e depende do servidor; não funciona offline nem contém banco local. Baixe `product-manager-<versão>-android.apk` na [página de Releases](https://github.com/mnl-nox/product_manager/releases/latest). Sem os secrets da chave, use o PWA; o APK de depuração permanece apenas nos artefatos de validação do Actions.

Para publicação no Google Play, configure no GitHub Actions os secrets `ANDROID_KEYSTORE_BASE64`, `ANDROID_KEYSTORE_PASSWORD`, `ANDROID_KEY_ALIAS` e `ANDROID_KEY_PASSWORD`. O workflow então gera e anexa `product-manager-<versão>-android.aab` e `product-manager-<versão>-android.apk`, ambos assinados com a chave de upload. O AAB deve ser enviado pelo Play Console e não pode ser instalado diretamente. O `versionCode` deriva de `VERSION`; confirme que supera as versões enviadas anteriormente.

Sem os secrets, os pacotes Windows/Linux e o PWA continuam disponíveis. O APK de depuração fica apenas como artefato de validação no Actions, sem publicação como download oficial. Não use uma nova chave se já existe uma chave de upload associada ao app no Play Console.

## Atualização do banco e rastreabilidade de estoque

Antes de atualizar uma instalação existente, faça backup do arquivo SQLite e confirme que é possível restaurá-lo. A inicialização aplica compatibilidade de esquema e cria um saldo de abertura para produtos legados com quantidade positiva que ainda não possuam movimentos. Essa operação registra o saldo atual como ponto inicial; não reconstrói vendas ou recebimentos antigos. O livro-razão impede alterações/exclusões de movimentos, e produtos com histórico não podem ser removidos definitivamente. Teste essa migração em uma cópia do banco antes de atualizar a instância pública.

## Backup e restauração SQLite

A imagem inclui `scripts/database_recovery.py`. O backup usa a API online do SQLite, verifica integridade/esquema e cria um arquivo novo com permissão `0600`; não sobrescreve backups existentes. A restauração também valida a cópia. Para substituir o banco em uso, pare a aplicação e passe `--replace` explicitamente:

```bash
python scripts/database_recovery.py backup /data/product_manager.db /caminho-seguro/product_manager-2026-10-13.db
python scripts/database_recovery.py restore /caminho-seguro/product_manager-2026-10-13.db /data/product_manager.db --replace
```

Guarde cópias em armazenamento separado, protegido e com retenção definida. O comando é manual: não configura agenda, criptografia externa, cópia fora do host ou política de retenção. Faça backup antes de migrações e teste restauração em uma cópia isolada.

## Testar a imagem local com Podman

O teste abaixo constrói sem rede, publica a aplicação somente no loopback e mantém o banco efêmero em `tmpfs`. Não use dados reais neste smoke test.

```bash
export PRODUCT_MANAGER_SETUP_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
podman build --network=none --format docker -t product-manager:qa .
podman run -d --rm --name product-manager-qa \
  --network=slirp4netns \
  -p 127.0.0.1:8000:8000 \
  --tmpfs /data:rw,size=64m,mode=0777 \
  -e PRODUCT_MANAGER_SETUP_TOKEN="$PRODUCT_MANAGER_SETUP_TOKEN" \
  -e PRODUCT_MANAGER_COOKIE_SECURE=0 \
  product-manager:qa
```

Espere o healthcheck do container ficar `healthy` e exercite `/healthz`, `/readyz`, bootstrap/login e as APIs necessárias para validar os fluxos do seu build. Para ver o estado e os logs:

```bash
podman inspect --format '{{.State.Status}} {{.State.Health.Status}}' product-manager-qa
podman logs product-manager-qa
```

Ao terminar, pare o container para apagar o banco temporário:

```bash
podman stop product-manager-qa
```

O teste local de 13/10/2026 construiu `product-manager:qa` com Podman 5.4.2 e executou os fluxos HTTP documentados em `relatorios/qa-e2e-corrections.md`. Essa verificação do container não substitui E2E de navegador nem valida atualização/migração de um volume persistente.

## Limites operacionais

- O servidor precisa permanecer ativo e acessível para login, consultas e gravações.
- O banco é compartilhado por todos os usuários desta implantação; não há isolamento entre organizações.
- Mantenha o token de configuração e senhas fora do código-fonte.
- Teste o fluxo de primeiro acesso, login, cadastro, exportação e restauração de backup antes de uso produtivo.
