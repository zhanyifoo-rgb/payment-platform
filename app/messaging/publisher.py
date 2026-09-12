from app.messaging.rabbitmq import channel
import json
import pika

def send_process_payment_message(payment_id: str):
    # all payments are succeed for now
    channel.basic_publish(
        exchange="payments",
        routing_key="payment.created",
        body=json.dumps({
            "payment_id": payment_id,
            "retry_count": 0
        }),
        properties=pika.BasicProperties(
        delivery_mode=pika.DeliveryMode.Persistent
        )
    )