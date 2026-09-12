from app.config import settings
import pika

RABBITMQ_URL = settings.rabbitmq_url

params = pika.URLParameters(RABBITMQ_URL)

def create_connection():
    return pika.BlockingConnection(params)

def setup_rabbitmq(channel):
        # Main exchange
    channel.exchange_declare(
        exchange="payments",
        exchange_type="topic",
        durable=True
    )

    # Main payment processing queue
    channel.queue_declare(
        queue="payment_processing_queue",
        durable=True
    )

    channel.queue_bind(
        exchange="payments",
        queue="payment_processing_queue",
        routing_key="payment.created"
    )

    # Retry consumer queue
    channel.queue_declare(
        queue="payment_retry_queue",
        durable=True
    )

    channel.queue_bind(
        exchange="payments",
        queue="payment_retry_queue",
        routing_key="payment.retry"
    )

    # 2 second retry
    channel.queue_declare(
        queue="payment.retry.2s",
        durable=True,
        arguments={
            "x-message-ttl": 2000,
            "x-dead-letter-exchange": "payments",
            "x-dead-letter-routing-key": "payment.retry"
        }
    )

    channel.queue_bind(
        exchange="payments",
        queue="payment.retry.2s",
        routing_key="payment.retry.2s"
    )

    # 4 second retry
    channel.queue_declare(
        queue="payment.retry.4s",
        durable=True,
        arguments={
            "x-message-ttl": 4000,
            "x-dead-letter-exchange": "payments",
            "x-dead-letter-routing-key": "payment.retry"
        }
    )

    channel.queue_bind(
        exchange="payments",
        queue="payment.retry.4s",
        routing_key="payment.retry.4s"
    )

    # 8 second retry
    channel.queue_declare(
        queue="payment.retry.8s",
        durable=True,
        arguments={
            "x-message-ttl": 8000,
            "x-dead-letter-exchange": "payments",
            "x-dead-letter-routing-key": "payment.retry"
        }
    )

    channel.queue_bind(
        exchange="payments",
        queue="payment.retry.8s",
        routing_key="payment.retry.8s"
    )

    # Dead-letter exchange
    channel.exchange_declare(
        exchange="payments.dlx",
        exchange_type="topic",
        durable=True
    )

    # Dead-letter Queue
    channel.queue_declare(
        queue="payment.dlq",
        durable=True
    )

    channel.queue_bind(
        queue="payment.dlq",
        exchange="payments.dlx",
        routing_key="payment.failed"
    )

channel = create_connection().channel()
channel.confirm_delivery()
setup_rabbitmq(channel)