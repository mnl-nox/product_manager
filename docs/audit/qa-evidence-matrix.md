# Matriz de evidências de QA

**Estado inicial:** planejamento; nenhuma execução é declarada por este documento.  
**Issue relacionada:** #51.  
**Regra:** marcar como aprovado somente com evidência reproduzível vinculada ao commit revisado.

## Matriz requisito → verificação → evidência

| Área | Verificação mínima | Evidência a registrar | Estado inicial |
|---|---|---|---|
| Compilação Python | `python -m compileall -q api scripts tests` | Saída, versão Python, SHA do commit e resultado | Pendente |
| Testes automatizados | `make test` | Saída completa, duração, ambiente e falhas | Pendente |
| Contratos HTTP e segurança | Testes de sessão, autorização, CSRF, validação e códigos de status | Rotas/papéis cobertos e cenários negativos | Parcial — há testes existentes; inventário completo pendente |
| Estoque | Criar movimento, transição inválida, falha, repetição e rastreabilidade | Saldo antes/depois, ledger e transação | Parcial — constraints têm testes de caracterização em PR separado; fluxos API pendentes |
| Compras e recebimento | Recebimento parcial/total, duplicado, cancelamento e falha no meio da operação | Quantidade pedida/recebida, status e saldo reconciliados | Pendente |
| Financeiro/vendas | Valores positivos, arredondamento, transação, cancelamento/estorno e totais | Registros, centavos, totais e reconciliação | Pendente |
| Migração | Banco vazio e fixtures representativas de versões antigas | Versão antes/depois, contagens, integridade e rollback/recuperação | Pendente |
| Backup/restauração | Backup com WAL tratado corretamente; restaurar em diretório isolado; executar `PRAGMA integrity_check` e `PRAGMA foreign_key_check` | Comandos, saída, hashes, contagens e limitações | Pendente |
| Concorrência/carga | Escritas concorrentes e carga com conjunto de dados sintético documentado | Taxa de erro, latência p50/p95, bloqueios e consistência final | Pendente |
| UI/E2E | Fluxos de produto, compra, venda, financeiro, relatórios e permissões em navegador | Navegador/versão, passos, screenshots, erros e resultado esperado/obtido | Pendente |
| Acessibilidade | Teclado, foco, labels, contraste, mensagens de estado e responsividade | Roteiro por tela, falhas e regressões automatizadas | Pendente |
| Empacotamento | Instalação limpa e atualização em cada plataforma suportada | Sistema operacional, artefato, passos e primeiro acesso | Pendente |
| Dependências/configuração | Dependências, segredos, configuração e logs de produção | Ferramentas/versões, achados, falsos positivos e correções | Pendente |

## Registro obrigatório por execução

Para cada linha, preencher:

- **Commit SHA:**
- **Data/hora e ambiente:**
- **Comando ou roteiro:**
- **Resultado observado:** aprovado / falhou / bloqueado / não aplicável
- **Resumo da saída ou link do artefato:**
- **Falhas e issue de acompanhamento:**
- **Limitações e riscos residuais:**
- **Responsável pela revisão:**

Não incluir tokens, senhas, dados pessoais reais ou cópias de banco de produção nos artefatos. Usar dados sintéticos ou anonimizados.

## Critérios de liberação

1. Os testes rápidos de CI devem passar no commit candidato.
2. Toda falha bloqueante deve estar corrigida ou ter exceção explícita, responsável e justificativa aprovada.
3. Integridade de banco deve ser verificada após migração e restauração; existência de arquivo não é evidência suficiente.
4. Testes caros podem ficar fora da CI rápida, mas devem ter procedimento repetível e execução registrada para o release correspondente.
5. Relatórios precisam distinguir claramente teste executado, teste planejado, teste bloqueado e cobertura desconhecida.
