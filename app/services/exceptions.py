class UserNotFoundError(Exception):
    pass


class RequestNotFoundError(Exception):
    pass


class InactiveUserError(Exception):
    pass


class ActiveRequestLimitError(Exception):
    pass


class AdminNotFoundError(Exception):
    pass


class AdminAlreadyExistsError(Exception):
    pass


class RequestAlreadyClosedError(Exception):
    pass


class RequestTransitionNotAllowedError(Exception):
    pass


class AdminIsNotActiveError(Exception):
    pass


class PasswordNotValidError(Exception):
    pass


class RefreshTokenInvalidError(Exception):
    pass


class RefreshTokenExpiredError(Exception):
    pass


class AdminSelfDeleteError(Exception):
    pass


class UserHasRequestsError(Exception):
    pass
