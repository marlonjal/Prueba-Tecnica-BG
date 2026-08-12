"""Page Object for transfers between ParaBank accounts."""

from __future__ import annotations

from decimal import Decimal

from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class TransferPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.heading = page.get_by_role("heading", name="Transfer Funds")
        self.amount_input = page.locator("#amount")
        self.source_select = page.locator("#fromAccountId")
        self.target_select = page.locator("#toAccountId")
        self.submit_button = page.locator('input[type="submit"][value="Transfer"]')
        self.result = page.locator("#showResult")
        self.errors = page.locator("#showForm .error")

    def open(self) -> None:
        self.page.get_by_role("link", name="Transfer Funds", exact=True).click()
        expect(self.heading).to_be_visible()
        expect(self.source_select).not_to_be_empty()
        expect(self.target_select).not_to_be_empty()

    def transfer(
        self, amount: str | Decimal, source_account: str, target_account: str
    ) -> None:
        self.amount_input.fill(str(amount))
        self.source_select.select_option(source_account)
        self.target_select.select_option(target_account)
        self.submit_button.click()

    def confirmation_text(self) -> str:
        expect(self.result).to_be_visible()
        return self.result.inner_text()

    def visible_error_messages(self) -> list[str]:
        return [message.strip() for message in self.errors.all_inner_texts()]
