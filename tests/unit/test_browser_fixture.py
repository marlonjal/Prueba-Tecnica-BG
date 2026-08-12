"""Local smoke test for the isolated Playwright page fixture."""

from playwright.sync_api import Page, expect


def test_page_fixture_runs_in_an_isolated_browser_context(page: Page) -> None:
    page.set_content("<main><h1>Playwright ready</h1></main>")
    expect(page.get_by_role("heading", name="Playwright ready")).to_be_visible()
