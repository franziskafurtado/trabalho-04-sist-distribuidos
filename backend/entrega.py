import json
import time
import pika
from threading import Thread

# Configurações do RabbitMQ
RABBITMQ_HOST = 'localhost'
EXCHANGE_NAME = 'ecommerce'
QUEUE_NAME_APPROVED = 'Pagamentos_Aprovados'
QUEUE_NAME_SENT = 'Pedidos_Enviados'

# Configuração para o tópico Pedidos_Enviados
ROUTING_KEY_SENT = 'order.sent'

# Função para configurar RabbitMQ
def setup_rabbitmq():
    """Configura as filas e o exchange no RabbitMQ."""
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='topic', durable=True)

    # Declarar e vincular a fila de Pedidos_Enviados
    channel.queue_declare(queue=QUEUE_NAME_SENT, durable=True)
    channel.queue_bind(exchange=EXCHANGE_NAME, queue=QUEUE_NAME_SENT, routing_key=ROUTING_KEY_SENT)

    connection.close()

# Função para publicar eventos no RabbitMQ
def publish_event(routing_key, event):
    """Publica um evento no RabbitMQ."""
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.basic_publish(
        exchange=EXCHANGE_NAME,
        routing_key=routing_key,
        body=json.dumps(event),
        properties=pika.BasicProperties(content_type='application/json')
    )
    connection.close()

# Função para processar um pedido aprovado
def process_approved_payment(ch, method, properties, body):
    """Processa mensagens do tópico Pagamentos_Aprovados."""
    try:
        event = json.loads(body)
        transaction_id = event.get("transaction_id")
        amount = event.get("amount")
        buyer_info = event.get("buyer_info")

        if not transaction_id or not amount or not buyer_info:
            print(f"Evento inválido recebido: {event}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        print(f"Processando pagamento aprovado para transação {transaction_id}...")

        # Simula a emissão de nota fiscal
        time.sleep(2)
        invoice_id = f"NF-{transaction_id:06d}"  # Exemplo de número de nota fiscal
        print(f"Nota fiscal emitida: {invoice_id}")

        # Simula o envio do pedido
        time.sleep(3)
        print(f"Pedido enviado para {buyer_info['name']}.")

        # Publica o evento no tópico Pedidos_Enviados
        sent_event = {
            "transaction_id": transaction_id,
            "amount": amount,
            "buyer_info": buyer_info,
            "invoice_id": invoice_id,
            "status": "enviado"
        }
        publish_event(ROUTING_KEY_SENT, sent_event)
        print(f"Evento de envio publicado: {sent_event}")

        # Confirma o processamento da mensagem
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"Erro ao processar pagamento aprovado: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag)

# Função para consumir mensagens do RabbitMQ
def consume_events():
    """Consome eventos do tópico Pagamentos_Aprovados."""
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME_APPROVED, durable=True)

    # Vincula a fila ao tópico
    channel.queue_bind(exchange=EXCHANGE_NAME, queue=QUEUE_NAME_APPROVED, routing_key='payment.approved')

    print("Aguardando eventos de Pagamentos_Aprovados...")
    channel.basic_consume(queue=QUEUE_NAME_APPROVED, on_message_callback=process_approved_payment)
    channel.start_consuming()

# Inicializa o microsserviço
if __name__ == "__main__":
    setup_rabbitmq()
    # Consumo de eventos em uma thread separada
    consumer_thread = Thread(target=consume_events)
    consumer_thread.start()
