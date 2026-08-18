from fastapi import FastAPI, Depends
from .schemas import PaymentResponse,PaymentRequest,PaymentStatus
from uuid import uuid4
from sqlalchemy.orm import Session

from .database import SessionLocal
from .model import Payment
from .schemas import PaymentRequest

app = FastAPI()

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close

@app.get("/")
def homepage():
    return {"status":"ok"}

@app.post("/payments", response_model=PaymentResponse)
def create_payment(payment: PaymentRequest, db: Session = Depends(get_db)):
    payment_id = f"pay_{uuid4().hex[:12]}"

    new_payment = Payment(
        customer_id=payment.customer_id,
        amount=payment.amount,
        currency=payment.currency,
        payment_status = PaymentStatus.PENDING.value,
    )

    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    
    return PaymentResponse(
        payment_id=payment_id,
        customer_id=new_payment.customer_id,
        amount=new_payment.amount,
        currency=new_payment.currency,
        status=PaymentStatus.PENDING.value
    )