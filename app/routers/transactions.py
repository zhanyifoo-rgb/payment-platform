from fastapi import Depends, Header, HTTPException, APIRouter
from app.schemas import (
    TransactionResponse,
    TransactionRequest,
    TransactionStatus,
    TransactionStatusUpdate,
    TransactionType
)
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
import json
import hashlib

from app.database import get_db
from app.services.transaction_service import transition_transaction
from app.model import (
    Transaction,
    IdempotencyKey,
    TransactionStatusHistory,
    User,
    UserRoles
)
from app.utils.security import get_current_user, requires_admin
from uuid import UUID
from app.messaging.publisher import send_process_transaction_message
from app.Exceptions import InsufficientFundError


router = APIRouter(
    prefix="/api/v1/transactions",
    tags=["transactions"]
)


@router.get(
    "/get/{transaction_id}",
    response_model=TransactionResponse
)
def get_transaction(
    transaction_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    transaction = db.scalar(
        select(Transaction).where(
            Transaction.transaction_id == transaction_id
        )
    )

    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found."
        )

    if (
        current_user.role is UserRoles.CUSTOMER
        and current_user.user_id != transaction.user_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Unable to access transaction as it belongs to a different user."
        )

    return TransactionResponse(
        transaction_type= transaction.transaction_type,
        transaction_id=transaction.transaction_id,
        user_id=transaction.user_id,
        amount=transaction.amount,
        currency=transaction.currency,
        status=transaction.transaction_status,
        recipient_account_number=transaction.recipient_account_number
    )


@router.post(
    "/createpayment",
    response_model=TransactionResponse
)
def create_payment_transaction(
    transaction: TransactionRequest,
    db: Session = Depends(get_db),
    idempotency_key: str = Header(...),
    current_user: User = Depends(get_current_user)
):

    recipient = db.scalar(
        select(User).where(
            User.account_number == transaction.recipient_account_number
        )
    )

    if recipient is None:
        raise HTTPException(
            status_code=404,
            detail="Recipient account not found"
        )

    if current_user.available_balance < transaction.amount:
        raise InsufficientFundError("Insufficient fund.")

    new_transaction = Transaction(
        transaction_type = TransactionType.PAYMENT,
        user_id=current_user.user_id,
        amount=transaction.amount,
        currency=transaction.currency,
        transaction_status=TransactionStatus.PENDING,
        recipient_account_number=transaction.recipient_account_number
    )

    current_request_hash = create_request_hash(
        transaction,
        current_user.user_id
    )

    try:
        db.add(new_transaction)
        db.flush()

        new_idempotency_key = IdempotencyKey(
            transaction_id=new_transaction.transaction_id,
            idempotency_key=idempotency_key,
            request_hash=current_request_hash
        )

        db.add(new_idempotency_key)

        db.commit()
        db.refresh(new_transaction)

    # Handle integrity errors caused by different reasons in the future.
    except IntegrityError:
        db.rollback()

        idempotency_key_request_hash = db.scalar(
            select(IdempotencyKey.request_hash).where(
                IdempotencyKey.idempotency_key == idempotency_key
            )
        )

        if idempotency_key_request_hash == current_request_hash:

            current_transaction = db.scalar(
                select(Transaction)
                .join(IdempotencyKey)
                .where(
                    IdempotencyKey.idempotency_key == idempotency_key
                )
            )

            if current_transaction:
                return TransactionResponse(
                    transaction_id=current_transaction.transaction_id,
                    user_id=current_transaction.user_id,
                    amount=current_transaction.amount,
                    currency=current_transaction.currency,
                    status=current_transaction.transaction_status,
                    recipient_account_number=(
                        current_transaction.recipient_account_number
                    )
                )

            raise

        else:
            raise HTTPException(
                status_code=409,
                detail="Idempotency key reused with different request parameters"
            )

    except Exception:
        db.rollback()
        raise

    send_process_transaction_message(
        str(new_transaction.transaction_id)
    )

    return TransactionResponse(
        transaction_type=new_transaction.transaction_type,
        transaction_id=new_transaction.transaction_id,
        user_id=new_transaction.user_id,
        amount=new_transaction.amount,
        currency=new_transaction.currency,
        status=new_transaction.transaction_status,
        recipient_account_number=(
            new_transaction.recipient_account_number
        )
    )


