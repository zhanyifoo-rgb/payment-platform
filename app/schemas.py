from enums import Enums
from decimal import Decimal 
from pydantic import BaseModel, Field

# region Enums
class PaymentStatus(str, Enums):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed" 

class Currencies(str, Enums):
    MYR = "MYR"
    USD = "USD"
    SGD = "SGD"

# endregion 

class PaymentRequest(BaseModel):
    customer_id: str
    amount: Decimal = Field(gt=0,decimal_places=2)
    currency: str