class MissingSubscriptionIdError(Exception):
    def __init__(self, message="User has no subscription ID"):
        super().__init__(message)


class SubscriptionCancellationError(Exception):
    def __init__(self, message="Error cancelling subscription"):
        super().__init__(message)
