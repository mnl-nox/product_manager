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

## Compras (API autenticada)
`POST /api/purchasing/suppliers`, `POST /api/purchasing/requests`, `POST /api/purchasing/quotes`, `POST /api/purchasing/requests/{id}/approve`, `POST /api/purchasing/requests/{id}/order` e `POST /api/purchasing/orders/{id}/receive`. Enviar token CSRF em `X-CSRF-Token`; valores em centavos.

## RH (somente administrador)
`POST /api/hr/departments`, `POST /api/hr/employees`, `POST /api/hr/absences` e `POST /api/hr/absences/{id}/decision`. A API valida datas ISO e matrícula única.

## Relatórios
`GET /api/reports/summary?from=2026-10-01&to=2026-10-31` consulta métricas do período. `POST /api/reports/sales` registra venda com produto, quantidade, preço unitário, data e situação. Nunca use dados reais nos testes.
