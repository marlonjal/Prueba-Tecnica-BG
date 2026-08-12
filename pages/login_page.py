"""Page Object for ParaBank authentication."""

from __future__ import annotations

from playwright.sync_api import Page, expect

from config.settings import settings
from pages.base_page import BasePage


class LoginPage(BasePage):
    """Model login, authenticated-state detection, and logout actions."""

    def __init__(self, page: Page) -> None:
        """Define locators used by the public login form and account menu."""
        super().__init__(page)
        self.username_input = page.locator('input[name="username"]')
        self.password_input = page.locator('input[name="password"]')
        self.submit_button = page.locator('input[type="submit"][value="Log In"]')
        self.login_panel = page.locator("#loginPanel")
        self.error = page.locator("#rightPanel .error")
        self.accounts_heading = page.get_by_role("heading", name="Accounts Overview")

    def open(self) -> None:
        """Navigate to the home page and wait for the login form."""
        super().open("/index.htm")
        expect(self.login_panel).to_be_visible()

    def login(self, username: str, password: str) -> None:
        """Submit the supplied credentials through the public login form."""
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.submit_button.click()

    def is_authenticated(self) -> bool:
        """Report whether the authenticated account overview is visible."""
        try:
            expect(self.accounts_heading).to_be_visible(timeout=settings.default_timeout)
            return True
        except AssertionError:
            return False

    def error_message(self) -> str:
        """Wait for and return the login rejection message."""
        expect(self.error).to_be_visible()
        return self.error.inner_text().strip()

    def visible_error_message(self) -> str:
        """Return the current rejection message without waiting for it."""
        return self.error.inner_text().strip() if self.error.is_visible() else ""

    def logout(self) -> None:
        """Close the active customer session through the navigation menu."""
        self.page.get_by_role("link", name="Log Out", exact=True).click()
        expect(self.login_panel).to_be_visible()
