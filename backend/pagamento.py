from flask import Flask, request, jsonify
import requests
from myRabbit import *

app = Flask(__name__)

# Configuração do RabbitMQ
RABBITMQ_HOST = 'localhost'
EXCHANGE_NAME = 'ecommerce'
QUEUE_NAME_APPROVED = 'Pagamentos_Aprovados'
QUEUE_NAME_REJECTED = 'Pagamentos_Recusados'
PAYMENT_WEBHOOK_URL = "http://localhost:5003/pagamento/webhook"
AUX = True

def processa_pedido_criado(event):
    print(f"Enviando o pedido {event} para aprovação")
    response = requests.post(PAYMENT_WEBHOOK_URL, json = event)
    

CONSUMER_TOPICS = [
    {'queueName': 'Pedidos_Criados', 'func': processa_pedido_criado}
]

@app.route('/pagamento/return', methods=['POST'])
def webhook():
    response = request.json
    print(f"Retorno:{response['status']}")
    if response['status'] == "autorizado":
        publish_message(channel, EXCHANGE_NAME, QUEUE_NAME_APPROVED, response)
    else:
        publish_message(channel, EXCHANGE_NAME, QUEUE_NAME_REJECTED, response)
        
    return jsonify({"message": "Webhook processado com sucesso"}), 200

if __name__ == "__main__":
    connection, channel = init_rabbitmq(RABBITMQ_HOST, EXCHANGE_NAME)
    start_event_consumers(RABBITMQ_HOST, EXCHANGE_NAME, CONSUMER_TOPICS)
    app.run(debug=False, port=5002)
