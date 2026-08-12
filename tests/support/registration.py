"""Stable preconditions for customer registration scenarios."""

from core.exceptions import EnvironmentUnavailable


def register_valid_customer(registration_page, user) -> str:
    """Retry once if ParaBank discards a populated username during submission."""
    last_errors: list[str] = []
    for _ in range(2):
        registration_page.open()
        registration_page.register(user)
        try:
            return registration_page.success_text()
        except AssertionError:
            last_errors = registration_page.visible_error_messages()
            discarded_username = any(
                "username is required" in message.lower() for message in last_errors
            )
            if not discarded_username:
                raise

    raise EnvironmentUnavailable(
        "ParaBank discarded a populated username in two registration attempts: "
        f"{' | '.join(last_errors)}"
    )
