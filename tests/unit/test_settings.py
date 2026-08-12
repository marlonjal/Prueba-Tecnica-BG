"""Unit tests for environment parsing."""

import pytest

from config.settings import env_bool, env_int


@pytest.mark.parametrize("value", ["1", "true", "TRUE", "yes"])
def test_env_bool_accepts_supported_truthy_values(monkeypatch, value: str) -> None:
    monkeypatch.setenv("TEST_BOOLEAN", value)
    assert env_bool("TEST_BOOLEAN", False) is True


def test_env_bool_uses_default_when_variable_is_missing(monkeypatch) -> None:
    monkeypatch.delenv("TEST_BOOLEAN", raising=False)
    assert env_bool("TEST_BOOLEAN", True) is True


def test_env_int_reads_integer_value(monkeypatch) -> None:
    monkeypatch.setenv("TEST_INTEGER", "25000")
    assert env_int("TEST_INTEGER", 1000) == 25_000
