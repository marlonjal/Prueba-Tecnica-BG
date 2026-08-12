"""Helpers for deterministic and resilient test evidence."""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

from playwright.sync_api import Error as PlaywrightError, Page


def artifact_slug(value: str) -> str:
    """Convert a test name into a stable, filesystem-safe identifier."""
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", ascii_value.lower()).strip("-")


def safe_screenshot(page: Page, destination: Path) -> None:
    """Capture evidence without masking the original functional result."""
    try:
        page.screenshot(path=str(destination), full_page=True, timeout=5_000)
    except PlaywrightError:
        pass
