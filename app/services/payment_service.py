from app.schemas import PaymentStatus

ALLOWED_TRANSITIONS = {
    PaymentStatus.PENDING : {PaymentStatus.PROCESSING,PaymentStatus.CANCELLED},
    PaymentStatus.PROCESSING : {PaymentStatus.SUCCEEDED,PaymentStatus.FAILED},
    PaymentStatus.SUCCEEDED : set(),
    PaymentStatus.FAILED : set(),
    PaymentStatus.CANCELLED : set()
}

def transition_payment(payment,new_status: PaymentStatus):
    allowed = ALLOWED_TRANSITIONS[payment.payment_status]

    if new_status not in allowed:
        raise ValueError(f"Cannot transition from {payment.payment_status} to {new_status}")

    payment.payment_status = new_status
    