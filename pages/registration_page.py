"""Page Object for ParaBank customer registration."""

from __future__ import annotations

from playwright.sync_api import Page, expect

from models.user import User
from pages.base_page import BasePage


class RegistrationPage(BasePage):
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
        super().__init__(page)
        self.heading = page.get_by_role("heading", name="Signing up is easy!")
        self.submit_button = page.locator('input[type="submit"][value="Register"]')
        self.errors = page.locator("#rightPanel .error")
        self.result_panel = page.locator("#rightPanel")

    def open(self) -> None:
        super().open("/register.htm")
        expect(self.heading).to_be_visible()

    def fill(self, user: User, omitted_field: str | None = None) -> None:
        for field, selector in self.FIELD_SELECTORS.items():
            if field != omitted_field:
                self.page.locator(selector).fill(getattr(user, field))

    def register(self, user: User, omitted_field: str | None = None) -> None:
        self.fill(user, omitted_field)
        self.submit_button.click()

    def success_text(self) -> str:
        expect(self.result_panel).to_contain_text("Your account was created successfully")
        return self.result_panel.inner_text()

    def error_messages(self) -> list[str]:
        expect(self.errors.first).to_be_visible()
        return [message.strip() for message in self.errors.all_inner_texts()]
