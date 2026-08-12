"""Unit tests for shared-environment authentication policy."""

from types import SimpleNamespace

import pytest

from core.exceptions import EnvironmentUnavailable
from tests.support import authentication


class FakeLoginPage:
    def __init__(self, outcomes: list[bool], error: str = "login rejected") -> None:
        self.outcomes = iter(outcomes)
        self.error = error
        self.open_calls = 0
        self.login_calls: list[tuple[str, str]] = []

    def open(self) -> None:
        self.open_calls += 1

    def login(self, username: str, password: str) -> None:
        self.login_calls.append((username, password))

    def is_authenticated(self) -> bool:
        return next(self.outcomes)

    def visible_error_message(self) -> str:
        return self.error


def set_credentials(monkeypatch, username: str, password: str) -> None:
    monkeypatch.setattr(
        authentication,
        "settings",
        SimpleNamespace(username=username, password=password),
    )


def test_configured_login_retries_once_and_recovers(monkeypatch) -> None:
    set_credentials(monkeypatch, "john", "demo")
    login_page = FakeLoginPage([False, True])

    authentication.authenticate_configured_user(login_page)

    assert login_page.open_calls == 2
    assert login_page.login_calls == [("john", "demo"), ("john", "demo")]


def test_public_credentials_rejection_is_environment_unavailable(monkeypatch) -> None:
    set_credentials(monkeypatch, "john", "demo")
    login_page = FakeLoginPage([False, False], "could not verify identity")

    with pytest.raises(EnvironmentUnavailable, match="john/demo"):
        authentication.authenticate_configured_user(login_page)


def test_custom_credentials_rejection_remains_a_failure(monkeypatch) -> None:
    set_credentials(monkeypatch, "custom-user", "custom-password")
    login_page = FakeLoginPage([False, False])

    with pytest.raises(AssertionError, match="PARABANK_USERNAME"):
        authentication.authenticate_configured_user(login_page)
