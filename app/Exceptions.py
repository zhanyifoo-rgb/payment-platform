
class PaymentProcessingError(Exception):
    pass

class TemporaryPaymentError(Exception):
    pass

class PermanentPaymentError(Exception):
    pass