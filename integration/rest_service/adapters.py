from typing import List
from .data_classes import ExternalInvoiceData, InvoicingProcessRequest


class ShopperInvoicingClientAdapter:
    def start_invoicing_process(self, invoices_process_datas: List[InvoicingProcessRequest]) -> List[ExternalInvoiceData]:
        pass

    def emit_notification(self, invoices_process_datas: List[ExternalInvoiceData]) -> None:
        pass

    def external_service_is_healthy(self) -> bool:
        raise NotImplementedError
