# Resultado dos testes

Registro da validação local da versão **1.0.0**, executada em **12/10/2026**.

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
