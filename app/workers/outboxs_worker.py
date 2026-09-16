from app.database import SessionLocal
from app.messaging.rabbitmq import create_connection, setup_rabbitmq
from sqlalchemy import select
from app.model import OutboxEvent
import pika
from datetime import datetime, timezone
import time
import json
from app.schemas import PaymentStatus

def process_outbox():
    print("1. Starting outbox worker", flush=True)

    connection = create_connection()
    print("2. RabbitMQ connection created", flush=True)

    channel = connection.channel()
    print("3. RabbitMQ channel created", flush=True)

    setup_rabbitmq(channel)
    print("4. RabbitMQ setup complete", flush=True)

    while True:
        print("5. Checking outbox", flush=True)

        with SessionLocal() as db:
            unpublished_events = db.scalars(
                select(OutboxEvent)
                .where(
                    OutboxEvent.event_type == "PaymentStatusChanged",
                    OutboxEvent.published_at.is_(None)
                )
                .limit(100)
            ).all()

            print(
                f"6. Found {len(unpublished_events)} unpublished events",
                flush=True
            )

            for event in unpublished_events:
                try:
                    print(
                        f"7. Publishing {event.event_id}",
                        flush=True
                    )

                    channel.basic_publish(
                        exchange="payments",
                        routing_key=event.routing_key,
                        body=json.dumps(event.payload),
                    )

                    print(
                        f"8. Published {event.event_id}",
                        flush=True
                    )

                    event.published_at = datetime.now(timezone.utc)
                    db.commit()

                    print(
                        f"9. Marked {event.event_id} as published",
                        flush=True
                    )

                except Exception as e:
                    print(
                        f"ERROR publishing {event.event_id}: "
                        f"{type(e).__name__}: {e}",
                        flush=True
                    )
                    db.rollback()

        time.sleep(5)

if __name__ == "__main__":
    process_outbox()