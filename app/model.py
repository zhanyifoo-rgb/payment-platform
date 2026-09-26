from sqlalchemy import Numeric, DateTime, ForeignKey, UUID, String
from sqlalchemy.orm import DeclarativeBase, relationship, mapped_column, Mapped
from sqlalchemy.dialects.postgresql import JSONB

from .schemas import (
    TransactionStatus,
    Currencies,
    UserRoles,
    TransactionType
)

from datetime import datetime, timezone
from uuid import uuid4, UUID as pythonUUID
from decimal import Decimal


class Base(DeclarativeBase):
    pass


class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id: Mapped[pythonUUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid4,
        primary_key=True
    )

    transaction_type: Mapped[TransactionType] = mapped_column(
        nullable=False
    )

    user_id: Mapped[pythonUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id"),
        nullable=False
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    currency: Mapped[Currencies] = mapped_column(
        nullable=False
    )

    transaction_status: Mapped[TransactionStatus] = mapped_column(
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    recipient_account_number: Mapped[str] = mapped_column(
        String(12),
        nullable=False
    )

    idempotency = relationship(
        "IdempotencyKey",
        back_populates="transaction",
        uselist=False
    )

    transaction_status_history = relationship(
        "TransactionStatusHistory",
        back_populates="transaction"
    )

    user = relationship(
        "User",
        back_populates="transactions"
    )


class IdempotencyKey(Base):
    __tablename__ = "idempotency_keys"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    transaction_id: Mapped[pythonUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("transactions.transaction_id"),
        unique=True,
        nullable=False
    )

    idempotency_key: Mapped[str] = mapped_column(
        unique=True,
        nullable=False
    )

    request_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False
    )

    transaction = relationship(
        "Transaction",
        back_populates="idempotency"
    )


class TransactionStatusHistory(Base):
    __tablename__ = "transaction_status_history"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    transaction_id: Mapped[pythonUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("transactions.transaction_id"),
        nullable=False
    )

    old_status: Mapped[TransactionStatus] = mapped_column(
        nullable=False
    )

    new_status: Mapped[TransactionStatus] = mapped_column(
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    transaction = relationship(
        "Transaction",
        back_populates="transaction_status_history"
    )


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[pythonUUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid4,
        primary_key=True
    )

    account_number: Mapped[str] = mapped_column(
        String(12),
        unique=True,
        nullable=False
    )

    username: Mapped[str] = mapped_column(
        unique=True,
        nullable=False
    )

    first_name: Mapped[str] = mapped_column(
        nullable=False
    )

    last_name: Mapped[str] = mapped_column(
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True
    )

    phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        unique=True
    )

    available_balance: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=0
    )

    password_hash: Mapped[str] = mapped_column(
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    role: Mapped[UserRoles] = mapped_column(
        nullable=False,
        default=UserRoles.CUSTOMER
    )

    transactions = relationship(
        "Transaction",
        back_populates="user"
    )


class OutboxEvent(Base):
    __tablename__ = "outbox_events"

    event_id: Mapped[int] = mapped_column(
        primary_key=True
    )

    event_type: Mapped[str] = mapped_column(
        nullable=False
    )

    aggregate_id: Mapped[str] = mapped_column(
        nullable=False
    )

    payload: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )