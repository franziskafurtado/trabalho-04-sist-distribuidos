import pika
import json
from flask import Flask, Response
from queue import Queue
from threading import Thread

app = Flask(__name__)

# Configuração do RabbitMQ
RABBITMQ_HOST = 'localhost'
EXCHANGE_NAME = 'ecommerce'

TOPICS = [
    'Pedidos_Criados',
    'Pagamentos_Aprovados',
    'Pagamentos_Recusados',
    'Pedidos_Enviados'
]

# Fila para armazenar notificações
notification_queue = Queue()

# Inicializando RabbitMQ
def init_rabbitmq():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='topic', durable=True)
    return connection, channel

# Consumindo mensagens de todos os tópicos
def consume_topics():
    connection, channel = init_rabbitmq()

    # Cria e vincula uma fila temporária para consumir todos os tópicos
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    for topic in TOPICS:
        channel.queue_bind(exchange=EXCHANGE_NAME, queue=queue_name, routing_key=topic)

    print("Aguardando eventos de todos os tópicos...")

    def callback(ch, method, properties, body):
        try:
            message = json.loads(body)
            order_id = message.get("order_id")
            status = message.get("status")
            print(f"Notificação recebida: Pedido {order_id}, Status: {status}")

            # Adiciona notificação à fila
            notification_queue.put({"order_id": order_id, "status": status})

            # Confirmação manual
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(f"Erro ao processar mensagem: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=queue_name, on_message_callback=callback)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Encerrando o consumidor...")
        channel.stop_consuming()
        connection.close()

# Rota SSE para notificar o frontend
@app.route('/notifications')
def notifications():
    def generate():
        while True:
            notification = notification_queue.get()
            yield f"data: {json.dumps(notification)}\n\n"

    return Response(generate(), content_type='text/event-stream')

# Inicia o consumidor em uma thread separada
def start_consumer():
    consumer_thread = Thread(target=consume_topics, daemon=True)
    consumer_thread.start()

if __name__ == "__main__":
    start_consumer()
    app.run(debug=True, threaded=True)
