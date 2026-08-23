from fastapi import FastAPI, Depends, Header, HTTPException
from .schemas import PaymentResponse,PaymentRequest,PaymentStatus, PaymentStatusUpdate
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
import json
import hashlib
from .database import SessionLocal
from .services.payment_service import transition_payment
from .model import Payment,IdempotencyKey,PaymentStatusHistory
from uuid import UUID

app = FastAPI()

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

@app.get("/")
def homepage():
    return {"status":"ok"}

@app.post("/payments", response_model=PaymentResponse)
def create_payment(payment: PaymentRequest, db: Session = Depends(get_db), idempotency_key: str = Header(...)):

    new_payment = Payment(
                    customer_id=payment.customer_id,
                    amount=payment.amount,
                    currency=payment.currency,
                    payment_status = PaymentStatus.PENDING,
                )

    current_request_hash = create_request_hash(payment)
    
    try:
        db.add(new_payment)
        db.flush()

        new_idempotency_key = IdempotencyKey(
                    payment_id = new_payment.payment_id,
                    idempotency_key = idempotency_key,
                    request_hash = current_request_hash
                )

        db.add(new_idempotency_key)

        db.commit()
        db.refresh(new_payment)

    # handle integrity errors caused by different reason in the future.
    except IntegrityError:
        db.rollback()

        idempotency_key_request_hash = db.scalar(select(IdempotencyKey.request_hash).where(IdempotencyKey.idempotency_key == idempotency_key))

        if idempotency_key_request_hash == current_request_hash:
            current_payment = db.scalar(select(Payment).join(IdempotencyKey).where(IdempotencyKey.idempotency_key == idempotency_key))

            if current_payment:
                return PaymentResponse(
                        payment_id=current_payment.payment_id,
                        customer_id=current_payment.customer_id,
                        amount=current_payment.amount,
                        currency=current_payment.currency,
                        status=current_payment.payment_status
                    )

            raise
        else:
            raise HTTPException(status_code=409,detail="Idempotency key reused with different request parameters")

    except Exception:
        db.rollback()
        raise

    return PaymentResponse(
                payment_id=new_payment.payment_id,
                customer_id=new_payment.customer_id,
                amount=new_payment.amount,
                currency=new_payment.currency,
                status=new_payment.payment_status
            )

@app.patch("/payments/{payment_id}/status")
def update_payment_status(payment_id: UUID,request: PaymentStatusUpdate,db: Session = Depends(get_db)):

    payment = db.execute(select(Payment).where(Payment.payment_id == payment_id)).scalar_one_or_none()

    if payment is None:
        raise HTTPException(
        status_code=404,
        detail="Payment not found"
    )

    old_status = payment.payment_status
    
    try:
        transition_payment(payment, request.status)

        new_payment_status_history = PaymentStatusHistory(
                payment_id = payment_id,
                old_status = old_status,
                new_status = payment.payment_status
            )

        db.add(new_payment_status_history)
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
        detail="Failed to update payment status"
        )
        
    return payment


def create_request_hash(payment: PaymentRequest) -> str:
    data = {
        "customer_id": payment.customer_id,
        "amount": str(payment.amount),
        "currency": payment.currency.value
    }

    serialized = json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":")
    )

    return hashlib.sha256(
        serialized.encode("utf-8")
    ).hexdigest()


