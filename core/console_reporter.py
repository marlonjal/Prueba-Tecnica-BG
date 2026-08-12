"""Compact, readable console progress grouped by test file."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import PurePath
from textwrap import wrap

import pytest

_totals: Counter[str] = Counter()
_results: dict[str, Counter[str]] = defaultdict(Counter)
_durations: Counter[str] = Counter()
_completed_files: set[str] = set()
_completed_nodes: set[str] = set()
_node_reports: dict[str, pytest.TestReport] = {}
_file_order: list[str] = []
_incidents: Counter[tuple[str, str, str]] = Counter()
_terminal = None
_compact = False

_COLUMNS = (
    ("PROGRESO", 8),
    ("ARCHIVO", 30),
    ("SUBPRUEBAS", 13),
    ("RESULTADO", 28),
    ("AVANCE", 6),
    ("BARRA", 12),
)

_INCIDENT_COLUMNS = (
    ("ESTADO", 8),
    ("CANT.", 5),
    ("ARCHIVO", 28),
    ("DETALLE", 60),
)


def pytest_configure(config: pytest.Config) -> None:
    """Enable compact output for executions while preserving collection output."""
    global _compact
    _compact = not config.option.collectonly
    if _compact:
        config.option.verbose = -1
        config.option.reportchars = ""


def pytest_collection_finish(session: pytest.Session) -> None:
    """Build the execution plan and announce its compact grouped view."""
    if not _compact:
        return

    global _terminal
    _terminal = session.config.pluginmanager.getplugin("terminalreporter")
    _reset_state()
    for item in session.items:
        file_path = item.nodeid.split("::", 1)[0]
        if file_path not in _totals:
            _file_order.append(file_path)
        _totals[file_path] += 1

    _terminal.write_sep(
        "=",
        f"PLAN DE EJECUCIÓN: {len(session.items)} PRUEBAS EN {len(_file_order)} ARCHIVOS",
    )
    _write_table_border("top")
    _write_table_header()
    _write_table_border("middle")


@pytest.hookimpl(tryfirst=True)
def pytest_report_teststatus(report: pytest.TestReport, config: pytest.Config):
    """Hide repeated symbols only in compact mode; preserve result categories."""
    if not _compact:
        return None
    if report.when == "call" and report.passed:
        return "passed", "", ""
    if report.when == "call" and report.failed:
        return "failed", "", ""
    if report.when == "call" and report.skipped and hasattr(report, "wasxfail"):
        return "xfailed", "", ""
    if report.when == "call" and report.skipped:
        return "skipped", "", ""
    if report.when == "setup" and report.skipped:
        return "skipped", "", ""
    if report.when == "setup" and report.failed:
        return "error", "", ""
    if report.when == "teardown" and report.skipped:
        return "skipped", "", ""
    if report.when == "teardown" and report.failed:
        return "error", "", ""
    return None


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    """Store phase outcomes and print a test only after teardown has finished."""
    if not _compact or report.nodeid in _completed_nodes:
        return

    _durations[report.nodeid] += report.duration
    if report.when == "call" or (
        report.when in {"setup", "teardown"} and (report.failed or report.skipped)
    ):
        _node_reports[report.nodeid] = report

    if report.when != "teardown":
        return

    _completed_nodes.add(report.nodeid)
    file_path = report.nodeid.split("::", 1)[0]
    final_report = _node_reports.pop(report.nodeid, report)
    result_name = _result_name(final_report)
    _results[file_path][result_name] += 1
    if result_name != "passed":
        _incidents[
            (
                _incident_status(result_name),
                PurePath(file_path).name,
                _incident_detail(final_report),
            )
        ] += 1

    executed = sum(_results[file_path].values())
    if executed == _totals[file_path]:
        _completed_files.add(file_path)
        _print_file_result(file_path)


def _result_name(report: pytest.TestReport) -> str:
    """Normalize a Pytest report into one summary category."""
    if hasattr(report, "wasxfail"):
        return "xfail" if report.skipped else "xpass"
    if report.when in {"setup", "teardown"} and report.failed:
        return "error"
    if report.passed:
        return "passed"
    if report.skipped:
        return "skipped"
    return "failed"


def _print_file_result(file_path: str) -> None:
    """Render the completed aggregate row for a test file."""
    position = len(_completed_files)
    total_files = len(_file_order)
    percentage = round(position * 100 / total_files)
    results = _results[file_path]
    executed = sum(results.values())
    noun = "ejecutada" if executed == 1 else "ejecutadas"
    filename = PurePath(file_path).name
    values = (
        f"[{position:02d}/{total_files:02d}]",
        filename,
        f"{executed} {noun}",
        _result_summary(results),
        f"{percentage}%",
        _progress_bar(position, total_files),
    )
    line = _table_row(values)
    _terminal.write_line(
        line,
        red=bool(results["failed"] or results["error"]),
        yellow=bool(results["xfail"] or results["xpass"] or results["skipped"]),
        green=not results["failed"]
        and not results["error"]
        and not results["xfail"]
        and not results["xpass"]
        and not results["skipped"],
    )
    if position == total_files:
        _write_table_border("bottom")


@pytest.hookimpl(trylast=True)
def pytest_terminal_summary(terminalreporter, exitstatus, config) -> None:
    """Replace Pytest's long short-summary list with a grouped fixed-width table."""
    del exitstatus, config
    if not _compact or not _incidents:
        return

    terminalreporter.write_sep("=", "RESUMEN DE INCIDENCIAS")
    _write_incident_border(terminalreporter, "top")
    terminalreporter.write_line(
        _incident_table_row(tuple(title for title, _ in _INCIDENT_COLUMNS)),
        bold=True,
        cyan=True,
    )
    _write_incident_border(terminalreporter, "middle")
    for (status, filename, detail), count in sorted(
        _incidents.items(), key=_incident_sort_key
    ):
        lines = _incident_row_lines(status, count, filename, detail)
        for values in lines:
            terminalreporter.write_line(
                _incident_table_row(values),
                red=status in {"FALLIDA", "ERROR"},
                yellow=status in {"OMITIDA", "XFAIL", "XPASS"},
            )
    _write_incident_border(terminalreporter, "bottom")


