"""Shared navigation behavior for all Page Objects."""

from __future__ import annotations

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from core.exceptions import EnvironmentUnavailable


class BasePage:
    TRANSIENT_HTTP_STATUSES = {429, 502, 503, 504}

    def __init__(self, page: Page) -> None:
        self.page = page

    def open(self, path: str) -> None:
        """Open a relative ParaBank path with one transient retry."""
        target = path.lstrip("/")
        for attempt in range(2):
            try:
                response = self.page.goto(target, wait_until="domcontentloaded")
                if response is None or response.status not in self.TRANSIENT_HTTP_STATUSES:
                    return
                if attempt == 1:
                    raise EnvironmentUnavailable(
                        f"ParaBank returned HTTP {response.status} for {response.url}"
                    )
            except PlaywrightTimeoutError as error:
                if attempt == 1:
                    raise EnvironmentUnavailable(
                        f"ParaBank did not respond after two attempts: {target}"
                    ) from error
            self.page.goto("about:blank", wait_until="commit", timeout=5_000)
