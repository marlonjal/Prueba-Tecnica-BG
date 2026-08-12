"""Service Object for ParaBank's public REST API."""

from __future__ import annotations

from decimal import Decimal
from urllib.parse import quote

from playwright.sync_api import APIRequestContext, APIResponse


class ParaBankApi:
    def __init__(self, request: APIRequestContext) -> None:
        self.request = request

    def login(self, username: str, password: str) -> APIResponse:
        return self.request.get(f"login/{quote(username)}/{quote(password)}")

    def customer_accounts(self, customer_id: int) -> APIResponse:
        return self.request.get(f"customers/{customer_id}/accounts")

    def account(self, account_id: int) -> APIResponse:
        return self.request.get(f"accounts/{account_id}")

    def transactions(self, account_id: int) -> APIResponse:
        return self.request.get(f"accounts/{account_id}/transactions")

    def withdraw(
        self, account_id: int | str, amount: Decimal | str | None
    ) -> APIResponse:
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
        params = {
            "fromAccountId": str(source_account),
            "toAccountId": str(target_account),
        }
        if amount is not None:
            params["amount"] = str(amount)
        return self.request.post("transfer", params=params)

    @staticmethod
    def response_text(response: APIResponse) -> str:
        return response.text()
