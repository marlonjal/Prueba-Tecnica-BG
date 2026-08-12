"""Unit tests for ParaBank API request construction."""

from decimal import Decimal

from services.parabank_api import ParaBankApi


class FakeRequestContext:
    """Record HTTP method, path, and parameters without network access."""

    def __init__(self) -> None:
        """Initialize an empty request-call history."""
        self.calls: list[tuple[str, str, dict | None]] = []

    def get(self, path: str):
        """Record a simulated GET request."""
        self.calls.append(("GET", path, None))
        return object()

    def post(self, path: str, params: dict):
        """Record a simulated POST request and its parameters."""
        self.calls.append(("POST", path, params))
        return object()


def test_login_url_encodes_credentials() -> None:
    """Verify that login encodes credentials inside URL segments."""
    request = FakeRequestContext()

    ParaBankApi(request).login("qa user", "p@ss word")

    assert request.calls == [("GET", "login/qa%20user/p%40ss%20word", None)]


def test_withdraw_serializes_decimal_parameters() -> None:
    """Verify that withdrawal values become API string parameters."""
    request = FakeRequestContext()

    ParaBankApi(request).withdraw(12345, Decimal("1.00"))

    assert request.calls == [
        ("POST", "withdraw", {"accountId": "12345", "amount": "1.00"})
    ]


def test_withdraw_omits_missing_amount() -> None:
    """Verify that an intentionally absent amount is not serialized."""
    request = FakeRequestContext()

    ParaBankApi(request).withdraw("12345", None)

    assert request.calls == [("POST", "withdraw", {"accountId": "12345"})]


def test_create_account_serializes_required_parameters() -> None:
    """Verify the parameter contract used to create another account."""
    request = FakeRequestContext()

    ParaBankApi(request).create_account(12212, 1, 12345)

    assert request.calls == [
        (
            "POST",
            "createAccount",
            {
                "customerId": "12212",
                "newAccountType": "1",
                "fromAccountId": "12345",
            },
        )
    ]


def test_transfer_serializes_account_and_amount_parameters() -> None:
    """Verify serialization of account IDs and the transfer amount."""
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
