"""Page Object for transfers between ParaBank accounts."""

from __future__ import annotations

from decimal import Decimal

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, expect

from core.exceptions import EnvironmentUnavailable
from pages.base_page import BasePage


class TransferPage(BasePage):
    """Model the authenticated transfer form and confirmation panel."""

    def __init__(self, page: Page) -> None:
        """Define transfer inputs, account selectors, results, and errors."""
        super().__init__(page)
        self.heading = page.get_by_role("heading", name="Transfer Funds")
        self.amount_input = page.locator("#amount")
        self.source_select = page.locator("#fromAccountId")
        self.target_select = page.locator("#toAccountId")
        self.submit_button = page.locator('input[type="submit"][value="Transfer"]')
        self.result = page.locator("#showResult")
        self.errors = page.locator("#showForm .error")

    def open(self) -> None:
        """Open the transfer screen and wait until its selectors are populated."""
        self.page.get_by_role("link", name="Transfer Funds", exact=True).click()
        expect(self.heading).to_be_visible()
        expect(self.source_select).not_to_be_empty()
        expect(self.target_select).not_to_be_empty()

    def transfer(
        self, amount: str | Decimal, source_account: str, target_account: str
    ) -> None:
        """Submit a transfer using the specified amount and account identifiers."""
        self.amount_input.fill(str(amount))
        self.source_select.select_option(source_account)
        self.target_select.select_option(target_account)
        self.submit_button.click()

    def account_ids(self) -> list[str]:
        """Return distinct accounts that are present in both transfer selectors."""
        try:
            self.page.wait_for_function(
                """
                () => {
                  const source = [...document.querySelectorAll('#fromAccountId option')]
                    .map(option => option.value).filter(Boolean);
                  const target = new Set(
                    [...document.querySelectorAll('#toAccountId option')]
                      .map(option => option.value).filter(Boolean)
                  );
                  return [...new Set(source.filter(value => target.has(value)))].length >= 2;
                }
                """,
                timeout=5_000,
            )
        except PlaywrightTimeoutError as error:
            raise EnvironmentUnavailable(
                "ParaBank did not expose two consistent accounts in the transfer form"
            ) from error

        source_ids = self.source_select.locator("option").evaluate_all(
            "options => options.map(option => option.value).filter(Boolean)"
        )
        target_ids = set(
            self.target_select.locator("option").evaluate_all(
                "options => options.map(option => option.value).filter(Boolean)"
            )
        )
        return list(dict.fromkeys(value for value in source_ids if value in target_ids))

    def confirmation_text(self) -> str:
        """Wait for and return the successful-transfer confirmation."""
        expect(self.result).to_be_visible()
        return self.result.inner_text()

    def visible_error_messages(self) -> list[str]:
        """Return validation messages currently shown by the transfer form."""
        return [message.strip() for message in self.errors.all_inner_texts()]
