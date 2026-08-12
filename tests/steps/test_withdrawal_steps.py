"""BDD steps for withdrawals through Playwright APIRequestContext."""

from __future__ import annotations

from decimal import Decimal

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from tests.support.api_responses import (
    raise_for_transient_response,
    response_is_rejected,
)

scenarios("../features/withdrawal.feature")

@given("que autentico por API al cliente configurado y obtengo una cuenta")
def authenticated_account(api_session_data, scenario_state):
    """Store one authenticated account for the current withdrawal scenario."""
    scenario_state["account"] = api_session_data["accounts"][0]


@when(parsers.parse('retiro "{monto}" de la cuenta seleccionada'))
def withdraw_valid_amount(api_client, scenario_state, monto):
    """Read the initial balance and submit a valid withdrawal."""
    account_id = scenario_state["account"]["id"]
    account_response = api_client.account(account_id)
    raise_for_transient_response(
        account_response, api_client, "reading the initial balance"
    )
    assert account_response.ok
    scenario_state["balance_before"] = Decimal(
        str(account_response.json()["balance"])
    )
    scenario_state["response"] = api_client.withdraw(account_id, monto)


@then("el API confirma el retiro")
def assert_withdrawal_success(api_client, scenario_state):
    """Verify that the API confirms a successful withdrawal."""
    response = scenario_state["response"]
    raise_for_transient_response(response, api_client, "withdrawing funds")
    assert response.ok, (
        f"Withdrawal failed ({response.status}): {api_client.response_text(response)}"
    )
    response_text = api_client.response_text(response).lower()
    assert "success" in response_text or "withdraw" in response_text


@then(parsers.parse('el saldo de la cuenta disminuye en "{monto}"'))
def assert_balance_decreased(api_client, scenario_state, monto):
    """Verify that the final balance decreased by the requested amount."""
    account_id = scenario_state["account"]["id"]
    account_response = api_client.account(account_id)
    raise_for_transient_response(
        account_response, api_client, "reading the final balance"
    )
    assert account_response.ok
    actual_balance = Decimal(str(account_response.json()["balance"]))
    expected_balance = scenario_state["balance_before"] - Decimal(monto)
    assert actual_balance == expected_balance


@then(parsers.parse('se registra una transacción débito por "{monto}"'))
def assert_debit_transaction(api_client, scenario_state, monto):
    """Verify that transaction history contains the expected debit."""
    account_id = scenario_state["account"]["id"]
    response = api_client.transactions(account_id)
    raise_for_transient_response(response, api_client, "reading account transactions")
    assert response.ok
    expected_amount = Decimal(monto)
    matching_transactions = [
        transaction
        for transaction in response.json()
        if transaction.get("type", "").lower() == "debit"
        and Decimal(str(transaction.get("amount"))) == expected_amount
    ]
    assert matching_transactions


@when(parsers.parse('intento retirar el monto "{monto}" de la cuenta seleccionada'))
def withdraw_invalid_amount(api_client, scenario_state, monto):
    """Submit one invalid withdrawal amount from the scenario outline."""
    scenario_state["response"] = api_client.withdraw(
        scenario_state["account"]["id"], monto
    )


@when("intento retirar sin enviar el monto")
def withdraw_without_amount(api_client, scenario_state):
    """Submit a withdrawal request without the amount parameter."""
    scenario_state["response"] = api_client.withdraw(
        scenario_state["account"]["id"], None
    )


@when(parsers.parse('intento retirar "{monto}" de una cuenta inexistente por API'))
def withdraw_unknown_account(api_client, scenario_state, monto):
    """Submit a withdrawal against a deliberately nonexistent account."""
    scenario_state["response"] = api_client.withdraw(999_999_999, monto)


@when("intento retirar un monto superior al saldo disponible")
def withdraw_over_balance(api_client, scenario_state):
    """Build and submit an amount guaranteed to exceed the known balance."""
    account = scenario_state["account"]
    amount = Decimal(str(account["balance"])) + Decimal("1000000")
    scenario_state["response"] = api_client.withdraw(account["id"], amount)


@then("el API rechaza la operación de retiro")
def assert_withdrawal_rejected(api_client, scenario_state):
    """Verify rejection or register an accepted invalid withdrawal as XFAIL."""
    response = scenario_state["response"]
    if not response_is_rejected(response, api_client):
        pytest.xfail(
            "ParaBank defect: an invalid withdrawal was accepted "
            f"({response.status}): {api_client.response_text(response)}"
        )
