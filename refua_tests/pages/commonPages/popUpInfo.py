"""
Popup Page Informartion
Message to add as HomePage dialog that appears on main page
"""

from playwright.sync_api import Page


class PopUpInfo:
    def __init__(self, page: Page):
        self.__page = page
        self.__close_button = page.locator("[data-test='CloseIcon']")
        self.__checkBox_doNotShow = page.locator(
            "[data-test='CheckBoxOutlineBlankIcon']"
        )
        self.__downLoadPwa = page.locator("#download-pwa")

    def close_pop_up(self):
        self.__close_button.click()

    def do_not_show_again(self):
        self.__checkBox_doNotShow.click()

    def download_pwa(self):
        self.__downLoadPwa.click()

    def validate_pop_up_displayed(self) -> bool:
        return (
            self.__close_button.is_visible() and self.__checkBox_doNotShow.is_visible()
        )

    def validate_pop_up_not_displayed(self) -> bool:
        return (
            not self.__close_button.is_visible()
            and not self.__checkBox_doNotShow.is_visible()
        )

    def is_visible(self) -> bool:
        """Check if popup is visible"""
        return self.__page.locator('[role="dialog"], .modal, .popup').is_visible()

    def wait_for_popup(self):
        """Wait for popup to appear"""
        self.__page.wait_for_selector(
            '[role="dialog"], .modal, .popup', state="visible"
        )

    def close(self):
        """Close the popup - adjust selector as needed"""
        close_selectors = [
            '[aria-label="Close"]',
            ".close-btn",
            "#close",
            'button:has-text("Close")',
            'button:has-text("X")',
        ]
        for selector in close_selectors:
            if self.__page.locator(selector).count() > 0:
                self.__page.click(selector)
                break
