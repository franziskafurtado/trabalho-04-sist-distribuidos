from flask import Flask, request, jsonify
from myRabbit import *

app = Flask(__name__)

# Configuração do RabbitMQ
RABBITMQ_HOST = 'localhost'
EXCHANGE_NAME = 'ecommerce'
QUEUE_NAME_APPROVED = 'Pagamentos_Aprovados'
QUEUE_NAME_REJECTED = 'Pagamentos_Recusados'
AUX = True

def processa_pedido_criado(event):
    print("Pedido criado")
    if AUX:
        print("Pagamento aprovado")
        AUX = False
        publish_message(channel, EXCHANGE_NAME, QUEUE_NAME_APPROVED, event)
    else:
        print("Pagamento recusado")
        AUX = True
        publish_message(channel, EXCHANGE_NAME, QUEUE_NAME_REJECTED, event)

CONSUMER_TOPICS = [
    {'queueName': 'Pedidos_Criados', 'func': processa_pedido_criado}
]

if __name__ == "__main__":
    connection, channel = init_rabbitmq(RABBITMQ_HOST, EXCHANGE_NAME)
    start_event_consumers(RABBITMQ_HOST, EXCHANGE_NAME, CONSUMER_TOPICS)
    app.run(debug=True, port=5001)
