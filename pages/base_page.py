"""Shared navigation behavior for all Page Objects."""

from __future__ import annotations

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from core.exceptions import EnvironmentUnavailable


class BasePage:
    """Provide navigation and environment checks shared by every Page Object."""

    TRANSIENT_HTTP_STATUSES = {429, 502, 503, 504}

    def __init__(self, page: Page) -> None:
        """Store the Playwright page used by the concrete Page Object."""
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

    def raise_if_security_challenge(self) -> None:
        """Classify anti-bot interstitials as shared-environment outages."""
        body_text = self.page.locator("body").inner_text().lower()
        challenge_markers = (
            "performing security verification",
            "verify you are human",
        )
        if any(marker in body_text for marker in challenge_markers):
            raise EnvironmentUnavailable(
                "ParaBank redirected the browser to a Cloudflare security challenge"
            )
