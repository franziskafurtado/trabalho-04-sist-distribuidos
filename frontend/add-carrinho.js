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
