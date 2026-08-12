"""BDD step definitions for customer registration."""

from __future__ import annotations

from dataclasses import replace

from pytest_bdd import given, parsers, scenarios, then, when

from models.user import UserFactory

scenarios("../features/registration.feature")

FIELD_LABELS = {
    "first_name": "First name",
    "last_name": "Last name",
    "street": "Address",
    "city": "City",
    "state": "State",
    "zip_code": "Zip Code",
    "ssn": "Social Security Number",
    "username": "Username",
    "password": "Password",
    "confirmation": "Password confirmation",
}


@given("que abro el formulario público de registro")
def open_registration(registration_page):
    registration_page.open()


@when("envío datos únicos y válidos de un nuevo cliente")
def register_valid_user(registration_page, valid_user, scenario_state):
    scenario_state["user"] = valid_user
    registration_page.register(valid_user)


@then("la cuenta se crea y el cliente queda autenticado")
def assert_registration_success(registration_page, scenario_state):
    user = scenario_state["user"]
    result = registration_page.success_text()
    assert f"Welcome {user.username}" in result


@when(parsers.parse('envío el registro sin completar "{campo}"'))
def register_without_field(registration_page, valid_user, campo):
    assert campo in FIELD_LABELS, f"Unsupported BDD field: {campo}"
    registration_page.register(valid_user, omitted_field=campo)


@then(parsers.parse('ParaBank informa que el campo "{campo}" es obligatorio'))
def assert_required_field(registration_page, campo):
    errors = " | ".join(registration_page.error_messages()).lower()
    label = FIELD_LABELS[campo].lower()
    assert "required" in errors
    assert label in errors


@when("envío un registro cuyas contraseñas no coinciden")
def register_password_mismatch(registration_page, valid_user):
    mismatched_user = replace(valid_user, confirmation="DifferentPassword!123")
    registration_page.register(mismatched_user)


@then("ParaBank informa que las contraseñas deben coincidir")
def assert_password_mismatch(registration_page):
    errors = " | ".join(registration_page.error_messages()).lower()
    assert "password" in errors and "match" in errors


@given("que ya registré un cliente con un usuario único")
def register_existing_user(registration_page, valid_user, scenario_state):
    registration_page.open()
    registration_page.register(valid_user)
    assert "created successfully" in registration_page.success_text()
    scenario_state["existing_user"] = valid_user


@when("intento registrar otro cliente con el mismo usuario")
def register_duplicate_username(registration_page, scenario_state):
    duplicate = replace(
        UserFactory.valid(), username=scenario_state["existing_user"].username
    )
    registration_page.open()
    registration_page.register(duplicate)


@then("ParaBank informa que el usuario ya existe")
def assert_duplicate_username(registration_page):
    errors = " | ".join(registration_page.error_messages()).lower()
    assert "username" in errors and ("exists" in errors or "already" in errors)
