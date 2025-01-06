import pika
import json
import time
from myRabbit import *

RABBITMQ_HOST = 'localhost'
EXCHANGE_NAME = 'ecommerce'

connection, channel = init_rabbitmq(RABBITMQ_HOST, EXCHANGE_NAME)

if __name__ == "__main__":
    test_events = [
        {"routing_key": "Pedidos_Criados", "message": {"order_id": 1, "status": "criado"}},
        {"routing_key": "Pagamentos_Aprovados", "message": {"order_id": 1, "status": "aprovado"}},
        {"routing_key": "Pagamentos_Recusados", "message": {"order_id": 2, "status": "recusado"}},
        {"routing_key": "Pedidos_Enviados", "message": {"order_id": 1, "status": "enviado"}}
    ]

    for event in test_events:
        print(f"Publicando evento no tópico '{event['routing_key']}'...")      
        publish_message(channel, EXCHANGE_NAME, event["routing_key"], event["message"])
        time.sleep(1)