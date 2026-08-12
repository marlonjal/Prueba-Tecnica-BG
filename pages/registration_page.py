"""Page Object for ParaBank customer registration."""

from __future__ import annotations

from playwright.sync_api import Page, expect

from models.user import User
from pages.base_page import BasePage


class RegistrationPage(BasePage):
    """Model the public customer-registration form and its outcomes."""

    FIELD_SELECTORS = {
        "first_name": 'input[name="customer.firstName"]',
        "last_name": 'input[name="customer.lastName"]',
        "street": 'input[name="customer.address.street"]',
        "city": 'input[name="customer.address.city"]',
        "state": 'input[name="customer.address.state"]',
        "zip_code": 'input[name="customer.address.zipCode"]',
        "phone": 'input[name="customer.phoneNumber"]',
        "ssn": 'input[name="customer.ssn"]',
        "username": 'input[name="customer.username"]',
        "password": 'input[name="customer.password"]',
        "confirmation": 'input[name="repeatedPassword"]',
    }

    def __init__(self, page: Page) -> None:
        """Define form, result, and validation-message locators."""
        super().__init__(page)
        self.heading = page.get_by_role("heading", name="Signing up is easy!")
        self.submit_button = page.locator('input[type="submit"][value="Register"]')
        self.errors = page.locator("#rightPanel .error")
        self.result_panel = page.locator("#rightPanel")

    def open(self) -> None:
        """Navigate to the public registration form and wait for its heading."""
        super().open("/register.htm")
        expect(self.heading).to_be_visible()

    def fill(self, user: User, omitted_field: str | None = None) -> None:
        """Fill customer data while optionally leaving one field empty."""
        for field, selector in self.FIELD_SELECTORS.items():
            if field != omitted_field:
                self.page.locator(selector).fill(getattr(user, field))

    def register(self, user: User, omitted_field: str | None = None) -> None:
        """Fill and submit a customer-registration request."""
        self.fill(user, omitted_field)
        self.submit_button.click()

    def success_text(self) -> str:
        """Return the successful registration panel or classify anti-bot blocks."""
        try:
            expect(self.result_panel).to_contain_text(
                "Your account was created successfully"
            )
        except AssertionError:
            self.raise_if_security_challenge()
            raise
        return self.result_panel.inner_text()

    def error_messages(self) -> list[str]:
        """Wait for and return registration validation messages."""
        try:
            expect(self.errors.first).to_be_visible()
        except AssertionError:
            self.raise_if_security_challenge()
            raise
        return self.visible_error_messages()

    def visible_error_messages(self) -> list[str]:
        """Return currently rendered validation messages without waiting."""
        return [message.strip() for message in self.errors.all_inner_texts()]
