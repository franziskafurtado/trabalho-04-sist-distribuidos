// Função para adicionar o produto ao carrinho
function adicionarAoCarrinho(event) {
    const produto = event.target.closest('.produto');
    const nomeProduto = produto.querySelector('h3').innerText;
    const precoProduto = produto.querySelector('.preco').innerText;
    const imagemProduto = produto.querySelector('img').src;

    const itemCarrinho = {
        nome: nomeProduto,
        preco: precoProduto,
        imagem: imagemProduto,
        quantidade: 1
    };

    console.log(`Produto adicionado ao carrinho: ${nomeProduto}, Preço: ${precoProduto}`);

    let carrinho = JSON.parse(localStorage.getItem('carrinho')) || [];
    carrinho.push(itemCarrinho);

    localStorage.setItem('carrinho', JSON.stringify(carrinho));
}

// Adiciona o evento de clique aos botões de "Adicionar ao carrinho"
const botoesAdicionar = document.querySelectorAll('.adicionar-carrinho');
botoesAdicionar.forEach(button => {
    button.addEventListener('click', adicionarAoCarrinho);
});
