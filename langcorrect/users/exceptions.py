class UserIsNoneError(Exception):
    def __init__(self, message="User cannot be none"):
        super().__init__(message)


class MissingSystemUserError(Exception):
    def __init__(self, message="System user does not exist"):
        super().__init__(message)
