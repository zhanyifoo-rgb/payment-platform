from app.messaging.rabbitmq import create_connection
from sqlalchemy import select
from app.database import SessionLocal
from app.model import (
    Transaction,
    TransactionStatus,
    TransactionStatusHistory,
    User
)
from app.services.transaction_service import (
    process_transaction,
    transition_transaction,
    finalize_transaction
)
from uuid import UUID
import pika
import json
from app.Exceptions import (
    TemporaryTransactionError,
    PermanentTransactionError
)


def on_message_received(ch, method, properties, body):
    message = json.loads(body)

    transaction_id = UUID(message["transaction_id"])
    retry_count = message.get("retry_count", 0)
    routing_key = method.routing_key

    should_ack = False
    should_nack = False

    # Claim transaction
    with SessionLocal() as db:
        with db.begin():
            # Lock transaction row until the database transaction finishes
            transaction = db.execute(
                select(Transaction)
                .where(
                    Transaction.transaction_id == transaction_id
                )
                .with_for_update()
            ).scalar_one_or_none()

            if transaction is None:
                should_nack = True

            else:
                current_transaction_status = (
                    transaction.transaction_status
                )

                if routing_key == "transaction.created":
                    # Prevent duplicate message processing
                    if (
                        current_transaction_status
                        != TransactionStatus.PENDING
                    ):
                        should_ack = True

                    else:
                        transition_transaction(
                            transaction,
                            TransactionStatus.PROCESSING
                        )

                        new_transaction_status_history = (
                            TransactionStatusHistory(
                                transaction_id=transaction_id,
                                old_status=current_transaction_status,
                                new_status=(
                                    transaction.transaction_status
                                )
                            )
                        )

                        db.add(
                            new_transaction_status_history
                        )

                        current_transaction_status = (
                            transaction.transaction_status
                        )

                elif routing_key == "transaction.retry":
                    # Prevent duplicate message processing
                    if (
                        current_transaction_status
                        != TransactionStatus.PROCESSING
                    ):
                        should_ack = True

                else:
                    should_nack = True

    if should_ack:
        ch.basic_ack(
            delivery_tag=method.delivery_tag
        )
        return

    elif should_nack:
        ch.basic_nack(
            delivery_tag=method.delivery_tag,
            requeue=False
        )
        return

    # Process transaction
    if current_transaction_status == TransactionStatus.PROCESSING:

        try:
            # Process transaction
            process_transaction(transaction_id)

        except TemporaryTransactionError:
            max_retry_count = 3

            retry_queues = {
                0: "transaction.retry.2s",
                1: "transaction.retry.4s",
                2: "transaction.retry.8s",
            }

            if retry_count < max_retry_count:
                try:
                    ch.basic_publish(
                        exchange="transactions",
                        routing_key=retry_queues[retry_count],
                        body=json.dumps({
                            "transaction_id": str(transaction_id),
                            "retry_count": retry_count + 1
                        }),
                        properties=pika.BasicProperties(
                            delivery_mode=pika.DeliveryMode.Persistent
                        )
                    )

                except (
                    pika.exceptions.NackError,
                    pika.exceptions.AMQPError
                ):
                    # RabbitMQ rejected the message
                    ch.basic_nack(
                        delivery_tag=method.delivery_tag,
                        requeue=True
                    )
                    return

            else:
                finalize_transaction(
                    transaction_id,
                    TransactionStatus.FAILED
                )

            ch.basic_ack(
                delivery_tag=method.delivery_tag
            )

        except PermanentTransactionError:

            finalize_transaction(
                transaction_id,
                TransactionStatus.FAILED
            )

            ch.basic_ack(
                delivery_tag=method.delivery_tag
            )

        except Exception:

            ch.basic_nack(
                delivery_tag=method.delivery_tag,
                requeue=True
            )

        else:

            finalize_transaction(
                transaction_id,
                TransactionStatus.SUCCEEDED
            )

            ch.basic_ack(
                delivery_tag=method.delivery_tag
            )


def main():
    connection = create_connection()
    channel = connection.channel()

    channel.basic_qos(
        prefetch_count=1
    )

    channel.queue_declare(
        queue="transaction_processing_queue",
        durable=True
    )

    channel.basic_consume(
        queue="transaction_processing_queue",
        auto_ack=False,
        on_message_callback=on_message_received
    )

    channel.start_consuming()


if __name__ == "__main__":
    main()