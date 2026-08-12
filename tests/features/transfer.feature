@regression @destructive
Feature: Transferencia de fondos entre cuentas
  Como cliente autenticado de ParaBank
  Quiero transferir dinero entre mis cuentas
  Para administrar mis fondos

  @smoke @positive @ui
  Scenario: Transferencia web exitosa entre dos cuentas distintas
    Given que inicio sesión y dispongo de dos cuentas para transferir
    When transfiero "1.00" desde la primera cuenta hacia la segunda
    Then la pantalla confirma el monto y las cuentas de la transferencia

  @negative @ui
  Scenario Outline: Transferencia web rechazada con monto inválido
    Given que inicio sesión y dispongo de dos cuentas para transferir
    When intento transferir el monto "<monto>" entre las cuentas
    Then la transferencia web no debe confirmarse

    Examples:
      | monto |
      |       |
      | 0     |
      | -1    |
      | abc   |

  @negative @ui
  Scenario: Transferencia web rechazada hacia la misma cuenta de origen
    Given que inicio sesión y dispongo de una cuenta para validar
    When intento transferir "1.00" hacia la misma cuenta
    Then la transferencia web no debe confirmarse

  @negative @api
  Scenario: Transferencia API rechazada con cuenta de origen inexistente
    Given que autentico por API y obtengo una cuenta destino
    When transfiero por API desde una cuenta inexistente
    Then el API rechaza la transferencia

  @negative @api
  Scenario: Transferencia API rechazada con cuenta de destino inexistente
    Given que autentico por API y obtengo una cuenta origen
    When transfiero por API hacia una cuenta inexistente
    Then el API rechaza la transferencia

  @negative @api
  Scenario: Transferencia API rechazada sin monto
    Given que autentico por API y obtengo dos cuentas
    When transfiero por API sin informar el monto
    Then el API rechaza la transferencia
