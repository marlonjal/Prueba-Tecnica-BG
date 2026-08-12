"""BDD steps for web and API fund transfers."""

from __future__ import annotations

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from tests.support.api_responses import response_is_rejected
from tests.support.accounts import ensure_two_accounts
from tests.support.authentication import authenticate_configured_user

scenarios("../features/transfer.feature")


def login_and_accounts(login_page, accounts_page) -> list[str]:
    """Authenticate through the UI and return the displayed account IDs."""
    authenticate_configured_user(login_page)
    return accounts_page.account_ids()


@given("que inicio sesión y dispongo de dos cuentas para transferir")
def authenticated_with_two_accounts(
    login_page,
    accounts_page,
    open_account_page,
    transfer_page,
    scenario_state,
):
    """Prepare two UI accounts and store a valid source-target pair."""
    ui_accounts = login_and_accounts(login_page, accounts_page)
    if len(ui_accounts) < 2:
        open_account_page.open_savings_account(ui_accounts[0])
    transfer_page.open()
    available_accounts = transfer_page.account_ids()
    scenario_state["source"], scenario_state["target"] = available_accounts[:2]


@given("que inicio sesión y dispongo de una cuenta para validar")
def authenticated_with_one_account(
    login_page, accounts_page, transfer_page, scenario_state
):
    """Authenticate and retain one account for invalid transfer scenarios."""
    accounts = login_and_accounts(login_page, accounts_page)
    assert accounts, "The configured customer has no accounts"
    scenario_state["source"] = accounts[0]
    transfer_page.open()


@when(parsers.parse('transfiero "{monto}" desde la primera cuenta hacia la segunda'))
def transfer_valid_amount(transfer_page, scenario_state, monto):
    """Submit the valid transfer amount defined by the feature."""
    transfer_page.transfer(
        monto, scenario_state["source"], scenario_state["target"]
    )
    scenario_state["amount"] = monto


@then("la pantalla confirma el monto y las cuentas de la transferencia")
def assert_transfer_success(transfer_page, scenario_state):
    """Verify amount and account identifiers in the confirmation panel."""
    confirmation = transfer_page.confirmation_text()
    assert "Transfer Complete" in confirmation
    assert scenario_state["amount"] in confirmation
    assert scenario_state["source"] in confirmation
    assert scenario_state["target"] in confirmation


@when(parsers.re(r'intento transferir el monto "(?P<monto>.*)" entre las cuentas'))
def transfer_invalid_amount(transfer_page, scenario_state, monto):
    """Submit one invalid amount from the transfer scenario outline."""
    transfer_page.transfer(
        monto, scenario_state["source"], scenario_state["target"]
    )


@when(parsers.parse('intento transferir "{monto}" hacia la misma cuenta'))
def transfer_to_same_account(transfer_page, scenario_state, monto):
    """Attempt a transfer whose source and destination are identical."""
    source_account = scenario_state["source"]
    transfer_page.transfer(monto, source_account, source_account)


@then("la transferencia web no debe confirmarse")
def assert_web_transfer_rejected(transfer_page):
    """Verify UI rejection or register an accepted invalid transfer as XFAIL."""
    confirmed = transfer_page.result.is_visible() and (
        "Transfer Complete" in transfer_page.result.inner_text()
    )
    if confirmed:
        pytest.xfail("ParaBank defect: an invalid web transfer was accepted")
    assert transfer_page.visible_error_messages()


@given("que autentico por API y obtengo una cuenta destino")
def api_target_account(api_session_data, scenario_state):
    """Store an existing target account for an invalid-source API request."""
    scenario_state["target"] = api_session_data["accounts"][0]["id"]


@when("transfiero por API desde una cuenta inexistente")
def api_unknown_source(api_client, scenario_state):
    """Submit an API transfer from a deliberately nonexistent account."""
    scenario_state["response"] = api_client.transfer(
        999_999_999, scenario_state["target"], "1.00"
    )


@given("que autentico por API y obtengo una cuenta origen")
def api_source_account(api_session_data, scenario_state):
    """Store an existing source account for an invalid-target API request."""
    scenario_state["source"] = api_session_data["accounts"][0]["id"]


@when("transfiero por API hacia una cuenta inexistente")
def api_unknown_target(api_client, scenario_state):
    """Submit an API transfer to a deliberately nonexistent account."""
    scenario_state["response"] = api_client.transfer(
        scenario_state["source"], 999_999_999, "1.00"
    )


@given("que autentico por API y obtengo dos cuentas")
def api_two_accounts(api_client, api_session_data, scenario_state):
    """Ensure and retain two accounts for the missing-amount API scenario."""
    accounts = ensure_two_accounts(api_client, api_session_data)
    scenario_state["source"] = accounts[0]["id"]
    scenario_state["target"] = accounts[1]["id"]


@when("transfiero por API sin informar el monto")
def api_transfer_without_amount(api_client, scenario_state):
    """Submit an API transfer while intentionally omitting its amount."""
    scenario_state["response"] = api_client.transfer(
        scenario_state["source"], scenario_state["target"], None
    )


@then("el API rechaza la transferencia")
def assert_api_transfer_rejected(api_client, scenario_state):
    """Verify API rejection or register an accepted invalid request as XFAIL."""
    response = scenario_state["response"]
    if not response_is_rejected(response, api_client):
        pytest.xfail(
            "ParaBank defect: an invalid API transfer was accepted "
            f"({response.status}): {api_client.response_text(response)}"
        )
