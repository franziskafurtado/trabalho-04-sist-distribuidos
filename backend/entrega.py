import time
from myRabbit import *

RABBITMQ_HOST = 'localhost'
EXCHANGE_NAME = 'ecommerce'
QUEUE_NAME_SENT = 'Pedidos_Enviados'

def Pagamento_Aprovado(event):
    print(f"Pagamento aprovado para o pedido {event['order_id']}.")
    if gera_nota_fiscal(event):
        processa_entrega(event)
    else:
        print("Erro ao gerar nota fiscal.")

def gera_nota_fiscal(event):
    print(f"Gerando nota fiscal para o pedido {event['order_id']}.")
    return True

def processa_entrega(event):
    print("Enviando pedido...")
    time.sleep(3)
    print(f"Pedido {event['order_id']} enviado com sucesso.")
    publish_message(channel, EXCHANGE_NAME, QUEUE_NAME_SENT, event)

CONSUMER_TOPICS = [
    {'queueName': 'Pagamentos_Aprovados', 'func': Pagamento_Aprovado}
]

if __name__ == "__main__":
    connection, channel = init_rabbitmq(RABBITMQ_HOST, EXCHANGE_NAME)
    start_event_consumers(RABBITMQ_HOST, EXCHANGE_NAME, CONSUMER_TOPICS)
    try:
        while True:
            print("Aguardando eventos...")
            time.sleep(10)
    except KeyboardInterrupt:
        print("Encerrando consumidor de eventos...")
        