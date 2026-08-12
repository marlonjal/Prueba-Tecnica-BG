# Prueba técnica Automation QA Engineer - Banco Guayaquil

Suite funcional para los flujos de registro, autenticación, retiro y
transferencia de fondos en [ParaBank](https://parabank.parasoft.com/parabank/).
Está construida con Python, Playwright, Pytest, pytest-bdd y Page Object Model.

## Tecnologías

- Python 3.12.
- Playwright 1.52.0 con Chromium.
- Pytest 8.3.4 y pytest-bdd 7.3.0.
- Reportes HTML con pytest-html y JSON con pytest-bdd.
- Docker y Docker Compose como forma recomendada de ejecución.

## Preparación y ejecución con Docker

Requisitos: Git, Docker Desktop o Docker Engine con Compose y acceso HTTPS a
ParaBank.

```bash
# Preparación inicial
git clone git@github.com:marlonjal/Prueba-Tecnica-BG.git
cd Prueba-Tecnica-BG
git switch feature/development_test
docker compose build tests

# Regresión segura recomendada
docker compose run --rm tests

# Pruebas unitarias del framework
docker compose run --rm tests python -m pytest tests/unit -q

# Pruebas positivas
docker compose run --rm tests python -m pytest -m positive -v

# Pruebas negativas
docker compose run --rm tests python -m pytest -m negative -v

# Suite completa
docker compose run --rm tests python -m pytest -v
```

La regresión segura excluye automáticamente los escenarios `destructive`. Los
comandos de pruebas positivas, negativas y suite completa sí pueden crear
clientes o modificar cuentas y saldos del ambiente público.

Todos los comandos de prueba muestran tablas compactas y alineadas por archivo.
Las incidencias se resumen en consola y el diagnóstico completo queda en el
reporte HTML. Para solicitar también el traceback nativo, agregue `--tb=short`
al comando que necesite investigar.

## Configuración

Copie `.env.example` como `.env` para sobrescribir valores locales. `.env` no
se versiona.

| Variable | Predeterminado | Uso |
|---|---|---|
| `PARABANK_BASE_URL` | Portal público | Interfaz web |
| `PARABANK_API_URL` | API REST v2 | Servicios bancarios |
| `PARABANK_USERNAME` | `john` | Usuario demostrativo |
| `PARABANK_PASSWORD` | `demo` | Clave demostrativa |
| `BROWSER` | `chromium` | Motor de navegador |
| `HEADLESS` | `true` | Ejecución sin interfaz |
| `DEFAULT_TIMEOUT` | `15000` | Espera de elementos en ms |
| `NAVIGATION_TIMEOUT` | `30000` | Espera de navegación en ms |
| `EVIDENCE_EACH_STEP` | `false` | Captura después de cada step |
| `CLEAN_RESULTS` | `false` | Limpia evidencias antes de ejecutar |

## Arquitectura

```text
Feature Gherkin
      |
      v
Step definition
      |
      +-------------------+
      |                   |
      v                   v
Page Object          Service Object
(Playwright UI)      (APIRequestContext)
      |                   |
      +---------+---------+
                v
         ParaBank UI / API
```

- `pages/`: selectores y acciones de interfaz.
- `services/`: solicitudes al API REST.
- `models/`: datos tipados y fábricas únicas.
- `config/`: variables de entorno tipadas.
- `core/`: excepciones y utilidades transversales.
- `tests/features/`: comportamiento Gherkin.
- `tests/steps/`: adaptación del negocio a Page/Service Objects.
- `tests/unit/`: regresiones locales del framework.

Más detalle en [docs/ARQUITECTURA.md](docs/ARQUITECTURA.md).

## Alcance

La suite reúne 35 escenarios BDD:

| Funcionalidad | UI | API | Total |
|---|---:|---:|---:|
| Registro | 13 | 0 | 13 |
| Login y logout | 6 | 0 | 6 |
| Retiro | 0 | 7 | 7 |
| Transferencia | 6 | 3 | 9 |
| **Total** | **25** | **10** | **35** |

Adicionalmente, 32 pruebas unitarias protegen configuración, evidencias,
selectores, datos, autenticación, precondiciones y construcción de solicitudes
API.

## Reportes y evidencias

Toda salida queda bajo `results/`, excluida de Git:

- `results/reports/report.html`: reporte HTML autocontenido.
- `results/reports/cucumber-report.json`: resultados Cucumber JSON.
- `results/reports/test-results.xlsx`: libro de Excel con resumen visual y una
  fila por prueba, incluyendo estado, duración y detalle.
- `results/screenshots/<caso>/`: estado final, fallo y pasos opcionales.
- `results/videos/<caso>.webm`: video de cada escenario UI.
- `results/traces/<caso>.zip`: trace de Playwright con red y snapshots.

## Integración continua

GitHub Actions construye la misma imagen Docker. Push y pull request ejecutan
únicamente la regresión segura. La regresión completa requiere lanzar
manualmente el workflow y activar `include_destructive`.

## Hallazgos del ambiente

Durante la validación, ParaBank autenticó al cliente público con un usuario
inexistente y también con una contraseña incorrecta. Ambos casos permanecen
como `XFAIL`: el defecto queda visible sin presentarse como un fallo técnico del
framework. Consulte [docs/RESULTADOS_VALIDACION.md](docs/RESULTADOS_VALIDACION.md).
