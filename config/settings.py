"""Typed environment configuration for the automation framework."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env", override=False)


def env_bool(name: str, default: bool) -> bool:
    """Read a boolean environment variable using explicit truthy values."""
    value = os.getenv(name)
    return default if value is None else value.strip().lower() in {"1", "true", "yes"}


def env_int(name: str, default: int) -> int:
    """Read an integer environment variable or return its default."""
    value = os.getenv(name)
    return default if value is None else int(value)


@dataclass(frozen=True)
class Settings:
    """Immutable runtime settings loaded from environment variables."""

    base_url: str = os.getenv(
        "PARABANK_BASE_URL", "https://parabank.parasoft.com/parabank"
    ).rstrip("/")
    api_url: str = os.getenv(
        "PARABANK_API_URL",
        "https://parabank.parasoft.com/parabankv2/services/bank",
    ).rstrip("/")
    username: str = os.getenv("PARABANK_USERNAME", "john")
    password: str = os.getenv("PARABANK_PASSWORD", "demo")
    browser: str = os.getenv("BROWSER", "chromium").lower()
    headless: bool = env_bool("HEADLESS", True)
    slow_mo: int = env_int("SLOW_MO", 0)
    default_timeout: int = env_int("DEFAULT_TIMEOUT", 15_000)
    navigation_timeout: int = env_int("NAVIGATION_TIMEOUT", 30_000)
    evidence_each_step: bool = env_bool("EVIDENCE_EACH_STEP", False)
    clean_results: bool = env_bool("CLEAN_RESULTS", False)


settings = Settings()
