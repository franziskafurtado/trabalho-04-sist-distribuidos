from flask import Flask, request, jsonify
import requests
import json
import pika
import time

app = Flask(__name__)

# Configuração do RabbitMQ
RABBITMQ_HOST = 'localhost'
EXCHANGE_NAME = 'ecommerce'
TOPIC_APPROVED = 'Pagamentos_Aprovados'
TOPIC_REJECTED = 'Pagamentos_Recusados'

# URL do Webhook do sistema de pagamento externo
PAYMENT_GATEWAY_URL = 'http://external-payment-system.com/webhook'

# Dados simulados para transações (em um cenário real, deve-se usar um banco de dados)
transactions = {}
transaction_id_counter = 1

# Função para inicializar RabbitMQ
def init_rabbitmq():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='topic', durable=True)
    return connection, channel

# Função para publicar mensagem no RabbitMQ
def publish_message(routing_key, message):
    connection, channel = init_rabbitmq()
    channel.basic_publish(
        exchange=EXCHANGE_NAME,
        routing_key=routing_key,
        body=json.dumps(message),
        properties=pika.BasicProperties(content_type='application/json')
    )
    connection.close()

# Função para simular o processamento de pagamento
def process_payment(transaction_id, amount, buyer_info):
    """Simula o processamento de pagamento."""
    time.sleep(5)  # Simula um processamento demorado
    status = "aprovado" if amount <= 1000 else "recusado"  # Regras fictícias para simulação

    # Atualiza o status da transação
    transactions[transaction_id]["status"] = status

    # Notifica o webhook configurado
    send_payment_notification(transaction_id)

# Função para enviar notificação do status do pagamento via Webhook
def send_payment_notification(transaction_id):
    """Envia notificação para o Webhook do sistema de pagamento."""
    transaction = transactions.get(transaction_id)
    if not transaction:
        print(f"Transação {transaction_id} não encontrada.")
        return

    data = {
        "transaction_id": transaction_id,
        "status": transaction["status"],
        "amount": transaction["amount"],
        "buyer_info": transaction["buyer_info"]
    }

    try:
        response = requests.post(PAYMENT_GATEWAY_URL, json=data, timeout=5)
        print(f"Webhook enviado para {PAYMENT_GATEWAY_URL}. Resposta: {response.status_code}")
    except requests.RequestException as e:
        print(f"Erro ao enviar webhook: {e}")

# Endpoint para processar o pagamento
@app.route('/process-payment', methods=['POST'])
def initiate_payment():
    """Endpoint para iniciar o processamento de pagamento."""
    global transaction_id_counter

    data = request.json
    if not data or "amount" not in data or "buyer_info" not in data:
        return jsonify({"error": "Dados inválidos. Informe 'amount' e 'buyer_info'."}), 400

    # Cria uma nova transação
    transaction_id = transaction_id_counter
    transaction_id_counter += 1

    transactions[transaction_id] = {
        "status": "pendente",
        "amount": data["amount"],
        "buyer_info": data["buyer_info"]
    }

    # Inicia o processamento de pagamento em uma thread separada
    process_payment(transaction_id, data["amount"], data["buyer_info"])

    return jsonify({"message": "Pagamento em processamento", "transaction_id": transaction_id}), 200

# Endpoint para receber notificações de pagamento (Webhook)
@app.route('/payment-webhook', methods=['POST'])
def payment_webhook():
    """Endpoint que recebe notificações de pagamento (aprovado ou recusado)."""
    data = request.json
    if not data or "transaction_id" not in data or "status" not in data:
        return jsonify({"error": "Dados inválidos"}), 400

    transaction_id = data["transaction_id"]
    status = data["status"]

    # Valida a transação existente
    transaction = transactions.get(transaction_id)
    if not transaction:
        return jsonify({"error": "Transação não encontrada"}), 404

    # Atualiza o status da transação
    transaction["status"] = status

    # Publica o evento no RabbitMQ de acordo com o status do pagamento
    if status == "aprovado":
        routing_key = TOPIC_APPROVED
    else:
        routing_key = TOPIC_REJECTED

    event = {
        "transaction_id": transaction_id,
        "amount": transaction["amount"],
        "buyer_info": transaction["buyer_info"],
        "status": status
    }
    publish_message(routing_key, event)
    print(f"Evento publicado no tópico '{routing_key}': {event}")

    return jsonify({"message": "Notificação de pagamento processada com sucesso"}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5001)
