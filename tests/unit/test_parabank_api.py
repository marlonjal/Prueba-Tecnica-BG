"""Unit tests for ParaBank API request construction."""

from decimal import Decimal

from services.parabank_api import ParaBankApi


class FakeRequestContext:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, dict | None]] = []

    def get(self, path: str):
        self.calls.append(("GET", path, None))
        return object()

    def post(self, path: str, params: dict):
        self.calls.append(("POST", path, params))
        return object()


def test_login_url_encodes_credentials() -> None:
    request = FakeRequestContext()

    ParaBankApi(request).login("qa user", "p@ss word")

    assert request.calls == [("GET", "login/qa%20user/p%40ss%20word", None)]


def test_withdraw_serializes_decimal_parameters() -> None:
    request = FakeRequestContext()

    ParaBankApi(request).withdraw(12345, Decimal("1.00"))

    assert request.calls == [
        ("POST", "withdraw", {"accountId": "12345", "amount": "1.00"})
    ]


def test_withdraw_omits_missing_amount() -> None:
    request = FakeRequestContext()

    ParaBankApi(request).withdraw("12345", None)

    assert request.calls == [("POST", "withdraw", {"accountId": "12345"})]


def test_transfer_serializes_account_and_amount_parameters() -> None:
    request = FakeRequestContext()

    ParaBankApi(request).transfer(12345, 67890, Decimal("5.25"))

    assert request.calls == [
        (
            "POST",
            "transfer",
            {
                "fromAccountId": "12345",
                "toAccountId": "67890",
                "amount": "5.25",
            },
        )
    ]
