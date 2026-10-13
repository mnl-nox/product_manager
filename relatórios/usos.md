# Jornadas de uso

## Web — prioridade principal

### Administrador
1. Entrar pela URL HTTPS e autenticar.
2. Consultar dashboard e catálogo.
3. Criar, editar, desativar e reativar produto.
4. Gerenciar usuários e permissões.
5. Exportar relatório.
6. Encerrar sessão e confirmar que a sessão revogada não acessa endpoints protegidos.

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