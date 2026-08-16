from enums import Enums

class PaymentStatus(str, Enums):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed" 
