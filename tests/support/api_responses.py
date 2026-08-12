"""Shared classification of ParaBank API error responses."""

from core.exceptions import EnvironmentUnavailable

TRANSIENT_HTTP_STATUSES = {429, 502, 503, 504}


def raise_for_transient_response(response, api_client, operation: str) -> None:
    """Prevent infrastructure outages from becoming functional results."""
    if response.status in TRANSIENT_HTTP_STATUSES:
        raise EnvironmentUnavailable(
            f"ParaBank API returned HTTP {response.status} while {operation}: "
            f"{api_client.response_text(response)}"
        )


def response_is_rejected(response, api_client) -> bool:
    """Return whether ParaBank rejected a request for a functional reason."""
    raise_for_transient_response(response, api_client, "validating a rejected request")
    response_text = api_client.response_text(response).lower()
    return not response.ok or any(
        token in response_text
        for token in ("error", "invalid", "could not", "not found", "insufficient")
    )
