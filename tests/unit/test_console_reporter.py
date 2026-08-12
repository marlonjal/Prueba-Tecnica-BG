"""Unit tests for the compact terminal incident summary."""

from collections import Counter, defaultdict
from types import SimpleNamespace

from core import console_reporter
from core.console_reporter import (
    _compact_detail,
    _execution_plan_title,
    _incident_detail,
    _incident_row_lines,
    _incident_table_row,
    _result_summary,
)


class FakeTerminal:
    """Capture custom reporter lines without opening a real terminal session."""

    def __init__(self) -> None:
        """Initialize the rendered line collection."""
        self.lines: list[str] = []

    def write_line(self, line: str, **styles) -> None:
        """Record one line while accepting Pytest terminal style arguments."""
        del styles
        self.lines.append(line)


def test_incident_rows_wrap_without_breaking_table_width() -> None:
    """Verify that long diagnostic text remains inside fixed table borders."""
    detail = "ParaBank API login failed because the shared environment returned " * 3

    rows = _incident_row_lines("OMITIDA", 6, "test_withdrawal_steps.py", detail)
    rendered = [_incident_table_row(row) for row in rows]

    assert len(rows) > 1
    assert len({len(line) for line in rendered}) == 1
    assert all(line.startswith("│") and line.endswith("│") for line in rendered)
    assert len(_compact_detail("x" * 500)) == 180
    assert _compact_detail("x" * 500).endswith("…")
    assert _execution_plan_title(1, 1) == "PLAN DE EJECUCIÓN: 1 PRUEBA EN 1 ARCHIVO"
    assert _execution_plan_title(2, 3) == "PLAN DE EJECUCIÓN: 2 PRUEBAS EN 3 ARCHIVOS"
    assert _result_summary(Counter(skipped=1)) == "1 omitida"
    assert _result_summary(Counter(skipped=2)) == "2 omitidas"


def test_skip_detail_removes_repeated_pytest_prefix() -> None:
    """Verify grouped incidents display only their actionable reason."""
    report = SimpleNamespace(
        skipped=True,
        longrepr=(
            "test.py",
            0,
            "SKIPPED because the shared environment is unavailable: HTTP 429",
        ),
    )

    assert _incident_detail(report) == "HTTP 429"
    xfail_report = SimpleNamespace(
        skipped=True,
        wasxfail="reason: known ParaBank defect",
    )
    assert _incident_detail(xfail_report) == "known ParaBank defect"
    failure_report = SimpleNamespace(
        skipped=False,
        longrepr=SimpleNamespace(
            reprcrash=SimpleNamespace(
                message=(
                    "AssertionError: Locator expected to contain the success message\n"
                    "Actual value: registration form"
                ),
                path="pages/registration_page.py",
                lineno=55,
            )
        ),
        longreprtext="long traceback that must not be displayed",
    )
    assert _incident_detail(failure_report) == (
        "AssertionError: Locator expected to contain the success message "
        "(registration_page.py:55)"
    )


def test_default_compact_view_hides_native_traceback() -> None:
    """Verify normal executions rely on the aligned custom incident table."""
    config = SimpleNamespace(
        option=SimpleNamespace(collectonly=False, tbstyle="auto"),
        invocation_params=SimpleNamespace(args=()),
    )

    console_reporter.pytest_configure(config)

    assert config.option.tbstyle == "no"


def test_explicit_traceback_style_is_preserved() -> None:
    """Verify callers can still request native Pytest diagnostic output."""
    config = SimpleNamespace(
        option=SimpleNamespace(collectonly=False, tbstyle="short"),
        invocation_params=SimpleNamespace(args=("--tb=short",)),
    )

    console_reporter.pytest_configure(config)

    assert config.option.tbstyle == "short"


def test_teardown_failure_replaces_the_previously_passed_call(monkeypatch) -> None:
    """Verify cleanup errors replace a successful call before rendering results."""
    terminal = FakeTerminal()
    with monkeypatch.context() as isolated:
        isolated.setattr(console_reporter, "_compact", True)
        isolated.setattr(console_reporter, "_terminal", terminal)
        isolated.setattr(console_reporter, "_totals", Counter())
        isolated.setattr(console_reporter, "_results", defaultdict(Counter))
        isolated.setattr(console_reporter, "_durations", Counter())
        isolated.setattr(console_reporter, "_completed_files", set())
        isolated.setattr(console_reporter, "_completed_nodes", set())
        isolated.setattr(console_reporter, "_node_reports", {})
        isolated.setattr(console_reporter, "_file_order", [])
        isolated.setattr(console_reporter, "_incidents", Counter())
        console_reporter._totals["tests/unit/sample.py"] = 1
        console_reporter._file_order.append("tests/unit/sample.py")
        call_report = SimpleNamespace(
            nodeid="tests/unit/sample.py::test_example",
            when="call",
            duration=0.1,
            failed=False,
            passed=True,
            skipped=False,
        )
        teardown_report = SimpleNamespace(
            nodeid="tests/unit/sample.py::test_example",
            when="teardown",
            duration=0.1,
            failed=True,
            passed=False,
            skipped=False,
            longreprtext="RuntimeError: cleanup failed",
        )

        console_reporter.pytest_runtest_logreport(call_report)
        assert not console_reporter._completed_nodes

        console_reporter.pytest_runtest_logreport(teardown_report)

        assert console_reporter._results["tests/unit/sample.py"]["error"] == 1
        assert console_reporter._results["tests/unit/sample.py"]["passed"] == 0
        assert any("1 error" in line for line in terminal.lines)
