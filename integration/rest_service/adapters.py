from typing import List
from .data_classes import InvoicingProcess


class ShopperInvoicingClientAdapter:
    def start_invoicing_process(self, invoices_process_datas: List[InvoicingProcess]) -> None:
        pass

    def external_service_is_healthy(self) -> bool:
        raise NotImplementedError
