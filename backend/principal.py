from flask import Flask, request, jsonify, Response, render_template, send_from_directory
import pika
import json
from threading import Thread
from queue import Queue
import os
import atexit
from myRabbit import *

app = Flask(__name__, static_folder="../frontend", template_folder="../frontend")

# Configuração do RabbitMQ
RABBITMQ_HOST = 'localhost'
EXCHANGE_NAME = 'ecommerce'
QUEUE_NAME_CREATED = 'Pedidos_Criados'
QUEUE_NAME_DELETED = 'Pedidos_Excluídos'

products = {
    1: {"name": "Teclado Mecânico", "price": 199.75},
    2: {"name": "Mouse Gamer", "price": 879.00},
    3: {"name": "Monitor Full HD", "price": 1450.00},
    4: {"name": "Headset", "price": 110.00}
}
carts = {}  # {user_id: {product_id: quantity}}
orders = {}  # {order_id: {user_id, products, status}}

sse_queue = Queue()

# Rota para servir a página inicial
@app.route('/')
def index():
    return render_template('index.html')

# Rota para servir arquivos estáticos
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/products', methods=['GET'])
def get_products():
    return jsonify(products)

@app.route('/cart/<int:user_id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def manage_cart(user_id):
    if request.method == 'GET':
        return jsonify(carts.get(user_id, {}))

    data = request.json
    product_id = data['product_id']
    quantity = data.get('quantity', 1)

    if request.method == 'POST':
        carts.setdefault(user_id, {}).setdefault(product_id, 0)
        carts[user_id][product_id] += quantity
    elif request.method == 'PUT':
        if user_id in carts and product_id in carts[user_id]:
            carts[user_id][product_id] = quantity
    elif request.method == 'DELETE':
        if user_id in carts and product_id in carts[user_id]:
            del carts[user_id][product_id]

    return jsonify(carts.get(user_id, {}))

@app.route('/orders', methods=['POST', 'DELETE'])
def manage_orders():
    if request.method == 'POST':
        data = request.json
        user_id = data['user_id']
        order_id = len(orders) + 1
        order = {
            "user_id": user_id,
            "products": carts.get(user_id, {}),
            "status": "Created"
        }
        orders[order_id] = order

        # Publica evento para Pedidos_Criados
        publish_message(channel, f'{QUEUE_NAME_CREATED}', {"order_id": order_id, **order})

        # Adiciona à fila SSE
        sse_queue.put({"event": "order_created", "data": {"order_id": order_id, **order}})

        # Limpa o carrinho
        carts[user_id] = {}
        return jsonify(order)

    elif request.method == 'DELETE':
        data = request.json
        order_id = data['order_id']

        if order_id in orders:
            order = orders.pop(order_id)

            # Publica o evento para Pedidos_Excluídos
            publish_message(channel ,f'{QUEUE_NAME_DELETED}', {"order_id": order_id, **order})

            # Adiciona à fila SSE
            sse_queue.put({"event": "order_deleted", "data": {"order_id": order_id, **order}})

            return jsonify({"message": "Order deleted"})
        else:
            return jsonify({"error": "Order not found"}), 404

@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = orders.get(order_id)
    if order:
        return jsonify(order)
    else:
        return jsonify({"error": "Pedido não encontrado"}), 404

@app.route('/save-cart', methods=['POST'])
def save_cart():
    data = request.json  # Espera receber os dados do carrinho no corpo da requisição
    if not data:
        return jsonify({"error": "Nenhum dado recebido"}), 400

    # Aqui você pode processar os dados do carrinho
    user_id = data.get("user_id")
    cart = data.get("cart")  # Dados do carrinho no formato JSON

    if user_id and cart:
        carts[user_id] = cart
        return jsonify({"message": "Carrinho salvo com sucesso"}), 200
    else:
        return jsonify({"error": "Dados incompletos"}), 400

if __name__ == '__main__':
    connection, channel = init_rabbitmq(RABBITMQ_HOST, EXCHANGE_NAME)
    app.run(debug=True, threaded=True, port=5000)

    
