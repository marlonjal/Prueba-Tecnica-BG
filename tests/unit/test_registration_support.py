"""Unit tests for stable customer-registration preconditions."""

import pytest

from core.exceptions import EnvironmentUnavailable
from tests.support.registration import register_valid_customer


class FakeRegistrationPage:
    """Simulate transient and successful registration responses."""

    def __init__(self, outcomes: list[str]) -> None:
        """Store sequential outcomes and reset the attempt counter."""
        self.outcomes = outcomes
        self.attempts = 0

    def open(self) -> None:
        """Satisfy the helper interface without real navigation."""
        pass

    def register(self, user) -> None:
        """Record one simulated form submission."""
        del user
        self.attempts += 1

    def success_text(self) -> str:
        """Return success or raise the configured transient assertion."""
        outcome = self.outcomes[self.attempts - 1]
        if outcome == "success":
            return "Your account was created successfully"
        raise AssertionError("registration rejected")

    @staticmethod
    def visible_error_messages() -> list[str]:
        """Return the anomaly produced by a discarded username."""
        return ["Username is required."]


def test_valid_registration_retries_a_discarded_username_once() -> None:
    """Verify recovery when the first valid username is discarded."""
    registration_page = FakeRegistrationPage(["discarded", "success"])

    result = register_valid_customer(registration_page, object())

    assert "created successfully" in result
    assert registration_page.attempts == 2


def test_repeated_discarded_username_is_environment_unavailable() -> None:
    """Verify repeated username loss is an environment failure."""
    registration_page = FakeRegistrationPage(["discarded", "discarded"])

    with pytest.raises(EnvironmentUnavailable, match="discarded a populated username"):
        register_valid_customer(registration_page, object())
