from enum import Enum
from decimal import Decimal
from pydantic import BaseModel, Field
from uuid import UUID


# region Enums

class TransactionType(str, Enum):
    PAYMENT = "payment"
    TOPUP = "topup"


class TransactionStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Currencies(str, Enum):
    MYR = "MYR"
    USD = "USD"
    SGD = "SGD"


class UserRoles(str, Enum):
    CUSTOMER = "Customer"
    PAYMENTPROCESSOR = "PaymentProcessor"
    ADMIN = "Admin"


# endregion


# region Transactions

class TransactionRequest(BaseModel):
    transaction_type: TransactionType
    recipient_account_number: str
    amount: Decimal = Field(
        gt=0,
        decimal_places=2
    )
    currency: Currencies


class TransactionResponse(BaseModel):
    transaction_type: TransactionType
    transaction_id: UUID
    user_id: UUID
    amount: Decimal
    currency: Currencies
    status: TransactionStatus
    recipient_account_number: str


class TransactionStatusUpdate(BaseModel):
    status: TransactionStatus


# endregion


# region Users

class UserRegister(BaseModel):
    username: str
    password: str
    email: str
    phone: str
    first_name: str
    last_name: str


class UserResponse(BaseModel):
    user_id: UUID
    username: str
    account_number: str


# endregion