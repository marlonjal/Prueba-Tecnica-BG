"""Page Object for creating another account in the authenticated UI session."""

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, expect

from core.exceptions import EnvironmentUnavailable
from pages.base_page import BasePage


class OpenAccountPage(BasePage):
    """Model creation of a second account within the active UI session."""

    def __init__(self, page: Page) -> None:
        """Define navigation, form controls, and result locators."""
        super().__init__(page)
        self.link = page.get_by_role("link", name="Open New Account", exact=True)
        self.heading = page.get_by_role("heading", name="Open New Account")
        self.account_type = page.locator("#type")
        self.source_account = page.locator("#fromAccountId")
        self.submit_button = page.locator(
            'input[type="submit"][value="Open New Account"]'
        )
        self.result = page.locator("#openAccountResult")
        self.new_account = page.locator("#newAccountId")

    def open_savings_account(self, source_account: str) -> str:
        """Create a savings account funded from the supplied source account."""
        try:
            self.link.click()
            expect(self.heading).to_be_visible()
            self.account_type.select_option(label="SAVINGS")
            self.source_account.select_option(source_account)
            self.submit_button.click()
            expect(self.result).to_be_visible()
            expect(self.new_account).to_be_visible()
        except (AssertionError, PlaywrightTimeoutError) as error:
            self.raise_if_security_challenge()
            raise EnvironmentUnavailable(
                "ParaBank could not create the second UI account required by "
                "the transfer scenario"
            ) from error
        return self.new_account.inner_text().strip()
