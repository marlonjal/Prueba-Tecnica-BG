@regression @api @destructive
Feature: Retiro de fondos mediante API
  Como cliente de ParaBank
  Quiero retirar dinero de una cuenta
  Para disponer de parte de mi saldo

  @smoke @positive
  Scenario: Retiro exitoso de una cuenta con saldo disponible
    Given que autentico por API al cliente configurado y obtengo una cuenta
    When retiro "1.00" de la cuenta seleccionada
    Then el API confirma el retiro
    And el saldo de la cuenta disminuye en "1.00"
    And se registra una transacción débito por "1.00"

  @negative
  Scenario Outline: Retiro rechazado con monto no permitido
    Given que autentico por API al cliente configurado y obtengo una cuenta
    When intento retirar el monto "<monto>" de la cuenta seleccionada
    Then el API rechaza la operación de retiro

    Examples:
      | monto |
      | 0     |
      | -1    |
      | abc   |

  @negative
  Scenario: Retiro rechazado sin informar el monto
    Given que autentico por API al cliente configurado y obtengo una cuenta
    When intento retirar sin enviar el monto
    Then el API rechaza la operación de retiro

  @negative
  Scenario: Retiro rechazado para una cuenta inexistente
    When intento retirar "1.00" de una cuenta inexistente por API
    Then el API rechaza la operación de retiro

  @negative
  Scenario: Retiro rechazado cuando supera el saldo disponible
    Given que autentico por API al cliente configurado y obtengo una cuenta
    When intento retirar un monto superior al saldo disponible
    Then el API rechaza la operación de retiro
