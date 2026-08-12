@regression @ui
Feature: Inicio de sesión
  Como cliente registrado de ParaBank
  Quiero autenticarme y cerrar mi sesión
  Para acceder de manera segura a mis cuentas

  @smoke @positive
  Scenario: Inicio de sesión exitoso
    Given que estoy en la página de inicio de ParaBank
    When inicio sesión con las credenciales configuradas
    Then se muestra el resumen de cuentas del cliente

  @negative
  Scenario Outline: Inicio de sesión rechazado con credenciales inválidas
    Given que estoy en la página de inicio de ParaBank
    When intento iniciar sesión con usuario "<usuario>" y clave "<clave>"
    Then el acceso es rechazado con un mensaje visible

    Examples:
      | usuario             | clave          |
      |                     | demo           |
      | john                |                |
      | usuario_inexistente | demo           |
      | john                | clave_invalida |

  @positive
  Scenario: Cierre de sesión exitoso
    Given que inicié sesión correctamente en ParaBank
    When cierro la sesión desde el menú del cliente
    Then vuelve a mostrarse el formulario de acceso
