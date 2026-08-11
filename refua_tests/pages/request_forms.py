"""Request / action form pages opened from כל הפעולות or speed dial."""

from __future__ import annotations

from dataclasses import dataclass

from playwright.sync_api import Page, expect

from refua_tests.pages.automation_ids import MeditikIds as Ids
from refua_tests.pages.meditek_base_page import MeditekBasePage
from refua_tests.pages.soft_notes import report_soft_note


@dataclass(frozen=True)
class RequestFormSpec:
    """Sanity contract for one request form."""

    tile_label: str  # button text on /all-actions
    path: str
    page_title: str
    # data-testid that must exist (hard)
    required_test_ids: tuple[str, ...] = ()
    # Hebrew snippets expected on a real form (soft if testids already OK)
    required_texts: tuple[str, ...] = ()


# Forms confirmed on test via all-actions tiles.
REQUEST_FORMS: tuple[RequestFormSpec, ...] = (
    RequestFormSpec(
        tile_label="הפניה חדשה",
        path="/referral-request",
        page_title="הפניה חדשה",
        required_test_ids=(
            Ids.INPUT_PHONE_NUMBER,
            "meditik-referral-request-btn-submit",
        ),
        required_texts=("הפניה", "טלפון"),
    ),
    RequestFormSpec(
        tile_label="קבלת מרשם",
        path="/prescription-request",
        page_title="קבלת מרשם",
        required_test_ids=(
            Ids.INPUT_PHONE_NUMBER,
            "meditik-prescription-request-btn-submit",
        ),
        required_texts=("מרשם", "טלפון", "שליחת בקשה"),
    ),
    RequestFormSpec(
        tile_label="אישור ימי מחלה",
        path="/sick-days-request",
        page_title="אישור ימי מחלה",
        required_test_ids=(
            Ids.INPUT_PHONE_NUMBER,
            "meditik-sick-days-request-btn-submit",
            "meditik-sick-days-request-input-cause",
            "meditik-sick-days-request-input-date-range",
        ),
        required_texts=("ימי מחלה", "טלפון"),
    ),
    RequestFormSpec(
        tile_label="קבלת שובר למדרסים",
        path="/insoles-request",
        page_title="קבלת שובר למדרסים",
        required_test_ids=(
            Ids.INPUT_PHONE_NUMBER,
            "meditik-insoles-request-btn-submit",
        ),
        required_texts=("מדרסים", "טלפון", "שליחת בקשה"),
    ),
    RequestFormSpec(
        tile_label="החזרת תשובה להפניה",
        path="/referral-answers-request",
        page_title="בקשה להחזרת תשובה להפניה",
        required_test_ids=(
            Ids.INPUT_PHONE_NUMBER,
            "meditik-referral-answer-request-btn-submit",
        ),
        required_texts=("הפניה", "טלפון"),
    ),
    RequestFormSpec(
        tile_label="שיננית עד הבית",
        path="/dentist-request",
        page_title="שיננית עד הבית",
        required_test_ids=(
            Ids.INPUT_PHONE_NUMBER,
            "meditik-dentist-request-btn-submit",
            "meditik-dentist-request-select-chain",
        ),
        required_texts=("שיננית", "טלפון", "שליחת בקשה"),
    ),
)


class RequestFormPage(MeditekBasePage):
    """Open a request form from כל הפעולות and assert shell + key objects."""

    def __init__(self, page: Page, spec: RequestFormSpec):
        super().__init__(page)
        self.spec = spec

    def open_from_all_actions(self, *, session_ready: bool = False):
        if not session_ready:
            self.open_home()
            self.ensure_logged_in()
        self.go_to_all_actions()
        self.page.wait_for_url("**/all-actions**", timeout=60000)
        self.close_menu()
        self.dismiss_blocking_dialogs()
        self.wait_for_loading_done()

        tile = self.page.locator("button").filter(has_text=self.spec.tile_label).first
        expect(tile).to_be_visible(timeout=20000)
        tile.scroll_into_view_if_needed(timeout=5000)
        tile.click(force=True)

        self.page.wait_for_url(
            f"**{self.spec.path}**",
            timeout=60000,
            wait_until="domcontentloaded",
        )
        self.close_menu()
        self.wait_for_loading_done()
        self.dismiss_blocking_dialogs()
        # SPA often updates the URL before React mounts the form.
        self._wait_for_form_shell()
        return self

    def _wait_for_form_shell(self, timeout: int = 30000):
        """Wait until a real form marker appears (not chrome-only shell)."""
        spec = self.spec
        if not spec.required_test_ids:
            return self
        primary = self.page.get_by_test_id(spec.required_test_ids[0]).first
        try:
            primary.wait_for(state="visible", timeout=timeout)
        except Exception:
            # Attached is enough to prove the route mounted something.
            primary.wait_for(state="attached", timeout=5000)
        return self

    def assert_form_loaded(self):
        spec = self.spec
        assert spec.path in self.page.url, (
            f"Expected URL containing {spec.path}, got {self.page.url}"
        )
        self.close_menu()
        self.assert_no_app_error(context=spec.page_title)

        missing_ids = []
        for tid in spec.required_test_ids:
            loc = self.page.get_by_test_id(tid)
            try:
                loc.first.wait_for(state="attached", timeout=20000)
            except Exception:
                missing_ids.append(tid)

        body = self._body_text(timeout=15000)
        assert "דף זה לא נמצא" not in body, f"404 on {spec.path}"

        assert not missing_ids, (
            f"{spec.page_title}: missing form objects (data-testid): "
            + ", ".join(missing_ids)
            + f" | body snip: {body[:250]!r}"
        )

        # Content must include title or required texts — not chrome / speed-dial only.
        content_ok = spec.page_title in body or all(
            t in body for t in spec.required_texts[:1]
        )
        if not content_ok and Ids.INPUT_PHONE_NUMBER in spec.required_test_ids:
            # Phone field present = form mounted even if labels differ.
            content_ok = self.page.get_by_test_id(Ids.INPUT_PHONE_NUMBER).count() > 0

        assert content_ok, (
            f"{spec.page_title}: form content did not load on {spec.path}. "
            f"Body snip: {body[:250]!r}"
        )

        if spec.page_title not in body:
            report_soft_note(
                f"Request form title mismatch on {spec.path}: "
                f"expected {spec.page_title!r} in body. Continuing by URL/testids."
            )

        if Ids.INPUT_PHONE_NUMBER in spec.required_test_ids:
            try:
                expect(self.page.get_by_test_id(Ids.INPUT_PHONE_NUMBER).first).to_be_visible(
                    timeout=10000
                )
            except Exception:
                report_soft_note(
                    f"{spec.page_title}: phone input attached but not visible yet."
                )

        missing_texts = [t for t in spec.required_texts if t not in body]
        for t in missing_texts:
            report_soft_note(
                f"{spec.page_title}: expected text {t!r} not found on form "
                f"(testids OK). Body snip: {body[:200]!r}"
            )
        return self

    def run_sanity_from_all_actions(self, *, session_ready: bool = False):
        self.open_from_all_actions(session_ready=session_ready)
        self.assert_form_loaded()
        return self
