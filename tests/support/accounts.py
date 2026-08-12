"""Reusable account preconditions for destructive transfer scenarios."""

from services.parabank_api import ParaBankApi
from tests.support.api_responses import raise_for_transient_response


def ensure_two_accounts(
    api_client: ParaBankApi, api_session_data: dict
) -> list[dict]:
    """Create a savings account only when the public customer has one account."""
    accounts = api_session_data["accounts"]
    if len(accounts) >= 2:
        return accounts

    source_account = accounts[0]
    response = api_client.create_account(
        customer_id=api_session_data["customer"]["id"],
        account_type=1,
        source_account=source_account["id"],
    )
    raise_for_transient_response(
        response, api_client, "creating the second transfer account"
    )
    assert response.ok, (
        f"Could not create the second transfer account ({response.status}): "
        f"{api_client.response_text(response)}"
    )
    created_account = response.json()
    assert created_account["id"] != source_account["id"]
    accounts.append(created_account)
    return accounts
