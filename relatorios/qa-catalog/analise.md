# Análise técnica e decisão de liberação

## Resumo
A aplicação contém API Python, interface Web, SQLite, sessões, permissões por papel, PWA e empacotamento Windows/Linux. A prioridade é tornar testes e evidências reproduzíveis antes de ampliar arquitetura.

## Alterações recentes
- Spec RPM alinhado aos caminhos de documentação preparados pelo script.
- Endpoints /healthz e /readyz adicionados.
- Docker e Render configurados para usar readiness.
- Testes de sucesso e falha de readiness adicionados.
- Documentação de qualidade criada e organizada em relatorios/qa-catalog/.
- Site público: seção de avaliações sem depoimentos fictícios, com CTA para feedback no GitHub; contatos por e-mail e Instagram no site e no rodapé.

## Limitações desta implementação de feedback
- As avaliações ainda não são armazenadas nem moderadas dentro do produto; o CTA direciona para GitHub Discussions. Não há sistema de estrelas, persistência, prevenção de spam ou painel de moderação.
- Os links e a estrutura HTML foram atualizados no repositório, mas ainda precisam de validação visual e funcional no site publicado.

## Módulos integrados e lacunas de validação
- Compras: fornecedores, solicitações, cotações, aprovação por perfil/limite, pedidos e recebimento parcial. O recebimento atualiza estoque e registra `PURCHASE_IN`; testes E2E do fluxo completo ainda são necessários.
- RH: departamentos, colaboradores, ausências com decisão, metadados de documentos e jornada. Acesso restrito ao administrador; não há cálculo de folha.
- Relatórios: indicadores financeiros, contas vencidas, ranking de vendas, registro de vendas, agrupamento por unidade/departamento e exportação de jornada via CSV. Margem bruta e giro contábil exato continuam fora do escopo.
- Estoque: livro-razão append-only para saldo inicial, ajustes manuais, vendas realizadas e recebimentos de compras; devoluções, estornos, transferências e reconciliação física ainda não compõem fluxos completos.

## Bloqueios de aceite
1. CI: o merge do PR #16 teve checks de Python/C23 e jobs de build aprovados. O PR #17 de documentação também passou nos checks Python/C23, validação de commits e builds Windows/Linux/PWA; a publicação do site deve ser acompanhada separadamente.
2. Pacotes: a falha RPM v1.1.3 é histórica; a execução posterior do PR #16 teve os jobs de pacote Windows/Linux/PWA aprovados. Artefatos e instalação real devem ser inspecionados por release.
3. Web E2E: não há evidência completa de fluxos críticos automatizados em navegador.
4. Segurança: cobertura de papéis/CSRF/sessões/exportações precisa ser ampliada; não houve pentest.
5. Dados: backup/restauração não demonstrados; migrações e concorrência precisam de testes.
6. Versionamento: `VERSION` estava em `1.1.0` apesar da release `v1.7.5`; esta branch alinha a versão e altera o workflow para sincronizar futuras tags. O comportamento precisa ser confirmado no próximo ciclo de release.
7. Acessibilidade/desempenho: não há avaliação WCAG nem medições de baseline.
8. Plataformas: builds históricos Windows/PWA não comprovam instalação e upgrade em dispositivos reais.

## Decisão
**ACEITE FINAL: NÃO CONCEDIDO — validação incompleta.** A release só poderá ser aprovada quando os checks e casos obrigatórios passarem no mesmo commit, os artefatos forem verificados e não houver falhas P0/P1 abertas.

## Próximas etapas
1. Concluir CI da branch de auditoria e corrigir falhas sem suprimir testes.
2. Executar workflow de pacotes e verificar DEB, RPM, Windows e PWA.
3. Validar a sincronização de tag e `VERSION` em um ciclo real; manter o changelog alinhado às releases.
4. Ampliar testes de autorização e regressão da API.
5. Adicionar E2E Web para móvel/desktop.
6. Medir baseline de desempenho.
7. Testar backup/restauração e acessibilidade.
8. Executar testes e revisão de segurança dos novos módulos, especialmente transações de compra/recebimento, dados pessoais de RH e baixa de estoque.
9. Só então iniciar análise de ambiente com Podman.

## Evidências históricas
- CI principal: https://github.com/mnl-nox/product_manager/actions/runs/38348153696
- Release: https://github.com/mnl-nox/product_manager/actions/runs/38348153800
- Pacotes v1.1.3: https://github.com/mnl-nox/product_manager/actions/runs/38348165447

Esses runs são históricos e não validam automaticamente commits posteriores.