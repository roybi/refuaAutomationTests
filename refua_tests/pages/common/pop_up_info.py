"""Reusable Meditik dialogs / popups (PWA install, info modals)."""

from playwright.sync_api import Page

_HANDLER_FLAG = "_meditik_pwa_auto_dismiss_installed"


class PopUpInfo:
    """Common overlay dialogs that can block the main UI."""

    PWA_HEADING = "כל המידע הרפואי במרחק של קליל"

    def __init__(self, page: Page):
        self._page = page

    @classmethod
    def install_auto_dismiss(cls, page: Page) -> None:
        """Register a Playwright locator handler so the PWA popup is closed
        whenever it appears — even mid-wait on any screen.

        Safe to call multiple times (idempotent per page).
        """
        if getattr(page, _HANDLER_FLAG, False):
            return

        popup = cls(page)

        def _close(_locator=None) -> None:
            popup.dismiss_if_present()

        # Prefer specific PWA heading so we don't auto-close unrelated dialogs.
        page.add_locator_handler(
            page.get_by_role("dialog").filter(has_text=cls.PWA_HEADING),
            _close,
        )
        try:
            from refua_tests.pages.automation_ids import MeditikIds as Ids

            page.add_locator_handler(
                page.get_by_test_id(Ids.DOWNLOAD_PWA_MODAL),
                _close,
            )
            page.add_locator_handler(
                page.locator("#download-pwa"),
                _close,
            )
        except Exception:
            pass

        setattr(page, _HANDLER_FLAG, True)

    def dismiss_if_present(self):
        """Close PWA / blocking dialogs if visible; never fail if absent."""
        for _ in range(3):
            if not self._dismiss_once():
                break
            try:
                self._page.wait_for_timeout(200)
            except Exception:
                break

    def _dismiss_once(self) -> bool:
        """Return True if something was dismissed."""
        try:
            from refua_tests.pages.automation_ids import MeditikIds as Ids

            pwa = self._page.get_by_test_id(Ids.DOWNLOAD_PWA_MODAL).or_(
                self._page.locator("#download-pwa")
            )
            close_mapped = self._page.get_by_test_id(Ids.DOWNLOAD_PWA_BTN_CLOSE)
            if pwa.count() > 0 and pwa.first.is_visible(timeout=500):
                if close_mapped.count() > 0 and close_mapped.first.is_visible(timeout=500):
                    close_mapped.first.click(timeout=3000, force=True)
                    return True
        except Exception:
            pass

        try:
            dialog = self._page.get_by_role("dialog").filter(has_text=self.PWA_HEADING)
            if dialog.count() == 0 or not dialog.first.is_visible(timeout=500):
                return False

            dlg = dialog.first
            close_candidates = [
                dlg.get_by_test_id("meditik-download-pwa-btn-close"),
                dlg.locator(
                    '[aria-label="Close"], [aria-label="סגור"], [aria-label="close"]'
                ),
                dlg.locator("button").first,
            ]
            for candidate in close_candidates:
                try:
                    if candidate.count() > 0 and candidate.first.is_visible(timeout=400):
                        candidate.first.click(timeout=3000, force=True)
                        return True
                except Exception:
                    continue

            self._page.keyboard.press("Escape")
            return True
        except Exception:
            return False

    def is_visible(self) -> bool:
        try:
            return self._page.get_by_role("dialog").filter(
                has_text=self.PWA_HEADING
            ).first.is_visible(timeout=500)
        except Exception:
            return False