def _result_summary(results: Counter[str]) -> str:
    """Build the Spanish result text displayed in one table row."""
    details: list[str] = []
    if results["passed"]:
        label = "aprobada" if results["passed"] == 1 else "aprobadas"
        details.append(f"{results['passed']} {label}")
    if results["xfail"]:
        details.append(f"{results['xfail']} XFAIL")
    if results["xpass"]:
        details.append(f"{results['xpass']} XPASS")
    if results["skipped"]:
        details.append(f"{results['skipped']} omitidas")
    if results["failed"]:
        label = "fallida" if results["failed"] == 1 else "fallidas"
        details.append(f"{results['failed']} {label}")
    if results["error"]:
        label = "error" if results["error"] == 1 else "errores"
        details.append(f"{results['error']} {label}")
    return " · ".join(details)


def _progress_bar(completed: int, total: int, width: int = 12) -> str:
    """Create a fixed-width Unicode progress bar for completed files."""
    filled = round(completed * width / total)
    return f"{'█' * filled}{'░' * (width - filled)}"


def _table_row(values: tuple[str, ...]) -> str:
    """Format values as a fixed-width row with box-drawing separators."""
    cells = [
        f" {_fit_cell(value, width):<{width}} "
        for value, (_, width) in zip(values, _COLUMNS)
    ]
    return f"│{'│'.join(cells)}│"


def _fit_cell(value: str, width: int) -> str:
    """Keep borders aligned even if an unexpected label is unusually long."""
    if len(value) <= width:
        return value
    return f"{value[: width - 1]}…"


def _incident_status(result_name: str) -> str:
    """Translate internal result categories for the incident summary."""
    return {
        "failed": "FALLIDA",
        "error": "ERROR",
        "skipped": "OMITIDA",
        "xfail": "XFAIL",
        "xpass": "XPASS",
    }.get(result_name, result_name.upper())


def _incident_detail(report: pytest.TestReport) -> str:
    """Extract and clean the most useful one-line explanation from a report."""
    if hasattr(report, "wasxfail"):
        detail = str(report.wasxfail)
        return detail.removeprefix("reason: ")
    if report.skipped:
        detail = (
            str(report.longrepr[2])
            if isinstance(report.longrepr, tuple) and len(report.longrepr) >= 3
            else str(report.longrepr)
        )
        prefixes = (
            "SKIPPED because the shared environment is unavailable: ",
            "Skipped: ",
        )
        for prefix in prefixes:
            if detail.startswith(prefix):
                return detail[len(prefix) :]
        return detail
    lines = report.longreprtext.strip().splitlines()
    return lines[-1] if lines else "Sin detalle disponible"


def _incident_row_lines(
    status: str, count: int, filename: str, detail: str
) -> list[tuple[str, str, str, str]]:
    """Wrap a logical incident into aligned physical table rows."""
    detail_width = _INCIDENT_COLUMNS[-1][1]
    wrapped = wrap(
        " ".join(detail.split()),
        width=detail_width,
        break_long_words=True,
        break_on_hyphens=False,
    ) or [""]
    return [
        (
            status if index == 0 else "",
            str(count) if index == 0 else "",
            filename if index == 0 else "",
            line,
        )
        for index, line in enumerate(wrapped)
    ]


def _incident_table_row(values: tuple[str, ...]) -> str:
    """Format one incident row with the same fixed width as its borders."""
    cells = [
        f" {value:<{width}} "
        for value, (_, width) in zip(values, _INCIDENT_COLUMNS)
    ]
    return f"│{'│'.join(cells)}│"


def _write_incident_border(terminalreporter, position: str) -> None:
    """Write a top, middle, or bottom border for the incident table."""
    characters = {
        "top": ("┌", "┬", "┐"),
        "middle": ("├", "┼", "┤"),
        "bottom": ("└", "┴", "┘"),
    }
    left, separator, right = characters[position]
    segments = ["─" * (width + 2) for _, width in _INCIDENT_COLUMNS]
    terminalreporter.write_line(f"{left}{separator.join(segments)}{right}")


def _incident_sort_key(item) -> tuple[int, str, str]:
    """Order severe failures before environment skips and known defects."""
    (status, filename, detail), _ = item
    priority = {"ERROR": 0, "FALLIDA": 1, "XPASS": 2, "OMITIDA": 3, "XFAIL": 4}
    return priority.get(status, 5), filename, detail


def _write_table_header() -> None:
    """Write the colored column-header row to Pytest's terminal reporter."""
    _terminal.write_line(
        _table_row(tuple(title for title, _ in _COLUMNS)),
        bold=True,
        cyan=True,
    )


def _write_table_border(position: str) -> None:
    """Write the requested top, middle, or bottom table border."""
    characters = {
        "top": ("┌", "┬", "┐"),
        "middle": ("├", "┼", "┤"),
        "bottom": ("└", "┴", "┘"),
    }
    left, separator, right = characters[position]
    segments = ["─" * (width + 2) for _, width in _COLUMNS]
    _terminal.write_line(f"{left}{separator.join(segments)}{right}")


def _reset_state() -> None:
    """Clear module state before Pytest starts a new collection."""
    _totals.clear()
    _results.clear()
    _durations.clear()
    _completed_files.clear()
    _completed_nodes.clear()
    _node_reports.clear()
    _file_order.clear()
    _incidents.clear()
