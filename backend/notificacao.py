import pika
import json
from flask import Flask, Response
from queue import Queue
from threading import Thread
import atexit
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuração do RabbitMQ
RABBITMQ_HOST = 'localhost'
EXCHANGE_NAME = 'ecommerce'

# Lista de tópicos específicos
TOPICS = [
    'Pagamentos_Aprovados',
    'Pagamentos_Recusados',
    'Pedidos_Criados',
    'Pedidos_Enviados'
]

# Fila para armazenar notificações
notification_queue = Queue()

# Inicializando RabbitMQ
def init_rabbitmq():
    global CONNECTION, CHANNEL
    CONNECTION = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    CHANNEL = CONNECTION.channel()
    CHANNEL.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='topic', durable=True)
    atexit.register(close_connection)

def close_connection():
    global CONNECTION
    if CONNECTION.is_open:
        CONNECTION.close()
        print("Conexão encerrada.")

def process_events():
    # Declarar uma fila temporária que recebe mensagens dos tópicos especificados
    result = CHANNEL.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    # Vincular a fila aos tópicos específicos
    for topic in TOPICS:
        CHANNEL.queue_bind(exchange=EXCHANGE_NAME, queue=queue_name, routing_key=topic)

    def callback(ch, method, properties, body):
        event = json.loads(body)
        print(f"Evento recebido: {event}")
        notification_queue.put(event)  # Colocar na fila de notificações
        ch.basic_ack(delivery_tag=method.delivery_tag)

    CHANNEL.basic_consume(queue=queue_name, on_message_callback=callback)
    try:
        CHANNEL.start_consuming()
    except KeyboardInterrupt:
        CHANNEL.stop_consuming()

# Rota SSE para notificar o frontend
@app.route('/notifications')
def notifications():
    def generate():
        while True:
            try:
                notification = notification_queue.get()
                yield f"data: {json.dumps(notification)}\n\n"
            except GeneratorExit:  # Cliente desconectado
                print("Cliente desconectado.")
                break

    return Response(generate(), content_type='text/event-stream')

if __name__ == "__main__":
    init_rabbitmq()
    Thread(target=process_events, daemon=True).start()
    app.run(debug=True, threaded=True, host="127.0.0.1", port=8000)