@router.patch(
    "/{transaction_id}/status",
    response_model=TransactionResponse
)
def update_transaction_status(
    transaction_id: UUID,
    request: TransactionStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(requires_admin)
):

    # Lock transaction row until the database transaction finishes.
    transaction = db.execute(
        select(Transaction)
        .where(Transaction.transaction_id == transaction_id)
        .with_for_update()
    ).scalar_one_or_none()

    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    old_status = transaction.transaction_status

    try:
        transition_transaction(
            transaction,
            request.status
        )

        new_transaction_status_history = TransactionStatusHistory(
            transaction_id=transaction_id,
            old_status=old_status,
            new_status=transaction.transaction_status
        )

        db.add(new_transaction_status_history)
        db.commit()

    except ValueError as e:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail=str(e)
        )

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to update transaction status"
        )

    return TransactionResponse(
        transaction_type= transaction.transaction_type,
        transaction_id=transaction.transaction_id,
        user_id=transaction.user_id,
        amount=transaction.amount,
        currency=transaction.currency,
        status=transaction.transaction_status,
        recipient_account_number=(
            transaction.recipient_account_number
        )
    )


def create_request_hash(
    transaction: TransactionRequest,
    user_id: UUID
) -> str:

    data = {
        "user_id": str(user_id),
        "amount": str(transaction.amount),
        "currency": transaction.currency.value
    }

    serialized = json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":")
    )

    return hashlib.sha256(
        serialized.encode("utf-8")
    ).hexdigest()

@router.post(
    "/topup",
    response_model=TransactionResponse
)
def create_topup_transaction(
    transaction: TransactionRequest,
    db: Session = Depends(get_db),
    idempotency_key: str = Header(...),
    current_user: User = Depends(get_current_user)
):

    new_transaction = Transaction(
        transaction_type = TransactionType.TOPUP,
        user_id=current_user.user_id,
        amount=transaction.amount,
        currency=transaction.currency,
        transaction_status=TransactionStatus.PENDING,
        recipient_account_number=transaction.recipient_account_number
    )

    current_request_hash = create_request_hash(
        transaction,
        current_user.user_id
    )

    try:
        db.add(new_transaction)
        db.flush()

        new_idempotency_key = IdempotencyKey(
            transaction_id=new_transaction.transaction_id,
            idempotency_key=idempotency_key,
            request_hash=current_request_hash
        )

        db.add(new_idempotency_key)

        db.commit()
        db.refresh(new_transaction)

    # Handle integrity errors caused by different reasons in the future.
    except IntegrityError:
        db.rollback()

        idempotency_key_request_hash = db.scalar(
            select(IdempotencyKey.request_hash).where(
                IdempotencyKey.idempotency_key == idempotency_key
            )
        )

        if idempotency_key_request_hash == current_request_hash:

            current_transaction = db.scalar(
                select(Transaction)
                .join(IdempotencyKey)
                .where(
                    IdempotencyKey.idempotency_key == idempotency_key
                )
            )

            if current_transaction:
                return TransactionResponse(
                        transaction_type= new_transaction.transaction_type,
                        transaction_id=new_transaction.transaction_id,
                        user_id=new_transaction.user_id,
                        amount=new_transaction.amount,
                        currency=new_transaction.currency,
                        status=new_transaction.transaction_status,
                        recipient_account_number=(
                            new_transaction.recipient_account_number
                        )
                )

            raise

        else:
            raise HTTPException(
                status_code=409,
                detail="Idempotency key reused with different request parameters"
            )

    except Exception:
        db.rollback()
        raise

    send_process_transaction_message(
        str(new_transaction.transaction_id)
    )

    return TransactionResponse(
            transaction_type= new_transaction.transaction_type,
            transaction_id=new_transaction.transaction_id,
            user_id=new_transaction.user_id,
            amount=new_transaction.amount,
            currency=new_transaction.currency,
            status=new_transaction.transaction_status,
            recipient_account_number=(
                new_transaction.recipient_account_number
            )
    )