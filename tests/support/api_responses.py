"""Shared classification of ParaBank API error responses."""


def response_is_rejected(response, api_client) -> bool:
    response_text = api_client.response_text(response).lower()
    return not response.ok or any(
        token in response_text
        for token in ("error", "invalid", "could not", "not found", "insufficient")
    )
