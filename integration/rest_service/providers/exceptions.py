class UnhandledErrorAPIException(Exception):
    error_code = "UNHANDLED_ERROR_API_EXCEPTION"

    def __init__(self, *args, **kwargs):
        self.error_message = kwargs.get("error_message")

    def __str__(self):
        return f"{self.error_message}"


class GenericAPIException(Exception):
    error_code = "GENERIC_API_EXCEPTION"

    def __init__(self, *args, **kwargs):
        self.error_message = kwargs.get("error_message")

    def __str__(self):
        return f"{self.error_message}"


class BadRequestAPIException(GenericAPIException):
    error_code = "PROVIDER_BAD_REQUEST_ERROR"


class TimeoutAPIException(GenericAPIException):
    error_code = "PROVIDER_TIMEOUT_ERROR"


class UnauthorizedAPIException(GenericAPIException):
    error_code = "PROVIDER_UNAUTHORIZED_ERROR"


class ForbiddenAPIException(GenericAPIException):
    error_code = "PROVIDER_FORBIDDEN_ERROR"


class NotFoundAPIException(GenericAPIException):
    error_code = "PROVIDER_NOT_FOUND_ERROR"


class UnprocessableEntityAPIException(GenericAPIException):
    error_code = "PROVIDER_UNPROCESSABLE_ENTITY_ERROR"


class ServiceUnavailableAPIException(GenericAPIException):
    error_code = "PROVIDER_SERVICE_UNAVAILABLE_ERROR"
