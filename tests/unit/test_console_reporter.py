"""Unit tests for the compact terminal incident summary."""

from collections import Counter, defaultdict
from types import SimpleNamespace

from core import console_reporter
from core.console_reporter import (
    _incident_detail,
    _incident_row_lines,
    _incident_table_row,
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


def test_teardown_failure_replaces_the_previously_passed_call(monkeypatch) -> None:
    """Verify cleanup errors replace a successful call before rendering results."""
    terminal = FakeTerminal()
    monkeypatch.setattr(console_reporter, "_compact", True)
    monkeypatch.setattr(console_reporter, "_terminal", terminal)
    monkeypatch.setattr(console_reporter, "_totals", Counter())
    monkeypatch.setattr(console_reporter, "_results", defaultdict(Counter))
    monkeypatch.setattr(console_reporter, "_durations", Counter())
    monkeypatch.setattr(console_reporter, "_completed_files", set())
    monkeypatch.setattr(console_reporter, "_completed_nodes", set())
    monkeypatch.setattr(console_reporter, "_node_reports", {})
    monkeypatch.setattr(console_reporter, "_file_order", [])
    monkeypatch.setattr(console_reporter, "_incidents", Counter())
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
