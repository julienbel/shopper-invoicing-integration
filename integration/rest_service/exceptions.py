class GenericSatelliteException(Exception):
    def __init__(self, *args, **kwargs):
        self.error_message = kwargs.get("error_message")

    def __str__(self):
        return "{}".format(self.error_message)


class UnauthorizedSatelliteException(GenericSatelliteException):
    error_code = "SATELLITE_UNAUTHORIZED_ERROR"


class InvoicingProcessException(GenericSatelliteException):
    pass

class PdfGenerationException(InvoicingProcessException):
    pass

class SendEmailException(InvoicingProcessException):
    pass