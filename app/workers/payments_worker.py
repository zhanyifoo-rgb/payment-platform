from app.main import channel
from app.database import get_db
from fastapi import Depends,HTTPException
from sqlalchemy import select
from app.database import SessionLocal
from app.model import Payment,PaymentStatus,PaymentStatusHistory
from app.routers.payments import transition_payment
import random
import time
from uuid import UUID
import pika

def on_message_received(ch,method,properties,body):
    payment_id = UUID(body.decode("utf-8"))

    db = SessionLocal()

    try:
        # Lock payment row until a transaction finishes
        payment = db.execute(select(Payment).where(Payment.payment_id == payment_id).with_for_update()).scalar_one_or_none()

        if payment is None:
            ch.basic_nack(delivery_tag=method.delivery_tag,requeue=False)
            return

        old_status = payment.payment_status

        processed = False

        if old_status == PaymentStatus.PENDING:
            transition_payment(payment, PaymentStatus.PROCESSING)

            new_payment_status_history = PaymentStatusHistory(
                    payment_id = payment_id,
                    old_status = old_status,
                    new_status = payment.payment_status
                )

            db.add(new_payment_status_history)

            # wait for processing time
            time.sleep(random.randint(1,4))

            old_status = payment.payment_status
            transition_payment(payment, PaymentStatus.SUCCEEDED)
            
            new_payment_status_history = PaymentStatusHistory(
                    payment_id = payment_id,
                    old_status = old_status,
                    new_status = payment.payment_status
                )

            db.add(new_payment_status_history)

            db.commit()
            processed = True

        if processed:
            ch.basic_publish(
                        exchange="payments",
                        routing_key="payment.succeeded",
                        body=str(payment_id),
                        properties=pika.BasicProperties(
                            delivery_mode=pika.DeliveryMode.Persistent
                        )
                        )
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except Exception:
        db.rollback()
        ch.basic_nack(delivery_tag=method.delivery_tag,requeue=False)

    finally:
        db.close()

channel.basic_consume(queue='payment_processing_queue', auto_ack=False,on_message_callback=on_message_received)
channel.start_consuming()
