from app.config import settings
import pika


RABBITMQ_URL = settings.rabbitmq_url

params = pika.URLParameters(RABBITMQ_URL)


def create_connection():
    return pika.BlockingConnection(params)


def setup_rabbitmq(channel):

    # Main exchange
    channel.exchange_declare(
        exchange="transactions",
        exchange_type="topic",
        durable=True
    )

    # Main transaction processing queue
    channel.queue_declare(
        queue="transaction_processing_queue",
        durable=True
    )

    channel.queue_bind(
        exchange="transactions",
        queue="transaction_processing_queue",
        routing_key="transaction.created"
    )

    # Retry consumer queue
    channel.queue_declare(
        queue="transaction_retry_queue",
        durable=True
    )

    channel.queue_bind(
        exchange="transactions",
        queue="transaction_retry_queue",
        routing_key="transaction.retry"
    )

    # 2 second retry
    channel.queue_declare(
        queue="transaction.retry.2s",
        durable=True,
        arguments={
            "x-message-ttl": 2000,
            "x-dead-letter-exchange": "transactions",
            "x-dead-letter-routing-key": "transaction.retry"
        }
    )

    channel.queue_bind(
        exchange="transactions",
        queue="transaction.retry.2s",
        routing_key="transaction.retry.2s"
    )

    # 4 second retry
    channel.queue_declare(
        queue="transaction.retry.4s",
        durable=True,
        arguments={
            "x-message-ttl": 4000,
            "x-dead-letter-exchange": "transactions",
            "x-dead-letter-routing-key": "transaction.retry"
        }
    )

    channel.queue_bind(
        exchange="transactions",
        queue="transaction.retry.4s",
        routing_key="transaction.retry.4s"
    )

    # 8 second retry
    channel.queue_declare(
        queue="transaction.retry.8s",
        durable=True,
        arguments={
            "x-message-ttl": 8000,
            "x-dead-letter-exchange": "transactions",
            "x-dead-letter-routing-key": "transaction.retry"
        }
    )

    channel.queue_bind(
        exchange="transactions",
        queue="transaction.retry.8s",
        routing_key="transaction.retry.8s"
    )

    # Dead-letter exchange
    channel.exchange_declare(
        exchange="transactions.dlx",
        exchange_type="topic",
        durable=True
    )

    # Dead-letter queue
    channel.queue_declare(
        queue="transaction.dlq",
        durable=True
    )

    channel.queue_bind(
        queue="transaction.dlq",
        exchange="transactions.dlx",
        routing_key="transaction.failed"
    )