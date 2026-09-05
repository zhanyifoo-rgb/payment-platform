from app.config import settings
import pika

RABBITMQ_URL = settings.rabbitmq_url

params = pika.URLParameters(RABBITMQ_URL)

def create_connection():
    return pika.BlockingConnection(params)

def setup_rabbitmq(channel):
    channel.exchange_declare(exchange="payments", exchange_type="topic", durable = True)

    channel.queue_declare(queue="payment_processing_queue", durable = True)

    channel.queue_bind(exchange="payments",queue="payment_processing_queue",routing_key="payment.created")