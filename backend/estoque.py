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
    1: {"name": "Teclado Mecânico", "stock": 50},
    2: {"name": "Mouse Gamer", "stock": 30},
    3: {"name": "Monitor Full HD", "stock": 20},
    4: {"name": "Headset", "stock": 60}
}

# Lógica para atualizar o estoque quando um pedido é criado
def handle_order_created(event):
    products = event.get("products", {})
    for product_id, quantity in products.items():
        if product_id in inventory:
            inventory[product_id]["stock"] -= quantity
            inventory[product_id]["stock"] = max(0, inventory[product_id]["stock"])
            print(f"Produto: {inventory[product_id]["name"]} retirado {quantity}, estoque atual {inventory[product_id]["stock"]} ")

# Lógica para atualizar o estoque quando um pedido é excluído
def handle_order_deleted(event):
    products = event.get("products", {})
    for product_id, quantity in products.items():
        if product_id in inventory:
            inventory[product_id]["stock"] += quantity
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
    app.run(debug=True, port=7000)
