import base64
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
    Response
)
from integration.rest_service.exceptions import UnauthorizedSatelliteException
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
    shopper_payments_adapter = cls()

    app = Flask(__name__)

    def validate_request(signature):
        password = None
        if signature:
            if "Bearer" in signature:
                signature = signature.replace("Bearer", "")

            password = str(base64.b64decode(signature), "utf-8")

        if not password == getenv("REQUEST_PASSWORD"):
            raise UnauthorizedSatelliteException(
                error_message="Satellite unauthorized exception"
            )

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
                "provider": shopper_payments_adapter.name,
            }
        }
        message = exception.message if hasattr(exception, "message") else None
        if message:
            try:
                data["data"]["detail"] = json.loads(message)
            except (TypeError, JSONDecodeError):
                data["data"]["detail"] = str(message)

        return data


    @app.route(f"/healthz", methods=["GET"])
    def health():
        return {}, 200

    # External integration's health
    @app.route(f"/external_health", methods=["GET"])
    def external_health():
        if shopper_payments_adapter.external_service_is_healthy():
            return {}, 200
        return {}, 503

    return app
