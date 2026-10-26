"""Meditik Visit Summaries (סיכומי ביקור) — /appointments module page object.

Third instance of the non-tabbed empty-state module shape, after Sick Days and
Vaccinations, so every assertion is inherited from
:class:`EmptyStateModulePage` and this class only supplies configuration.

The workbook (Visit_Summaries_Test_Cases_1.xlsx, VSUM-001..014) adds two
expectations the first two instances did not exercise, which is why the shared
base grew ``assert_quick_action_control`` (VSUM-004) and
``assert_complete_empty_state`` (VSUM-008) rather than this class growing them
privately — Sick Days and Vaccinations have equivalent cases still blocked on
quick-action ids, and they now inherit the implementation for free.

ROUTE WARNING: Visit Summaries is served at ``/appointments``, which is NOT the
My Appointments screen (``/zimun-torim``). The workbook's Key Notes state the
URL explicitly.

Copy is asserted HARD: VSUM-003 pins the exact Hebrew title and its
Error/Validation column rejects a duplicate or truncated title, and the string
is the application's own language rather than a translation.

Named ``VisitSummariesModulePage`` to avoid confusion with
``refua_tests.pages.menuPages.VisitSummariesPage``, which covers reaching this
screen from the side menu in the older menu-sanity suite.
"""

from __future__ import annotations

from refua_tests.pages.automationIds import MeditikIds as Ids
from refua_tests.pages.emptyStateModulePage import EmptyStateModulePage
from refua_tests.pages.meditikBasePage import MeditekBasePage


class VisitSummariesModulePage(EmptyStateModulePage):
    """The /appointments page: shell chrome plus a unique page-level empty state."""

    MODULE_NAME = "Visit Summaries"
    PATH = Ids.VISIT_SUMMARIES_MODULE_PATH
    EXPECTED_EMPTY_TEXT = Ids.VISIT_SUMMARIES_EXPECTED_EMPTY_TEXT
    # VSUM-011 reaches the route through application navigation.
    MENU_LABEL = MeditekBasePage.MENU_VISIT_SUMMARIES
    # No PAGE_TEST_ID: the workbook supplies no visit-summaries page root, so
    # page-ready is route + toolbar (VSUM-001's only grounded id).
    # No ROW_PREFIX either — the Limitations line records that no visit-summary
    # list-item testid exists in the inventory, so VSUM-008's phantom-record
    # check falls back to the legacy card locator in the shared base.
