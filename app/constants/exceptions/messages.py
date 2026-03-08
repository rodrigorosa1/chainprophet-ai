class UserEmailNotFoundError(Exception):
    MESSAGE = "Email not found"


class UserNotFoundError(Exception):
    MESSAGE = "User not found"


class UserEmailDocumentAlreadyExistsError(Exception):
    MESSAGE = "Email already exists"


class PlanNotFoundError(Exception):
    MESSAGE = "Plan not found"


class SubscriptionNotFoundError(Exception):
    MESSAGE = "Subscription not found"


class ActiveAlreadyExistsError(Exception):
    MESSAGE = "Active already exists"
