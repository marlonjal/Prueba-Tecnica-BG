"""Page Object for the authenticated account overview."""

from __future__ import annotations

from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class AccountsPage(BasePage):
    """Model the authenticated account-overview screen."""

    def __init__(self, page: Page) -> None:
        """Define stable locators for the overview and account links."""
        super().__init__(page)
        self.heading = page.get_by_role("heading", name="Accounts Overview")
        self.table = page.locator("#accountTable")
        self.account_links = page.locator("#accountTable tbody tr td:first-child a")

    def wait_until_loaded(self) -> None:
        """Wait until the overview and at least one account are visible."""
        expect(self.heading).to_be_visible()
        expect(self.table).to_be_visible()
        expect(self.account_links.first).to_be_visible()

    def account_ids(self) -> list[str]:
        """Return the account identifiers displayed in the overview table."""
        self.wait_until_loaded()
        return [account.strip() for account in self.account_links.all_inner_texts()]
