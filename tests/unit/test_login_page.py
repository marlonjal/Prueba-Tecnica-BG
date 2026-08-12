"""Local contract test for LoginPage form actions."""

from playwright.sync_api import Page

from pages.login_page import LoginPage


def test_login_page_fills_credentials_and_submits(page: Page) -> None:
    page.set_content(
        """
        <form onsubmit="window.submitted = true; return false">
          <input name="username">
          <input name="password" type="password">
          <input type="submit" value="Log In">
        </form>
        """
    )
    login_page = LoginPage(page)

    login_page.login("qa-user", "qa-password")

    assert login_page.username_input.input_value() == "qa-user"
    assert login_page.password_input.input_value() == "qa-password"
    assert page.evaluate("window.submitted") is True
