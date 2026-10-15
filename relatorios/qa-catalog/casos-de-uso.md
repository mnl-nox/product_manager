# Jornadas de uso

## Web — prioridade principal

### Administrador
1. Entrar pela URL HTTPS e autenticar.
2. Consultar dashboard e catálogo.
3. Criar, editar, desativar e reativar produto.
4. Cadastrar produto com saldo inicial e consultar o histórico de estoque.
5. Registrar venda realizada ou recebimento de compra e confirmar a movimentação correspondente.
6. Tentar excluir produto com histórico e confirmar que a API bloqueia a operação; desativar o produto para preservar rastreabilidade.
7. Gerenciar usuários e permissões.
8. Exportar relatório e encerrar sessão; confirmar que a sessão revogada não acessa endpoints protegidos.

Aceite: dados persistem, erros são claros, autorização é verificada no servidor e os fluxos funcionam em telas móveis e desktop.

### Operação
Consultar estoque, criar/atualizar produtos permitidos e tratar alertas. Confirmar que ações administrativas são negadas.

### Financeiro
Consultar resumo, registrar movimentações permitidas e exportar apenas dados autorizados.

### Leitor
Consultar informações permitidas, tentar escrita e confirmar HTTP 403 sem alteração de dados.

## PWA
Instalar, reabrir, testar conexão perdida e recuperada e atualizar a versão. A aplicação deve sinalizar offline e nunca simular uma gravação concluída sem resposta do servidor.

## Windows e Linux
Instalar em máquina limpa, criar dados sintéticos, reiniciar, atualizar e verificar persistência e inicialização. Testar desinstalação conforme política do pacote.

## Android
Instalar o artefato identificado, testar teclado virtual, rotação, retomada da rede e sessão expirada. O wrapper atual depende da aplicação HTTPS; não assumir cliente offline independente.

## Limites
Usar dados sintéticos. Não assumir isolamento multi-organização, pois ele não foi comprovado em todas as entidades. Podman será avaliado em etapa separada.

## Compras e fornecedores
1. Cadastrar fornecedor.
2. Abrir solicitação com itens e quantidades.
3. Registrar cotações por fornecedor e comparar total/prazo.
4. Enviar a solicitação para aprovação financeira ou administrativa conforme alçada.
5. Emitir pedido com cotação selecionada e registrar recebimentos parciais ou totais.
6. Conferir a atualização do estoque e trilha de auditoria.

## Recursos humanos
1. Cadastrar departamentos e colaboradores.
2. Registrar férias/ausências e decidir aprovação.
3. Registrar apenas metadados de documentos; arquivos não são carregados nesta versão.
4. Quando necessário, registrar minutos de jornada pela API. A aplicação não calcula folha, horas extras ou banco de horas.

## Relatórios e indicadores
1. Selecionar intervalo de datas.
2. Registrar vendas realizadas ou previstas.
3. Consultar resultado, margem de resultado, contas vencidas, previsão simples de caixa, ranking de produtos e agrupamentos mensais/categoria.
4. Validar definições e limitações em `docs/development.md` antes de usar os indicadores para decisões contábeis.
