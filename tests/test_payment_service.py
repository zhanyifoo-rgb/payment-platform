from app.services.payment_service import transition_payment
from app.model import Payment
from app.schemas import PaymentStatus
import pytest

# Parametrize the test 
@pytest.mark.parametrize(
    "old_status,new_status",
    [
        (PaymentStatus.PENDING, PaymentStatus.PROCESSING),
        (PaymentStatus.PENDING, PaymentStatus.CANCELLED),
        (PaymentStatus.PROCESSING, PaymentStatus.SUCCEEDED),
        (PaymentStatus.PROCESSING, PaymentStatus.FAILED),
    ]
)

def test_valid_payment_transition(old_status,new_status):
    payment = Payment(payment_status = old_status)

    transition_payment(payment,new_status)

    assert payment.payment_status is new_status

@pytest.mark.parametrize(
    "invalid_old_status,invalid_new_status",
    [
        (PaymentStatus.SUCCEEDED, PaymentStatus.PROCESSING),
        (PaymentStatus.FAILED, PaymentStatus.PROCESSING),
        (PaymentStatus.CANCELLED, PaymentStatus.PROCESSING),
        (PaymentStatus.PROCESSING, PaymentStatus.CANCELLED),
    ]
)

def test_invalid_payment_transition(invalid_old_status,invalid_new_status):
    payment = Payment(payment_status = invalid_old_status)

    with pytest.raises(ValueError):
        transition_payment(payment,invalid_new_status)