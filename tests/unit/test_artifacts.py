"""Unit tests for deterministic evidence names."""

from core.artifacts import artifact_slug


def test_artifact_slug_normalizes_accents_spaces_and_symbols() -> None:
    assert artifact_slug("Transferencia válida #1") == "transferencia-valida-1"


def test_artifact_slug_removes_edge_separators() -> None:
    assert artifact_slug(" -- Login exitoso -- ") == "login-exitoso"
