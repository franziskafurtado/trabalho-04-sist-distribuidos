// Função para adicionar o evento de clique nos botões de "Cancelar Pedido"
function adicionarEventosCancelarPedido() {
    // Seleciona todos os botões de cancelar pedido
    const botoesCancelar = document.querySelectorAll('.cancelar-pedido');
    
    // Adiciona um evento de clique para cada botão
    botoesCancelar.forEach((botao) => {
        botao.addEventListener('click', (event) => {
            const pedidoDiv = event.target.closest('.pedido'); // Seleciona o pedido relacionado ao botão
            const pedidoId = pedidoDiv.querySelector('strong').textContent; // Extrai o ID do pedido
            console.log(`O usuário clicou em cancelar o ${pedidoId}`);
        });
    });
}

// Inicializa os eventos quando a página carregar
document.addEventListener('DOMContentLoaded', () => {
    adicionarEventosCancelarPedido();
});
