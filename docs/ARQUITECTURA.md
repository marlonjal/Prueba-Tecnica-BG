# Arquitectura del framework

## Objetivo

Separar intención de negocio, interacción de interfaz, consumo de API, datos e
infraestructura para que los casos sean legibles y mantenibles.

## Capas

```text
tests/features -> tests/steps -> pages    -> ParaBank UI
                           `-> services -> ParaBank API

config + core + models + tests/conftest.py
              soportan todas las capas
```

- Las features describen comportamiento sin selectores ni rutas HTTP.
- Los steps conservan solo orquestación y aserciones de negocio.
- Los Page Objects encapsulan selectores, esperas y acciones UI.
- `ParaBankApi` encapsula endpoints y serialización de parámetros.
- Los modelos y factories producen datos únicos por escenario.
- Las fixtures crean un navegador por sesión y un contexto aislado por prueba.

## Patrones aplicados

- Page Object Model para UI.
- Service Object para API.
- Behavior-Driven Development con Gherkin.
- Factory para datos de clientes.
- Dependency Injection mediante fixtures de Pytest.
- Configuration Object inmutable cargado desde el entorno.

## Ciclo de vida y evidencias

Cada escenario UI recibe su propio `BrowserContext`, página, video y trace. El
teardown conserva una captura final y añade otra captura cuando el caso falla.
Con `EVIDENCE_EACH_STEP=true` se genera una imagen adicional por paso Gherkin.

La API usa un `APIRequestContext` de Playwright por sesión. Los datos de login y
cuentas se consultan una sola vez para reducir carga sobre el ambiente público.

## Seguridad operativa

Los casos que crean clientes o pueden modificar productos y saldos usan el
marcador `destructive`. La ejecución predeterminada y CI los excluyen. No se
reinicia ni limpia la base de datos compartida.
