"""Pending workbook specifications; no UI step implementations are claimed."""

import pytest
from pytest_bdd import scenarios

pytestmark = pytest.mark.skip(
    reason=(
        "Blocked: approved isolated data setup/cleanup and API/data-model contracts "
        "are unavailable; unspecified product rules are deferred. See "
        "docs/setup/WORKBOOK_CASES.json for each case's requirements and reason."
    )
)

scenarios("features/meditik_workbook_pending.feature", encoding="utf-8-sig")