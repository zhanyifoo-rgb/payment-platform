from app.schemas import TransactionStatus
from app.model import Transaction, TransactionStatusHistory, OutboxEvent, User, TransactionType
import random
import time
from app.database import SessionLocal
from app.Exceptions import TemporaryTransactionError, PermanentTransactionError, InsufficientFundError
from sqlalchemy import select

ALLOWED_TRANSITIONS = {
    TransactionStatus.PENDING : {TransactionStatus.PROCESSING,TransactionStatus.CANCELLED},
    TransactionStatus.PROCESSING : {TransactionStatus.SUCCEEDED,TransactionStatus.FAILED},
    TransactionStatus.SUCCEEDED : set(),
    TransactionStatus.FAILED : set(),
    TransactionStatus.CANCELLED : set()
}

def transition_transaction(
    transaction: Transaction,
    new_status: TransactionStatus
):
    allowed = ALLOWED_TRANSITIONS[transaction.transaction_status]

    if new_status not in allowed:
        raise ValueError(
            f"Cannot transition from "
            f"{transaction.transaction_status} to {new_status}"
        )

    print(
        f"{transaction.transaction_id} transition "
        f"from {transaction.transaction_status} to {new_status}"
    )

    transaction.transaction_status = new_status


def process_transaction(transaction_id: str):
    db = SessionLocal()

    with db.begin():
        # Lock transaction row until the transaction finishes
        transaction = db.execute(
            select(Transaction)
            .where(Transaction.transaction_id == transaction_id)
            .with_for_update()
        ).scalar_one_or_none()

        if transaction is None:
            return

        if transaction.transaction_status != TransactionStatus.PROCESSING:
            return

    # Wait for processing time
    time.sleep(random.randint(1, 4))

    if random.random() < 0.2:
        if random.random() < 0.5:
            raise TemporaryTransactionError()
        else:
            raise PermanentTransactionError()


def finalize_transaction(
    transaction_id: str,
    transaction_status: TransactionStatus
):
    with SessionLocal() as db:
        with db.begin():
            # Lock transaction row until the transaction finishes
            transaction = db.execute(
                select(Transaction)
                .where(Transaction.transaction_id == transaction_id)
                .with_for_update()
            ).scalar_one_or_none()

            if (
                transaction is None
                or transaction.transaction_status != TransactionStatus.PROCESSING
            ):
                return

            current_transaction_status = transaction.transaction_status

            if transaction_status == TransactionStatus.SUCCEEDED:
                recipient = db.execute(
                    select(User)
                    .where(
                        User.account_number
                        == transaction.recipient_account_number
                    )
                    .with_for_update()
                ).scalar_one_or_none()

                if recipient is None:
                    raise ValueError("Recipient not found")
            
                if transaction.transaction_type == TransactionType.PAYMENT:

                    sender = db.execute(
                        select(User)
                        .where(User.user_id == transaction.user_id)
                        .with_for_update()
                    ).scalar_one_or_none()

                    if sender is None:
                        raise ValueError("Sender not found")

                    if sender.available_balance < transaction.amount:
                        raise InsufficientFundError()

                    recipient.available_balance += transaction.amount
                    sender.available_balance -= transaction.amount

                elif transaction.transaction_type == TransactionType.TOPUP:

                    recipient.available_balance += transaction.amount


            transition_transaction(
                transaction,
                transaction_status
            )

            new_transaction_status_history = TransactionStatusHistory(
                transaction_id=transaction_id,
                old_status=current_transaction_status,
                new_status=transaction.transaction_status
            )

            db.add(new_transaction_status_history)

            new_outbox_event = OutboxEvent(
                event_type="TransactionStatusChanged",
                aggregate_id=str(transaction_id),
                payload={
                    "transaction_id": str(transaction.transaction_id),
                    "user_id": str(transaction.user_id),
                    "old_status": current_transaction_status.value,
                    "new_status": transaction.transaction_status.value,
                    "amount": str(transaction.amount),
                    "currency": transaction.currency.value,
                    "recipient_account_number": (
                        transaction.recipient_account_number
                    )
                }
            )

            db.add(new_outbox_event)