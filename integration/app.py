import arrow
import json
import logging
from json import JSONDecodeError
from os import getenv
from uuid import UUID
import sentry_sdk
from flask import Flask, jsonify, request
from flask_mail import Mail, Message

from integration.rest_service.adapters import ShopperInvoicingClientAdapter
from integration.rest_service.data_classes import (
    ErrorDetail,
    ErrorResponse,
    Response,
    Invoice,
    InvoicingProcess,
    InvoicingProcessRequest,
InvoiceLine,
KeyValueField,
TaxInformation,
PartnerFiscalData
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

    app = Flask(__name__, static_url_path="/static", static_folder="static")

    app.config['DEBUG'] = True
    app.config['EXPLAIN_TEMPLATE_LOADING'] = getenv("EXPLAIN_TEMPLATE_LOADING", False) == "True"

    app.config['MAIL_SERVER'] = getenv("MAIL_SERVER")
    app.config['MAIL_PORT'] = getenv("MAIL_PORT")
    app.config['MAIL_USERNAME'] = getenv("MAIL_USERNAME")
    app.config['MAIL_PASSWORD'] = getenv("MAIL_PASSWORD")
    app.config['MAIL_USE_TLS'] = getenv("MAIL_USE_TLS", False) == "True"
    app.config['MAIL_USE_SSL'] = getenv("MAIL_USE_SSL", False) == "True"
    app.config['MAIL_DEBUG'] = getenv("MAIL_DEBUG", False) == "True"

    app.mail = Mail(app)



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
                    ]
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
        invoices_processes = json.loads(request.data)

        invoices_processes_datas = [
            InvoicingProcessRequest(
                process=InvoicingProcess(
                    uuid=UUID(invoice["process"].get("uuid")),
                    created_at=arrow.get(
                                    invoice["process"].get("created_at")
                                ).datetime,
                    updated_at=arrow.get(
                                    invoice["process"].get("updated_at")
                                ).datetime,
                    user_uuid=UUID(invoice["process"].get("uuid")),
                    requester=invoice["process"].get("requester"),
                    process_status=invoice["process"].get("process_status"),
                ),
                invoice=Invoice(
                    uuid=UUID(invoice["invoice"].get("uuid")),
                    created_at=arrow.get(
                        invoice["invoice"].get("created_at")
                    ).datetime,
                    user_uuid=UUID(invoice["invoice"].get("user_uuid")),
                    gross_amount_e5=int(invoice["invoice"].get("gross_amount_e5")),
                    lines=[InvoiceLine(**line) for line in invoice["invoice"].get("lines")],
                    taxes=[TaxInformation(**taxe) for taxe in invoice["invoice"].get("taxes")],
                    partner_fiscal_data=PartnerFiscalData(
                        full_name=invoice["invoice"]["partner_fiscal_data"].get("full_name"),
                        form_of_identification=[KeyValueField(**item) for item in invoice["invoice"]["partner_fiscal_data"].get("form_of_identification")],
                        extra_fields=[KeyValueField(**item) for item in invoice["invoice"]["partner_fiscal_data"].get("extra_fields")]
                    ),
                ),
            ) for invoice in invoices_processes
        ]

        try:
            external_invoices = shopper_invoicing_adapter.start_invoicing_process(
                invoices_processes_datas
            )
        except GenericAPIException as e:
            logger.info(
                "Shopper invoicing integration (start_invoicing_process) request error %s",
                e.error_message,
                extra=get_logger_data(e),
            )
            return get_error_response(e, 400)

        try:
            shopper_invoicing_adapter.emit_notification(external_invoices)
        except GenericAPIException as e:
            logger.info(
                "Shopper invoicing integration (emit_notification) request error %s",
                e.error_message,
                extra=get_logger_data(e),
            )
            return get_error_response(e, 400)

        return jsonify(Response(data={}))

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
