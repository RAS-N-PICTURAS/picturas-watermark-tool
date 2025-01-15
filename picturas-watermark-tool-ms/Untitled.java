import json
import logging
import os
import random
import time
import uuid
from datetime import datetime

import pika
from pika.exchange_type import ExchangeType

# Configuração de diretórios e RabbitMQ
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
PICTURAS_SRC_FOLDER = os.getenv("PICTURAS_SRC_FOLDER", "./usage_example/images/src/")
PICTURAS_OUT_FOLDER = os.getenv("PICTURAS_OUT_FOLDER", "./usage_example/images/out/")

# Configuração de logs
LOG_FORMAT = '%(asctime)s [%(levelname)s] %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

LOGGER = logging.getLogger(__name__)

def message_queue_connect():
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    return connection, channel

def message_queue_setup(channel):
    channel.exchange_declare(
        exchange="picturas.tools",
        exchange_type=ExchangeType.direct,
        durable=True,
    )
    channel.queue_declare(queue="results",durable=True)
    channel.queue_bind(
        queue="results",
        exchange="picturas.tools",
        routing_key="results",
    )

    channel.queue_declare(queue="change-brightness-requests", durable=True)
    channel.queue_bind(
        queue="change-brightness-requests",
        exchange="picturas.tools",
        routing_key="requests.change-brightness",
    )

def publish_request_message(channel, routing_key, request_id, procedure, parameters):
    # Construir o payload da mensagem de solicitação
    message = {
        "messageId": request_id,
        "timestamp": datetime.now().isoformat(),
        "procedure": procedure,
        "parameters": parameters,
    }

    # Publicar a mensagem no exchange
    channel.basic_publish(
        exchange="picturas.tools",
        routing_key=routing_key,
        body=json.dumps(message),
    )

    logging.info("Published request '%s' to '%s'", request_id, routing_key)

def publish_mock_requests_forever():
    try:
        while True:
            for file_name in os.listdir(PICTURAS_SRC_FOLDER):
                request_id = str(uuid.uuid4())

                change_brightness_parameters = {
                    "inputImageURI": os.path.join(PICTURAS_SRC_FOLDER, file_name),
                    "outputImageURI": os.path.join(PICTURAS_OUT_FOLDER, file_name),
                    "brightnessFactor": random.uniform(0.5, 2.0)  # Fator de brilho aleatório entre 0.5 e 2.0
                }

                publish_request_message(channel, "requests.change-brightness", request_id, "change_brightness", change_brightness_parameters)
                time.sleep(random.uniform(2, 5))
    finally:
        connection.close()

if __name__ == "__main__":
    connection, channel = message_queue_connect()
    message_queue_setup(channel)  # Configurar as filas
    publish_mock_requests_forever()

