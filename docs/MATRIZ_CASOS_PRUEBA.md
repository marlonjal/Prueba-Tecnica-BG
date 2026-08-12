# Matriz de casos de prueba

## Registro

| ID | Tipo | Caso | Resultado esperado |
|---|---|---|---|
| REG-001 | Positivo | Registro válido | Cliente creado y autenticado |
| REG-002 a REG-011 | Negativo | Campo obligatorio vacío | Mensaje específico de requerido |
| REG-012 | Negativo | Contraseñas distintas | Registro rechazado |
| REG-013 | Negativo | Usuario duplicado | Registro rechazado |

Los campos obligatorios cubiertos son nombre, apellido, dirección, ciudad,
estado, código postal, SSN, usuario, contraseña y confirmación.

## Login y logout

| ID | Tipo | Caso | Resultado esperado |
|---|---|---|---|
| LOG-001 | Positivo | Credenciales configuradas | Resumen de cuentas visible |
| LOG-002 | Negativo | Usuario vacío | Acceso rechazado |
| LOG-003 | Negativo | Contraseña vacía | Acceso rechazado |
| LOG-004 | Negativo | Usuario inexistente | Acceso rechazado |
| LOG-005 | Negativo | Contraseña incorrecta | Acceso rechazado |
| LOG-006 | Positivo | Cierre de sesión | Formulario de acceso visible |

## Retiro por API

| ID | Tipo | Caso | Resultado esperado |
|---|---|---|---|
| RET-001 | Positivo | Retiro de 1.00 | Saldo disminuye y aparece débito |
| RET-002 | Negativo | Monto cero | Operación rechazada |
| RET-003 | Negativo | Monto negativo | Operación rechazada |
| RET-004 | Negativo | Monto no numérico | Operación rechazada |
| RET-005 | Negativo | Monto ausente | Operación rechazada |
| RET-006 | Negativo | Cuenta inexistente | Operación rechazada |
| RET-007 | Negativo | Monto superior al saldo | Operación rechazada |

## Transferencias

| ID | Canal | Tipo | Caso | Resultado esperado |
|---|---|---|---|---|
| TRA-001 | UI | Positivo | Transferencia de 1.00 | Confirmación con monto y cuentas |
| TRA-002 | UI | Negativo | Monto vacío | Transferencia rechazada |
| TRA-003 | UI | Negativo | Monto cero | Transferencia rechazada |
| TRA-004 | UI | Negativo | Monto negativo | Transferencia rechazada |
| TRA-005 | UI | Negativo | Monto no numérico | Transferencia rechazada |
| TRA-006 | UI | Negativo | Misma cuenta | Transferencia rechazada |
| TRA-007 | API | Negativo | Origen inexistente | Operación rechazada |
| TRA-008 | API | Negativo | Destino inexistente | Operación rechazada |
| TRA-009 | API | Negativo | Monto ausente | Operación rechazada |

Todos los retiros y transferencias se marcan `destructive`, incluidos los casos
negativos, porque un defecto del SUT podría aceptar la solicitud y alterar el
saldo.
