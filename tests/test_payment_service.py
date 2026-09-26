from app.services.transaction_service import transition_transaction
from app.model import Transaction
from app.schemas import TransactionStatus
import pytest


# Parametrize the test
@pytest.mark.parametrize(
    "old_status,new_status",
    [
        (TransactionStatus.PENDING, TransactionStatus.PROCESSING),
        (TransactionStatus.PENDING, TransactionStatus.CANCELLED),
        (TransactionStatus.PROCESSING, TransactionStatus.SUCCEEDED),
        (TransactionStatus.PROCESSING, TransactionStatus.FAILED),
    ]
)
def test_valid_transaction_transition(old_status, new_status):
    transaction = Transaction(
        transaction_status=old_status
    )

    transition_transaction(
        transaction,
        new_status
    )

    assert transaction.transaction_status is new_status


@pytest.mark.parametrize(
    "invalid_old_status,invalid_new_status",
    [
        (TransactionStatus.SUCCEEDED, TransactionStatus.PROCESSING),
        (TransactionStatus.FAILED, TransactionStatus.PROCESSING),
        (TransactionStatus.CANCELLED, TransactionStatus.PROCESSING),
        (TransactionStatus.PROCESSING, TransactionStatus.CANCELLED),
    ]
)
def test_invalid_transaction_transition(
    invalid_old_status,
    invalid_new_status
):
    transaction = Transaction(
        transaction_status=invalid_old_status
    )

    with pytest.raises(ValueError):
        transition_transaction(
            transaction,
            invalid_new_status
        )