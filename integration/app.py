import json
import logging
from json import JSONDecodeError
from os import getenv

import sentry_sdk
from flask import Flask, jsonify, request

from integration.rest_service.adapters import ShopperInvoicingClientAdapter
from integration.rest_service.data_classes import (
    ErrorDetail,
    ErrorResponse,
    Response,
    InvoicingProcess
)
from integration.rest_service.providers.exceptions import GenericAPIException

logger = logging.getLogger(__name__)


ENVIRONMENT = getenv("FLASK_ENVIRONMENT", "local")
SENTRY_DSN = getenv("SENTRY_DSN", None)

if SENTRY_DSN:
    sentry_sdk.init(
        SENTRY_DSN,
        environment=ENVIRONMENT,
    )


def run_app(cls):
    assert issubclass(
        cls, ShopperInvoicingClientAdapter
    ), "adapter requires to extend from ShopperInvoicingClientAdapter class"
    shopper_invoicing_adapter = cls()

    app = Flask(__name__)

    def get_error_response(e, code):
        try:
            error_message = e.error_message.decode()
        except AttributeError:
            error_message = e.error_message
        return (
            jsonify(
                ErrorResponse(
                    error_details=[
                        ErrorDetail(code=e.error_code, message=error_message)
                    ],
                )
            ),
            code,
        )

    def get_logger_data(exception):
        data = {
            "data": {
                "provider": shopper_invoicing_adapter.name,
            }
        }
        message = exception.message if hasattr(exception, "message") else None
        if message:
            try:
                data["data"]["detail"] = json.loads(message)
            except (TypeError, JSONDecodeError):
                data["data"]["detail"] = str(message)

        return data

    @app.route("/invoicing/process/start", methods=["POST"])
    def start_invoicing_process():
        invoices_processes_dict = json.loads(request.data)

        print("start_invoicing_process", invoices_processes_dict)

        invoices_processes_datas = [InvoicingProcess(**item) for item in invoices_processes_dict["invoices_processes"]]
        try:
            response_data = shopper_invoicing_adapter.start_invoicing_process(
                invoices_processes_datas
            )
        except GenericAPIException as e:
            logger.info(
                "Shopper invoicing integration (start_invoicing_process) request error %s",
                e.error_message,
                extra=get_logger_data(e),
            )
            return get_error_response(e, 400)

        return jsonify(Response(data=response_data))

    @app.route("/healthz", methods=["GET"])
    def health():
        return {}, 200

    # External integration's health
    @app.route("/external_health", methods=["GET"])
    def external_health():
        if shopper_invoicing_adapter.external_service_is_healthy():
            return {}, 200
        return {}, 503

    return app
