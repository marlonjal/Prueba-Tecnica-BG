"""Unit tests for isolated customer test data."""

from models.user import UserFactory


def test_user_factory_generates_unique_valid_credentials() -> None:
    first = UserFactory.valid()
    second = UserFactory.valid()

    assert first.username != second.username
    assert first.password == first.confirmation
    assert second.password == second.confirmation
    assert len(first.ssn) == 9
