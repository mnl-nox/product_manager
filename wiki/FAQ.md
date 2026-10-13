# Perguntas frequentes

## O Product Manager é uma aplicação web ou desktop?

A interface é web. No Windows/Linux, `desktop.py` inicia um servidor local e abre o navegador. No Android, a distribuição é um PWA instalável; não é um APK nativo.

## Preciso instalar dependências Python?

A API e os testes usam bibliotecas padrão do Python. O núcleo C separado requer GNU Make e compilador com suporte a C23.

## Qual é a versão mínima do Python?

Python 3.10 ou superior para execução direta. O Dockerfile usa Python 3.12.

## Existe usuário ou senha padrão?

Não. A primeira conta é criada por bootstrap usando um token temporário. Defina `PRODUCT_MANAGER_SETUP_TOKEN` antes de iniciar a API, ou use o fluxo do launcher desktop.

## Onde fica o banco?

Na execução a partir do código, o padrão é `db/product_manager.db`. É possível substituir o caminho com `PRODUCT_MANAGER_DB`. Pacotes desktop usam o diretório de dados do usuário; Docker Compose usa o volume `product-manager-data`.

## O aplicativo pode ser usado por várias contas?

Sim, com papéis diferentes, mas todas as contas compartilham o mesmo workspace. Não há isolamento entre organizações.

## Quais papéis existem?

`admin`, `operator`, `finance` e `viewer`. As permissões são verificadas pela API.

## O financeiro é contabilidade?

Não. O módulo registra receitas/despesas previstas ou realizadas e calcula saldos operacionais. Não substitui escrituração contábil ou fiscal.

## Os alertas enviam e-mail ou notificações push?

Não na versão documentada. Os alertas são apresentados dentro do aplicativo.

## O aplicativo funciona offline no Android?

O shell da interface pode ser mantido em cache pelo service worker, mas as chamadas `/api/` exigem conexão e não são armazenadas em cache.

## Como exportar dados?

CSV e XLSX podem ser baixados localmente. O envio para Google Sheets é opcional e depende de ID de planilha e token de acesso configurados pelo administrador.

## O app renova o token Google automaticamente?

Não. A configuração documentada usa token OAuth de curta duração; a renovação precisa ser gerenciada externamente.

## Posso expor a porta 8000 na internet?

Não diretamente. O servidor Python não fornece TLS. Para serviço compartilhado, configure HTTPS, cookies Secure, restrição de rede, segredos, backups e procedimentos de atualização. Avalie também os limites de isolamento multi-organização.

## Como executar os testes?

```bash
make test
python3 -m compileall -q api scripts tests
```

Para compilar o núcleo C, execute `make`.

## Como reportar um bug ou vulnerabilidade?

Use os templates de issue para bugs e recursos. Para vulnerabilidades, siga o processo indicado em `SECURITY.md` e evite publicar detalhes exploráveis em issues públicas.

## Onde encontro o roadmap?

No arquivo `.product-manager-roadmap.md`. Ele descreve possibilidades futuras, não promessas de entrega. Consulte também `CHANGELOG.md` para mudanças registradas.