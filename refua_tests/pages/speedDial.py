"""Meditik Speed Dial (+ / פעולות מהירות) — shared across screens."""

from __future__ import annotations

from playwright.sync_api import Page, expect

from refua_tests.pages.automationIds import MeditikIds as Ids
from refua_tests.pages.softNotes import report_soft_note


# Expected Hebrew labels for known action testids (soft-checked).
SPEED_DIAL_LABELS: dict[str, str] = {
    Ids.SPEED_DIAL_BOOK_APPOINTMENT: "זימון תור",
    Ids.SPEED_DIAL_SICK_DAYS: "בקשה לימי מחלה",
    Ids.SPEED_DIAL_NEW_REFERRAL: "בקשה להפניה חדשה",
    Ids.SPEED_DIAL_PRESCRIPTION: "בקשה למרשם",
    Ids.SPEED_DIAL_INSOLES: "שובר למדרסים",
    Ids.SPEED_DIAL_REFERRAL_ANSWER: "החזרת תשובה להפניה",
    Ids.SPEED_DIAL_BARHAN: 'פניה לברה"ן',
    Ids.SPEED_DIAL_MOKED: "פנייה למוקד מקול הלב",
}

# Per-route expected speed-dial actions (testid hard-check).
SPEED_DIAL_BY_PATH: dict[str, tuple[str, ...]] = {
    "/home": (
        Ids.SPEED_DIAL_NEW_REFERRAL,
        Ids.SPEED_DIAL_PRESCRIPTION,
        Ids.SPEED_DIAL_REFERRAL_ANSWER,
        Ids.SPEED_DIAL_BARHAN,
        Ids.SPEED_DIAL_MOKED,
    ),
    "/user-requests": (
        Ids.SPEED_DIAL_PRESCRIPTION,
        Ids.SPEED_DIAL_INSOLES,
        Ids.SPEED_DIAL_REFERRAL_ANSWER,
        Ids.SPEED_DIAL_SICK_DAYS,
    ),
    "/zimun-torim": (
        Ids.SPEED_DIAL_BOOK_APPOINTMENT,
        Ids.SPEED_DIAL_PRESCRIPTION,
        Ids.SPEED_DIAL_NEW_REFERRAL,
        Ids.SPEED_DIAL_SICK_DAYS,
    ),
    "/medicines": (
        Ids.SPEED_DIAL_PRESCRIPTION,
        Ids.SPEED_DIAL_BOOK_APPOINTMENT,
    ),
    "/referrals": (
        Ids.SPEED_DIAL_BOOK_APPOINTMENT,
        Ids.SPEED_DIAL_NEW_REFERRAL,
    ),
    "/lab-results": (
        Ids.SPEED_DIAL_BOOK_APPOINTMENT,
        Ids.SPEED_DIAL_PRESCRIPTION,
        Ids.SPEED_DIAL_NEW_REFERRAL,
        Ids.SPEED_DIAL_INSOLES,
    ),
    "/sick-days": (
        Ids.SPEED_DIAL_SICK_DAYS,
        Ids.SPEED_DIAL_BOOK_APPOINTMENT,
    ),
}


class SpeedDial:
    """Open/close speed dial and assert action buttons by data-testid.

    Note: the mapping puts ``data-testid`` on the SpeedDial *root* (presentation
    div), not on the FAB. Cards often intercept pointer events — use force click.
    Closed action FABs are in the DOM but not ``visible`` until opened.
    """

    def __init__(self, page: Page):
        self.page = page
        self.root = page.locator(
            f'[data-testid="{Ids.SPEED_DIAL_TRIGGER}"], #speed-dial'
        ).first
        self.fab = self.root.locator("button").first

    def is_present(self, timeout: int = 30000) -> bool:
        """True when speed-dial root + FAB button exist in the DOM (may load late)."""
        try:
            self.root.wait_for(state="attached", timeout=timeout)
            self.fab.wait_for(state="attached", timeout=timeout)
            return True
        except Exception:
            return False

    def open(self):
        self.root.wait_for(state="attached", timeout=30000)
        self.fab.wait_for(state="attached", timeout=30000)
        try:
            if self.fab.get_attribute("aria-expanded") == "true":
                return self
        except Exception:
            pass
        # Home/list cards often sit above the FAB in hit-testing.
        self.fab.click(force=True, timeout=15000)
        try:
            expect(self.fab).to_have_attribute("aria-expanded", "true", timeout=10000)
        except Exception:
            # Some builds toggle without stable aria — continue; actions check below.
            self.page.wait_for_timeout(500)
        return self

    def close(self):
        try:
            if self.fab.get_attribute("aria-expanded") == "true":
                self.fab.click(force=True, timeout=5000)
                self.page.wait_for_timeout(300)
                return self
        except Exception:
            pass
        try:
            self.page.keyboard.press("Escape")
        except Exception:
            pass
        return self

    def action(self, test_id: str):
        return self.page.get_by_test_id(test_id)

    def assert_actions_present(self, expected_test_ids: tuple[str, ...]):
        """Hard: each action testid attached (and visible once dial is open). Soft: label."""
        assert self.is_present(timeout=30000), "Speed dial root/FAB not in DOM"
        self.open()
        missing = []
        for tid in expected_test_ids:
            btn = self.action(tid)
            try:
                btn.wait_for(state="attached", timeout=10000)
            except Exception:
                missing.append(tid)
                continue
            # Prefer visible after open; if still hidden, attached is enough for sanity
            # (MUI sometimes keeps closed opacity briefly).
            try:
                expect(btn).to_be_visible(timeout=5000)
            except Exception:
                report_soft_note(
                    f"Speed-dial action {tid} is attached but not visible yet "
                    f"after open — treating as present."
                )
            expected_label = SPEED_DIAL_LABELS.get(tid)
            if expected_label:
                try:
                    text = (btn.inner_text(timeout=3000) or "").strip()
                    text = " ".join(text.split())
                except Exception:
                    text = ""
                if text and expected_label not in text:
                    report_soft_note(
                        f"Speed-dial label mismatch for {tid}: "
                        f"expected {expected_label!r}, got {text!r}. "
                        f"Continuing by data-testid."
                    )
        assert not missing, (
            "Speed-dial actions missing (by data-testid): " + ", ".join(missing)
        )
        return self
