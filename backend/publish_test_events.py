import pika
import json
import time

RABBITMQ_HOST = 'localhost'
EXCHANGE_NAME = 'ecommerce'

def publish_event(routing_key, message):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='topic', durable=True)
    channel.basic_publish(
        exchange=EXCHANGE_NAME,
        routing_key=routing_key,
        body=json.dumps(message),
        properties=pika.BasicProperties(content_type='application/json')
    )
    connection.close()
    print(f"Mensagem enviada para o tópico '{routing_key}': {message}")
    time.sleep(1)

if __name__ == "__main__":
    test_events = [
        {"routing_key": "Pedidos_Criados", "message": {"order_id": 1, "status": "criado"}},
        {"routing_key": "Pagamentos_Aprovados", "message": {"order_id": 1, "status": "aprovado"}},
        {"routing_key": "Pagamentos_Recusados", "message": {"order_id": 2, "status": "recusado"}},
        {"routing_key": "Pedidos_Enviados", "message": {"order_id": 1, "status": "enviado"}}
    ]

    for event in test_events:
        publish_event(event["routing_key"], event["message"])
