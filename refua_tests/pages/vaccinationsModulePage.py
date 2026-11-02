"""Meditik Vaccinations (חיסונים) — /vaccinations module page object.

Covers the Vaccinations page from the Vaccinations workbook (VACC-001..020),
which is a case-for-case twin of the Sick_days workbook: same non-tabbed
empty-state shape, same Ready set (001/002/003/014), same requirement to fail on
a missing, duplicated or hidden element.

Every assertion therefore lives in :class:`EmptyStateModulePage`; this class
only supplies the route, the page testid and the exact expected copy. The copy
is asserted HARD (VACC-002 requires failing when the text differs, and the
string is Hebrew, the application's own language).

Named ``VaccinationsModulePage`` to avoid confusion with
``refua_tests.pages.menuPages.VaccinationsPage``, which covers reaching this
screen from the side menu in the older menu-sanity suite.
"""

from __future__ import annotations

from refua_tests.pages.automationIds import MeditikIds as Ids
from refua_tests.pages.emptyStateModulePage import EmptyStateModulePage


class VaccinationsModulePage(EmptyStateModulePage):
    """The /vaccinations page: shell chrome plus a unique page-level empty state."""

    MODULE_NAME = "Vaccinations"
    PATH = Ids.VACCINATIONS_MODULE_PATH
    PAGE_TEST_ID = Ids.VACCINATIONS_PAGE
    EXPECTED_EMPTY_TEXT = Ids.VACCINATIONS_EXPECTED_EMPTY_TEXT
