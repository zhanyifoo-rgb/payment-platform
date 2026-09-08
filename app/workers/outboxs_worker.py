from app.database import SessionLocal
from app.messaging.rabbitmq import channel
from sqlalchemy import select
from app.model import OutboxEvent
import pika
from datetime import datetime, timezone
import time
import json

def process_outbox():
    while True:
        with SessionLocal() as db:
            unpublished_events = db.scalars(select(OutboxEvent).where(OutboxEvent.event_type == "PaymentStatusChanged",OutboxEvent.published_at.is_(None)).limit(100)).all()
            
            for event in unpublished_events:
                try:
                    channel.basic_publish(
                            exchange="payments",
                            routing_key=f"payment.{event.payload['new_status']}",
                            body=json.dumps({
                                "event_id": event.event_id,
                                "event_type": event.event_type,
                                "aggregate_id": event.aggregate_id,
                                "payload" : event.payload
                                }),
                            properties=pika.BasicProperties(
                                delivery_mode=pika.DeliveryMode.Persistent
                            ))
    
                    event.published_at = datetime.now(timezone.utc)

                    db.commit()

                except Exception as e:
                    db.rollback()
                    print(f"Failed to publish event {event.event_id}: {e}")

        time.sleep(5)

if __name__ == "__main__":
    process_outbox()