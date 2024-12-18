from flask import Flask, jsonify, request
import pika
import json
from threading import Thread

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

# Inicializando RabbitMQ
def init_rabbitmq():
    global CONNECTION, CHANNEL
    CONNECTION = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    CHANNEL = CONNECTION.channel()
    CHANNEL.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='topic', durable=True)
    CHANNEL.queue_declare(queue=QUEUE_NAME_CREATED, durable=True)
    CHANNEL.queue_declare(queue=QUEUE_NAME_DELETED, durable=True)

def close_connection():
    global CONNECTION
    CONNECTION.close()
    print("Conexão encerrada.")

def process_events(queue_name):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)

    def callback(ch, method, properties, body):
        event = json.loads(body)
        print(f"Evento recebido no {queue_name}: {event}")

        if queue_name == QUEUE_NAME_CREATED:
            handle_order_created(event)
        elif queue_name == QUEUE_NAME_DELETED:
            handle_order_deleted(event)

        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=queue_name, on_message_callback=callback)
    channel.start_consuming()  # Inicia o consumo

def start_event_consumers():
    global CHANNEL
    Thread(target=process_events, args=(QUEUE_NAME_CREATED,), daemon=True).start()
    Thread(target=process_events, args=(QUEUE_NAME_DELETED,), daemon=True).start()

# Publicando mensagem para no tópico
def publish_message(routing_key, message):
    global CHANNEL
    CHANNEL.basic_publish(
        exchange=EXCHANGE_NAME,
        routing_key=routing_key,
        body=json.dumps(message),
        properties=pika.BasicProperties(content_type='application/json')
    )

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
    init_rabbitmq()
    start_event_consumers()
    app.run(debug=True, port=7000)
