from dataclasses import dataclass
from decimal import Decimal
from typing import List, Union



@dataclass
class ErrorDetail:
    code: str
    message: str


@dataclass
class ErrorResponse:
    error_details: List[ErrorDetail] = None


@dataclass
class Response:
    data: Union[
        CardBalanceResponse, CardResponse, ListCardResponse, WalletBalanceResponse
    ] = None
