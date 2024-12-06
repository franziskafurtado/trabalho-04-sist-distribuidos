// Função para carregar o carrinho do localStorage
function carregarCarrinho() {
    const carrinho = JSON.parse(localStorage.getItem('carrinho')) || [];
    const secaoCarrinho = document.querySelector('#carrinho');
    secaoCarrinho.innerHTML = ''; // Limpa o conteúdo atual

    let total = 0;

    // Renderiza os itens do carrinho
    carrinho.forEach((item, index) => {
        total += parseFloat(item.preco.replace('R$', '').replace(',', '.')) * item.quantidade;

        const itemCarrinho = document.createElement('div');
        itemCarrinho.classList.add('item-carrinho');
        itemCarrinho.innerHTML = `
            <div class="img-produto">
                <img src="${item.imagem}" alt="${item.nome}">
            </div>
            <div class="detalhes-carrinho">
                <h3>${item.nome}</h3>
                <p>${item.preco}</p>
                <p>Quantidade: <input type="number" value="${item.quantidade}" min="1" class="quantidade" data-index="${index}"></p>
                <button class="remover-item" data-index="${index}">Remover</button>
            </div>
        `;
        secaoCarrinho.appendChild(itemCarrinho);
    });

    // Renderiza o total
    const totalDiv = document.createElement('div');
    totalDiv.classList.add('total');
    totalDiv.innerHTML = `
        <h3>Total: R$ ${total.toFixed(2).replace('.', ',')}</h3>
        <button class="finalizar-compra">Realizar Pagamento</button>
    `;
    secaoCarrinho.appendChild(totalDiv);

    // Adiciona evento ao botão "Realizar Pagamento"
    const botaoPagamento = totalDiv.querySelector('.finalizar-compra');
    botaoPagamento.addEventListener('click', () => {
        console.log('Usuário clicou em "Realizar Pagamento"');
    });

    // Garante que os eventos sejam reaplicados
    adicionarEventos();
}

// Função para remover item do carrinho
function removerItem(event) {
    const index = event.target.dataset.index;
    let carrinho = JSON.parse(localStorage.getItem('carrinho')) || [];

    console.log(`Removendo o item de índice ${index}`); // Log para o console

    carrinho.splice(index, 1); // Remove o item pelo índice
    localStorage.setItem('carrinho', JSON.stringify(carrinho)); // Atualiza o localStorage
    carregarCarrinho(); // Recarrega a exibição do carrinho
}

// Função para atualizar a quantidade do item no carrinho
function atualizarQuantidade(event) {
    const index = event.target.dataset.index;
    const novaQuantidade = parseInt(event.target.value);
    let carrinho = JSON.parse(localStorage.getItem('carrinho')) || [];

    if (novaQuantidade > 0) {
        carrinho[index].quantidade = novaQuantidade; // Atualiza a quantidade
        localStorage.setItem('carrinho', JSON.stringify(carrinho)); // Atualiza o localStorage
        carregarCarrinho(); // Recarrega a exibição do carrinho
    }
}

// Adiciona os eventos aos botões e inputs após carregar o carrinho
function adicionarEventos() {
    const botoesRemover = document.querySelectorAll('.remover-item');
    botoesRemover.forEach(botao => botao.addEventListener('click', removerItem));

    const inputsQuantidade = document.querySelectorAll('.quantidade');
    inputsQuantidade.forEach(input => input.addEventListener('change', atualizarQuantidade));
}

// Inicializa a página
document.addEventListener('DOMContentLoaded', () => {
    carregarCarrinho();
    adicionarEventos();
});
