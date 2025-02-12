from flask import Flask, request, jsonify, Response, render_template, send_from_directory
from queue import Queue
from myRabbit import *
import requests
from flask_cors import CORS

app = Flask(__name__, static_folder="../frontend", template_folder="../frontend")
CORS(app)

# Configuração do RabbitMQ
RABBITMQ_HOST = 'localhost'
EXCHANGE_NAME = 'ecommerce'
QUEUE_NAME_CREATED = 'Pedidos_Criados'
QUEUE_NAME_DELETED = 'Pedidos_Excluídos'
QUEUE_NAME_APPROVED = 'Pagamentos_Aprovados'
QUEUE_NAME_REJECTED = 'Pagamentos_Recusados'
INVENTORY_URL = "http://localhost:5001/inventory"

# Simulando banco de dados em memória
products = {
    1: {"name": "Teclado Mecânico", "price": 199.75},
    2: {"name": "Mouse Gamer", "price": 879.00},
    3: {"name": "Monitor Full HD", "price": 1450.00},
    4: {"name": "Headset", "price": 110.00}
}
carts = {}  # {user_id: {product_id: quantity}}
orders = {}  # {order_id: {user_id, products, status}}

sse_queue = Queue()

# 🔥 Atualiza o status quando o pagamento é processado
def Pagamentos_Aprovados(event):
    order_id = event["order_id"]
    if order_id in orders:
        orders[order_id]["status"] = "Autorizado"
        print(f'✅ Pagamento aprovado para o pedido {order_id}. Status atualizado.')

def Pagamentos_Recusados(event):
    order_id = event["order_id"]
    if order_id in orders:
        orders[order_id]["status"] = "Recusado"
        print(f'❌ Pagamento recusado para o pedido {order_id}. Status atualizado.')

def Pedidos_Enviados(event):
    order_id = event["order_id"]
    if order_id in orders:
        orders[order_id]["status"] = "Enviado"
        print(f'📦 Pedido {order_id} enviado com sucesso. Status atualizado.')

# Lista de tópicos específicos
CONSUMER_TOPICS = [
    {'queueName': QUEUE_NAME_APPROVED, 'func': Pagamentos_Aprovados},
    {'queueName': QUEUE_NAME_REJECTED, 'func': Pagamentos_Recusados},
    {'queueName': 'Pedidos_Enviados', 'func': Pedidos_Enviados},
]

# 📌 Rotas da API
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/products', methods=['GET'])
def get_products():
    return jsonify(products)

@app.route('/inventory', methods=['GET'])
def get_inventory():
    try:
        response = requests.get(INVENTORY_URL)
        response.raise_for_status()
        inventory = response.json()
        return jsonify(inventory)
    except requests.RequestException as e:
        return jsonify({"error": f"Erro ao consultar o estoque: {e}"}), 500

# 🛒 Gerenciamento de pedidos
@app.route('/orders', methods=['POST', 'DELETE'])
def manage_orders():
    if request.method == 'POST':
        data = request.json
        user_id = data['user_id']
        cart = data.get('cart', [])
        order_id = len(orders) + 1
        order = {
            "order_id": order_id,
            "user_id": user_id,
            "products": cart,
            "status": "Criado"
        }
        orders[order_id] = order

        # Publica evento para Pedidos_Criados
        publish_message(channel, EXCHANGE_NAME, QUEUE_NAME_CREATED, {"order_id": order_id, **order})
        print(f"📦 Pedido criado: {order}")

        # Limpa o carrinho do usuário
        carts[user_id] = {}
        return jsonify(order), 201

    elif request.method == 'DELETE':
        data = request.json
        order_id = data['order_id']

        if order_id in orders:
            order = orders.pop(order_id)
            publish_message(channel, EXCHANGE_NAME, QUEUE_NAME_DELETED, {"order_id": order_id, **order})
            print(f"🗑 Pedido {order_id} deletado.")
            return jsonify({"message": "Order deleted"}), 200
        else:
            return jsonify({"error": "Order not found"}), 404

@app.route('/orders/user/<int:user_id>', methods=['GET'])
def get_orders_by_user(user_id):
    user_orders = {k: v for k, v in orders.items() if v["user_id"] == user_id}
    return jsonify(user_orders)

@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    if order_id in orders:
        return jsonify(orders[order_id])
    return jsonify({"error": "Pedido não encontrado"}), 404

# ✅ NOVA ROTA: Atualizar status do pedido
@app.route('/orders/update', methods=['POST'])
def update_order_status():
    data = request.json
    order_id = data.get("order_id")
    status = data.get("status")

    if order_id in orders:
        orders[order_id]["status"] = status
        print(f"🔄 Pedido {order_id} atualizado para {status}.")
        return jsonify({"message": "Status atualizado", "order": orders[order_id]}), 200
    else:
        print(f"⚠ Pedido {order_id} não encontrado!")
        return jsonify({"error": "Pedido não encontrado"}), 404

# Função para buscar estoque
def fetch_inventory(id=None):
    url = f"{INVENTORY_URL}/{id}" if id else INVENTORY_URL
    try:
        response = requests.get(url)
        if response.status_code == 200:
            inventory = response.json()
            print("📦 Estoque:", inventory)
        else:
            print(f"Erro: Status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao conectar ao estoque: {e}")

# 🔄 Inicialização do RabbitMQ
if __name__ == '__main__':
    connection, channel = init_rabbitmq(RABBITMQ_HOST, EXCHANGE_NAME)
    start_event_consumers(RABBITMQ_HOST, EXCHANGE_NAME, CONSUMER_TOPICS)
    fetch_inventory()
    app.run(debug=True, threaded=True, port=5000)
