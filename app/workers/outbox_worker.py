from app.database import SessionLocal
from app.messaging.rabbitmq import create_connection, setup_rabbitmq
from sqlalchemy import select
from app.model import OutboxEvent
import pika
from datetime import datetime, timezone
import time
import json
from app.schemas import TransactionStatus


def process_outbox():
    connection = create_connection()
    channel = connection.channel()

    setup_rabbitmq(channel)

    print("Outbox worker started", flush=True)

    while True:
        with SessionLocal() as db:
            unpublished_events = db.scalars(
                select(OutboxEvent)
                .where(
                    OutboxEvent.event_type == "TransactionStatusChanged",
                    OutboxEvent.published_at.is_(None)
                )
                .limit(100)
            ).all()

            for event in unpublished_events:
                try:
                    new_status = event.payload["new_status"]

                    message = json.dumps({
                        "event_id": event.event_id,
                        "event_type": event.event_type,
                        "aggregate_id": event.aggregate_id,
                        "payload": event.payload
                    })

                    if new_status == TransactionStatus.SUCCEEDED.value:
                        channel.basic_publish(
                            exchange="transactions",
                            routing_key=f"transaction.{new_status}",
                            body=message,
                            properties=pika.BasicProperties(
                                delivery_mode=pika.DeliveryMode.Persistent
                            )
                        )

                    elif new_status == TransactionStatus.FAILED.value:
                        channel.basic_publish(
                            exchange="transactions.dlx",
                            routing_key="transaction.failed",
                            body=message,
                            properties=pika.BasicProperties(
                                delivery_mode=pika.DeliveryMode.Persistent
                            )
                        )

                    event.published_at = datetime.now(timezone.utc)

                    db.commit()

                    print(
                        f"Event {event.event_id} published",
                        flush=True
                    )

                except Exception as e:
                    db.rollback()

                    print(
                        f"Failed to publish event {event.event_id}: {e}",
                        flush=True
                    )

        time.sleep(5)


if __name__ == "__main__":
    process_outbox()