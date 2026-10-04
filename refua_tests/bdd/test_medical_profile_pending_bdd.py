"""Pending Medical Profile specifications; no UI step implementations are claimed."""

import pytest
from pytest_bdd import scenarios

pytestmark = pytest.mark.skip(
    reason=(
        "Blocked: Security/API-Contract/Data-Model/Product/UX/Performance "
        "confirmation is unavailable for these cases. See "
        "docs/setup/MEDICAL_PROFILE_CASES.json for each case's Clarification "
        "Status."
    )
)

scenarios("features/meditik_medical_profile_pending.feature", encoding="utf-8-sig")
