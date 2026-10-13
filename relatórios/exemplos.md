# Exemplos reproduzíveis

Execute na raiz do repositório, com banco temporário e sem credenciais de produção.

## Python
```bash
python3 -m compileall -q api tests
python3 -m unittest discover -s tests -v
```
Esperado: código de saída zero e nenhum teste com falha/erro. Registrar a contagem real exibida pelo runner.

## Liveness/readiness
```bash
curl -i http://127.0.0.1:8000/healthz
curl -i http://127.0.0.1:8000/readyz
```
Esperado com serviço saudável: HTTP 200 em ambas as rotas. /healthz retorna status ok; /readyz retorna status ready.

A falha de banco deve ser simulada em teste automatizado ou ambiente descartável. Não corromper nem remover banco de usuário para provocar falha.

## Configuração
```bash
grep -n 'healthCheckPath' render.yaml
grep -n 'readyz' Dockerfile
grep -n 'healthz\|readyz' tests/test_api.py
bash -n packaging/linux/build-packages.sh
```
Esses comandos verificam configuração/sintaxe, não substituem o build completo de pacotes.

## Evidência de release
Registrar SHA, URL do workflow, conclusão de cada job, artefatos e tamanhos, versão/tag/changelog, plataforma e data. Nunca publicar cookies, tokens, senhas ou dados pessoais nos logs.