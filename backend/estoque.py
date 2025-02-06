from flask import Flask, jsonify, request
from myRabbit import *

app = Flask(__name__)
 
# Configuração do RabbitMQ
RABBITMQ_HOST = 'localhost'
EXCHANGE_NAME = 'ecommerce'
QUEUE_NAME_CREATED = 'Pedidos_Criados'
QUEUE_NAME_DELETED = 'Pedidos_Excluídos'

# Estoque inicial dos produtos
inventory = { 
    1: {"name": "Teclado Mecânico", "stock": 5},
    2: {"name": "Mouse Gamer", "stock": 3},
    3: {"name": "Monitor Full HD", "stock": 2},
    4: {"name": "Headset", "stock": 3}
}

# Lógica para atualizar o estoque quando um pedido é criado
def handle_order_created(event):
    products = event.get("products", {})
    for item in products:
        for product_id, product_info in inventory.items():
            if product_info["name"] == item["nome"]:
                if product_info["stock"] >= item["quantidade"]:
                    product_info["stock"] -= item["quantidade"]
                    print(f"Produto: {item['nome']} retirado {item['quantidade']}, estoque atual {product_info['stock']} ")
                else:
                    print(f"Estoque insuficiente para {item['nome']}!")

# Lógica para atualizar o estoque quando um pedido é excluído
def handle_order_deleted(event):
    products = event.get("products", {})
    for item in products:
        for product_id, product_info in inventory.items():
            if product_info["name"] == item["nome"]:
                if product_info["stock"] >= item["quantidade"]:
                    product_info["stock"] += item["quantidade"]
                    print(f"Produto: {inventory[product_id]["name"]} adicionado {quantity}, estoque atual {inventory[product_id]["stock"]} ")

CONSUMER_TOPICS = [
    {'queueName': 'Pedidos_Criados', 'func': handle_order_created},
    {'queueName': 'Pedidos_Excluídos', 'func': handle_order_deleted}
]

# Endpoint REST para consultar o estoque
@app.route('/inventory', methods=['GET'])
def get_inventory():
    return jsonify(inventory)

# Endpoint REST para consultar um produto específico
@app.route('/inventory/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = inventory.get(product_id)
    if product:
        return jsonify(product)
    else:
        return jsonify({"error": "Produto não encontrado"}), 404

if __name__ == "__main__":
    connection, channel = init_rabbitmq(RABBITMQ_HOST, EXCHANGE_NAME)
    start_event_consumers(RABBITMQ_HOST, EXCHANGE_NAME, CONSUMER_TOPICS)
    app.run(port=5001)
