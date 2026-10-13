# Plano de desempenho

## Escopo
Priorizar carregamento inicial, login, dashboard, listas de produtos/clientes, filtros e exportações. Não executar benchmark de ambiente Podman nesta fase.

## Perfis iniciais
1. Smoke: 1 usuário, fluxos críticos.
2. Concorrência moderada: 5 usuários virtuais com leituras/escritas documentadas.
3. Regressão concorrente: 20 usuários virtuais, somente em ambiente descartável e com dados sintéticos; interromper diante de degradação severa.
4. Catálogo volumoso: conjuntos sintéticos crescentes com contagem registrada.

Esses são perfis iniciais de teste, não alegações de capacidade suportada.

## Medir
- Latência p50/p95/p99 por endpoint.
- Requisições por segundo e taxa de erro.
- HTTP 4xx esperados separados de 5xx.
- Tempo de carregamento Web e tamanho dos recursos.
- CPU, memória, I/O e tamanho do banco.
- Tempo de exportação, tamanho do arquivo e bloqueios SQLite.

## Procedimento
1. Criar banco temporário e dados sintéticos reproduzíveis.
2. Aquecer o serviço e obter baseline sem concorrência.
3. Aumentar carga gradualmente, observando latência e erros.
4. Interromper se houver indisponibilidade, corrupção de dados ou crescimento contínuo de memória.
5. Validar integridade após o teste e remover somente dados temporários.
6. Repetir no mesmo ambiente para comparar commits.

## Critérios
- Zero erro 5xx no perfil nominal definido para aceite.
- Zero perda/corrupção de dados sob concorrência testada.
- Sem vazamento evidente em execução sustentada.
- p95 dentro da meta acordada após baseline; até lá, resultado é não medido.
- Nunca executar carga contra produção.

## Estado
Nenhuma medição foi executada nesta etapa. Latência, throughput e consumo permanecem NÃO MEDIDOS.