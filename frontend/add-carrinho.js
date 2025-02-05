let inventory = {};

// Função para adicionar o produto ao carrinho
function adicionarAoCarrinho(event) {
    const produto = event.target.closest('.produto');
    const nomeProduto = produto.querySelector('h3').innerText;
    const precoProduto = produto.querySelector('.preco').innerText;
    const imagemProduto = produto.querySelector('img').src;

    let carrinho = JSON.parse(localStorage.getItem('carrinho')) || [];

    // Verifica se o produto já está no carrinho
    const itemExistente = carrinho.find(item => item.nome === nomeProduto);

    if (itemExistente) {
        // Incrementa a quantidade se o produto já estiver no carrinho
        itemExistente.quantidade += 1;
    } else {
        // Adiciona o produto ao carrinho se for novo
        const itemCarrinho = {
            nome: nomeProduto,
            preco: precoProduto,
            imagem: imagemProduto,
            quantidade: 1
        };
        carrinho.push(itemCarrinho);
    }

    // Atualiza o localStorage
    localStorage.setItem('carrinho', JSON.stringify(carrinho));
    console.log(`Produto adicionado ao carrinho: ${nomeProduto}, Preço: ${precoProduto}`);
}

// Adiciona o evento de clique aos botões de "Adicionar ao carrinho"
const botoesAdicionar = document.querySelectorAll('.adicionar-carrinho');
botoesAdicionar.forEach(button => {
    button.addEventListener('click', adicionarAoCarrinho);
});

// Função para buscar o estoque de todos os produtos
async function fetchInventory() {
    try {
        const response = await fetch('http://localhost:5000/inventory');
        if (response.ok) {
            inventory = await response.json();
            console.log('Estoque carregado:', inventory);
        } else {
            console.error('Erro ao buscar estoque:', response.statusText);
            alert('Erro ao carregar o estoque. Tente novamente.');
        }
    } catch (error) {
        console.error('Erro ao buscar estoque:', error);
        alert('Erro ao carregar o estoque. Tente novamente.');
    }
}

// Função para verificar o estoque antes de adicionar ao carrinho
function checkStock(productId, quantity) {
    const availableStock = inventory[productId] || 0;
    if (availableStock >= quantity) {
        return true; // Estoque suficiente
    } else {
        alert('Estoque insuficiente para este produto.');
        return false; // Estoque insuficiente
    }
}

// Exemplo de uso ao adicionar um produto ao carrinho
function addToCart(productId, quantity) {
    if (checkStock(productId, quantity)) {
        // Lógica para adicionar ao carrinho
        console.log(`Produto ${productId} adicionado ao carrinho.`);
    }
}

// Carrega o estoque ao abrir a página
document.addEventListener('DOMContentLoaded', () => {
    fetchInventory();
});