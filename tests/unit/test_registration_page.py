"""Local contract tests for RegistrationPage selectors and actions."""

from playwright.sync_api import Page

from models.user import UserFactory
from pages.registration_page import RegistrationPage


def test_registration_page_fills_every_customer_field(page: Page) -> None:
    """Verify that RegistrationPage maps every User field to its input."""
    inputs = "".join(
        f'<input name="{selector.split(chr(34))[1]}">'
        for selector in RegistrationPage.FIELD_SELECTORS.values()
    )
    page.set_content(f'{inputs}<input type="submit" value="Register">')
    user = UserFactory.valid()

    registration_page = RegistrationPage(page)
    registration_page.fill(user)

    for field, selector in RegistrationPage.FIELD_SELECTORS.items():
        assert page.locator(selector).input_value() == getattr(user, field)


def test_registration_page_leaves_omitted_field_empty(page: Page) -> None:
    """Verify that the requested field remains intentionally empty."""
    inputs = "".join(
        f'<input name="{selector.split(chr(34))[1]}">'
        for selector in RegistrationPage.FIELD_SELECTORS.values()
    )
    page.set_content(f'{inputs}<input type="submit" value="Register">')

    RegistrationPage(page).fill(UserFactory.valid(), omitted_field="username")

    assert page.locator('input[name="customer.username"]').input_value() == ""
