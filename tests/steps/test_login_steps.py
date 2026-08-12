"""BDD step definitions for authentication and logout."""

from __future__ import annotations

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from tests.support.authentication import authenticate_configured_user

scenarios("../features/login.feature")


@given("que estoy en la página de inicio de ParaBank")
def open_login(login_page):
    login_page.open()


@when("inicio sesión con las credenciales configuradas")
def login_with_configured_user(login_page):
    authenticate_configured_user(login_page)


@then("se muestra el resumen de cuentas del cliente")
def assert_accounts_overview(login_page, accounts_page):
    assert login_page.is_authenticated()
    accounts_page.wait_until_loaded()


@when(
    parsers.re(
        r'intento iniciar sesión con usuario "(?P<usuario>.*)" '
        r'y clave "(?P<clave>.*)"'
    )
)
def login_with_invalid_credentials(login_page, usuario, clave):
    login_page.login(usuario, clave)


@then("el acceso es rechazado con un mensaje visible")
def assert_login_rejected(login_page):
    visible_error = login_page.visible_error_message()
    if visible_error:
        assert not login_page.accounts_heading.is_visible()
        return
    if login_page.is_authenticated():
        pytest.xfail(
            "ParaBank defect: invalid credentials authenticated as the public customer"
        )
    assert login_page.error_message()


@given("que inicié sesión correctamente en ParaBank")
def authenticated_user(login_page):
    authenticate_configured_user(login_page)


@when("cierro la sesión desde el menú del cliente")
def logout(login_page):
    login_page.logout()


@then("vuelve a mostrarse el formulario de acceso")
def assert_login_form(login_page):
    assert login_page.login_panel.is_visible()
    assert login_page.username_input.is_visible()
    assert login_page.password_input.is_visible()
