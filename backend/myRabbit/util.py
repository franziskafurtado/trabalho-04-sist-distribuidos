import pika
import atexit
import json
from threading import Thread

def init_rabbitmq(host, exchange):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
    channel = connection.channel()
    channel.exchange_declare(exchange= exchange, exchange_type='topic', durable=True)
    atexit.register(close_connection,connection)
    return connection, channel

def close_connection(connection):
    connection.close()
    print("Conexão encerrada.")

def publish_message(channel, exchange, routing_key, message):
    channel.basic_publish(
        exchange=exchange,
        routing_key=routing_key,
        body=json.dumps(message),
        properties=pika.BasicProperties(content_type='application/json')
    )
    print(f"Mensagem enviada para o tópico '{routing_key}': {message}")

def process_events(host, queue_name, func_callback):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)

    def callback(ch, method, properties, body):
        event = json.loads(body)
        print(f"Evento recebido no {queue_name}: {event}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return func_callback(event)

    channel.basic_consume(queue=queue_name, on_message_callback=callback)
    channel.start_consuming()  # Inicia o consumo

def start_event_consumers(host,topics):
    for topic in topics:
        Thread(target=process_events, args=(host, topic['queueName'], topic['func']), daemon=True).start()