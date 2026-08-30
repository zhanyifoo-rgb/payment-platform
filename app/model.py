from sqlalchemy import Numeric, DateTime,ForeignKey, UUID, String
from sqlalchemy.orm import DeclarativeBase,relationship,mapped_column,Mapped
from .schemas import PaymentStatus, Currencies
from datetime import datetime, timezone
from uuid import uuid4,UUID as pythonUUID
from decimal import Decimal

class Base(DeclarativeBase):
    pass

class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int]= mapped_column(primary_key=True)
    payment_id: Mapped[pythonUUID] = mapped_column(UUID(as_uuid=True),default=uuid4, nullable = False, unique=True)
    customer_id: Mapped[int] = mapped_column(nullable = False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10,2), nullable = False)
    currency: Mapped[Currencies] = mapped_column(nullable = False)
    payment_status: Mapped[PaymentStatus] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=lambda : datetime.now(timezone.utc),nullable=False)

    idempotency = relationship("IdempotencyKey", back_populates="payment")
    payment_status_history = relationship("PaymentStatusHistory", back_populates="payment")

class IdempotencyKey(Base):
    __tablename__ = "idempotency_keys"

    id: Mapped[int] = mapped_column(primary_key=True)
    payment_id: Mapped[pythonUUID] = mapped_column(ForeignKey("payments.payment_id"),unique=True,nullable=False)
    idempotency_key: Mapped[str] = mapped_column(unique=True,nullable=False)
    request_hash: Mapped[str] = mapped_column(String(64),nullable=False)

    payment = relationship("Payment",back_populates="idempotency")

class PaymentStatusHistory(Base):
    __tablename__ = "payment_status_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    payment_id: Mapped[pythonUUID] = mapped_column(ForeignKey("payments.payment_id"),nullable=False)
    old_status: Mapped[PaymentStatus] = mapped_column(nullable=False)
    new_status: Mapped[PaymentStatus] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=lambda : datetime.now(timezone.utc),nullable=False)

    payment = relationship("Payment",back_populates="payment_status_history")