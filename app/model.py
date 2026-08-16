from sqlalchemy import Column, Integer, String, Numeric, DateTime, Enum
from database import Base
from enums import PaymentStatus
from datetime import datetime

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer)
    amount = Column(Numeric(10,2))
    currency = Column(String)
    payment_status = Column(Enum(PaymentStatus), nullable=False)
    created_at = Column(DateTime)

