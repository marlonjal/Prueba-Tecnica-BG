"""Local contract test for TransferPage form actions."""

from playwright.sync_api import Page

from pages.transfer_page import TransferPage


def test_transfer_page_fills_accounts_amount_and_submits(page: Page) -> None:
    """Verify account discovery, field selection, and transfer submission."""
    page.set_content(
        """
        <form onsubmit="window.submitted = true; return false">
          <input id="amount">
          <select id="fromAccountId">
            <option value="12345">12345</option>
            <option value="67890">67890</option>
          </select>
          <select id="toAccountId">
            <option value="12345">12345</option>
            <option value="67890">67890</option>
          </select>
          <input type="submit" value="Transfer">
        </form>
        """
    )
    transfer_page = TransferPage(page)

    assert transfer_page.account_ids() == ["12345", "67890"]

    transfer_page.transfer("5.25", "12345", "67890")

    assert transfer_page.amount_input.input_value() == "5.25"
    assert transfer_page.source_select.input_value() == "12345"
    assert transfer_page.target_select.input_value() == "67890"
    assert page.evaluate("window.submitted") is True
