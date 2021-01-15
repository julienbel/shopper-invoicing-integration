

class ShopperInvoicingClientAdapter:
    def start_invoicing_process(self) -> None:
        pass

    def external_service_is_healthy(self) -> bool:
        raise NotImplementedError
