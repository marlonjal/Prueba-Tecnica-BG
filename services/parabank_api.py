"""Service Object for ParaBank's public REST API."""

from __future__ import annotations

from decimal import Decimal
from urllib.parse import quote

from playwright.sync_api import APIRequestContext, APIResponse


class ParaBankApi:
    """Encapsulate calls to the public ParaBank REST API."""

    def __init__(self, request: APIRequestContext) -> None:
        """Store the Playwright request context shared by API scenarios."""
        self.request = request

    def login(self, username: str, password: str) -> APIResponse:
        """Authenticate credentials and return the customer response."""
        return self.request.get(f"login/{quote(username)}/{quote(password)}")

    def customer_accounts(self, customer_id: int) -> APIResponse:
        """Request all accounts owned by a customer."""
        return self.request.get(f"customers/{customer_id}/accounts")

    def create_account(
        self, customer_id: int, account_type: int, source_account: int
    ) -> APIResponse:
        """Create an account of the requested type from a source account."""
        return self.request.post(
            "createAccount",
            params={
                "customerId": str(customer_id),
                "newAccountType": str(account_type),
                "fromAccountId": str(source_account),
            },
        )

    def account(self, account_id: int) -> APIResponse:
        """Request the current details and balance of one account."""
        return self.request.get(f"accounts/{account_id}")

    def transactions(self, account_id: int) -> APIResponse:
        """Request the transaction history associated with an account."""
        return self.request.get(f"accounts/{account_id}/transactions")

    def withdraw(
        self, account_id: int | str, amount: Decimal | str | None
    ) -> APIResponse:
        """Submit a withdrawal, omitting the amount when it is intentionally absent."""
        params = {"accountId": str(account_id)}
        if amount is not None:
            params["amount"] = str(amount)
        return self.request.post("withdraw", params=params)

    def transfer(
        self,
        source_account: int | str,
        target_account: int | str,
        amount: Decimal | str | None,
    ) -> APIResponse:
        """Submit a transfer between accounts with an optional amount."""
        params = {
            "fromAccountId": str(source_account),
            "toAccountId": str(target_account),
        }
        if amount is not None:
            params["amount"] = str(amount)
        return self.request.post("transfer", params=params)

    @staticmethod
    def response_text(response: APIResponse) -> str:
        """Return an API response body as text for assertions and diagnostics."""
        return response.text()
