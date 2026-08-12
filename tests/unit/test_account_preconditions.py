"""Unit tests for account preconditions used by transfer scenarios."""

import pytest

from core.exceptions import EnvironmentUnavailable
from tests.support.accounts import ensure_two_accounts


class FakeResponse:
    """Represent a successful account-creation response in isolation."""

    ok = True
    status = 200

    def json(self) -> dict:
        """Return the account payload expected from ParaBank."""
        return {"id": 67890, "customerId": 12212, "type": "SAVINGS"}


class TransientResponse(FakeResponse):
    """Represent a temporary ParaBank outage during account creation."""

    ok = False
    status = 503


class FakeApiClient:
    """Record account-creation calls without accessing the public API."""

    def __init__(self, response: FakeResponse | None = None) -> None:
        """Initialize the call history and configurable API response."""
        self.create_calls: list[tuple[int, int, int]] = []
        self.response = response or FakeResponse()

    def create_account(
        self, customer_id: int, account_type: int, source_account: int
    ) -> FakeResponse:
        """Record parameters and return a deterministic successful response."""
        self.create_calls.append((customer_id, account_type, source_account))
        return self.response

    @staticmethod
    def response_text(response: FakeResponse) -> str:
        """Satisfy the diagnostic response interface required by the helper."""
        return ""


def test_ensure_two_accounts_creates_only_the_missing_account() -> None:
    """Verify that one missing account triggers exactly one API creation."""
    api_client = FakeApiClient()
    session_data = {
        "customer": {"id": 12212},
        "accounts": [{"id": 12345, "type": "CHECKING"}],
    }

    accounts = ensure_two_accounts(api_client, session_data)

    assert [account["id"] for account in accounts] == [12345, 67890]
    assert api_client.create_calls == [(12212, 1, 12345)]


def test_ensure_two_accounts_reuses_existing_accounts() -> None:
    """Verify that an existing pair is reused without mutation."""
    api_client = FakeApiClient()
    session_data = {
        "customer": {"id": 12212},
        "accounts": [{"id": 12345}, {"id": 67890}],
    }

    accounts = ensure_two_accounts(api_client, session_data)

    assert len(accounts) == 2
    assert api_client.create_calls == []


def test_ensure_two_accounts_classifies_transient_api_outage() -> None:
    """Verify a temporary API response is skipped as an environment outage."""
    api_client = FakeApiClient(TransientResponse())
    session_data = {
        "customer": {"id": 12212},
        "accounts": [{"id": 12345, "type": "CHECKING"}],
    }

    with pytest.raises(EnvironmentUnavailable) as error:
        ensure_two_accounts(api_client, session_data)

    assert str(error.value) == (
        "ParaBank API returned HTTP 503 (temporary service outage) while creating "
        "the second transfer account; retry later"
    )
