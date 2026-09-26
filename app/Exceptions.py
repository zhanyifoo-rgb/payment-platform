
class TransactionProcessingError(Exception):
    pass

class TemporaryTransactionError(Exception):
    pass

class PermanentTransactionError(Exception):
    pass

class InsufficientFundError(Exception):
    pass