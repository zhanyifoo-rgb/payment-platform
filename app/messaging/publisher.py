import json
import pika

from app.messaging.rabbitmq import setup_rabbitmq, create_connection


def send_process_transaction_message(transaction_id: str):
    connection = create_connection()
    channel = connection.channel()

    try:
        channel.confirm_delivery()

        setup_rabbitmq(channel)

        channel.basic_publish(
            exchange="transactions",
            routing_key="transaction.created",
            body=json.dumps({
                "transaction_id": transaction_id,
                "retry_count": 0
            }),
            properties=pika.BasicProperties(
                delivery_mode=pika.DeliveryMode.Persistent
            )
        )

    finally:
        connection.close()