"""Workbook cases awaiting approved data and behavior contracts."""

import json
from pathlib import Path

import pytest

import allure

CASES = json.loads(
    (Path(__file__).resolve().parents[2] / "docs/setup/WORKBOOK_CASES.json").read_text(
        encoding="utf-8-sig"
    )
)


@pytest.mark.meditik
@pytest.mark.parametrize(
    "case",
    [
        pytest.param(
            case,
            id=case["TC_ID"],
            marks=pytest.mark.skip(reason=case["Blocked_Reason"]),
        )
        for case in CASES
    ],
)
def test_workbook_case(case):
    """Report blocked requirements without invoking medical-data workflows."""
    allure.dynamic.title(f'{case["TC_ID"]}: {case["Scenario"]}')
    allure.dynamic.description(case["Detailed Automation Steps"])
    allure.attach(
        json.dumps(case, ensure_ascii=False, indent=2),
        name="Workbook requirements and blocking reason",
        attachment_type=allure.attachment_type.JSON,
    )
    pytest.skip(case["Blocked_Reason"])