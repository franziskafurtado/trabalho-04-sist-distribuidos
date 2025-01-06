import json
from flask import Flask, Response
from queue import Queue
from flask_cors import CORS
from myRabbit import *

app = Flask(__name__)
CORS(app)

# Configuração do RabbitMQ
RABBITMQ_HOST = 'localhost'
EXCHANGE_NAME = 'ecommerce'

def teste(msg):
    print('teste:', msg)

# Lista de tópicos específicos
CONSUMER_TOPICS = [
    {'queueName': 'Pagamentos_Aprovados', 'func': teste},
    {'queueName': 'Pagamentos_Recusados', 'func': teste},
    {'queueName': 'Pedidos_Criados', 'func': teste},
    {'queueName': 'Pedidos_Enviados', 'func': teste},
]

# Fila para armazenar notificações
notification_queue = Queue()


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
    connection, channel = init_rabbitmq(RABBITMQ_HOST, EXCHANGE_NAME)
    start_event_consumers(RABBITMQ_HOST, CONSUMER_TOPICS)
    app.run(debug=True, threaded=True, host="127.0.0.1", port=8000)
