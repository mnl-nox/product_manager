# Resultado dos testes

**Registro histórico:** validação local da versão **1.0.0**, executada em **12/10/2026**. Estes resultados descrevem apenas aquele ambiente e não substituem os checks de CI do commit ou release atual.

## Ambiente disponível

- Debian GNU/Linux 13 (trixie), x86_64, kernel Linux 6.12.
- Python 3.13.5; não havia Python 3.10, 3.11 ou 3.12 instalado para uma matriz local.
- GCC/`cc` disponível; `rpmbuild`, PowerShell (`pwsh`) e Android Debug Bridge (`adb`) indisponíveis.

## Verificações executadas

| Verificação | Resultado | Observação |
| --- | --- | --- |
| `make test` | **Aprovado** | 13 testes passaram: API, autenticação, cadastro de produtos, PWA, Conventional Commits e notas de release. Banco de teste temporário. |
| `python3 -m compileall -q api scripts tests` | **Aprovado** | Módulos Python compilados sem erros em Python 3.13.5. |
| `make -B` | **Aprovado** | Núcleo C23 compilado do zero com `-Wall -Wextra -Wpedantic -Werror`. |
| `make package-linux` | **Aprovado** | Gerado `build/packages/product-manager_1.0.0_amd64.deb`. Metadados e conteúdo do pacote foram inspecionados com `dpkg-deb`. |
| `make package-pwa` | **Aprovado** | Gerado `build/packages/product-manager-pwa-1.0.0.zip`; `unzip -t` confirmou que o arquivo não tem erros de compressão. |
| `git diff --check` | **Aprovado** | Nenhum erro de whitespace no diff. |

Os testes da API foram atualizados para cobrir o contrato atual: as chamadas funcionais usam uma sessão administrativa simulada, e uma verificação separada confirma que `/api/health` exige autenticação.

## Cobertura de plataforma

Os resultados acima são validações feitas no host Debian indicado. O pacote `.deb` foi construído e inspecionado, mas **não foi instalado no sistema**. O pacote RPM não foi construído localmente porque `rpmbuild` não está instalado.

Não houve execução em Windows: este ambiente não tem PowerShell nem runner Windows. O workflow de CI pode construir o instalador `.exe` em um runner Windows, mas isso não foi executado nesta validação. Para Android, foi validado o ZIP do PWA; não houve instalação em dispositivo ou emulador porque `adb`/emulador não está disponível. O PWA deve ser servido por HTTPS para instalação no navegador.

Assim, esta rodada confirma testes automatizados e builds locais disponíveis, mas não equivale a uma homologação nativa em Windows, RPM ou Android. Para repetir as verificações locais:

```bash
make test
python3 -m compileall -q api scripts tests
make -B
make package-linux package-pwa
```

## Container Podman

Validação adicional em **12/10/2026** com Podman rootless:

| Verificação | Resultado | Observação |
| --- | --- | --- |
| `podman build --network=none --format docker -t product-manager-smoke .` | **Aprovado** | A rede de build padrão tentou usar `pasta`, que falhou neste host; o Dockerfile não precisa de rede durante o build. |
| Execução com `--network=slirp4netns` | **Aprovado** | Porta publicada somente no loopback; banco guardado no volume `product-manager-smoke-data`. |
| Healthcheck do container | **Aprovado** | O primeiro probe pode ocorrer antes do servidor aceitar conexões; healthcheck usa intervalo de 5 s e período inicial de 15 s, e o estado final ficou `healthy`. |
| Smoke test HTTP | **Aprovado** | Login servido, bootstrap administrativo fechado após persistência, autenticação concluída e `/api/dashboard` respondeu HTTP 200. |

Para repetir o build rootless neste host, use `podman build --network=none --format docker`. Para iniciar, use a rede `slirp4netns`; a configuração equivalente está no exemplo Podman do README.


## Atualização da CI — correção de rotas e transações (13/10/2026)

A execução da [CI da PR #20](https://github.com/mnl-nox/product_manager/actions/runs/38474512854) terminou com sucesso após a correção do roteamento e do binding SQL de recebimento: **40 testes Python passaram**, assim como os jobs de C23 e Conventional Commits.

A execução da [CI da PR #22](https://github.com/mnl-nox/product_manager/actions/runs/38475015757) confirmou **49 testes Python aprovados**, junto com os jobs C23 e Conventional Commits. A rodada adicionou oito testes de segurança para permissões e CSRF e removeu a duplicação de setup em RH. Isso não substitui testes E2E, restauração de backup, teste de carga, pentest ou homologação nativa. Para a matriz completa e as lacunas restantes, consulte [Plano e relatório completo de QA](qa-plan-and-results.md).
