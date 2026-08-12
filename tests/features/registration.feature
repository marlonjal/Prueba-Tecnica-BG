@regression @ui
Feature: Registro de clientes
  Como nuevo cliente de ParaBank
  Quiero registrar mis datos y credenciales
  Para utilizar los servicios bancarios en línea

  @smoke @positive @destructive
  Scenario: Registro exitoso con todos los datos obligatorios
    Given que abro el formulario público de registro
    When envío datos únicos y válidos de un nuevo cliente
    Then la cuenta se crea y el cliente queda autenticado

  @negative
  Scenario Outline: Registro rechazado cuando falta un dato obligatorio
    Given que abro el formulario público de registro
    When envío el registro sin completar "<campo>"
    Then ParaBank informa que el campo "<campo>" es obligatorio

    Examples:
      | campo        |
      | first_name   |
      | last_name    |
      | street       |
      | city         |
      | state        |
      | zip_code     |
      | ssn          |
      | username     |
      | password     |
      | confirmation |

  @negative @destructive
  Scenario: Registro rechazado cuando las contraseñas no coinciden
    Given que abro el formulario público de registro
    When envío un registro cuyas contraseñas no coinciden
    Then ParaBank informa que las contraseñas deben coincidir

  @negative @destructive
  Scenario: Registro rechazado cuando el usuario ya existe
    Given que ya registré un cliente con un usuario único
    When intento registrar otro cliente con el mismo usuario
    Then ParaBank informa que el usuario ya existe
