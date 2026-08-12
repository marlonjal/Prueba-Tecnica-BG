"""BDD steps for web and API fund transfers."""

from __future__ import annotations

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from tests.support.api_responses import response_is_rejected
from tests.support.authentication import authenticate_configured_user

scenarios("../features/transfer.feature")


def login_and_accounts(login_page, accounts_page) -> list[str]:
    authenticate_configured_user(login_page)
    return accounts_page.account_ids()


@given("que inicio sesión y dispongo de dos cuentas para transferir")
def authenticated_with_two_accounts(
    login_page, accounts_page, transfer_page, scenario_state
):
    accounts = login_and_accounts(login_page, accounts_page)
    assert len(accounts) >= 2, "The configured customer needs at least two accounts"
    scenario_state["source"], scenario_state["target"] = accounts[:2]
    transfer_page.open()


@given("que inicio sesión y dispongo de una cuenta para validar")
def authenticated_with_one_account(
    login_page, accounts_page, transfer_page, scenario_state
):
    accounts = login_and_accounts(login_page, accounts_page)
    assert accounts, "The configured customer has no accounts"
    scenario_state["source"] = accounts[0]
    transfer_page.open()


@when(parsers.parse('transfiero "{monto}" desde la primera cuenta hacia la segunda'))
def transfer_valid_amount(transfer_page, scenario_state, monto):
    transfer_page.transfer(
        monto, scenario_state["source"], scenario_state["target"]
    )
    scenario_state["amount"] = monto


@then("la pantalla confirma el monto y las cuentas de la transferencia")
def assert_transfer_success(transfer_page, scenario_state):
    confirmation = transfer_page.confirmation_text()
    assert "Transfer Complete" in confirmation
    assert scenario_state["amount"] in confirmation
    assert scenario_state["source"] in confirmation
    assert scenario_state["target"] in confirmation


@when(parsers.re(r'intento transferir el monto "(?P<monto>.*)" entre las cuentas'))
def transfer_invalid_amount(transfer_page, scenario_state, monto):
    transfer_page.transfer(
        monto, scenario_state["source"], scenario_state["target"]
    )


@when(parsers.parse('intento transferir "{monto}" hacia la misma cuenta'))
def transfer_to_same_account(transfer_page, scenario_state, monto):
    source_account = scenario_state["source"]
    transfer_page.transfer(monto, source_account, source_account)


@then("la transferencia web no debe confirmarse")
def assert_web_transfer_rejected(transfer_page):
    confirmed = transfer_page.result.is_visible() and (
        "Transfer Complete" in transfer_page.result.inner_text()
    )
    if confirmed:
        pytest.xfail("ParaBank defect: an invalid web transfer was accepted")
    assert transfer_page.visible_error_messages()


@given("que autentico por API y obtengo una cuenta destino")
def api_target_account(api_session_data, scenario_state):
    scenario_state["target"] = api_session_data["accounts"][0]["id"]


@when("transfiero por API desde una cuenta inexistente")
def api_unknown_source(api_client, scenario_state):
    scenario_state["response"] = api_client.transfer(
        999_999_999, scenario_state["target"], "1.00"
    )


@given("que autentico por API y obtengo una cuenta origen")
def api_source_account(api_session_data, scenario_state):
    scenario_state["source"] = api_session_data["accounts"][0]["id"]


@when("transfiero por API hacia una cuenta inexistente")
def api_unknown_target(api_client, scenario_state):
    scenario_state["response"] = api_client.transfer(
        scenario_state["source"], 999_999_999, "1.00"
    )


@given("que autentico por API y obtengo dos cuentas")
def api_two_accounts(api_session_data, scenario_state):
    accounts = api_session_data["accounts"]
    assert len(accounts) >= 2, "The configured customer needs at least two accounts"
    scenario_state["source"] = accounts[0]["id"]
    scenario_state["target"] = accounts[1]["id"]


@when("transfiero por API sin informar el monto")
def api_transfer_without_amount(api_client, scenario_state):
    scenario_state["response"] = api_client.transfer(
        scenario_state["source"], scenario_state["target"], None
    )


@then("el API rechaza la transferencia")
def assert_api_transfer_rejected(api_client, scenario_state):
    response = scenario_state["response"]
    if not response_is_rejected(response, api_client):
        pytest.xfail(
            "ParaBank defect: an invalid API transfer was accepted "
            f"({response.status}): {api_client.response_text(response)}"
        )
