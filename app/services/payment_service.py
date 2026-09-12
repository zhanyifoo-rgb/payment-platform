from app.schemas import PaymentStatus
from app.model import Payment, PaymentStatusHistory, OutboxEvent
import random
import time
from app.database import SessionLocal
from app.Exceptions import TemporaryPaymentError, PermanentPaymentError
from sqlalchemy import select

ALLOWED_TRANSITIONS = {
    PaymentStatus.PENDING : {PaymentStatus.PROCESSING,PaymentStatus.CANCELLED},
    PaymentStatus.PROCESSING : {PaymentStatus.SUCCEEDED,PaymentStatus.FAILED},
    PaymentStatus.SUCCEEDED : set(),
    PaymentStatus.FAILED : set(),
    PaymentStatus.CANCELLED : set()
}

def transition_payment(payment: Payment,new_status: PaymentStatus):
    allowed = ALLOWED_TRANSITIONS[payment.payment_status]

    if new_status not in allowed:
        raise ValueError(f"Cannot transition from {payment.payment_status} to {new_status}")

    print(f"{payment.payment_id} transition from {payment.payment_status} to {new_status}")
    payment.payment_status = new_status

def process_payment(payment_id: str):
    db = SessionLocal()

    with db.begin():
        # Lock payment row until a transaction finishes
        payment = db.execute(select(Payment).where(Payment.payment_id == payment_id)).scalar_one_or_none()
        
    if payment.payment_status != PaymentStatus.PROCESSING:
        return

    # wait for processing time
    time.sleep(random.randint(1,4))

    if random.random() < 0.2:
        if  random.random() < 0.5:
            raise TemporaryPaymentError()
        else:
            raise PermanentPaymentError()

def finalize_payment(payment_id: str, payment_status: PaymentStatus):
    with SessionLocal() as db:
        with db.begin():
            # Lock payment row until a transaction finishes
            payment = db.execute(select(Payment).where(Payment.payment_id == payment_id).with_for_update()).scalar_one_or_none()

            if payment is None or payment.payment_status != PaymentStatus.PROCESSING:
                return
            
            current_payment_status = payment.payment_status

            transition_payment(payment, payment_status)

            new_payment_status_history = PaymentStatusHistory(
                    payment_id = payment_id,
                    old_status = current_payment_status,
                    new_status = payment.payment_status
                )

            db.add(new_payment_status_history)

            new_outbox_event = OutboxEvent(
                event_type = "PaymentStatusChanged",
                aggregate_id = str(payment_id),
                payload = {
                    "payment_id": str(payment.payment_id),
                    "customer_id": str(payment.user_id),
                    "old_status": current_payment_status.value,
                    "new_status": payment.payment_status.value,
                    "amount": str(payment.amount),
                    "currency": payment.currency.value
                }
            )

            db.add(new_outbox_event)

