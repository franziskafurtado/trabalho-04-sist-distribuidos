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

# Fila para armazenar notificações
notification_queue = Queue()


def teste(msg):
    print('teste:', msg)

def Pagamentos_Aprovados(event):
    notification = f'Pagamento aprovado para o pedido {event["order_id"]}.'
    notification_queue.put(notification)

def Pagamentos_Recusados(event):
    notification = f'Pagamento recusado para o pedido {event["order_id"]}.'
    notification_queue.put(notification)

def Pedidos_Criados(event):
    notification = f'Pedido {event["order_id"]} criado com sucesso.'
    notification_queue.put(notification)

def Pedidos_Enviados(event):    
    notification = f'Pedido {event["order_id"]} enviado com sucesso.'
    notification_queue.put(notification)

# Lista de tópicos específicos
CONSUMER_TOPICS = [
    {'queueName': 'Pagamentos_Aprovados', 'func': Pagamentos_Aprovados},
    {'queueName': 'Pagamentos_Recusados', 'func': Pagamentos_Recusados},
    {'queueName': 'Pedidos_Criados', 'func': Pedidos_Criados},
    {'queueName': 'Pedidos_Enviados', 'func': Pedidos_Enviados},
]

# Rota SSE para notificar o frontend
@app.route('/notifications')
def notifications():
    def generate():
        while True:
            try:
                notification = notification_queue.get()
                print(f'Notificação: {notification}')
                yield f"data: {json.dumps(notification)}\n\n"
            except GeneratorExit:  # Cliente desconectado
                print("Cliente desconectado.")
                break

    return Response(generate(), content_type='text/event-stream')

if __name__ == "__main__":
    connection, channel = init_rabbitmq(RABBITMQ_HOST, EXCHANGE_NAME)
    start_event_consumers(RABBITMQ_HOST, CONSUMER_TOPICS)
    app.run(debug=True, threaded=True, host="127.0.0.1", port=8000)
