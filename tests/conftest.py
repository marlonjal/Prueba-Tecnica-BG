"""Playwright lifecycle, shared fixtures, reports, and test evidence."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from config.settings import PROJECT_ROOT, settings
from core.artifacts import artifact_slug, safe_screenshot

RESULTS_DIR = PROJECT_ROOT / "results"
REPORTS_DIR = RESULTS_DIR / "reports"
SCREENSHOTS_DIR = RESULTS_DIR / "screenshots"
VIDEOS_DIR = RESULTS_DIR / "videos"
TRACES_DIR = RESULTS_DIR / "traces"


def pytest_sessionstart(session: pytest.Session) -> None:
    """Prepare the single ignored output tree used by all reporters."""
    del session
    for directory in (REPORTS_DIR, SCREENSHOTS_DIR, VIDEOS_DIR, TRACES_DIR):
        directory.mkdir(parents=True, exist_ok=True)
        if settings.clean_results:
            for entry in directory.iterdir():
                if entry.is_dir():
                    shutil.rmtree(entry)
                else:
                    entry.unlink()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    """Expose setup/call/teardown results to evidence fixtures."""
    del call
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"report_{report.when}", report)


def pytest_bdd_before_scenario(request, feature, scenario) -> None:
    del feature
    request.node._scenario_name = scenario.name
    request.node._step_counter = 0


def pytest_bdd_after_step(request, feature, scenario, step, step_func, step_func_args) -> None:
    """Optionally capture a screenshot after every successful Gherkin step."""
    del feature, scenario, step_func, step_func_args
    if not settings.evidence_each_step:
        return
    page = getattr(request.node, "_active_page", None)
    screenshot_dir = getattr(request.node, "_screenshot_dir", None)
    if page is None or screenshot_dir is None or page.is_closed():
        return
    request.node._step_counter += 1
    step_slug = artifact_slug(f"{step.keyword}-{step.name}")[:80]
    safe_screenshot(
        page,
        screenshot_dir / f"step-{request.node._step_counter:02d}-{step_slug}.png",
    )


@pytest.fixture(scope="session")
def playwright_instance() -> Playwright:
    with sync_playwright() as playwright:
        yield playwright


@pytest.fixture(scope="session")
def browser(playwright_instance: Playwright) -> Browser:
    browser_type = getattr(playwright_instance, settings.browser, None)
    if browser_type is None:
        raise ValueError(f"Unsupported browser: {settings.browser}")
    instance = browser_type.launch(headless=settings.headless, slow_mo=settings.slow_mo)
    yield instance
    instance.close()


@pytest.fixture
def browser_context(browser: Browser, request: pytest.FixtureRequest) -> BrowserContext:
    """Create an isolated context, trace, video, and screenshot tree per test."""
    scenario_slug = artifact_slug(request.node.name)
    screenshot_dir = SCREENSHOTS_DIR / scenario_slug
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    request.node._screenshot_dir = screenshot_dir
    video_temp_dir = Path(tempfile.mkdtemp(prefix=f"parabank-{scenario_slug}-"))

    context = browser.new_context(
        base_url=f"{settings.base_url}/",
        viewport={"width": 1440, "height": 900},
        record_video_dir=str(video_temp_dir),
        record_video_size={"width": 1280, "height": 720},
    )
    context.set_default_timeout(settings.default_timeout)
    context.set_default_navigation_timeout(settings.navigation_timeout)
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    yield context

    page = getattr(request.node, "_active_page", None)
    video = page.video if page is not None and not page.is_closed() else None
    if page is not None and not page.is_closed():
        safe_screenshot(page, screenshot_dir / "final-state.png")
        report = getattr(request.node, "report_call", None)
        if report is not None and report.failed:
            safe_screenshot(page, screenshot_dir / "failure.png")
    context.tracing.stop(path=str(TRACES_DIR / f"{scenario_slug}.zip"))
    context.close()
    if video is not None:
        video.save_as(str(VIDEOS_DIR / f"{scenario_slug}.webm"))
    shutil.rmtree(video_temp_dir, ignore_errors=True)


@pytest.fixture
def page(browser_context: BrowserContext, request: pytest.FixtureRequest) -> Page:
    active_page = browser_context.new_page()
    request.node._active_page = active_page
    yield active_page


@pytest.fixture(scope="session")
def api_context(playwright_instance: Playwright):
    context = playwright_instance.request.new_context(
        base_url=f"{settings.api_url}/",
        extra_http_headers={"Accept": "application/json"},
        timeout=settings.navigation_timeout,
    )
    yield context
    context.dispose()


@pytest.fixture
def scenario_state() -> dict:
    """Keep mutable scenario data isolated from every other test."""
    return {}
