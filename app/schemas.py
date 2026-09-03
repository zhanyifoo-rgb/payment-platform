from enum import Enum
from decimal import Decimal 
from pydantic import BaseModel, Field
from uuid import UUID

# region Enums
class PaymentStatus(str, Enum):
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

# region payments
class PaymentRequest(BaseModel):
    user_id: UUID
    amount: Decimal = Field(gt=0,decimal_places=2)
    currency: Currencies

class PaymentResponse(BaseModel):
    payment_id: UUID
    user_id: UUID
    amount: Decimal
    currency: Currencies
    status: PaymentStatus

class PaymentStatusUpdate(BaseModel):
    status: PaymentStatus
# endregion

# region users

class UserRegister(BaseModel):
    username: str
    password: str
    role: UserRoles

class UserResponse(BaseModel):
    user_id: UUID
    username: str

# endregion