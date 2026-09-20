from sqlalchemy import Numeric, DateTime,ForeignKey, UUID, String
from sqlalchemy.orm import DeclarativeBase,relationship,mapped_column,Mapped
from sqlalchemy.dialects.postgresql import JSONB
from .schemas import PaymentStatus, Currencies, UserRoles
from datetime import datetime, timezone
from uuid import uuid4,UUID as pythonUUID
from decimal import Decimal

class Base(DeclarativeBase):
    pass

class Payment(Base):
    __tablename__ = "payments"

    payment_id: Mapped[pythonUUID] = mapped_column(UUID(as_uuid=True),default=uuid4, primary_key=True)
    user_id: Mapped[pythonUUID] = mapped_column(UUID(as_uuid=True),ForeignKey("users.user_id"), nullable = False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10,2), nullable = False)
    currency: Mapped[Currencies] = mapped_column(nullable = False)
    payment_status: Mapped[PaymentStatus] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=lambda : datetime.now(timezone.utc),nullable=False)

    idempotency = relationship("IdempotencyKey", back_populates="payment",uselist=False)
    payment_status_history = relationship("PaymentStatusHistory", back_populates="payment")
    user = relationship(
    "User",
    back_populates="payments"
)

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

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[pythonUUID] = mapped_column(UUID(as_uuid=True),default=uuid4,primary_key=True)
    account_number: Mapped[str] = mapped_column(String(12), unique = True, nullable = False)
    username: Mapped[str] = mapped_column(unique=True,nullable=False)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(String(255),nullable=False, unique = True)
    phone: Mapped[str] = mapped_column(String(20),nullable=False, unique = True)
    available_balance: Mapped[Decimal] = mapped_column(Numeric(10,2), nullable = False, default=0)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=lambda : datetime.now(timezone.utc),nullable=False)
    role: Mapped[UserRoles] = mapped_column(nullable=False, default=UserRoles.CUSTOMER)

    payments = relationship(
        "Payment",
        back_populates="user"
    )

class OutboxEvent(Base):
    __tablename__ = "outbox_events"

    event_id: Mapped[int] = mapped_column(primary_key=True)
    event_type: Mapped[str] = mapped_column(nullable=False)
    aggregate_id: Mapped[str] = mapped_column(nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB,nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=lambda : datetime.now(timezone.utc),nullable=False)
    published_at: Mapped[datetime|None] = mapped_column(DateTime(timezone=True),nullable=True)


