from sqlalchemy import Column, Integer, String, Numeric, DateTime, Enum
from sqlalchemy.orm import DeclarativeBase
from .schemas import PaymentStatus, Currencies
from datetime import datetime, timezone

class Base(DeclarativeBase):
    pass

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, nullable = False)
    amount = Column(Numeric(10,2), nullable = False)
    currency = Column(Enum(Currencies), nullable = False)
    payment_status = Column(Enum(PaymentStatus), nullable=False)
    created_at = Column(DateTime,default=lambda : datetime.now(timezone.utc),nullable=False)

