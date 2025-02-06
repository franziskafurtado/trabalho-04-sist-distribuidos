from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import random
import threading
import time
import json

app = Flask(__name__)
CORS(app)

# Configuração do Webhook (backend do e-commerce)
PAYMENT_RESULT_URL = "http://localhost:5002/pagamento/return"

# Simulação de Banco de Dados de Transações
transactions = {}

# Simulação de Processamento de Pagamentos
def process_payment(data):
    """Simula o processamento do pagamento e envia uma notificação via Webhook."""
    time.sleep(2)  # Simula o tempo de processamento

    # Determina o status do pagamento aleatoriamente
    status = random.choice(["autorizado", "recusado"])
    # status = "autorizado"
    data["status"] = status
    print(data)
    return data


@app.route('/pagamento/webhook', methods=['POST'])
def pay():
    data = request.json
    result = process_payment(data)
    response = requests.post(PAYMENT_RESULT_URL, json=result)
    return jsonify({"message": "Webhook processado com sucesso"}), 200

if __name__ == "__main__":
    app.run(port=5003, debug=False)
