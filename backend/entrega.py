import json
import time
import pika
from threading import Thread

RABBITMQ_HOST = 'localhost'
EXCHANGE_NAME = 'ecommerce'
QUEUE_NAME_APPROVED = 'Pagamentos_Aprovados'
QUEUE_NAME_SENT = 'Pedidos_Enviados'

def publish_message(channel, routing_key, message):
    channel.basic_publish(
        exchange=EXCHANGE_NAME,
        routing_key=routing_key,
        body=json.dumps(message),
        properties=pika.BasicProperties(content_type='application/json')
    )

def process_approved_payment(ch, method, properties, event, channel):
    order_id = event.get("order_id")
    status = event.get("status")

    if not order_id or status != "aprovado":
        print(f"Evento inválido ou status não aprovado: {event}")
        ch.basic_ack(delivery_tag=method.delivery_tag)  # Marca como processado, mas inválido
        return

    print(f"Processando pagamento aprovado para o pedido {order_id}...")

    # Simula a emissão de nota fiscal
    time.sleep(2)
    invoice_id = f"NF-{order_id:06d}" if str(order_id).isdigit() else f"NF-{order_id}"
    print(f"Nota fiscal emitida: {invoice_id}")

    # Simula o envio do pedido
    time.sleep(3)
    print(f"Pedido enviado para o pedido {order_id}.")

    # Publica o evento no tópico `Pedidos_Enviados`
    sent_event = {
        "order_id": order_id,
        "invoice_id": invoice_id,
        "status": "enviado"
    }
    publish_message(channel, QUEUE_NAME_SENT, sent_event)
    print(f"Evento de envio publicado: {sent_event}")

    # Confirma o processamento da mensagem
    ch.basic_ack(delivery_tag=method.delivery_tag)

def teste():
    print('teste')  # Função de teste


if __name__ == "__main__":
    init_rabbitmq()
    start_event_consumers()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        close_connection()
