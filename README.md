# Prueba técnica QA Automatizador - Banco Guayaquil

Suite funcional para los flujos de registro, autenticación, retiro y
transferencia de fondos en [ParaBank](https://parabank.parasoft.com/parabank/).
Está construida con Python, Playwright, Pytest, pytest-bdd y Page Object Model.

## Tecnologías

- Python 3.12.
- Playwright 1.52.0 con Chromium.
- Pytest 8.3.4 y pytest-bdd 7.3.0.
- Reportes HTML con pytest-html y JSON con pytest-bdd.
- Docker y Docker Compose como forma recomendada de ejecución.

## Ejecución recomendada con Docker

Requisitos: Git, Docker Desktop o Docker Engine con Compose y acceso HTTPS a
ParaBank.

```bash
git clone git@github.com:marlonjal/Prueba-Tecnica-BG.git
cd Prueba-Tecnica-BG
git switch feature/development_test
docker compose build tests
docker compose run --rm tests
```

El comando predeterminado ejecuta la regresión segura y excluye los escenarios
`destructive`. Para ejecutar conscientemente la suite completa:

```bash
docker compose run --rm tests python -m pytest
```

Los escenarios destructivos pueden crear clientes o modificar cuentas y saldos
del ambiente público compartido.

### Ejecución por tipo de prueba con Docker

Los marcadores de Pytest permiten ejecutar grupos específicos. Las variantes
seguras agregan `and not destructive` para impedir cambios persistentes.

```bash
# Regresión segura: excluye creación de clientes y movimientos de saldos
docker compose run --rm tests

# Casos positivos seguros
docker compose run --rm tests python -m pytest -m "positive and not destructive" -v

# Casos negativos seguros
docker compose run --rm tests python -m pytest -m "negative and not destructive" -v

# Casos de interfaz web seguros
docker compose run --rm tests python -m pytest -m "ui and not destructive" -v

# Recorrido crítico seguro
docker compose run --rm tests python -m pytest -m "smoke and not destructive" -v

# Pruebas unitarias del framework, sin acceder a ParaBank
docker compose run --rm tests python -m pytest tests/unit -q
```

Los siguientes comandos incluyen operaciones potencialmente persistentes y
deben ejecutarse conscientemente contra el ambiente público:

```bash
# Todos los casos positivos, incluidos registro, retiro y transferencia
docker compose run --rm tests python -m pytest -m positive -v

# Todos los casos negativos; un defecto del SUT podría aceptar una operación
docker compose run --rm tests python -m pytest -m negative -v

# Todos los casos de interfaz web
docker compose run --rm tests python -m pytest -m ui -v

# Todos los casos del API REST; retiros y transferencias modifican saldos
docker compose run --rm tests python -m pytest -m api -v

# Únicamente escenarios que pueden modificar datos o saldos
docker compose run --rm tests python -m pytest -m destructive -v

# Regresión completa: escenarios BDD y pruebas unitarias
docker compose run --rm tests python -m pytest -v
```

También se puede ejecutar una funcionalidad concreta por archivo:

```bash
docker compose run --rm tests python -m pytest tests/steps/test_registration_steps.py -v
docker compose run --rm tests python -m pytest tests/steps/test_login_steps.py -v
docker compose run --rm tests python -m pytest tests/steps/test_withdrawal_steps.py -v
docker compose run --rm tests python -m pytest tests/steps/test_transfer_steps.py -v
```

Para revisar qué casos selecciona un marcador sin ejecutarlos, añada
`--collect-only`:

```bash
docker compose run --rm tests python -m pytest -m negative --collect-only -q
```

## Ejecución local

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m playwright install chromium
python -m pytest -m "not destructive"
```

Comandos focalizados:

```powershell
# Pruebas unitarias del framework
python -m pytest tests/unit -q

# Casos UI seguros
python -m pytest -m "ui and not destructive" -v

# Verificar la colección sin ejecutar escenarios
python -m pytest --collect-only -q
```

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

Adicionalmente, 21 pruebas unitarias protegen configuración, evidencias,
selectores, datos, autenticación y construcción de solicitudes API.

## Reportes y evidencias

Toda salida queda bajo `results/`, excluida de Git:

- `results/reports/report.html`: reporte HTML autocontenido.
- `results/reports/cucumber-report.json`: resultados Cucumber JSON.
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
