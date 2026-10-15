# Protocolo de execução

## Pré-condições
- Checkout do commit candidato exato.
- Ambiente isolado, Python e dependências compatíveis com CI.
- Banco temporário e dados sintéticos.
- Segredos somente por ambiente seguro.
- Nenhuma análise Podman nesta fase.

## Sequência obrigatória
1. Revisar diff e sintaxe dos workflows.
2. Compilar os módulos Python.
3. Executar testes unitários e integrados.
4. Executar lint, análise de dependências e checks configurados.
5. Testar contrato API, autenticação, CSRF e papéis.
6. Executar E2E Web em viewport móvel e desktop.
7. Testar cache e atualização PWA.
8. Gerar e validar DEB, RPM, Windows e PWA.
9. Validar /healthz e /readyz no build e no ambiente de teste.
10. Conferir versão, tag, changelog e artefatos.
11. Anexar evidências e revisar defeitos abertos.

## Política de falha
Não ignorar testes, remover assertions, converter falhas em sucesso nem usar continue-on-error para contornar erros. Corrigir a causa raiz e adicionar teste de regressão. Reexecutar o conjunto afetado e depois o pipeline completo no commit final. Ambiente indisponível deve ser BLOQUEADO/NÃO EXECUTADO, nunca APROVADO. Falha P0/P1 bloqueia release.

## Registro
| Campo | Valor |
|---|---|
| Commit | PENDENTE |
| Branch/tag | PENDENTE |
| URL CI | PENDENTE |
| Testes passados/falhos/ignorados | PENDENTE |
| Builds e artefatos | PENDENTE |
| Resultado final | NÃO EXECUTADO |
| Data/ambiente | PENDENTE |

## Definição de pronto
Todos os checks obrigatórios e casos P0/P1 devem passar no mesmo commit. Artefatos devem existir e ser inspecionados. Nenhuma falha conhecida pode ficar sem decisão documentada. Testes verdes não provam ausência matemática de bugs.