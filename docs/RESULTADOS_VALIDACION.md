# Resultados de validación

## Ambiente

- Python local 3.12.4 y Python 3.12.3 en la imagen Docker.
- Playwright 1.52.0.
- Chromium 136.0.7103.25.
- Pytest 8.3.4.
- Ambiente público de ParaBank.

## Resultados comprobados

- Pruebas unitarias: **34 aprobadas**.
- Colección: **69 pruebas** (35 BDD y 34 unitarias).
- Registro no destructivo: **11 aprobadas**, 2 excluidas.
- Login y logout: **4 aprobadas**, 2 `XFAIL`.
- Regresión segura consolidada en Docker: **47 aprobadas**, **1 omitida** por
  reto de seguridad de Cloudflare, **2 `XFAIL`** y **19 excluidas** por el
  marcador `destructive`; código de salida `0`.

Las features de retiro y transferencia fueron recolectadas y sus Page/Service
Objects se validaron localmente. No se ejecutaron contra el ambiente público
durante la construcción, porque pueden modificar saldos.

## Hallazgos funcionales

| ID | Esperado | Observado | Estado |
|---|---|---|---|
| LOG-004 | Rechazar usuario inexistente | Sesión iniciada como John Smith | XFAIL |
| LOG-005 | Rechazar contraseña incorrecta | Sesión iniciada como John Smith | XFAIL |

Las capturas, videos y traces de estas ejecuciones se generan localmente bajo
`results/` y no se versionan porque pueden incluir datos del ambiente.

## Interpretación de resultados

- `PASSED`: el comportamiento coincide con la expectativa.
- `FAILED`: defecto de la automatización o comportamiento no catalogado.
- `XFAIL`: defecto funcional conocido y reproducible del SUT.
- `SKIPPED`: indisponibilidad comprobada del ambiente compartido.
