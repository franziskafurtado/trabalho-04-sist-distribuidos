// Função para buscar os pedidos do usuário
async function buscarPedidos() {
    try {
        const userId = 1; // Substitua pelo ID do usuário, se disponível
        const response = await fetch(`http://localhost:5000/orders/user/${userId}`);
        if (response.ok) {
            const pedidosDict = await response.json(); // Recebe o dicionário de pedidos
            console.log('Pedidos recebidos (dicionário):', pedidosDict);

            // Converte o dicionário em uma lista de pedidos
            const pedidosList = Object.values(pedidosDict);
            console.log('Pedidos convertidos (lista):', pedidosList);

            renderizarPedidos(pedidosList); // Passa a lista para a função de renderização
        } else {
            console.error('Erro ao buscar pedidos:', response.statusText);
            alert('Erro ao buscar pedidos. Tente novamente.');
        }
    } catch (error) {
        console.error('Erro ao buscar pedidos:', error);
        alert('Erro ao buscar pedidos. Tente novamente.');
    }
}

// Função para renderizar os pedidos na página
function renderizarPedidos(pedidos) {
    const secaoPedidos = document.querySelector('#pedidos');
    secaoPedidos.innerHTML = ''; // Limpa o conteúdo atual

    if (pedidos.length === 0) {
        secaoPedidos.innerHTML = '<p>Nenhum pedido encontrado.</p>';
        return;
    }

    pedidos.forEach((pedido) => {
        const total = calcularTotalPedido(pedido.products); // Calcula o total do pedido

        const pedidoDiv = document.createElement('div');
        pedidoDiv.classList.add('pedido');

        // Formata o status do pedido
        let statusClass = '';
        switch (pedido.status) {
            case 'Created':
                statusClass = 'status-criado';
                break;
            case 'Payment Approved':
                statusClass = 'status-aprovado';
                break;
            case 'Payment Rejected':
                statusClass = 'status-recusado';
                break;
            case 'Order Shipped':
                statusClass = 'status-enviado';
                break;
            default:
                statusClass = 'status-criado';
        }

        // Renderiza o pedido
        pedidoDiv.innerHTML = `
            <p><strong>Pedido #${pedido.order_id}</strong></p>
            <p>Data: ${new Date().toLocaleDateString()}</p>
            <p>Total: R$ ${total.toFixed(2).replace('.', ',')}</p>
            <p><strong class="${statusClass}">Status:</strong> ${pedido.status}</p>
            ${pedido.status === 'Created' || pedido.status === 'Payment Approved' ? '<button class="cancelar-pedido">Cancelar Pedido</button>' : ''}
        `;
        secaoPedidos.appendChild(pedidoDiv);
    });

    // Adiciona os eventos de cancelamento
    adicionarEventosCancelarPedido();
}

// Função para calcular o total de um pedido
function calcularTotalPedido(produtos) {
    return produtos.reduce((total, produto) => {
        const preco = parseFloat(produto.preco.replace('R$', '').replace(',', '.')); // Converte o preço para número
        return total + preco * produto.quantidade;
    }, 0);
}

// Função para adicionar eventos de cancelamento
function adicionarEventosCancelarPedido() {
    const botoesCancelar = document.querySelectorAll('.cancelar-pedido');
    botoesCancelar.forEach((botao) => {
        botao.addEventListener('click', async (event) => {
            const pedidoDiv = event.target.closest('.pedido');
            const pedidoId = pedidoDiv.querySelector('strong').textContent.replace('Pedido #', ''); // Extrai o ID do pedido
            console.log(`O usuário clicou em cancelar o ${pedidoId}`);

            try {
                // Envia uma requisição DELETE para o backend
                const response = await fetch(`http://localhost:5000/orders`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        order_id: parseInt(pedidoId), // Converte o ID para número
                    }),
                });

                if (response.ok) {
                    const data = await response.json();
                    console.log('Resposta do servidor:', data);
                    alert(`Pedido #${pedidoId} cancelado com sucesso!`);
                    buscarPedidos(); // Recarrega a lista de pedidos
                } else {
                    const error = await response.json();
                    console.error('Erro ao cancelar o pedido:', error);
                    alert('Erro ao cancelar o pedido. Tente novamente.');
                }
            } catch (error) {
                console.error('Erro ao enviar a requisição:', error);
                alert('Erro ao cancelar o pedido. Tente novamente.');
            }
        });
    });
}

// Inicializa a página
document.addEventListener('DOMContentLoaded', () => {
    buscarPedidos(); // Busca os pedidos ao carregar a página
});