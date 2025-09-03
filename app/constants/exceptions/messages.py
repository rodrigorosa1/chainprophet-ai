class UserEmailNotFoundError(Exception):
    MESSAGE = "Email not found"


class UserNotFoundError(Exception):
    MESSAGE = "User not found"


class UserEmailDocumentAlreadyExistsError(Exception):
    MESSAGE = "Email already exists"


class AlertNotFoundError(Exception):
    MESSAGE = "Alert not found"


class ActiveAlreadyExistsError(Exception):
    MESSAGE = "Active already exists"
