"""Stable authentication for scenarios using the configured customer."""

from config.settings import settings
from core.exceptions import EnvironmentUnavailable
from pages.login_page import LoginPage


def authenticate_configured_user(login_page: LoginPage) -> None:
    """Authenticate and retry once when the shared demo environment rejects login."""
    errors: list[str] = []

    for _ in range(2):
        login_page.open()
        login_page.login(settings.username, settings.password)
        if login_page.is_authenticated():
            return
        errors.append(login_page.visible_error_message() or "no response message")

    detail = errors[-1]
    if settings.username == "john" and settings.password == "demo":
        raise EnvironmentUnavailable(
            f"ParaBank rejected public credentials john/demo twice: {detail}"
        )
    raise AssertionError(
        "ParaBank rejected the configured credentials after two attempts: "
        f"{detail}. Check PARABANK_USERNAME and PARABANK_PASSWORD."
    )
