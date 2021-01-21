import arrow

from dataclasses import dataclass, asdict
from datetime import datetime
from decimal import Decimal
from typing import List, Union
from uuid import UUID, uuid4


@dataclass
class InvoicingItemModel:
    uuid: UUID
    created_at: datetime

    def serialize(self):
        return asdict(self)

@dataclass
class UpdatableInvoicingItemModel(InvoicingItemModel):
    updated_at: datetime


@dataclass
class KeyValueField:
    name: str
    value: str


@dataclass
class FormOfIdentification(KeyValueField):
    pass


@dataclass
class ExtraField(KeyValueField):
    pass


@dataclass
class User:
    full_name: str
    form_of_identification: List[KeyValueField]
    extra_fields: List[KeyValueField]


@dataclass
class TaxInformation:
    _type: str
    description: str
    code: str
    factor_type: str
    factor: Decimal
    taxable_amount_e5: int
    tax_amount_e5: int


@dataclass
class InvoiceLine:
    description: str
    unit: str
    quantity: int
    amount_e5: int
    total_amount_e5: int
    taxes: List[TaxInformation]


@dataclass
class PartnerFiscalData(User):
    pass


@dataclass
class InvoiceBase:
    user_uuid: UUID
    gross_amount_e5: int
    lines: List[InvoiceLine]
    taxes: List[TaxInformation]
    partner_fiscal_data: PartnerFiscalData


@dataclass
class InvoiceData(InvoiceBase):
    pass


@dataclass
class Invoice(InvoiceBase, InvoicingItemModel):
    pass


@dataclass
class InvoicingProcess(UpdatableInvoicingItemModel):
    user_uuid: UUID
    requester: str
    process_status: str


@dataclass
class InvoicingProcessCreationRequest:
    requester: str
    invoice_data: InvoiceData


@dataclass
class CompanyFiscalData(User):
    pass


@dataclass
class ExternalInvoiceData(InvoicingItemModel):
    process_status: str
    data: dict
    company_fiscal_data: User


@dataclass
class InvoicingProcessRejectionRequest:
    user_uuid: UUID
    external_response_data: ExternalInvoiceData
    created_at: str
    uuid: UUID


@dataclass
class ErrorDetail:
    code: str
    message: str


@dataclass
class ErrorResponse:
    error_details: List[ErrorDetail] = None


@dataclass
class Response:
    data: Union[str] = None
