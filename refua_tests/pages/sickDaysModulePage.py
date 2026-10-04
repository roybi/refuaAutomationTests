"""Meditik Sick Days (ימי מחלה) — /sick-days module page object.

Covers the Sick Days page from the Sick_days workbook (SICK-DAYS-001..020).

This page is NOT tabbed: its grounded coverage is the shell chrome plus a
page-level empty state. That shape is shared with Vaccinations, so every
assertion lives in :class:`EmptyStateModulePage` and this class is a thin
configuration of it — route, page testid and the exact expected copy.

The empty-state copy is asserted HARD (SICK-DAYS-002 requires failing when the
text differs, and the string is Hebrew, the application's own language).

Named ``SickDaysModulePage`` to avoid confusion with
``refua_tests.pages.menuPages.SickDaysPage``, which covers reaching this screen
from the side menu in the older menu-sanity suite.
"""

from __future__ import annotations

from refua_tests.pages.automationIds import MeditikIds as Ids
from refua_tests.pages.emptyStateModulePage import (EmptyStateModulePage,
                                                    ModuleEmptyState)

# Kept as an alias so existing imports of the old name keep working.
SickDaysState = ModuleEmptyState


class SickDaysModulePage(EmptyStateModulePage):
    """The /sick-days page: shell chrome plus a unique page-level empty state."""

    MODULE_NAME = "Sick Days"
    PATH = Ids.SICK_DAYS_MODULE_PATH
    PAGE_TEST_ID = Ids.SICK_DAYS_PAGE
    EXPECTED_EMPTY_TEXT = Ids.SICK_DAYS_EXPECTED_EMPTY_TEXT
    EMPTY_STATE_TITLE_ID = Ids.SICK_DAYS_EMPTY_STATE_TITLE
    EMPTY_STATE_ICON_ID = Ids.SICK_DAYS_EMPTY_STATE_ICON
