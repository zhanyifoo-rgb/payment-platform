from app.messaging.rabbitmq import channel
from sqlalchemy import select
from app.database import SessionLocal
from app.model import Payment,PaymentStatus,PaymentStatusHistory, OutboxEvent
from app.services.payment_service import process_payment,transition_payment, finalize_payment
from uuid import UUID
import pika
import json
from app.Exceptions import TemporaryPaymentError, PermanentPaymentError

def on_message_received(ch,method,properties,body):
    message = json.loads(body)
    payment_id = UUID(message["payment_id"])
    retry_count = message.get("retry_count",0)
    routing_key = method.routing_key

    # claim payment
    with SessionLocal() as db:
        with db.begin():
            # Lock payment row until a transaction finishes
            payment = db.execute(select(Payment).where(Payment.payment_id == payment_id).with_for_update()).scalar_one_or_none()

            if payment is None:
                ch.basic_nack(delivery_tag=method.delivery_tag,requeue=False)
                return

            current_payment_status = payment.payment_status

            if routing_key == "payment.created":
                # Prevent double message sent 
                if current_payment_status != PaymentStatus.PENDING:
                    ch.basic_ack(
                        delivery_tag=method.delivery_tag
                    )
                    return
                
                transition_payment(payment, PaymentStatus.PROCESSING)
                
                new_payment_status_history = PaymentStatusHistory(
                        payment_id = payment_id,
                        old_status = current_payment_status,
                        new_status = payment.payment_status
                    )

                db.add(new_payment_status_history)

                current_payment_status = payment.payment_status

            elif routing_key == "payment.retry":
                # Prevent double message sent 
                if current_payment_status != PaymentStatus.PROCESSING:
                    ch.basic_ack(
                        delivery_tag=method.delivery_tag
                    )
                    return

            else:
                ch.basic_nack(delivery_tag=method.delivery_tag,requeue=False)
                return

    # Process payment
    if current_payment_status == PaymentStatus.PROCESSING:
        try:
            # Process payment
            process_payment(payment_id)

        except TemporaryPaymentError:
            max_retry_count = 3

            retry_queues = {
                0: "payment.retry.2s",
                1: "payment.retry.4s",
                2: "payment.retry.8s",
            }

            if retry_count < max_retry_count:
                try:
                    channel.basic_publish(exchange='payments', routing_key=retry_queues[retry_count],body=json.dumps({
                                    "payment_id": str(payment_id),
                                    "retry_count": retry_count + 1
                                }),
                                properties=pika.BasicProperties(
                                delivery_mode=pika.DeliveryMode.Persistent
                                ))

                except (pika.exceptions.NackError, pika.exceptions.AMQPError):
                    # RabbitMQ rejected the message
                    ch.basic_nack(
                        delivery_tag=method.delivery_tag,
                        requeue=True
                    )
                    return
            else:
                finalize_payment(payment_id,PaymentStatus.FAILED)
                        
            ch.basic_ack(delivery_tag=method.delivery_tag)
                
        except PermanentPaymentError:
            finalize_payment(payment_id,PaymentStatus.FAILED)
                                    
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception:
            ch.basic_nack(delivery_tag=method.delivery_tag,requeue=False)

        else:
            finalize_payment(payment_id,PaymentStatus.SUCCEEDED)
                                
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
channel.queue_declare(queue="payment_processing_queue", durable = True)
channel.basic_consume(queue='payment_processing_queue', auto_ack=False, on_message_callback=on_message_received)
channel.start_consuming()
